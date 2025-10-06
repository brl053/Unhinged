#!/usr/bin/env node

// Event API Server - Receives events from frontend and persists to PostgreSQL
// This is the missing piece for proper OLTP event persistence

const http = require('http');
const url = require('url');
const { Client } = require('pg');

const PORT = 8084;

// Database configuration
const DB_CONFIG = {
  host: 'localhost',
  port: 5433,
  database: 'postgres',
  user: 'postgres',
  password: 'postgres'
};

class EventAPIServer {
  constructor() {
    this.client = new Client(DB_CONFIG);
    this.eventBuffer = [];
    this.isConnected = false;
  }

  async connect() {
    try {
      await this.client.connect();
      this.isConnected = true;
      console.log('✅ Connected to PostgreSQL for event persistence');
      
      // Ensure events table exists
      await this.ensureEventsTable();
      
      return true;
    } catch (error) {
      console.error('❌ Failed to connect to PostgreSQL:', error.message);
      return false;
    }
  }

  async ensureEventsTable() {
    try {
      await this.client.query(`
        CREATE TABLE IF NOT EXISTS events (
          id VARCHAR(255) PRIMARY KEY,
          event_type VARCHAR(100) NOT NULL,
          event_data JSONB NOT NULL,
          source VARCHAR(100) NOT NULL,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          metadata JSONB
        );
      `);
      
      // Create indexes for performance
      await this.client.query(`
        CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
      `);
      await this.client.query(`
        CREATE INDEX IF NOT EXISTS idx_events_source ON events(source);
      `);
      await this.client.query(`
        CREATE INDEX IF NOT EXISTS idx_events_created_at ON events(created_at);
      `);
      await this.client.query(`
        CREATE INDEX IF NOT EXISTS idx_events_session_id ON events((metadata->>'sessionId'));
      `);
      
      console.log('✅ Events table and indexes ready');
    } catch (error) {
      console.error('❌ Failed to create events table:', error.message);
    }
  }

  async persistEvent(event) {
    if (!this.isConnected) {
      console.error('❌ Database not connected, buffering event');
      this.eventBuffer.push(event);
      return false;
    }

    try {
      await this.client.query(`
        INSERT INTO events (id, event_type, event_data, source, created_at, metadata)
        VALUES ($1, $2, $3, $4, $5, $6)
        ON CONFLICT (id) DO NOTHING
      `, [
        event.id,
        event.type,
        JSON.stringify(event.data),
        event.source,
        event.timestamp,
        JSON.stringify(event.metadata || {})
      ]);
      
      console.log(`✅ Persisted event: ${event.type} (${event.source})`);
      return true;
    } catch (error) {
      console.error('❌ Failed to persist event:', error.message);
      return false;
    }
  }

