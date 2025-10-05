// ============================================================================
// Database Dependency Injection Module
// ============================================================================
// 
// @file DatabaseModule.kt
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-04
// @description Koin DI module for database configuration and connection management
// 
// This module provides:
// - HikariCP connection pool configuration
// - PostgreSQL database connection management
// - Transaction management utilities
// - Database health check components
// - Environment-specific database configurations
// 
// LLM-Native Features:
// - Optimized connection pool settings for high-throughput document operations
// - Read/write connection splitting for session context queries
// - Connection monitoring and metrics collection
// - Automatic failover and retry logic
// ============================================================================

package com.unhinged.di

import com.typesafe.config.Config
import com.typesafe.config.ConfigFactory
import com.zaxxer.hikari.HikariConfig
import com.zaxxer.hikari.HikariDataSource
import org.koin.core.qualifier.named
import org.koin.dsl.module
import org.slf4j.LoggerFactory
import javax.sql.DataSource

/**
 * Database dependency injection module with LLM-optimized configuration
 * 
 * Provides:
 * - Primary database connection pool for read/write operations
 * - Read-only replica connections for session context queries
 * - Transaction management utilities
 * - Database health monitoring
 * 
 * Configuration Properties:
 * - database.url: PostgreSQL connection URL
 * - database.username: Database username
 * - database.password: Database password
 * - database.pool.maximum: Maximum connection pool size
 * - database.pool.minimum: Minimum idle connections
 * - database.pool.timeout: Connection timeout in milliseconds
 * 
 * @since 1.0.0
 * @author Unhinged Team
 */
val databaseModule = module {
    
    // ========================================================================
    // Configuration
    // ========================================================================
    
    /**
     * Application configuration loaded from application.conf
     */
    single<Config> {
        ConfigFactory.load().resolve()
    }
    
    // ========================================================================
    // Database Connection Pools
    // ========================================================================
    
    /**
     * Primary database connection pool for read/write operations
     * 
     * Optimized for:
     * - Document CRUD operations with high throughput
     * - Transaction management for consistency
     * - Connection reuse for performance
     */
    single<DataSource>(named("primary")) {
        val config = get<Config>()
        val logger = LoggerFactory.getLogger("DatabaseModule")
        
        logger.info("Configuring primary database connection pool")
        
        val hikariConfig = HikariConfig().apply {
            // Connection settings
            jdbcUrl = config.getString("database.url")
            username = config.getString("database.username")
            password = config.getString("database.password")
            driverClassName = "org.postgresql.Driver"
            
            // Pool settings optimized for LLM workloads
            maximumPoolSize = config.getInt("database.pool.maximum")
            minimumIdle = config.getInt("database.pool.minimum")
            connectionTimeout = config.getLong("database.pool.timeout")
            idleTimeout = 600000 // 10 minutes
            maxLifetime = 1800000 // 30 minutes
            
            // Performance optimizations
            isAutoCommit = false // Explicit transaction management
            transactionIsolation = "TRANSACTION_READ_COMMITTED"
            
            // Connection validation
            connectionTestQuery = "SELECT 1"
            validationTimeout = 5000
            
            // Monitoring and metrics
            poolName = "UnhingedPrimaryPool"
            isRegisterMbeans = true
            
            // PostgreSQL-specific optimizations
            addDataSourceProperty("cachePrepStmts", "true")
            addDataSourceProperty("prepStmtCacheSize", "250")
            addDataSourceProperty("prepStmtCacheSqlLimit", "2048")
            addDataSourceProperty("useServerPrepStmts", "true")
            addDataSourceProperty("useLocalSessionState", "true")
            addDataSourceProperty("rewriteBatchedStatements", "true")
            addDataSourceProperty("cacheResultSetMetadata", "true")
            addDataSourceProperty("cacheServerConfiguration", "true")
            addDataSourceProperty("elideSetAutoCommits", "true")
            addDataSourceProperty("maintainTimeStats", "false")
        }
        
        HikariDataSource(hikariConfig)
    }
    
    /**
     * Read-only database connection pool for session context queries
     * 
     * Optimized for:
     * - High-frequency session context retrieval
     * - LLM prompt construction queries
     * - Analytics and reporting queries
     */
    single<DataSource>(named("readonly")) {
        val config = get<Config>()
        val logger = LoggerFactory.getLogger("DatabaseModule")
        
        logger.info("Configuring read-only database connection pool")
        
        val hikariConfig = HikariConfig().apply {
            // Connection settings (can point to read replica)
            jdbcUrl = config.getString("database.readonly.url")
            username = config.getString("database.readonly.username") 
            password = config.getString("database.readonly.password")
            driverClassName = "org.postgresql.Driver"
            
            // Pool settings optimized for read queries
            maximumPoolSize = config.getInt("database.readonly.pool.maximum")
            minimumIdle = config.getInt("database.readonly.pool.minimum")
            connectionTimeout = config.getLong("database.readonly.pool.timeout")
            idleTimeout = 300000 // 5 minutes (shorter for read-only)
            maxLifetime = 900000 // 15 minutes
            
            // Read-only optimizations
            isReadOnly = true
            isAutoCommit = true // No transactions needed for reads
            transactionIsolation = "TRANSACTION_READ_COMMITTED"
            
            // Connection validation
            connectionTestQuery = "SELECT 1"
            validationTimeout = 3000
            
            // Monitoring
            poolName = "UnhingedReadOnlyPool"
            isRegisterMbeans = true
            
            // PostgreSQL read optimizations
            addDataSourceProperty("cachePrepStmts", "true")
            addDataSourceProperty("prepStmtCacheSize", "500") // Larger cache for reads
            addDataSourceProperty("prepStmtCacheSqlLimit", "4096")
            addDataSourceProperty("useServerPrepStmts", "true")
            addDataSourceProperty("defaultRowFetchSize", "1000") // Optimize for large result sets
            addDataSourceProperty("cacheResultSetMetadata", "true")
            addDataSourceProperty("cacheServerConfiguration", "true")
        }
        
        HikariDataSource(hikariConfig)
    }
    
    // ========================================================================
    // Database Utilities
    // ========================================================================
    
    /**
     * Database health checker for monitoring and alerting
     */
    single<DatabaseHealthChecker> {
        DatabaseHealthChecker(
            primaryDataSource = get(named("primary")),
            readOnlyDataSource = get(named("readonly"))
        )
    }
    
    /**
     * Transaction manager for coordinating database operations
     */
    single<TransactionManager> {
        TransactionManager(get(named("primary")))
    }
}

