# Event Bus and Centralized Logging Integration

## Architecture Overview

Two complementary systems work together in Unhinged:

### 1. **Event Bus** (`control/gtk4_gui/utils/event_bus.py`)
- **Purpose**: Real-time component communication within GTK4 GUI
- **Scope**: In-process, synchronous pub/sub for UI state changes
- **Subscribers**: Multiple GUI components (FormInput, ChatroomView, StatusView, etc.)
- **Lifetime**: Session-scoped (created at app startup, destroyed at shutdown)
- **Data Flow**: Component → EventBus → Multiple Subscribers (synchronous)

### 2. **Event Framework** (`libs/event-framework/python/src/events/`)
- **Purpose**: Structured, persistent logging for audit trail and debugging
- **Scope**: Cross-service, asynchronous event logging to files/CRDB/Redis
- **Subscribers**: Log files, monitoring systems, analytics pipelines
- **Lifetime**: Persistent (logs survive app restart)
- **Data Flow**: Service → EventLogger → File/CRDB/Redis (asynchronous)

## Integration Pattern

```
AudioHandler (records & transcribes)
    ↓
    ├─→ Event Bus (real-time)
    │   └─→ TRANSCRIPTION_COMPLETED event
    │       └─→ FormInput subscribes → updates UI immediately
    │
    └─→ Event Framework (persistent)
        └─→ EventLogger.info("Transcription completed", metadata)
            └─→ /build/tmp/{session_id}.log (structured YAML/JSON)
```

## Key Differences

| Aspect | Event Bus | Event Framework |
|--------|-----------|-----------------|
| **Latency** | Synchronous (ms) | Asynchronous (buffered) |
| **Persistence** | In-memory only | File/CRDB/Redis |
| **Scope** | Single process | Cross-service |
| **Use Case** | UI state sync | Audit trail |
| **Subscribers** | GUI components | Monitoring/Analytics |
| **Data Loss** | Lost on crash | Persisted |

## Implementation Strategy

### Phase 1: Current State (DONE)
- Event Bus emits granular transcription events
- Event Framework logs via GUISessionLogger
- Both systems operate independently

### Phase 2: Recommended Integration
Bridge the gap by having AudioHandler emit to BOTH systems:

```python
# In AudioHandler._record_and_transcribe()

# 1. Emit to Event Bus (real-time UI updates)
self._event_bus.emit_simple(
    AudioEvents.TRANSCRIPTION_COMPLETED,
    {"transcript": result.text}
)

# 2. Log to Event Framework (persistent audit trail)
self.session_logger.info(
    "Transcription completed",
    metadata={
        "transcript_length": len(result.text),
        "duration_ms": elapsed_time,
        "model": "whisper-base",
    }
)
```

### Phase 3: Unified Event Correlation
Use trace IDs to correlate Event Bus events with Event Framework logs:

```python
# Generate trace ID at transcription start
trace_id = str(uuid.uuid4())

# Emit to Event Bus with trace ID
self._event_bus.emit_simple(
    AudioEvents.TRANSCRIPTION_STARTED,
    {"trace_id": trace_id}
)

# Log to Event Framework with same trace ID
self.session_logger.with_trace(trace_id).info(
    "Transcription started"
)
```

## Current Gaps

1. **No persistent logging of transcription events** - Event Bus events are lost on crash
2. **No trace correlation** - Can't link UI events to log entries
3. **No cross-service visibility** - Other services can't see GUI transcription events
4. **No analytics** - No structured data for transcription metrics

## Recommended Next Steps

1. Add EventLogger to AudioHandler
2. Log all transcription lifecycle events to Event Framework
3. Implement trace ID correlation
4. Create transcription metrics dashboard
5. Set up alerts for transcription errors

## Files to Update

- `control/gtk4_gui/handlers/audio_handler.py` - Add EventLogger integration
- `control/gtk4_gui/desktop_app/app.py` - Pass session logger to AudioHandler
- `TRANSCRIPTION_MIGRATION_GUIDE.md` - Document logging integration

