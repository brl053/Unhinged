"""
Core event logging implementation for Python services
"""

import json
import sys
import traceback
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

import yaml

# Optional OpenTelemetry import
try:
    from opentelemetry import trace
    from opentelemetry.trace import Span

    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False


class LogLevel(Enum):
    """Log levels with numeric values for filtering"""

    DEBUG = 0
    INFO = 1
    WARN = 2
    ERROR = 3

    @classmethod
    def from_value(cls, value: int) -> Optional["LogLevel"]:
        """Get log level from numeric value"""
        for level in cls:
            if level.value == value:
                return level
        return None

    @classmethod
    def from_name(cls, name: str) -> Optional["LogLevel"]:
        """Get log level from string name (case insensitive)"""
        try:
            return cls[name.upper()]
        except KeyError:
            return None


class OutputFormat(Enum):
    """Supported output formats"""

    YAML = "yaml"
    JSON = "json"


@dataclass
class LogEvent:
    """Structured log event data"""

    timestamp: datetime
    level: LogLevel
    message: str
    service_id: str
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    exception: Optional[Exception] = None
    context_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EventLoggerConfig:
    """Event logger configuration"""

    service_id: str
    version: str = "1.0.0"
    environment: str = "development"
    min_log_level: LogLevel = LogLevel.INFO
    output_format: OutputFormat = OutputFormat.YAML
    include_stack_trace: bool = True
    context_data: Dict[str, Any] = field(default_factory=dict)


