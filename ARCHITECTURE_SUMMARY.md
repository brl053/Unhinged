# Unhinged Transcription Architecture Summary

## Three-Layer Architecture

### Layer 1: Event Bus (Real-Time UI)
**Location**: `control/gtk4_gui/utils/event_bus.py`
- **Purpose**: Synchronous component communication
- **Scope**: Single process, in-memory
- **Lifetime**: Session-scoped
- **Subscribers**: GUI components (FormInput, ChatroomView, etc.)

**Transcription Events**:
- `TRANSCRIPTION_STARTED` - Transcription begins
- `TRANSCRIPTION_COMPLETED` - Transcript ready with text
- `TRANSCRIPTION_ERROR` - Error occurred
- `TRANSCRIPTION_PROGRESS` - Progress updates (reserved)

### Layer 2: Event Framework (Persistent Logging)
**Location**: `libs/event-framework/python/src/events/`
- **Purpose**: Structured, persistent event logging
- **Scope**: Cross-service, asynchronous
- **Lifetime**: Persistent (survives app restart)
- **Subscribers**: Log files, monitoring, analytics

**Transcription Events Logged**:
- `TRANSCRIPTION_STARTED` → `/build/tmp/{session_id}.log`
- `TRANSCRIPTION_COMPLETED` → `/build/tmp/{session_id}.log`
- `TRANSCRIPTION_ERROR` → `/build/tmp/{session_id}.log`

### Layer 3: Callback Pattern (Legacy)
**Location**: `control/gtk4_gui/handlers/audio_handler.py`
- **Status**: DEPRECATED
- **Purpose**: Backward compatibility
- **Replacement**: Use event bus instead
- **Timeline**: Remove when COMPONENTS_AVAILABLE becomes permanent

## Data Flow

```
AudioHandler (records & transcribes)
    ↓
    ├─→ Event Bus (real-time)
    │   └─→ TRANSCRIPTION_COMPLETED
    │       └─→ FormInput subscribes
    │           └─→ Updates UI immediately
    │
    ├─→ Event Framework (persistent)
    │   └─→ GUISessionLogger.log_gui_event()
    │       └─→ /build/tmp/{session_id}.log
    │
    └─→ Callback (DEPRECATED)
        └─→ Only if FormInput unavailable
```

## Key Design Decisions

1. **Dual Emission**: Events emitted to both systems for:
   - Real-time UI responsiveness
   - Persistent audit trail
   - Backward compatibility

2. **Conditional Callbacks**: Result callback only set when FormInput unavailable
   - Prevents duplicate transcripts
   - Maintains backward compatibility
   - Clear deprecation path

3. **Structured Logging**: Event framework provides:
   - YAML/JSON output
   - OpenTelemetry integration
   - Trace correlation
   - Cross-service visibility

## Migration Path

**Phase 1** (DONE): Consolidate to single pattern
- Implement set_callbacks() method
- Prevent duplicate transcripts
- Add deprecation warnings

**Phase 2** (DONE): Event-driven architecture
- Add granular transcription events
- Integrate with event framework
- Document migration guide

**Phase 3** (NEXT): Complete migration
- Migrate all consumers to event bus
- Remove callback infrastructure
- Simplify codebase

## Files Modified

- `control/gtk4_gui/utils/event_bus.py` - Added TRANSCRIPTION_* events
- `control/gtk4_gui/handlers/audio_handler.py` - Event framework integration
- `control/gtk4_gui/components/form_input.py` - Subscribe to new events
- `control/gtk4_gui/desktop_app/app.py` - Pass session_logger to AudioHandler

## Documentation

- `TRANSCRIPTION_MIGRATION_GUIDE.md` - Consumer migration instructions
- `EVENT_BUS_AND_LOGGING_INTEGRATION.md` - Architecture details
- `ARCHITECTURE_SUMMARY.md` - This file

