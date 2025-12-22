"""GraphCanvas - Renders a full graph through a viewport.

The canvas is responsible for:
- Drawing all visible nodes and edges
- Transforming world coordinates to screen coordinates via viewport
- Visual styling (selection, highlighting, animations)

Pattern: Stateless rendering functions that take graph, layout, viewport, and renderer.
This keeps rendering pure and testable.
"""

from dataclasses import dataclass

from libs.python.models.graph.schema import Graph, Node
from libs.python.terminal.cell import Color, Style
from libs.python.terminal.renderer import Renderer
from libs.python.terminal.unhinged.graph_layout import GraphLayout
from libs.python.terminal.unhinged.viewport import Viewport

# =============================================================================
# Style Configuration
# =============================================================================


@dataclass(frozen=True)
class GraphStyle:
    """Visual style configuration for graph rendering."""

    node_fg: Color = Color.WHITE
    node_bg: Color = Color.BLACK
    node_border: Color = Color.BLUE
    selected_fg: Color = Color.BLACK
    selected_bg: Color = Color.CYAN
    edge_color: Color = Color.YELLOW
    edge_arrow: Color = Color.BRIGHT_YELLOW


DEFAULT_STYLE = GraphStyle()


# =============================================================================
# Edge Rendering
# =============================================================================


def _draw_edge_line(
    r: Renderer,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    viewport: Viewport,
    style: Style,
) -> None:
    """Draw a line between two screen positions."""
    # Simple line drawing - horizontal then vertical
    dx = x2 - x1
    dy = y2 - y1

    # Draw horizontal segment
    if dx != 0:
        step = 1 if dx > 0 else -1
        for x in range(x1, x1 + dx, step):
            if 0 <= x < viewport.width and 0 <= y1 < viewport.height:
                r.char(x, y1, "─", style)

    # Draw vertical segment
    if dy != 0:
        step = 1 if dy > 0 else -1
        mid_x = x1 + dx
        for y in range(y1, y1 + dy + step, step):
            if 0 <= mid_x < viewport.width and 0 <= y < viewport.height:
                char = "│"
                # Corner at junction
                if y == y1 and dx != 0:
                    char = "┐" if dx > 0 else "┌"
                # Arrow at end
                elif y == y2:
                    char = "▼" if dy > 0 else "▲"
                r.char(mid_x, y, char, style)


def render_edges(
    graph: Graph,
    layout: GraphLayout,
    viewport: Viewport,
    r: Renderer,
    style: GraphStyle = DEFAULT_STYLE,
    highlighted_edges: set[str] | None = None,
    offset_x: int = 0,
    offset_y: int = 0,
) -> None:
    """Render all visible edges."""
    edge_style = Style(fg=style.edge_color)

    for edge in graph.edges:
        src_pos = layout.get_position(edge.source_node_id)
        tgt_pos = layout.get_position(edge.target_node_id)
        if not src_pos or not tgt_pos:
            continue

        # Convert to screen coords
        sx1, sy1 = viewport.world_to_screen(src_pos[0], src_pos[1])
        sx2, sy2 = viewport.world_to_screen(tgt_pos[0], tgt_pos[1])

        # Skip if completely off screen
        if not (
            viewport.is_visible(src_pos[0], src_pos[1], margin=2)
            or viewport.is_visible(tgt_pos[0], tgt_pos[1], margin=2)
        ):
            continue

        # Offset to connect from bottom of source to top of target
        _draw_edge_line(r, sx1 + offset_x, sy1 + 1 + offset_y, sx2 + offset_x, sy2 - 1 + offset_y, viewport, edge_style)


# =============================================================================
# Node Rendering
# =============================================================================


def render_node(
    node: Node,
    x: int,
    y: int,
    r: Renderer,
    selected: bool = False,
    style: GraphStyle = DEFAULT_STYLE,
) -> None:
    """Render a single node at screen position.

    Draws a simple text box with node name. No sprites.
    """
    label = node.name[:14]
    box_w = len(label) + 2
    box_x = x - box_w // 2

    # Node style
    border_style = Style(
        fg=style.selected_fg if selected else style.node_border,
        bg=style.selected_bg if selected else None,
    )
    label_style = Style(
        fg=style.selected_fg if selected else style.node_fg,
        bg=style.selected_bg if selected else None,
    )

    # Draw simple box: [NodeName]
    r.char(box_x, y, "[", border_style)
    r.text(box_x + 1, y, label, label_style)
    r.char(box_x + 1 + len(label), y, "]", border_style)


