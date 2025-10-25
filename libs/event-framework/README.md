# Unhinged Event Framework

A polyglot event logging framework providing unified logging capabilities across the Unhinged codebase with OpenTelemetry integration and structured output.

## Overview

The Event Framework provides structured logging capabilities that integrate seamlessly with the existing observability system, supporting both Kotlin (for platforms) and Python (for AI services) with consistent APIs and output formats.

## Features

- **Structured Logging**: Emit logs in YAML format for consistency with existing observability patterns
- **Standard Log Levels**: DEBUG (0), INFO (1), WARN (2), ERROR (3) with numeric values for filtering
- **OpenTelemetry Integration**: Automatic trace_id and span_id inclusion when available
- **Lightweight Performance**: Optimized for high-frequency logging
- **Multi-Language Support**: Consistent APIs across Kotlin, Python, and TypeScript/JavaScript
- **ServiceBase Integration**: Seamless integration with existing service framework
- **GUI Integration**: Specialized logging for native GTK4 GUI and web interactions
- **Protobuf Compatibility**: Event emission patterns compatible with existing schemas

## Architecture

```
libs/event-framework/
├── kotlin/                    # Kotlin implementation
│   ├── src/main/kotlin/com/unhinged/events/
│   │   ├── EventLogger.kt     # Core interfaces
│   │   ├── DefaultEventLogger.kt  # Implementation
│   │   ├── ServiceBaseIntegration.kt  # ServiceBase extensions
│   │   └── ProtobufIntegration.kt     # Protobuf event helpers
│   └── build.gradle.kts       # Gradle configuration
├── python/                    # Python implementation
│   ├── src/unhinged_events/
│   │   ├── event_logger.py    # Core implementation
│   │   ├── protobuf_integration.py  # Protobuf event helpers
│   │   └── gui_integration.py # GTK4 GUI integration
│   └── pyproject.toml         # Python packaging
└── typescript/                # TypeScript/JavaScript implementation
    ├── src/
    │   ├── event-logger.ts    # Core implementation
    │   ├── web-integration.ts # Web/DOM integration
    │   └── protobuf-integration.ts # Protobuf event helpers
    ├── package.json           # NPM packaging
    └── tsconfig.json          # TypeScript configuration
```

## Quick Start

### Kotlin Usage

```kotlin
import com.unhinged.events.*

// Create a service logger
val logger = createServiceEventLogger("my-service", "1.0.0")

// Log structured events
logger.info("Processing user request", mapOf(
    "user_id" to "user123",
    "request_type" to "inference",
    "model" to "llama3.2"
))

// Log errors with exceptions
try {
    processRequest()
} catch (e: Exception) {
    logger.error("Request processing failed", e, mapOf(
        "retry_count" to 3,
        "timeout_ms" to 5000
    ))
}

// Create child loggers with context
val requestLogger = logger.withContext(mapOf(
    "request_id" to "req_abc123",
    "session_id" to "sess_xyz789"
))
```

### Python Usage

```python
from unhinged_events import create_service_logger

# Create a service logger
logger = create_service_logger("my-ai-service", version="1.0.0")

# Log structured events
logger.info("Processing user request", {
    "user_id": "user123",
    "request_type": "inference",
    "model": "llama3.2"
})

# Log errors with exceptions
try:
    process_request()
except Exception as e:
    logger.error("Request processing failed", exception=e, metadata={
        "retry_count": 3,
        "timeout_ms": 5000
    })

# Create child loggers with context
request_logger = logger.with_context({
    "request_id": "req_abc123",
    "session_id": "sess_xyz789"
})
```

### TypeScript/JavaScript Usage

```typescript
import { createServiceLogger, createWebLogger, autoTrackWebEvents } from '@unhinged/event-framework';

// Create a service logger
const logger = createServiceLogger('my-web-service', '1.0.0');

// Log structured events
logger.info('Processing user request', {
    user_id: 'user123',
    request_type: 'api_call',
    endpoint: '/api/users'
});

// Web-specific logging
const webLogger = createWebLogger('my-web-app');
webLogger.logButtonClick('Submit Form', 'submit-btn', { x: 100, y: 200 });
webLogger.logPageNavigation('/home', '/profile', 'navigation');

// Auto-track web events
autoTrackWebEvents(webLogger, 'user123');
```

### GUI Integration (Python GTK4)

```python
from unhinged_events import create_gui_logger, create_gtk_click_handler

# Create GUI logger
gui_logger = create_gui_logger("unhinged-control-center", "1.0.0")

# Log user interactions
gui_logger.log_button_click("Start Service", tool_name="service_manager")
gui_logger.log_tool_switch("chat", "logs", user_id="user123")
gui_logger.log_keyboard_shortcut("Ctrl+T", "new_tab")

# GTK4 integration helpers
def setup_button_logging(button, label, tool_name):
    handler = create_gtk_click_handler(gui_logger, label, tool_name)
    button.connect("clicked", handler)
```

## Integration with ServiceBase

### Kotlin ServiceBase Integration