  async handleEventPost(req, res) {
    let body = '';
    
    req.on('data', chunk => {
      body += chunk.toString();
    });
    
    req.on('end', async () => {
      try {
        const events = JSON.parse(body);
        
        // Handle single event or array of events
        const eventArray = Array.isArray(events) ? events : [events];
        
        let successCount = 0;
        let failCount = 0;
        
        for (const event of eventArray) {
          // Validate event structure
          if (!event.id || !event.type || !event.source || !event.data) {
            console.error('❌ Invalid event structure:', event);
            failCount++;
            continue;
          }
          
          const success = await this.persistEvent(event);
          if (success) {
            successCount++;
          } else {
            failCount++;
          }
        }
        
        // Set CORS headers
        res.setHeader('Access-Control-Allow-Origin', '*');
        res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
        res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
        
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
          success: true,
          processed: eventArray.length,
          persisted: successCount,
          failed: failCount,
          timestamp: new Date().toISOString()
        }));
        
      } catch (error) {
        console.error('❌ Error processing events:', error.message);
        
        res.setHeader('Access-Control-Allow-Origin', '*');
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
          success: false,
          error: error.message,
          timestamp: new Date().toISOString()
        }));
      }
    });
  }

  async handleHealthCheck(req, res) {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      status: 'healthy',
      service: 'event-api-server',
      database_connected: this.isConnected,
      buffered_events: this.eventBuffer.length,
      timestamp: new Date().toISOString()
    }));
  }

  async handleOptions(req, res) {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    res.writeHead(200);
    res.end();
  }

  async handleGetEvents(req, res) {
    if (!this.isConnected) {
      res.setHeader('Access-Control-Allow-Origin', '*');
      res.writeHead(503, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Database not connected' }));
      return;
    }

    try {
      const parsedUrl = url.parse(req.url, true);
      const limit = parseInt(parsedUrl.query.limit) || 50;
      const eventType = parsedUrl.query.type;
      const source = parsedUrl.query.source;
      
      let query = 'SELECT * FROM events';
      let params = [];
      let conditions = [];
      
      if (eventType) {
        conditions.push(`event_type = $${params.length + 1}`);
        params.push(eventType);
      }
      
      if (source) {
        conditions.push(`source = $${params.length + 1}`);
        params.push(source);
      }
      
      if (conditions.length > 0) {
        query += ' WHERE ' + conditions.join(' AND ');
      }
      
      query += ` ORDER BY created_at DESC LIMIT $${params.length + 1}`;
      params.push(limit);
      
      const result = await this.client.query(query, params);
      
      res.setHeader('Access-Control-Allow-Origin', '*');
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({
        events: result.rows,
        count: result.rows.length,
        timestamp: new Date().toISOString()
      }));
      
    } catch (error) {
      console.error('❌ Error fetching events:', error.message);
      res.setHeader('Access-Control-Allow-Origin', '*');
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: error.message }));
    }
  }

  start() {
    const server = http.createServer(async (req, res) => {
      const parsedUrl = url.parse(req.url, true);
      const path = parsedUrl.pathname;
      const method = req.method;
      
      console.log(`[${method}] ${path}`);
      
      // Handle CORS preflight
      if (method === 'OPTIONS') {
        await this.handleOptions(req, res);
        return;
      }
      
      // Route handling
      if (path === '/events' && method === 'POST') {
        await this.handleEventPost(req, res);
      } else if (path === '/events' && method === 'GET') {
        await this.handleGetEvents(req, res);
      } else if (path === '/health' && method === 'GET') {
        await this.handleHealthCheck(req, res);
      } else if (path === '/' && method === 'GET') {
        res.setHeader('Access-Control-Allow-Origin', '*');
        res.writeHead(200, { 'Content-Type': 'text/plain' });
        res.end(`🔥 Event API Server v1.0.0

📋 Available endpoints:
- POST /events              - Persist events to PostgreSQL
- GET  /events              - Retrieve events (with filters)
- GET  /health              - Health check
- GET  /                    - This info

🎯 OLTP Event Persistence for Full-Stack Microservice Architecture
Ready to persist ALL events to PostgreSQL!`);
      } else {
        res.writeHead(404, { 'Content-Type': 'text/plain' });
        res.end('Not Found');
      }
    });

    server.listen(PORT, () => {
      console.log(`🚀 Event API Server running on http://localhost:${PORT}`);
      console.log(`📋 Endpoints:`);
      console.log(`   POST http://localhost:${PORT}/events`);
      console.log(`   GET  http://localhost:${PORT}/events`);
      console.log(`   GET  http://localhost:${PORT}/health`);
      console.log(`🎯 Ready for OLTP event persistence!`);
    });

    // Graceful shutdown
    process.on('SIGINT', async () => {
      console.log('\n🛑 Shutting down event API server...');
      if (this.client) {
        await this.client.end();
      }
      server.close(() => {
        console.log('✅ Event API server stopped');
        process.exit(0);
      });
    });
  }
}

// Start the server
async function main() {
  const eventServer = new EventAPIServer();
  
  if (await eventServer.connect()) {
    eventServer.start();
  } else {
    console.error('❌ Failed to start event API server');
    process.exit(1);
  }
}

if (require.main === module) {
  main().catch(console.error);
}
