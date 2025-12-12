"""Graph loader for JSON graph definitions.

@llm-type library.graph.loader
@llm-does load JSON graph definitions into executable Graph objects
"""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from .generation_nodes import (
    AudioGenerationNode,
    ImageGenerationNode,
    TextGenerationNode,
    VideoGenerationNode,
)
from .graph import Graph
from .nodes import (
    GraphNode,
    HumanFeedbackNode,
    LLMNode,
    RecallNode,
    RubricGradeNode,
    StructuredOutputNode,
    SubgraphNode,
    UnixCommandNode,
    UserInputNode,
    WebSearchNode,
)


class GraphLoadError(Exception):
    """Raised when a graph definition cannot be loaded."""


# Registry of node type names to node classes
NODE_TYPE_REGISTRY: dict[str, type[GraphNode]] = {
    "unix": UnixCommandNode,
    "llm": LLMNode,
    "structured_llm": StructuredOutputNode,
    "user_input": UserInputNode,
    "rubric_grade": RubricGradeNode,
    "recall": RecallNode,
    "subgraph": SubgraphNode,
    "web_search": WebSearchNode,
    "human_feedback": HumanFeedbackNode,
    "text_gen": TextGenerationNode,
    "image_gen": ImageGenerationNode,
    "audio_gen": AudioGenerationNode,
    "video_gen": VideoGenerationNode,
}


def load_graph_from_json(json_path: str | Path) -> Graph:
    """Load a graph from a JSON file.

    Args:
        json_path: Path to the JSON graph definition file.

    Returns:
        Executable Graph object.

    Raises:
        GraphLoadError: If the file cannot be loaded or parsed.
    """
    path = Path(json_path)
    if not path.exists():
        raise GraphLoadError(f"Graph file not found: {path}")

    try:
        with path.open() as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        raise GraphLoadError(f"Invalid JSON in {path}: {exc}") from exc

    return load_graph_from_dict(data)


def load_graph_from_dict(data: dict[str, Any]) -> Graph:
    """Load a graph from a dictionary (parsed JSON).

    Expected format:
    {
        "name": "Graph Name",
        "description": "...",
        "nodes": [
            {"id": "node1", "type": "unix", "command": "..."},
            {"id": "node2", "type": "llm", "config": {...}},
            ...
        ],
        "edges": [
            {"from": "node1", "to": "node2"},
            {"from": "node2", "to": "node3", "condition": "..."},
            ...
        ]
    }
    """
    graph = Graph()

    # Load nodes
    nodes_data = data.get("nodes", [])
    for node_def in nodes_data:
        node = _create_node(node_def)
        graph.add_node(node)

    # Load edges
    edges_data = data.get("edges", [])
    for edge_def in edges_data:
        source = edge_def.get("from")
        target = edge_def.get("to")
        condition = edge_def.get("condition")

        if not source or not target:
            raise GraphLoadError(f"Edge missing 'from' or 'to': {edge_def}")

        graph.add_edge(source, target, condition)

    return graph


def _create_node(node_def: dict[str, Any]) -> GraphNode:
    """Create a GraphNode from a node definition dict."""
    node_id = node_def.get("id")
    node_type = node_def.get("type")

    if not node_id:
        raise GraphLoadError(f"Node missing 'id': {node_def}")
    if not node_type:
        raise GraphLoadError(f"Node '{node_id}' missing 'type'")

    if node_type not in NODE_TYPE_REGISTRY:
        raise GraphLoadError(f"Unknown node type '{node_type}' for node '{node_id}'")

    config = node_def.get("config", {})

    # Dispatch to type-specific factory
    factory = _NODE_FACTORIES.get(node_type)
    if factory is None:
        raise GraphLoadError(f"No factory for node type '{node_type}'")
    return factory(node_id, node_def, config)


def _create_unix_node(node_id: str, node_def: dict[str, Any], config: dict[str, Any]) -> UnixCommandNode:
    command = node_def.get("command", config.get("command", ""))
    return UnixCommandNode(node_id=node_id, command=command, timeout=config.get("timeout", 30.0))


def _create_llm_node(node_id: str, node_def: dict[str, Any], config: dict[str, Any]) -> LLMNode:
    del node_def  # unused
    return LLMNode(
        node_id=node_id,
        model=config.get("model", "llama2"),
        provider=config.get("provider", "ollama"),
        system_prompt=config.get("system_prompt", ""),
        input_template=config.get("input_template", ""),
        max_tokens=config.get("max_tokens", 1024),
        temperature=config.get("temperature", 0.7),
    )


