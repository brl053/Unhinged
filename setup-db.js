#!/usr/bin/env node

// Database Setup Script
// Creates the unhinged user and database if they don't exist

const { Client } = require('pg');

// Connect as postgres superuser first
const ADMIN_CONFIG = {
  host: 'localhost',
  port: 5433,
  database: 'postgres',
  user: 'postgres',
  password: 'postgres'  // Default postgres password
};

async function setupDatabase() {
  let client = null;
  
  try {
    console.log('🔄 Connecting as postgres superuser...');
    client = new Client(ADMIN_CONFIG);
    await client.connect();
    console.log('✅ Connected as postgres');
    
    // Check if unhinged user exists
    const userResult = await client.query(
      "SELECT 1 FROM pg_roles WHERE rolname = 'unhinged'"
    );
    
    if (userResult.rows.length === 0) {
      console.log('🔄 Creating unhinged user...');
      await client.query(
        "CREATE USER unhinged WITH PASSWORD 'unhinged_password'"
      );
      console.log('✅ Created unhinged user');
    } else {
      console.log('ℹ️  unhinged user already exists');
    }
    
    // Check if unhinged database exists
    const dbResult = await client.query(
      "SELECT 1 FROM pg_database WHERE datname = 'unhinged'"
    );
    
    if (dbResult.rows.length === 0) {
      console.log('🔄 Creating unhinged database...');
      await client.query('CREATE DATABASE unhinged OWNER unhinged');
      console.log('✅ Created unhinged database');
    } else {
      console.log('ℹ️  unhinged database already exists');
    }
    
    // Grant privileges
    console.log('🔄 Granting privileges...');
    await client.query('GRANT ALL PRIVILEGES ON DATABASE unhinged TO unhinged');
    console.log('✅ Granted privileges');
    
    await client.end();
    
    // Now test connection as unhinged user
    console.log('🔄 Testing connection as unhinged user...');
    const testClient = new Client({
      host: 'localhost',
      port: 5433,
      database: 'unhinged',
      user: 'unhinged',
      password: 'unhinged_password'
    });
    
    await testClient.connect();
    const result = await testClient.query('SELECT current_database(), current_user');
    console.log('✅ Test connection successful:');
    console.log(`   Database: ${result.rows[0].current_database}`);
    console.log(`   User: ${result.rows[0].current_user}`);
    await testClient.end();
    
    console.log('\n🎉 Database setup complete!');
    console.log('You can now use the database inspector:');
    console.log('   node db-inspector.js');
    
  } catch (error) {
    console.error('❌ Setup failed:', error.message);
    
    if (error.message.includes('password authentication failed')) {
      console.log('\n💡 Trying alternative postgres passwords...');
      
      // Try common postgres passwords
      const passwords = ['', 'postgres', 'password', 'unhinged_password'];
      
      for (const password of passwords) {
        try {
          console.log(`🔄 Trying postgres password: '${password || '(empty)'}'`);
          const testConfig = { ...ADMIN_CONFIG, password };
          const testClient = new Client(testConfig);
          await testClient.connect();
          console.log(`✅ Found working password: '${password || '(empty)'}'`);
          await testClient.end();
          
          console.log('\n📝 Update the ADMIN_CONFIG in this script with the working password and run again.');
          return;
        } catch (e) {
          console.log(`❌ Password '${password || '(empty)'}' failed`);
        }
      }
      
      console.log('\n💡 You may need to reset the postgres container:');
      console.log('   docker compose down');
      console.log('   docker volume rm unhinged_postgres-data');
      console.log('   docker compose up -d postgres');
    }
    
    process.exit(1);
  } finally {
    if (client) {
      try { await client.end(); } catch (e) {}
    }
  }
}

if (require.main === module) {
  setupDatabase().catch(console.error);
}
