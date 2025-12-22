"""Workspace screen - Graph editing workspace.

Entry point: run_workspace()

Supports multiple modes:
- LIST: Split-pane node navigator
- GRAPH: ASCII neighborhood view
- EDIT: Node property editing
- CONNECT: Edge creation
- ADD: New node creation

Uses canonical types from libs/python/models/graph/schema.py.
"""

from libs.python.terminal.cell import Color, Style
from libs.python.terminal.engine import Engine, Event, InputEvent
from libs.python.terminal.renderer import Renderer
from libs.python.terminal.unhinged.graph_actions import (
    AddEdge,
    AddNode,
    DeleteNode,
    UpdateNode,
)
from libs.python.terminal.unhinged.graph_registry import NodeRegistry
from libs.python.terminal.unhinged.graph_types import (
    Graph,
    Node,
    get_edges_from,
    get_edges_to,
    node_description,
    node_x,
    node_y,
)
from libs.python.terminal.unhinged.workspace_state import (
    WorkspaceMode,
    WorkspaceState,
    create_workspace_state,
)

# =============================================================================
# Update Functions (per mode)
# =============================================================================


def update(state: WorkspaceState, event: Event) -> WorkspaceState:
    """Route update to mode-specific handler."""
    # Handle escape to go back to list/view mode from other modes
    if event.type == InputEvent.ESCAPE:
        if state.mode not in (WorkspaceMode.LIST, WorkspaceMode.VIEW):
            return state.enter_list_mode()  # Will redirect to VIEW if read_only
        return state

    # Route to mode-specific handler
    match state.mode:
        case WorkspaceMode.VIEW:
            return _update_view_mode(state, event)
        case WorkspaceMode.LIST:
            return _update_list_mode(state, event)
        case WorkspaceMode.GRAPH:
            return _update_graph_mode(state, event)
        case WorkspaceMode.EDIT:
            return _update_edit_mode(state, event)
        case WorkspaceMode.CONNECT:
            return _update_connect_mode(state, event)
        case WorkspaceMode.ADD:
            return _update_add_mode(state, event)
        case WorkspaceMode.NODE_DETAIL:
            return _update_node_detail_mode(state, event)
    return state


def _update_view_mode(state: WorkspaceState, event: Event) -> WorkspaceState:
    """Handle input in read-only view mode."""
    if event.type == InputEvent.QUIT:
        return state.quit()

    # W/S for up/down navigation
    if event.type == InputEvent.NAV_UP:
        return state.nav_up()
    if event.type == InputEvent.NAV_DOWN:
        return state.nav_down()

    # A/D for tab switching
    if event.type == InputEvent.NAV_LEFT:
        return state.nav_left()
    if event.type == InputEvent.NAV_RIGHT:
        return state.nav_right()

    # V to switch to graph view
    if event.type == InputEvent.CHAR and event.char == "v":
        return state.enter_graph_mode()

    # E to open node detail view
    if event.type == InputEvent.INTERACT:
        node = state.selected_node
        if node:
            content_lines = _build_node_detail_content(node, state)
            return state.enter_node_detail_mode(node.id, content_lines)

    return state


def _update_list_mode(state: WorkspaceState, event: Event) -> WorkspaceState:
    """Handle input in list mode."""
    if event.type == InputEvent.QUIT:
        return state.quit()

    if event.type == InputEvent.NAV_UP:
        return state.nav_up()

    if event.type == InputEvent.NAV_DOWN:
        return state.nav_down()

    if event.type == InputEvent.INTERACT:
        # Edit selected node
        node = state.selected_node
        if node:
            return state.enter_edit_mode(node.id)
        return state

    # 'V' to toggle graph view
    if event.type == InputEvent.CHAR and event.char == "v":
        return state.enter_graph_mode()

    # 'A' to add new node
    if event.type == InputEvent.CHAR and event.char == "a":
        return state.enter_add_mode()

    # 'C' to connect (start edge from selected node)
    if event.type == InputEvent.CHAR and event.char == "c":
        node = state.selected_node
        if node:
            return state.enter_connect_mode(node.id)
        return state

    # 'X' to delete selected node
    if event.type == InputEvent.CHAR and event.char == "x":
        node = state.selected_node
        if node:
            action = DeleteNode(node_id=node.id)
            new_graph = state.history.execute(action, state.graph)
            return state._replace(
                graph=new_graph,
                status=f"Deleted node: {node.name}",
            )
        return state

    # 'U' to undo
    if event.type == InputEvent.CHAR and event.char == "u":
        if state.history.can_undo:
            new_graph = state.history.undo(state.graph)
            return state._replace(graph=new_graph, status="Undo")
        return state.set_status("Nothing to undo")

    # 'R' to redo
    if event.type == InputEvent.CHAR and event.char == "r":
        if state.history.can_redo:
            new_graph = state.history.redo(state.graph)
            return state._replace(graph=new_graph, status="Redo")
        return state.set_status("Nothing to redo")

    return state


