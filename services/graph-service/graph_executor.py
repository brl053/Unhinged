#!/usr/bin/env python3
"""Pure-Python Graph execution engine (no gRPC).

@llm-type service.core
@llm-does execute libs.python.models.graph.Graph instances using local services
"""

from __future__ import annotations

import asyncio
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

# Make libs.python importable when running as a service script
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from events import create_service_logger
from node_executors import NodeExecutorFactory

from libs.python.models.events.schema import EventKind, GraphEvent, GraphEventType
from libs.python.models.graph.schema import Edge, ExecutionStatus, Graph, GraphType, Node

# Initialize event logger
events = create_service_logger("graph-executor", "1.0.0 (models.graph)")


class GraphExecutor:
    """Core Graph execution engine using Python models.

    In-memory only: callers are responsible for persistence.
    """

    def __init__(self) -> None:
        self.graphs: dict[str, Graph] = {}
        self.executions: dict[str, dict[str, Any]] = {}
        self.node_factory = NodeExecutorFactory()
        events.info("Graph executor initialized (libs.python.models.graph)")

    async def create_graph(self, graph: Graph) -> str:
        """Create and store a Graph definition."""

        if not graph.id:
            graph.id = str(uuid.uuid4())

        self._validate_graph(graph)
        self.graphs[graph.id] = graph

        events.info(
            "Graph created and stored",
            {
                "graph_id": graph.id,
                "name": graph.name,
                "node_count": len(graph.nodes),
                "edge_count": len(graph.edges),
            },
        )

        return graph.id

    async def get_graph(self, graph_id: str) -> Graph:
        """Retrieve a Graph definition by id."""

        if graph_id not in self.graphs:
            raise ValueError(f"Graph not found: {graph_id}")
        return self.graphs[graph_id]

    async def list_graphs(self) -> list[Graph]:
        """Return all graphs (callers can filter)."""

        return list(self.graphs.values())

    async def delete_graph(self, graph_id: str) -> None:
        """Delete a Graph definition, failing if executions are running."""

        if graph_id not in self.graphs:
            raise ValueError(f"Graph not found: {graph_id}")

        running = [
            exec_id
            for exec_id, data in self.executions.items()
            if data.get("graph_id") == graph_id
            and data.get("status") in {ExecutionStatus.RUNNING, ExecutionStatus.PENDING}
        ]
        if running:
            raise ValueError(f"Cannot delete Graph with running executions: {running}")

        del self.graphs[graph_id]
        events.info("Graph deleted", {"graph_id": graph_id})

    async def execute_graph(
        self,
        graph_id: str,
        input_data: dict[str, Any] | None = None,
        execution_id: str | None = None,
    ) -> str:
        """Start asynchronous execution of a stored graph."""

        if graph_id not in self.graphs:
            raise ValueError(f"Graph not found: {graph_id}")

        if execution_id is None:
            execution_id = str(uuid.uuid4())

        graph = self.graphs[graph_id]

        state: dict[str, Any] = {
            "execution_id": execution_id,
            "graph_id": graph_id,
            "status": ExecutionStatus.RUNNING,
            "started_at": datetime.utcnow().isoformat(),
            "input_data": input_data or {},
            "node_states": {},
            "events": [],  # list[GraphEvent]
        }

        self.executions[execution_id] = state
        asyncio.create_task(self._execute_graph_async(graph, state))

        events.info(
            "Graph execution initiated",
            {"graph_id": graph_id, "execution_id": execution_id},
        )

        return execution_id

    async def _execute_graph_async(self, graph: Graph, execution_state: dict[str, Any]) -> None:
        """Execute a graph asynchronously using topological order and events."""

        try:
            execution_id = execution_state["execution_id"]

            # Add execution started event
            self._add_execution_event(
                execution_state,
                event_type=GraphEventType.EXECUTION_STARTED,
                node_id=None,
                details={},
            )

            node_map: dict[str, Node] = {node.id: node for node in graph.nodes}
            edge_map = self._build_edge_map(graph.edges)

            executed_nodes: set[str] = set()

            while len(executed_nodes) < len(graph.nodes):
                ready_nodes: list[Node] = []
                for node in graph.nodes:
                    if node.id not in executed_nodes:
                        dependencies = edge_map.get(node.id, [])
                        if all(dep in executed_nodes for dep in dependencies):
                            ready_nodes.append(node)

                if not ready_nodes:
                    raise RuntimeError("Circular dependency detected or no ready nodes")

                tasks = [self._execute_node(node, execution_state, node_map) for node in ready_nodes]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                for node, result in zip(ready_nodes, results, strict=False):  # type: ignore[arg-type]
                    if isinstance(result, Exception):
                        await self._handle_node_failure(node, execution_state, result)
                        return
                    executed_nodes.add(node.id)

            execution_state["status"] = ExecutionStatus.COMPLETED
            execution_state["completed_at"] = datetime.utcnow().isoformat()
            self._add_execution_event(
                execution_state,
                event_type=GraphEventType.EXECUTION_COMPLETED,
                node_id=None,
                details={},
            )

            events.info("Graph execution completed", {"execution_id": execution_id})

        except Exception as exc:
            execution_state["status"] = ExecutionStatus.FAILED
            execution_state["error_message"] = str(exc)
            execution_state["completed_at"] = datetime.utcnow().isoformat()
            self._add_execution_event(
                execution_state,
                event_type=GraphEventType.EXECUTION_FAILED,
                node_id=None,
                details={"error": str(exc)},
            )

            events.error(
                "Graph execution failed",
                exception=exc,
                metadata={"execution_id": execution_state["execution_id"]},
            )

    async def _execute_node(self, node: Node, execution_state: dict[str, Any], node_map: dict[str, Node]) -> None:
        """Execute a single node instance from models.graph."""

        node_id = node.id

        try:
            self._add_execution_event(
                execution_state,
                event_type=GraphEventType.NODE_STARTED,
                node_id=node_id,
                details={},
            )

            executor = self.node_factory.get_executor(node.type)
            input_data = self._collect_node_inputs(node, execution_state, node_map)
            output_data = await executor.execute(node, input_data)

            execution_state["node_states"][node_id] = {
                "status": ExecutionStatus.COMPLETED,
                "started_at": datetime.utcnow().isoformat(),
                "completed_at": datetime.utcnow().isoformat(),
                "output_data": output_data,
            }

            self._add_execution_event(
                execution_state,
                event_type=GraphEventType.NODE_COMPLETED,
                node_id=node_id,
                details=output_data,
            )

            events.info(
                "Node executed successfully",
                {
                    "node_id": node_id,
                    "node_type": node.type,
                    "execution_id": execution_state["execution_id"],
                },
            )

        except Exception as exc:
            execution_state["node_states"][node_id] = {
                "status": ExecutionStatus.FAILED,
                "started_at": datetime.utcnow().isoformat(),
                "completed_at": datetime.utcnow().isoformat(),
                "error_message": str(exc),
            }

            self._add_execution_event(
                execution_state,
                event_type=GraphEventType.NODE_FAILED,
                node_id=node_id,
                details={"error": str(exc)},
            )
            raise

    def _collect_node_inputs(
        self, node: Node, execution_state: dict[str, Any], node_map: dict[str, Node]
    ) -> dict[str, Any]:
        """Collect input data for a node from its dependencies.

        For now this simply returns the execution-level input_data. Edge-level
        data routing can be layered in using the Edge model when needed.
        """

        del node, node_map  # unused for now
        return dict(execution_state.get("input_data", {}))

    def _build_edge_map(self, edges: list[Edge]) -> dict[str, list[str]]:
        """Build a map of node dependencies from edges"""
        edge_map: dict[str, list[str]] = {}
        for edge in edges:
            target = edge.target_node_id
            source = edge.source_node_id

            if target not in edge_map:
                edge_map[target] = []
            edge_map[target].append(source)

        return edge_map

    def _add_execution_event(
        self,
        execution_state: dict[str, Any],
        *,
        event_type: GraphEventType,
        node_id: str | None,
        details: dict[str, Any],
    ) -> None:
        """Append a GraphEvent to the in-memory execution log."""

        event = GraphEvent(
            id=str(uuid.uuid4()),
            kind=EventKind.GRAPH,
            created_at=datetime.utcnow(),
            payload={},
            stream="graph-execution",
            correlation_id=execution_state["execution_id"],
            causation_id=None,
            event_type=event_type,
            graph_id=execution_state["graph_id"],
            node_id=node_id,
            details=details,
        )
        execution_state.setdefault("events", []).append(event)

    async def _handle_node_failure(self, node: Node, execution_state: dict[str, Any], error: Exception) -> None:
        """Handle node execution failure by marking execution as failed and logging."""

        execution_state["status"] = ExecutionStatus.FAILED
        execution_state["error_message"] = f"Node {node.id} failed: {error}"  # noqa: EM102
        execution_state["completed_at"] = datetime.utcnow().isoformat()

        self._add_execution_event(
            execution_state,
            event_type=GraphEventType.EXECUTION_FAILED,
            node_id=None,
            details={"failed_node": node.id, "error": str(error)},
        )

    def _validate_graph(self, graph: Graph) -> None:
        """Validate Graph structure based on graph_type.

        Mirrors the high-level semantics of the original gRPC contracts but operates
        purely on the Python models.
        """

        if not graph.nodes:
            raise ValueError("Graph must have at least one node")

        # Check for duplicate node IDs
        node_ids = [node.id for node in graph.nodes]
        if len(node_ids) != len(set(node_ids)):
            raise ValueError("Duplicate node IDs found")

        # Validate edges reference existing nodes
        for edge in graph.edges:
            if edge.source_node_id not in node_ids:
                raise ValueError(f"Edge references non-existent source node: {edge.source_node_id}")
            if edge.target_node_id not in node_ids:
                raise ValueError(f"Edge references non-existent target node: {edge.target_node_id}")

        # Validate based on graph type
        if graph.graph_type == GraphType.DAG and self._has_cycle(graph.nodes, graph.edges):
            # DAG validation: detect cycles
            raise ValueError("DAG graph type does not allow cycles")
        if graph.graph_type == GraphType.TREE and not self._is_tree(graph.nodes, graph.edges):
            # Tree validation: each node (except root) has exactly one parent
            raise ValueError("TREE graph type requires strict tree structure")
        # Other types: no additional structural validation for now

    def _has_cycle(self, nodes: list[Node], edges: list[Edge]) -> bool:
        """Detect cycles in graph using DFS."""

        # Build adjacency list
        adj: dict[str, list[str]] = {node.id: [] for node in nodes}
        for edge in edges:
            adj[edge.source_node_id].append(edge.target_node_id)

        visited: set[str] = set()
        rec_stack: set[str] = set()

        def dfs(node_id: str) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)

            for neighbor in adj.get(node_id, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node_id)
            return False

        return any(node.id not in visited and dfs(node.id) for node in nodes)

    def _is_tree(self, nodes: list[Node], edges: list[Edge]) -> bool:
        """Check if graph is a valid tree structure."""

        if not nodes:
            return True

        # Count incoming edges for each node
        incoming_count: dict[str, int] = {node.id: 0 for node in nodes}
        for edge in edges:
            incoming_count[edge.target_node_id] += 1

        # Tree must have exactly one root (0 incoming edges)
        roots = [nid for nid, count in incoming_count.items() if count == 0]
        if len(roots) != 1:
            return False

        # All other nodes must have exactly one incoming edge
        for nid, count in incoming_count.items():
            if nid != roots[0] and count != 1:
                return False

        # Must not have cycles
        return not self._has_cycle(nodes, edges)

    async def cancel_execution(self, execution_id: str) -> None:
        """Cancel a running execution (best-effort, cooperative)."""

        if execution_id not in self.executions:
            raise ValueError(f"Execution not found: {execution_id}")

        execution_state = self.executions[execution_id]

        if execution_state["status"] not in {ExecutionStatus.RUNNING, ExecutionStatus.PENDING}:
            raise ValueError(f"Cannot cancel execution in status: {execution_state['status']}")

        execution_state["status"] = ExecutionStatus.CANCELLED
        execution_state["completed_at"] = datetime.utcnow().isoformat()

        self._add_execution_event(
            execution_state,
            event_type=GraphEventType.EXECUTION_CANCELLED,
            node_id=None,
            details={},
        )

        events.info("Execution cancelled", {"execution_id": execution_id})
