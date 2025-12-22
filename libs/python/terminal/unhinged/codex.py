"""Codex screen - Node type reference and documentation.

Entry point: run_codex()

Features:
- Browse all node types by category
- View detailed documentation for each node
- Configuration options, inputs, outputs
"""

from libs.python.graph.node_codex import (
    NodeCategory,
    NodeCodexEntry,
    get_by_category,
    render_entry_text,
)
from libs.python.terminal.cell import Color, Style
from libs.python.terminal.engine import Engine, Event, InputEvent
from libs.python.terminal.renderer import Renderer

# Category display order and colors
_CATEGORY_CONFIG = {
    NodeCategory.GENERATION: {"label": "Generation", "color": Color.GREEN},
    NodeCategory.ANALYSIS: {"label": "Analysis", "color": Color.YELLOW},
    NodeCategory.CONTROL_FLOW: {"label": "Control Flow", "color": Color.MAGENTA},
    NodeCategory.IO: {"label": "I/O", "color": Color.CYAN},
    NodeCategory.MEMORY: {"label": "Memory", "color": Color.BLUE},
}


class CodexState:
    """State for Codex browser."""

    def __init__(self) -> None:
        # Order entries by category to match visual display
        self.entries: list[NodeCodexEntry] = []
        for cat in NodeCategory:
            self.entries.extend(get_by_category(cat))
        self.selected_index: int = 0
        self.scroll_offset: int = 0
        self.detail_scroll: int = 0
        self.running: bool = True
        self.status: str = "W/S: Navigate  |  A/D: Scroll details  |  Q: Back"

    @property
    def selected_entry(self) -> NodeCodexEntry | None:
        if 0 <= self.selected_index < len(self.entries):
            return self.entries[self.selected_index]
        return None

    def nav_up(self) -> "CodexState":
        if self.selected_index > 0:
            self.selected_index -= 1
            self.detail_scroll = 0
            # Adjust scroll offset to keep selection visible
            if self.selected_index < self.scroll_offset:
                self.scroll_offset = self.selected_index
        return self

    def nav_down(self) -> "CodexState":
        if self.selected_index < len(self.entries) - 1:
            self.selected_index += 1
            self.detail_scroll = 0
        return self

    def scroll_detail_up(self) -> "CodexState":
        if self.detail_scroll > 0:
            self.detail_scroll -= 1
        return self

    def scroll_detail_down(self) -> "CodexState":
        self.detail_scroll += 1
        return self

    def quit(self) -> "CodexState":
        self.running = False
        return self


def update(state: CodexState, event: Event) -> CodexState:
    """Update state based on input event."""
    if event.type == InputEvent.QUIT:
        return state.quit()
    if event.type == InputEvent.NAV_UP:
        return state.nav_up()
    if event.type == InputEvent.NAV_DOWN:
        return state.nav_down()
    if event.type == InputEvent.NAV_LEFT:
        return state.scroll_detail_up()
    if event.type == InputEvent.NAV_RIGHT:
        return state.scroll_detail_down()
    return state


def render(state: CodexState, r: Renderer) -> None:
    """Render the Codex screen."""
    w = r.fb.width
    h = r.fb.height

    # Styles
    border_style = Style(fg=Color.BLUE)
    title_style = Style(fg=Color.BLUE).bold()
    selected_style = Style(fg=Color.BLACK, bg=Color.BLUE)
    normal_style = Style(fg=Color.WHITE)
    dim_style = Style(fg=Color.BRIGHT_BLACK)
    status_style = Style(fg=Color.YELLOW)

    # Main frame
    r.panel(0, 0, w, h - 2, title="[ Node Codex ]", style=border_style, title_style=title_style)

    # Split layout: left list, right details
    list_width = min(28, w // 3)
    detail_start = list_width + 1

    # Header
    r.text(2, 2, "Node Types", title_style)
    r.text(detail_start + 1, 2, "Details", title_style)

    # Vertical separator
    for y in range(3, h - 3):
        r.text(list_width, y, "│", dim_style)

    # Left: Node list by category
    # entries in state are already ordered by category
    list_y = 4
    entry_idx = 0
    current_cat: NodeCategory | None = None

    for entry in state.entries:
        # Category header when category changes
        if entry.category != current_cat:
            current_cat = entry.category
            if list_y > 4:
                list_y += 1  # Gap before new category
            if list_y < h - 4:
                cat_cfg = _CATEGORY_CONFIG.get(current_cat, {"label": current_cat.value, "color": Color.WHITE})
                cat_style = Style(fg=cat_cfg["color"])
                r.text(2, list_y, f"─ {cat_cfg['label']} ─", cat_style)
                list_y += 1

        if list_y >= h - 4:
            entry_idx += 1
            continue

        is_sel = state.selected_index == entry_idx
        prefix = "▶" if is_sel else " "
        style = selected_style if is_sel else normal_style
        label = f"{prefix}{entry.icon} {entry.name}"
        r.text(2, list_y, label[: list_width - 3], style)
        list_y += 1
        entry_idx += 1

    # Right: Selected entry details
    entry = state.selected_entry
    if entry:
        detail_lines = render_entry_text(entry, width=w - detail_start - 3)
        detail_y = 4
        max_lines = h - 7

        # Apply scroll
        start = state.detail_scroll
        visible_lines = detail_lines[start : start + max_lines]

        for line in visible_lines:
            if detail_y >= h - 3:
                break
            r.text(detail_start + 1, detail_y, line[: w - detail_start - 3], normal_style)
            detail_y += 1

        # Scroll indicator
        if len(detail_lines) > max_lines:
            scroll_info = f"[{start + 1}-{min(start + max_lines, len(detail_lines))}/{len(detail_lines)}]"
            r.text(w - len(scroll_info) - 2, h - 4, scroll_info, dim_style)

    # Status bar
    r.panel(0, h - 2, w, 2, style=border_style)
    r.text(2, h - 1, state.status[: w - 4], status_style)


def run_codex() -> None:
    """Run the Codex browser screen.

    Returns when user presses Q to go back.
    """
    initial = CodexState()
    engine = Engine()

    def _update(state: CodexState, event: Event) -> CodexState:
        return update(state, event)

    def _render(state: CodexState, r: Renderer) -> None:
        render(state, r)

    engine.run(_update, _render, initial)


if __name__ == "__main__":
    run_codex()
