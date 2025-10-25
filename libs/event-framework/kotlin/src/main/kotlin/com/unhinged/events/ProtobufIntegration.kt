package com.unhinged.events

import java.time.Instant

/**
 * Integration helpers for protobuf event schemas
 * 
 * Provides utilities to emit events that are compatible with the existing
 * protobuf schemas defined in the observability and CDC event systems.
 */

/**
 * Universal event emitter that creates events compatible with protobuf schemas
 */
public class UniversalEventEmitter(
    private val eventLogger: EventLogger,
    private val serviceId: String,
    private val version: String
) {
    
    /**
     * Emit a universal event following the CDC event pattern
     */
    public fun emitUniversalEvent(
        eventType: String,
        payload: Map<String, Any>,
        userId: String? = null,
        sessionId: String? = null,
        correlationId: String? = null,
        traceId: String? = null,
        spanId: String? = null
    ) {
        val eventMetadata = mutableMapOf<String, Any>(
            "event_type" to eventType,
            "event_id" to generateEventId(),
            "event_version" to "1.0.0",
            "timestamp_ms" to System.currentTimeMillis(),
            "source_service" to serviceId,
            "source_version" to version,
            "environment" to (System.getenv("ENVIRONMENT") ?: "development")
        )
        
        // Add optional context fields
        userId?.let { eventMetadata["user_id"] = it }
        sessionId?.let { eventMetadata["session_id"] = it }
        correlationId?.let { eventMetadata["correlation_id"] = it }
        
        // Add payload
        eventMetadata["payload"] = payload
        
        // Create logger with trace context if available
        val logger = if (traceId != null && spanId != null) {
            eventLogger.withTrace(traceId, spanId)
        } else {
            eventLogger
        }
        
        // Emit as structured log event
        logger.info("Universal event: $eventType", eventMetadata)
    }
    
    /**
     * Emit LLM inference event
     */
    public fun emitLLMInferenceEvent(
        eventType: LLMEventType,
        modelName: String,
        promptTokens: Int? = null,
        responseTokens: Int? = null,
        latencyMs: Long? = null,
        success: Boolean = true,
        errorMessage: String? = null,
        userId: String? = null,
        sessionId: String? = null,
        traceId: String? = null,
        spanId: String? = null
    ) {
        val payload = mutableMapOf<String, Any>(
            "model_name" to modelName,
            "success" to success
        )
        
        promptTokens?.let { payload["prompt_tokens"] = it }
        responseTokens?.let { payload["response_tokens"] = it }
        latencyMs?.let { payload["latency_ms"] = it }
        errorMessage?.let { payload["error_message"] = it }
        
        emitUniversalEvent(
            eventType = "llm.inference.${eventType.name.lowercase()}",
            payload = payload,
            userId = userId,
            sessionId = sessionId,
            traceId = traceId,
            spanId = spanId
        )
    }
    
    /**
     * Emit service health event
     */
    public fun emitServiceHealthEvent(
        healthStatus: ServiceHealthStatus,
        checkResults: Map<String, Boolean> = emptyMap(),
        responseTimeMs: Long? = null,
        traceId: String? = null,
        spanId: String? = null
    ) {
        val payload = mapOf(
            "health_status" to healthStatus.name,
            "check_results" to checkResults,
            "response_time_ms" to responseTimeMs,
            "timestamp" to Instant.now().toString()
        )
        
        emitUniversalEvent(
            eventType = "service.health",
            payload = payload,
            traceId = traceId,
            spanId = spanId
        )
    }
    
    /**
     * Emit system state change event
     */
    public fun emitSystemStateEvent(
        entityType: String,
        entityId: String,
        changeType: StateChangeType,
        fieldChanges: Map<String, Any> = emptyMap(),
        userId: String? = null,
        traceId: String? = null,
        spanId: String? = null
    ) {
        val payload = mapOf(
            "entity_type" to entityType,
            "entity_id" to entityId,
            "change_type" to changeType.name,
            "field_changes" to fieldChanges,
            "timestamp" to Instant.now().toString()
        )
        
        emitUniversalEvent(
            eventType = "system.state_change",
            payload = payload,
            userId = userId,
            traceId = traceId,
            spanId = spanId
        )
    }
    
    /**
     * Emit performance metric event
     */
    public fun emitPerformanceEvent(
        operationName: String,
        durationMs: Long,
        success: Boolean,
        metadata: Map<String, Any> = emptyMap(),
        traceId: String? = null,
        spanId: String? = null
    ) {
        val payload = mapOf(
            "operation_name" to operationName,
            "duration_ms" to durationMs,
            "success" to success,
            "metadata" to metadata
        )
        
        emitUniversalEvent(
            eventType = "performance.operation",
            payload = payload,
            traceId = traceId,
            spanId = spanId
        )
    }
    
    private fun generateEventId(): String = java.util.UUID.randomUUID().toString()
}

/**
 * LLM event types matching protobuf schema
 */
public enum class LLMEventType {
    STARTED,
    COMPLETED,
    FAILED,
    TOKEN_USAGE
}

/**
 * Service health status matching protobuf schema
 */
public enum class ServiceHealthStatus {
    UNKNOWN,
    HEALTHY,
    DEGRADED,
    UNHEALTHY,
    MAINTENANCE
}

/**
 * State change types matching protobuf schema
 */
public enum class StateChangeType {
    CREATE,
    UPDATE,
    DELETE,
    ARCHIVE,
    RESTORE
}

/**
 * Extension function to create a universal event emitter for a service
 */
public fun EventLogger.createUniversalEmitter(
    serviceId: String,
    version: String = "1.0.0"
): UniversalEventEmitter {
    return UniversalEventEmitter(this, serviceId, version)
}

/**
 * Extension function to emit events directly from an EventLogger
 */
public fun EventLogger.emitUniversalEvent(
    serviceId: String,
    eventType: String,
    payload: Map<String, Any>,
    userId: String? = null,
    sessionId: String? = null,
    traceId: String? = null,
    spanId: String? = null
) {
    val emitter = createUniversalEmitter(serviceId)
    emitter.emitUniversalEvent(eventType, payload, userId, sessionId, null, traceId, spanId)
}
