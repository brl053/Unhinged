#!/usr/bin/env node

// Database Debug Utility - Focused on debugging events and chat data
// This tool helps debug the voice recording integration by inspecting database state

const { Client } = require('pg');

// Working database configuration
const DB_CONFIG = {
  host: 'localhost',
  port: 5433,
  database: 'postgres',
  user: 'postgres',
  password: 'postgres'
};

class DatabaseDebugger {
  constructor() {
    this.client = new Client(DB_CONFIG);
  }

  async connect() {
    try {
      await this.client.connect();
      console.log('✅ Connected to PostgreSQL');
      console.log(`📍 ${DB_CONFIG.host}:${DB_CONFIG.port}/${DB_CONFIG.database}`);
      return true;
    } catch (error) {
      console.error('❌ Connection failed:', error.message);
      return false;
    }
  }

  async disconnect() {
    await this.client.end();
    console.log('👋 Disconnected');
  }

  async createTestTables() {
    console.log('🔧 Creating test tables for debugging...');
    
    try {
      // Create chat_sessions table
      await this.client.query(`
        CREATE TABLE IF NOT EXISTS chat_sessions (
          id VARCHAR(255) PRIMARY KEY,
          user_id VARCHAR(255) NOT NULL,
          title VARCHAR(500),
          is_active BOOLEAN DEFAULT true,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          metadata JSONB
        );
      `);
      console.log('✅ Created chat_sessions table');

      // Create chat_messages table
      await this.client.query(`
        CREATE TABLE IF NOT EXISTS chat_messages (
          id VARCHAR(255) PRIMARY KEY,
          session_id VARCHAR(255) NOT NULL,
          content TEXT NOT NULL,
          role VARCHAR(50) NOT NULL,
          timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          metadata JSONB,
          FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
        );
      `);
      console.log('✅ Created chat_messages table');

      // Create voice_recordings table for debugging
      await this.client.query(`
        CREATE TABLE IF NOT EXISTS voice_recordings (
          id SERIAL PRIMARY KEY,
          session_id VARCHAR(255),
          original_audio_size INTEGER,
          transcription_text TEXT,
          transcription_language VARCHAR(10),
          processing_time_ms INTEGER,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          metadata JSONB
        );
      `);
      console.log('✅ Created voice_recordings table');

      // Create events table for general debugging
      await this.client.query(`
        CREATE TABLE IF NOT EXISTS events (
          id SERIAL PRIMARY KEY,
          event_type VARCHAR(100) NOT NULL,
          event_data JSONB NOT NULL,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          source VARCHAR(100)
        );
      `);
      console.log('✅ Created events table');

      console.log('🎉 Test tables created successfully!');
    } catch (error) {
      console.error('❌ Error creating tables:', error.message);
    }
  }

  async insertTestData() {
    console.log('📝 Inserting test data...');
    
    try {
      // Insert test session
      const sessionId = 'test-session-' + Date.now();
      await this.client.query(`
        INSERT INTO chat_sessions (id, user_id, title, metadata)
        VALUES ($1, $2, $3, $4)
      `, [sessionId, 'test-user', 'Voice Recording Test Session', JSON.stringify({
        source: 'voice-recording-test',
        created_by: 'db-debug-tool'
      })]);
      console.log(`✅ Created test session: ${sessionId}`);

      // Insert test messages
      await this.client.query(`
        INSERT INTO chat_messages (id, session_id, content, role, metadata)
        VALUES ($1, $2, $3, $4, $5)
      `, [
        'msg-' + Date.now() + '-1',
        sessionId,
        'Hello, this is a test voice message',
        'USER',
        JSON.stringify({ source: 'voice-recording', audio_duration_ms: 2500 })
      ]);

      await this.client.query(`
        INSERT INTO chat_messages (id, session_id, content, role, metadata)
        VALUES ($1, $2, $3, $4, $5)
      `, [
        'msg-' + Date.now() + '-2',
        sessionId,
        'This is a test AI response',
        'ASSISTANT',
        JSON.stringify({ source: 'mock-backend', processing_time_ms: 150 })
      ]);
      console.log('✅ Inserted test messages');

      // Insert test voice recording
      await this.client.query(`
        INSERT INTO voice_recordings (session_id, original_audio_size, transcription_text, transcription_language, processing_time_ms, metadata)
        VALUES ($1, $2, $3, $4, $5, $6)
      `, [
        sessionId,
        15420,
        'Hello, this is a test voice message',
        'en',
        1250,
        JSON.stringify({
          whisper_model: 'base',
          confidence: 0.95,
          audio_format: 'webm'
        })
      ]);
      console.log('✅ Inserted test voice recording');

      // Insert test event
      await this.client.query(`
        INSERT INTO events (event_type, event_data, source)
        VALUES ($1, $2, $3)
      `, [
        'voice_recording_completed',
        JSON.stringify({
          session_id: sessionId,
          transcription: 'Hello, this is a test voice message',
          duration_ms: 2500,
          file_size: 15420
        }),
        'voice-recorder-component'
      ]);
      console.log('✅ Inserted test event');

      console.log('🎉 Test data inserted successfully!');
      return sessionId;
    } catch (error) {
      console.error('❌ Error inserting test data:', error.message);
    }
  }

