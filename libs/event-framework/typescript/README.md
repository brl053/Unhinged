# Unhinged Event Framework - TypeScript/JavaScript

A polyglot event logging framework for Unhinged services with OpenTelemetry integration and structured YAML output.

## Features

- **Structured Logging**: Emit logs in YAML or JSON format for consistency with observability systems
- **Log Levels**: Standard log levels with numeric values (DEBUG=0, INFO=1, WARN=2, ERROR=3)
- **OpenTelemetry Integration**: Automatic trace_id and span_id inclusion when available
- **Web Integration**: Specialized logging for browser interactions and DOM events
- **Lightweight Performance**: Optimized for high-frequency logging in web applications
- **Cross-Platform**: Works in both Node.js and browser environments

## Installation

```bash
npm install @unhinged/event-framework
```

## Quick Start

### Basic Usage

```typescript
import { createServiceLogger, LogLevel } from '@unhinged/event-framework';

// Create a logger for your service
const logger = createServiceLogger('my-web-service', '1.0.0');

// Log events with structured metadata
logger.info('Processing user request', {
    user_id: 'user123',
    request_type: 'api_call',
    endpoint: '/api/users'
});

// Log errors with exceptions
try {
    await processRequest();
} catch (error) {
    logger.error('Request processing failed', error, {
        retry_count: 3,
        timeout_ms: 5000
    });
}

// Create child loggers with additional context
const requestLogger = logger.withContext({
    request_id: 'req_abc123',
    session_id: 'sess_xyz789'
});
```

### Web Integration

```typescript
import { createWebLogger, autoTrackWebEvents } from '@unhinged/event-framework';

// Create a web-specific logger
const webLogger = createWebLogger('my-web-app', '1.0.0');

// Log specific web interactions
webLogger.logButtonClick('Submit Form', 'submit-btn', { x: 100, y: 200 });
webLogger.logLinkClick('Home', '/home', 'nav-home');
webLogger.logFormSubmit('contact-form', '/api/contact', 5);

// Auto-track common web events
autoTrackWebEvents(webLogger, 'user123');

// Log performance metrics
webLogger.logPerformanceMetric('page_load_time', 1250, 'ms');
```

### OpenTelemetry Integration

```typescript
import { trace } from '@opentelemetry/api';
import { createServiceLogger } from '@unhinged/event-framework';

const logger = createServiceLogger('my-service');

// Trace context is automatically included
const tracer = trace.getTracer('my-service');
const span = tracer.startSpan('my-operation');

// Set span as active
trace.setSpan(trace.active(), span);

logger.info('Operation started'); // Will include trace_id and span_id

span.end();
```

### Protobuf Event Integration

```typescript
import { createUniversalEmitter, LLMEventType } from '@unhinged/event-framework';

const logger = createServiceLogger('ai-service');
const emitter = createUniversalEmitter(logger, 'ai-service');

// Emit LLM inference events
emitter.emitLLMInferenceEvent(
    LLMEventType.STARTED,
    'gpt-4',
    undefined, // prompt tokens
    undefined, // response tokens
    undefined, // latency
    true,      // success
    undefined, // error message
    'user123',
    'session456'
);

// Emit performance events
emitter.emitPerformanceEvent(
    'api_request',
    150, // duration in ms
    true, // success
    { endpoint: '/api/users' }
);
```

## Configuration

```typescript
import { EventLoggerConfig, LogLevel, OutputFormat, createLogger } from '@unhinged/event-framework';

const config: EventLoggerConfig = {
    serviceId: 'my-service',
    version: '1.0.0',
    environment: 'production',
    minLogLevel: LogLevel.INFO,
    outputFormat: OutputFormat.YAML,
    includeStackTrace: true,
    contextData: {
        component: 'web-frontend',
        region: 'us-west-2'
    }
};

const logger = createLogger(config);
```

## Output Format

Events are emitted in structured YAML format by default:

```yaml
timestamp: '2025-01-04T10:30:45.123Z'
level: INFO
level_value: 1
service_id: my-web-service
message: User button_click on 'Submit Form'
trace_id: 1234567890abcdef1234567890abcdef
span_id: abcdef1234567890
metadata:
  event_type: user_interaction
  web_event_type: button_click
  element_id: submit-btn
  coordinates:
    x: 100
    y: 200
context:
  service_version: 1.0.0
  environment: production
  component_type: web_ui
  session_id: web_session_1704362445123
```

## Browser vs Node.js

The framework works in both environments:

- **Browser**: Logs to `console.log()`, integrates with DOM events
- **Node.js**: Logs to `stdout`, integrates with server-side operations

## Integration with Existing Systems

This framework integrates seamlessly with:

- **OpenTelemetry**: Automatic trace context inclusion
- **Unhinged Service Framework**: Compatible with existing observability patterns
- **GUI Logs Tab**: Structured output appears in the application's logs interface
- **CLI Output**: Logs are visible when running development servers

## Development

```bash
# Install dependencies
npm install

# Build the library
npm run build

# Run tests
npm test

# Watch mode for development
npm run build:watch
```

## API Reference

### Core Classes

- `EventLogger`: Main logging interface
- `DefaultEventLogger`: Default implementation
- `WebEventLogger`: Web-specific logger with DOM integration

### Factory Functions

- `createLogger(config)`: Create logger with full configuration
- `createServiceLogger(serviceId, version?, environment?, minLogLevel?)`: Create service logger
- `createWebLogger(appName?, version?)`: Create web-specific logger

### Integration Functions

- `autoTrackWebEvents(logger, userId?)`: Auto-track common web interactions
- `createUniversalEmitter(logger, serviceId, version?)`: Create protobuf-compatible event emitter
