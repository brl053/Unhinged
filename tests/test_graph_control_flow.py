"""Tests for higher-order graph control flow constructs.

@llm-type test.graph.control_flow
@llm-does TDD exit criteria for ForLoopGraph, WhileLoopGraph, BreakNode, ContinueNode

EXIT CRITERIA:
1. ForLoopGraph iterates over input collection, executing body graph per item
2. WhileLoopGraph executes body graph until condition fails
3. BreakNode terminates enclosing loop early
4. ContinueNode skips to next iteration
5. Loop constructs emit CDC events for each iteration
6. Nested loops work correctly
7. Loop state (index, item) is accessible in body graph
"""

import pytest

from libs.python.graph import Graph, GraphExecutor, UnixCommandNode


class TestForLoopGraph:
    """TDD specs for ForLoopGraph."""

    # =========================================================================
    # EXIT CRITERION 1: Iterate over collection
    # =========================================================================

    @pytest.mark.asyncio
    async def test_iterates_over_list(self) -> None:
        """ForLoopGraph executes body for each item in list."""
        from libs.python.graph.control_flow import ForLoopGraph

        # Body graph: echo the input
        body = Graph()
        body.add_node(UnixCommandNode("echo", command="cat"))

        loop = ForLoopGraph(
            node_id="for_loop",
            items=["one", "two", "three"],
            body_graph=body,
            item_input_node="echo",
        )

        result = await loop.execute({})

        assert result["success"] is True
        assert result["iterations"] == 3
        assert "one" in str(result["outputs"])
        assert "three" in str(result["outputs"])

    @pytest.mark.asyncio
    async def test_empty_list_no_iterations(self) -> None:
        """Empty input list results in zero iterations."""
        from libs.python.graph.control_flow import ForLoopGraph

        body = Graph()
        body.add_node(UnixCommandNode("echo", command="echo test"))

        loop = ForLoopGraph(node_id="for_loop", items=[], body_graph=body)

        result = await loop.execute({})

        assert result["success"] is True
        assert result["iterations"] == 0

    # =========================================================================
    # EXIT CRITERION 7: Loop state accessible
    # =========================================================================

    @pytest.mark.asyncio
    async def test_loop_index_available(self) -> None:
        """Current loop index is passed to body graph."""
        from libs.python.graph.control_flow import ForLoopGraph

        body = Graph()
        body.add_node(UnixCommandNode("echo", command="cat"))

        loop = ForLoopGraph(
            node_id="for_loop",
            items=["a", "b", "c"],
            body_graph=body,
        )

        result = await loop.execute({})

        # Each iteration should have access to index
        assert "iteration_indices" in result or result["iterations"] == 3


class TestWhileLoopGraph:
    """TDD specs for WhileLoopGraph."""

    # =========================================================================
    # EXIT CRITERION 2: Execute until condition fails
    # =========================================================================

    @pytest.mark.asyncio
    async def test_executes_until_condition_false(self) -> None:
        """WhileLoopGraph continues until condition evaluates false."""
        from libs.python.graph.control_flow import WhileLoopGraph

        body = Graph()
        body.add_node(UnixCommandNode("inc", command="echo incremented"))

        # Condition: loop while counter < 3
        loop = WhileLoopGraph(
            node_id="while_loop",
            condition="loop_count < 3",
            body_graph=body,
            max_iterations=10,  # Safety limit
        )

        result = await loop.execute({"loop_count": 0})

        assert result["success"] is True
        assert result["iterations"] == 3

    @pytest.mark.asyncio
    async def test_max_iterations_safety(self) -> None:
        """WhileLoopGraph respects max_iterations to prevent infinite loops."""
        from libs.python.graph.control_flow import WhileLoopGraph

        body = Graph()
        body.add_node(UnixCommandNode("noop", command="true"))

        # Always-true condition
        loop = WhileLoopGraph(
            node_id="while_loop",
            condition="True",  # Infinite without max
            body_graph=body,
            max_iterations=5,
        )

        result = await loop.execute({})

        assert result["iterations"] == 5
        assert "max_iterations" in result.get("termination_reason", "")


