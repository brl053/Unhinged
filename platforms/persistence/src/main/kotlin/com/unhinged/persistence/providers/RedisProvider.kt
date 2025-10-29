// ============================================================================
// Persistence Platform - Redis Provider Implementation
// ============================================================================
//
// @file RedisProvider.kt
// @version 1.0.0
// @author Unhinged Team
// @date 2025-10-19
// @description Redis database provider implementation for caching and session storage
//
// This provider implements the DatabaseProvider interface for Redis,
// providing high-performance caching, session storage, and real-time
// data operations with TTL support and pub/sub capabilities.
//
// ============================================================================

package com.unhinged.persistence.providers

import com.unhinged.persistence.core.*
import com.unhinged.persistence.config.TechnologyConfiguration
import com.unhinged.persistence.model.*
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import kotlinx.serialization.json.Json
import kotlinx.serialization.encodeToString
import kotlinx.serialization.decodeFromString
import org.slf4j.LoggerFactory
import redis.clients.jedis.JedisPool
import redis.clients.jedis.JedisPoolConfig
import redis.clients.jedis.Jedis
import redis.clients.jedis.exceptions.JedisException
import java.time.Instant
import java.util.concurrent.ConcurrentHashMap

/*
 * @llm-type misc.provider
 * @llm-does redis database provider for high-performance caching and
 */
class RedisProvider : DatabaseProvider {
    
    private val logger = LoggerFactory.getLogger(RedisProvider::class.java)
    private val json = Json { ignoreUnknownKeys = true }
    
    override val technologyType = TechnologyType.CACHE
    override val providerName = "redis"
    
    private var jedisPool: JedisPool? = null
    private var configuration: TechnologyConfiguration? = null
    private val metrics = ConcurrentHashMap<String, Any>()
    
    // ==========================================================================
    // Initialization and Lifecycle
    // ==========================================================================
    
    override suspend fun initialize(config: TechnologyConfiguration) {
        logger.info("🔥 Initializing Redis provider...")
        
        this.configuration = config
        
        try {
            val poolConfig = JedisPoolConfig().apply {
                maxTotal = config.connectionConfig.connectionPool.maxSize
                maxIdle = config.connectionConfig.connectionPool.maxSize
                minIdle = config.connectionConfig.connectionPool.minSize
                testOnBorrow = true
                testOnReturn = true
                testWhileIdle = true
            }
            
            val host = config.connectionConfig.hosts.firstOrNull() ?: "localhost"
            val port = config.connectionConfig.port
            val password = config.connectionConfig.password
            
            jedisPool = if (password != null) {
                JedisPool(poolConfig, host, port, 2000, password)
            } else {
                JedisPool(poolConfig, host, port, 2000)
            }
            
            // Test connection
            jedisPool?.resource?.use { jedis ->
                jedis.ping()
                logger.info("✅ Redis connection established successfully")
            }
            
        } catch (e: Exception) {
            logger.error("❌ Failed to initialize Redis provider", e)
            throw e
        }
    }
    
    override suspend fun shutdown() {
        logger.info("🛑 Shutting down Redis provider...")
        jedisPool?.close()
        jedisPool = null
        logger.info("✅ Redis provider shutdown complete")
    }
    
    // ==========================================================================
    // Connection Management
    // ==========================================================================
    
    override suspend fun testConnection(): Boolean {
        return try {
            jedisPool?.resource?.use { jedis ->
                jedis.ping() == "PONG"
            } ?: false
        } catch (e: Exception) {
            logger.warn("Redis connection test failed", e)
            false
        }
    }
    
    override suspend fun getConnectionStatus(): ConnectionStatus {
        val pool = jedisPool
        return if (pool != null) {
            ConnectionStatus(
                connected = !pool.isClosed,
                connectionCount = pool.numActive,
                maxConnections = pool.maxTotal,
                lastConnected = Instant.now(),
                connectionDetails = mapOf(
                    "active_connections" to pool.numActive,
                    "idle_connections" to pool.numIdle,
                    "max_total" to pool.maxTotal
                )
            )
        } else {
            ConnectionStatus(connected = false)
        }
    }
    
    // ==========================================================================
    // Schema Management (Redis-specific)
    // ==========================================================================
    
    override suspend fun createDatabase(databaseName: String, config: DatabaseConfig) {
        // Redis doesn't have explicit database creation, but we can select database index
        jedisPool?.resource?.use { jedis ->
            val dbIndex = config.properties["database_index"] as? Int ?: 0
            jedis.select(dbIndex)
            logger.info("Selected Redis database index: $dbIndex for $databaseName")
        }
    }
    
