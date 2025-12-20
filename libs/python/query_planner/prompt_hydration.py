"""Prompt hydration for intent analysis.

@llm-type library.query_planner.prompt_hydration
@llm-does provides runtime context injection for grounded LLM intent classification

Hydration injects the available action space into the LLM prompt:
- CLI commands (introspected from Click)
- Available graphs (from document store)
- Linux commands (curated safe list)
- Session context (CDC feed, LRU outputs)

This grounds the LLM in reality: it knows what actions are actually available.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from libs.python.graph.context import SessionContext

# Curated list of safe Linux commands for voice operation
# Organized by category for prompt clarity
LINUX_COMMANDS: dict[str, list[str]] = {
    "disk": [
        "df -h",
        "du -sh *",
        "lsblk",
    ],
    "process": [
        "ps aux",
        "top -bn1 | head -20",
        "htop",
        "pgrep -a",
    ],
    "network": [
        "ip addr",
        "ping -c 3",
        "curl -s",
        "ss -tuln",
    ],
    "system": [
        "uptime",
        "free -h",
        "uname -a",
        "cat /etc/os-release",
    ],
    "audio": [
        "pw-cli ls",
        "wpctl status",
        "wpctl get-volume @DEFAULT_SINK@",
        "wpctl set-volume @DEFAULT_SINK@",
    ],
    "gpu": [
        "nvidia-smi",
        "nvidia-smi --query-gpu=utilization.gpu --format=csv",
    ],
    "files": [
        "ls -la",
        "find . -name",
        "cat",
        "head",
        "tail",
    ],
    "logs": [
        "journalctl -xe",
        "journalctl -u",
        "dmesg | tail",
    ],
}


@dataclass
class HydrationContext:
    """Runtime context for prompt hydration.

    Collected before intent analysis to ground the LLM in available actions.
    """

    cli_commands: list[dict[str, Any]] = field(default_factory=list)
    available_graphs: list[dict[str, Any]] = field(default_factory=list)
    linux_commands: dict[str, list[str]] = field(default_factory=lambda: LINUX_COMMANDS.copy())
    session_outputs: dict[str, Any] = field(default_factory=dict)
    recent_cdc: list[dict[str, Any]] = field(default_factory=list)

    def to_prompt_section(self) -> str:
        """Format hydration context as a prompt section."""
        sections = []

        # CLI commands
        if self.cli_commands:
            cmds = "\n".join(f"  - unhinged {c['name']}: {c.get('help', '')}" for c in self.cli_commands[:20])
            sections.append(f"## Available CLI Commands\n\n{cmds}")

        # Graphs
        if self.available_graphs:
            graphs = "\n".join(
                f"  - {g.get('name', g.get('id', '?'))}: {g.get('description', 'No description')}"
                for g in self.available_graphs[:10]
            )
            sections.append(f"## Available Graphs\n\n{graphs}")

        # Linux commands (abbreviated)
        if self.linux_commands:
            linux_lines: list[str] = []
            for category, cmd_list in self.linux_commands.items():
                linux_lines.append(f"  {category}: {', '.join(cmd_list[:3])}")
            sections.append("## Linux Commands\n\n" + "\n".join(linux_lines))

        # Session context
        if self.session_outputs:
            outputs_json = json.dumps(list(self.session_outputs.keys())[:5])
            sections.append(f"## Session Context\n\nRecent outputs: {outputs_json}")

        return "\n\n".join(sections)


def get_cli_commands() -> list[dict[str, Any]]:
    """Introspect available Unhinged CLI commands via Click."""
    commands: list[dict[str, Any]] = []
    try:
        from cli.core.app import cli

        ctx = cli.make_context("unhinged", [])
        for name in cli.list_commands(ctx):
            cmd = cli.get_command(ctx, name)
            if not cmd:
                continue
            help_str = cmd.get_short_help_str(limit=60) if hasattr(cmd, "get_short_help_str") else ""
            commands.append({"name": name, "help": help_str})
    except Exception:
        pass  # CLI introspection is best-effort
    return commands


def get_available_graphs(limit: int = 20) -> list[dict[str, Any]]:
    """Query document store for available graphs."""
    graphs: list[dict[str, Any]] = []
    try:
        from libs.python.persistence import get_document_store

        store = get_document_store()
        docs = store.query("graphs", filters=None, limit=limit)
        graphs = [
            {
                "id": doc.id,
                "name": doc.data.get("name", doc.id),
                "description": doc.data.get("description", ""),
                "tags": doc.data.get("tags", []),
            }
            for doc in docs
        ]
    except Exception:
        pass  # Document store query is best-effort
    return graphs


def get_session_context(session: SessionContext | None, max_cdc: int = 10) -> dict[str, Any]:
    """Extract relevant session context for prompt hydration.

    Args:
        session: The SessionContext to extract from
        max_cdc: Maximum number of recent CDC events to include

    Returns:
        Dict with outputs and recent_cdc for hydration
    """
    if session is None:
        return {"outputs": {}, "recent_cdc": []}

    # Get LRU cached outputs
    outputs = session.get_all_outputs()

    # Get recent CDC events (last N)
    cdc_feed = session.cdc_feed()
    recent_cdc = [{"type": e.event_type.value, "data": e.data, "stage": e.stage} for e in cdc_feed[-max_cdc:]]

    return {"outputs": outputs, "recent_cdc": recent_cdc}


def build_hydration_context(session: SessionContext | None = None) -> HydrationContext:
    """Build complete hydration context for intent analysis.

    This is the main entry point - collects all context sources.

    Args:
        session: Optional SessionContext for session-aware hydration

    Returns:
        HydrationContext ready for prompt injection
    """
    cli_commands = get_cli_commands()
    available_graphs = get_available_graphs()
    session_data = get_session_context(session)

    return HydrationContext(
        cli_commands=cli_commands,
        available_graphs=available_graphs,
        linux_commands=LINUX_COMMANDS.copy(),
        session_outputs=session_data.get("outputs", {}),
        recent_cdc=session_data.get("recent_cdc", []),
    )
