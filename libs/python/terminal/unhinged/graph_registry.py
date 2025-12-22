"""Graph registry - Node type handlers and registry pattern.

Provides extensibility for different node types with their own
create, validate, and render behaviors.

Uses canonical types from libs/python/models/graph/schema.py.
"""

from dataclasses import dataclass
from typing import Any, Protocol

from libs.python.terminal.unhinged.graph_types import Node, NodeType

# =============================================================================
# Handler Protocol
# =============================================================================


class NodeTypeHandler(Protocol):
    """Protocol for node type handlers."""

    @property
    def icon(self) -> str:
        """Icon character for this node type."""
        ...

    @property
    def color(self) -> str:
        """Color name for this node type."""
        ...

    def get_default_ports(self) -> list[str]:
        """Get default port names for this node type (input ports, output ports)."""
        ...

    def validate(self, node: Node) -> list[str]:
        """Validate a node, returning list of error messages."""
        ...

    def get_property_schema(self) -> dict[str, Any]:
        """Get schema for node config properties (for editing UI)."""
        ...


# =============================================================================
# Built-in Handlers
# =============================================================================


@dataclass
class LLMChatHandler:
    """Handler for LLM chat nodes."""

    @property
    def icon(self) -> str:
        return "💬"

    @property
    def color(self) -> str:
        return "cyan"

    def get_default_ports(self) -> list[str]:
        return ["in", "out"]

    def validate(self, node: Node) -> list[str]:
        errors = []
        if not node.name:
            errors.append("LLM Chat node must have a name")
        return errors

    def get_property_schema(self) -> dict[str, Any]:
        return {
            "model": {"type": "string", "description": "Model name"},
            "temperature": {"type": "float", "description": "Temperature (0-1)"},
        }


@dataclass
class ConditionalHandler:
    """Handler for conditional/branch nodes."""

    @property
    def icon(self) -> str:
        return "◇"

    @property
    def color(self) -> str:
        return "yellow"

    def get_default_ports(self) -> list[str]:
        return ["in", "true", "false"]

    def validate(self, node: Node) -> list[str]:
        errors = []
        if "expression" not in node.config:
            errors.append("Conditional node must have an expression")
        return errors

    def get_property_schema(self) -> dict[str, Any]:
        return {
            "expression": {"type": "string", "description": "Boolean expression"},
        }


@dataclass
class DataTransformHandler:
    """Handler for data transformation nodes."""

    @property
    def icon(self) -> str:
        return "⚙"

    @property
    def color(self) -> str:
        return "blue"

    def get_default_ports(self) -> list[str]:
        return ["in", "out"]

    def validate(self, node: Node) -> list[str]:
        return []

    def get_property_schema(self) -> dict[str, Any]:
        return {
            "transform": {"type": "string", "description": "Transform expression"},
        }


@dataclass
class SpeechToTextHandler:
    """Handler for speech-to-text nodes."""

    @property
    def icon(self) -> str:
        return "🎤"

    @property
    def color(self) -> str:
        return "green"

    def get_default_ports(self) -> list[str]:
        return ["audio_in", "text_out"]

    def validate(self, node: Node) -> list[str]:
        return []

    def get_property_schema(self) -> dict[str, Any]:
        return {
            "model": {"type": "string", "description": "STT model"},
            "language": {"type": "string", "description": "Language code"},
        }


@dataclass
class TextToSpeechHandler:
    """Handler for text-to-speech nodes."""

    @property
    def icon(self) -> str:
        return "🔊"

    @property
    def color(self) -> str:
        return "magenta"

    def get_default_ports(self) -> list[str]:
        return ["text_in", "audio_out"]

    def validate(self, node: Node) -> list[str]:
        return []

    def get_property_schema(self) -> dict[str, Any]:
        return {
            "voice": {"type": "string", "description": "Voice ID"},
        }


