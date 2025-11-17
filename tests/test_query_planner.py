"""Tests for the query planner DSL.

@llm-type test.query_planner
@llm-does unit tests for QueryPlan, PlanNode, and headphone volume planner
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

try:
    import libs  # type: ignore[import-not-found]
except ModuleNotFoundError:  # pragma: no cover - defensive path setup
    ROOT = Path(__file__).resolve().parents[1]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    import libs  # type: ignore[import-not-found]  # noqa: F401

from libs.python.query_planner import build_audio_volume_plan, plan_to_graph


class TestAudioVolumePlanner:
    """Tests for the audio volume diagnostic planner."""

    def test_build_audio_volume_plan_basic_headphones(self) -> None:
        """Planner builds a plan with expected nodes and metadata for headphones."""

        query = "The headphone volume on my Logitech Pro X2 is too low"
        plan = build_audio_volume_plan(query)

        assert plan.domain == "audio/headphone_volume"
        assert plan.intent == "volume_low"
        assert plan.query == query
        assert plan.metadata["node_count"] == len(plan.nodes)
        assert plan.metadata["edge_count"] == len(plan.edges)

        node_ids = {node.id for node in plan.nodes}
        expected = {
            "check_audio_server",
            "list_sinks",
            "list_cards",
            "alsa_mixer",
            "usb_devices",
            "aggregate",
        }
        assert expected.issubset(node_ids)

    def test_build_audio_volume_plan_browser_audio(self) -> None:
        """Planner also supports browser/system-wide audio volume queries."""

        query = "why is my audio low from youtube and the browser? might be all apps idk"
        plan = build_audio_volume_plan(query)

        assert plan.domain == "audio/system_volume"
        assert plan.intent == "volume_low"
        assert plan.query == query

    def test_plan_to_graph_creates_unix_command_nodes(self) -> None:
        """Compilation to Graph creates only executable unix_command nodes."""

        query = "Headphone volume is too quiet"
        plan = build_audio_volume_plan(query)
        graph = plan_to_graph(plan)

        # Aggregate node stays in plan only
        assert "aggregate" not in graph.nodes

        for node_id in (
            "check_audio_server",
            "list_sinks",
            "list_cards",
            "alsa_mixer",
            "usb_devices",
        ):
            assert node_id in graph.nodes

        groups = graph.topological_groups()
        assert groups


if __name__ == "__main__":  # pragma: no cover - manual test entry point
    pytest.main([__file__, "-v"])
