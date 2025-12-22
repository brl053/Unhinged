"""Graphs screen - Graph selection and management.

Entry point: run_graphs()

Features:
- Create new graph
- Text input for name/description
- List of 10 most recent graphs
"""

from libs.python.terminal.cell import Color, Style
from libs.python.terminal.engine import Engine, Event, InputEvent
from libs.python.terminal.renderer import Renderer
from libs.python.terminal.unhinged.state import (
    GraphSlot,
    GraphsState,
    create_graphs_state,
)

# Lazy imports
_doc_store = None


def _get_document_store():
    """Lazy load document store."""
    global _doc_store
    if _doc_store is None:
        from libs.python.persistence import get_document_store

        _doc_store = get_document_store()
    return _doc_store


def _load_graphs(limit: int = 10) -> list[GraphSlot]:
    """Load recent graphs from document store."""
    try:
        store = _get_document_store()
        docs = store.query("graphs", limit=limit)
        return [
            GraphSlot(
                graph_id=doc.id,
                name=doc.data.get("name", "Untitled"),
                description=doc.data.get("description", ""),
                updated_at=doc.updated_at.strftime("%Y-%m-%d %H:%M"),
                node_count=doc.data.get("node_count", 0),
            )
            for doc in docs
        ]
    except Exception:
        return []


def _create_empty_graph(name: str, description: str = "") -> str | None:
    """Create an empty graph in the document store."""
    try:
        import json

        store = _get_document_store()
        graph_def = {
            "name": name or "Untitled Graph",
            "description": description,
            "tags": [],
            "nodes": [],
            "edges": [],
            "version": "1.0",
        }
        doc = store.create(
            "graphs",
            {
                "name": graph_def["name"],
                "description": description,
                "tags": [],
                "content": json.dumps(graph_def, indent=2),
                "encoding": "json",
                "node_count": 0,
                "edge_count": 0,
            },
        )
        return doc.id
    except Exception:
        return None


def update(state: GraphsState, event: Event) -> GraphsState:
    """Update state based on input event."""
    # Handle text input mode
    if state.input_focused:
        if event.type == InputEvent.ESCAPE:
            return state.unfocus_input()
        if event.type == InputEvent.ENTER:
            return state.unfocus_input()
        if event.type == InputEvent.CHAR:
            return state.append_char(event.char)
        # Backspace (typically sent as specific char or handled separately)
        if event.char == "\x7f" or event.char == "\b":
            return state.backspace()
        return state

    # Normal navigation mode
    if event.type == InputEvent.QUIT:
        return state.quit()

    if event.type == InputEvent.NAV_UP:
        return state.nav_up()

    if event.type == InputEvent.NAV_DOWN:
        return state.nav_down()

    if event.type == InputEvent.INTERACT:
        # E key: focus input if on input row, otherwise select
        if state.selected_index == 1:
            return state.focus_input()
        return state.select()

    return state


def render(state: GraphsState, r: Renderer) -> None:
    """Render the Graphs screen."""
    w = r.fb.width
    h = r.fb.height

    # Styles
    border_style = Style(fg=Color.MAGENTA)
    title_style = Style(fg=Color.MAGENTA).bold()
    selected_style = Style(fg=Color.BLACK, bg=Color.MAGENTA)
    normal_style = Style(fg=Color.WHITE)
    dim_style = Style(fg=Color.BRIGHT_BLACK)
    status_style = Style(fg=Color.YELLOW)
    input_style = Style(fg=Color.CYAN)
    input_focused_style = Style(fg=Color.BLACK, bg=Color.CYAN)

    # Main frame
    r.panel(0, 0, w, h - 2, title="[ Graphs ]", style=border_style, title_style=title_style)

    # Header
    r.text(2, 2, "Graph Management", title_style)
    r.text(2, 3, "─" * (w - 4), dim_style)

    menu_y = 5

    # Option 0: Create Graph
    is_sel = state.selected_index == 0
    prefix = "▶ " if is_sel else "  "
    style = selected_style if is_sel else normal_style
    r.text(2, menu_y, f"{prefix}[+] Create New Graph", style)
    menu_y += 2

    # Option 1: Text Input for name
    is_sel = state.selected_index == 1
    prefix = "▶ " if is_sel else "  "
    label = "Name: "
    if state.input_focused:
        input_display = state.input_text + "█"
        r.text(2, menu_y, f"{prefix}{label}", input_focused_style)
        r.text(2 + len(prefix) + len(label), menu_y, input_display[: w - 12], input_focused_style)
    else:
        style = selected_style if is_sel else input_style
        input_display = state.input_text if state.input_text else "(press TAB to type)"
        r.text(2, menu_y, f"{prefix}{label}{input_display}"[: w - 4], style)
    menu_y += 2

    # Separator
    r.text(2, menu_y, "─" * (w - 4), dim_style)
    r.text(2, menu_y + 1, "Recent Graphs:", dim_style)
    menu_y += 3

    # Graph list
    for i, graph in enumerate(state.graphs):
        if menu_y >= h - 5:
            break
        idx = i + 2  # Offset for Create and Input
        is_sel = state.selected_index == idx
        prefix = "▶ " if is_sel else "  "
        style = selected_style if is_sel else normal_style

        # Graph name and info
        name = graph.name[:30]
        nodes = f"({graph.node_count} nodes)"
        label = f"{prefix}[{i+1}] {name}  {nodes}  {graph.updated_at}"
        r.text(2, menu_y, label[: w - 4], style)

        # Description on next line
        if graph.description and not is_sel:
            r.text(8, menu_y + 1, graph.description[: w - 12], dim_style)
            menu_y += 2
        else:
            menu_y += 1

    if not state.graphs:
        r.text(4, menu_y, "No graphs found. Create one to get started.", dim_style)

    # Help text
    help_y = h - 5
    if state.input_focused:
        r.text(2, help_y, "Type to enter name  |  ENTER/ESC: Done", dim_style)
    else:
        r.text(2, help_y, "W/S: Navigate  |  E: Select/Edit  |  Q: Back", dim_style)

    # Status bar
    r.panel(0, h - 2, w, 2, style=border_style)
    r.text(2, h - 1, state.status[: w - 4], status_style)


def run_graphs() -> tuple[str | None, bool]:
    """Run the Graphs screen.

    Returns:
        Tuple of (graph_id, create_new):
        - (graph_id, False) if a graph was selected
        - (None, True) if user chose to create new graph
        - (None, False) if user quit/back
    """
    # Load graphs
    graphs = _load_graphs(limit=10)

    # Initial state
    initial = create_graphs_state(graphs=graphs)

    # Run engine
    engine = Engine()

    def _update(state: GraphsState, event: Event) -> GraphsState:
        return update(state, event)

    final_state = [initial]

    def _render(state: GraphsState, r: Renderer) -> None:
        final_state[0] = state
        render(state, r)

    engine.run(_update, _render, initial)

    state = final_state[0]

    # Handle create new
    if state.create_new:
        name = state.input_text or "Untitled Graph"
        graph_id = _create_empty_graph(name)
        return (graph_id, True)

    return (state.selected_graph_id, False)


if __name__ == "__main__":
    result = run_graphs()
    print(f"Result: {result}")
