package com.unhinged.platform.example

import com.unhinged.framework.ServiceBase
import com.unhinged.framework.health.HealthCheckResult
import com.unhinged.framework.health.HealthStatus
import com.unhinged.framework.health.DependencyCheckResult
import io.grpc.ServerBuilder
import kotlinx.coroutines.delay
import kotlinx.coroutines.runBlocking
import org.slf4j.LoggerFactory
import kotlin.random.Random

/**
 * Example service demonstrating the Unhinged Service Framework
 * 
 * Shows how to:
 * - Extend ServiceBase for automatic health endpoints
 * - Register custom health checks
 * - Register dependency health monitoring
 * - Implement business logic with minimal boilerplate
 */
class ExampleService : ServiceBase(
    serviceId = "example-service",
    version = "1.0.0",
    port = 8090
) {
    
    private val logger = LoggerFactory.getLogger(ExampleService::class.java)
    
    // Simulated business components
    private var databaseConnected = true
    private var cacheConnected = true
    private var processingEnabled = true
    
    override suspend fun initialize() {
        logger.info("Initializing Example Service...")
        
        // Simulate initialization work
        delay(100)
        
        // Register custom health checks
        registerCustomHealthChecks()
        
        // Register dependency monitoring
        registerDependencies()
        
        logger.info("Example Service initialized")
    }
    
    override suspend fun cleanup() {
        logger.info("Cleaning up Example Service...")
        
        // Simulate cleanup work
        processingEnabled = false
        databaseConnected = false
        cacheConnected = false
        
        logger.info("Example Service cleaned up")
    }
    
    override fun registerGrpcServices(serverBuilder: ServerBuilder<*>) {
        // Add business-specific gRPC services here
        // serverBuilder.addService(ExampleBusinessServiceImpl())
        logger.info("Registered business gRPC services")
    }
    
    private fun registerCustomHealthChecks() {
        // Register processing health check
        registerHealthCheck("processing-engine") {
            val startTime = System.currentTimeMillis()
            
            // Simulate health check work
            delay(Random.nextLong(1, 10))
            
            val responseTime = System.currentTimeMillis() - startTime
            val healthy = processingEnabled
            
            HealthCheckResult(
                healthy = healthy,
                message = if (healthy) "Processing engine operational" else "Processing engine disabled",
                responseTimeMs = responseTime,
                details = mapOf(
                    "enabled" to processingEnabled.toString(),
                    "last_check" to System.currentTimeMillis().toString()
                )
            )
        }
        
        // Register business logic health check
        registerHealthCheck("business-logic") {
            val startTime = System.currentTimeMillis()
            
            // Simulate complex business logic health check
            delay(Random.nextLong(5, 50))
            
            val responseTime = System.currentTimeMillis() - startTime
            val healthy = databaseConnected && cacheConnected
            
            HealthCheckResult(
                healthy = healthy,
                message = when {
                    !databaseConnected -> "Database connection failed"
                    !cacheConnected -> "Cache connection failed"
                    else -> "Business logic healthy"
                },
                responseTimeMs = responseTime,
                details = mapOf(
                    "database_connected" to databaseConnected.toString(),
                    "cache_connected" to cacheConnected.toString()
                )
            )
        }
    }
    
    private fun registerDependencies() {
        // Register database dependency
        registerDependency(
            name = "postgres-database",
            type = "database",
            endpoint = "localhost:5432"
        ) {
            val startTime = System.currentTimeMillis()
            
            // Simulate database health check
            delay(Random.nextLong(10, 100))
            
            val responseTime = System.currentTimeMillis() - startTime
            
            DependencyCheckResult(
                healthy = databaseConnected,
                responseTimeMs = responseTime,
                version = if (databaseConnected) "PostgreSQL 15.4" else null,
                errorMessage = if (!databaseConnected) "Connection timeout" else null
            )
        }
        
        // Register cache dependency
        registerDependency(
            name = "redis-cache",
            type = "cache",
            endpoint = "localhost:6379"
        ) {
            val startTime = System.currentTimeMillis()
            
            // Simulate cache health check
            delay(Random.nextLong(5, 30))
            
            val responseTime = System.currentTimeMillis() - startTime
            
            DependencyCheckResult(
                healthy = cacheConnected,
                responseTimeMs = responseTime,
                version = if (cacheConnected) "Redis 7.2.0" else null,
                errorMessage = if (!cacheConnected) "Connection refused" else null
            )
        }
        
        // Register downstream service dependency
        registerDependency(
            name = "llm-service",
            type = "service",
            endpoint = "localhost:8080"
        ) {
            val startTime = System.currentTimeMillis()
            
            // Simulate downstream service health check
            delay(Random.nextLong(20, 200))
            
            val responseTime = System.currentTimeMillis() - startTime
            val healthy = Random.nextBoolean() // Simulate intermittent issues
            
            DependencyCheckResult(
                healthy = healthy,
                responseTimeMs = responseTime,
                version = if (healthy) "LLM Service 2.1.0" else null,
                errorMessage = if (!healthy) "Service temporarily unavailable" else null
            )
        }
    }
    
    /**
     * Simulate business operations that affect health
     */
    fun simulateOperations() {
        // Simulate database connection issues
        if (Random.nextDouble() < 0.1) {
            databaseConnected = !databaseConnected
            logger.info("Database connection changed: $databaseConnected")
            
            // Update overall health based on critical dependencies
            if (!databaseConnected) {
                updateHealthStatus(HealthStatus.UNHEALTHY)
            } else if (!cacheConnected) {
                updateHealthStatus(HealthStatus.DEGRADED)
            } else {
                updateHealthStatus(HealthStatus.HEALTHY)
            }
        }
        
        // Simulate cache connection issues
        if (Random.nextDouble() < 0.05) {
            cacheConnected = !cacheConnected
            logger.info("Cache connection changed: $cacheConnected")
            
            // Cache is non-critical, so only degrade service
            if (!databaseConnected) {
                updateHealthStatus(HealthStatus.UNHEALTHY)
            } else if (!cacheConnected) {
                updateHealthStatus(HealthStatus.DEGRADED)
            } else {
                updateHealthStatus(HealthStatus.HEALTHY)
            }
        }
    }
}

/**
 * Main function to run the example service
 */
fun main() {
    val service = ExampleService()
    
    runBlocking {
        try {
            // Start the service
            service.start()
            
            // Simulate operations in background
            kotlinx.coroutines.launch {
                while (true) {
                    delay(5000) // Every 5 seconds
                    service.simulateOperations()
                }
            }
            
            println("Example Service started successfully!")
            println("Health endpoints available:")
            println("  Heartbeat: http://localhost:8090/health/heartbeat")
            println("  Diagnostics: http://localhost:8090/health/diagnostics")
            println("Press Ctrl+C to stop...")
            
            // Wait for termination
            service.awaitTermination()
            
        } catch (e: Exception) {
            println("Failed to start service: ${e.message}")
            e.printStackTrace()
        } finally {
            service.stop()
        }
    }
}
