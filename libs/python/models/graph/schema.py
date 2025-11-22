"""Graph domain models aligned with gRPC contracts.

@llm-type library.models.graph
@llm-does define core Graph / Node / Edge types shared across CLI, services, and UI
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class GraphType(str, Enum):
    """Graph structure semantics.

    Mirrors unhinged.graph.v1.GraphType but used as the Python-first source of truth.
    """

    DAG = "DAG"
    CYCLIC = "CYCLIC"
    CYCLIC_WITH_BREAKERS = "CYCLIC_WITH_BREAKERS"
    TREE = "TREE"
    UNRESTRICTED = "UNRESTRICTED"


class NodeType(str, Enum):
    """Supported node kinds for the graph engine.

    Mirrors unhinged.graph.v1.NodeType values.
    """

    SPEECH_TO_TEXT = "SPEECH_TO_TEXT"
    TEXT_TO_SPEECH = "TEXT_TO_SPEECH"
    LLM_CHAT = "LLM_CHAT"
    LLM_COMPLETION = "LLM_COMPLETION"
    VISION_AI = "VISION_AI"
    IMAGE_GENERATION = "IMAGE_GENERATION"
    CONTEXT_HYDRATION = "CONTEXT_HYDRATION"
    PROMPT_ENHANCEMENT = "PROMPT_ENHANCEMENT"
    DATA_TRANSFORM = "DATA_TRANSFORM"
    CONDITIONAL = "CONDITIONAL"
    LOOP_BREAKER = "LOOP_BREAKER"
    HTTP_REQUEST = "HTTP_REQUEST"
    CUSTOM_SERVICE = "CUSTOM_SERVICE"


class ExecutionStatus(str, Enum):
    """Execution state for graphs and nodes."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


@dataclass
class Edge:
    """Directed connection between two nodes.

    Matches unhinged.graph.v1.Edge at the semantic level.
    """

    id: str
    source_node_id: str
    target_node_id: str
    source_output: str = ""
    target_input: str = ""


@dataclass
class Node:
    """Graph node with typed configuration.

    The config dict is intentionally unstructured here; specific node types can
    wrap it with richer accessors as needed.
    """

    id: str
    name: str
    type: NodeType
    config: dict[str, Any] = field(default_factory=dict)


@dataclass
class Graph:
    """Graph definition shared by CLI, services, and UI.

    This is the Python-first representation that all higher layers should use.
    Adapters will translate to/from gRPC `Graph` messages and database documents.
    """

    id: str
    name: str
    description: str = ""
    graph_type: GraphType = GraphType.DAG
    nodes: list[Node] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)
    # Generic metadata bag; corresponds to ResourceMetadata and friends at the
    # contract layer but is kept as a dict here to avoid overfitting.
    metadata: dict[str, Any] = field(default_factory=dict)
