"""Workspace state - State management for the graph workspace screen.

Supports multiple modes: list, graph view, edit, connect.
Uses canonical types from libs/python/models/graph/schema.py.
"""

from dataclasses import dataclass, field
from enum import Enum

from libs.python.terminal.unhinged.graph_actions import CommandHistory
from libs.python.terminal.unhinged.graph_types import Graph, Node, NodeType, get_node


class WorkspaceMode(Enum):
    """Current mode of the workspace."""

    VIEW = "view"  # Read-only view (no editing)
    LIST = "list"  # Split-pane node navigator (default)
    GRAPH = "graph"  # ASCII neighborhood view
    EDIT = "edit"  # Editing a node's properties
    CONNECT = "connect"  # Drawing an edge between nodes
    ADD = "add"  # Adding a new node (type selection)
    NODE_DETAIL = "node_detail"  # Full-screen node detail view


# =============================================================================
# Mode-specific States
# =============================================================================


@dataclass
class ListModeState:
    """State for list mode navigation."""

    # Selected node index in the list
    selected_index: int = 0
    # Scroll offset for long lists
    scroll_offset: int = 0
    # Detail panel focus (0 = node list, 1 = edge list)
    panel_focus: int = 0


@dataclass
class GraphModeState:
    """State for graph visualization mode with viewport.

    Uses viewport/camera pattern for viewing the entire graph.
    Layout is calculated once and cached. Viewport controls what's visible.
    """

    # Currently selected node ID
    selected_node_id: str | None = None
    # Viewport position in world coordinates
    viewport_x: float = 0.0
    viewport_y: float = 0.0
    # Target viewport position (for smooth animation)
    target_x: float = 0.0
    target_y: float = 0.0
    # Animation progress (0.0 = at current, 1.0 = at target)
    anim_progress: float = 1.0
    # Whether layout needs recalculation
    layout_dirty: bool = True


@dataclass
class EditModeState:
    """State for node editing mode."""

    # Node being edited
    node_id: str
    # Current field being edited
    field_index: int = 0
    # Text input buffer
    input_buffer: str = ""
    # Is currently in text input mode
    input_active: bool = False
    # Fields available for editing
    fields: tuple[str, ...] = ("name", "description")


@dataclass
class ConnectModeState:
    """State for edge creation mode."""

    # Source node
    from_node_id: str
    # Source port (or None to auto-select)
    from_port: str | None = None
    # Currently highlighted target node
    target_index: int = 0


@dataclass
class AddModeState:
    """State for adding a new node."""

    # Currently selected node type index
    type_index: int = 0
    # Available node types (canonical NodeType values)
    node_types: tuple[NodeType, ...] = (
        NodeType.LLM_CHAT,
        NodeType.DATA_TRANSFORM,
        NodeType.CONDITIONAL,
        NodeType.HTTP_REQUEST,
        NodeType.SPEECH_TO_TEXT,
        NodeType.TEXT_TO_SPEECH,
    )


@dataclass
class ViewModeState:
    """State for read-only view mode."""

    # Selected node index in the list
    selected_index: int = 0
    # Scroll offset for long lists
    scroll_offset: int = 0
    # Current tab: 0=nodes, 1=edges, 2=info
    current_tab: int = 0


@dataclass
class NodeDetailState:
    """State for full-screen node detail view."""

    # The node being viewed
    node_id: str
    # Scroll offset for long content
    scroll_offset: int = 0
    # Pre-rendered content lines (computed on entry)
    content_lines: list[str] = field(default_factory=list)


# =============================================================================
# Main Workspace State
# =============================================================================


