"""Graph DAG visual renderer.

Renders graph nodes and edges as a visual DAG layout with boxes and arrows.
Used for graph visualization in the widget corral.

Layout algorithm:
1. Topological sort to assign layers (depth)
2. Nodes at same depth = same row
3. Box drawing for nodes, arrows for edges
"""

from typing import Any

from rich.console import Group, RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from cli.tui.console import console


def _compute_layers(nodes: list[dict], edges: list[dict]) -> dict[str, int]:
    """Compute layer (depth) for each node using topological sort.

    Nodes with no incoming edges start at layer 0.
    Each subsequent layer contains nodes whose predecessors are all placed.
    """
    # Build adjacency and in-degree
    node_ids = {n["id"] for n in nodes}
    incoming: dict[str, set[str]] = {nid: set() for nid in node_ids}
    outgoing: dict[str, set[str]] = {nid: set() for nid in node_ids}

    for edge in edges:
        src, tgt = edge.get("source"), edge.get("target")
        if src is not None and tgt is not None and src in node_ids and tgt in node_ids:
            incoming[tgt].add(src)
            outgoing[src].add(tgt)

    # Assign layers - BFS from roots
    layers: dict[str, int] = {}
    # Start with nodes that have no incoming edges
    current_layer = [nid for nid in node_ids if not incoming[nid]]
    layer_num = 0

    while current_layer:
        for nid in current_layer:
            layers[nid] = layer_num
        # Next layer: nodes whose all predecessors are assigned
        next_layer = []
        for nid in node_ids:
            if nid not in layers and all(pred in layers for pred in incoming[nid]):
                next_layer.append(nid)
        current_layer = next_layer
        layer_num += 1

    # Handle cycles or disconnected nodes - assign to last layer
    for nid in node_ids:
        if nid not in layers:
            layers[nid] = layer_num

    return layers


def _group_by_layer(nodes: list[dict], layers: dict[str, int]) -> list[list[dict]]:
    """Group nodes by their layer."""
    if not layers:
        return [nodes] if nodes else []

    max_layer = max(layers.values()) if layers else 0
    grouped: list[list[dict]] = [[] for _ in range(max_layer + 1)]

    for node in nodes:
        layer = layers.get(node["id"], 0)
        grouped[layer].append(node)

    return grouped


def _node_style(node_type: str) -> str:
    """Get style for node type."""
    styles = {
        "unix": "green",
        "llm": "magenta",
        "api": "cyan",
        "input": "yellow",
        "user_input": "yellow",
        "subgraph": "blue",
        "conditional": "red",
        "transform": "white",
    }
    return styles.get(node_type, "white")


def _render_node_box(node: dict, width: int = 12) -> Panel:
    """Render a single node as a Rich Panel."""
    node_id = node.get("id", "?")
    node_type = node.get("type", "?")
    style = _node_style(node_type)

    # Truncate ID if needed
    display_id = node_id[: width - 4] if len(node_id) > width - 4 else node_id

    content = Text()
    content.append(display_id, style=f"bold {style}")
    content.append(f"\n({node_type})", style="dim")

    return Panel(
        content,
        width=width,
        height=4,
        border_style=style,
        padding=(0, 1),
    )


def _render_layer_row(layer_nodes: list[dict], layer_num: int, max_nodes: int = 6) -> Table:
    """Render a single layer as a horizontal row of nodes."""
    table = Table.grid(padding=(0, 2))

    # Add columns for each node position
    for _ in range(min(len(layer_nodes), max_nodes)):
        table.add_column(justify="center")

    # Create row of node panels
    panels = []
    for node in layer_nodes[:max_nodes]:
        panels.append(_render_node_box(node))

    if panels:
        table.add_row(*panels)

    return table


def _render_arrows(from_count: int, to_count: int, width: int = 80) -> Text:
    """Render arrow lines between layers."""
    if from_count == 0 or to_count == 0:
        return Text("")

    # Simple centered arrow
    arrow_line = Text()
    padding = " " * (width // 2 - 2)
    arrow_line.append(padding)
    arrow_line.append("│\n", style="dim")
    arrow_line.append(padding)
    arrow_line.append("▼", style="dim")

    return arrow_line


def graph_dag(
    graph_data: dict[str, Any],
    *,
    show_edges: bool = True,
    compact: bool = False,
) -> None:
    """Render a graph as a visual DAG with boxes and arrows.

    Args:
        graph_data: Graph definition dict with 'nodes' and 'edges'.
        show_edges: Whether to show arrows between layers.
        compact: Use smaller node boxes.
    """
    name = graph_data.get("name", "Graph")
    description = graph_data.get("description", "")
    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])

    if not nodes:
        console.print("[warning]Empty graph[/warning]")
        return

    # Compute layout
    layers = _compute_layers(nodes, edges)
    grouped = _group_by_layer(nodes, layers)

    # Build render groups
    renderables: list[RenderableType] = []

    # Header
    header = Text()
    header.append(f"◆ {name}", style="bold cyan")
    if description:
        header.append(f" - {description}", style="dim")
    renderables.append(header)
    renderables.append(Text(""))

    # Render each layer
    for i, layer_nodes in enumerate(grouped):
        if layer_nodes:
            layer_table = _render_layer_row(layer_nodes, i)
            renderables.append(layer_table)

            # Add arrows to next layer if not last
            if show_edges and i < len(grouped) - 1 and grouped[i + 1]:
                arrows = _render_arrows(len(layer_nodes), len(grouped[i + 1]))
                renderables.append(arrows)

    # Edge summary
    if edges and show_edges:
        renderables.append(Text(""))
        edge_text = Text()
        edge_text.append("Edges: ", style="dim")
        edge_strs = []
        for e in edges[:5]:  # Show first 5
            src, tgt = e.get("source", "?"), e.get("target", "?")
            cond = e.get("condition")
            s = f"{src}→{tgt}"
            if cond:
                s += f"[{cond}]"
            edge_strs.append(s)
        edge_text.append(", ".join(edge_strs), style="dim")
        if len(edges) > 5:
            edge_text.append(f" (+{len(edges) - 5} more)", style="dim")
        renderables.append(edge_text)

    # Print
    console.print()
    console.print(Group(*renderables))
    console.print()


def graph_dag_panel(
    graph_data: dict[str, Any],
    *,
    width: int | None = None,
    title: str | None = None,
) -> Panel:
    """Return graph DAG as a Panel widget (for layout composition).

    Args:
        graph_data: Graph definition dict.
        width: Panel width (None for auto).
        title: Override panel title.

    Returns:
        Rich Panel containing the DAG visualization.
    """
    name = graph_data.get("name", "Graph")
    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])

    content: RenderableType
    if not nodes:
        content = Text("Empty graph", style="dim")
    else:
        layers = _compute_layers(nodes, edges)
        grouped = _group_by_layer(nodes, layers)

        # Build as Group of renderables (not pre-rendered text)
        render_items: list[RenderableType] = []
        for i, layer_nodes in enumerate(grouped):
            if layer_nodes:
                layer_table = _render_layer_row(layer_nodes, i, max_nodes=4)
                render_items.append(layer_table)
                if i < len(grouped) - 1 and grouped[i + 1]:
                    arrow = Text()
                    arrow.append("       │\n", style="dim")
                    arrow.append("       ▼", style="dim")
                    render_items.append(arrow)

        content = Group(*render_items)

    return Panel(
        content,
        title=title or f"[ {name} ]",
        border_style="blue",
        width=width,
    )
