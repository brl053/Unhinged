"""Tests for conditional branching in graph execution."""

import asyncio

import pytest

from libs.python.graph import Graph, GraphExecutor, UnixCommandNode
from libs.python.graph.graph import GraphNode, NodeExecutionResult


class MockChoiceNode(GraphNode):
    """Mock node that returns a choice without reading from stdin."""

    def __init__(self, node_id: str, selected_option: int) -> None:
        super().__init__(node_id=node_id)
        self.selected_option = selected_option

    async def execute(self, input_payload: dict) -> dict:
        return {
            "user_input": str(self.selected_option),
            "confirmed": True,
            "selected_option": self.selected_option,
            "success": True,
        }


@pytest.mark.asyncio
async def test_conditional_edge_evaluation() -> None:
    """Test that conditional edges are evaluated correctly."""

    graph = Graph()

    # Create a mock choice node that returns selected_option=0
    graph.add_node(MockChoiceNode(node_id="user_choice", selected_option=0))

    # Create two command nodes
    graph.add_node(
        UnixCommandNode(
            node_id="cmd_a",
            command="echo 'Running option A'",
            timeout=5.0,
        )
    )

    graph.add_node(
        UnixCommandNode(
            node_id="cmd_b",
            command="echo 'Running option B'",
            timeout=5.0,
        )
    )

    # Add conditional edges
    # cmd_a runs if user selects option 0
    graph.add_edge("user_choice", "cmd_a", condition="user_choice['selected_option'] == 0")
    # cmd_b runs if user selects option 1
    graph.add_edge("user_choice", "cmd_b", condition="user_choice['selected_option'] == 1")

    executor = GraphExecutor()
    result = await executor.execute(graph)

    # Verify execution succeeded
    assert result.success

    # Verify cmd_a was executed (option 0 selected)
    assert "cmd_a" in result.node_results
    assert result.node_results["cmd_a"].success
    assert "Running option A" in result.node_results["cmd_a"].output.get("stdout", "")

    # Verify cmd_b was NOT executed (option 1 not selected)
    assert "cmd_b" not in result.node_results


@pytest.mark.asyncio
async def test_conditional_edge_option_1() -> None:
    """Test conditional branching with option 1 selected."""

    graph = Graph()

    # Create a mock choice node that returns selected_option=1
    graph.add_node(MockChoiceNode(node_id="user_choice", selected_option=1))

    graph.add_node(
        UnixCommandNode(
            node_id="cmd_a",
            command="echo 'Running option A'",
            timeout=5.0,
        )
    )

    graph.add_node(
        UnixCommandNode(
            node_id="cmd_b",
            command="echo 'Running option B'",
            timeout=5.0,
        )
    )

    graph.add_edge("user_choice", "cmd_a", condition="user_choice['selected_option'] == 0")
    graph.add_edge("user_choice", "cmd_b", condition="user_choice['selected_option'] == 1")

    executor = GraphExecutor()
    result = await executor.execute(graph)

    # Verify execution succeeded
    assert result.success

    # Verify cmd_b was executed (option 1 selected)
    assert "cmd_b" in result.node_results
    assert result.node_results["cmd_b"].success
    assert "Running option B" in result.node_results["cmd_b"].output.get("stdout", "")

    # Verify cmd_a was NOT executed (option 0 not selected)
    assert "cmd_a" not in result.node_results


@pytest.mark.asyncio
async def test_unconditional_edges_always_execute() -> None:
    """Test that unconditional edges always execute regardless of conditions."""

    graph = Graph()

    # Create a mock choice node that returns selected_option=1
    graph.add_node(MockChoiceNode(node_id="user_choice", selected_option=1))

    graph.add_node(
        UnixCommandNode(
            node_id="cmd_always",
            command="echo 'Always runs'",
            timeout=5.0,
        )
    )

    graph.add_node(
        UnixCommandNode(
            node_id="cmd_conditional",
            command="echo 'Conditional'",
            timeout=5.0,
        )
    )

    # Unconditional edge - always runs
    graph.add_edge("user_choice", "cmd_always")
    # Conditional edge - only runs if option 0
    graph.add_edge("user_choice", "cmd_conditional", condition="user_choice['selected_option'] == 0")

    executor = GraphExecutor()
    result = await executor.execute(graph)

    # Verify execution succeeded
    assert result.success

    # Verify cmd_always was executed (unconditional)
    assert "cmd_always" in result.node_results
    assert result.node_results["cmd_always"].success

    # Verify cmd_conditional was NOT executed (condition not met)
    assert "cmd_conditional" not in result.node_results
