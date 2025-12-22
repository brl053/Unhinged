"""Table of Contents - Main landing page.

Entry point: run_toc()

Navigation to:
- User Terminal: Daily driver for non-dev tasks
- Sudoers Terminal: Elevated privileges, more formal
- Graphs: Graph management and selection
"""

from libs.python.terminal.cell import Color, Style
from libs.python.terminal.engine import Engine, Event, InputEvent
from libs.python.terminal.renderer import Renderer
from libs.python.terminal.unhinged.state import (
    TOCItem,
    TOCState,
    create_toc_state,
)

# Menu item display configuration
_MENU_ITEMS = {
    TOCItem.USER_TERMINAL: {
        "label": "User Terminal",
        "desc": "Daily driver for everyday tasks",
        "icon": "🖥️ ",
    },
    TOCItem.SUDOERS_TERMINAL: {
        "label": "Sudoers Terminal",
        "desc": "Elevated privileges, formal mode",
        "icon": "🔐",
    },
    TOCItem.GRAPHS: {
        "label": "Graphs",
        "desc": "Manage and run graph workflows",
        "icon": "📊",
    },
    TOCItem.CODEX: {
        "label": "Codex",
        "desc": "Node type reference and documentation",
        "icon": "📖",
    },
}


def update(state: TOCState, event: Event) -> TOCState:
    """Update state based on input event."""
    if event.type == InputEvent.QUIT:
        return state.quit()

    if event.type == InputEvent.NAV_UP:
        return state.nav_up()

    if event.type == InputEvent.NAV_DOWN:
        return state.nav_down()

    if event.type == InputEvent.INTERACT:
        return state.select()

    return state


def render(state: TOCState, r: Renderer) -> None:
    """Render the Table of Contents screen."""
    w = r.fb.width
    h = r.fb.height

    # Styles
    border_style = Style(fg=Color.CYAN)
    title_style = Style(fg=Color.CYAN).bold()
    selected_style = Style(fg=Color.BLACK, bg=Color.CYAN)
    normal_style = Style(fg=Color.WHITE)
    desc_style = Style(fg=Color.BRIGHT_BLACK)
    dim_style = Style(fg=Color.BRIGHT_BLACK)
    status_style = Style(fg=Color.YELLOW)

    # Main frame
    r.panel(0, 0, w, h - 2, title="[ Unhinged ]", style=border_style, title_style=title_style)

    # Header area
    r.text(2, 2, "Table of Contents", title_style)
    r.text(2, 3, "─" * (w - 4), dim_style)

    # Menu items
    menu_y = 5
    items = state.items

    for i, item in enumerate(items):
        config = _MENU_ITEMS[item]
        is_selected = state.selected_index == i
        prefix = "▶ " if is_selected else "  "
        style = selected_style if is_selected else normal_style

        # Icon and label
        label = f"{prefix}{config['icon']} {config['label']}"
        r.text(2, menu_y, label[: w - 4], style)

        # Description on next line (not highlighted)
        if not is_selected:
            r.text(6, menu_y + 1, config["desc"][: w - 8], desc_style)
        else:
            r.text(6, menu_y + 1, config["desc"][: w - 8], dim_style)

        menu_y += 3

    # Help text
    help_y = h - 5
    r.text(2, help_y, "W/S: Navigate  |  E: Select  |  Q: Quit", dim_style)

    # Status bar
    r.panel(0, h - 2, w, 2, style=border_style)
    r.text(2, h - 1, state.status[: w - 4], status_style)


def run_toc() -> TOCItem | None:
    """Run the Table of Contents screen.

    Returns:
        Selected TOCItem, or None if user quit without selection.
    """
    # Initial state
    initial = create_toc_state()

    # Run engine
    engine = Engine()

    def _update(state: TOCState, event: Event) -> TOCState:
        return update(state, event)

    final_state = [initial]  # Use list to capture final state

    def _render(state: TOCState, r: Renderer) -> None:
        final_state[0] = state
        render(state, r)

    engine.run(_update, _render, initial)

    return final_state[0].selected_item


if __name__ == "__main__":
    result = run_toc()
    print(f"Selected: {result}")