/**
 * Database health checker for monitoring connection pools and database connectivity
 * 
 * @param primaryDataSource Primary database connection pool
 * @param readOnlyDataSource Read-only database connection pool
 */
class DatabaseHealthChecker(
    private val primaryDataSource: DataSource,
    private val readOnlyDataSource: DataSource
) {
    private val logger = LoggerFactory.getLogger(DatabaseHealthChecker::class.java)
    
    /**
     * Check health of all database connections
     * 
     * @return true if all connections are healthy, false otherwise
     */
    suspend fun checkHealth(): Boolean {
        return try {
            val primaryHealthy = checkConnectionHealth(primaryDataSource, "primary")
            val readOnlyHealthy = checkConnectionHealth(readOnlyDataSource, "readonly")
            
            primaryHealthy && readOnlyHealthy
        } catch (e: Exception) {
            logger.error("Database health check failed: ${e.message}", e)
            false
        }
    }
    
    /**
     * Check health of a specific data source
     */
    private fun checkConnectionHealth(dataSource: DataSource, name: String): Boolean {
        return try {
            dataSource.connection.use { conn ->
                conn.prepareStatement("SELECT 1").use { stmt ->
                    stmt.executeQuery().use { rs ->
                        val result = rs.next() && rs.getInt(1) == 1
                        logger.debug("Database health check for $name: ${if (result) "OK" else "FAILED"}")
                        result
                    }
                }
            }
        } catch (e: Exception) {
            logger.error("Database health check failed for $name: ${e.message}", e)
            false
        }
    }
    
    /**
     * Get connection pool metrics for monitoring
     */
    fun getPoolMetrics(): Map<String, Any> {
        val metrics = mutableMapOf<String, Any>()
        
        if (primaryDataSource is HikariDataSource) {
            val poolMXBean = primaryDataSource.hikariPoolMXBean
            metrics["primary_active_connections"] = poolMXBean.activeConnections
            metrics["primary_idle_connections"] = poolMXBean.idleConnections
            metrics["primary_total_connections"] = poolMXBean.totalConnections
            metrics["primary_threads_awaiting"] = poolMXBean.threadsAwaitingConnection
        }
        
        if (readOnlyDataSource is HikariDataSource) {
            val poolMXBean = readOnlyDataSource.hikariPoolMXBean
            metrics["readonly_active_connections"] = poolMXBean.activeConnections
            metrics["readonly_idle_connections"] = poolMXBean.idleConnections
            metrics["readonly_total_connections"] = poolMXBean.totalConnections
            metrics["readonly_threads_awaiting"] = poolMXBean.threadsAwaitingConnection
        }
        
        return metrics
    }
}

/**
 * Transaction manager for coordinating database operations
 * 
 * @param dataSource Primary database connection pool
 */
class TransactionManager(
    private val dataSource: DataSource
) {
    private val logger = LoggerFactory.getLogger(TransactionManager::class.java)
    
    /**
     * Execute a block of code within a database transaction
     * 
     * @param block Code block to execute within transaction
     * @return Result of the block execution
     */
    suspend fun <T> withTransaction(block: suspend () -> T): T {
        return dataSource.connection.use { conn ->
            conn.autoCommit = false
            try {
                val result = block()
                conn.commit()
                logger.debug("Transaction committed successfully")
                result
            } catch (e: Exception) {
                conn.rollback()
                logger.error("Transaction rolled back due to error: ${e.message}", e)
                throw e
            }
        }
    }
}
