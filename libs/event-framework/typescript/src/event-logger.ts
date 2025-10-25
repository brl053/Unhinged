/**
 * Unhinged Event Framework - TypeScript/JavaScript Implementation
 * 
 * Provides structured logging capabilities with OpenTelemetry integration
 * and YAML output format for consistency with existing observability patterns.
 */

import * as yaml from 'js-yaml';

/**
 * Log levels with numeric values for filtering
 */
export enum LogLevel {
    DEBUG = 0,
    INFO = 1,
    WARN = 2,
    ERROR = 3
}

/**
 * Supported output formats
 */
export enum OutputFormat {
    YAML = 'yaml',
    JSON = 'json'
}

/**
 * Structured log event data
 */
export interface LogEvent {
    timestamp: string;
    level: LogLevel;
    message: string;
    serviceId: string;
    traceId?: string;
    spanId?: string;
    metadata?: Record<string, any>;
    exception?: {
        type: string;
        message: string;
        stack?: string;
    };
    contextData?: Record<string, any>;
}

/**
 * Event logger configuration
 */
export interface EventLoggerConfig {
    serviceId: string;
    version?: string;
    environment?: string;
    minLogLevel?: LogLevel;
    outputFormat?: OutputFormat;
    includeStackTrace?: boolean;
    contextData?: Record<string, any>;
}

/**
 * Core event logging interface
 */
export interface EventLogger {
    /**
     * Log a debug event (level 0)
     */
    debug(message: string, metadata?: Record<string, any>): void;
    
    /**
     * Log an info event (level 1)
     */
    info(message: string, metadata?: Record<string, any>): void;
    
    /**
     * Log a warning event (level 2)
     */
    warn(message: string, metadata?: Record<string, any>): void;
    
    /**
     * Log an error event (level 3)
     */
    error(message: string, error?: Error, metadata?: Record<string, any>): void;
    
    /**
     * Check if a log level is enabled
     */
    isEnabled(level: LogLevel): boolean;
    
    /**
     * Create a child logger with additional context
     */
    withContext(additionalContext: Record<string, any>): EventLogger;
    
    /**
     * Create a child logger with trace context
     */
    withTrace(traceId: string, spanId: string): EventLogger;
}

/**
 * Default implementation of EventLogger with YAML output and OpenTelemetry integration
 */
export class DefaultEventLogger implements EventLogger {
    private config: Required<EventLoggerConfig>;
    private contextData: Record<string, any>;
    private traceContext?: { traceId: string; spanId: string };
    
    constructor(
        config: EventLoggerConfig,
        contextData: Record<string, any> = {},
        traceContext?: { traceId: string; spanId: string }
    ) {
        this.config = {
            version: '1.0.0',
            environment: 'development',
            minLogLevel: LogLevel.INFO,
            outputFormat: OutputFormat.YAML,
            includeStackTrace: true,
            contextData: {},
            ...config
        };
        this.contextData = contextData;
        this.traceContext = traceContext;
    }
    
    debug(message: string, metadata: Record<string, any> = {}): void {
        if (this.isEnabled(LogLevel.DEBUG)) {
            this.emitEvent(LogLevel.DEBUG, message, metadata);
        }
    }
    
    info(message: string, metadata: Record<string, any> = {}): void {
        if (this.isEnabled(LogLevel.INFO)) {
            this.emitEvent(LogLevel.INFO, message, metadata);
        }
    }
    
    warn(message: string, metadata: Record<string, any> = {}): void {
        if (this.isEnabled(LogLevel.WARN)) {
            this.emitEvent(LogLevel.WARN, message, metadata);
        }
    }
    
    error(message: string, error?: Error, metadata: Record<string, any> = {}): void {
        if (this.isEnabled(LogLevel.ERROR)) {
            this.emitEvent(LogLevel.ERROR, message, metadata, error);
        }
    }
    
    isEnabled(level: LogLevel): boolean {
        return level >= this.config.minLogLevel;
    }
    
    withContext(additionalContext: Record<string, any>): EventLogger {
        const mergedContext = { ...this.contextData, ...additionalContext };
        return new DefaultEventLogger(this.config, mergedContext, this.traceContext);
    }
    
    withTrace(traceId: string, spanId: string): EventLogger {
        const newTraceContext = { traceId, spanId };
        return new DefaultEventLogger(this.config, this.contextData, newTraceContext);
    }
    
