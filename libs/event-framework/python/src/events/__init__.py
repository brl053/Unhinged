"""
Event Framework - Python Implementation

Provides structured logging capabilities with OpenTelemetry integration
and YAML output format for consistency with existing observability patterns.
"""

from .event_logger import (
    EventLogger,
    EventLoggerConfig,
    LogEvent,
    LogLevel,
    OutputFormat,
    create_logger,
    create_service_logger,
)

# GTK4 GUI session logging integration
from .gui_session_logger import (
    GUIOutputCapture,
    GUISessionLogger,
    create_gui_session_logger,
    gui_session_context,
)
from .protobuf_integration import (
    LLMEventType,
    ServiceHealthStatus,
    StateChangeType,
    UniversalEventEmitter,
    create_universal_emitter,
    emit_universal_event,
)

__version__ = "1.0.0"
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