def _update_graph_mode(state: WorkspaceState, event: Event) -> WorkspaceState:
    """Handle input in full graph view mode with viewport navigation.

    Controls:
    - WASD: Pan the viewport around the graph
    - Tab/Shift-Tab or N/P: Select next/previous node
    - E: Center viewport on selected node (with animation)
    - V: Return to list mode
    - Q: Back
    """
    from libs.python.terminal.unhinged.workspace_state import GraphModeState

    if event.type == InputEvent.QUIT:
        return state.enter_list_mode()

    # 'V' to toggle back to list/view
    if event.type == InputEvent.CHAR and event.char == "v":
        return state.enter_list_mode()

    gs = state.graph_state
    if not gs:
        return state

    # Pan speed
    PAN_SPEED = 3.0

    # WASD panning
    if event.type == InputEvent.NAV_UP:
        new_gs = GraphModeState(
            selected_node_id=gs.selected_node_id,
            viewport_x=gs.viewport_x,
            viewport_y=gs.viewport_y - PAN_SPEED,
            target_x=gs.target_x,
            target_y=gs.target_y - PAN_SPEED,
            anim_progress=1.0,
            layout_dirty=gs.layout_dirty,
        )
        return state._replace(graph_state=new_gs)

    if event.type == InputEvent.NAV_DOWN:
        new_gs = GraphModeState(
            selected_node_id=gs.selected_node_id,
            viewport_x=gs.viewport_x,
            viewport_y=gs.viewport_y + PAN_SPEED,
            target_x=gs.target_x,
            target_y=gs.target_y + PAN_SPEED,
            anim_progress=1.0,
            layout_dirty=gs.layout_dirty,
        )
        return state._replace(graph_state=new_gs)

    if event.type == InputEvent.NAV_LEFT:
        new_gs = GraphModeState(
            selected_node_id=gs.selected_node_id,
            viewport_x=gs.viewport_x - PAN_SPEED,
            viewport_y=gs.viewport_y,
            target_x=gs.target_x - PAN_SPEED,
            target_y=gs.target_y,
            anim_progress=1.0,
            layout_dirty=gs.layout_dirty,
        )
        return state._replace(graph_state=new_gs)

    if event.type == InputEvent.NAV_RIGHT:
        new_gs = GraphModeState(
            selected_node_id=gs.selected_node_id,
            viewport_x=gs.viewport_x + PAN_SPEED,
            viewport_y=gs.viewport_y,
            target_x=gs.target_x + PAN_SPEED,
            target_y=gs.target_y,
            anim_progress=1.0,
            layout_dirty=gs.layout_dirty,
        )
        return state._replace(graph_state=new_gs)

    # N/P or Tab to cycle through nodes
    if event.type == InputEvent.CHAR and event.char in ("n", "\t"):
        nodes = state.graph.nodes
        if nodes:
            current_idx = 0
            if gs.selected_node_id:
                for i, n in enumerate(nodes):
                    if n.id == gs.selected_node_id:
                        current_idx = i
                        break
            new_idx = (current_idx + 1) % len(nodes)
            new_node_id = nodes[new_idx].id
            new_gs = GraphModeState(
                selected_node_id=new_node_id,
                viewport_x=gs.viewport_x,
                viewport_y=gs.viewport_y,
                target_x=gs.target_x,
                target_y=gs.target_y,
                anim_progress=gs.anim_progress,
                layout_dirty=gs.layout_dirty,
            )
            return state._replace(
                graph_state=new_gs,
                status=f"Selected: {nodes[new_idx].name}",
            )

    if event.type == InputEvent.CHAR and event.char == "p":
        nodes = state.graph.nodes
        if nodes:
            current_idx = 0
            if gs.selected_node_id:
                for i, n in enumerate(nodes):
                    if n.id == gs.selected_node_id:
                        current_idx = i
                        break
            new_idx = (current_idx - 1) % len(nodes)
            new_node_id = nodes[new_idx].id
            new_gs = GraphModeState(
                selected_node_id=new_node_id,
                viewport_x=gs.viewport_x,
                viewport_y=gs.viewport_y,
                target_x=gs.target_x,
                target_y=gs.target_y,
                anim_progress=gs.anim_progress,
                layout_dirty=gs.layout_dirty,
            )
            return state._replace(
                graph_state=new_gs,
                status=f"Selected: {nodes[new_idx].name}",
            )

    # E to center viewport on selected node
    if event.type == InputEvent.CHAR and event.char == "e":
        if gs.selected_node_id:
            from libs.python.terminal.unhinged.graph_layout import calculate_hierarchical_layout
            from libs.python.terminal.unhinged.graph_types import get_node

            node = get_node(state.graph, gs.selected_node_id)
            if node:
                # Get layout to find node position
                layout = calculate_hierarchical_layout(state.graph)
                pos = layout.get_position(gs.selected_node_id)
                if pos:
                    # Center viewport on this position
                    # Assume viewport is ~80x24, offset to center
                    new_vp_x = pos[0] - 40
                    new_vp_y = pos[1] - 10
                    new_gs = GraphModeState(
                        selected_node_id=gs.selected_node_id,
                        viewport_x=new_vp_x,
                        viewport_y=new_vp_y,
                        target_x=new_vp_x,
                        target_y=new_vp_y,
                        anim_progress=1.0,
                        layout_dirty=False,
                    )
                    return state._replace(
                        graph_state=new_gs,
                        status=f"Centered on: {node.name}",
                    )

    return state


