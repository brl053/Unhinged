"""Graph actions - Action types and reducer for graph mutations.

Implements the Action/Reducer pattern with Command history for undo/redo.
Uses canonical types from libs/python/models/graph/schema.py.
"""

from dataclasses import dataclass, field, replace
from typing import Any

from libs.python.terminal.unhinged.graph_types import (
    Graph,
    NodeType,
    create_edge,
    create_node,
    node_x,
    node_y,
)

# =============================================================================
# Action Types
# =============================================================================


@dataclass(frozen=True)
class GraphAction:
    """Base class for all graph actions."""

    pass


@dataclass(frozen=True)
class AddNode(GraphAction):
    """Add a new node to the graph."""

    node_type: NodeType
    name: str
    x: int = 0
    y: int = 0
    config: tuple[tuple[str, Any], ...] = ()  # Frozen dict alternative

    # Set after execution to enable undo
    created_node_id: str | None = None


@dataclass(frozen=True)
class DeleteNode(GraphAction):
    """Delete a node and its connected edges."""

    node_id: str


@dataclass(frozen=True)
class UpdateNode(GraphAction):
    """Update a node's properties."""

    node_id: str
    name: str | None = None
    config_updates: tuple[tuple[str, Any], ...] | None = None


@dataclass(frozen=True)
class AddEdge(GraphAction):
    """Add an edge between two nodes."""

    source_node_id: str
    target_node_id: str
    source_output: str = "out"
    target_input: str = "in"

    created_edge_id: str | None = None


@dataclass(frozen=True)
class DeleteEdge(GraphAction):
    """Delete an edge."""

    edge_id: str


@dataclass(frozen=True)
class UpdateEdge(GraphAction):
    """Update an edge's properties."""

    edge_id: str
    source_output: str | None = None
    target_input: str | None = None


@dataclass(frozen=True)
class WrapInSubgraph(GraphAction):
    """Wrap selected nodes in a subgraph."""

    node_ids: tuple[str, ...]
    subgraph_name: str = "Subgraph"


@dataclass(frozen=True)
class SetParallel(GraphAction):
    """Mark nodes to run in parallel."""

    node_ids: tuple[str, ...]
    join_strategy: str = "all"  # "all", "any", "n_of_m"


@dataclass(frozen=True)
class UpdateGraph(GraphAction):
    """Update graph-level properties."""

    name: str | None = None
    description: str | None = None
    metadata_updates: tuple[tuple[str, Any], ...] | None = None


# =============================================================================
# Reducer
# =============================================================================


def graph_reducer(graph: Graph, action: GraphAction) -> Graph:
    """Apply an action to a graph, returning a new graph state."""
    match action:
        case AddNode(node_type, name, x, y, config, _):
            return _add_node(graph, node_type, name, x, y, dict(config))

        case DeleteNode(node_id):
            return _delete_node(graph, node_id)

        case UpdateNode(node_id, name, config_updates):
            return _update_node(graph, node_id, name, config_updates)

        case AddEdge(source_node_id, target_node_id, source_output, target_input, _):
            return _add_edge(graph, source_node_id, target_node_id, source_output, target_input)

        case DeleteEdge(edge_id):
            return _delete_edge(graph, edge_id)

        case UpdateEdge(edge_id, source_output, target_input):
            return _update_edge(graph, edge_id, source_output, target_input)

        case WrapInSubgraph(node_ids, subgraph_name):
            return _wrap_in_subgraph(graph, node_ids, subgraph_name)

        case UpdateGraph(name, description, metadata_updates):
            return _update_graph(graph, name, description, metadata_updates)

        case _:
            return graph


def _add_node(
    graph: Graph,
    node_type: NodeType,
    name: str,
    x: int,
    y: int,
    config: dict,
) -> Graph:
    """Add a node to the graph."""
    node = create_node(node_type=node_type, name=name, x=x, y=y, **config)
    return replace(graph, nodes=[*graph.nodes, node])


def _delete_node(graph: Graph, node_id: str) -> Graph:
    """Delete a node and its connected edges."""
    nodes = [n for n in graph.nodes if n.id != node_id]
    edges = [e for e in graph.edges if e.source_node_id != node_id and e.target_node_id != node_id]
    return replace(graph, nodes=nodes, edges=edges)


def _update_node(
    graph: Graph,
    node_id: str,
    name: str | None,
    config_updates: tuple | None,
) -> Graph:
    """Update a node's properties."""
    nodes = []
    for node in graph.nodes:
        if node.id == node_id:
            new_name = name if name is not None else node.name
            new_config = node.config.copy()
            if config_updates is not None:
                new_config.update(dict(config_updates))
            nodes.append(replace(node, name=new_name, config=new_config))
        else:
            nodes.append(node)
    return replace(graph, nodes=nodes)


