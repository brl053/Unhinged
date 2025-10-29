// ============================================================================
// Database Client Registry - Unified Database Access
// ============================================================================
//
// @file DatabaseClientRegistry.kt
// @version 1.0.0
// @author Unhinged Team
// @date 2025-10-20
// @description Unified registry for all database clients and connections
//
// This registry provides a centralized way to access all database technologies
// in the persistence platform. It manages connections, health checks, and
// provides a unified interface for database operations.
//
// ============================================================================

package com.unhinged.persistence.client

import kotlinx.coroutines.*
import kotlinx.serialization.json.Json
import java.util.concurrent.ConcurrentHashMap
import kotlin.time.Duration.Companion.seconds

/*
 * @llm-type misc.database-registry
 * @llm-does unified database client registry for multi-database persi...
 */
class DatabaseClientRegistry {
    
    private val clients = ConcurrentHashMap<DatabaseType, DatabaseClient>()
    private val healthStatus = ConcurrentHashMap<DatabaseType, HealthStatus>()
    private val connectionRetries = ConcurrentHashMap<DatabaseType, Int>()
    private val maxRetries = 3
    
    private val healthCheckScope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    
    enum class DatabaseType {
        COCKROACHDB,    // Distributed SQL
        REDIS,          // Cache and Sessions
        CASSANDRA,      // NoSQL and Column-based
        CHROMA,         // Vector Database
        SPARK           // Data Lake Processing
    }
    
    data class HealthStatus(
        val isHealthy: Boolean,
        val lastCheck: Long,
        val errorMessage: String? = null,
        val responseTime: Long = 0
    )
    
    interface DatabaseClient {
        suspend fun connect(): Boolean
        suspend fun disconnect()
        suspend fun healthCheck(): Boolean
        suspend fun execute(operation: String, params: Map<String, Any> = emptyMap()): Any?
        val type: DatabaseType
        val isConnected: Boolean
    }
    
    /**
     * Initialize the registry with all database clients
     */
    suspend fun initialize() {
        // Initialize all database clients
        registerClient(CockroachDBClient())
        registerClient(RedisClient())
        registerClient(CassandraClient())
        registerClient(ChromaClient())
        registerClient(SparkClient())
        
        // Start health monitoring
        startHealthMonitoring()
        
        println("✅ Database Client Registry initialized with ${clients.size} clients")
    }
    
    /**
     * Register a database client
     */
    private suspend fun registerClient(client: DatabaseClient) {
        try {
            if (client.connect()) {
                clients[client.type] = client
                healthStatus[client.type] = HealthStatus(true, System.currentTimeMillis())
                connectionRetries[client.type] = 0
                println("✅ Connected to ${client.type}")
            } else {
                healthStatus[client.type] = HealthStatus(false, System.currentTimeMillis(), "Failed to connect")
                println("❌ Failed to connect to ${client.type}")
            }
        } catch (e: Exception) {
            healthStatus[client.type] = HealthStatus(false, System.currentTimeMillis(), e.message)
            println("❌ Error connecting to ${client.type}: ${e.message}")
        }
    }
    
    /**
     * Get a database client by type
     */
    fun getClient(type: DatabaseType): DatabaseClient? {
        return clients[type]?.takeIf { it.isConnected }
    }
    
    /**
     * Execute operation on specific database
     */
    suspend fun execute(type: DatabaseType, operation: String, params: Map<String, Any> = emptyMap()): Any? {
        val client = getClient(type) ?: throw IllegalStateException("Client for $type not available")
        
        return try {
            client.execute(operation, params)
        } catch (e: Exception) {
            // Mark as unhealthy and attempt reconnection
            healthStatus[type] = HealthStatus(false, System.currentTimeMillis(), e.message)
            attemptReconnection(type)
            throw e
        }
    }
    
    /**
     * Get health status for all databases
     */
    fun getSystemHealth(): Map<DatabaseType, HealthStatus> {
        return healthStatus.toMap()
    }
    
    /**
     * Get health status for specific database
     */
    fun getHealth(type: DatabaseType): HealthStatus? {
        return healthStatus[type]
    }
    
