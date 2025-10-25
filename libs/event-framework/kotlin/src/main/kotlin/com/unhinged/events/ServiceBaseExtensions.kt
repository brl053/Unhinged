package com.unhinged.events

/**
 * Extension functions to integrate the event framework with ServiceBase
 * 
 * These extensions provide a seamless way to add structured event logging
 * to existing ServiceBase implementations without modifying the core framework.
 */

/**
 * Extension property to add event logging to any service
 * Usage: In your ServiceBase subclass, access via `this.eventLogger`
 */
public val Any.eventLogger: EventLogger
    get() = EventLoggerRegistry.getOrCreateLogger(this::class.java.simpleName)

/**
 * Registry to manage event loggers per service class
 */
public object EventLoggerRegistry {
    private val loggers = mutableMapOf<String, EventLogger>()
    
    /**
     * Get or create an event logger for a service
     */
    public fun getOrCreateLogger(serviceId: String): EventLogger {
        return loggers.getOrPut(serviceId) {
            createServiceEventLogger(
                serviceId = serviceId,
                version = System.getProperty("service.version", "1.0.0"),
                config = EventLoggerConfig(
                    serviceId = serviceId,
                    environment = System.getenv("ENVIRONMENT") ?: "development",
                    minLogLevel = LogLevel.fromName(System.getenv("LOG_LEVEL") ?: "INFO") ?: LogLevel.INFO,
                    contextData = mapOf(
                        "framework" to "unhinged-service-framework",
                        "language" to "kotlin"
                    )
                )
            ).baseLogger
        }
    }
    
    /**
     * Register a custom logger for a service
     */
    public fun registerLogger(serviceId: String, logger: EventLogger) {
        loggers[serviceId] = logger
    }
    
    /**
     * Clear all registered loggers (useful for testing)
     */
    public fun clear() {
        loggers.clear()
    }
}

/**
 * Example integration with ServiceBase pattern
 * This shows how a ServiceBase subclass would use the event framework
 */
public abstract class EventAwareServiceBase(
    private val serviceId: String,
    private val version: String,
    private val port: Int = 8080
) {
    
    // Event logger for this service
    protected val eventLogger: ServiceEventLogger = createServiceEventLogger(serviceId, version)
    
    /**
     * Enhanced start method with event logging
     */
    public open suspend fun start() {
        eventLogger.logServiceStartup(port, mapOf(
            "startup_time" to System.currentTimeMillis(),
            "jvm_version" to System.getProperty("java.version")
        ))
        
        try {
            // Initialize service-specific components
            initialize()
            
            // Start gRPC server with health endpoints
            startGrpcServer()
            
            // Register default health checks
            registerDefaultHealthChecks()
            
            eventLogger.info("Service initialization completed successfully")
            
        } catch (e: Exception) {
            eventLogger.error("Service startup failed", e, mapOf(
                "startup_phase" to "initialization",
                "port" to port
            ))
            throw e
        }
    }
    
    /**
     * Enhanced stop method with event logging
     */
    public open suspend fun stop() {
        eventLogger.logServiceShutdown("requested", mapOf(
            "uptime_ms" to (System.currentTimeMillis() - startTime),
            "graceful" to true
        ))
        
        try {
            // Cleanup service-specific resources
            cleanup()
            
            eventLogger.info("Service shutdown completed successfully")
            
        } catch (e: Exception) {
            eventLogger.error("Error during service shutdown", e)
            throw e
        }
    }
    
    /**
     * Log gRPC method calls with timing
     */
    protected fun <T> logGrpcCall(methodName: String, block: () -> T): T {
        val startTime = System.currentTimeMillis()
        val requestLogger = eventLogger.withRequestContext(
            requestId = generateRequestId(),
            userId = getCurrentUserId(),
            sessionId = getCurrentSessionId()
        )
        
        requestLogger.debug("gRPC method started", mapOf(
            "method" to methodName,
            "start_time" to startTime
        ))
        
        return try {
            val result = block()
            val duration = System.currentTimeMillis() - startTime
            
            eventLogger.logGrpcRequest(
                method = methodName,
                duration = duration,
                success = true,
                additionalContext = mapOf(
                    "result_type" to result?.javaClass?.simpleName
                )
            )
            
            result
        } catch (e: Exception) {
            val duration = System.currentTimeMillis() - startTime
            
            eventLogger.logGrpcRequest(
                method = methodName,
                duration = duration,
                success = false,
                errorMessage = e.message,
                additionalContext = mapOf(
                    "exception_type" to e.javaClass.simpleName
                )
            )
            
            throw e
        }
    }
    
    /**
     * Log health check results
     */
    protected fun logHealthCheckResult(
        checkName: String,
        healthy: Boolean,
        responseTime: Long,
        details: Map<String, Any> = emptyMap()
    ) {
        eventLogger.logHealthCheck(checkName, healthy, responseTime, details)
    }
    
    // Abstract methods to be implemented by subclasses
    protected abstract suspend fun initialize()
    protected abstract suspend fun cleanup()
    protected abstract fun startGrpcServer()
    protected abstract fun registerDefaultHealthChecks()
    
    // Helper methods (would be implemented based on actual service context)
    private fun generateRequestId(): String = java.util.UUID.randomUUID().toString()
    private fun getCurrentUserId(): String? = null // Would extract from request context
    private fun getCurrentSessionId(): String? = null // Would extract from request context
    
    private val startTime = System.currentTimeMillis()
}
