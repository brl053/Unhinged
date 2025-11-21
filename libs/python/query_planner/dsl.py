"""Structured query planning DSL for `unhinged query`.

@llm-type library.query_planner.dsl
@llm-does define QueryPlan/PlanNode/PlanEdge abstractions and a deterministic
@llm-does planner for the headphone volume diagnostic use case.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import yaml

from libs.python.graph import Graph, UnixCommandNode, UserInputNode

from .hypothesis import Hypothesis, HypothesisSet


@dataclass
class PlanConstraints:
    """Execution constraints for a single plan node.

    read_only: indicates whether the node must not modify system state.
    timeout_seconds: soft timeout for the node's execution.
    """

    read_only: bool = True
    timeout_seconds: float = 10.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "read_only": self.read_only,
            "timeout_seconds": self.timeout_seconds,
        }


@dataclass
class PlanNode:
    """Single step in a query plan.

    type is a logical node type (e.g. "unix_command", "aggregate").
    params holds type-specific configuration.
    """

    id: str
    type: str
    description: str
    params: dict[str, Any] = field(default_factory=dict)
    constraints: PlanConstraints = field(default_factory=PlanConstraints)
    outputs: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "description": self.description,
            "params": dict(self.params),
            "constraints": self.constraints.to_dict(),
            "outputs": list(self.outputs),
        }


@dataclass
class PlanEdge:
    """Directed edge between two plan nodes.

    pipe_output can be used in future to select which output key is piped.
    condition is a string expression evaluated at runtime (e.g., "user_input.selected_option == 2").
    """

    from_node: str
    to_node: str
    pipe_output: str | None = None
    condition: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "from_node": self.from_node,
            "to_node": self.to_node,
        }
        if self.pipe_output is not None:
            data["pipe_output"] = self.pipe_output
        if self.condition is not None:
            data["condition"] = self.condition
        return data


@dataclass
class QueryPlan:
    """High-level plan produced by `unhinged query`.

    YAML is the canonical on-the-wire representation; JSON is derived.
    """

    version: str
    query: str
    intent: str
    domain: str
    nodes: list[PlanNode]
    edges: list[PlanEdge]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "query": self.query,
            "intent": self.intent,
            "domain": self.domain,
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
            "metadata": dict(self.metadata),
        }

    def to_yaml(self) -> str:
        """Serialize plan to YAML (canonical format)."""

        result = yaml.safe_dump(self.to_dict(), sort_keys=False, default_flow_style=False)
        return str(result) if result is not None else ""

    def to_json_compatible(self) -> dict[str, Any]:
        """Return JSON-serialisable representation of the plan."""

        return self.to_dict()


def _detect_audio_intent(query: str) -> tuple[str, str]:
    """Detect audio intent and domain for v1.

    v1 supports "audio volume too low/quiet" diagnostics, including
    headphone-specific and general system/browser/Youtube audio cases.
    """

    text = query.lower()

    volume_keywords = (
        "volume",
        "too quiet",
        "too low",
        "not loud",
        "can't hear",
        "cant hear",
        "hard to hear",
        "really quiet",
        "really low",
    )
    context_keywords = (
        "headphone",
        "headphones",
        "headset",
        "earbuds",
        "youtube",
        "browser",
        "firefox",
        "chrome",
        "all apps",
        "system audio",
        "system sound",
        "system volume",
        "audio",
        "sound",
    )

    low_volume_phrase = "low" in text and any(kw in text for kw in ("audio", "volume", "sound"))

    if (any(kw in text for kw in volume_keywords) or low_volume_phrase) and any(kw in text for kw in context_keywords):
        headphone_terms = ("headphone", "headphones", "headset", "earbuds")
        if any(term in text for term in headphone_terms):
            return "volume_low", "audio/headphone_volume"
        return "volume_low", "audio/system_volume"

    raise ValueError("Only audio volume diagnostics are supported in v1 of `unhinged query`.")


def build_audio_volume_plan(query: str) -> QueryPlan:
    """Build a deterministic plan for low/quiet audio volume diagnostics."""

    intent, domain = _detect_audio_intent(query)

    nodes: list[PlanNode] = []
    edges: list[PlanEdge] = []

    nodes.append(
        PlanNode(
            id="check_audio_server",
            type="unix_command",
            description=("Check if the user-level audio server (PipeWire/PulseAudio) is running."),
            params={
                "command": (
                    "ps aux | grep -E 'pipewire|pulseaudio' | grep -v grep || echo 'no audio server process found'"
                ),
            },
        )
    )

    nodes.append(
        PlanNode(
            id="list_sinks",
            type="unix_command",
            description="List available audio sinks and their volume/mute state.",
            params={"command": "pactl list sinks"},
        )
    )

    nodes.append(
        PlanNode(
            id="list_cards",
            type="unix_command",
            description="List audio cards and currently selected profiles.",
            params={"command": "pactl list cards"},
        )
    )

    nodes.append(
        PlanNode(
            id="alsa_mixer",
            type="unix_command",
            description=("Dump ALSA mixer controls for additional volume/mute diagnostics."),
            params={"command": "amixer scontents || amixer"},
        )
    )

    nodes.append(
        PlanNode(
            id="usb_devices",
            type="unix_command",
            description=("List attached USB devices (for USB headsets like Logitech PRO X2)."),
            params={"command": "lsusb"},
        )
    )

    nodes.append(
        PlanNode(
            id="aggregate",
            type="aggregate",
            description=("Aggregate diagnostic data and prepare for LLM-based interpretation."),
        )
    )

    nodes.append(
        PlanNode(
            id="confirm_pactl_install",
            type="user_input",
            description="Ask user to confirm installation of PulseAudio tools or investigate PipeWire alternative.",
            params={
                "prompt": "PulseAudio tools (pactl) not found. Choose an option:",
                "options": [
                    "Install PulseAudio tools (pulseaudio-utils)",
                    "Use PipeWire-native diagnostics instead",
                    "Skip and investigate manually",
                ],
            },
        )
    )

    edges.extend(
        [
            PlanEdge("check_audio_server", "list_sinks"),
            PlanEdge("check_audio_server", "list_cards"),
            PlanEdge("check_audio_server", "alsa_mixer"),
            PlanEdge("check_audio_server", "usb_devices"),
            PlanEdge("list_sinks", "aggregate"),
            PlanEdge("list_cards", "aggregate"),
            PlanEdge("alsa_mixer", "aggregate"),
            PlanEdge("usb_devices", "aggregate"),
            PlanEdge("aggregate", "confirm_pactl_install"),
        ]
    )

    metadata = {
        "estimated_time_ms": 5000,  # Increased for user input
        "parallelizable": True,
        "node_count": len(nodes),
        "edge_count": len(edges),
        "has_user_input": True,
    }

    return QueryPlan(
        version="1.0",
        query=query,
        intent=intent,
        domain=domain,
        nodes=nodes,
        edges=edges,
        metadata=metadata,
    )


def build_pipewire_alternative_plan(query: str) -> QueryPlan:
    """Build alternative plan using PipeWire-native commands instead of pactl."""

    intent, domain = _detect_audio_intent(query)

    nodes: list[PlanNode] = []
    edges: list[PlanEdge] = []

    nodes.append(
        PlanNode(
            id="check_audio_server",
            type="unix_command",
            description="Check if PipeWire is running.",
            params={"command": "ps aux | grep -E 'pipewire' | grep -v grep"},
        )
    )

    nodes.append(
        PlanNode(
            id="pw_dump",
            type="unix_command",
            description="Dump PipeWire graph and device information.",
            params={"command": 'pw-dump | grep -E \'"name"|"volume"|"mute"\' || echo \'pw-dump not available\''},
        )
    )

    nodes.append(
        PlanNode(
            id="pw_cli_list",
            type="unix_command",
            description="List PipeWire objects and their properties.",
            params={"command": "pw-cli list-objects 2>/dev/null || echo 'pw-cli not available'"},
        )
    )

    nodes.append(
        PlanNode(
            id="alsa_mixer",
            type="unix_command",
            description="Dump ALSA mixer controls.",
            params={"command": "amixer scontents || amixer"},
        )
    )

    nodes.append(
        PlanNode(
            id="usb_devices",
            type="unix_command",
            description="List USB audio devices.",
            params={"command": "lsusb"},
        )
    )

    nodes.append(
        PlanNode(
            id="aggregate",
            type="aggregate",
            description="Aggregate PipeWire diagnostic data.",
        )
    )

    edges.extend(
        [
            PlanEdge("check_audio_server", "pw_dump"),
            PlanEdge("check_audio_server", "pw_cli_list"),
            PlanEdge("check_audio_server", "alsa_mixer"),
            PlanEdge("check_audio_server", "usb_devices"),
            PlanEdge("pw_dump", "aggregate"),
            PlanEdge("pw_cli_list", "aggregate"),
            PlanEdge("alsa_mixer", "aggregate"),
            PlanEdge("usb_devices", "aggregate"),
        ]
    )

    metadata = {
        "estimated_time_ms": 3000,
        "parallelizable": True,
        "node_count": len(nodes),
        "edge_count": len(edges),
        "alternative": "pipewire_native",
    }

    return QueryPlan(
        version="1.0",
        query=query,
        intent=intent,
        domain=domain,
        nodes=nodes,
        edges=edges,
        metadata=metadata,
    )


def build_audio_volume_plan_with_branching(query: str) -> QueryPlan:
    """Build audio volume plan with runtime branching based on user input.

    The plan includes a user_input node that prompts the user to choose between:
    1. Install PulseAudio tools (pactl)
    2. Use PipeWire-native diagnostics
    3. Skip and investigate manually

    Conditional edges route execution based on the user's choice.
    """
    intent = "volume_low"
    domain = "audio/headphone_volume"

    nodes: list[PlanNode] = []
    edges: list[PlanEdge] = []

    # Initial diagnostic nodes (always run)
    audio_server_cmd = "ps aux | grep -E 'pipewire|pulseaudio' | grep -v grep || echo 'no audio server process found'"
    nodes.extend(
        [
            PlanNode(
                id="check_audio_server",
                type="unix_command",
                description="Check if the user-level audio server (PipeWire/PulseAudio) is running.",
                params={"command": audio_server_cmd},
            ),
            PlanNode(
                id="alsa_mixer",
                type="unix_command",
                description="Dump ALSA mixer controls for additional volume/mute diagnostics.",
                params={"command": "amixer scontents || amixer"},
            ),
            PlanNode(
                id="usb_devices",
                type="unix_command",
                description="List attached USB devices (for USB headsets like Logitech PRO X2).",
                params={"command": "lsusb"},
            ),
        ]
    )

    # User choice node
    nodes.append(
        PlanNode(
            id="user_choice",
            type="user_input",
            description="Ask user to choose diagnostic approach.",
            params={
                "prompt": "Choose diagnostic approach:",
                "options": [
                    "Use PulseAudio tools (pactl)",
                    "Use PipeWire-native commands",
                    "Skip and investigate manually",
                ],
            },
        )
    )

    # PulseAudio branch (option 1)
    nodes.extend(
        [
            PlanNode(
                id="pactl_list_sinks",
                type="unix_command",
                description="List available audio sinks and their volume/mute state (PulseAudio).",
                params={"command": "pactl list sinks"},
            ),
            PlanNode(
                id="pactl_list_cards",
                type="unix_command",
                description="List audio cards and currently selected profiles (PulseAudio).",
                params={"command": "pactl list cards"},
            ),
        ]
    )

    # PipeWire branch (option 2)
    nodes.extend(
        [
            PlanNode(
                id="pw_dump",
                type="unix_command",
                description="Dump PipeWire graph and device information.",
                params={"command": "pw-dump"},
            ),
            PlanNode(
                id="pw_cli_list",
                type="unix_command",
                description="List PipeWire objects and their properties.",
                params={"command": "pw-cli list-objects"},
            ),
        ]
    )

    # Aggregate node (runs after any branch)
    nodes.append(
        PlanNode(
            id="aggregate",
            type="aggregate",
            description="Aggregate diagnostic data and prepare for LLM-based interpretation.",
            params={},
        )
    )

    # Initial edges (always execute)
    edges.extend(
        [
            PlanEdge("check_audio_server", "user_choice"),
            PlanEdge("alsa_mixer", "user_choice"),
            PlanEdge("usb_devices", "user_choice"),
        ]
    )

    # Conditional edges from user_choice
    # Option 1: PulseAudio (selected_option == 0)
    edges.extend(
        [
            PlanEdge("user_choice", "pactl_list_sinks", condition="user_choice['selected_option'] == 0"),
            PlanEdge("user_choice", "pactl_list_cards", condition="user_choice['selected_option'] == 0"),
            PlanEdge("pactl_list_sinks", "aggregate"),
            PlanEdge("pactl_list_cards", "aggregate"),
        ]
    )

    # Option 2: PipeWire (selected_option == 1)
    edges.extend(
        [
            PlanEdge("user_choice", "pw_dump", condition="user_choice['selected_option'] == 1"),
            PlanEdge("user_choice", "pw_cli_list", condition="user_choice['selected_option'] == 1"),
            PlanEdge("pw_dump", "aggregate"),
            PlanEdge("pw_cli_list", "aggregate"),
        ]
    )

    # Option 3: Skip (selected_option == 2) - just go to aggregate
    edges.append(PlanEdge("user_choice", "aggregate", condition="user_choice['selected_option'] == 2"))

    metadata = {
        "estimated_time_ms": 5000,
        "parallelizable": True,
        "node_count": len(nodes),
        "edge_count": len(edges),
        "has_user_input": True,
        "has_branching": True,
    }

    return QueryPlan(
        version="1.0",
        query=query,
        intent=intent,
        domain=domain,
        nodes=nodes,
        edges=edges,
        metadata=metadata,
    )


def build_audio_volume_hypotheses(query: str) -> HypothesisSet:
    """Build a set of alternative diagnostic hypotheses for audio volume issues."""

    hypothesis_set = HypothesisSet(query=query)

    # Hypothesis 1: Use PulseAudio tools (default)
    pactl_plan = build_audio_volume_plan(query)
    hypothesis_set.add_hypothesis(
        Hypothesis(
            id="pactl_tools",
            name="PulseAudio Tools (pactl)",
            description="Use PulseAudio command-line tools for diagnostics",
            plan=pactl_plan,
            user_choice=False,
        )
    )

    # Hypothesis 2: Use PipeWire-native commands
    pipewire_plan = build_pipewire_alternative_plan(query)
    hypothesis_set.add_hypothesis(
        Hypothesis(
            id="pipewire_native",
            name="PipeWire Native Commands",
            description="Use PipeWire-native tools (pw-dump, pw-cli) for diagnostics",
            plan=pipewire_plan,
            user_choice=False,
        )
    )

    # Hypothesis 3: Interactive branching (ask user at runtime)
    branching_plan = build_audio_volume_plan_with_branching(query)
    hypothesis_set.add_hypothesis(
        Hypothesis(
            id="interactive_branching",
            name="Interactive Branching",
            description="Ask user to choose diagnostic approach at runtime",
            plan=branching_plan,
            user_choice=True,
        )
    )

    # Set first as default
    hypothesis_set.select_hypothesis("pactl_tools")

    return hypothesis_set


def plan_to_graph(plan: QueryPlan) -> Graph:
    """Compile a QueryPlan into the core Graph representation.

    Supports unix_command and user_input nodes; aggregate and other
    higher-level nodes remain in the plan for LLM consumption.
    """

    graph = Graph()

    for node in plan.nodes:
        if node.type == "unix_command":
            command = node.params.get("command")
            if not command:
                continue
            timeout = float(node.constraints.timeout_seconds)
            graph.add_node(UnixCommandNode(node_id=node.id, command=command, timeout=timeout))

        elif node.type == "user_input":
            prompt = node.params.get("prompt", "Enter input:")
            options = node.params.get("options")
            default = node.params.get("default")
            graph.add_node(
                UserInputNode(
                    node_id=node.id,
                    prompt=prompt,
                    options=options,
                    default=default,
                )
            )

    existing_ids = set(graph.nodes.keys())
    for edge in plan.edges:
        if edge.from_node in existing_ids and edge.to_node in existing_ids:
            graph.add_edge(edge.from_node, edge.to_node, condition=edge.condition)

    return graph
