"""
Integration helpers for protobuf event schemas

Provides utilities to emit events that are compatible with the existing
protobuf schemas defined in the observability and CDC event systems.
"""

import os
import time
import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from .event_logger import EventLogger


class LLMEventType(Enum):
    """LLM event types matching protobuf schema"""

    STARTED = "started"
    COMPLETED = "completed"
    FAILED = "failed"
    TOKEN_USAGE = "token_usage"


class ServiceHealthStatus(Enum):
    """Service health status matching protobuf schema"""

    UNKNOWN = "unknown"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    MAINTENANCE = "maintenance"


class StateChangeType(Enum):
    """State change types matching protobuf schema"""

    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    ARCHIVE = "archive"
    RESTORE = "restore"


class UniversalEventEmitter:
    """Universal event emitter that creates events compatible with protobuf schemas"""

    def __init__(self, event_logger: EventLogger, service_id: str, version: str = "1.0.0"):
        self.event_logger = event_logger
        self.service_id = service_id
        self.version = version

    def emit_universal_event(
        self,
        event_type: str,
        payload: dict[str, Any],
        user_id: str | None = None,
        session_id: str | None = None,
        correlation_id: str | None = None,
        trace_id: str | None = None,
        span_id: str | None = None,
    ) -> None:
        """Emit a universal event following the CDC event pattern"""
        event_metadata = {
            "event_type": event_type,
            "event_id": self._generate_event_id(),
            "event_version": "1.0.0",
            "timestamp_ms": int(time.time() * 1000),
            "source_service": self.service_id,
            "source_version": self.version,
            "environment": os.getenv("ENVIRONMENT", "development"),
            "payload": payload,
        }

        # Add optional context fields
        if user_id:
            event_metadata["user_id"] = user_id
        if session_id:
            event_metadata["session_id"] = session_id
        if correlation_id:
            event_metadata["correlation_id"] = correlation_id

        # Create logger with trace context if available
        if trace_id and span_id:
            logger = self.event_logger.with_trace(trace_id, span_id)
        else:
            logger = self.event_logger

        # Emit as structured log event
        logger.info(f"Universal event: {event_type}", event_metadata)

    def emit_llm_inference_event(
        self,
        event_type: LLMEventType,
        model_name: str,
        prompt_tokens: int | None = None,
        response_tokens: int | None = None,
        latency_ms: int | None = None,
        success: bool = True,
        error_message: str | None = None,
        user_id: str | None = None,
        session_id: str | None = None,
        trace_id: str | None = None,
        span_id: str | None = None,
    ) -> None:
        """Emit LLM inference event"""
        payload = {"model_name": model_name, "success": success}

        if prompt_tokens is not None:
            payload["prompt_tokens"] = prompt_tokens
        if response_tokens is not None:
            payload["response_tokens"] = response_tokens
        if latency_ms is not None:
            payload["latency_ms"] = latency_ms
        if error_message:
            payload["error_message"] = error_message

        self.emit_universal_event(
            event_type=f"llm.inference.{event_type.value}",
            payload=payload,
            user_id=user_id,
            session_id=session_id,
            trace_id=trace_id,
            span_id=span_id,
        )

    def emit_service_health_event(
        self,
        health_status: ServiceHealthStatus,
        check_results: dict[str, bool] | None = None,
        response_time_ms: int | None = None,
        trace_id: str | None = None,
        span_id: str | None = None,
    ) -> None:
        """Emit service health event"""
        payload = {
            "health_status": health_status.value,
            "check_results": check_results or {},
            "response_time_ms": response_time_ms,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        self.emit_universal_event(
            event_type="service.health",
            payload=payload,
            trace_id=trace_id,
            span_id=span_id,
        )

    def emit_system_state_event(
        self,
        entity_type: str,
        entity_id: str,
        change_type: StateChangeType,
        field_changes: dict[str, Any] | None = None,
        user_id: str | None = None,
        trace_id: str | None = None,
        span_id: str | None = None,
    ) -> None:
        """Emit system state change event"""
        payload = {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "change_type": change_type.value,
            "field_changes": field_changes or {},
            "timestamp": datetime.now(UTC).isoformat(),
        }

        self.emit_universal_event(
            event_type="system.state_change",
            payload=payload,
            user_id=user_id,
            trace_id=trace_id,
            span_id=span_id,
        )

    def emit_performance_event(
        self,
        operation_name: str,
        duration_ms: int,
        success: bool,
        metadata: dict[str, Any] | None = None,
        trace_id: str | None = None,
        span_id: str | None = None,
    ) -> None:
        """Emit performance metric event"""
        payload = {
            "operation_name": operation_name,
            "duration_ms": duration_ms,
            "success": success,
            "metadata": metadata or {},
        }

        self.emit_universal_event(
            event_type="performance.operation",
            payload=payload,
            trace_id=trace_id,
            span_id=span_id,
        )

    def _generate_event_id(self) -> str:
        """Generate a unique event ID"""
        return str(uuid.uuid4())


def create_universal_emitter(
    event_logger: EventLogger, service_id: str, version: str = "1.0.0"
) -> UniversalEventEmitter:
    """Create a universal event emitter for a service"""
    return UniversalEventEmitter(event_logger, service_id, version)


def emit_universal_event(
    event_logger: EventLogger,
    service_id: str,
    event_type: str,
    payload: dict[str, Any],
    user_id: str | None = None,
    session_id: str | None = None,
    trace_id: str | None = None,
    span_id: str | None = None,
) -> None:
    """Emit a universal event directly from an EventLogger"""
    emitter = create_universal_emitter(event_logger, service_id)
    emitter.emit_universal_event(
        event_type=event_type,
        payload=payload,
        user_id=user_id,
        session_id=session_id,
        trace_id=trace_id,
        span_id=span_id,
    )
