"""
@llm-type lib.tui_testing.screen_capture
@llm-does Terminal screen capture using pyte for TUI e2e testing

Screen Capture

Uses pyte (VTXXX-compatible terminal emulator) to process ANSI escape
sequences and maintain an in-memory screen buffer. Provides structured
data (ScreenSnapshot) for test assertions.

Architecture:
- pyte.Screen: Maintains 2D buffer of characters with attributes
- pyte.Stream: Processes ANSI sequences, updates Screen
- ScreenCapture: Wraps both, exposes snapshot() for assertions

This is deterministic - no real TTY, no timing issues, pure data.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pyte

# ANSI color index to name mapping (SGR 30-37 / 40-47)
_ANSI_COLORS = [
    "black",
    "red",
    "green",
    "yellow",
    "blue",
    "magenta",
    "cyan",
    "white",
]


def _ansi_color_to_name(color: str | None) -> str:
    """Convert pyte color representation to string name.

    pyte uses string color names like "default", "red", or hex codes.
    This normalizes them for assertion.

    Args:
        color: pyte color string or None

    Returns:
        Normalized color name string
    """
    if color is None or color == "default":
        return "default"
    # pyte already uses string names for basic colors
    if color in _ANSI_COLORS:
        return color
    # Extended colors come as hex strings or color indices
    return str(color)


@dataclass
class ScreenCell:
    """Single terminal cell with character and attributes.

    Represents one character position in the terminal buffer.
    Captures all style information for assertion.
    """

    char: str  # Single character (or empty for unfilled)
    fg: str = "default"  # Foreground color name
    bg: str = "default"  # Background color name
    bold: bool = False
    italic: bool = False
    underline: bool = False
    strikethrough: bool = False
    reverse: bool = False


@dataclass
class ScreenSnapshot:
    """Immutable snapshot of terminal screen state.

    A 2D grid of ScreenCells plus cursor position.
    This is the "frame" you capture and assert against.
    """

    width: int
    height: int
    cells: list[list[ScreenCell]] = field(default_factory=list)
    cursor_x: int = 0
    cursor_y: int = 0

    def get_text(self) -> str:
        """Extract plain text from screen, lines joined by newlines."""
        lines = []
        for row in self.cells:
            line = "".join(cell.char for cell in row).rstrip()
            lines.append(line)
        # Remove trailing empty lines
        while lines and not lines[-1]:
            lines.pop()
        return "\n".join(lines)

    def get_cell(self, x: int, y: int) -> ScreenCell:
        """Get cell at position. Raises IndexError if out of bounds."""
        if y < 0 or y >= len(self.cells):
            raise IndexError(f"Row {y} out of bounds (0-{len(self.cells) - 1})")
        if x < 0 or x >= len(self.cells[y]):
            raise IndexError(f"Column {x} out of bounds (0-{len(self.cells[y]) - 1})")
        return self.cells[y][x]

    def get_region(self, x: int, y: int, w: int, h: int) -> ScreenSnapshot:
        """Extract a rectangular region as a new snapshot."""
        region_cells = []
        for row_idx in range(y, min(y + h, self.height)):
            row = []
            for col_idx in range(x, min(x + w, self.width)):
                row.append(self.cells[row_idx][col_idx])
            region_cells.append(row)
        return ScreenSnapshot(
            width=w,
            height=h,
            cells=region_cells,
            cursor_x=max(0, self.cursor_x - x),
            cursor_y=max(0, self.cursor_y - y),
        )

    def assert_cell(self, x: int, y: int, expected: ScreenCell) -> None:
        """Assert cell at position matches expected."""
        actual = self.get_cell(x, y)
        assert actual == expected, f"Cell mismatch at ({x}, {y}):\n" f"  Expected: {expected}\n" f"  Actual:   {actual}"

    def assert_text_at(self, x: int, y: int, text: str) -> None:
        """Assert text starting at position matches expected."""
        for i, expected_char in enumerate(text):
            actual = self.get_cell(x + i, y)
            assert actual.char == expected_char, (
                f"Text mismatch at ({x + i}, {y}):\n"
                f"  Expected char: {expected_char!r}\n"
                f"  Actual char:   {actual.char!r}"
            )

    def assert_char_at(self, x: int, y: int, char: str) -> None:
        """Assert single character at position."""
        self.assert_text_at(x, y, char)


class ScreenCapture:
    """Terminal screen capture using pyte.

    Feed ANSI output, get structured snapshots for assertion.

    Usage:
        cap = ScreenCapture(80, 24)
        cap.feed("Hello\\x1b[1mBold\\x1b[0m")
        snap = cap.snapshot()
        snap.assert_text_at(0, 0, "Hello")
    """

    def __init__(self, width: int = 80, height: int = 24) -> None:
        """Initialize screen capture.

        Args:
            width: Terminal width in columns (default 80)
            height: Terminal height in rows (default 24)
        """
        self.width = width
        self.height = height
        self._screen = pyte.Screen(width, height)
        self._stream = pyte.Stream(self._screen)

    def feed(self, data: str) -> None:
        """Feed data (with ANSI sequences) to the terminal emulator."""
        self._stream.feed(data)

    def reset(self) -> None:
        """Reset screen to initial state."""
        self._screen.reset()

    def snapshot(self) -> ScreenSnapshot:
        """Capture current screen state as immutable snapshot."""
        cells: list[list[ScreenCell]] = []

        for y in range(self._screen.lines):
            row: list[ScreenCell] = []
            for x in range(self._screen.columns):
                char_data = self._screen.buffer[y][x]
                cell = ScreenCell(
                    char=char_data.data,
                    fg=_ansi_color_to_name(char_data.fg),
                    bg=_ansi_color_to_name(char_data.bg),
                    bold=char_data.bold,
                    italic=char_data.italics,
                    underline=char_data.underscore,
                    strikethrough=char_data.strikethrough,
                    reverse=char_data.reverse,
                )
                row.append(cell)
            cells.append(row)

        return ScreenSnapshot(
            width=self._screen.columns,
            height=self._screen.lines,
            cells=cells,
            cursor_x=self._screen.cursor.x,
            cursor_y=self._screen.cursor.y,
        )