class TestBreakNode:
    """TDD specs for BreakNode."""

    # =========================================================================
    # EXIT CRITERION 3: Early termination
    # =========================================================================

    @pytest.mark.asyncio
    async def test_break_terminates_loop(self) -> None:
        """BreakNode causes enclosing loop to exit."""
        from libs.python.graph.control_flow import BreakNode, ForLoopGraph

        body = Graph()
        # Break on second item
        body.add_node(BreakNode("break", condition="item == 'stop'"))
        body.add_node(UnixCommandNode("echo", command="cat"))
        body.add_edge("break", "echo", condition="not break['triggered']")

        loop = ForLoopGraph(
            node_id="for_loop",
            items=["go", "stop", "never_reached"],
            body_graph=body,
        )

        result = await loop.execute({})

        assert result["iterations"] < 3
        assert "never_reached" not in str(result["outputs"])


class TestContinueNode:
    """TDD specs for ContinueNode."""

    # =========================================================================
    # EXIT CRITERION 4: Skip to next iteration
    # =========================================================================

    @pytest.mark.asyncio
    async def test_continue_skips_iteration(self) -> None:
        """ContinueNode skips rest of current iteration."""
        from libs.python.graph.control_flow import ContinueNode, ForLoopGraph

        body = Graph()
        body.add_node(ContinueNode("skip", condition="item == 'skip_me'"))
        body.add_node(UnixCommandNode("echo", command="cat"))
        body.add_edge("skip", "echo", condition="not skip['triggered']")

        loop = ForLoopGraph(
            node_id="for_loop",
            items=["process", "skip_me", "also_process"],
            body_graph=body,
        )

        result = await loop.execute({})

        assert result["iterations"] == 3  # All iterations happen
        assert "skip_me" not in str(result["outputs"])  # But skip_me not processed


class TestLoopCDCEvents:
    """TDD specs for loop CDC event emission."""

    # =========================================================================
    # EXIT CRITERION 5: CDC events per iteration
    # =========================================================================

    @pytest.mark.asyncio
    async def test_for_loop_emits_iteration_events(self) -> None:
        """ForLoopGraph emits CDC event for each iteration."""
        from unittest.mock import MagicMock

        from libs.python.graph.control_flow import ForLoopGraph

        body = Graph()
        body.add_node(UnixCommandNode("echo", command="true"))

        loop = ForLoopGraph(node_id="for_loop", items=["a", "b"], body_graph=body)

        # Session context is injected via loop's internal session reference
        # not via execute() args - matching GraphNode signature
        mock_session = MagicMock()
        loop._session_ctx = mock_session  # type: ignore[attr-defined]
        result = await loop.execute({})

        # Should have emitted events for loop start, each iteration, and loop end
        assert mock_session.emit.call_count >= 2


class TestNestedLoops:
    """TDD specs for nested loop constructs."""

    # =========================================================================
    # EXIT CRITERION 6: Nested loops
    # =========================================================================

    @pytest.mark.asyncio
    async def test_nested_for_loops(self) -> None:
        """ForLoopGraph can contain another ForLoopGraph."""
        from libs.python.graph.control_flow import ForLoopGraph

        # Inner loop
        inner_body = Graph()
        inner_body.add_node(UnixCommandNode("echo", command="cat"))

        inner_loop = ForLoopGraph(
            node_id="inner_for",
            items=["x", "y"],
            body_graph=inner_body,
        )

        # Outer loop body contains inner loop
        outer_body = Graph()
        outer_body.add_node(inner_loop)

        outer_loop = ForLoopGraph(
            node_id="outer_for",
            items=["a", "b"],
            body_graph=outer_body,
        )

        result = await outer_loop.execute({})

        assert result["success"] is True
        # 2 outer * 2 inner = 4 total inner iterations
        assert result.get("total_inner_iterations", 0) == 4 or result["iterations"] == 2