    /**
     * Start periodic health monitoring
     */
    private fun startHealthMonitoring() {
        healthCheckScope.launch {
            while (isActive) {
                for ((type, client) in clients) {
                    launch {
                        checkClientHealth(type, client)
                    }
                }
                delay(30.seconds) // Check every 30 seconds
            }
        }
    }
    
    /**
     * Check health of individual client
     */
    private suspend fun checkClientHealth(type: DatabaseType, client: DatabaseClient) {
        val startTime = System.currentTimeMillis()
        
        try {
            val isHealthy = client.healthCheck()
            val responseTime = System.currentTimeMillis() - startTime
            
            healthStatus[type] = HealthStatus(
                isHealthy = isHealthy,
                lastCheck = System.currentTimeMillis(),
                responseTime = responseTime
            )
            
            if (!isHealthy) {
                println("⚠️ Health check failed for $type")
                attemptReconnection(type)
            }
            
        } catch (e: Exception) {
            val responseTime = System.currentTimeMillis() - startTime
            healthStatus[type] = HealthStatus(
                isHealthy = false,
                lastCheck = System.currentTimeMillis(),
                errorMessage = e.message,
                responseTime = responseTime
            )
            
            println("❌ Health check error for $type: ${e.message}")
            attemptReconnection(type)
        }
    }
    
    /**
     * Attempt to reconnect to a database
     */
    private suspend fun attemptReconnection(type: DatabaseType) {
        val retries = connectionRetries.getOrDefault(type, 0)
        
        if (retries < maxRetries) {
            connectionRetries[type] = retries + 1
            
            println("🔄 Attempting reconnection to $type (attempt ${retries + 1}/$maxRetries)")
            
            try {
                val client = clients[type]
                if (client != null) {
                    client.disconnect()
                    if (client.connect()) {
                        connectionRetries[type] = 0
                        healthStatus[type] = HealthStatus(true, System.currentTimeMillis())
                        println("✅ Reconnected to $type")
                    }
                }
            } catch (e: Exception) {
                println("❌ Reconnection failed for $type: ${e.message}")
            }
        } else {
            println("💀 Max reconnection attempts reached for $type")
        }
    }
    
    /**
     * Shutdown the registry and close all connections
     */
    suspend fun shutdown() {
        healthCheckScope.cancel()
        
        for ((type, client) in clients) {
            try {
                client.disconnect()
                println("✅ Disconnected from $type")
            } catch (e: Exception) {
                println("⚠️ Error disconnecting from $type: ${e.message}")
            }
        }
        
        clients.clear()
        healthStatus.clear()
        connectionRetries.clear()
    }
    
    /**
     * Get connection statistics
     */
    fun getConnectionStats(): Map<String, Any> {
        val totalClients = clients.size
        val healthyClients = healthStatus.values.count { it.isHealthy }
        val avgResponseTime = healthStatus.values
            .filter { it.isHealthy }
            .map { it.responseTime }
            .average()
            .takeIf { !it.isNaN() } ?: 0.0
        
        return mapOf(
            "total_clients" to totalClients,
            "healthy_clients" to healthyClients,
            "unhealthy_clients" to (totalClients - healthyClients),
            "avg_response_time_ms" to avgResponseTime,
            "health_percentage" to if (totalClients > 0) (healthyClients * 100.0 / totalClients) else 0.0
        )
    }
}

/**
 * Global registry instance
 */
object DatabaseRegistry {
    private val registry = DatabaseClientRegistry()
    
    suspend fun initialize() = registry.initialize()
    fun getClient(type: DatabaseClientRegistry.DatabaseType) = registry.getClient(type)
    suspend fun execute(type: DatabaseClientRegistry.DatabaseType, operation: String, params: Map<String, Any> = emptyMap()) = 
        registry.execute(type, operation, params)
    fun getSystemHealth() = registry.getSystemHealth()
    fun getHealth(type: DatabaseClientRegistry.DatabaseType) = registry.getHealth(type)
    fun getConnectionStats() = registry.getConnectionStats()
    suspend fun shutdown() = registry.shutdown()
}
