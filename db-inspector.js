#!/usr/bin/env node

// Database Inspector Utility for Unhinged PostgreSQL
// Provides easy access to inspect database contents and debug events

const { Client } = require('pg');
const readline = require('readline');

// Database configuration - try multiple connection options
const DB_CONFIGS = [
  {
    name: 'Docker Compose (unhinged user)',
    host: 'localhost',
    port: 5433,
    database: 'unhinged',
    user: 'unhinged',
    password: 'unhinged_password'
  },
  {
    name: 'Docker Compose (postgres user)',
    host: 'localhost',
    port: 5433,
    database: 'unhinged',
    user: 'postgres',
    password: 'unhinged_password'
  },
  {
    name: 'Default postgres (empty password)',
    host: 'localhost',
    port: 5433,
    database: 'postgres',
    user: 'postgres',
    password: ''
  },
  {
    name: 'Default postgres (postgres password)',
    host: 'localhost',
    port: 5433,
    database: 'postgres',
    user: 'postgres',
    password: 'postgres'
  }
];

class DatabaseInspector {
  constructor() {
    this.client = null;
    this.config = null;
    this.rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });
  }

  async connect() {
    // Try each configuration until one works
    for (const config of DB_CONFIGS) {
      try {
        console.log(`🔄 Trying ${config.name}...`);
        this.client = new Client(config);
        await this.client.connect();
        this.config = config;
        console.log('✅ Connected to PostgreSQL database');
        console.log(`📍 ${config.host}:${config.port}/${config.database} (user: ${config.user})`);
        return true;
      } catch (error) {
        console.log(`❌ ${config.name} failed: ${error.message}`);
        if (this.client) {
          try { await this.client.end(); } catch (e) {}
          this.client = null;
        }
      }
    }
    console.error('❌ All connection attempts failed');
    return false;
  }

  async disconnect() {
    await this.client.end();
    this.rl.close();
    console.log('👋 Disconnected from database');
  }

  async showTables() {
    try {
      const result = await this.client.query(`
        SELECT 
          schemaname,
          tablename,
          tableowner
        FROM pg_tables 
        WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
        ORDER BY schemaname, tablename;
      `);
      
      console.log('\n📋 Database Tables:');
      console.log('==================');
      if (result.rows.length === 0) {
        console.log('No user tables found');
      } else {
        result.rows.forEach(row => {
          console.log(`📄 ${row.schemaname}.${row.tablename} (owner: ${row.tableowner})`);
        });
      }
      console.log(`\nTotal: ${result.rows.length} tables\n`);
    } catch (error) {
      console.error('❌ Error fetching tables:', error.message);
    }
  }

  async showTableSchema(tableName) {
    try {
      const result = await this.client.query(`
        SELECT 
          column_name,
          data_type,
          is_nullable,
          column_default,
          character_maximum_length
        FROM information_schema.columns 
        WHERE table_name = $1 
        ORDER BY ordinal_position;
      `, [tableName]);
      
      console.log(`\n📋 Schema for table: ${tableName}`);
      console.log('=====================================');
      if (result.rows.length === 0) {
        console.log(`Table '${tableName}' not found`);
      } else {
        result.rows.forEach(row => {
          const nullable = row.is_nullable === 'YES' ? 'NULL' : 'NOT NULL';
          const length = row.character_maximum_length ? `(${row.character_maximum_length})` : '';
          const defaultVal = row.column_default ? ` DEFAULT ${row.column_default}` : '';
          console.log(`  📄 ${row.column_name}: ${row.data_type}${length} ${nullable}${defaultVal}`);
        });
      }
      console.log();
    } catch (error) {
      console.error('❌ Error fetching schema:', error.message);
    }
  }

  async showTableData(tableName, limit = 10) {
    try {
      const result = await this.client.query(`SELECT * FROM ${tableName} LIMIT $1`, [limit]);
      
      console.log(`\n📋 Data from table: ${tableName} (limit: ${limit})`);
      console.log('================================================');
      if (result.rows.length === 0) {
        console.log('No data found');
      } else {
        console.table(result.rows);
      }
      console.log(`\nShowing ${result.rows.length} rows\n`);
    } catch (error) {
      console.error('❌ Error fetching data:', error.message);
    }
  }

  async executeQuery(query) {
    try {
      console.log(`\n🔍 Executing: ${query}`);
      console.log('================================');
      const result = await this.client.query(query);
      
      if (result.rows.length === 0) {
        console.log('No results found');
      } else {
        console.table(result.rows);
      }
      console.log(`\n📊 ${result.rows.length} rows returned\n`);
    } catch (error) {
      console.error('❌ Query error:', error.message);
    }
  }

  async showDatabaseStats() {
    try {
      // Database size
      const sizeResult = await this.client.query(`
        SELECT pg_size_pretty(pg_database_size(current_database())) as database_size;
      `);
      
      // Table sizes
      const tablesResult = await this.client.query(`
        SELECT 
          schemaname,
          tablename,
          pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
          pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
        FROM pg_tables 
        WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
        ORDER BY size_bytes DESC;
      `);

      console.log('\n📊 Database Statistics:');
      console.log('=======================');
      console.log(`💾 Database size: ${sizeResult.rows[0].database_size}`);
      console.log('\n📋 Table sizes:');
      tablesResult.rows.forEach(row => {
        console.log(`  📄 ${row.schemaname}.${row.tablename}: ${row.size}`);
      });
      console.log();
    } catch (error) {
      console.error('❌ Error fetching stats:', error.message);
    }
  }

  async interactiveMode() {
    console.log('\n🎯 Interactive Database Inspector');
    console.log('==================================');
    console.log('Commands:');
    console.log('  tables          - Show all tables');
    console.log('  schema <table>  - Show table schema');
    console.log('  data <table>    - Show table data (limit 10)');
    console.log('  data <table> N  - Show table data (limit N)');
    console.log('  stats           - Show database statistics');
    console.log('  sql <query>     - Execute custom SQL query');
    console.log('  quit            - Exit inspector');
    console.log();

    const askQuestion = () => {
      this.rl.question('🔍 db> ', async (input) => {
        const parts = input.trim().split(' ');
        const command = parts[0].toLowerCase();

        switch (command) {
          case 'tables':
            await this.showTables();
            break;
          case 'schema':
            if (parts[1]) {
              await this.showTableSchema(parts[1]);
            } else {
              console.log('Usage: schema <table_name>');
            }
            break;
          case 'data':
            if (parts[1]) {
              const limit = parts[2] ? parseInt(parts[2]) : 10;
              await this.showTableData(parts[1], limit);
            } else {
              console.log('Usage: data <table_name> [limit]');
            }
            break;
          case 'stats':
            await this.showDatabaseStats();
            break;
          case 'sql':
            if (parts.length > 1) {
              const query = parts.slice(1).join(' ');
              await this.executeQuery(query);
            } else {
              console.log('Usage: sql <query>');
            }
            break;
          case 'quit':
          case 'exit':
            await this.disconnect();
            return;
          case '':
            break;
          default:
            console.log('Unknown command. Type "quit" to exit.');
        }
        askQuestion();
      });
    };

    askQuestion();
  }

  // Quick inspection methods for debugging
  async quickInspect() {
    console.log('🔍 Quick Database Inspection');
    console.log('============================');
    
    await this.showTables();
    await this.showDatabaseStats();
    
    // Check for common event tables
    const eventTables = ['chat_messages', 'chat_sessions', 'events', 'document_events', 'llm_events'];
    for (const table of eventTables) {
      try {
        const result = await this.client.query(`SELECT COUNT(*) as count FROM ${table}`);
        console.log(`📊 ${table}: ${result.rows[0].count} records`);
      } catch (error) {
        // Table doesn't exist, skip
      }
    }
    console.log();
  }
}