def _update_edit_mode(state: WorkspaceState, event: Event) -> WorkspaceState:
    """Handle input in edit mode."""
    if not state.edit_state:
        return state.enter_list_mode()

    es = state.edit_state

    # Text input active
    if es.input_active:
        if event.type == InputEvent.ESCAPE or event.type == InputEvent.ENTER:
            # Save the field value
            from libs.python.terminal.unhinged.graph_types import get_node

            node = get_node(state.graph, es.node_id)
            if node and es.input_buffer:
                field = es.fields[es.field_index]
                if field == "name":
                    action = UpdateNode(node_id=es.node_id, name=es.input_buffer)
                elif field == "description":
                    action = UpdateNode(
                        node_id=es.node_id,
                        config_updates=(("description", es.input_buffer),),
                    )
                else:
                    return state.enter_list_mode()
                new_graph = state.history.execute(action, state.graph)
                return state._replace(graph=new_graph).enter_list_mode()
            return state.enter_list_mode()

        if event.type == InputEvent.CHAR:
            from libs.python.terminal.unhinged.workspace_state import EditModeState

            new_es = EditModeState(
                node_id=es.node_id,
                field_index=es.field_index,
                input_buffer=es.input_buffer + event.char,
                input_active=True,
                fields=es.fields,
            )
            return state._replace(edit_state=new_es)

        # Backspace
        if event.char == "\x7f" or event.char == "\b":
            from libs.python.terminal.unhinged.workspace_state import EditModeState

            new_es = EditModeState(
                node_id=es.node_id,
                field_index=es.field_index,
                input_buffer=es.input_buffer[:-1],
                input_active=True,
                fields=es.fields,
            )
            return state._replace(edit_state=new_es)

        return state

    # Navigation
    if event.type == InputEvent.NAV_UP:
        return state.nav_up()
    if event.type == InputEvent.NAV_DOWN:
        return state.nav_down()

    # Activate text input
    if event.type == InputEvent.INTERACT:
        from libs.python.terminal.unhinged.graph_types import get_node

        node = get_node(state.graph, es.node_id)
        if node:
            field = es.fields[es.field_index]
            # Get initial value - name is on node, description is in config
            if field == "name":
                initial = node.name
            elif field == "description":
                initial = node.config.get("description", "")
            else:
                initial = ""
            from libs.python.terminal.unhinged.workspace_state import EditModeState

            new_es = EditModeState(
                node_id=es.node_id,
                field_index=es.field_index,
                input_buffer=initial,
                input_active=True,
                fields=es.fields,
            )
            return state._replace(edit_state=new_es)

    return state


def _update_connect_mode(state: WorkspaceState, event: Event) -> WorkspaceState:
    """Handle input in connect mode."""
    if not state.connect_state:
        return state.enter_list_mode()

    if event.type == InputEvent.NAV_UP:
        return state.nav_up()
    if event.type == InputEvent.NAV_DOWN:
        return state.nav_down()

    if event.type == InputEvent.INTERACT:
        cs = state.connect_state
        if cs.target_index < len(state.graph.nodes):
            target = state.graph.nodes[cs.target_index]
            if target.id != cs.from_node_id:
                action = AddEdge(
                    source_node_id=cs.from_node_id,
                    target_node_id=target.id,
                    source_output="out",
                    target_input="in",
                )
                new_graph = state.history.execute(action, state.graph)
                return state._replace(
                    graph=new_graph,
                    status=f"Connected to {target.name}",
                ).enter_list_mode()

    return state


def _update_add_mode(state: WorkspaceState, event: Event) -> WorkspaceState:
    """Handle input in add node mode."""
    if not state.add_state:
        return state.enter_list_mode()

    if event.type == InputEvent.NAV_UP:
        return state.nav_up()
    if event.type == InputEvent.NAV_DOWN:
        return state.nav_down()

    if event.type == InputEvent.INTERACT:
        node_type = state.add_state.node_types[state.add_state.type_index]
        # node_type is now a NodeType enum
        action = AddNode(
            node_type=node_type,
            name=f"New {node_type.value.replace('_', ' ').title()}",
        )
        new_graph = state.history.execute(action, state.graph)
        return state._replace(
            graph=new_graph,
            status=f"Added {node_type.value} node",
        ).enter_list_mode()

    return state


