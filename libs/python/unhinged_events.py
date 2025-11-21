"""
Backward compatibility module for unhinged_events.

This module re-exports from the canonical location in libs/event-framework/python/src/events.
"""

import sys
from pathlib import Path

# Add event framework to path
event_framework_path = Path(__file__).parent.parent / "event-framework" / "python" / "src"
if str(event_framework_path) not in sys.path:
    sys.path.insert(0, str(event_framework_path))

# Re-export everything from events
from events import (  # noqa: E402
    EventLogger,
    EventLoggerConfig,
    GUIOutputCapture,
    GUISessionLogger,
    LLMEventType,
    LogEvent,
    LogLevel,
    OutputFormat,
    ServiceHealthStatus,
    StateChangeType,
    UniversalEventEmitter,
    create_gui_session_logger,
    create_logger,
    create_service_logger,
    create_universal_emitter,
    emit_universal_event,
    gui_session_context,
)

__all__ = [
    "EventLogger",
    "LogLevel",
    "LogEvent",
    "EventLoggerConfig",
    "OutputFormat",
    "create_logger",
    "create_service_logger",
    "UniversalEventEmitter",
    "LLMEventType",
    "ServiceHealthStatus",
    "StateChangeType",
    "create_universal_emitter",
    "emit_universal_event",
    "GUISessionLogger",
    "GUIOutputCapture",
    "create_gui_session_logger",
    "gui_session_context",
]

