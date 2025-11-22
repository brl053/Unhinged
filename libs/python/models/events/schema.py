"""Event domain models used across the system.

@llm-type library.models.events
@llm-does define core event types for CDC, graph execution, tool calls, CLI, etc.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class EventKind(str, Enum):
    """High-level categories of events.

    Intentionally broad so that domains can grow without changing the base type.
    """

    GRAPH = "GRAPH"
    CDC = "CDC"
    TOOL = "TOOL"
    CLI = "CLI"
    SYSTEM = "SYSTEM"


@dataclass
class Event:
    """Base event flowing through the system.

    This is the shape we want everywhere instead of gRPC-specific types.
    """

    id: str
    kind: EventKind
    created_at: datetime
    # Opaque payload owned by the producing domain. Downstream code should
    # convert this into richer types when it cares about structure.
    payload: dict[str, Any] = field(default_factory=dict)
    # Optional partitioning information for CDC / streams.
    stream: str | None = None
    # Optional correlation / causation identifiers.
    correlation_id: str | None = None
    causation_id: str | None = None


class GraphEventType(str, Enum):
    """Types of graph-related events.

    These cover what the current gRPC execution events are doing, but are more
    general so the graph domain can grow new event types over time.
    """

    EXECUTION_STARTED = "EXECUTION_STARTED"
    NODE_STARTED = "NODE_STARTED"
    NODE_COMPLETED = "NODE_COMPLETED"
    NODE_FAILED = "NODE_FAILED"
    EXECUTION_COMPLETED = "EXECUTION_COMPLETED"
    EXECUTION_FAILED = "EXECUTION_FAILED"
    EXECUTION_CANCELLED = "EXECUTION_CANCELLED"


@dataclass
class GraphEvent(Event):
    """Event specific to the graph domain.

    This replaces the gRPC ExecutionEvent / NodeExecution messages and can be
    published to any CDC feed or in-process bus.
    """

    event_type: GraphEventType = GraphEventType.EXECUTION_STARTED
    graph_id: str | None = None
    node_id: str | None = None
    # Free-form data such as node outputs, error messages, debug info, etc.
    details: dict[str, Any] = field(default_factory=dict)