def _update_node_detail_mode(state: WorkspaceState, event: Event) -> WorkspaceState:
    """Handle input in full-screen node detail view."""
    if event.type == InputEvent.QUIT or event.type == InputEvent.ESCAPE:
        return state.exit_node_detail_mode()

    # W/S for scrolling up/down
    if event.type == InputEvent.NAV_UP:
        return state.nav_up()
    if event.type == InputEvent.NAV_DOWN:
        return state.nav_down()

    return state


def _wrap_text(text: str, width: int) -> list[str]:
    """Word-wrap text to specified width."""
    if not text:
        return []
    lines: list[str] = []
    for paragraph in text.split("\n"):
        if not paragraph:
            lines.append("")
            continue
        while len(paragraph) > width:
            # Find last space before width
            break_at = paragraph.rfind(" ", 0, width)
            if break_at <= 0:
                break_at = width  # Force break if no space
            lines.append(paragraph[:break_at])
            paragraph = paragraph[break_at:].lstrip()
        if paragraph:
            lines.append(paragraph)
    return lines


def _build_node_detail_content(node: Node, state: WorkspaceState) -> list[str]:
    """Build pre-rendered content lines for node detail view."""
    lines: list[str] = []

    # Header
    icon = NodeRegistry.get_icon(node.type)
    type_str = node.type.value if hasattr(node.type, "value") else str(node.type)
    lines.append(f"{'═' * 60}")
    lines.append(f"  {icon}  {node.name}")
    lines.append(f"{'═' * 60}")
    lines.append("")

    # Basic info
    lines.append(f"ID:   {node.id}")
    lines.append(f"Type: {type_str}")
    lines.append("")

    # Description
    desc = node_description(node)
    if desc:
        lines.append("─── Description ───")
        lines.extend(_wrap_text(desc, 70))
        lines.append("")

    # Config - the main content that needed scrolling!
    if node.config:
        lines.append("─── Configuration ───")
        for key, value in node.config.items():
            lines.append(f"  {key}:")
            val_str = str(value)
            wrapped = _wrap_text(val_str, 66)  # Indent by 4
            for wl in wrapped:
                lines.append(f"    {wl}")
            lines.append("")

    # Connections
    edges_from = get_edges_from(state.graph, node.id)
    edges_to = get_edges_to(state.graph, node.id)

    if edges_from or edges_to:
        lines.append("─── Connections ───")
        if edges_from:
            lines.append("  Outputs to:")
            for e in edges_from:
                lines.append(f"    → {e.target_node_id}")
        if edges_to:
            lines.append("  Inputs from:")
            for e in edges_to:
                lines.append(f"    ← {e.source_node_id}")
        lines.append("")

    # Position
    x, y = node_x(node), node_y(node)
    if x or y:
        lines.append(f"Position: ({x}, {y})")

    return lines


# =============================================================================
# Render Functions
# =============================================================================


def render(state: WorkspaceState, r: Renderer) -> None:
    """Route render to mode-specific renderer."""
    match state.mode:
        case WorkspaceMode.VIEW:
            _render_view_mode(state, r)
        case WorkspaceMode.LIST:
            _render_list_mode(state, r)
        case WorkspaceMode.GRAPH:
            _render_graph_mode(state, r)
        case WorkspaceMode.EDIT:
            _render_edit_mode(state, r)
        case WorkspaceMode.CONNECT:
            _render_connect_mode(state, r)
        case WorkspaceMode.ADD:
            _render_add_mode(state, r)
        case WorkspaceMode.NODE_DETAIL:
            _render_node_detail_mode(state, r)


