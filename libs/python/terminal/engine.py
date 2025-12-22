"""Blocking synchronous engine loop.

This is intentionally simple and blocking.
When a node executes, the UI freezes. That's the design.

Later: parallel jobs for UI. But first, understand the basics.
"""

import select
import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Protocol, TypeVar

from libs.python.terminal.framebuffer import FrameBuffer, create_framebuffer
from libs.python.terminal.renderer import Renderer
from libs.python.terminal.terminal import Terminal


class HasRunning(Protocol):
    """Protocol for state objects that have a running flag."""

    @property
    def running(self) -> bool:
        ...


StateT = TypeVar("StateT", bound=HasRunning)


class InputEvent(Enum):
    """Input event types."""

    NONE = auto()
    CHAR = auto()
    ENTER = auto()
    ESCAPE = auto()
    TAB = auto()  # Tab key
    QUIT = auto()  # Ctrl+C or 'q'
    # Navigation (WASD)
    NAV_UP = auto()  # W
    NAV_DOWN = auto()  # S
    NAV_LEFT = auto()  # A
    NAV_RIGHT = auto()  # D
    # Actions
    INTERACT = auto()  # E
    COPY = auto()  # C


@dataclass
class Event:
    """Input event with optional character."""

    type: InputEvent
    char: str = ""


@dataclass
class EngineState:
    """Application state for the engine."""

    running: bool = True
    status: str = "Ready"
    content: list[str] = field(default_factory=list)
    # Extensible: add your own state here


class Engine:
    """Simple blocking engine loop.

    Pattern:
        engine = Engine()
        engine.run(update_fn, render_fn)

    - update_fn(state, event) -> state  # Pure state transition
    - render_fn(state, renderer)         # Draw to framebuffer

    The loop is synchronous and blocking.
    If render_fn calls slow code, the UI freezes. Intentional.
    """

    def __init__(self) -> None:
        self.term = Terminal()
        self.fb: FrameBuffer | None = None
        self.renderer: Renderer | None = None

    def run(
        self,
        update: Callable[[StateT, Event], StateT],
        render: Callable[[StateT, Renderer], None],
        initial_state: StateT,
    ) -> None:
        """Main engine loop. Blocks until state.running is False."""

        state = initial_state

        try:
            # Setup terminal
            self.term.enter_raw_mode()
            self.term.enter_alt_screen()
            self.term.clear()

            # Create framebuffer
            self.fb = create_framebuffer(self.term)
            self.renderer = Renderer(self.fb)

            # Initial render
            render(state, self.renderer)
            self.fb.flush(self.term)

            # Main loop
            while state.running:
                # 1. Read input (with timeout for responsive feel)
                event = self._read_event(timeout=0.1)

                # 2. Update state
                if event.type != InputEvent.NONE:
                    state = update(state, event)

                # 3. Render (blocks if slow)
                self.renderer.clear()
                render(state, self.renderer)
                self.fb.flush(self.term)

        finally:
            # Cleanup
            self.term.exit_alt_screen()
            self.term.exit_raw_mode()

    def _read_event(self, timeout: float = 0.1) -> Event:
        """Read input event with timeout."""
        ready, _, _ = select.select([sys.stdin], [], [], timeout)
        if not ready:
            return Event(type=InputEvent.NONE)

        char = sys.stdin.read(1)
        if not char:
            return Event(type=InputEvent.NONE)

        return self._parse_char(char)

    def _parse_char(self, char: str) -> Event:
        """Parse a character into an input event."""
        byte_val = ord(char)

        # Check control characters first
        if byte_val == 3:  # Ctrl+C
            return Event(type=InputEvent.QUIT)
        if byte_val in (10, 13):  # Enter
            return Event(type=InputEvent.ENTER)
        if byte_val == 27:  # Escape
            return Event(type=InputEvent.ESCAPE)

        # Use lookup table for key mappings
        key_map = {
            "q": InputEvent.QUIT,
            "w": InputEvent.NAV_UP,
            "s": InputEvent.NAV_DOWN,
            "a": InputEvent.NAV_LEFT,
            "d": InputEvent.NAV_RIGHT,
            "e": InputEvent.INTERACT,
            "c": InputEvent.COPY,
        }
        event_type = key_map.get(char.lower())
        if event_type is not None:
            return Event(type=event_type)

        # Regular printable character
        if 32 <= byte_val < 127:
            return Event(type=InputEvent.CHAR, char=char)

        return Event(type=InputEvent.NONE)