def _create_structured_llm_node(node_id: str, node_def: dict[str, Any], config: dict[str, Any]) -> StructuredOutputNode:
    del node_def  # unused
    return StructuredOutputNode(
        node_id=node_id,
        model=config.get("model", "llama2"),
        provider=config.get("provider", "ollama"),
        system_prompt=config.get("system_prompt", ""),
        input_template=config.get("input_template", ""),
        max_tokens=config.get("max_tokens", 1024),
        temperature=config.get("temperature", 0.7),
        json_schema=config.get("json_schema"),
        max_retries=config.get("max_retries", 2),
    )


def _create_user_input_node(node_id: str, node_def: dict[str, Any], config: dict[str, Any]) -> UserInputNode:
    del node_def  # unused
    return UserInputNode(
        node_id=node_id,
        prompt=config.get("prompt", ""),
        options=config.get("options"),
        default=config.get("default"),
    )


def _create_rubric_grade_node(node_id: str, node_def: dict[str, Any], config: dict[str, Any]) -> RubricGradeNode:
    del node_def  # unused
    return RubricGradeNode(
        node_id=node_id,
        rubric_name=config.get("rubric_name", "invoice_v1"),
        threshold=config.get("threshold"),
    )


def _create_recall_node(node_id: str, node_def: dict[str, Any], config: dict[str, Any]) -> RecallNode:
    del node_def  # unused
    return RecallNode(
        node_id=node_id,
        collection=config.get("collection", "default"),
        limit=config.get("limit", 5),
        threshold=config.get("threshold", 0.7),
    )


def _create_web_search_node(node_id: str, node_def: dict[str, Any], config: dict[str, Any]) -> WebSearchNode:
    del node_def  # unused
    return WebSearchNode(
        node_id=node_id,
        query_template=config.get("query_template", "{{input.query}}"),
        max_results=config.get("max_results", 5),
        max_content_chars=config.get("max_content_chars", 3000),
    )


def _create_human_feedback_node(node_id: str, node_def: dict[str, Any], config: dict[str, Any]) -> HumanFeedbackNode:
    del node_def  # unused
    return HumanFeedbackNode(
        node_id=node_id,
        prompt_template=config.get("prompt_template", "Provide feedback:"),
        options=config.get("options"),
    )


def _create_text_gen_node(node_id: str, node_def: dict[str, Any], config: dict[str, Any]) -> TextGenerationNode:
    del node_def  # unused
    return TextGenerationNode(
        node_id=node_id,
        prompt_template=config.get("prompt_template", "{{input.topic}}"),
        model=config.get("model", "llama2"),
        provider=config.get("provider", "ollama"),
        max_tokens=config.get("max_tokens", 1024),
        temperature=config.get("temperature", 0.7),
        output_dir=config.get("output_dir"),
    )


def _create_image_gen_node(node_id: str, node_def: dict[str, Any], config: dict[str, Any]) -> ImageGenerationNode:
    del node_def  # unused
    return ImageGenerationNode(
        node_id=node_id,
        prompt_template=config.get("prompt_template", "{{input.topic}}"),
        width=config.get("width", 512),
        height=config.get("height", 512),
        num_inference_steps=config.get("num_inference_steps", 20),
        guidance_scale=config.get("guidance_scale", 7.5),
        output_dir=config.get("output_dir"),
    )


def _create_audio_gen_node(node_id: str, node_def: dict[str, Any], config: dict[str, Any]) -> AudioGenerationNode:
    del node_def  # unused
    return AudioGenerationNode(
        node_id=node_id,
        prompt_template=config.get("prompt_template", "{{input.topic}}"),
        voice=config.get("voice", "nova"),
        speed=config.get("speed", 1.0),
        output_dir=config.get("output_dir"),
    )


def _create_video_gen_node(node_id: str, node_def: dict[str, Any], config: dict[str, Any]) -> VideoGenerationNode:
    del node_def  # unused
    return VideoGenerationNode(
        node_id=node_id,
        prompt_template=config.get("prompt_template", "{{input.topic}}"),
        approach=config.get("approach", "frame-interp"),
        duration=config.get("duration", 5),
        fps=config.get("fps", 24),
        width=config.get("width", 512),
        height=config.get("height", 512),
        output_dir=config.get("output_dir"),
    )


# Type alias for node factory functions
NodeFactory = Callable[[str, dict[str, Any], dict[str, Any]], GraphNode]

# Factory dispatch table - maps node type to factory function
_NODE_FACTORIES: dict[str, NodeFactory] = {
    "unix": _create_unix_node,
    "llm": _create_llm_node,
    "structured_llm": _create_structured_llm_node,
    "user_input": _create_user_input_node,
    "rubric_grade": _create_rubric_grade_node,
    "recall": _create_recall_node,
    "web_search": _create_web_search_node,
    "human_feedback": _create_human_feedback_node,
    "text_gen": _create_text_gen_node,
    "image_gen": _create_image_gen_node,
    "audio_gen": _create_audio_gen_node,
    "video_gen": _create_video_gen_node,
}
