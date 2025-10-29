/**
 * Protobuf Integration for TypeScript/JavaScript
 * 
 * Provides utilities to emit events that are compatible with the existing
 * protobuf schemas defined in the observability and CDC event systems.
 */

import { EventLogger } from './event-logger';

/**
 * LLM event types matching protobuf schema
 */
export enum LLMEventType {
    STARTED = 'started',
    COMPLETED = 'completed',
    FAILED = 'failed',
    TOKEN_USAGE = 'token_usage'
}

/**
 * Service health status matching protobuf schema
 */
export enum ServiceHealthStatus {
    UNKNOWN = 'unknown',
    HEALTHY = 'healthy',
    DEGRADED = 'degraded',
    UNHEALTHY = 'unhealthy',
    MAINTENANCE = 'maintenance'
}

/**
 * State change types matching protobuf schema
 */
export enum StateChangeType {
    CREATE = 'create',
    UPDATE = 'update',
    DELETE = 'delete',
    ARCHIVE = 'archive',
    RESTORE = 'restore'
}

/**
 * Universal event emitter that creates events compatible with protobuf schemas
 */
export class UniversalEventEmitter {
    constructor(
        private eventLogger: EventLogger,
        private serviceId: string,
        private version: string = '1.0.0'
    ) {}
    
    /**
     * Emit a universal event following the CDC event pattern
     */
    emitUniversalEvent(
        eventType: string,
        payload: Record<string, any>,
        userId?: string,
        sessionId?: string,
        correlationId?: string,
        traceId?: string,
        spanId?: string
    ): void {
        const eventMetadata: Record<string, any> = {
            event_type: eventType,
            event_id: this.generateEventId(),
            event_version: '1.0.0',
            timestamp_ms: Date.now(),
            source_service: this.serviceId,
            source_version: this.version,
            environment: this.getEnvironment(),
            payload
        };
        
        // Add optional context fields
        if (userId) eventMetadata.user_id = userId;
        if (sessionId) eventMetadata.session_id = sessionId;
        if (correlationId) eventMetadata.correlation_id = correlationId;
        
        // Create logger with trace context if available
        const logger = (traceId && spanId)
            ? this.eventLogger.withTrace(traceId, spanId)
            : this.eventLogger;
        
        // Emit as structured log event
        logger.info(`Universal event: ${eventType}`, eventMetadata);
    }
    
    /**
     * Emit LLM inference event
     */
    emitLLMInferenceEvent(
        eventType: LLMEventType,
        modelName: string,
        promptTokens?: number,
        responseTokens?: number,
        latencyMs?: number,
        success: boolean = true,
        errorMessage?: string,
        userId?: string,
        sessionId?: string,
        traceId?: string,
        spanId?: string
    ): void {
        const payload: Record<string, any> = {
            model_name: modelName,
            success
        };
        
        if (promptTokens !== undefined) payload.prompt_tokens = promptTokens;
        if (responseTokens !== undefined) payload.response_tokens = responseTokens;
        if (latencyMs !== undefined) payload.latency_ms = latencyMs;
        if (errorMessage) payload.error_message = errorMessage;
        
        this.emitUniversalEvent(
            `llm.inference.${eventType}`,
            payload,
            userId,
            sessionId,
            undefined,
            traceId,
            spanId
        );
    }
    
    /**
     * Emit service health event
     */
    emitServiceHealthEvent(
        healthStatus: ServiceHealthStatus,
        checkResults?: Record<string, boolean>,
        responseTimeMs?: number,
        traceId?: string,
        spanId?: string
    ): void {
        const payload: Record<string, any> = {
            health_status: healthStatus,
            check_results: checkResults || {},
            response_time_ms: responseTimeMs,
            timestamp: new Date().toISOString()
        };
        
        this.emitUniversalEvent(
            'service.health',
            payload,
            undefined,
            undefined,
            undefined,
            traceId,
            spanId
        );
    }
    
    /**
     * Emit system state change event
     */
    emitSystemStateEvent(
        entityType: string,
        entityId: string,
        changeType: StateChangeType,
        fieldChanges?: Record<string, any>,
        userId?: string,
        traceId?: string,
        spanId?: string
    ): void {
        const payload: Record<string, any> = {
            entity_type: entityType,
            entity_id: entityId,
            change_type: changeType,
            field_changes: fieldChanges || {},
            timestamp: new Date().toISOString()
        };
        
        this.emitUniversalEvent(
            'system.state_change',
            payload,
            userId,
            undefined,
            undefined,
            traceId,
            spanId
        );
    }
    
    /**
     * Emit performance metric event
     */
    emitPerformanceEvent(
        operationName: string,
        durationMs: number,
        success: boolean,
        metadata?: Record<string, any>,
        traceId?: string,
        spanId?: string
    ): void {
        const payload: Record<string, any> = {
            operation_name: operationName,
            duration_ms: durationMs,
            success,
            metadata: metadata || {}
        };
        
        this.emitUniversalEvent(
            'performance.operation',
            payload,
            undefined,
            undefined,
            undefined,
            traceId,
            spanId
        );
    }
    
    private generateEventId(): string {
        // Simple UUID v4 implementation
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
            const r = Math.random() * 16 | 0;
            const v = c === 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }
    
    private getEnvironment(): string {
        if (typeof process !== 'undefined' && process.env) {
            return process.env.NODE_ENV || process.env.ENVIRONMENT || 'development';
        }
        return 'development';
    }
}

/**
 * Create a universal event emitter for a service
 */
export function createUniversalEmitter(
    eventLogger: EventLogger,
    serviceId: string,
    version: string = '1.0.0'
): UniversalEventEmitter {
    return new UniversalEventEmitter(eventLogger, serviceId, version);
}

/**
 * Emit a universal event directly from an EventLogger
 */
export function emitUniversalEvent(
    eventLogger: EventLogger,
    serviceId: string,
    eventType: string,
    payload: Record<string, any>,
    userId?: string,
    sessionId?: string,
    traceId?: string,
    spanId?: string
): void {
    const emitter = createUniversalEmitter(eventLogger, serviceId);
    emitter.emitUniversalEvent(eventType, payload, userId, sessionId, undefined, traceId, spanId);
}