def _render_view_mode(state: WorkspaceState, r: Renderer) -> None:
    """Render read-only view with tabbed interface."""
    w = r.fb.width
    h = r.fb.height

    # Styles
    border_style = Style(fg=Color.BLUE)
    title_style = Style(fg=Color.BLUE).bold()
    tab_active = Style(fg=Color.BLACK, bg=Color.BLUE)
    tab_inactive = Style(fg=Color.BLUE)
    selected_style = Style(fg=Color.BLACK, bg=Color.WHITE)
    normal_style = Style(fg=Color.WHITE)
    dim_style = Style(fg=Color.BRIGHT_BLACK)
    status_style = Style(fg=Color.YELLOW)
    type_style = Style(fg=Color.CYAN)

    vs = state.view_state
    tabs = ["Nodes", "Edges", "Info"]

    # Main panel
    r.panel(0, 0, w, h - 2, title=f"[ {state.graph.name} - View Only ]", style=border_style, title_style=title_style)

    # Tab bar
    tab_x = 2
    for i, tab_name in enumerate(tabs):
        style = tab_active if i == vs.current_tab else tab_inactive
        label = f" {tab_name} "
        r.text(tab_x, 2, label, style)
        tab_x += len(label) + 1

    # Content area based on active tab
    content_y = 4
    content_h = h - 8

    if vs.current_tab == 0:
        # Nodes tab - split view: list on left, details on right
        # Draw vertical separator
        sep_x = w // 2
        for y_pos in range(3, h - 4):
            r.text(sep_x, y_pos, "│", dim_style)

        if not state.graph.nodes:
            r.text(2, content_y, "No nodes in this graph.", dim_style)
        else:
            for i, node in enumerate(state.graph.nodes):
                if i >= content_h:
                    r.text(2, content_y + content_h, f"... and {len(state.graph.nodes) - content_h} more", dim_style)
                    break
                is_sel = i == vs.selected_index
                icon = NodeRegistry.get_icon(node.type)
                prefix = "▶ " if is_sel else "  "
                style = selected_style if is_sel else normal_style

                # Format: icon name - left half only (type shown in details)
                label = f"{prefix}{icon} {node.name}"
                # Limit label to left half minus padding for separator
                max_label_w = w // 2 - 3
                r.text(2, content_y + i, label[:max_label_w], style)

            # Show selected node details in right panel
            if state.selected_node:
                node = state.selected_node
                detail_x = w // 2 + 2
                detail_w = w - detail_x - 2  # Available width for details

                # Show node index in header for clarity
                node_idx = vs.selected_index + 1
                total_nodes = len(state.graph.nodes)
                r.text(detail_x, 4, f"─── Node {node_idx}/{total_nodes} ───"[:detail_w], dim_style)
                r.text(detail_x, 6, f"ID: {node.id}"[:detail_w], dim_style)
                r.text(detail_x, 7, f"Name: {node.name}"[:detail_w], normal_style)
                type_str = node.type.value if hasattr(node.type, "value") else str(node.type)
                r.text(detail_x, 8, f"Type: {type_str}"[:detail_w], type_style)
                desc = node_description(node)
                if desc:
                    r.text(detail_x, 10, "Description:", dim_style)
                    # Word wrap description
                    for j, line_start in enumerate(range(0, len(desc), detail_w)):
                        if j > 2:
                            r.text(detail_x, 11 + j, "...", dim_style)
                            break
                        r.text(detail_x, 11 + j, desc[line_start : line_start + detail_w], normal_style)

                # Show config keys
                if node.config:
                    config_y = 15
                    r.text(detail_x, config_y, "Config:", dim_style)
                    for j, key in enumerate(list(node.config.keys())[:5]):
                        if j > 4:
                            break
                        val = str(node.config[key])[: detail_w - len(key) - 4]
                        r.text(detail_x + 2, config_y + 1 + j, f"{key}: {val}"[: detail_w - 2], dim_style)

    elif vs.current_tab == 1:
        # Edges tab
        if not state.graph.edges:
            r.text(2, content_y, "No edges in this graph.", dim_style)
        else:
            for i, edge in enumerate(state.graph.edges):
                if i >= content_h:
                    r.text(2, content_y + content_h, f"... and {len(state.graph.edges) - content_h} more", dim_style)
                    break
                # Get source and target names
                from libs.python.terminal.unhinged.graph_types import get_node

                source = get_node(state.graph, edge.source_node_id)
                target = get_node(state.graph, edge.target_node_id)
                src_name = source.name if source else edge.source_node_id
                tgt_name = target.name if target else edge.target_node_id
                r.text(2, content_y + i, f"  {src_name}  →  {tgt_name}", normal_style)

    else:
        # Info tab
        r.text(2, content_y, f"Graph: {state.graph.name}", normal_style)
        r.text(2, content_y + 1, f"ID: {state.graph.id}", dim_style)
        r.text(2, content_y + 2, f"Type: {state.graph.graph_type.value}", dim_style)
        r.text(2, content_y + 4, "Description:", dim_style)
        desc = state.graph.description or "(no description)"
        r.text(2, content_y + 5, desc[: w - 4], normal_style)
        r.text(2, content_y + 7, f"Nodes: {len(state.graph.nodes)}", normal_style)
        r.text(2, content_y + 8, f"Edges: {len(state.graph.edges)}", normal_style)

        if state.graph.metadata:
            r.text(2, content_y + 10, "Metadata:", dim_style)
            for j, (key, val) in enumerate(list(state.graph.metadata.items())[:5]):
                r.text(4, content_y + 11 + j, f"{key}: {str(val)[:40]}", dim_style)

    # Help bar
    r.text(1, h - 4, "W/S: Navigate  |  A/D: Switch Tab  |  V: Graph View  |  Q: Back", dim_style)

    # Status bar
    r.panel(0, h - 2, w, 2, style=border_style)
    r.text(2, h - 1, state.status[: w - 4], status_style)


