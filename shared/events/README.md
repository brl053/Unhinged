# @unhinged/events

Centralized event logging library for the Unhinged monorepo.

## Features

- 🎯 **Type-safe event logging** with TypeScript
- 📊 **Multiple destinations** (console, database, file)
- 🔄 **Event buffering and batching** for performance
- 🎣 **Event handlers and filters** for custom processing
- 🏗️ **Standardized event schema** across all services
- 🚀 **Zero-dependency core** with optional integrations

## Installation

```bash
# In your service directory
npm install @unhinged/events

# For database logging (optional)
npm install pg @types/pg
```

## Quick Start

```typescript
import { createEventLogger, EventSource } from '@unhinged/events';

// Create logger for your service
const logger = createEventLogger({
  serviceName: EventSource.VOICE_RECORDER,
  enableConsole: true,
  enableDatabase: true,
  databaseConfig: {
    host: 'localhost',
    port: 5433,
    database: 'postgres',
    user: 'postgres',
    password: 'postgres'
  }
});

// Log events
await logger.logVoiceRecording('voice_recording_started', {
  sessionId: 'session-123',
  audioFormat: 'webm'
});

await logger.logTranscription('transcription_completed', {
  sessionId: 'session-123',
  audioSize: 15420,
  transcriptionText: 'Hello world',
  language: 'en',
  processingTimeMs: 1250
});

// Don't forget to close when shutting down
await logger.close();
```

## Event Types

### Voice Recording Events
```typescript
await logger.logVoiceRecording('voice_recording_started', {
  sessionId: 'session-123',
  audioFormat: 'webm'
});

await logger.logVoiceRecording('voice_recording_stopped', {
  sessionId: 'session-123',
  duration: 5000,
  audioSize: 15420
});
```

### Transcription Events
```typescript
await logger.logTranscription('transcription_completed', {
  sessionId: 'session-123',
  audioSize: 15420,
  transcriptionText: 'Hello world',
  language: 'en',
  confidence: 0.95,
  processingTimeMs: 1250
});
```

### Chat Events
```typescript
await logger.logChat('chat_message_sent', {
  sessionId: 'session-123',
  messageId: 'msg-456',
  messageContent: 'Hello',
  messageRole: 'user',
  messageSource: 'voice'
});
```

### Error Events
```typescript
await logger.logError('error_occurred', {
  errorType: 'ValidationError',
  errorMessage: 'Invalid audio format',
  errorCode: 'AUDIO_001',
  context: { format: 'mp3', expected: 'webm' }
});
```

## Configuration

```typescript
const logger = createEventLogger({
  serviceName: EventSource.REACT_FRONTEND,
  
  // Default metadata added to all events
  defaultMetadata: {
    userId: 'user-123',
    sessionId: 'session-456'
  },
  
  // Destinations
  enableConsole: true,
  enableDatabase: true,
  enableFile: true,
  filePath: './logs/events.jsonl',
  
  // Database config
  databaseConfig: {
    host: 'localhost',
    port: 5433,
    database: 'postgres',
    user: 'postgres',
    password: 'postgres'
  },
  
  // Performance tuning
  bufferSize: 100,        // Events to buffer before flushing
  flushInterval: 5000,    // Flush every 5 seconds
  minSeverity: EventSeverity.INFO
});
```

## Event Handlers

```typescript
// Listen for specific events
logger.onEvent('voice_recording_completed', (event) => {
  console.log('Voice recording completed:', event.data);
});

// Add filters
logger.addFilter((event) => {
  // Only log events from specific sessions
  return event.metadata?.sessionId === 'important-session';
});
```

## Service Integration Examples

### React Frontend
```typescript
// frontend/src/services/EventService.ts
import { createEventLogger, EventSource } from '@unhinged/events';

export const eventLogger = createEventLogger({
  serviceName: EventSource.REACT_FRONTEND,
  enableConsole: true,
  enableDatabase: false, // Frontend doesn't connect to DB directly
  defaultMetadata: {
    userAgent: navigator.userAgent
  }
});

// In components
await eventLogger.logEvent('button_clicked', {
  actionType: 'voice_record_start',
  elementId: 'voice-record-button'
});
```

### Backend Service
```typescript
// backend/src/services/EventService.kt (conceptual)
import { createEventLogger, EventSource } from '@unhinged/events';

export const eventLogger = createEventLogger({
  serviceName: EventSource.KOTLIN_BACKEND,
  enableConsole: true,
  enableDatabase: true,
  databaseConfig: process.env.DATABASE_CONFIG
});
```

### Whisper Service
```typescript
// services/whisper-tts/src/EventService.ts
import { createEventLogger, EventSource } from '@unhinged/events';

export const eventLogger = createEventLogger({
  serviceName: EventSource.WHISPER_TTS,
  enableConsole: true,
  enableDatabase: true
});

// Log transcription events
await eventLogger.logTranscription('transcription_started', {
  sessionId: request.sessionId,
  audioSize: audioBlob.size
});
```

## Database Schema

The library expects this table structure:

```sql
CREATE TABLE events (
  id VARCHAR(255) PRIMARY KEY,
  event_type VARCHAR(100) NOT NULL,
  event_data JSONB NOT NULL,
  source VARCHAR(100) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  metadata JSONB
);

-- Indexes for performance
CREATE INDEX idx_events_type ON events(event_type);
CREATE INDEX idx_events_source ON events(source);
CREATE INDEX idx_events_created_at ON events(created_at);
CREATE INDEX idx_events_session_id ON events((metadata->>'sessionId'));
```

## Development

```bash
# Build the library
npm run build

# Watch for changes
npm run build:watch

# Run tests
npm run test

# Lint code
npm run lint
```

## License

MIT