class EventLogger(ABC):
    """Abstract base class for event loggers"""

    @abstractmethod
    def debug(self, message: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Log a debug event (level 0)"""
        pass

    @abstractmethod
    def info(self, message: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Log an info event (level 1)"""
        pass

    @abstractmethod
    def warn(self, message: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Log a warning event (level 2)"""
        pass

    @abstractmethod
    def error(
        self,
        message: str,
        exception: Optional[Exception] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log an error event (level 3)"""
        pass

    @abstractmethod
    def is_enabled(self, level: LogLevel) -> bool:
        """Check if a log level is enabled"""
        pass

    @abstractmethod
    def with_context(self, additional_context: Dict[str, Any]) -> "EventLogger":
        """Create a child logger with additional context"""
        pass

    @abstractmethod
    def with_trace(self, trace_id: str, span_id: str) -> "EventLogger":
        """Create a child logger with trace context"""
        pass


class DefaultEventLogger(EventLogger):
    """Default implementation of EventLogger with YAML output and OpenTelemetry integration"""

    def __init__(
        self,
        config: EventLoggerConfig,
        context_data: Optional[Dict[str, Any]] = None,
        trace_context: Optional[Dict[str, str]] = None,
    ):
        self.config = config
        self.context_data = context_data or {}
        self.trace_context = trace_context

    def debug(self, message: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        if self.is_enabled(LogLevel.DEBUG):
            self._emit_event(LogLevel.DEBUG, message, metadata or {})

    def info(self, message: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        if self.is_enabled(LogLevel.INFO):
            self._emit_event(LogLevel.INFO, message, metadata or {})

    def warn(self, message: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        if self.is_enabled(LogLevel.WARN):
            self._emit_event(LogLevel.WARN, message, metadata or {})

    def error(
        self,
        message: str,
        exception: Optional[Exception] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        if self.is_enabled(LogLevel.ERROR):
            self._emit_event(LogLevel.ERROR, message, metadata or {}, exception)

    def is_enabled(self, level: LogLevel) -> bool:
        return level.value >= self.config.min_log_level.value

    def with_context(self, additional_context: Dict[str, Any]) -> EventLogger:
        merged_context = {**self.context_data, **additional_context}
        return DefaultEventLogger(self.config, merged_context, self.trace_context)

    def with_trace(self, trace_id: str, span_id: str) -> EventLogger:
        trace_context = {"trace_id": trace_id, "span_id": span_id}
        return DefaultEventLogger(self.config, self.context_data, trace_context)

    def _emit_event(
        self,
        level: LogLevel,
        message: str,
        metadata: Dict[str, Any],
        exception: Optional[Exception] = None,
    ) -> None:
        """Emit a log event"""
        current_trace = self._get_current_trace_context()

        event = LogEvent(
            timestamp=datetime.now(timezone.utc),
            level=level,
            message=message,
            service_id=self.config.service_id,
            trace_id=current_trace.get("trace_id") if current_trace else None,
            span_id=current_trace.get("span_id") if current_trace else None,
            metadata=metadata,
            exception=exception,
            context_data={**self.context_data, **self.config.context_data},
        )

        if self.config.output_format == OutputFormat.YAML:
            output = self._format_as_yaml(event)
        else:
            output = self._format_as_json(event)

        # Output to stdout for CLI visibility and GUI logs tab
        print(output, file=sys.stdout)
        sys.stdout.flush()

    def _get_current_trace_context(self) -> Optional[Dict[str, str]]:
        """Get current trace context from OpenTelemetry or explicit context"""
        # First check if we have explicit trace context
        if self.trace_context:
            return self.trace_context

        # Then try to get from OpenTelemetry current span
        if OPENTELEMETRY_AVAILABLE:
            try:
                current_span = trace.get_current_span()
                if current_span and current_span.get_span_context().is_valid:
                    span_context = current_span.get_span_context()
                    return {
                        "trace_id": format(span_context.trace_id, "032x"),
                        "span_id": format(span_context.span_id, "016x"),
                    }
            except Exception:
                # OpenTelemetry not available or no active span
                pass

        return None

    def _format_as_yaml(self, event: LogEvent) -> str:
        """Format event as YAML"""
        event_dict = self._build_event_dict(event)
        return yaml.dump(event_dict, default_flow_style=False, indent=2).rstrip()

    def _format_as_json(self, event: LogEvent) -> str:
        """Format event as JSON"""
        event_dict = self._build_event_dict(event)
        return json.dumps(event_dict, indent=2, default=str)

    def _build_event_dict(self, event: LogEvent) -> Dict[str, Any]:
        """Build event dictionary for serialization"""
        event_dict = {
            "timestamp": event.timestamp.isoformat(),
            "level": event.level.name,
            "level_value": event.level.value,
            "service_id": event.service_id,
            "message": event.message,
        }

        # Add trace context if available
        if event.trace_id:
            event_dict["trace_id"] = event.trace_id
        if event.span_id:
            event_dict["span_id"] = event.span_id

        # Add metadata if present
        if event.metadata:
            event_dict["metadata"] = event.metadata

        # Add context data if present
        if event.context_data:
            event_dict["context"] = event.context_data

        # Add exception details if present
        if event.exception:
            exception_dict = {
                "type": type(event.exception).__name__,
                "message": str(event.exception),
            }

            if self.config.include_stack_trace:
                exception_dict["stack_trace"] = traceback.format_exc()

            event_dict["exception"] = exception_dict

        return event_dict


def create_logger(config: EventLoggerConfig) -> EventLogger:
    """Create a new event logger with the specified configuration"""
    return DefaultEventLogger(config)


def create_logger_simple(service_id: str) -> EventLogger:
    """Create a new event logger with minimal configuration"""
    config = EventLoggerConfig(service_id=service_id)
    return create_logger(config)


def create_service_logger(
    service_id: str,
    version: str = "1.0.0",
    environment: str = "development",
    min_log_level: LogLevel = LogLevel.INFO,
) -> EventLogger:
    """Create a service-specific event logger"""
    config = EventLoggerConfig(
        service_id=service_id,
        version=version,
        environment=environment,
        min_log_level=min_log_level,
        context_data={
            "service_version": version,
            "environment": environment,
            "service_type": "python_service",
        },
    )
    return create_logger(config)
