"""
@llm-type library.graph.template
@llm-does template interpolation DSL for graph nodes

Template DSL v1
---------------

Simple namespace-based path access for template interpolation.

Syntax:
    {{node_id.field}}      - Access node output: nodes["node_id"]["field"]
    {{node_id.a.b.c}}      - Nested access: nodes["node_id"]["a"]["b"]["c"]
    {{session.key}}        - Session data: session.get("key")
    {{session.id}}         - Session ID: session.session_id
    {{session.created_at}} - Session creation time
    {{env.VAR_NAME}}       - Environment variable: os.environ.get("VAR_NAME")

Reserved namespaces:
    - session: SessionContext access
    - env: Environment variables
    - Everything else: Node output access

Behavior:
    - Unresolved paths remain as-is: {{unknown.field}} → "{{unknown.field}}"
    - None values become empty string
    - Non-dict values terminate path traversal

Usage:
    from libs.python.graph.template import interpolate

    result = interpolate(
        template="Hello {{session.user}}, result: {{diagnose.stdout}}",
        nodes={"diagnose": {"stdout": "OK", "code": 0}},
        session=session_context,
    )
"""

from __future__ import annotations

import os
import re
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from libs.python.graph.context import SessionContext

# Reserved namespace prefixes
_RESERVED_NAMESPACES = frozenset({"session", "env"})

# Regex pattern for {{path}} placeholders
_PLACEHOLDER_PATTERN = re.compile(r"\{\{([^}]+)\}\}")


def interpolate(
    template: str,
    nodes: dict[str, Any] | None = None,
    session: SessionContext | None = None,
) -> str:
    """Interpolate template placeholders with values from nodes, session, and env.

    Args:
        template: String with {{path}} placeholders
        nodes: Dict of node_id -> node output dict
        session: Optional SessionContext for {{session.*}} access

    Returns:
        Interpolated string with placeholders replaced
    """
    if not template:
        return template

    nodes = nodes or {}

    def resolve_path(path: str) -> str:
        """Resolve a dotted path to a value."""
        parts = path.strip().split(".")
        if not parts:
            return f"{{{{{path}}}}}"

        namespace = parts[0]
        rest = parts[1:]

        # Handle reserved namespaces
        if namespace == "env":
            return _resolve_env(rest)
        if namespace == "session":
            return _resolve_session(rest, session)

        # Default: node output access
        return _resolve_node(namespace, rest, nodes)

    def replace_match(match: re.Match[str]) -> str:
        path = match.group(1)
        return resolve_path(path)

    return _PLACEHOLDER_PATTERN.sub(replace_match, template)


def _resolve_env(parts: list[str]) -> str:
    """Resolve {{env.VAR_NAME}} to environment variable."""
    if not parts:
        return "{{env}}"
    var_name = parts[0]
    # Ignore further nesting for env vars
    return os.environ.get(var_name, "")


def _resolve_session(parts: list[str], session: SessionContext | None) -> str:
    """Resolve {{session.key}} to session data."""
    if session is None:
        # No session provided, keep placeholder
        return "{{session." + ".".join(parts) + "}}" if parts else "{{session}}"

    if not parts:
        return "{{session}}"

    key = parts[0]

    # Special session attributes
    if key == "id":
        return session.session_id
    if key == "created_at":
        return session.created_at.isoformat()

    # Session data access
    value = session.get(key)

    # Handle nested access into session data
    for part in parts[1:]:
        if isinstance(value, dict):
            value = value.get(part)
        else:
            # Can't traverse further, return original placeholder
            return "{{session." + ".".join(parts) + "}}"

    return _to_string(value)


def _resolve_node(node_id: str, parts: list[str], nodes: dict[str, Any]) -> str:
    """Resolve {{node_id.field}} to node output."""
    if node_id not in nodes:
        # Node not found, keep placeholder
        full_path = ".".join([node_id, *parts]) if parts else node_id
        return f"{{{{{full_path}}}}}"

    value = nodes[node_id]

    # Traverse path
    for part in parts:
        if isinstance(value, dict):
            value = value.get(part)
        else:
            # Can't traverse further, return original placeholder
            full_path = ".".join([node_id, *parts])
            return f"{{{{{full_path}}}}}"

    return _to_string(value)


def _to_string(value: Any) -> str:
    """Convert value to string for interpolation."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)
