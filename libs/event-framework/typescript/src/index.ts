/**
 * Unhinged Event Framework - TypeScript/JavaScript
 * 
 * A polyglot event logging framework providing unified logging capabilities
 * across the Unhinged codebase with OpenTelemetry integration and structured output.
 */

// Core event logging
export {
    EventLogger,
    LogLevel,
    OutputFormat,
    LogEvent,
    EventLoggerConfig,
    DefaultEventLogger,
    createLogger,
    createSimpleLogger,
    createServiceLogger
} from './event-logger';

// Web integration
export {
    WebEvent,
    WebEventLogger,
    createWebLogger,
    autoTrackWebEvents
} from './web-integration';

// Protobuf integration
export {
    UniversalEventEmitter,
    LLMEventType,
    ServiceHealthStatus,
    StateChangeType,
    createUniversalEmitter,
    emitUniversalEvent
} from './protobuf-integration';

// Version
export const VERSION = '1.0.0';
