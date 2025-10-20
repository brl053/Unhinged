package com.unhinged.framework

import com.unhinged.framework.health.*
import io.grpc.Server
import io.grpc.ServerBuilder
import io.grpc.stub.StreamObserver
import kotlinx.coroutines.*
import org.slf4j.LoggerFactory
import java.util.concurrent.TimeUnit

/**
 * Base class for all Unhinged services
 * 
 * Provides automatic health endpoints, metrics collection, and service lifecycle management.
 * Services extend this class and only need to implement business logic.
 */
public abstract class ServiceBase(
    private val serviceId: String,
    private val version: String,
    private val port: Int = 8080
) {
    
    private val logger = LoggerFactory.getLogger(this::class.java)
    private val scope = CoroutineScope(Dispatchers.Default + SupervisorJob())
    
    // Health management
    private val healthManager = HealthManager(serviceId, version, scope)
    
    // gRPC server
    private var server: Server? = null
    
    /**
     * Start the service
     */
    public open suspend fun start() {
        logger.info("Starting service: $serviceId v$version on port $port")
        
        try {
            // Initialize service-specific components
            initialize()
            
            // Start gRPC server with health endpoints
            startGrpcServer()
            
            // Register default health checks
            registerDefaultHealthChecks()
            
            // Update health status to healthy
            healthManager.updateHealthStatus(HealthStatus.HEALTHY)
            
            logger.info("Service started successfully: $serviceId")
            
        } catch (e: Exception) {
            logger.error("Failed to start service: $serviceId", e)
            healthManager.updateHealthStatus(HealthStatus.UNHEALTHY)
            throw e
        }
    }
    
    /**
     * Stop the service gracefully
     */
    public open suspend fun stop() {
        logger.info("Stopping service: $serviceId")
        
        try {
            // Update health status
            healthManager.updateHealthStatus(HealthStatus.MAINTENANCE)
            
            // Stop gRPC server
            server?.shutdown()?.awaitTermination(30, TimeUnit.SECONDS)
            
            // Cleanup service-specific resources
            cleanup()
            
            // Shutdown health manager
            healthManager.shutdown()
            
            // Cancel coroutine scope
            scope.cancel()
            
            logger.info("Service stopped: $serviceId")
            
        } catch (e: Exception) {
            logger.error("Error stopping service: $serviceId", e)
            throw e
        }
    }
    
    /**
     * Register a custom health check
     */
    protected fun registerHealthCheck(name: String, check: suspend () -> HealthCheckResult) {
        healthManager.registerHealthCheck(name, check)
    }
    
    /**
     * Register a dependency for health monitoring
     */
    protected fun registerDependency(
        name: String,
        type: String,
        endpoint: String,
        checker: suspend () -> DependencyCheckResult
    ) {
        healthManager.registerDependency(name, type, endpoint, checker)
    }
    
    /**
     * Update service health status
     */
    protected fun updateHealthStatus(status: HealthStatus) {
        healthManager.updateHealthStatus(status)
    }
    
    /**
     * Override to initialize service-specific components
     */
    protected open suspend fun initialize() {
        // Default implementation does nothing
    }
    
    /**
     * Override to cleanup service-specific resources
     */
    protected open suspend fun cleanup() {
        // Default implementation does nothing
    }
    
    /**
     * Override to register service-specific gRPC services
     */
    protected open fun registerGrpcServices(serverBuilder: ServerBuilder<*>) {
        // Default implementation does nothing
    }
    
    private fun startGrpcServer() {
        val serverBuilder = ServerBuilder.forPort(port)
        
        // Add health service
        serverBuilder.addService(HealthServiceImpl(healthManager))
        
        // Add service-specific gRPC services
        registerGrpcServices(serverBuilder)
        
        server = serverBuilder.build().start()
        
        logger.info("gRPC server started on port $port")
        
        // Add shutdown hook
        Runtime.getRuntime().addShutdownHook(Thread {
            logger.info("Shutting down gRPC server due to JVM shutdown")
            runBlocking { stop() }
        })
    }
    
    private fun registerDefaultHealthChecks() {
        // Register basic JVM health check
        registerHealthCheck("jvm-memory") {
            val runtime = Runtime.getRuntime()
            val totalMemory = runtime.totalMemory()
            val freeMemory = runtime.freeMemory()
            val usedMemory = totalMemory - freeMemory
            val usagePercent = (usedMemory.toDouble() / totalMemory.toDouble()) * 100.0
            
            val healthy = usagePercent < 90.0 // Consider unhealthy if > 90% memory usage
            
            HealthCheckResult(
                healthy = healthy,
                message = if (healthy) "Memory usage normal" else "High memory usage: ${usagePercent.toInt()}%",
                responseTimeMs = 1,
                details = mapOf(
                    "usage_percent" to usagePercent.toString(),
                    "used_bytes" to usedMemory.toString(),
                    "total_bytes" to totalMemory.toString()
                )
            )
        }
        
        // Register gRPC server health check
        registerHealthCheck("grpc-server") {
            val healthy = server?.isShutdown == false
            
            HealthCheckResult(
                healthy = healthy,
                message = if (healthy) "gRPC server running" else "gRPC server not running",
                responseTimeMs = 1
            )
        }
    }
    
    /**
     * Wait for the server to terminate
     */
    public suspend fun awaitTermination() {
        server?.awaitTermination()
    }
}

/**
 * gRPC Health Service Implementation
 */
private class HealthServiceImpl(
    private val healthManager: HealthManager
) : HealthServiceGrpc.HealthServiceImplBase() {
    
    override fun heartbeat(
        request: HeartbeatRequest,
        responseObserver: StreamObserver<HeartbeatResponse>
    ) {
        try {
            val response = healthManager.getHeartbeat()
            responseObserver.onNext(response)
            responseObserver.onCompleted()
        } catch (e: Exception) {
            responseObserver.onError(e)
        }
    }
    
    override fun diagnostics(
        request: DiagnosticsRequest,
        responseObserver: StreamObserver<DiagnosticsResponse>
    ) {
        try {
            runBlocking {
                val response = healthManager.getDiagnostics(request)
                responseObserver.onNext(response)
                responseObserver.onCompleted()
            }
        } catch (e: Exception) {
            responseObserver.onError(e)
        }
    }
}

// Placeholder for generated gRPC classes
// These would be generated from the health.proto file
private object HealthServiceGrpc {
    abstract class HealthServiceImplBase {
        open fun heartbeat(request: HeartbeatRequest, responseObserver: StreamObserver<HeartbeatResponse>) {
            throw UnsupportedOperationException("Method not implemented")
        }
        
        open fun diagnostics(request: DiagnosticsRequest, responseObserver: StreamObserver<DiagnosticsResponse>) {
            throw UnsupportedOperationException("Method not implemented")
        }
    }
}

// Placeholder StreamObserver
private interface StreamObserver<T> {
    fun onNext(value: T)
    fun onError(t: Throwable)
    fun onCompleted()
}
