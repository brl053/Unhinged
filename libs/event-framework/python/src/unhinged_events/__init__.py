"""
Unhinged Event Framework - Python Implementation

Provides structured logging capabilities with OpenTelemetry integration
and YAML output format for consistency with existing observability patterns.
"""

from .event_logger import (
    EventLogger,
    LogLevel,
    LogEvent,
    EventLoggerConfig,
    OutputFormat,
    create_logger,
    create_service_logger
)

from .protobuf_integration import (
    UniversalEventEmitter,
    LLMEventType,
    ServiceHealthStatus,
    StateChangeType,
    create_universal_emitter,
    emit_universal_event
)

from .gui_integration import (
    GUIEventLogger,
    GUIEvent,
    create_gui_logger,
    create_gtk_click_handler,
    create_gtk_text_changed_handler
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
    "GUIEventLogger",
    "GUIEvent",
    "create_gui_logger",
    "create_gtk_click_handler",
    "create_gtk_text_changed_handler"
]
