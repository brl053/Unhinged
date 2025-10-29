package com.unhinged.events

import java.time.Instant

/**
 * Core event logging interface for the Unhinged event framework
 * 
 * Provides structured logging capabilities with OpenTelemetry integration
 * and YAML output format for consistency with existing observability patterns.
 */
public interface EventLogger {
    
    /**
     * Log a debug event (level 0)
     */
    public fun debug(message: String, metadata: Map<String, Any> = emptyMap())
    
    /**
     * Log an info event (level 1)
     */
    public fun info(message: String, metadata: Map<String, Any> = emptyMap())
    
    /**
     * Log a warning event (level 2)
     */
    public fun warn(message: String, metadata: Map<String, Any> = emptyMap())
    
    /**
     * Log an error event (level 3)
     */
    public fun error(message: String, throwable: Throwable? = null, metadata: Map<String, Any> = emptyMap())
    
    /**
     * Check if a log level is enabled
     */
    public fun isEnabled(level: LogLevel): Boolean
    
    /**
     * Create a child logger with additional context
     */
    public fun withContext(additionalContext: Map<String, Any>): EventLogger
    
    /**
     * Create a child logger with trace context
     */
    public fun withTrace(traceId: String, spanId: String): EventLogger
}

/**
 * Log levels with numeric values for filtering
 */
public enum class LogLevel(public val value: Int, public val displayName: String) {
    DEBUG(0, "DEBUG"),
    INFO(1, "INFO"),
    WARN(2, "WARN"),
    ERROR(3, "ERROR");
    
    public companion object {
        public fun fromValue(value: Int): LogLevel? = values().find { it.value == value }
        public fun fromName(name: String): LogLevel? = values().find { 
            it.displayName.equals(name, ignoreCase = true) 
        }
    }
}

/**
 * Structured log event data
 */
public data class LogEvent(
    val timestamp: Instant,
    val level: LogLevel,
    val message: String,
    val serviceId: String,
    val traceId: String? = null,
    val spanId: String? = null,
    val metadata: Map<String, Any> = emptyMap(),
    val exception: Throwable? = null,
    val contextData: Map<String, Any> = emptyMap()
)

/**
 * Event logger configuration
 */
public data class EventLoggerConfig(
    val serviceId: String,
    val version: String = "1.0.0",
    val environment: String = "development",
    val minLogLevel: LogLevel = LogLevel.INFO,
    val outputFormat: OutputFormat = OutputFormat.YAML,
    val includeStackTrace: Boolean = true,
    val contextData: Map<String, Any> = emptyMap()
)

/**
 * Supported output formats
 */
public enum class OutputFormat {
    YAML,
    JSON
}

/**
 * Factory for creating event loggers
 */
public object EventLoggerFactory {
    
    /**
     * Create a new event logger with the specified configuration
     */
    public fun createLogger(config: EventLoggerConfig): EventLogger {
        return DefaultEventLogger(config)
    }
    
    /**
     * Create a new event logger with minimal configuration
     */
    public fun createLogger(serviceId: String): EventLogger {
        return createLogger(EventLoggerConfig(serviceId = serviceId))
    }
}
