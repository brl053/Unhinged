"""Graph data types - Re-exports from shared schema + workspace helpers.

Uses the canonical types from libs/python/models/graph/schema.py.
Adds workspace-specific helper functions for UI operations.
"""

import uuid
from typing import Any

# Re-export canonical types - these are the source of truth
from libs.python.models.graph.schema import (
    Edge,
    ExecutionStatus,
    Graph,
    GraphType,
    Node,
    NodeType,
)

# Re-export for convenience
__all__ = [
    "Edge",
    "ExecutionStatus",
    "Graph",
    "GraphType",
    "Node",
    "NodeType",
    # Helpers
    "create_empty_graph",
    "create_node",
    "create_edge",
    "get_node",
    "get_edges_from",
    "get_edges_to",
    "get_connected_nodes",
    "node_x",
    "node_y",
    "node_description",
    # Loader
    "load_graph_from_document",
    "map_stored_node_type",
]


# =============================================================================
# Type Mapping: stored node types -> canonical NodeType
# =============================================================================

# Map stored node type strings to canonical NodeType enum
# The document store uses simple strings like "unix", "llm", etc.
STORED_TYPE_TO_NODE_TYPE: dict[str, NodeType] = {
    # Runtime node types from libs/python/graph/loader.py
    "unix": NodeType.CUSTOM_SERVICE,
    "llm": NodeType.LLM_CHAT,
    "structured_llm": NodeType.LLM_COMPLETION,
    "user_input": NodeType.CUSTOM_SERVICE,
    "rubric_grade": NodeType.DATA_TRANSFORM,
    "recall": NodeType.CONTEXT_HYDRATION,
    "subgraph": NodeType.CUSTOM_SERVICE,
    "web_search": NodeType.HTTP_REQUEST,
    "human_feedback": NodeType.CUSTOM_SERVICE,
    "text_gen": NodeType.LLM_COMPLETION,
    "image_gen": NodeType.IMAGE_GENERATION,
    "audio_gen": NodeType.TEXT_TO_SPEECH,
    "video_gen": NodeType.CUSTOM_SERVICE,
    "text_classifier": NodeType.DATA_TRANSFORM,
    # Direct mappings
    "speech_to_text": NodeType.SPEECH_TO_TEXT,
    "text_to_speech": NodeType.TEXT_TO_SPEECH,
    "llm_chat": NodeType.LLM_CHAT,
    "llm_completion": NodeType.LLM_COMPLETION,
    "vision_ai": NodeType.VISION_AI,
    "image_generation": NodeType.IMAGE_GENERATION,
    "context_hydration": NodeType.CONTEXT_HYDRATION,
    "prompt_enhancement": NodeType.PROMPT_ENHANCEMENT,
    "data_transform": NodeType.DATA_TRANSFORM,
    "conditional": NodeType.CONDITIONAL,
    "loop_breaker": NodeType.LOOP_BREAKER,
    "http_request": NodeType.HTTP_REQUEST,
    "custom_service": NodeType.CUSTOM_SERVICE,
}


def map_stored_node_type(stored_type: str) -> NodeType:
    """Map a stored node type string to canonical NodeType enum."""
    normalized = stored_type.lower().strip()
    return STORED_TYPE_TO_NODE_TYPE.get(normalized, NodeType.CUSTOM_SERVICE)


# =============================================================================
# Node Config Accessors (UI-specific properties stored in Node.config)
# =============================================================================


def node_x(node: Node) -> int:
    """Get node X position from config."""
    return node.config.get("x", 0)


def node_y(node: Node) -> int:
    """Get node Y position from config."""
    return node.config.get("y", 0)


def node_description(node: Node) -> str:
    """Get node description from config."""
    return node.config.get("description", "")


# =============================================================================
# Graph Helper Functions (operate on canonical Graph/Node/Edge types)
# =============================================================================


def get_node(graph: Graph, node_id: str) -> Node | None:
    """Get a node by ID from a graph."""
    for node in graph.nodes:
        if node.id == node_id:
            return node
    return None


def get_edges_from(graph: Graph, node_id: str) -> list[Edge]:
    """Get all edges originating from a node."""
    return [e for e in graph.edges if e.source_node_id == node_id]