def _add_edge(
    graph: Graph,
    source_node_id: str,
    target_node_id: str,
    source_output: str,
    target_input: str,
) -> Graph:
    """Add an edge to the graph."""
    edge = create_edge(source_node_id, target_node_id, source_output=source_output, target_input=target_input)
    return replace(graph, edges=[*graph.edges, edge])


def _delete_edge(graph: Graph, edge_id: str) -> Graph:
    """Delete an edge."""
    edges = [e for e in graph.edges if e.id != edge_id]
    return replace(graph, edges=edges)


def _update_edge(
    graph: Graph,
    edge_id: str,
    source_output: str | None,
    target_input: str | None,
) -> Graph:
    """Update an edge's properties."""
    edges = []
    for edge in graph.edges:
        if edge.id == edge_id:
            new_source = source_output if source_output is not None else edge.source_output
            new_target = target_input if target_input is not None else edge.target_input
            edges.append(replace(edge, source_output=new_source, target_input=new_target))
        else:
            edges.append(edge)
    return replace(graph, edges=edges)


def _wrap_in_subgraph(
    graph: Graph,
    node_ids: tuple[str, ...],
    subgraph_name: str,
) -> Graph:
    """Wrap nodes in a subgraph node."""
    # Extract nodes to wrap
    wrapped_nodes = [n for n in graph.nodes if n.id in node_ids]
    remaining_nodes = [n for n in graph.nodes if n.id not in node_ids]

    # Extract internal edges (between wrapped nodes)
    internal_edges = [e for e in graph.edges if e.source_node_id in node_ids and e.target_node_id in node_ids]
    external_edges = [e for e in graph.edges if e.source_node_id not in node_ids or e.target_node_id not in node_ids]

    # Create subgraph node with children stored in config
    subgraph_node = create_node(
        node_type=NodeType.SUBGRAPH,
        name=subgraph_name,
        x=node_x(wrapped_nodes[0]) if wrapped_nodes else 0,
        y=node_y(wrapped_nodes[0]) if wrapped_nodes else 0,
        children=[n.id for n in wrapped_nodes],
        child_edges=[e.id for e in internal_edges],
    )

    # TODO: Rewire external edges to subgraph ports

    return replace(
        graph,
        nodes=[*remaining_nodes, subgraph_node],
        edges=external_edges,
    )


def _update_graph(
    graph: Graph,
    name: str | None,
    description: str | None,
    metadata_updates: tuple | None,
) -> Graph:
    """Update graph-level properties."""
    new_name = name if name is not None else graph.name
    new_desc = description if description is not None else graph.description
    new_metadata = graph.metadata.copy()
    if metadata_updates is not None:
        new_metadata.update(dict(metadata_updates))
    return replace(graph, name=new_name, description=new_desc, metadata=new_metadata)


# =============================================================================
# Command History (Undo/Redo)
# =============================================================================


@dataclass
class Command:
    """A command with its action and the state before execution (for undo)."""

    action: GraphAction
    state_before: Graph | None = None


@dataclass
class CommandHistory:
    """Manages undo/redo stacks for graph operations."""

    undo_stack: list[Command] = field(default_factory=list)
    redo_stack: list[Command] = field(default_factory=list)
    max_history: int = 50

    def execute(self, action: GraphAction, graph: Graph) -> Graph:
        """Execute an action and add to undo stack."""
        command = Command(action=action, state_before=graph)
        new_graph = graph_reducer(graph, action)

        self.undo_stack.append(command)
        if len(self.undo_stack) > self.max_history:
            self.undo_stack.pop(0)

        # Clear redo stack on new action
        self.redo_stack.clear()

        return new_graph

    def undo(self, graph: Graph) -> Graph:
        """Undo the last action."""
        if not self.undo_stack:
            return graph

        command = self.undo_stack.pop()
        self.redo_stack.append(Command(action=command.action, state_before=graph))

        return command.state_before or graph

    def redo(self, graph: Graph) -> Graph:
        """Redo the last undone action."""
        if not self.redo_stack:
            return graph

        command = self.redo_stack.pop()
        self.undo_stack.append(Command(action=command.action, state_before=graph))

        return graph_reducer(graph, command.action)

    @property
    def can_undo(self) -> bool:
        """Check if undo is available."""
        return len(self.undo_stack) > 0

    @property
    def can_redo(self) -> bool:
        """Check if redo is available."""
        return len(self.redo_stack) > 0
