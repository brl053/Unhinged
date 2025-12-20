"""FrameBuffer - 2D array of cells with dirty tracking.

This is the core data structure: a grid of characters.
When you call flush(), only changed cells are written to terminal.
"""

from libs.python.terminal.cell import Cell, Style
from libs.python.terminal.terminal import Terminal


class FrameBuffer:
    """2D grid of cells with differential rendering.

    Key insight: don't redraw the whole screen every frame.
    Track what changed, only write diffs.
    """

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height

        # Current frame (what we're drawing to)
        self._cells: list[list[Cell]] = [[Cell.empty() for _ in range(width)] for _ in range(height)]

        # Previous frame (what's on screen)
        self._prev: list[list[Cell]] = [[Cell.empty() for _ in range(width)] for _ in range(height)]

        # Force full redraw on first flush
        self._force_redraw = True

    def resize(self, width: int, height: int) -> None:
        """Resize buffer. Clears content."""
        self.width = width
        self.height = height
        self._cells = [[Cell.empty() for _ in range(width)] for _ in range(height)]
        self._prev = [[Cell.empty() for _ in range(width)] for _ in range(height)]
        self._force_redraw = True

    def clear(self) -> None:
        """Clear buffer to empty cells."""
        empty = Cell.empty()
        for row in self._cells:
            for i in range(len(row)):
                row[i] = empty

    def set_cell(self, x: int, y: int, cell: Cell) -> None:
        """Set a single cell."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self._cells[y][x] = cell

    def get_cell(self, x: int, y: int) -> Cell:
        """Get a single cell."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self._cells[y][x]
        return Cell.empty()

    def put_char(self, x: int, y: int, char: str, style: Style | None = None) -> None:
        """Put a character at position with optional style."""
        self.set_cell(x, y, Cell.from_char(char, style))

    def put_text(self, x: int, y: int, text: str, style: Style | None = None) -> None:
        """Put a string starting at position."""
        for i, char in enumerate(text):
            if x + i >= self.width:
                break
            self.put_char(x + i, y, char, style)

    def fill(self, x: int, y: int, w: int, h: int, char: str = " ", style: Style | None = None) -> None:
        """Fill a rectangle with a character."""
        cell = Cell.from_char(char, style)
        for row in range(y, min(y + h, self.height)):
            for col in range(x, min(x + w, self.width)):
                self._cells[row][col] = cell

    def flush(self, term: Terminal) -> int:
        """Render changes to terminal. Returns number of cells written."""
        cells_written = 0

        for y in range(self.height):
            for x in range(self.width):
                curr = self._cells[y][x]
                prev = self._prev[y][x]

                if self._force_redraw or curr != prev:
                    term.move_cursor(x, y)
                    term.write_styled(curr.char, curr.style)
                    self._prev[y][x] = curr
                    cells_written += 1

        term.flush()
        self._force_redraw = False
        return cells_written

    def force_redraw(self) -> None:
        """Mark entire buffer for redraw on next flush."""
        self._force_redraw = True


def create_framebuffer(term: Terminal) -> FrameBuffer:
    """Create a framebuffer sized to current terminal."""
    size = term.get_size()
    return FrameBuffer(size.width, size.height)