def _render_list_mode(state: WorkspaceState, r: Renderer) -> None:
    """Render split-pane list view."""
    w = r.fb.width
    h = r.fb.height

    # Styles
    border_style = Style(fg=Color.CYAN)
    title_style = Style(fg=Color.CYAN).bold()
    selected_style = Style(fg=Color.BLACK, bg=Color.CYAN)
    normal_style = Style(fg=Color.WHITE)
    dim_style = Style(fg=Color.BRIGHT_BLACK)
    status_style = Style(fg=Color.YELLOW)

    # Split: left panel (nodes), right panel (details)
    split_x = w // 2

    # Left panel: Node list
    r.panel(0, 0, split_x, h - 2, title=f"[ {state.graph.name} ]", style=border_style, title_style=title_style)

    list_y = 2
    for i, node in enumerate(state.graph.nodes):
        if list_y >= h - 4:
            break
        is_sel = i == state.list_state.selected_index
        prefix = "▶ " if is_sel else "  "
        icon = NodeRegistry.get_icon(node.type)
        style = selected_style if is_sel else normal_style
        label = f"{prefix}{icon} {node.name}"
        r.text(1, list_y, label[: split_x - 2], style)
        list_y += 1

    if not state.graph.nodes:
        r.text(2, 2, "No nodes. Press A to add.", dim_style)

    # Right panel: Details
    r.panel(split_x, 0, w - split_x, h - 2, title="[ Details ]", style=border_style, title_style=title_style)

    node = state.selected_node
    if node:
        r.text(split_x + 2, 2, f"Name: {node.name}", normal_style)
        # node.type is a NodeType enum
        type_str = node.type.value if hasattr(node.type, "value") else str(node.type)
        r.text(split_x + 2, 3, f"Type: {type_str}", dim_style)
        r.text(split_x + 2, 4, f"ID: {node.id}", dim_style)
        desc = node_description(node)
        if desc:
            r.text(split_x + 2, 6, "Description:", dim_style)
            r.text(split_x + 2, 7, desc[: w - split_x - 4], normal_style)

        # Edges
        edges_out = get_edges_from(state.graph, node.id)
        edges_in = get_edges_to(state.graph, node.id)

        edge_y = 9
        if edges_out:
            r.text(split_x + 2, edge_y, "Outgoing:", dim_style)
            edge_y += 1
            for edge in edges_out[:3]:
                from libs.python.terminal.unhinged.graph_types import get_node

                target = get_node(state.graph, edge.target_node_id)
                name = target.name if target else edge.target_node_id
                r.text(split_x + 4, edge_y, f"→ {name}", normal_style)
                edge_y += 1

        if edges_in:
            r.text(split_x + 2, edge_y, "Incoming:", dim_style)
            edge_y += 1
            for edge in edges_in[:3]:
                from libs.python.terminal.unhinged.graph_types import get_node

                source = get_node(state.graph, edge.source_node_id)
                name = source.name if source else edge.source_node_id
                r.text(split_x + 4, edge_y, f"← {name}", normal_style)
                edge_y += 1
    else:
        r.text(split_x + 2, 2, "Select a node", dim_style)

    # Help bar
    help_y = h - 4
    r.text(1, help_y, "E:Edit A:Add C:Connect X:Delete V:View U:Undo Q:Back", dim_style)

    # Status bar
    r.panel(0, h - 2, w, 2, style=border_style)
    r.text(2, h - 1, state.status[: w - 4], status_style)


# =============================================================================
# Graph Layout Cache (module-level for persistence across renders)
# =============================================================================
from libs.python.terminal.unhinged.graph_layout import GraphLayout

_cached_layout: GraphLayout | None = None
_cached_graph_id: str | None = None


def _get_or_create_layout(graph: Graph) -> GraphLayout:
    """Get cached layout or create new one if graph changed."""
    global _cached_layout, _cached_graph_id
    from libs.python.terminal.unhinged.graph_layout import (
        calculate_hierarchical_layout,
    )

    if _cached_layout is None or _cached_graph_id != graph.id:
        _cached_layout = calculate_hierarchical_layout(graph)
        _cached_graph_id = graph.id
    return _cached_layout