def get_edges_to(graph: Graph, node_id: str) -> list[Edge]:
    """Get all edges going to a node."""
    return [e for e in graph.edges if e.target_node_id == node_id]


def get_connected_nodes(graph: Graph, node_id: str) -> list[str]:
    """Get IDs of all nodes connected to the given node."""
    connected = set()
    for edge in graph.edges:
        if edge.source_node_id == node_id:
            connected.add(edge.target_node_id)
        elif edge.target_node_id == node_id:
            connected.add(edge.source_node_id)
    return list(connected)


# =============================================================================
# Factory Functions
# =============================================================================


def create_empty_graph(graph_id: str, name: str = "Untitled") -> Graph:
    """Create a new empty graph."""
    return Graph(
        id=graph_id,
        name=name,
        description="",
        graph_type=GraphType.DAG,
        nodes=[],
        edges=[],
        metadata={},
    )


def create_node(
    node_id: str | None = None,
    node_type: NodeType = NodeType.DATA_TRANSFORM,
    name: str = "Untitled",
    x: int = 0,
    y: int = 0,
    description: str = "",
    **extra_config: Any,
) -> Node:
    """Create a new node with config for UI properties."""
    if node_id is None:
        node_id = str(uuid.uuid4())[:8]

    config: dict[str, Any] = {
        "x": x,
        "y": y,
        "description": description,
        **extra_config,
    }

    return Node(
        id=node_id,
        name=name,
        type=node_type,
        config=config,
    )


def create_edge(
    source_node_id: str,
    target_node_id: str,
    edge_id: str | None = None,
    source_output: str = "out",
    target_input: str = "in",
) -> Edge:
    """Create a new edge between nodes."""
    if edge_id is None:
        edge_id = str(uuid.uuid4())[:8]

    return Edge(
        id=edge_id,
        source_node_id=source_node_id,
        target_node_id=target_node_id,
        source_output=source_output,
        target_input=target_input,
    )


# =============================================================================
# Graph Loading from Document Store
# =============================================================================


def load_graph_from_document(doc_id: str, doc_data: dict[str, Any]) -> Graph:
    """Load a Graph from a document store document.

    Args:
        doc_id: The document ID (becomes graph ID)
        doc_data: The document data dict containing name, description, content, etc.

    Returns:
        A fully populated Graph object.
    """
    import json

    name = doc_data.get("name", "Untitled")
    description = doc_data.get("description", "")

    # Parse content JSON if present
    content_str = doc_data.get("content", "{}")
    try:
        content = json.loads(content_str) if isinstance(content_str, str) else content_str
    except json.JSONDecodeError:
        content = {}

    # Extract nodes
    nodes_data = content.get("nodes", [])
    nodes: list[Node] = []
    for i, node_def in enumerate(nodes_data):
        node_id = node_def.get("id", f"node_{i}")
        node_name = node_def.get("name", node_id)
        stored_type = node_def.get("type", "custom_service")
        node_type = map_stored_node_type(stored_type)

        # Build config from remaining fields
        config: dict[str, Any] = {}
        for key, value in node_def.items():
            if key not in ("id", "name", "type"):
                config[key] = value

        # Add position if not present (auto-layout)
        if "x" not in config:
            config["x"] = (i % 4) * 20
        if "y" not in config:
            config["y"] = (i // 4) * 10

        nodes.append(
            Node(
                id=node_id,
                name=node_name,
                type=node_type,
                config=config,
            )
        )

    # Extract edges
    edges_data = content.get("edges", [])
    edges: list[Edge] = []
    for i, edge_def in enumerate(edges_data):
        edge_id = edge_def.get("id", f"edge_{i}")
        # Handle both "from"/"to" and "source_node_id"/"target_node_id" formats
        source = edge_def.get("from") or edge_def.get("source_node_id", "")
        target = edge_def.get("to") or edge_def.get("target_node_id", "")

        if source and target:
            edges.append(
                Edge(
                    id=edge_id,
                    source_node_id=source,
                    target_node_id=target,
                    source_output=edge_def.get("source_output", "out"),
                    target_input=edge_def.get("target_input", "in"),
                )
            )

    return Graph(
        id=doc_id,
        name=name,
        description=description,
        graph_type=GraphType.DAG,
        nodes=nodes,
        edges=edges,
        metadata=doc_data.get("metadata", {}),
    )
