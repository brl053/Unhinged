"""Tests for the core graph library.

@llm-type test.graph
@llm-does unit tests for GraphNode, UnixCommandNode, Graph, and GraphExecutor
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

from libs.python.graph import (
    Graph,
    GraphExecutionResult,
    GraphExecutor,
    SubgraphNode,
    UnixCommandNode,
)


class TestUnixCommandNode:
    """Tests for UnixCommandNode execution semantics."""

    @pytest.mark.asyncio
    async def test_execute_simple_command(self) -> None:
        node = UnixCommandNode(node_id="n1", command="echo -n hello")
        result = await node.execute()

        assert result["success"] is True
        assert result["stdout"] == "hello"
        assert result["returncode"] == 0

    @pytest.mark.asyncio
    async def test_execute_failing_command(self) -> None:
        node = UnixCommandNode(node_id="n2", command="false")
        result = await node.execute()

        assert result["success"] is False
        assert isinstance(result["returncode"], int)
        assert result["returncode"] != 0

    @pytest.mark.asyncio
    async def test_execute_with_stdin(self) -> None:
        node = UnixCommandNode(node_id="n3", command="cat")
        payload = "graph-input"
        result = await node.execute({"stdin": payload})

        assert result["success"] is True
        assert result["stdout"] == payload

    @pytest.mark.asyncio
    async def test_timeout_is_reported_as_failure(self) -> None:
        node = UnixCommandNode(node_id="n4", command="sleep 5", timeout=0.1)
        result = await node.execute()

        assert result["success"] is False
        assert result["returncode"] is None
        assert "timed out" in result["stderr"]


class TestGraphTopology:
    """Tests for Graph structure and topological grouping."""

    def test_topological_groups_linear_chain(self) -> None:
        graph = Graph()
        n1 = UnixCommandNode("n1", command="true")
        n2 = UnixCommandNode("n2", command="true")
        n3 = UnixCommandNode("n3", command="true")

        graph.add_node(n1)
        graph.add_node(n2)
        graph.add_node(n3)
        graph.add_edge("n1", "n2")
        graph.add_edge("n2", "n3")

        groups = graph.topological_groups()

        assert groups == [["n1"], ["n2"], ["n3"]]


class TestGraphExecutor:
    """Tests for GraphExecutor parallel execution and piping semantics."""

    @pytest.mark.asyncio
    async def test_execute_independent_nodes(self) -> None:
        graph = Graph()
        n1 = UnixCommandNode("n1", command="echo -n one")
        n2 = UnixCommandNode("n2", command="echo -n two")
        n3 = UnixCommandNode("n3", command="echo -n three")

        for node in (n1, n2, n3):
            graph.add_node(node)

        executor = GraphExecutor()
        result = await executor.execute(graph)

        assert isinstance(result, GraphExecutionResult)
        assert result.success is True
        assert set(result.node_results.keys()) == {"n1", "n2", "n3"}
        assert result.node_results["n1"].output["stdout"] == "one"
        assert result.node_results["n2"].output["stdout"] == "two"
        assert result.node_results["n3"].output["stdout"] == "three"

    @pytest.mark.asyncio
    async def test_execute_respects_dependencies_and_pipes_stdout(self) -> None:
        graph = Graph()
        producer = UnixCommandNode("n1", command="echo -n foo")
        consumer = UnixCommandNode("n2", command="cat")

        graph.add_node(producer)
        graph.add_node(consumer)
        graph.add_edge("n1", "n2")

        executor = GraphExecutor()
        result = await executor.execute(graph)

        prod_out = result.node_results["n1"].output
        cons_out = result.node_results["n2"].output

        assert prod_out["stdout"] == "foo"
        assert cons_out["stdout"] == "foo"

    @pytest.mark.asyncio
    async def test_cycle_detection_returns_error(self) -> None:
        graph = Graph()
        n1 = UnixCommandNode("n1", command="true")
        n2 = UnixCommandNode("n2", command="true")

        graph.add_node(n1)
        graph.add_node(n2)
        graph.add_edge("n1", "n2")
        graph.add_edge("n2", "n1")

        executor = GraphExecutor()
        result = await executor.execute(graph)

        assert result.success is False
        assert result.error_message is not None
        assert "cycle" in result.error_message.lower()


class TestSubgraphNode:
    """Tests for SubgraphNode graph-of-graphs execution semantics."""

    @pytest.mark.asyncio
    async def test_subgraph_executes_inner_graph(self) -> None:
        inner = Graph()
        echo = UnixCommandNode("echo", command="echo -n inner")
        inner.add_node(echo)

        # No stdout adapter: we still expect structured subgraph payload.
        node = SubgraphNode(node_id="sub", subgraph=inner)

        result = await node.execute({})

        assert result["success"] is True
        assert "subgraph" in result
        sub = result["subgraph"]
        assert sub["node_results"]["echo"]["stdout"] == "inner"

    @pytest.mark.asyncio
    async def test_subgraph_can_provide_stdout_via_adapter(self) -> None:
        inner = Graph()
        echo = UnixCommandNode("echo", command="echo -n piped")
        inner.add_node(echo)

        def adapter(exec_result: GraphExecutionResult) -> str:
            return exec_result.node_results["echo"].output["stdout"]

        node = SubgraphNode(node_id="sub", subgraph=inner, stdout_adapter=adapter)

        result = await node.execute({})

        assert result["success"] is True
        assert result["stdout"] == "piped"

    @pytest.mark.asyncio
    async def test_subgraph_failure_propagates_success_flag(self) -> None:
        inner = Graph()
        failing = UnixCommandNode("fail", command="false")
        inner.add_node(failing)

        node = SubgraphNode(node_id="sub", subgraph=inner)

        result = await node.execute({})

        assert result["success"] is False
        assert result["subgraph"]["node_results"]["fail"]["success"] is False