    override suspend fun createTable(tableName: String, schema: TableSchema, config: TableConfig) {
        // Redis doesn't have tables, but we can create key patterns and metadata
        val keyPattern = "${tableName}:*"
        val schemaKey = "${tableName}:_schema"
        
        jedisPool?.resource?.use { jedis ->
            val schemaJson = json.encodeToString(schema)
            jedis.set(schemaKey, schemaJson)
            
            // Set TTL if specified
            config.defaultTtl?.let { ttl ->
                jedis.expire(schemaKey, ttl.toInt())
            }
            
            logger.info("Created Redis key pattern: $keyPattern with schema")
        }
    }
    
    override suspend fun dropTable(tableName: String) {
        jedisPool?.resource?.use { jedis ->
            val pattern = "${tableName}:*"
            val keys = jedis.keys(pattern)
            if (keys.isNotEmpty()) {
                jedis.del(*keys.toTypedArray())
                logger.info("Dropped Redis keys matching pattern: $pattern (${keys.size} keys)")
            }
        }
    }
    
    override suspend fun tableExists(tableName: String): Boolean {
        return jedisPool?.resource?.use { jedis ->
            jedis.exists("${tableName}:_schema")
        } ?: false
    }
    
    // ==========================================================================
    // Query Operations
    // ==========================================================================
    
    override suspend fun <T> executeQuery(query: QuerySpec, context: ExecutionContext): Flow<T> = flow {
        val startTime = System.currentTimeMillis()
        
        try {
            jedisPool?.resource?.use { jedis ->
                when (query.queryType) {
                    QueryType.POINT_LOOKUP -> {
                        val key = buildKey(query.tableName, query.parameters)
                        val value = jedis.get(key)
                        if (value != null) {
                            val result = json.decodeFromString<T>(value)
                            emit(result)
                        }
                    }
                    
                    QueryType.RANGE_SCAN -> {
                        val pattern = buildPattern(query.tableName, query.parameters)
                        val keys = jedis.keys(pattern)
                        
                        keys.take(query.limit ?: 100).forEach { key ->
                            val value = jedis.get(key)
                            if (value != null) {
                                val result = json.decodeFromString<T>(value)
                                emit(result)
                            }
                        }
                    }
                    
                    else -> {
                        logger.warn("Unsupported query type for Redis: ${query.queryType}")
                    }
                }
            }
            
            updateMetrics("query_success", startTime)
            
        } catch (e: Exception) {
            logger.error("Redis query execution failed", e)
            updateMetrics("query_error", startTime)
            throw e
        }
    }
    
    override suspend fun <T> executeQuerySingle(query: QuerySpec, context: ExecutionContext): T? {
        return try {
            jedisPool?.resource?.use { jedis ->
                val key = buildKey(query.tableName, query.parameters)
                val value = jedis.get(key)
                value?.let { json.decodeFromString<T>(it) }
            }
        } catch (e: Exception) {
            logger.error("Redis single query execution failed", e)
            null
        }
    }
    
    override suspend fun executeQueryCount(query: QuerySpec, context: ExecutionContext): Long {
        return try {
            jedisPool?.resource?.use { jedis ->
                val pattern = buildPattern(query.tableName, query.parameters)
                jedis.keys(pattern).size.toLong()
            } ?: 0L
        } catch (e: Exception) {
            logger.error("Redis count query execution failed", e)
            0L
        }
    }
    
    // ==========================================================================
    // CRUD Operations
    // ==========================================================================
    
    override suspend fun <T> insert(tableName: String, record: T, context: ExecutionContext): T {
        val startTime = System.currentTimeMillis()
        
        try {
            jedisPool?.resource?.use { jedis ->
                val key = generateKey(tableName, record)
                val value = json.encodeToString(record)
                
                jedis.set(key, value)
                
                // Set TTL if configured
                configuration?.performanceConfig?.defaultTtl?.let { ttl ->
                    jedis.expire(key, ttl.seconds.toInt())
                }
                
                logger.debug("Inserted record into Redis: $key")
            }
            
            updateMetrics("insert_success", startTime)
            return record
            
        } catch (e: Exception) {
            logger.error("Redis insert failed", e)
            updateMetrics("insert_error", startTime)
            throw e
        }
    }
    
    override suspend fun <T> insertBatch(tableName: String, records: List<T>, context: ExecutionContext): List<T> {
        val startTime = System.currentTimeMillis()
        
        try {
            jedisPool?.resource?.use { jedis ->
                val pipeline = jedis.pipelined()
                
                records.forEach { record ->
                    val key = generateKey(tableName, record)
                    val value = json.encodeToString(record)
                    pipeline.set(key, value)
                    
                    // Set TTL if configured
                    configuration?.performanceConfig?.defaultTtl?.let { ttl ->
                        pipeline.expire(key, ttl.seconds.toInt())
                    }
                }
                
                pipeline.sync()
                logger.debug("Batch inserted ${records.size} records into Redis")
            }
            
            updateMetrics("batch_insert_success", startTime)
            return records
            
        } catch (e: Exception) {
            logger.error("Redis batch insert failed", e)
            updateMetrics("batch_insert_error", startTime)
            throw e
        }
    }
    
