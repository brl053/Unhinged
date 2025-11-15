"""
@llm-doc Graph Canvas Widget for Visual Graph Editing
@llm-version 1.0.0
@llm-date 2025-10-31

GraphCanvasWidget - Cairo-based infinite pan/zoom canvas for rendering and editing node-based graphs.

Features:
- Infinite pan/zoom canvas with Cairo rendering
- Node and edge rendering
- Drag-to-pan and scroll-to-zoom navigation
- Grid snapping and alignment
- Selection and interaction handling
- Real-time viewport state management

This component serves as the foundation for visual graph editing with support for:
- Multiple node types (STT, TTS, LLM, Vision, etc.)
- Connection rendering with bezier curves
- Node status indicators
- Keyboard and mouse interactions
"""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

import math
from dataclasses import dataclass
from typing import Any

import cairo
from gi.repository import GObject, Gtk


@dataclass
class Viewport:
    """Represents the current viewport state."""

    x: float = 0.0
    y: float = 0.0
    zoom: float = 1.0

    def pan(self, dx: float, dy: float):
        """Pan the viewport."""
        self.x += dx
        self.y += dy

    def zoom_at(self, factor: float, cx: float, cy: float):
        """Zoom at a specific point."""
        # Clamp zoom level
        new_zoom = max(0.1, min(4.0, self.zoom * factor))

        # Adjust pan to zoom at cursor position
        if new_zoom != self.zoom:
            self.x = cx - (cx - self.x) * (new_zoom / self.zoom)
            self.y = cy - (cy - self.y) * (new_zoom / self.zoom)
            self.zoom = new_zoom