    private emitEvent(
        level: LogLevel,
        message: string,
        metadata: Record<string, any>,
        exception?: Error
    ): void {
        const currentTrace = this.getCurrentTraceContext();
        
        const event: LogEvent = {
            timestamp: new Date().toISOString(),
            level,
            message,
            serviceId: this.config.serviceId,
            traceId: currentTrace?.traceId,
            spanId: currentTrace?.spanId,
            metadata,
            contextData: { ...this.contextData, ...this.config.contextData }
        };
        
        // Add exception details if present
        if (exception) {
            event.exception = {
                type: exception.constructor.name,
                message: exception.message
            };
            
            if (this.config.includeStackTrace && exception.stack) {
                event.exception.stack = exception.stack;
            }
        }
        
        const output = this.config.outputFormat === OutputFormat.YAML
            ? this.formatAsYaml(event)
            : this.formatAsJson(event);
        
        // Output to console for visibility
        console.log(output);
    }
    
    private getCurrentTraceContext(): { traceId: string; spanId: string } | undefined {
        // First check if we have explicit trace context
        if (this.traceContext) {
            return this.traceContext;
        }
        
        // Try to get from OpenTelemetry if available
        try {
            // Check if OpenTelemetry is available in the environment
            if (typeof window !== 'undefined' && (window as any).opentelemetry) {
                const trace = (window as any).opentelemetry.trace;
                const activeSpan = trace.getActiveSpan();
                if (activeSpan) {
                    const spanContext = activeSpan.spanContext();
                    if (spanContext.isValid) {
                        return {
                            traceId: spanContext.traceId,
                            spanId: spanContext.spanId
                        };
                    }
                }
            }
            
            // Node.js environment
            if (typeof global !== 'undefined' && (global as any).opentelemetry) {
                const trace = (global as any).opentelemetry.trace;
                const activeSpan = trace.getActiveSpan();
                if (activeSpan) {
                    const spanContext = activeSpan.spanContext();
                    if (spanContext.isValid) {
                        return {
                            traceId: spanContext.traceId,
                            spanId: spanContext.spanId
                        };
                    }
                }
            }
        } catch (e) {
            // OpenTelemetry not available or no active span
        }
        
        return undefined;
    }
    
    private formatAsYaml(event: LogEvent): string {
        const eventMap = this.buildEventMap(event);
        return yaml.dump(eventMap, { indent: 2, flowLevel: -1 });
    }
    
    private formatAsJson(event: LogEvent): string {
        const eventMap = this.buildEventMap(event);
        return JSON.stringify(eventMap, null, 2);
    }
    
    private buildEventMap(event: LogEvent): Record<string, any> {
        const map: Record<string, any> = {
            timestamp: event.timestamp,
            level: LogLevel[event.level],
            level_value: event.level,
            service_id: event.serviceId,
            message: event.message
        };
        
        // Add trace context if available
        if (event.traceId) map.trace_id = event.traceId;
        if (event.spanId) map.span_id = event.spanId;
        
        // Add metadata if present
        if (event.metadata && Object.keys(event.metadata).length > 0) {
            map.metadata = event.metadata;
        }
        
        // Add context data if present
        if (event.contextData && Object.keys(event.contextData).length > 0) {
            map.context = event.contextData;
        }
        
        // Add exception details if present
        if (event.exception) {
            map.exception = event.exception;
        }
        
        return map;
    }
}

/**
 * Create a new event logger with the specified configuration
 */
export function createLogger(config: EventLoggerConfig): EventLogger {
    return new DefaultEventLogger(config);
}

/**
 * Create a new event logger with minimal configuration
 */
export function createSimpleLogger(serviceId: string): EventLogger {
    return createLogger({ serviceId });
}

/**
 * Create a service-specific event logger
 */
export function createServiceLogger(
    serviceId: string,
    version: string = '1.0.0',
    environment: string = 'development',
    minLogLevel: LogLevel = LogLevel.INFO
): EventLogger {
    const config: EventLoggerConfig = {
        serviceId,
        version,
        environment,
        minLogLevel,
        contextData: {
            service_version: version,
            environment,
            service_type: 'javascript_service'
        }
    };
    return createLogger(config);
}
