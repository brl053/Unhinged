# @unhinged/observability - Unified Logging Library

**Version**: 1.0.0
**Date**: 2025-10-06
**Author**: Unhinged Team

## 🎯 **Overview**

Multi-language unified logging library with Unix-style permission flags for output destinations. Extends our existing `@unhinged/events` architecture with OpenTelemetry compliance and flexible destination routing.

## 🏗️ **Permission Flag System**

### **Flag Definitions (Unix-style)**

```
C = Console output (stdout/stderr)
D = CDC persistence (Kafka events)
L = Data Lake storage (Parquet/Delta)
```

### **Flag Combinations**

```
C   = Console only (development default)
CD  = Console + CDC events
CL  = Console + Data lake
CDL = All destinations (production default)
D   = CDC only (background services)
L   = Data lake only (analytics)
DL  = CDC + Data lake (no console)
```

### **Environment Defaults**

```typescript
// Default configurations per environment
const DEFAULT_FLAGS = {
  development: 'C',      // Console only for dev
  staging: 'CD',         // Console + CDC for staging
  production: 'CDL',     // All destinations for prod
  test: 'C',            // Console only for tests
  analytics: 'L',       // Data lake only for analytics
};
```

## 🌐 **Multi-Language Support**

### **TypeScript/JavaScript Usage**

```typescript
import { createLogger } from '@unhinged/observability';

// Use environment defaults
const logger = createLogger({ service: 'chat-service' });

// Override flags
const analyticsLogger = createLogger({
  service: 'analytics-service',
  flags: 'L'  // Data lake only
});

// Runtime flag changes
const debugLogger = createLogger({
  service: 'debug-service',
  flags: process.env.DEBUG ? 'CDL' : 'C'
});

// Usage with OpenTelemetry context
logger.info('User logged in', { userId: '123', method: 'oauth' });
logger.error('Database connection failed', dbError, { retryCount: 3 });
```

### **Kotlin Implementation**

```kotlin
// packages/observability/src/kotlin/UnhingedLogger.kt
package com.unhinged.observability

import io.opentelemetry.api.trace.Span
import io.opentelemetry.api.trace.StatusCode
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.launch
import kotlinx.serialization.Serializable
import java.time.Instant

@Serializable
data class LogEntry(
    val timestamp: String,
    val level: LogLevel,
    val message: String,
    val service: String,
    val traceId: String? = null,
    val spanId: String? = null,
    val userId: String? = null,
    val sessionId: String? = null,
    val metadata: Map<String, Any>? = null
)

enum class LogLevel { DEBUG, INFO, WARN, ERROR, FATAL }

data class LoggerConfig(
    val service: String,
    val flags: String? = null,
    val environment: String? = null,
    val defaultMetadata: Map<String, Any> = emptyMap()
)

class UnhingedLogger(private val config: LoggerConfig) {
    private val flags: Set<Char>
    private val eventEmitter: EventEmitter
    private val coroutineScope: CoroutineScope

    init {
        val flagString = config.flags ?: getDefaultFlags(config.environment)
        flags = flagString.toSet()
        eventEmitter = EventEmitter()
        coroutineScope = CoroutineScope(Dispatchers.IO)
        setupDestinations()
    }

    private fun getDefaultFlags(environment: String?): String {
        val env = environment ?: System.getenv("ENVIRONMENT") ?: "development"
        return when (env) {
            "development" -> "C"
            "staging" -> "CD"
            "production" -> "CDL"
            "test" -> "C"
            "analytics" -> "L"
            else -> "C"
        }
    }

    fun info(message: String, metadata: Map<String, Any>? = null) {
        log(LogLevel.INFO, message, metadata)
    }

    fun error(message: String, throwable: Throwable? = null, metadata: Map<String, Any>? = null) {
        val errorMetadata = throwable?.let {
            mapOf(
                "error" to mapOf(
                    "class" to it.javaClass.simpleName,
                    "message" to it.message,
                    "stackTrace" to it.stackTraceToString()
                )
            ) + (metadata ?: emptyMap())
        } ?: metadata

        log(LogLevel.ERROR, message, errorMetadata)

        // Mark span as error if active
        val span = Span.current()
        if (span.isRecording) {
            span.setStatus(StatusCode.ERROR, message)
            throwable?.let { span.recordException(it) }
        }
    }

    private fun log(level: LogLevel, message: String, metadata: Map<String, Any>?) {
        val entry = createLogEntry(level, message, metadata)

        coroutineScope.launch {
            if ('C' in flags) outputToConsole(entry)
            if ('D' in flags) outputToCDC(entry)
            if ('L' in flags) outputToDataLake(entry)
        }
    }

    private fun createLogEntry(level: LogLevel, message: String, metadata: Map<String, Any>?): LogEntry {
        val span = Span.current()
        val spanContext = span.spanContext

        return LogEntry(
            timestamp = Instant.now().toString(),
            level = level,
            message = message,
            service = config.service,
            traceId = if (spanContext.isValid) spanContext.traceId else null,
            spanId = if (spanContext.isValid) spanContext.spanId else null,
            metadata = (config.defaultMetadata + (metadata ?: emptyMap()))
        )
    }

    private suspend fun outputToConsole(entry: LogEntry) {
        val color = when (entry.level) {
            LogLevel.DEBUG -> "\u001B[36m"  // Cyan
            LogLevel.INFO -> "\u001B[32m"   // Green
            LogLevel.WARN -> "\u001B[33m"   // Yellow
            LogLevel.ERROR -> "\u001B[31m"  // Red
            LogLevel.FATAL -> "\u001B[35m"  // Magenta
        }
        val reset = "\u001B[0m"
        val traceInfo = entry.traceId?.let { " [${it.take(8)}]" } ?: ""

        println("$color[${entry.level}]$reset ${entry.timestamp} ${entry.service}$traceInfo: ${entry.message}")

        entry.metadata?.let {
            println("  Metadata: $it")
        }
    }

    private suspend fun outputToCDC(entry: LogEntry) {
        eventEmitter.emit("log_entry", mapOf(
            "eventType" to "log_entry",
            "timestamp" to entry.timestamp,
            "service" to entry.service,
            "level" to entry.level.name,
            "message" to entry.message,
            "traceContext" to mapOf(
                "traceId" to entry.traceId,
                "spanId" to entry.spanId
            ),
            "metadata" to entry.metadata
        ))
    }

    private suspend fun outputToDataLake(entry: LogEntry) {
        // Batch and send to data lake
        // Implementation depends on data lake technology
    }
}

// Factory function
fun createLogger(config: LoggerConfig): UnhingedLogger {
    return UnhingedLogger(config)
}
```