@dataclass
class HTTPRequestHandler:
    """Handler for HTTP request nodes."""

    @property
    def icon(self) -> str:
        return "🌐"

    @property
    def color(self) -> str:
        return "white"

    def get_default_ports(self) -> list[str]:
        return ["in", "out", "error"]

    def validate(self, node: Node) -> list[str]:
        errors = []
        if "url" not in node.config:
            errors.append("HTTP node must have a URL")
        return errors

    def get_property_schema(self) -> dict[str, Any]:
        return {
            "url": {"type": "string", "description": "Request URL"},
            "method": {"type": "enum", "options": ["GET", "POST", "PUT", "DELETE"]},
        }


@dataclass
class LoopBreakerHandler:
    """Handler for loop breaker nodes."""

    @property
    def icon(self) -> str:
        return "↻"

    @property
    def color(self) -> str:
        return "red"

    def get_default_ports(self) -> list[str]:
        return ["in", "continue", "break"]

    def validate(self, node: Node) -> list[str]:
        return []

    def get_property_schema(self) -> dict[str, Any]:
        return {
            "max_iterations": {"type": "int", "description": "Max iterations"},
        }


@dataclass
class GenericNodeHandler:
    """Fallback handler for unknown node types."""

    @property
    def icon(self) -> str:
        return "□"

    @property
    def color(self) -> str:
        return "white"

    def get_default_ports(self) -> list[str]:
        return ["in", "out"]

    def validate(self, node: Node) -> list[str]:
        return []

    def get_property_schema(self) -> dict[str, Any]:
        return {}


# =============================================================================
# Node Registry
# =============================================================================


class NodeRegistry:
    """Registry of node type handlers."""

    _handlers: dict[str, NodeTypeHandler] = {}
    _initialized: bool = False

    @classmethod
    def _ensure_initialized(cls) -> None:
        """Initialize with built-in handlers for canonical NodeType values."""
        if cls._initialized:
            return
        cls._handlers = {
            NodeType.LLM_CHAT.value: LLMChatHandler(),
            NodeType.LLM_COMPLETION.value: LLMChatHandler(),  # Same handler
            NodeType.CONDITIONAL.value: ConditionalHandler(),
            NodeType.DATA_TRANSFORM.value: DataTransformHandler(),
            NodeType.SPEECH_TO_TEXT.value: SpeechToTextHandler(),
            NodeType.TEXT_TO_SPEECH.value: TextToSpeechHandler(),
            NodeType.HTTP_REQUEST.value: HTTPRequestHandler(),
            NodeType.LOOP_BREAKER.value: LoopBreakerHandler(),
            NodeType.VISION_AI.value: GenericNodeHandler(),
            NodeType.IMAGE_GENERATION.value: GenericNodeHandler(),
            NodeType.CONTEXT_HYDRATION.value: GenericNodeHandler(),
            NodeType.PROMPT_ENHANCEMENT.value: GenericNodeHandler(),
            NodeType.CUSTOM_SERVICE.value: GenericNodeHandler(),
        }
        cls._initialized = True

    @classmethod
    def register(cls, node_type: str, handler: NodeTypeHandler) -> None:
        """Register a custom node type handler."""
        cls._ensure_initialized()
        cls._handlers[node_type] = handler

    @classmethod
    def get(cls, node_type: str | NodeType) -> NodeTypeHandler:
        """Get handler for a node type."""
        cls._ensure_initialized()
        key = node_type.value if isinstance(node_type, NodeType) else node_type
        return cls._handlers.get(key, GenericNodeHandler())

    @classmethod
    def all_types(cls) -> list[str]:
        """Get all registered node types."""
        cls._ensure_initialized()
        return list(cls._handlers.keys())

    @classmethod
    def get_icon(cls, node_type: str | NodeType) -> str:
        """Get icon for a node type."""
        return cls.get(node_type).icon

    @classmethod
    def get_color(cls, node_type: str | NodeType) -> str:
        """Get color for a node type."""
        return cls.get(node_type).color