def _render_graph_mode(state: WorkspaceState, r: Renderer) -> None:
    """Render full graph view with viewport/camera navigation.

    Uses viewport/layout/canvas system without sprites for stability.
    """
    from libs.python.terminal.unhinged.viewport import Viewport

    w = r.fb.width
    h = r.fb.height

    border_style = Style(fg=Color.MAGENTA)
    title_style = Style(fg=Color.MAGENTA).bold()
    dim_style = Style(fg=Color.BRIGHT_BLACK)
    status_style = Style(fg=Color.YELLOW)

    # Draw border
    r.panel(0, 0, w, h - 2, title="[ Graph View ]", style=border_style, title_style=title_style)

    gs = state.graph_state
    if not gs or not state.graph.nodes:
        r.text(2, 2, "No nodes in graph. Press V to go back.", dim_style)
    else:
        # Get or create layout
        layout = _get_or_create_layout(state.graph)

        # Create viewport for the inner area (excluding border and status)
        inner_w = w - 2
        inner_h = h - 5  # Leave room for border, info, help, and status

        # Calculate viewport position - center on layout if first render
        vp_x = gs.viewport_x
        vp_y = gs.viewport_y

        # If no position set, center on graph
        if vp_x == 0 and vp_y == 0 and layout.positions:
            cx, cy = layout.center
            vp_x = cx - inner_w / 2
            vp_y = cy - inner_h / 2

        viewport = Viewport(
            world_x=vp_x,
            world_y=vp_y,
            width=inner_w,
            height=inner_h,
        )

        # Render nodes only (edges disabled for debugging)
        from libs.python.terminal.unhinged.graph_canvas import render_nodes

        render_nodes(
            graph=state.graph,
            layout=layout,
            viewport=viewport,
            r=r,
            selected_node_id=gs.selected_node_id,
            offset_x=1,
            offset_y=3,
        )
        # NOTE: Edges and minimap disabled to isolate crash

        # Show info
        node_count = len(state.graph.nodes)
        edge_count = len(state.graph.edges)
        info = f"Nodes: {node_count}  Edges: {edge_count}"
        if gs.selected_node_id:
            from libs.python.terminal.unhinged.graph_types import get_node

            sel = get_node(state.graph, gs.selected_node_id)
            if sel:
                info += f"  |  Selected: {sel.name}"
        r.text(2, 2, info, dim_style)

    # Help bar
    help_text = "WASD: Pan  |  N/P: Select  |  E: Center  |  V: List  |  Q: Back"
    r.text(1, h - 4, help_text, dim_style)

    # Status bar
    r.panel(0, h - 2, w, 2, style=border_style)
    r.text(2, h - 1, state.status[: w - 4], status_style)


def _render_edit_mode(state: WorkspaceState, r: Renderer) -> None:
    """Render node edit form."""
    w = r.fb.width
    h = r.fb.height

    border_style = Style(fg=Color.GREEN)
    title_style = Style(fg=Color.GREEN).bold()
    selected_style = Style(fg=Color.BLACK, bg=Color.GREEN)
    normal_style = Style(fg=Color.WHITE)
    dim_style = Style(fg=Color.BRIGHT_BLACK)
    input_style = Style(fg=Color.CYAN)
    status_style = Style(fg=Color.YELLOW)

    es = state.edit_state
    from libs.python.terminal.unhinged.graph_types import get_node

    node = get_node(state.graph, es.node_id) if es else None

    title = f"[ Edit: {node.name if node else 'Node'} ]"
    r.panel(0, 0, w, h - 2, title=title, style=border_style, title_style=title_style)

    if not node or not es:
        r.text(2, 2, "No node to edit", dim_style)
    else:
        y = 3
        for i, field in enumerate(es.fields):
            is_sel = i == es.field_index
            prefix = "▶ " if is_sel else "  "

            # Get value - name is on node, description is in config
            if field == "name":
                value = node.name
            elif field == "description":
                value = node.config.get("description", "")
            else:
                value = ""

            if es.input_active and is_sel:
                value = es.input_buffer + "█"
                style = input_style
            else:
                style = selected_style if is_sel else normal_style

            r.text(2, y, f"{prefix}{field.title()}:", dim_style)
            r.text(2 + len(prefix) + len(field) + 2, y, str(value)[: w - 20], style)
            y += 2

    # Help
    r.text(1, h - 4, "W/S: Field  |  E: Edit  |  ESC: Done", dim_style)

    # Status bar
    r.panel(0, h - 2, w, 2, style=border_style)
    r.text(2, h - 1, state.status[: w - 4], status_style)


def _render_connect_mode(state: WorkspaceState, r: Renderer) -> None:
    """Render edge connection mode."""
    w = r.fb.width
    h = r.fb.height

    border_style = Style(fg=Color.YELLOW)
    title_style = Style(fg=Color.YELLOW).bold()
    selected_style = Style(fg=Color.BLACK, bg=Color.YELLOW)
    normal_style = Style(fg=Color.WHITE)
    dim_style = Style(fg=Color.BRIGHT_BLACK)
    status_style = Style(fg=Color.YELLOW)

    cs = state.connect_state
    from libs.python.terminal.unhinged.graph_types import get_node

    source = get_node(state.graph, cs.from_node_id) if cs else None

    title = f"[ Connect from: {source.name if source else '?'} ]"
    r.panel(0, 0, w, h - 2, title=title, style=border_style, title_style=title_style)

    r.text(2, 2, "Select target node:", dim_style)

    y = 4
    for i, node in enumerate(state.graph.nodes):
        if y >= h - 5:
            break
        if cs and node.id == cs.from_node_id:
            continue  # Skip source node

        is_sel = cs and i == cs.target_index
        prefix = "▶ " if is_sel else "  "
        icon = NodeRegistry.get_icon(node.type)
        style = selected_style if is_sel else normal_style
        r.text(2, y, f"{prefix}{icon} {node.name}", style)
        y += 1

    # Help
    r.text(1, h - 4, "W/S: Target  |  E: Connect  |  ESC: Cancel", dim_style)

    # Status bar
    r.panel(0, h - 2, w, 2, style=border_style)
    r.text(2, h - 1, state.status[: w - 4], status_style)