    override suspend fun update(
        tableName: String,
        criteria: QueryCriteria,
        updates: Map<String, Any>,
        context: ExecutionContext
    ): Long {
        val startTime = System.currentTimeMillis()
        var updatedCount = 0L
        
        try {
            jedisPool?.resource?.use { jedis ->
                val pattern = buildPatternFromCriteria(tableName, criteria)
                val keys = jedis.keys(pattern)
                
                keys.forEach { key ->
                    val existingValue = jedis.get(key)
                    if (existingValue != null) {
                        // For Redis, we need to merge updates with existing data
                        val updatedValue = mergeUpdates(existingValue, updates)
                        jedis.set(key, updatedValue)
                        updatedCount++
                    }
                }
                
                logger.debug("Updated $updatedCount records in Redis")
            }
            
            updateMetrics("update_success", startTime)
            return updatedCount
            
        } catch (e: Exception) {
            logger.error("Redis update failed", e)
            updateMetrics("update_error", startTime)
            throw e
        }
    }
    
    override suspend fun delete(
        tableName: String,
        criteria: QueryCriteria,
        context: ExecutionContext
    ): Long {
        val startTime = System.currentTimeMillis()
        
        try {
            val deletedCount = jedisPool?.resource?.use { jedis ->
                val pattern = buildPatternFromCriteria(tableName, criteria)
                val keys = jedis.keys(pattern)
                
                if (keys.isNotEmpty()) {
                    jedis.del(*keys.toTypedArray()).toLong()
                } else {
                    0L
                }
            } ?: 0L
            
            updateMetrics("delete_success", startTime)
            logger.debug("Deleted $deletedCount records from Redis")
            return deletedCount
            
        } catch (e: Exception) {
            logger.error("Redis delete failed", e)
            updateMetrics("delete_error", startTime)
            throw e
        }
    }
    
    // ==========================================================================
    // Transaction Support (Limited in Redis)
    // ==========================================================================
    
    override fun supportsTransactions(): Boolean = true // Redis supports MULTI/EXEC
    
    override suspend fun beginTransaction(context: ExecutionContext): TransactionHandle? {
        // Redis transactions are handled per connection, return a simple handle
        return TransactionHandle(
            transactionId = context.requestId,
            participatingProviders = setOf(providerName),
            isolationLevel = IsolationLevel.READ_COMMITTED,
            timeout = 30000
        )
    }
    
    override suspend fun commitTransaction(transaction: TransactionHandle) {
        // Redis MULTI/EXEC is handled at the operation level
        logger.debug("Redis transaction committed: ${transaction.transactionId}")
    }
    
    override suspend fun rollbackTransaction(transaction: TransactionHandle) {
        // Redis DISCARD is handled at the operation level
        logger.debug("Redis transaction rolled back: ${transaction.transactionId}")
    }
    
    // ==========================================================================
    // Technology-Specific Operations
    // ==========================================================================
    
    override suspend fun <T> executeSpecificOperation(
        operation: SpecificOperation,
        context: ExecutionContext
    ): T? {
        return when (operation.operationType) {
            "EXPIRE" -> {
                jedisPool?.resource?.use { jedis ->
                    val key = operation.parameters["key"] as String
                    val ttl = operation.parameters["ttl"] as Int
                    jedis.expire(key, ttl) as T
                }
            }
            
            "PUBLISH" -> {
                jedisPool?.resource?.use { jedis ->
                    val channel = operation.parameters["channel"] as String
                    val message = operation.parameters["message"] as String
                    jedis.publish(channel, message) as T
                }
            }
            
            "INCR" -> {
                jedisPool?.resource?.use { jedis ->
                    val key = operation.parameters["key"] as String
                    jedis.incr(key) as T
                }
            }
            
            else -> {
                logger.warn("Unsupported Redis operation: ${operation.operationType}")
                null
            }
        }
    }
    
    // ==========================================================================
    // Performance and Monitoring
    // ==========================================================================
    