```kotlin
import com.unhinged.events.*

class MyService : ServiceBase("my-service", "1.0.0", 8080) {
    
    // Get event logger for this service
    private val eventLogger = this.eventLogger
    
    override suspend fun initialize() {
        eventLogger.info("Initializing service components")
        
        // Service-specific initialization
        initializeDatabase()
        initializeCache()
        
        eventLogger.info("Service initialization completed")
    }
    
    override fun registerGrpcServices(serverBuilder: ServerBuilder<*>) {
        serverBuilder.addService(MyGrpcServiceImpl(eventLogger))
    }
}

class MyGrpcServiceImpl(private val eventLogger: EventLogger) : MyServiceGrpc.MyServiceImplBase() {
    
    override fun processRequest(request: MyRequest, responseObserver: StreamObserver<MyResponse>) {
        val requestLogger = eventLogger.withContext(mapOf(
            "request_id" to request.requestId,
            "user_id" to request.userId
        ))
        
        requestLogger.info("Processing gRPC request", mapOf(
            "method" to "processRequest",
            "request_size" to request.serializedSize
        ))
        
        // Process request...
    }
}
```

### Python Service Integration

```python
from unhinged_events import create_service_logger, LLMEventType
from unhinged_events.protobuf_integration import create_universal_emitter

class AIService:
    def __init__(self, service_id: str):
        self.logger = create_service_logger(service_id, version="1.0.0")
        self.event_emitter = create_universal_emitter(self.logger, service_id)
    
    async def process_llm_request(self, prompt: str, user_id: str, session_id: str):
        request_logger = self.logger.with_context({
            "user_id": user_id,
            "session_id": session_id,
            "operation": "llm_inference"
        })
        
        request_logger.info("Starting LLM inference", {
            "prompt_length": len(prompt),
            "model": "llama3.2"
        })
        
        # Emit protobuf-compatible event
        self.event_emitter.emit_llm_inference_event(
            event_type=LLMEventType.STARTED,
            model_name="llama3.2",
            user_id=user_id,
            session_id=session_id
        )
        
        try:
            result = await self.run_inference(prompt)
            
            self.event_emitter.emit_llm_inference_event(
                event_type=LLMEventType.COMPLETED,
                model_name="llama3.2",
                prompt_tokens=len(prompt.split()),
                response_tokens=len(result.split()),
                latency_ms=100,
                success=True,
                user_id=user_id,
                session_id=session_id
            )
            
            return result
            
        except Exception as e:
            request_logger.error("LLM inference failed", exception=e)
            
            self.event_emitter.emit_llm_inference_event(
                event_type=LLMEventType.FAILED,
                model_name="llama3.2",
                success=False,
                error_message=str(e),
                user_id=user_id,
                session_id=session_id
            )
            
            raise
```

## Output Format

Events are emitted in structured YAML format:

```yaml
timestamp: '2025-01-04T10:30:45.123456Z'
level: INFO
level_value: 1
service_id: my-service
message: Processing user request
trace_id: 1234567890abcdef1234567890abcdef
span_id: abcdef1234567890
metadata:
  user_id: user123
  request_type: inference
  model: llama3.2
context:
  service_version: 1.0.0
  environment: production
  request_id: req_abc123
  session_id: sess_xyz789
```

## OpenTelemetry Integration

The framework automatically integrates with OpenTelemetry when available:

```kotlin
// Kotlin - automatic trace context
val span = tracer.spanBuilder("my-operation").startSpan()
span.makeCurrent().use {
    logger.info("Operation started")  // Will include trace_id and span_id
}
```

```python
# Python - automatic trace context
from opentelemetry import trace

with trace.get_tracer(__name__).start_as_current_span("my_operation"):
    logger.info("Operation started")  # Will include trace_id and span_id
```

## Configuration

### Environment Variables

- `ENVIRONMENT`: Sets the environment context (development, staging, production)
- `LOG_LEVEL`: Sets minimum log level (DEBUG, INFO, WARN, ERROR)

### Programmatic Configuration

```kotlin
// Kotlin
val config = EventLoggerConfig(
    serviceId = "my-service",
    version = "1.0.0",
    environment = "production",
    minLogLevel = LogLevel.INFO,
    outputFormat = OutputFormat.YAML,
    includeStackTrace = true,
    contextData = mapOf(
        "component" to "api-gateway",
        "region" to "us-west-2"
    )
)
val logger = EventLoggerFactory.createLogger(config)
```

```python
# Python
from unhinged_events import EventLoggerConfig, LogLevel, OutputFormat, create_logger

config = EventLoggerConfig(
    service_id="my-service",
    version="1.0.0",
    environment="production",
    min_log_level=LogLevel.INFO,
    output_format=OutputFormat.YAML,
    include_stack_trace=True,
    context_data={
        "component": "ai-pipeline",
        "region": "us-west-2"
    }
)
logger = create_logger(config)
```

## Testing

### Kotlin Tests

```bash
cd libs/event-framework/kotlin
./gradlew test
```

### Python Tests

```bash
cd libs/event-framework/python
pip install -e ".[dev]"
pytest
```

## Integration Points

- **CLI Output**: Logs appear when running `make start`
- **GUI Logs Tab**: Structured output visible in application logs interface
- **OpenTelemetry**: Automatic trace context propagation
- **Protobuf Events**: Compatible with existing CDC event schemas
- **ServiceBase**: Seamless integration with service framework

## Building and Testing

### Build Kotlin Module

```bash
cd libs/event-framework/kotlin
./gradlew build
```

### Build Python Module

```bash
cd libs/event-framework/python
pip install -e .
```

### Run Tests

```bash
# Kotlin tests
cd libs/event-framework/kotlin && ./gradlew test

# Python tests
cd libs/event-framework/python && pytest
```
