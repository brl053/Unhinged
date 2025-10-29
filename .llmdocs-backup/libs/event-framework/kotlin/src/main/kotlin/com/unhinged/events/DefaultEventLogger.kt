package com.unhinged.events

import io.opentelemetry.api.trace.Span
import io.opentelemetry.api.trace.SpanContext
import org.yaml.snakeyaml.DumperOptions
import org.yaml.snakeyaml.Yaml
import java.io.PrintWriter
import java.io.StringWriter
import java.time.Instant
import java.time.format.DateTimeFormatter

/**
 * Default implementation of EventLogger with YAML output and OpenTelemetry integration
 */
internal class DefaultEventLogger(
    private val config: EventLoggerConfig,
    private val contextData: Map<String, Any> = emptyMap(),
    private val traceContext: TraceContext? = null
) : EventLogger {
    
    private val yaml: Yaml by lazy {
        val options = DumperOptions().apply {
            defaultFlowStyle = DumperOptions.FlowStyle.BLOCK
            isPrettyFlow = true
            indent = 2
        }
        Yaml(options)
    }
    
    override fun debug(message: String, metadata: Map<String, Any>) {
        if (isEnabled(LogLevel.DEBUG)) {
            emitEvent(LogLevel.DEBUG, message, metadata)
        }
    }
    
    override fun info(message: String, metadata: Map<String, Any>) {
        if (isEnabled(LogLevel.INFO)) {
            emitEvent(LogLevel.INFO, message, metadata)
        }
    }
    
    override fun warn(message: String, metadata: Map<String, Any>) {
        if (isEnabled(LogLevel.WARN)) {
            emitEvent(LogLevel.WARN, message, metadata)
        }
    }
    
    override fun error(message: String, throwable: Throwable?, metadata: Map<String, Any>) {
        if (isEnabled(LogLevel.ERROR)) {
            emitEvent(LogLevel.ERROR, message, metadata, throwable)
        }
    }
    
    override fun isEnabled(level: LogLevel): Boolean {
        return level.value >= config.minLogLevel.value
    }
    
    override fun withContext(additionalContext: Map<String, Any>): EventLogger {
        val mergedContext = contextData + additionalContext
        return DefaultEventLogger(config, mergedContext, traceContext)
    }
    
    override fun withTrace(traceId: String, spanId: String): EventLogger {
        val newTraceContext = TraceContext(traceId, spanId)
        return DefaultEventLogger(config, contextData, newTraceContext)
    }
    
    private fun emitEvent(
        level: LogLevel,
        message: String,
        metadata: Map<String, Any>,
        exception: Throwable? = null
    ) {
        val currentTrace = getCurrentTraceContext()
        
        val event = LogEvent(
            timestamp = Instant.now(),
            level = level,
            message = message,
            serviceId = config.serviceId,
            traceId = currentTrace?.traceId,
            spanId = currentTrace?.spanId,
            metadata = metadata,
            exception = exception,
            contextData = contextData + config.contextData
        )
        
        val output = when (config.outputFormat) {
            OutputFormat.YAML -> formatAsYaml(event)
            OutputFormat.JSON -> formatAsJson(event)
        }
        
        // Output to stdout for CLI visibility and GUI logs tab
        println(output)
    }
    
    private fun getCurrentTraceContext(): TraceContext? {
        // First check if we have explicit trace context
        traceContext?.let { return it }
        
        // Then try to get from OpenTelemetry current span
        try {
            val currentSpan = Span.current()
            val spanContext = currentSpan.spanContext
            if (spanContext.isValid) {
                return TraceContext(
                    traceId = spanContext.traceId,
                    spanId = spanContext.spanId
                )
            }
        } catch (e: Exception) {
            // OpenTelemetry not available or no active span
        }
        
        return null
    }
    
    private fun formatAsYaml(event: LogEvent): String {
        val eventMap = buildEventMap(event)
        return yaml.dump(eventMap).trimEnd()
    }
    
    private fun formatAsJson(event: LogEvent): String {
        // Simple JSON formatting - could be enhanced with Jackson if needed
        val eventMap = buildEventMap(event)
        return eventMap.toString() // Basic implementation
    }
    
    private fun buildEventMap(event: LogEvent): Map<String, Any?> {
        val map = mutableMapOf<String, Any?>(
            "timestamp" to DateTimeFormatter.ISO_INSTANT.format(event.timestamp),
            "level" to event.level.displayName,
            "level_value" to event.level.value,
            "service_id" to event.serviceId,
            "message" to event.message
        )
        
        // Add trace context if available
        event.traceId?.let { map["trace_id"] = it }
        event.spanId?.let { map["span_id"] = it }
        
        // Add metadata if present
        if (event.metadata.isNotEmpty()) {
            map["metadata"] = event.metadata
        }
        
        // Add context data if present
        if (event.contextData.isNotEmpty()) {
            map["context"] = event.contextData
        }
        
        // Add exception details if present
        event.exception?.let { throwable ->
            val exceptionMap = mutableMapOf<String, Any>(
                "type" to throwable.javaClass.simpleName,
                "message" to (throwable.message ?: "No message")
            )
            
            if (config.includeStackTrace) {
                val stringWriter = StringWriter()
                throwable.printStackTrace(PrintWriter(stringWriter))
                exceptionMap["stack_trace"] = stringWriter.toString()
            }
            
            map["exception"] = exceptionMap
        }
        
        return map
    }
}

/**
 * Simple trace context holder
 */
internal data class TraceContext(
    val traceId: String,
    val spanId: String
)