  async showDebugInfo() {
    console.log('\n🔍 Database Debug Information');
    console.log('=============================');

    try {
      // Show all tables
      const tables = await this.client.query(`
        SELECT tablename FROM pg_tables 
        WHERE schemaname = 'public' 
        ORDER BY tablename
      `);
      
      console.log('\n📋 Available Tables:');
      tables.rows.forEach(row => {
        console.log(`  📄 ${row.tablename}`);
      });

      // Show data counts
      console.log('\n📊 Data Counts:');
      for (const table of tables.rows) {
        try {
          const count = await this.client.query(`SELECT COUNT(*) as count FROM ${table.tablename}`);
          console.log(`  📄 ${table.tablename}: ${count.rows[0].count} records`);
        } catch (e) {
          console.log(`  📄 ${table.tablename}: Error counting records`);
        }
      }

      // Show recent events
      try {
        const events = await this.client.query(`
          SELECT event_type, created_at, source 
          FROM events 
          ORDER BY created_at DESC 
          LIMIT 5
        `);
        
        console.log('\n📅 Recent Events:');
        if (events.rows.length === 0) {
          console.log('  No events found');
        } else {
          events.rows.forEach(row => {
            console.log(`  🔔 ${row.event_type} (${row.source}) - ${row.created_at}`);
          });
        }
      } catch (e) {
        console.log('\n📅 Recent Events: Table not found');
      }

      // Show recent chat activity
      try {
        const messages = await this.client.query(`
          SELECT cm.content, cm.role, cm.timestamp, cs.title
          FROM chat_messages cm
          JOIN chat_sessions cs ON cm.session_id = cs.id
          ORDER BY cm.timestamp DESC
          LIMIT 5
        `);
        
        console.log('\n💬 Recent Chat Messages:');
        if (messages.rows.length === 0) {
          console.log('  No messages found');
        } else {
          messages.rows.forEach(row => {
            const preview = row.content.substring(0, 50) + (row.content.length > 50 ? '...' : '');
            console.log(`  💬 ${row.role}: "${preview}" (${row.timestamp})`);
          });
        }
      } catch (e) {
        console.log('\n💬 Recent Chat Messages: Tables not found');
      }

      // Show recent voice recordings
      try {
        const recordings = await this.client.query(`
          SELECT transcription_text, transcription_language, processing_time_ms, created_at
          FROM voice_recordings
          ORDER BY created_at DESC
          LIMIT 5
        `);
        
        console.log('\n🎤 Recent Voice Recordings:');
        if (recordings.rows.length === 0) {
          console.log('  No voice recordings found');
        } else {
          recordings.rows.forEach(row => {
            const preview = row.transcription_text.substring(0, 50) + (row.transcription_text.length > 50 ? '...' : '');
            console.log(`  🎤 "${preview}" (${row.transcription_language}, ${row.processing_time_ms}ms) - ${row.created_at}`);
          });
        }
      } catch (e) {
        console.log('\n🎤 Recent Voice Recordings: Table not found');
      }

    } catch (error) {
      console.error('❌ Error showing debug info:', error.message);
    }
  }

  async logVoiceRecording(sessionId, audioSize, transcription, language, processingTime) {
    try {
      await this.client.query(`
        INSERT INTO voice_recordings (session_id, original_audio_size, transcription_text, transcription_language, processing_time_ms, metadata)
        VALUES ($1, $2, $3, $4, $5, $6)
      `, [
        sessionId,
        audioSize,
        transcription,
        language,
        processingTime,
        JSON.stringify({
          timestamp: new Date().toISOString(),
          source: 'voice-recorder-component'
        })
      ]);
      console.log('✅ Logged voice recording to database');
    } catch (error) {
      console.error('❌ Error logging voice recording:', error.message);
    }
  }
}

// CLI interface
async function main() {
  const args = process.argv.slice(2);
  const dbDebugger = new DatabaseDebugger();
  
  if (!(await dbDebugger.connect())) {
    process.exit(1);
  }

  try {
    if (args.length === 0 || args[0] === 'debug') {
      await dbDebugger.showDebugInfo();
    } else if (args[0] === 'setup') {
      await dbDebugger.createTestTables();
      await dbDebugger.insertTestData();
      await dbDebugger.showDebugInfo();
    } else if (args[0] === 'tables') {
      await dbDebugger.createTestTables();
    } else if (args[0] === 'test-data') {
      await dbDebugger.insertTestData();
    } else {
      console.log('Usage: node db-debug.js [debug|setup|tables|test-data]');
      console.log('  debug     - Show current database state (default)');
      console.log('  setup     - Create tables and insert test data');
      console.log('  tables    - Create tables only');
      console.log('  test-data - Insert test data only');
    }
  } finally {
    await dbDebugger.disconnect();
  }
}

if (require.main === module) {
  main().catch(console.error);
}

module.exports = DatabaseDebugger;
