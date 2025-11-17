"""Core graph structures and executor.

@llm-type library.graph.core
@llm-does provide a generic DAG abstraction and async executor for GraphNode
"""

from __future__ import annotations

import asyncio
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any, Optional

from .nodes import GraphNode


@dataclass
class NodeExecutionResult:
    """Execution result for a single node.

    This wraps the raw output dictionary returned by ``GraphNode.execute`` and
    adds a normalized ``success`` flag plus optional error string.
    """

    node_id: str
    output: dict[str, Any]
    success: bool
    error: Optional[str] = None


@dataclass
class GraphExecutionResult:
    """Result of executing a graph of nodes."""

    success: bool
    node_results: dict[str, NodeExecutionResult] = field(default_factory=dict)
    execution_order: list[list[str]] = field(default_factory=list)
    error_message: Optional[str] = None


class Graph:
    """Directed acyclic graph of ``GraphNode`` instances.

    The graph is intentionally minimal: it stores nodes and directed edges and
    can produce execution groups suitable for parallel execution.
    """

    def __init__(self) -> None:
        self.nodes: dict[str, GraphNode] = {}
        self.edges: list[tuple[str, str]] = []

    def add_node(self, node: GraphNode) -> None:
        if node.id in self.nodes:
            raise ValueError(f"Node with id {node.id!r} already exists")
        self.nodes[node.id] = node

    def add_edge(self, source_id: str, target_id: str) -> None:
        if source_id == target_id:
            raise ValueError("Self-loops are not allowed in DAGs")
        if source_id not in self.nodes:
            raise KeyError(f"Unknown source node {source_id!r}")
        if target_id not in self.nodes:
            raise KeyError(f"Unknown target node {target_id!r}")
        self.edges.append((source_id, target_id))

    def _build_adjacency(self) -> tuple[dict[str, list[str]], dict[str, int]]:
        """Return adjacency list and in-degree map for the current graph."""
        adjacency: dict[str, list[str]] = {node_id: [] for node_id in self.nodes}
        indegree: dict[str, int] = {node_id: 0 for node_id in self.nodes}

        for src, dst in self.edges:
            adjacency[src].append(dst)
            indegree[dst] += 1

        return adjacency, indegree

    def topological_groups(self) -> list[list[str]]:
        """Return execution groups for a DAG using Kahn's algorithm.

        Each inner list contains node ids that can be executed in parallel.
        Raises ``ValueError`` if the graph contains a cycle.
        """
        adjacency, indegree = self._build_adjacency()
        ready = [node_id for node_id, deg in indegree.items() if deg == 0]
        groups: list[list[str]] = []
        processed = 0

        while ready:
            # Current layer of nodes that can run in parallel
            group = sorted(ready)
            groups.append(group)
            ready = []

            for node_id in group:
                processed += 1
                for neighbour in adjacency[node_id]:
                    indegree[neighbour] -= 1
                    if indegree[neighbour] == 0:
                        ready.append(neighbour)

        if processed != len(self.nodes):
            raise ValueError("Graph contains a cycle; topological order not possible")

        return groups


class GraphExecutor:
    """Execute graphs of ``GraphNode`` instances with parallelism per layer."""

    async def execute(
        self,
        graph: Graph,
        initial_inputs: Optional[dict[str, dict[str, Any]]] = None,
    ) -> GraphExecutionResult:
        """Execute a graph and return aggregated results.

        ``initial_inputs`` can provide per-node input dictionaries. Outputs
        from upstream nodes are automatically routed to downstream nodes via
        the ``"stdin"`` key when present, which matches UNIX piping semantics.
        """
        initial_inputs = initial_inputs or {}

        try:
            execution_groups = graph.topological_groups()
        except ValueError as exc:  # cycle or invalid DAG
            return GraphExecutionResult(
                success=False,
                error_message=str(exc),
            )

        aggregated_inputs: dict[str, dict[str, Any]] = {
            node_id: dict(payload) for node_id, payload in initial_inputs.items()
        }
        node_results: dict[str, NodeExecutionResult] = {}
        success = True
        error_message: Optional[str] = None

        for group in execution_groups:
            tasks: dict[str, asyncio.Task[dict[str, Any]]] = {}
            for node_id in group:
                node = graph.nodes[node_id]
                input_payload = aggregated_inputs.get(node_id, {})
                tasks[node_id] = asyncio.create_task(node.execute(input_payload))

            # Wait for all nodes in this group to finish
            completed: Iterable[tuple[str, Any]] = zip(
                tasks.keys(), await asyncio.gather(*tasks.values(), return_exceptions=True)
            )

            for node_id, result in completed:
                if isinstance(result, Exception):
                    node_success = False
                    output: dict[str, Any] = {}
                    err = str(result)
                else:
                    output = result
                    node_success = bool(output.get("success", True))
                    err = None

                node_results[node_id] = NodeExecutionResult(
                    node_id=node_id,
                    output=output,
                    success=node_success,
                    error=err,
                )

                if not node_success and success:
                    success = False
                    error_message = err or output.get("stderr") or "Node execution failed"

                # Route stdout from this node into stdin of downstream nodes if needed
                stdout_value = output.get("stdout")
                if stdout_value is not None:
                    for src, dst in graph.edges:
                        if src == node_id:
                            dest_input = aggregated_inputs.setdefault(dst, {})
                            dest_input.setdefault("stdin", stdout_value)

        return GraphExecutionResult(
            success=success,
            node_results=node_results,
            execution_order=execution_groups,
            error_message=error_message,
        )