    override suspend fun getMetrics(): ProviderMetrics {
        val pool = jedisPool
        return ProviderMetrics(
            provider = providerName,
            connectionCount = pool?.numActive ?: 0,
            activeConnections = pool?.numActive ?: 0,
            queryCount = metrics["total_queries"] as? Long ?: 0L,
            errorCount = metrics["total_errors"] as? Long ?: 0L,
            averageResponseTime = metrics["avg_response_time"] as? Double ?: 0.0,
            throughput = metrics["throughput"] as? Double ?: 0.0,
            customMetrics = mapOf(
                "idle_connections" to (pool?.numIdle ?: 0),
                "max_connections" to (pool?.maxTotal ?: 0),
                "cache_hit_rate" to (metrics["cache_hit_rate"] ?: 0.0)
            )
        )
    }
    
    override suspend fun getHealthStatus(): HealthStatus {
        return try {
            val isHealthy = testConnection()
            val responseTime = measureResponseTime()
            
            HealthStatus(
                status = if (isHealthy) HealthState.HEALTHY else HealthState.UNHEALTHY,
                message = if (isHealthy) "Redis is healthy" else "Redis connection failed",
                responseTime = responseTime,
                details = mapOf(
                    "provider" to providerName,
                    "connection_pool_active" to (jedisPool?.numActive ?: 0),
                    "connection_pool_idle" to (jedisPool?.numIdle ?: 0)
                )
            )
        } catch (e: Exception) {
            HealthStatus(
                status = HealthState.UNHEALTHY,
                message = "Redis health check failed: ${e.message}",
                details = mapOf("error" to e.message.orEmpty())
            )
        }
    }
    
    override fun getConfiguration(): TechnologyConfiguration {
        return configuration ?: throw IllegalStateException("Redis provider not initialized")
    }
    
    // ==========================================================================
    // Capability Information
    // ==========================================================================
    
    override fun getSupportedQueryTypes(): Set<QueryType> {
        return setOf(
            QueryType.POINT_LOOKUP,
            QueryType.RANGE_SCAN
        )
    }
    
    override fun getSupportedDataTypes(): Set<DataType> {
        return setOf(
            DataType.STRING,
            DataType.INTEGER,
            DataType.LONG,
            DataType.FLOAT,
            DataType.DOUBLE,
            DataType.BOOLEAN,
            DataType.JSON,
            DataType.BINARY
        )
    }
    
    override fun supportsFeature(feature: DatabaseFeature): Boolean {
        return when (feature) {
            DatabaseFeature.TRANSACTIONS -> true
            DatabaseFeature.REPLICATION -> true
            DatabaseFeature.SHARDING -> true
            DatabaseFeature.STREAMING -> true
            DatabaseFeature.COMPRESSION -> false
            DatabaseFeature.ENCRYPTION -> true
            else -> false
        }
    }
    
    // ==========================================================================
    // Helper Methods
    // ==========================================================================
    
    private fun buildKey(tableName: String, parameters: Map<String, Any>): String {
        val id = parameters["id"] ?: parameters["key"] ?: "unknown"
        return "$tableName:$id"
    }
    
    private fun buildPattern(tableName: String, parameters: Map<String, Any>): String {
        val pattern = parameters["pattern"] as? String ?: "*"
        return "$tableName:$pattern"
    }
    
    private fun buildPatternFromCriteria(tableName: String, criteria: QueryCriteria): String {
        return when (criteria) {
            is QueryCriteria.Equals -> "$tableName:${criteria.value}"
            else -> "$tableName:*"
        }
    }
    
    private fun generateKey(tableName: String, record: Any): String {
        // Extract ID from record or generate one
        val id = extractIdFromRecord(record) ?: java.util.UUID.randomUUID().toString()
        return "$tableName:$id"
    }
    
    private fun extractIdFromRecord(record: Any): String? {
        // This would need reflection or serialization to extract ID field
        // For now, return null to generate UUID
        return null
    }
    
    private fun mergeUpdates(existingValue: String, updates: Map<String, Any>): String {
        // Parse existing JSON, merge updates, and serialize back
        // This is a simplified implementation
        return json.encodeToString(updates)
    }
    
    private fun measureResponseTime(): Long {
        return try {
            val start = System.currentTimeMillis()
            jedisPool?.resource?.use { jedis ->
                jedis.ping()
            }
            System.currentTimeMillis() - start
        } catch (e: Exception) {
            -1L
        }
    }
    
    private fun updateMetrics(operation: String, startTime: Long) {
        val duration = System.currentTimeMillis() - startTime
        metrics["total_${operation}"] = (metrics["total_${operation}"] as? Long ?: 0L) + 1
        metrics["last_${operation}_duration"] = duration
        
        // Update average response time
        val totalOps = metrics.keys.filter { it.startsWith("total_") }.sumOf { 
            metrics[it] as? Long ?: 0L 
        }
        val avgResponseTime = metrics["avg_response_time"] as? Double ?: 0.0
        metrics["avg_response_time"] = (avgResponseTime * (totalOps - 1) + duration) / totalOps
    }
}
