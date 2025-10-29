package com.unhinged.events

/**
 * Integration extensions for ServiceBase to provide event logging capabilities
 * 
 * This file provides extension functions and utilities to integrate the event framework
 * with the existing ServiceBase class from the service-framework library.
 */

/**
 * Extension function to create an event logger for a service
 * This would be used within ServiceBase implementations
 */
public fun createServiceEventLogger(
    serviceId: String,
    version: String = "1.0.0",
    environment: String = System.getenv("ENVIRONMENT") ?: "development",
    minLogLevel: LogLevel = LogLevel.INFO
): EventLogger {
    val config = EventLoggerConfig(
        serviceId = serviceId,
        version = version,
        environment = environment,
        minLogLevel = minLogLevel,
        contextData = mapOf(
            "service_version" to version,
            "environment" to environment
        )
    )
    
    return EventLoggerFactory.createLogger(config)
}

/**
 * Service event logger wrapper that provides common service-level context
 */
public class ServiceEventLogger(
    private val serviceId: String,
    private val version: String,
    private val baseLogger: EventLogger
) : EventLogger by baseLogger {
    
    /**
     * Log service startup event
     */
    public fun logServiceStartup(port: Int, additionalContext: Map<String, Any> = emptyMap()) {
        val context = mapOf(
            "event_type" to "service.startup",
            "port" to port,
            "service_version" to version
        ) + additionalContext
        
        info("Service starting", context)
    }
    
    /**
     * Log service shutdown event
     */
    public fun logServiceShutdown(reason: String = "normal", additionalContext: Map<String, Any> = emptyMap()) {
        val context = mapOf(
            "event_type" to "service.shutdown",
            "reason" to reason,
            "service_version" to version
        ) + additionalContext
        
        info("Service shutting down", context)
    }
    
    /**
     * Log health check events
     */
    public fun logHealthCheck(
        checkName: String,
        healthy: Boolean,
        responseTimeMs: Long,
        details: Map<String, Any> = emptyMap()
    ) {
        val context = mapOf(
            "event_type" to "service.health_check",
            "check_name" to checkName,
            "healthy" to healthy,
            "response_time_ms" to responseTimeMs
        ) + details
        
        if (healthy) {
            debug("Health check passed", context)
        } else {
            warn("Health check failed", context)
        }
    }
    
    /**
     * Log gRPC request events
     */
    public fun logGrpcRequest(
        method: String,
        duration: Long,
        success: Boolean,
        errorMessage: String? = null,
        additionalContext: Map<String, Any> = emptyMap()
    ) {
        val context = mapOf(
            "event_type" to "service.grpc_request",
            "method" to method,
            "duration_ms" to duration,
            "success" to success
        ) + additionalContext
        
        val message = "gRPC request: $method"
        
        when {
            success -> info(message, context)
            errorMessage != null -> error("$message failed: $errorMessage", null, context)
            else -> warn("$message failed", context)
        }
    }
    
    /**
     * Create a logger with request context
     */
    public fun withRequestContext(
        requestId: String,
        userId: String? = null,
        sessionId: String? = null
    ): EventLogger {
        val context = mutableMapOf<String, Any>(
            "request_id" to requestId
        )
        
        userId?.let { context["user_id"] = it }
        sessionId?.let { context["session_id"] = it }
        
        return baseLogger.withContext(context)
    }
}

/**
 * Factory function to create a service event logger
 */
public fun createServiceEventLogger(
    serviceId: String,
    version: String,
    config: EventLoggerConfig? = null
): ServiceEventLogger {
    val effectiveConfig = config ?: EventLoggerConfig(
        serviceId = serviceId,
        version = version,
        contextData = mapOf(
            "service_type" to "grpc_service",
            "framework" to "unhinged-service-framework"
        )
    )
    
    val baseLogger = EventLoggerFactory.createLogger(effectiveConfig)
    return ServiceEventLogger(serviceId, version, baseLogger)
}
