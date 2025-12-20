#!/usr/bin/env python3
"""Demo of the in-house terminal renderer.

Run with:
    python -m libs.python.terminal.demo

Press 'q' or Ctrl+C to quit.
Press Enter to simulate a blocking node execution.
Type characters to add to the buffer.
"""

import time

from libs.python.terminal.cell import Color, Style
from libs.python.terminal.engine import Engine, EngineState, Event, InputEvent
from libs.python.terminal.renderer import Renderer


def update(state: EngineState, event: Event) -> EngineState:
    """Pure state transition function."""

    if event.type == InputEvent.QUIT:
        return EngineState(running=False, status="Goodbye!", content=state.content)

    if event.type == InputEvent.ENTER:
        # Simulate blocking node execution
        # UI will freeze during this - INTENTIONAL
        return EngineState(
            running=True,
            status="Executing node... (blocking for 2 seconds)",
            content=state.content + ["[Node executed - UI was frozen]"],
        )

    if event.type == InputEvent.CHAR:
        return EngineState(
            running=True,
            status=f"Last key: '{event.char}'",
            content=state.content,
        )

    return state


def render(state: EngineState, r: Renderer) -> None:
    """Render current state to framebuffer."""

    w = r.fb.width
    h = r.fb.height

    # Main frame
    title_style = Style(fg=Color.CYAN)
    border_style = Style(fg=Color.WHITE)

    r.panel(0, 0, w, h - 2, title="[ Unhinged Engine Demo ]", style=border_style, title_style=title_style)

    # Status bar
    status_style = Style(fg=Color.YELLOW)
    r.panel(0, h - 2, w, 2, style=border_style)
    r.text(2, h - 1, state.status[: w - 4], status_style)

    # Instructions
    dim_style = Style(fg=Color.BRIGHT_BLACK)
    r.text(2, 2, "Press 'q' to quit | Enter to execute (blocks UI) | Type to add text", dim_style)

    # Content area
    content_style = Style(fg=Color.GREEN)
    for i, line in enumerate(state.content[-10:]):  # Last 10 lines
        r.text(2, 4 + i, line[: w - 4], content_style)

    # If we're about to execute a node, do the blocking work here
    # This happens DURING render - UI is frozen
    if "Executing node" in state.status:
        _simulate_slow_node()


def _simulate_slow_node() -> None:
    """Simulate a slow blocking operation.

    This is where API calls, graph execution, etc. would go.
    The UI is frozen during this. INTENTIONAL.
    """
    time.sleep(2)  # Simulate 2 second API call


def main() -> None:
    """Run the demo."""
    engine = Engine()

    initial = EngineState(
        running=True,
        status="Ready - Press Enter to see blocking execution",
        content=["Welcome to the in-house terminal renderer!"],
    )

    engine.run(update, render, initial)


if __name__ == "__main__":
    main()