class GraphCanvasWidget(Gtk.DrawingArea):
    """
    Cairo-based infinite pan/zoom canvas for rendering and editing node-based graphs.

    Provides the foundation for visual graph editing with support for:
    - Drag-to-pan and scroll-to-zoom navigation
    - Grid snapping and alignment
    - Node and edge rendering
    - Selection and interaction
    - Real-time viewport state management
    """

    __gtype_name__ = "GraphCanvasWidget"

    # GObject signals
    __gsignals__ = {
        "node-moved": (GObject.SignalFlags.RUN_FIRST, None, (str, float, float)),
        "edge-created": (GObject.SignalFlags.RUN_FIRST, None, (str, str, str, str)),
        "edge-deleted": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        "node-selected": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        "viewport-changed": (
            GObject.SignalFlags.RUN_FIRST,
            None,
            (float, float, float),
        ),
        "canvas-clicked": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    # GObject properties
    nodes = GObject.Property(type=object, nick="Nodes", blurb="Array of node objects")

    edges = GObject.Property(type=object, nick="Edges", blurb="Array of edge objects")

    grid_size = GObject.Property(
        type=int, default=20, nick="Grid Size", blurb="Grid cell size in pixels"
    )

    snap_to_grid = GObject.Property(
        type=bool,
        default=True,
        nick="Snap to Grid",
        blurb="Whether to snap node positions to grid",
    )

    show_grid = GObject.Property(
        type=bool,
        default=True,
        nick="Show Grid",
        blurb="Whether to display grid background",
    )

    readonly = GObject.Property(
        type=bool,
        default=False,
        nick="Read Only",
        blurb="When true, disables all editing interactions",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Initialize properties
        self.nodes = []
        self.edges = []
        self.grid_size = 20
        self.snap_to_grid = True
        self.show_grid = True
        self.readonly = False

        # Viewport state
        self.viewport = Viewport()

        # Interaction state
        self._selected_node = None
        self._dragging_node = None
        self._drag_start = None
        self._pan_start = None
        self._is_panning = False

        # Set up drawing area
        self.set_draw_func(self._on_draw)

        # Set up event handlers
        self._setup_event_handlers()

        # Set minimum size
        self.set_size_request(400, 300)

        # Add CSS class
        self.add_css_class("graph-canvas")

    def _setup_event_handlers(self):
        """Set up mouse and keyboard event handlers."""
        # Mouse events
        motion_controller = Gtk.EventControllerMotion.new()
        motion_controller.connect("motion", self._on_motion)
        self.add_controller(motion_controller)

        # Click events
        click_controller = Gtk.GestureClick.new()
        click_controller.connect("pressed", self._on_click_pressed)
        click_controller.connect("released", self._on_click_released)
        self.add_controller(click_controller)

        # Scroll events
        scroll_controller = Gtk.EventControllerScroll.new(Gtk.EventControllerScrollFlags.VERTICAL)
        scroll_controller.connect("scroll", self._on_scroll)
        self.add_controller(scroll_controller)

        # Drag events
        drag_controller = Gtk.GestureDrag.new()
        drag_controller.connect("drag-begin", self._on_drag_begin)
        drag_controller.connect("drag-update", self._on_drag_update)
        drag_controller.connect("drag-end", self._on_drag_end)
        self.add_controller(drag_controller)

    def _on_draw(self, area, context: cairo.Context, width: int, height: int):
        """Draw the canvas."""
        # Clear background
        context.set_source_rgb(0.95, 0.95, 0.95)
        context.paint()

        # Draw grid if enabled
        if self.show_grid:
            self._draw_grid(context, width, height)

        # Draw edges
        self._draw_edges(context, width, height)

        # Draw nodes
        self._draw_nodes(context, width, height)

    def _draw_arrow_head(
        self,
        context: cairo.Context,
        x: float,
        y: float,
        prev_x: float,
        prev_y: float,
        color: tuple[float, float, float],
    ):
        """Draw an arrow head at the end of an edge."""
        # Calculate angle
        angle = math.atan2(y - prev_y, x - prev_x)

        # Arrow dimensions
        arrow_size = 10
        arrow_angle = math.pi / 6  # 30 degrees

        # Calculate arrow points
        p1_x = x - arrow_size * math.cos(angle - arrow_angle)
        p1_y = y - arrow_size * math.sin(angle - arrow_angle)
        p2_x = x - arrow_size * math.cos(angle + arrow_angle)
        p2_y = y - arrow_size * math.sin(angle + arrow_angle)

        # Draw arrow
        context.set_source_rgb(*color)
        context.move_to(x, y)
        context.line_to(p1_x, p1_y)
        context.line_to(p2_x, p2_y)
        context.close_path()
        context.fill()

    def _draw_grid(self, context: cairo.Context, width: int, height: int):
        """Draw grid background."""
        context.set_source_rgb(0.9, 0.9, 0.9)
        context.set_line_width(0.5)

        # Calculate grid start positions
        grid_x = (self.viewport.x % self.grid_size) * self.viewport.zoom
        grid_y = (self.viewport.y % self.grid_size) * self.viewport.zoom

        # Draw vertical lines
        x = grid_x
        while x < width:
            context.move_to(x, 0)
            context.line_to(x, height)
            x += self.grid_size * self.viewport.zoom

        # Draw horizontal lines
        y = grid_y
        while y < height:
            context.move_to(0, y)
            context.line_to(width, y)
            y += self.grid_size * self.viewport.zoom

        context.stroke()

    def _draw_edges(self, context: cairo.Context, width: int, height: int):
        """Draw edges between nodes with enhanced visuals."""
        if not self.edges:
            return

        for edge in self.edges:
            # Find source and target nodes
            source_node = next((n for n in self.nodes if n.get("id") == edge.get("source")), None)
            target_node = next((n for n in self.nodes if n.get("id") == edge.get("target")), None)

            if source_node and target_node:
                # Get node positions in canvas space
                x1 = (
                    source_node.get("position", {}).get("x", 0) - self.viewport.x
                ) * self.viewport.zoom + 50
                y1 = (
                    source_node.get("position", {}).get("y", 0) - self.viewport.y
                ) * self.viewport.zoom + 30
                x2 = (
                    target_node.get("position", {}).get("x", 0) - self.viewport.x
                ) * self.viewport.zoom
                y2 = (
                    target_node.get("position", {}).get("y", 0) - self.viewport.y
                ) * self.viewport.zoom + 30

                # Determine edge color based on status
                status = edge.get("status", "idle")
                if status == "active":
                    color = (0.2, 0.8, 0.2)  # Green
                    line_width = 3.0
                elif status == "error":
                    color = (1.0, 0.2, 0.2)  # Red
                    line_width = 2.5
                else:
                    color = (0.5, 0.5, 0.5)  # Gray
                    line_width = 2.0

                context.set_source_rgb(*color)
                context.set_line_width(line_width)

                # Draw bezier curve
                context.move_to(x1, y1)
                context.curve_to(x1 + 100, y1, x2 - 100, y2, x2, y2)
                context.stroke()

                # Draw arrow head
                self._draw_arrow_head(context, x2, y2, x1, y1, color)

    def _draw_nodes(self, context: cairo.Context, width: int, height: int):
        """Draw nodes on the canvas."""
        if not self.nodes:
            return

        for node in self.nodes:
            self._draw_node(context, node, width, height)

    def _draw_node(self, context: cairo.Context, node: dict[str, Any], width: int, height: int):
        """Draw a single node with enhanced visuals."""
        x = (node.get("position", {}).get("x", 0) - self.viewport.x) * self.viewport.zoom
        y = (node.get("position", {}).get("y", 0) - self.viewport.y) * self.viewport.zoom
        node_width = 100
        node_height = 60
        corner_radius = 4

        # Get node status for color coding
        status = node.get("status", "idle")
        is_selected = node.get("id") == self._selected_node

        # Determine node color based on status
        if status == "running":
            color = (0.2, 0.8, 0.2)  # Green
        elif status == "failed":
            color = (1.0, 0.2, 0.2)  # Red
        elif status == "completed":
            color = (0.2, 0.6, 1.0)  # Blue
        else:
            color = (0.7, 0.7, 0.7)  # Gray

        # Draw rounded rectangle background
        context.new_path()
        context.arc(
            x + corner_radius,
            y + corner_radius,
            corner_radius,
            math.pi,
            3 * math.pi / 2,
        )
        context.arc(
            x + node_width - corner_radius,
            y + corner_radius,
            corner_radius,
            3 * math.pi / 2,
            2 * math.pi,
        )
        context.arc(
            x + node_width - corner_radius,
            y + node_height - corner_radius,
            corner_radius,
            0,
            math.pi / 2,
        )
        context.arc(
            x + corner_radius,
            y + node_height - corner_radius,
            corner_radius,
            math.pi / 2,
            math.pi,
        )
        context.close_path()

        context.set_source_rgb(*color)
        context.fill_preserve()

        # Draw border
        context.set_source_rgb(0.0, 0.0, 0.0)
        context.set_line_width(2.0 if is_selected else 1.0)
        context.stroke()

        # Draw selection highlight if selected
        if is_selected:
            context.set_source_rgba(0.2, 0.6, 1.0, 0.3)
            context.set_line_width(3.0)
            context.stroke()

        # Draw node label
        context.set_source_rgb(1.0, 1.0, 1.0)
        context.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        context.set_font_size(12)
        label = node.get("label", "Node")

        # Center text
        extents = context.text_extents(label)
        text_x = x + (node_width - extents.width) / 2
        text_y = y + (node_height - extents.height) / 2 + extents.height
        context.move_to(text_x, text_y)
        context.show_text(label)

        # Draw status indicator (small circle in corner)
        indicator_size = 6
        indicator_x = x + node_width - indicator_size - 4
        indicator_y = y + 4

        if status == "running":
            context.set_source_rgb(0.2, 0.8, 0.2)
        elif status == "failed":
            context.set_source_rgb(1.0, 0.2, 0.2)
        elif status == "completed":
            context.set_source_rgb(0.2, 0.6, 1.0)
        else:
            context.set_source_rgb(0.5, 0.5, 0.5)

        context.arc(indicator_x, indicator_y, indicator_size, 0, 2 * math.pi)
        context.fill()

    def _on_motion(self, controller, x: float, y: float):
        """Handle mouse motion."""
        pass

    def _on_click_pressed(self, controller, n_press: int, x: float, y: float):
        """Handle mouse click pressed."""
        if self.readonly:
            return

        # Check if clicked on a node
        for node in self.nodes:
            if self._point_in_node(x, y, node):
                self._selected_node = node.get("id")
                self.emit("node-selected", self._selected_node)
                self.queue_draw()
                return

        # Clicked on canvas background
        self._selected_node = None
        self.emit("canvas-clicked")
        self.queue_draw()

    def _on_click_released(self, controller, n_press: int, x: float, y: float):
        """Handle mouse click released."""
        pass

    def _on_scroll(self, controller, dx: float, dy: float) -> bool:
        """Handle scroll wheel for zooming."""
        if self.readonly:
            return False

        # Get cursor position
        x, y = controller.get_widget().get_pointer()

        # Zoom in/out
        factor = 1.1 if dy < 0 else 0.9
        self.viewport.zoom_at(factor, x, y)

        self.emit("viewport-changed", self.viewport.x, self.viewport.y, self.viewport.zoom)
        self.queue_draw()
        return True

    def _on_drag_begin(self, controller, x: float, y: float):
        """Handle drag begin."""
        if self.readonly:
            return

        # Check if dragging a selected node
        if self._selected_node:
            for node in self.nodes:
                if node.get("id") == self._selected_node:
                    if self._point_in_node(x, y, node):
                        self._dragging_node = self._selected_node
                        self._drag_start = (x, y)
                        return

        # Otherwise, start panning
        self._pan_start = (x, y)
        self._is_panning = True

    def _on_drag_update(self, controller, dx: float, dy: float):
        """Handle drag update."""
        if self.readonly:
            return

        # If dragging a node, move it
        if self._dragging_node and self._drag_start:
            for node in self.nodes:
                if node.get("id") == self._dragging_node:
                    # Update node position
                    pos = node.get("position", {"x": 0, "y": 0})
                    new_x = pos["x"] + dx / self.viewport.zoom
                    new_y = pos["y"] + dy / self.viewport.zoom

                    # Apply grid snapping if enabled
                    if self.snap_to_grid:
                        new_x = round(new_x / self.grid_size) * self.grid_size
                        new_y = round(new_y / self.grid_size) * self.grid_size

                    node["position"]["x"] = new_x
                    node["position"]["y"] = new_y

                    self.emit("node-moved", self._dragging_node, new_x, new_y)
                    self.queue_draw()
                    return

        # Pan the viewport
        if self._is_panning and self._pan_start:
            self.viewport.pan(-dx / self.viewport.zoom, -dy / self.viewport.zoom)
            self.emit("viewport-changed", self.viewport.x, self.viewport.y, self.viewport.zoom)
            self.queue_draw()

    def _on_drag_end(self, controller, x: float, y: float):
        """Handle drag end."""
        self._dragging_node = None
        self._drag_start = None
        self._is_panning = False
        self._pan_start = None

    def _point_in_node(self, x: float, y: float, node: dict[str, Any]) -> bool:
        """Check if a point is inside a node."""
        node_x = (node.get("position", {}).get("x", 0) - self.viewport.x) * self.viewport.zoom
        node_y = (node.get("position", {}).get("y", 0) - self.viewport.y) * self.viewport.zoom
        node_width = 100
        node_height = 60

        return node_x <= x <= node_x + node_width and node_y <= y <= node_y + node_height

    def set_nodes(self, nodes: list[dict[str, Any]]):
        """Set the nodes to display."""
        self.nodes = nodes
        self.queue_draw()

    def set_edges(self, edges: list[dict[str, Any]]):
        """Set the edges to display."""
        self.edges = edges
        self.queue_draw()

    def reset_viewport(self):
        """Reset viewport to default position and zoom."""
        self.viewport = Viewport()
        self.emit("viewport-changed", self.viewport.x, self.viewport.y, self.viewport.zoom)
        self.queue_draw()