def _render_add_mode(state: WorkspaceState, r: Renderer) -> None:
    """Render add node type selection."""
    w = r.fb.width
    h = r.fb.height

    border_style = Style(fg=Color.GREEN)
    title_style = Style(fg=Color.GREEN).bold()
    selected_style = Style(fg=Color.BLACK, bg=Color.GREEN)
    normal_style = Style(fg=Color.WHITE)
    dim_style = Style(fg=Color.BRIGHT_BLACK)
    status_style = Style(fg=Color.YELLOW)

    r.panel(0, 0, w, h - 2, title="[ Add Node ]", style=border_style, title_style=title_style)

    r.text(2, 2, "Select node type:", dim_style)

    ad = state.add_state
    if ad:
        y = 4
        for i, node_type in enumerate(ad.node_types):
            is_sel = i == ad.type_index
            prefix = "▶ " if is_sel else "  "
            icon = NodeRegistry.get_icon(node_type)
            style = selected_style if is_sel else normal_style
            # node_type is now a NodeType enum
            label = node_type.value.replace("_", " ").title()
            r.text(2, y, f"{prefix}{icon} {label}", style)
            y += 1

    # Help
    r.text(1, h - 4, "W/S: Type  |  E: Create  |  ESC: Cancel", dim_style)

    # Status bar
    r.panel(0, h - 2, w, 2, style=border_style)
    r.text(2, h - 1, state.status[: w - 4], status_style)


def _render_node_detail_mode(state: WorkspaceState, r: Renderer) -> None:
    """Render full-screen node detail view with scrolling."""
    w = r.fb.width
    h = r.fb.height

    # Styles
    border_style = Style(fg=Color.CYAN)
    title_style = Style(fg=Color.CYAN).bold()
    content_style = Style(fg=Color.WHITE)
    dim_style = Style(fg=Color.BRIGHT_BLACK)
    status_style = Style(fg=Color.YELLOW)
    header_style = Style(fg=Color.YELLOW)

    ds = state.node_detail_state
    if not ds:
        return

    # Draw border
    r.panel(0, 0, w, h, style=border_style)

    # Title bar
    node = None
    for n in state.graph.nodes:
        if n.id == ds.node_id:
            node = n
            break
    title = f"Node Details: {node.name if node else ds.node_id}"
    r.text(2, 1, title[: w - 4], title_style)

    # Content area
    content_y_start = 3
    content_h = h - 6  # Leave room for status bar
    content_w = w - 4

    # Scroll indicator
    total_lines = len(ds.content_lines)
    if total_lines > content_h:
        scroll_info = f"[{ds.scroll_offset + 1}-{min(ds.scroll_offset + content_h, total_lines)}/{total_lines}]"
        r.text(w - len(scroll_info) - 2, 1, scroll_info, dim_style)

    # Render visible content lines
    for i in range(content_h):
        line_idx = ds.scroll_offset + i
        if line_idx >= total_lines:
            break
        line = ds.content_lines[line_idx]
        # Highlight section headers
        if line.startswith("───") or line.startswith("═"):
            r.text(2, content_y_start + i, line[:content_w], header_style)
        else:
            r.text(2, content_y_start + i, line[:content_w], content_style)

    # Scroll hints
    if ds.scroll_offset > 0:
        r.text(w - 3, content_y_start, "▲", dim_style)
    if ds.scroll_offset + content_h < total_lines:
        r.text(w - 3, content_y_start + content_h - 1, "▼", dim_style)

    # Status bar
    r.panel(0, h - 2, w, 2, style=border_style)
    r.text(2, h - 1, state.status[: w - 4], status_style)


# =============================================================================
# Entry Point
# =============================================================================


def run_workspace(graph: Graph, read_only: bool = False) -> Graph:
    """Run the graph workspace screen.

    Args:
        graph: The graph to edit/view.
        read_only: If True, start in read-only VIEW mode.

    Returns:
        The (possibly modified) graph.
    """
    # Create initial state
    initial = create_workspace_state(graph, read_only=read_only)

    # Run engine
    engine = Engine()

    final_state = [initial]

    def _update(state: WorkspaceState, event: Event) -> WorkspaceState:
        return update(state, event)

    def _render(state: WorkspaceState, r: Renderer) -> None:
        final_state[0] = state
        render(state, r)

    engine.run(_update, _render, initial)

    return final_state[0].graph


def run_workspace_view(graph: Graph) -> None:
    """Run the graph workspace in read-only view mode.

    Convenience function for viewing graphs without editing.

    Args:
        graph: The graph to view.
    """
    run_workspace(graph, read_only=True)


if __name__ == "__main__":
    # Test with empty graph
    from libs.python.terminal.unhinged.graph_types import create_empty_graph

    test_graph = create_empty_graph("test-123", "Test Graph")
    result = run_workspace(test_graph)
    print(f"Final graph: {result.name} with {len(result.nodes)} nodes")
