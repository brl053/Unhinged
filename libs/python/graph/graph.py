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

    Edges can have optional conditions for runtime branching.
    """

    def __init__(self) -> None:
        self.nodes: dict[str, GraphNode] = {}
        self.edges: list[tuple[str, str, Optional[str]]] = []  # (source, target, condition)

    def add_node(self, node: GraphNode) -> None:
        if node.id in self.nodes:
            raise ValueError(f"Node with id {node.id!r} already exists")
        self.nodes[node.id] = node

    def add_edge(self, source_id: str, target_id: str, condition: Optional[str] = None) -> None:
        if source_id == target_id:
            raise ValueError("Self-loops are not allowed in DAGs")
        if source_id not in self.nodes:
            raise KeyError(f"Unknown source node {source_id!r}")
        if target_id not in self.nodes:
            raise KeyError(f"Unknown target node {target_id!r}")
        self.edges.append((source_id, target_id, condition))

    def _build_adjacency(self) -> tuple[dict[str, list[str]], dict[str, int], dict[tuple[str, str], Optional[str]]]:
        """Return adjacency list, in-degree map, and edge conditions for the current graph."""
        adjacency: dict[str, list[str]] = {node_id: [] for node_id in self.nodes}
        indegree: dict[str, int] = {node_id: 0 for node_id in self.nodes}
        edge_conditions: dict[tuple[str, str], Optional[str]] = {}

        for src, dst, condition in self.edges:
            adjacency[src].append(dst)
            indegree[dst] += 1
            edge_conditions[(src, dst)] = condition

        return adjacency, indegree, edge_conditions

    def topological_groups(self) -> list[list[str]]:
        """Return execution groups for a DAG using Kahn's algorithm.

        Each inner list contains node ids that can be executed in parallel.
        Raises ``ValueError`` if the graph contains a cycle.

        Note: Conditional edges are treated as unconditional for topological ordering.
        Condition evaluation happens at runtime during execution.
        """
        adjacency, indegree, _ = self._build_adjacency()
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

    def _evaluate_condition(self, condition: Optional[str], node_results: dict[str, NodeExecutionResult]) -> bool:
        """Evaluate a condition expression against node results.

        Supports expressions like:
        - "user_input.selected_option == 2"
        - "user_input.confirmed == true"
        """
        if condition is None or not condition:
            return True

        try:
            # Build a safe namespace with node results
            namespace: dict[str, Any] = {}
            for node_id, result in node_results.items():
                namespace[node_id] = result.output

            # Evaluate the condition
            return bool(eval(condition, {"__builtins__": {}}, namespace))
        except Exception:
            # If condition evaluation fails, skip the edge
            return False

    def _should_execute_node(
        self,
        node_id: str,
        graph: Graph,
        node_results: dict[str, NodeExecutionResult],
    ) -> bool:
        """Determine if a node should execute based on incoming edge conditions.

        A node executes if:
        1. It has no incoming edges (source node), OR
        2. All incoming edges have conditions that evaluate to True, OR
        3. At least one incoming edge has no condition (unconditional)

        Returns False if all incoming edges have conditions and at least one evaluates to False.
        """
        # Find all incoming edges to this node
        incoming_edges = [(src, dst, cond) for src, dst, cond in graph.edges if dst == node_id]

        if not incoming_edges:
            # No incoming edges - this is a source node, always execute
            return True

        # Check each incoming edge
        has_unconditional = False
        all_conditions_true = True

        for src, dst, condition in incoming_edges:
            if condition is None:
                # Unconditional edge - node should execute
                has_unconditional = True
            else:
                # Conditional edge - evaluate it
                if not self._evaluate_condition(condition, node_results):
                    all_conditions_true = False

        # Execute if: has unconditional edge OR all conditions are true
        return has_unconditional or all_conditions_true

    async def execute(
        self,
        graph: Graph,
        initial_inputs: Optional[dict[str, dict[str, Any]]] = None,
    ) -> GraphExecutionResult:
        """Execute a graph and return aggregated results.

        ``initial_inputs`` can provide per-node input dictionaries. Outputs
        from upstream nodes are automatically routed to downstream nodes via
        the ``"stdin"`` key when present, which matches UNIX piping semantics.

        Conditional edges are evaluated at runtime based on upstream node outputs.
        Nodes are only executed if all their incoming edges have conditions that
        evaluate to True (or have no condition).
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
                # Check if this node should execute based on incoming edge conditions
                should_execute = self._should_execute_node(node_id, graph, node_results)
                if not should_execute:
                    continue

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
                # Only route if the edge condition (if any) evaluates to True
                stdout_value = output.get("stdout")
                if stdout_value is not None:
                    for src, dst, condition in graph.edges:
                        if src == node_id:
                            # Evaluate condition if present
                            if self._evaluate_condition(condition, node_results):
                                dest_input = aggregated_inputs.setdefault(dst, {})
                                dest_input.setdefault("stdin", stdout_value)

        return GraphExecutionResult(
            success=success,
            node_results=node_results,
            execution_order=execution_groups,
            error_message=error_message,
        )
