# Transcription Event Bus Migration Guide

## Overview

The Unhinged audio transcription system is transitioning from a callback-based pattern to an event-driven architecture using the centralized event bus. This document provides guidance for migrating existing code.

## Why Migrate?

**Benefits of Event Bus Pattern:**
- Loose coupling between components
- Multiple subscribers without code changes
- Explicit, testable data flow
- Easier debugging and monitoring
- Aligns with framebuffer-based rendering architecture

## Deprecated Callback Pattern

The `AudioHandler.set_callbacks()` method is **DEPRECATED** and will be removed in a future version.

```python
# OLD (DEPRECATED)
audio_handler.set_callbacks(
    state_callback=on_state_changed,
    result_callback=on_transcription_result,
    error_callback=on_error,
    progress_callback=on_progress,
)
```

## New Event-Driven Pattern

### Granular Transcription Events

Replace callbacks with event subscriptions:

```python
from control.gtk4_gui.utils.event_bus import get_event_bus, AudioEvents

event_bus = get_event_bus()

# Subscribe to transcription lifecycle events
event_bus.subscribe(AudioEvents.TRANSCRIPTION_STARTED, on_transcription_started)
event_bus.subscribe(AudioEvents.TRANSCRIPTION_COMPLETED, on_transcription_completed)
event_bus.subscribe(AudioEvents.TRANSCRIPTION_ERROR, on_transcription_error)
event_bus.subscribe(AudioEvents.TRANSCRIPTION_PROGRESS, on_transcription_progress)
```

### Event Payloads

**TRANSCRIPTION_STARTED**
```python
def on_transcription_started(event):
    # No payload - indicates transcription has begun
    pass
```

**TRANSCRIPTION_COMPLETED**
```python
def on_transcription_completed(event):
    transcript = event.data.get("transcript")
    timestamp = event.data.get("duration")
    # Handle completed transcription
```

**TRANSCRIPTION_ERROR**
```python
def on_transcription_error(event):
    error_type = event.data.get("type")
    error_msg = event.data.get("message")
    device = event.data.get("device")
    # Handle transcription error
```

**TRANSCRIPTION_PROGRESS**
```python
def on_transcription_progress(event):
    progress = event.data.get("progress")  # 0.0 to 1.0
    # Update progress indicator
```

## Migration Checklist

- [ ] Identify all `set_callbacks()` calls in codebase
- [ ] Replace with event bus subscriptions
- [ ] Update event handlers to use `event.data` dict
- [ ] Test transcription end-to-end
- [ ] Remove callback code after verification
- [ ] Update documentation

## Timeline

- **Current**: Callbacks deprecated, events emitted in parallel
- **Next Phase**: All consumers migrated to events
- **Final**: Callback infrastructure removed

## Questions?

See `AudioEvents` class in `control/gtk4_gui/utils/event_bus.py` for complete event definitions.

