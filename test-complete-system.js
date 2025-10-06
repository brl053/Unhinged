#!/usr/bin/env node

// Complete System Test - Verify OLTP Event Persistence
// Tests the entire voice recording -> event logging -> PostgreSQL persistence flow

const http = require('http');
const { Client } = require('pg');

// Test configuration
const SERVICES = {
  frontend: 'http://localhost:8081',
  mockBackend: 'http://localhost:8080',
  whisperTTS: 'http://localhost:8000',
  eventAPI: 'http://localhost:8084'
};

const DB_CONFIG = {
  host: 'localhost',
  port: 5433,
  database: 'postgres',
  user: 'postgres',
  password: 'postgres'
};

class SystemTester {
  constructor() {
    this.client = new Client(DB_CONFIG);
    this.testResults = [];
  }

  async connect() {
    try {
      await this.client.connect();
      console.log('✅ Connected to PostgreSQL for testing');
      return true;
    } catch (error) {
      console.error('❌ Failed to connect to PostgreSQL:', error.message);
      return false;
    }
  }

  async testService(name, url) {
    try {
      const response = await fetch(url);
      if (response.ok) {
        console.log(`✅ ${name}: ${url} - HEALTHY`);
        this.testResults.push({ service: name, status: 'healthy', url });
        return true;
      } else {
        console.log(`❌ ${name}: ${url} - UNHEALTHY (${response.status})`);
        this.testResults.push({ service: name, status: 'unhealthy', url, error: response.status });
        return false;
      }
    } catch (error) {
      console.log(`❌ ${name}: ${url} - DOWN (${error.message})`);
      this.testResults.push({ service: name, status: 'down', url, error: error.message });
      return false;
    }
  }

  async testEventAPI() {
    console.log('\n🔍 Testing Event API...');
    
    // Test health endpoint
    const healthOk = await this.testService('Event API Health', `${SERVICES.eventAPI}/health`);
    
    // Test event persistence
    const testEvent = {
      id: `test_${Date.now()}`,
      type: 'system_test_event',
      source: 'system-tester',
      data: {
        message: 'Complete system test event',
        timestamp: new Date().toISOString()
      },
      timestamp: new Date().toISOString(),
      metadata: {
        testRun: true,
        sessionId: 'test-session-123'
      }
    };

    try {
      const response = await fetch(`${SERVICES.eventAPI}/events`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify([testEvent])
      });

      if (response.ok) {
        const result = await response.json();
        if (result.persisted === 1) {
          console.log('✅ Event API: Event persistence - SUCCESS');
          this.testResults.push({ service: 'Event API Persistence', status: 'healthy' });
          return testEvent.id;
        } else {
          console.log('❌ Event API: Event persistence - FAILED');
          this.testResults.push({ service: 'Event API Persistence', status: 'failed', error: 'No events persisted' });
          return null;
        }
      } else {
        console.log(`❌ Event API: Event persistence - HTTP ${response.status}`);
        this.testResults.push({ service: 'Event API Persistence', status: 'failed', error: response.status });
        return null;
      }
    } catch (error) {
      console.log(`❌ Event API: Event persistence - ERROR: ${error.message}`);
      this.testResults.push({ service: 'Event API Persistence', status: 'failed', error: error.message });
      return null;
    }
  }

  async testDatabasePersistence(eventId) {
    console.log('\n🔍 Testing Database Persistence...');
    
    if (!eventId) {
      console.log('❌ Database: No event ID to verify');
      return false;
    }

    try {
      const result = await this.client.query('SELECT * FROM events WHERE id = $1', [eventId]);
      
      if (result.rows.length === 1) {
        const event = result.rows[0];
        console.log('✅ Database: Event found in PostgreSQL');
        console.log(`   ID: ${event.id}`);
        console.log(`   Type: ${event.event_type}`);
        console.log(`   Source: ${event.source}`);
        console.log(`   Created: ${event.created_at}`);
        this.testResults.push({ service: 'PostgreSQL Persistence', status: 'healthy' });
        return true;
      } else {
        console.log('❌ Database: Event not found in PostgreSQL');
        this.testResults.push({ service: 'PostgreSQL Persistence', status: 'failed', error: 'Event not found' });
        return false;
      }
    } catch (error) {
      console.log(`❌ Database: Query failed - ${error.message}`);
      this.testResults.push({ service: 'PostgreSQL Persistence', status: 'failed', error: error.message });
      return false;
    }
  }

  async testEventRetrieval() {
    console.log('\n🔍 Testing Event Retrieval...');
    
    try {
      const response = await fetch(`${SERVICES.eventAPI}/events?limit=5`);
      
      if (response.ok) {
        const result = await response.json();
        console.log(`✅ Event API: Retrieved ${result.events.length} events`);
        
        if (result.events.length > 0) {
          console.log('   Recent events:');
          result.events.slice(0, 3).forEach(event => {
            console.log(`     - ${event.event_type} (${event.source}) at ${event.created_at}`);
          });
        }
        
        this.testResults.push({ service: 'Event Retrieval', status: 'healthy', count: result.events.length });
        return true;
      } else {
        console.log(`❌ Event API: Retrieval failed - HTTP ${response.status}`);
        this.testResults.push({ service: 'Event Retrieval', status: 'failed', error: response.status });
        return false;
      }
    } catch (error) {
      console.log(`❌ Event API: Retrieval error - ${error.message}`);
      this.testResults.push({ service: 'Event Retrieval', status: 'failed', error: error.message });
      return false;
    }
  }

  async testCompleteSystem() {
    console.log('🚀 Complete System Test - OLTP Event Persistence');
    console.log('==================================================');
    
    // Test all services
    console.log('\n🔍 Testing Core Services...');
    await this.testService('React Frontend', SERVICES.frontend);
    await this.testService('Mock Backend', SERVICES.mockBackend);
    await this.testService('Whisper TTS', SERVICES.whisperTTS);
    
    // Test event system
    const eventId = await this.testEventAPI();
    await this.testDatabasePersistence(eventId);
    await this.testEventRetrieval();
    
    // Summary
    console.log('\n📊 Test Results Summary');
    console.log('=======================');
    
    const healthy = this.testResults.filter(r => r.status === 'healthy').length;
    const total = this.testResults.length;
    
    console.log(`✅ Healthy: ${healthy}/${total} services`);
    
    if (healthy === total) {
      console.log('\n🎉 ALL SYSTEMS OPERATIONAL!');
      console.log('🎯 OLTP Event Persistence: FULLY FUNCTIONAL');
      console.log('\n📋 System Architecture:');
      console.log('   Frontend (React) → Event API → PostgreSQL');
      console.log('   Voice Recording → Transcription → Chat → Events → Database');
      console.log('\n🔥 Ready for full-stack microservice debugging!');
    } else {
      console.log('\n⚠️  Some services need attention:');
      this.testResults.filter(r => r.status !== 'healthy').forEach(result => {
        console.log(`   ❌ ${result.service}: ${result.error || result.status}`);
      });
    }
    
    return healthy === total;
  }

  async close() {
    await this.client.end();
  }
}

// Run the complete system test
async function main() {
  const tester = new SystemTester();
  
  if (await tester.connect()) {
    const success = await tester.testCompleteSystem();
    await tester.close();
    process.exit(success ? 0 : 1);
  } else {
    process.exit(1);
  }
}

if (require.main === module) {
  main().catch(console.error);
}
