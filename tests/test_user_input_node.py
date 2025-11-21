"""Tests for UserInputNode and hypothesis system.

@llm-type test.user_input_node
@llm-does verify UserInputNode execution and hypothesis selection
"""

import pytest

from libs.python.graph import Graph, UserInputNode
from libs.python.query_planner import (
    build_audio_volume_hypotheses,
    build_audio_volume_plan,
)


class TestUserInputNode:
    """Tests for UserInputNode graph node."""

    @pytest.mark.asyncio
    async def test_user_input_node_multiple_choice(self, monkeypatch) -> None:
        """UserInputNode with multiple options returns selected option."""
        node = UserInputNode(
            node_id="test_input",
            prompt="Choose an option:",
            options=["Option A", "Option B", "Option C"],
        )

        # Simulate user selecting option 2
        monkeypatch.setattr("builtins.input", lambda _: "2")

        result = await node.execute()

        assert result["success"] is True
        assert result["user_input"] == "Option B"
        assert result["selected_option"] == 1

    @pytest.mark.asyncio
    async def test_user_input_node_yes_no_prompt(self, monkeypatch) -> None:
        """UserInputNode with yes/no prompt returns confirmed flag."""
        node = UserInputNode(
            node_id="test_confirm",
            prompt="Do you want to proceed?",
        )

        # Simulate user saying yes
        monkeypatch.setattr("builtins.input", lambda _: "yes")

        result = await node.execute()

        assert result["success"] is True
        assert result["confirmed"] is True
        assert result["user_input"] == "yes"

    @pytest.mark.asyncio
    async def test_user_input_node_no_response(self, monkeypatch) -> None:
        """UserInputNode with no response returns confirmed=False."""
        node = UserInputNode(
            node_id="test_confirm",
            prompt="Do you want to proceed?",
        )

        # Simulate user saying no
        monkeypatch.setattr("builtins.input", lambda _: "no")

        result = await node.execute()

        assert result["success"] is True
        assert result["confirmed"] is False


class TestHypothesisSystem:
    """Tests for hypothesis and alternative route system."""

    def test_build_audio_volume_hypotheses(self) -> None:
        """build_audio_volume_hypotheses creates multiple diagnostic routes."""
        query = "my headphone volume is too low"
        hypothesis_set = build_audio_volume_hypotheses(query)

        assert hypothesis_set.query == query
        assert len(hypothesis_set.hypotheses) == 3
        assert hypothesis_set.hypotheses[0].id == "pactl_tools"
        assert hypothesis_set.hypotheses[1].id == "pipewire_native"
        assert hypothesis_set.hypotheses[2].id == "interactive_branching"

    def test_hypothesis_selection(self) -> None:
        """HypothesisSet can select and retrieve hypotheses."""
        query = "my headphone volume is too low"
        hypothesis_set = build_audio_volume_hypotheses(query)

        # Select pipewire hypothesis
        hypothesis_set.select_hypothesis("pipewire_native")

        selected = hypothesis_set.get_selected()
        assert selected is not None
        assert selected.id == "pipewire_native"
        assert selected.name == "PipeWire Native Commands"

    def test_pipewire_alternative_plan(self) -> None:
        """PipeWire alternative plan uses pw-dump and pw-cli commands."""
        query = "my headphone volume is too low"
        hypothesis_set = build_audio_volume_hypotheses(query)

        pipewire_hyp = hypothesis_set.hypotheses[1]
        plan = pipewire_hyp.plan

        # Check that plan has PipeWire-specific commands
        command_ids = {node.id for node in plan.nodes}
        assert "pw_dump" in command_ids
        assert "pw_cli_list" in command_ids

        # Check that pactl commands are not in PipeWire plan
        commands = {node.params.get("command", "") for node in plan.nodes if node.type == "unix_command"}
        assert not any("pactl" in cmd for cmd in commands)

    def test_pactl_plan_has_confirmation_node(self) -> None:
        """Default pactl plan includes user confirmation node."""
        plan = build_audio_volume_plan("my headphone volume is too low")

        # Check for confirmation node
        node_ids = {node.id for node in plan.nodes}
        assert "confirm_pactl_install" in node_ids

        # Check that it's a user_input type
        confirm_node = next(n for n in plan.nodes if n.id == "confirm_pactl_install")
        assert confirm_node.type == "user_input"
        assert "options" in confirm_node.params
