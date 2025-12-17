"""Graph tree visualization.

Displays graph nodes and edges in a hierarchical tree view.
Used by graph view command.
"""

from typing import Any

from rich.tree import Tree

from cli.tui.console import console


def _truncate(value: str, max_len: int = 60) -> str:
    """Truncate string if too long."""
    if len(value) > max_len:
        return value[: max_len - 3] + "..."
    return value


def _add_node_config(node_branch: Tree, node: dict[str, Any]) -> None:
    """Add config details under a node branch."""
    for key, value in node.items():
        if key not in ("id", "type"):
            val_str = _truncate(str(value))
            node_branch.add(f"[dim]{key}:[/dim] {val_str}")


def _add_nodes_branch(tree: Tree, nodes: list[dict], show_config: bool) -> None:
    """Add nodes branch to tree."""
    if not nodes:
        return
    nodes_branch = tree.add("[cyan]Nodes[/cyan]")
    for node in nodes:
        node_id = node.get("id", "?")
        node_type = node.get("type", "unknown")
        label = f"[bold]{node_id}[/bold] ({node_type})"
        if show_config:
            node_branch = nodes_branch.add(label)
            _add_node_config(node_branch, node)
        else:
            nodes_branch.add(label)


def _add_edges_branch(tree: Tree, edges: list[dict]) -> None:
    """Add edges branch to tree."""
    if not edges:
        return
    edges_branch = tree.add("[magenta]Edges[/magenta]")
    for edge in edges:
        source = edge.get("source", "?")
        target = edge.get("target", "?")
        condition = edge.get("condition")
        label = f"{source} → {target}"
        if condition:
            label += f" [dim][{condition}][/dim]"
        edges_branch.add(label)


def _add_tags_branch(tree: Tree, tags: list[str]) -> None:
    """Add tags branch to tree."""
    if not tags:
        return
    tags_branch = tree.add("[yellow]Tags[/yellow]")
    for tag in tags:
        tags_branch.add(f"#{tag}")


def graph_tree(
    graph_data: dict[str, Any],
    *,
    show_config: bool = False,
) -> None:
    """Display a graph as a Rich Tree.

    Args:
        graph_data: Graph definition dict with 'nodes' and 'edges'.
        show_config: Whether to show node configuration details.
    """
    name = graph_data.get("name", "Graph")
    description = graph_data.get("description", "")

    root_label = f"[bold]{name}[/bold]"
    if description:
        root_label += f" - [dim]{description}[/dim]"

    tree = Tree(root_label)

    _add_nodes_branch(tree, graph_data.get("nodes", []), show_config)
    _add_edges_branch(tree, graph_data.get("edges", []))
    _add_tags_branch(tree, graph_data.get("tags", []))

    console.print()
    console.print(tree)
    console.print()