@dataclass
class WorkspaceState:
    """Complete workspace state."""

    # The graph being edited/viewed
    graph: Graph

    # Current mode
    mode: WorkspaceMode = WorkspaceMode.LIST

    # Read-only flag (disables editing)
    read_only: bool = False

    # Command history for undo/redo (only used when not read_only)
    history: CommandHistory = field(default_factory=CommandHistory)

    # Mode-specific states
    list_state: ListModeState = field(default_factory=ListModeState)
    graph_state: GraphModeState = field(default_factory=GraphModeState)
    view_state: ViewModeState = field(default_factory=ViewModeState)
    edit_state: EditModeState | None = None
    connect_state: ConnectModeState | None = None
    add_state: AddModeState | None = None
    node_detail_state: NodeDetailState | None = None

    # Running flag
    running: bool = True

    # Status message
    status: str = "W/S: Navigate  |  E: Select  |  V: View  |  Q: Back"

    # Result flags
    save_on_exit: bool = False

    def _replace(self, **changes) -> "WorkspaceState":
        """Create a copy with some fields replaced."""
        from dataclasses import replace

        return replace(self, **changes)

    @property
    def selected_node(self) -> Node | None:
        """Get the currently selected node."""
        if self.mode == WorkspaceMode.VIEW:
            if 0 <= self.view_state.selected_index < len(self.graph.nodes):
                return self.graph.nodes[self.view_state.selected_index]
        elif self.mode == WorkspaceMode.LIST:
            if 0 <= self.list_state.selected_index < len(self.graph.nodes):
                return self.graph.nodes[self.list_state.selected_index]
        elif self.mode == WorkspaceMode.GRAPH:
            if self.graph_state.selected_node_id:
                return get_node(self.graph, self.graph_state.selected_node_id)
        return None

    # -------------------------------------------------------------------------
    # Mode transitions
    # -------------------------------------------------------------------------

    def enter_view_mode(self) -> "WorkspaceState":
        """Switch to read-only view mode."""
        return self._replace(
            mode=WorkspaceMode.VIEW,
            status="W/S: Navigate  |  E: Details  |  A/D: Tab  |  V: Graph  |  Q: Back",
        )

    def enter_list_mode(self) -> "WorkspaceState":
        """Switch to list mode (edit mode)."""
        if self.read_only:
            return self.enter_view_mode()
        return self._replace(
            mode=WorkspaceMode.LIST,
            status="W/S: Navigate  |  E: Edit  |  A: Add  |  V: View  |  Q: Back",
        )

    def enter_graph_mode(self) -> "WorkspaceState":
        """Switch to graph visualization mode with full graph view."""
        node = self.selected_node
        graph_state = GraphModeState(
            selected_node_id=node.id if node else None,
            layout_dirty=True,
        )
        return self._replace(
            mode=WorkspaceMode.GRAPH,
            graph_state=graph_state,
            status="WASD: Pan  |  W/S: Select  |  E: Center  |  V: List  |  Q: Back",
        )

    def enter_edit_mode(self, node_id: str) -> "WorkspaceState":
        """Switch to edit mode for a node."""
        edit_state = EditModeState(node_id=node_id)
        return self._replace(
            mode=WorkspaceMode.EDIT,
            edit_state=edit_state,
            status="W/S: Field  |  E: Edit  |  ESC: Done",
        )

    def enter_connect_mode(self, from_node_id: str) -> "WorkspaceState":
        """Switch to connect mode to draw an edge."""
        connect_state = ConnectModeState(from_node_id=from_node_id)
        return self._replace(
            mode=WorkspaceMode.CONNECT,
            connect_state=connect_state,
            status="W/S: Target  |  E: Connect  |  ESC: Cancel",
        )

    def enter_add_mode(self) -> "WorkspaceState":
        """Switch to add mode to create a new node."""
        add_state = AddModeState()
        return self._replace(
            mode=WorkspaceMode.ADD,
            add_state=add_state,
            status="W/S: Type  |  E: Create  |  ESC: Cancel",
        )

    def enter_node_detail_mode(self, node_id: str, content_lines: list[str]) -> "WorkspaceState":
        """Switch to full-screen node detail view."""
        detail_state = NodeDetailState(
            node_id=node_id,
            scroll_offset=0,
            content_lines=content_lines,
        )
        return self._replace(
            mode=WorkspaceMode.NODE_DETAIL,
            node_detail_state=detail_state,
            status="W/S: Scroll  |  Q: Back",
        )

    def exit_node_detail_mode(self) -> "WorkspaceState":
        """Exit node detail view back to previous mode."""
        # Return to view mode (could track previous mode if needed)
        return self._replace(
            mode=WorkspaceMode.VIEW,
            node_detail_state=None,
            status="W/S: Navigate  |  E: Details  |  A/D: Tab  |  V: Graph  |  Q: Back",
        )

    # -------------------------------------------------------------------------
    # Navigation
    # -------------------------------------------------------------------------

    def nav_up(self) -> "WorkspaceState":
        """Navigate up in current mode."""
        if self.mode == WorkspaceMode.VIEW:
            new_idx = max(0, self.view_state.selected_index - 1)
            new_view = ViewModeState(
                selected_index=new_idx,
                scroll_offset=self.view_state.scroll_offset,
                current_tab=self.view_state.current_tab,
            )
            return self._replace(view_state=new_view)
        elif self.mode == WorkspaceMode.LIST:
            new_idx = max(0, self.list_state.selected_index - 1)
            new_list = ListModeState(
                selected_index=new_idx,
                scroll_offset=self.list_state.scroll_offset,
                panel_focus=self.list_state.panel_focus,
            )
            return self._replace(list_state=new_list)
        elif self.mode == WorkspaceMode.ADD and self.add_state:
            new_idx = max(0, self.add_state.type_index - 1)
            new_add = AddModeState(
                type_index=new_idx,
                node_types=self.add_state.node_types,
            )
            return self._replace(add_state=new_add)
        elif self.mode == WorkspaceMode.EDIT and self.edit_state:
            new_idx = max(0, self.edit_state.field_index - 1)
            new_edit = EditModeState(
                node_id=self.edit_state.node_id,
                field_index=new_idx,
                input_buffer=self.edit_state.input_buffer,
                input_active=self.edit_state.input_active,
                fields=self.edit_state.fields,
            )
            return self._replace(edit_state=new_edit)
        elif self.mode == WorkspaceMode.CONNECT and self.connect_state:
            new_idx = max(0, self.connect_state.target_index - 1)
            new_conn = ConnectModeState(
                from_node_id=self.connect_state.from_node_id,
                from_port=self.connect_state.from_port,
                target_index=new_idx,
            )
            return self._replace(connect_state=new_conn)
        elif self.mode == WorkspaceMode.NODE_DETAIL and self.node_detail_state:
            new_offset = max(0, self.node_detail_state.scroll_offset - 1)
            new_detail = NodeDetailState(
                node_id=self.node_detail_state.node_id,
                scroll_offset=new_offset,
                content_lines=self.node_detail_state.content_lines,
            )
            return self._replace(node_detail_state=new_detail)
        return self

    def nav_down(self) -> "WorkspaceState":
        """Navigate down in current mode."""
        if self.mode == WorkspaceMode.VIEW:
            max_idx = max(0, len(self.graph.nodes) - 1)
            new_idx = min(max_idx, self.view_state.selected_index + 1)
            new_view = ViewModeState(
                selected_index=new_idx,
                scroll_offset=self.view_state.scroll_offset,
                current_tab=self.view_state.current_tab,
            )
            return self._replace(view_state=new_view)
        elif self.mode == WorkspaceMode.LIST:
            max_idx = max(0, len(self.graph.nodes) - 1)
            new_idx = min(max_idx, self.list_state.selected_index + 1)
            new_list = ListModeState(
                selected_index=new_idx,
                scroll_offset=self.list_state.scroll_offset,
                panel_focus=self.list_state.panel_focus,
            )
            return self._replace(list_state=new_list)
        elif self.mode == WorkspaceMode.ADD and self.add_state:
            max_idx = len(self.add_state.node_types) - 1
            new_idx = min(max_idx, self.add_state.type_index + 1)
            new_add = AddModeState(
                type_index=new_idx,
                node_types=self.add_state.node_types,
            )
            return self._replace(add_state=new_add)
        elif self.mode == WorkspaceMode.EDIT and self.edit_state:
            max_idx = len(self.edit_state.fields) - 1
            new_idx = min(max_idx, self.edit_state.field_index + 1)
            new_edit = EditModeState(
                node_id=self.edit_state.node_id,
                field_index=new_idx,
                input_buffer=self.edit_state.input_buffer,
                input_active=self.edit_state.input_active,
                fields=self.edit_state.fields,
            )
            return self._replace(edit_state=new_edit)
        elif self.mode == WorkspaceMode.CONNECT and self.connect_state:
            max_idx = max(0, len(self.graph.nodes) - 1)
            new_idx = min(max_idx, self.connect_state.target_index + 1)
            new_conn = ConnectModeState(
                from_node_id=self.connect_state.from_node_id,
                from_port=self.connect_state.from_port,
                target_index=new_idx,
            )
            return self._replace(connect_state=new_conn)
        elif self.mode == WorkspaceMode.NODE_DETAIL and self.node_detail_state:
            # Allow scrolling but don't exceed content length
            max_offset = max(0, len(self.node_detail_state.content_lines) - 1)
            new_offset = min(max_offset, self.node_detail_state.scroll_offset + 1)
            new_detail = NodeDetailState(
                node_id=self.node_detail_state.node_id,
                scroll_offset=new_offset,
                content_lines=self.node_detail_state.content_lines,
            )
            return self._replace(node_detail_state=new_detail)
        return self

    def nav_left(self) -> "WorkspaceState":
        """Navigate left (tab switching in view mode)."""
        if self.mode == WorkspaceMode.VIEW:
            new_tab = max(0, self.view_state.current_tab - 1)
            new_view = ViewModeState(
                selected_index=self.view_state.selected_index,
                scroll_offset=self.view_state.scroll_offset,
                current_tab=new_tab,
            )
            return self._replace(view_state=new_view)
        return self

    def nav_right(self) -> "WorkspaceState":
        """Navigate right (tab switching in view mode)."""
        if self.mode == WorkspaceMode.VIEW:
            new_tab = min(2, self.view_state.current_tab + 1)  # 3 tabs: nodes, edges, info
            new_view = ViewModeState(
                selected_index=self.view_state.selected_index,
                scroll_offset=self.view_state.scroll_offset,
                current_tab=new_tab,
            )
            return self._replace(view_state=new_view)
        return self

    def quit(self) -> "WorkspaceState":
        """Exit the workspace."""
        return self._replace(running=False)

    def set_status(self, status: str) -> "WorkspaceState":
        """Update status message."""
        return self._replace(status=status)


def create_workspace_state(graph: Graph, read_only: bool = False) -> WorkspaceState:
    """Create initial workspace state for a graph.

    Args:
        graph: The graph to view/edit.
        read_only: If True, start in VIEW mode with editing disabled.

    Returns:
        Initial WorkspaceState.
    """
    if read_only:
        return WorkspaceState(
            graph=graph,
            mode=WorkspaceMode.VIEW,
            read_only=True,
            status=f"Viewing: {graph.name}  |  {len(graph.nodes)} nodes  |  {len(graph.edges)} edges",
        )
    else:
        return WorkspaceState(
            graph=graph,
            mode=WorkspaceMode.LIST,
            read_only=False,
            status=f"Editing: {graph.name}  |  {len(graph.nodes)} nodes",
        )