// CLI interface
async function main() {
  const args = process.argv.slice(2);
  const inspector = new DatabaseInspector();
  
  if (!(await inspector.connect())) {
    process.exit(1);
  }

  if (args.length === 0) {
    // Interactive mode
    await inspector.quickInspect();
    await inspector.interactiveMode();
  } else {
    // Command mode
    const command = args[0].toLowerCase();
    
    switch (command) {
      case 'tables':
        await inspector.showTables();
        break;
      case 'schema':
        if (args[1]) {
          await inspector.showTableSchema(args[1]);
        } else {
          console.log('Usage: node db-inspector.js schema <table_name>');
        }
        break;
      case 'data':
        if (args[1]) {
          const limit = args[2] ? parseInt(args[2]) : 10;
          await inspector.showTableData(args[1], limit);
        } else {
          console.log('Usage: node db-inspector.js data <table_name> [limit]');
        }
        break;
      case 'stats':
        await inspector.showDatabaseStats();
        break;
      case 'quick':
        await inspector.quickInspect();
        break;
      default:
        console.log('Usage: node db-inspector.js [tables|schema|data|stats|quick]');
    }
    
    await inspector.disconnect();
  }
}

// Handle graceful shutdown
process.on('SIGINT', async () => {
  console.log('\n👋 Shutting down...');
  process.exit(0);
});

if (require.main === module) {
  main().catch(console.error);
}

module.exports = DatabaseInspector;