def render_nodes(
    graph: Graph,
    layout: GraphLayout,
    viewport: Viewport,
    r: Renderer,
    selected_node_id: str | None = None,
    style: GraphStyle = DEFAULT_STYLE,
    offset_x: int = 0,
    offset_y: int = 0,
) -> None:
    """Render all visible nodes."""
    for node in graph.nodes:
        pos = layout.get_position(node.id)
        if not pos:
            continue

        # Check visibility
        if not viewport.is_visible(pos[0], pos[1], margin=10):
            continue

        # Convert to screen
        sx, sy = viewport.world_to_screen(pos[0], pos[1])
        is_selected = node.id == selected_node_id
        render_node(node, sx + offset_x, sy + offset_y, r, selected=is_selected, style=style)


# =============================================================================
# Main Canvas Render Function
# =============================================================================


def render_graph_canvas(
    graph: Graph,
    layout: GraphLayout,
    viewport: Viewport,
    r: Renderer,
    selected_node_id: str | None = None,
    style: GraphStyle = DEFAULT_STYLE,
    offset_x: int = 0,
    offset_y: int = 0,
) -> None:
    """Render the complete graph canvas.

    This is the main entry point for graph rendering.
    Draws edges first (so nodes appear on top), then nodes.

    Args:
        graph: The graph to render.
        layout: Precalculated node positions.
        viewport: Camera/viewport defining visible area.
        r: Renderer to draw to.
        selected_node_id: ID of currently selected node (highlighted).
        style: Visual style configuration.
        offset_x: Screen X offset for all drawing.
        offset_y: Screen Y offset for all drawing.
    """
    # Draw edges first (underneath nodes)
    render_edges(graph, layout, viewport, r, style, offset_x=offset_x, offset_y=offset_y)

    # Draw nodes on top
    render_nodes(graph, layout, viewport, r, selected_node_id, style, offset_x=offset_x, offset_y=offset_y)


def render_minimap(
    layout: GraphLayout,
    viewport: Viewport,
    r: Renderer,
    x: int,
    y: int,
    width: int,
    height: int,
) -> None:
    """Render a minimap showing viewport position in the graph.

    Draws a small overview of the entire graph with a rectangle
    showing the current viewport position.
    """
    # Draw minimap border
    border_style = Style(fg=Color.BRIGHT_BLACK)
    r.text(x, y, "┌" + "─" * (width - 2) + "┐", border_style)
    for row in range(1, height - 1):
        r.text(x, y + row, "│" + " " * (width - 2) + "│", border_style)
    r.text(x, y + height - 1, "└" + "─" * (width - 2) + "┘", border_style)

    # Calculate scale
    if layout.width == 0 or layout.height == 0:
        return

    inner_w = width - 2
    inner_h = height - 2
    scale_x = inner_w / layout.width if layout.width > 0 else 1
    scale_y = inner_h / layout.height if layout.height > 0 else 1
    scale = min(scale_x, scale_y)

    # Draw viewport rectangle
    vp_x = int((viewport.world_x - layout.bounds[0]) * scale)
    vp_y = int((viewport.world_y - layout.bounds[1]) * scale)
    vp_w = max(1, int(viewport.width * scale))
    vp_h = max(1, int(viewport.height * scale))

    vp_style = Style(fg=Color.CYAN)
    # Clamp to minimap bounds
    vp_x = max(0, min(vp_x, inner_w - 1))
    vp_y = max(0, min(vp_y, inner_h - 1))

    # Draw viewport indicator
    for dy in range(min(vp_h, inner_h - vp_y)):
        for dx in range(min(vp_w, inner_w - vp_x)):
            r.char(x + 1 + vp_x + dx, y + 1 + vp_y + dy, "░", vp_style)
