#!/usr/bin/env python3
"""
@llm-type service.core
@llm-does Graph execution engine - orchestrates AI service workflows
"""

import asyncio
import sys
import uuid
from collections.abc import AsyncGenerator
from datetime import datetime
from pathlib import Path

# Add generated proto clients to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "generated" / "python" / "clients"))

try:
    from google.protobuf import struct_pb2, timestamp_pb2
    from unhinged_proto_clients import common_pb2, graph_service_pb2
except ImportError as e:
    print(f"❌ Proto clients not found: {e}")
    print("Run 'make generate' to generate proto clients")
    sys.exit(1)

from events import create_service_logger
from node_executors import NodeExecutorFactory

# Initialize event logger
events = create_service_logger("graph-executor", "1.0.0")


class GraphExecutor:
    """Core Graph execution engine"""

    def __init__(self):
        self.graphs: dict[str, graph_service_pb2.Graph] = {}
        self.executions: dict[str, dict] = {}
        self.node_factory = NodeExecutorFactory()
        events.info("Graph executor initialized")

    async def create_graph(self, graph: graph_service_pb2.Graph) -> str:
        """Create and store a Graph definition"""
        if not graph.id:
            graph.id = str(uuid.uuid4())

        # Validate Graph structure
        await self._validate_graph(graph)

        # Store Graph
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

    async def get_graph(self, graph_id: str) -> graph_service_pb2.Graph:
        """Retrieve a Graph definition"""
        if graph_id not in self.graphs:
            raise ValueError(f"Graph not found: {graph_id}")

        return self.graphs[graph_id]

    async def list_graphs(self, pagination, filters, graph_type) -> list[graph_service_pb2.Graph]:
        """List all Graph definitions"""
        # Simple implementation - return all Graphs
        # TODO: Implement pagination and filtering
        graphs = list(self.graphs.values())

        # Filter by graph_type if specified
        if graph_type and graph_type != graph_service_pb2.GRAPH_TYPE_UNSPECIFIED:
            graphs = [g for g in graphs if g.graph_type == graph_type]

        return graphs

    async def delete_graph(self, graph_id: str):
        """Delete a Graph definition"""
        if graph_id not in self.graphs:
            raise ValueError(f"Graph not found: {graph_id}")

        # Check for running executions
        running_executions = [
            exec_id
            for exec_id, exec_data in self.executions.items()
            if exec_data.get("graph_id") == graph_id and exec_data.get("status") == "RUNNING"
        ]

        if running_executions:
            raise ValueError(f"Cannot delete Graph with running executions: {running_executions}")

        del self.graphs[graph_id]
        events.info("Graph deleted", {"graph_id": graph_id})

    async def execute_graph(self, graph_id: str, input_data, execution_id: str | None = None) -> str:
        """Start Graph execution"""
        if graph_id not in self.graphs:
            raise ValueError(f"Graph not found: {graph_id}")

        if not execution_id:
            execution_id = str(uuid.uuid4())

        graph = self.graphs[graph_id]

        # Initialize execution state
        execution_state = {
            "execution_id": execution_id,
            "graph_id": graph_id,
            "status": "RUNNING",
            "started_at": datetime.utcnow().isoformat(),
            "input_data": input_data,
            "node_states": {},
            "events": [],
        }

        self.executions[execution_id] = execution_state

        # Start execution in background
        asyncio.create_task(self._execute_graph_async(graph, execution_state))

        events.info(
            "Graph execution initiated",
            {"graph_id": graph_id, "execution_id": execution_id},
        )

        return execution_id

    async def _execute_graph_async(self, graph: graph_service_pb2.Graph, execution_state: dict):
        """Execute Graph asynchronously"""
        try:
            execution_id = execution_state["execution_id"]

            # Add execution started event
            await self._add_execution_event(execution_state, "EXECUTION_STARTED", None, {})

            # Build execution graph
            node_map = {node.id: node for node in graph.nodes}
            edge_map = self._build_edge_map(graph.edges)

            # Execute nodes in topological order
            executed_nodes = set()

            while len(executed_nodes) < len(graph.nodes):
                # Find nodes ready to execute (all dependencies satisfied)
                ready_nodes = []
                for node in graph.nodes:
                    if node.id not in executed_nodes:
                        dependencies = edge_map.get(node.id, [])
                        if all(dep in executed_nodes for dep in dependencies):
                            ready_nodes.append(node)

                if not ready_nodes:
                    raise RuntimeError("Circular dependency detected or no ready nodes")

                # Execute ready nodes in parallel
                tasks = []
                for node in ready_nodes:
                    task = self._execute_node(node, execution_state, node_map)
                    tasks.append(task)

                # Wait for all nodes to complete
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Check for failures
                for i, result in enumerate(results):
                    node = ready_nodes[i]
                    if isinstance(result, Exception):
                        await self._handle_node_failure(node, execution_state, result)
                        return
                    else:
                        executed_nodes.add(node.id)

            # Mark execution as completed
            execution_state["status"] = "COMPLETED"
            execution_state["completed_at"] = datetime.utcnow().isoformat()
            await self._add_execution_event(execution_state, "EXECUTION_COMPLETED", None, {})

            events.info("Graph execution completed", {"execution_id": execution_id})

        except Exception as e:
            execution_state["status"] = "FAILED"
            execution_state["error_message"] = str(e)
            execution_state["completed_at"] = datetime.utcnow().isoformat()
            await self._add_execution_event(execution_state, "EXECUTION_FAILED", None, {"error": str(e)})

            events.error(
                "Graph execution failed",
                exception=e,
                metadata={"execution_id": execution_state["execution_id"]},
            )

    async def _execute_node(self, node: graph_service_pb2.Node, execution_state: dict, node_map: dict):
        """Execute a single node"""
        node_id = node.id

        try:
            # Add node started event
            await self._add_execution_event(execution_state, "NODE_STARTED", node_id, {})

            # Get node executor
            executor = self.node_factory.get_executor(node.type)

            # Collect input data from previous nodes
            input_data = await self._collect_node_inputs(node, execution_state, node_map)

            # Execute node
            output_data = await executor.execute(node, input_data)

            # Store node result
            execution_state["node_states"][node_id] = {
                "status": "COMPLETED",
                "started_at": datetime.utcnow().isoformat(),
                "completed_at": datetime.utcnow().isoformat(),
                "output_data": output_data,
            }

            # Add node completed event
            await self._add_execution_event(execution_state, "NODE_COMPLETED", node_id, output_data)

            events.info(
                "Node executed successfully",
                {
                    "node_id": node_id,
                    "node_type": node.type,
                    "execution_id": execution_state["execution_id"],
                },
            )

        except Exception as e:
            execution_state["node_states"][node_id] = {
                "status": "FAILED",
                "started_at": datetime.utcnow().isoformat(),
                "completed_at": datetime.utcnow().isoformat(),
                "error_message": str(e),
            }

            await self._add_execution_event(execution_state, "NODE_FAILED", node_id, {"error": str(e)})
            raise e

    async def _collect_node_inputs(self, node: graph_service_pb2.Node, execution_state: dict, node_map: dict) -> dict:
        """Collect input data for a node from its dependencies"""
        # Simple implementation - return execution input data for now
        # TODO: Implement proper edge-based data flow
        return execution_state.get("input_data", {})

    def _build_edge_map(self, edges) -> dict[str, list[str]]:
        """Build a map of node dependencies from edges"""
        edge_map = {}
        for edge in edges:
            target = edge.target_node_id
            source = edge.source_node_id

            if target not in edge_map:
                edge_map[target] = []
            edge_map[target].append(source)

        return edge_map

    async def _add_execution_event(
        self,
        execution_state: dict,
        event_type: str,
        node_id: str | None,
        event_data: dict,
    ):
        """Add an event to the execution log"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "node_id": node_id or "",
            "event_data": event_data,
        }
        execution_state["events"].append(event)

    async def _handle_node_failure(self, node: graph_service_pb2.Node, execution_state: dict, error: Exception):
        """Handle node execution failure"""
        execution_state["status"] = "FAILED"
        execution_state["error_message"] = f"Node {node.id} failed: {str(error)}"
        execution_state["completed_at"] = datetime.utcnow().isoformat()

        await self._add_execution_event(
            execution_state,
            "EXECUTION_FAILED",
            None,
            {"failed_node": node.id, "error": str(error)},
        )

    async def _validate_graph(self, graph: graph_service_pb2.Graph):
        """Validate Graph structure based on graph_type"""
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
        if graph.graph_type == graph_service_pb2.DAG:
            # DAG validation: detect cycles
            if self._has_cycle(graph.nodes, graph.edges):
                raise ValueError("DAG graph type does not allow cycles")
        elif graph.graph_type == graph_service_pb2.TREE:
            # Tree validation: each node (except root) has exactly one parent
            if not self._is_tree(graph.nodes, graph.edges):
                raise ValueError("TREE graph type requires strict tree structure")
        # CYCLIC, CYCLIC_WITH_BREAKERS, UNRESTRICTED: no additional validation needed

    def _has_cycle(self, nodes, edges) -> bool:
        """Detect cycles in graph using DFS"""
        # Build adjacency list
        adj = {node.id: [] for node in nodes}
        for edge in edges:
            adj[edge.source_node_id].append(edge.target_node_id)

        visited = set()
        rec_stack = set()

        def dfs(node_id):
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

        for node in nodes:
            if node.id not in visited:
                if dfs(node.id):
                    return True

        return False

    def _is_tree(self, nodes, edges) -> bool:
        """Check if graph is a valid tree structure"""
        if not nodes:
            return True

        # Count incoming edges for each node
        incoming_count = {node.id: 0 for node in nodes}
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

    async def stream_execution(self, execution_id: str) -> AsyncGenerator[graph_service_pb2.ExecutionEvent, None]:
        """Stream execution events"""
        if execution_id not in self.executions:
            raise ValueError(f"Execution not found: {execution_id}")

        execution_state = self.executions[execution_id]
        last_event_index = 0

        while execution_state.get("status") in ["RUNNING", "PENDING"]:
            events_list = execution_state.get("events", [])

            # Yield new events
            for i in range(last_event_index, len(events_list)):
                event_data = events_list[i]

                event = graph_service_pb2.ExecutionEvent()
                event.execution_id = execution_id

                # Convert timestamp
                timestamp = timestamp_pb2.Timestamp()
                timestamp.FromDatetime(datetime.fromisoformat(event_data["timestamp"]))
                event.timestamp.CopyFrom(timestamp)

                # Set event type
                event_type_map = {
                    "EXECUTION_STARTED": graph_service_pb2.EXECUTION_STARTED,
                    "NODE_STARTED": graph_service_pb2.NODE_STARTED,
                    "NODE_COMPLETED": graph_service_pb2.NODE_COMPLETED,
                    "NODE_FAILED": graph_service_pb2.NODE_FAILED,
                    "EXECUTION_COMPLETED": graph_service_pb2.EXECUTION_COMPLETED,
                    "EXECUTION_FAILED": graph_service_pb2.EXECUTION_FAILED,
                    "EXECUTION_CANCELLED": graph_service_pb2.EXECUTION_CANCELLED,
                }
                event.event_type = event_type_map.get(event_data["event_type"], 0)
                event.node_id = event_data.get("node_id", "")

                # Convert event data to Struct
                if event_data.get("event_data"):
                    struct_data = struct_pb2.Struct()
                    struct_data.update(event_data["event_data"])
                    event.event_data.CopyFrom(struct_data)

                yield event

            last_event_index = len(events_list)
            await asyncio.sleep(0.1)  # Small delay to avoid busy waiting

        # Yield final events if execution completed
        events_list = execution_state.get("events", [])
        for i in range(last_event_index, len(events_list)):
            event_data = events_list[i]
            # ... (same event creation logic as above)

    async def get_execution(self, execution_id: str) -> graph_service_pb2.GetExecutionResponse:
        """Get execution status and results"""
        if execution_id not in self.executions:
            raise ValueError(f"Execution not found: {execution_id}")

        execution_state = self.executions[execution_id]

        response = graph_service_pb2.GetExecutionResponse()
        response.execution_id = execution_id
        response.graph_id = execution_state["graph_id"]

        # Map status
        status_map = {
            "PENDING": graph_service_pb2.PENDING,
            "RUNNING": graph_service_pb2.RUNNING,
            "COMPLETED": graph_service_pb2.COMPLETED,
            "FAILED": graph_service_pb2.FAILED,
            "CANCELLED": graph_service_pb2.CANCELLED,
        }
        response.status = status_map.get(execution_state["status"], graph_service_pb2.EXECUTION_STATUS_UNSPECIFIED)

        # Set timestamps
        if execution_state.get("started_at"):
            started_at = timestamp_pb2.Timestamp()
            started_at.FromDatetime(datetime.fromisoformat(execution_state["started_at"]))
            response.started_at.CopyFrom(started_at)

        if execution_state.get("completed_at"):
            completed_at = timestamp_pb2.Timestamp()
            completed_at.FromDatetime(datetime.fromisoformat(execution_state["completed_at"]))
            response.completed_at.CopyFrom(completed_at)

        # Set error message if failed
        if execution_state.get("error_message"):
            response.error_message = execution_state["error_message"]

        return response

    async def cancel_execution(self, execution_id: str):
        """Cancel a running execution"""
        if execution_id not in self.executions:
            raise ValueError(f"Execution not found: {execution_id}")

        execution_state = self.executions[execution_id]

        if execution_state["status"] not in ["RUNNING", "PENDING"]:
            raise ValueError(f"Cannot cancel execution in status: {execution_state['status']}")

        execution_state["status"] = "CANCELLED"
        execution_state["completed_at"] = datetime.utcnow().isoformat()

        await self._add_execution_event(execution_state, "EXECUTION_CANCELLED", None, {})

        events.info("Execution cancelled", {"execution_id": execution_id})
