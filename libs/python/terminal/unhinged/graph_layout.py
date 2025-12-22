"""Graph layout algorithms for positioning nodes in 2D space.

Calculates world coordinates for all nodes in a graph.
Different algorithms can be used depending on graph type.

Pattern: Pure functions that take a Graph and return a GraphLayout.
Layouts are immutable and can be cached.
"""

from dataclasses import dataclass

from libs.python.models.graph.schema import Graph


@dataclass(frozen=True)
class GraphLayout:
    """Immutable layout result with node positions.

    Attributes:
        positions: Dict mapping node_id -> (x, y) in world coordinates.
        bounds: Tuple of (min_x, min_y, max_x, max_y) bounding box.
    """

    positions: dict[str, tuple[float, float]]
    bounds: tuple[float, float, float, float]  # min_x, min_y, max_x, max_y

    @property
    def width(self) -> float:
        return self.bounds[2] - self.bounds[0]

    @property
    def height(self) -> float:
        return self.bounds[3] - self.bounds[1]

    @property
    def center(self) -> tuple[float, float]:
        return (
            (self.bounds[0] + self.bounds[2]) / 2,
            (self.bounds[1] + self.bounds[3]) / 2,
        )

    def get_position(self, node_id: str) -> tuple[float, float] | None:
        """Get position of a node, or None if not in layout."""
        return self.positions.get(node_id)


def calculate_hierarchical_layout(
    graph: Graph,
    node_width: int = 20,
    node_height: int = 4,
    h_spacing: int = 8,
    v_spacing: int = 6,
) -> GraphLayout:
    """Calculate hierarchical/layered layout for DAGs.

    Nodes are arranged in layers based on their depth from root nodes.
    Best for directed acyclic graphs.
    """
    if not graph.nodes:
        return GraphLayout(positions={}, bounds=(0, 0, 0, 0))

    # Build adjacency maps
    node_map = {n.id: n for n in graph.nodes}
    children: dict[str, list[str]] = {n.id: [] for n in graph.nodes}
    parents: dict[str, list[str]] = {n.id: [] for n in graph.nodes}

    for edge in graph.edges:
        if edge.source_node_id in children and edge.target_node_id in parents:
            children[edge.source_node_id].append(edge.target_node_id)
            parents[edge.target_node_id].append(edge.source_node_id)

    # Find root nodes (no incoming edges)
    roots = [n.id for n in graph.nodes if not parents[n.id]]
    if not roots:
        # Cyclic graph - pick first node as root
        roots = [graph.nodes[0].id]

    # Assign layers via BFS
    layers: dict[str, int] = {}
    queue = [(r, 0) for r in roots]
    visited: set[str] = set()

    while queue:
        node_id, layer = queue.pop(0)
        if node_id in visited:
            layers[node_id] = max(layers.get(node_id, 0), layer)
            continue
        visited.add(node_id)
        layers[node_id] = layer
        for child_id in children[node_id]:
            queue.append((child_id, layer + 1))

    # Handle unvisited nodes (disconnected components)
    for node in graph.nodes:
        if node.id not in layers:
            layers[node.id] = 0

    # Group nodes by layer
    layer_nodes: dict[int, list[str]] = {}
    for node_id, layer in layers.items():
        layer_nodes.setdefault(layer, []).append(node_id)

    # Calculate positions
    positions: dict[str, tuple[float, float]] = {}
    max_layer = max(layers.values()) if layers else 0

    for layer_idx in range(max_layer + 1):
        nodes_in_layer = layer_nodes.get(layer_idx, [])
        layer_width = len(nodes_in_layer) * (node_width + h_spacing) - h_spacing
        start_x = -layer_width / 2

        for i, node_id in enumerate(nodes_in_layer):
            x = start_x + i * (node_width + h_spacing) + node_width / 2
            y = layer_idx * (node_height + v_spacing)
            positions[node_id] = (x, y)

    # Calculate bounds
    if positions:
        xs = [p[0] for p in positions.values()]
        ys = [p[1] for p in positions.values()]
        padding = max(node_width, node_height)
        bounds = (
            min(xs) - padding,
            min(ys) - padding,
            max(xs) + padding,
            max(ys) + padding,
        )
    else:
        bounds = (0, 0, 0, 0)

    return GraphLayout(positions=positions, bounds=bounds)


def calculate_grid_layout(
    graph: Graph,
    node_width: int = 20,
    node_height: int = 4,
    columns: int = 4,
    h_spacing: int = 6,
    v_spacing: int = 4,
) -> GraphLayout:
    """Calculate simple grid layout.

    Nodes arranged in a grid, good for unstructured graphs.
    """
    if not graph.nodes:
        return GraphLayout(positions={}, bounds=(0, 0, 0, 0))

    positions: dict[str, tuple[float, float]] = {}

    for i, node in enumerate(graph.nodes):
        col = i % columns
        row = i // columns
        x = col * (node_width + h_spacing)
        y = row * (node_height + v_spacing)
        positions[node.id] = (x, y)

    # Calculate bounds
    xs = [p[0] for p in positions.values()]
    ys = [p[1] for p in positions.values()]
    bounds = (
        min(xs) - node_width // 2,
        min(ys) - node_height // 2,
        max(xs) + node_width,
        max(ys) + node_height,
    )

    return GraphLayout(positions=positions, bounds=bounds)
