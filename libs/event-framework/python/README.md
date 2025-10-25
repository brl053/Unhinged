# Unhinged Event Framework - Python

A polyglot event logging framework for Unhinged services with OpenTelemetry integration and structured YAML output.

## Features

- **Structured Logging**: Emit logs in YAML or JSON format for consistency with observability systems
- **Log Levels**: Standard log levels with numeric values (DEBUG=0, INFO=1, WARN=2, ERROR=3)
- **OpenTelemetry Integration**: Automatic trace_id and span_id inclusion when available
- **Lightweight Performance**: Optimized for high-frequency logging in AI services
- **Context Management**: Easy context propagation and child logger creation

## Installation

```bash
pip install unhinged-events
```

## Quick Start

```python
from unhinged_events import create_service_logger, LogLevel

# Create a logger for your service
logger = create_service_logger("my-ai-service", version="1.0.0")

# Log events with structured metadata
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

# Create child loggers with additional context
request_logger = logger.with_context({
    "request_id": "req_abc123",
    "session_id": "sess_xyz789"
})

request_logger.debug("Starting inference pipeline")
```

## OpenTelemetry Integration

The framework automatically integrates with OpenTelemetry when available:

```python
from opentelemetry import trace
from unhinged_events import create_service_logger

logger = create_service_logger("my-service")

# Trace context is automatically included
with trace.get_tracer(__name__).start_as_current_span("my_operation"):
    logger.info("Operation started")  # Will include trace_id and span_id
```

## Configuration

```python
from unhinged_events import EventLoggerConfig, OutputFormat, LogLevel, create_logger

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

## Output Format

Events are emitted in structured YAML format by default:

```yaml
timestamp: '2025-01-04T10:30:45.123456Z'
level: INFO
level_value: 1
service_id: my-ai-service
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
  service_type: python_service
```

## Integration with Existing Systems

This framework is designed to integrate seamlessly with:

- **OpenTelemetry**: Automatic trace context inclusion
- **Unhinged Service Framework**: Compatible with existing observability patterns
- **GUI Logs Tab**: Structured output appears in the application's logs interface
- **CLI Output**: Logs are visible when running `make start`

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src tests
isort src tests

# Type checking
mypy src
```
