"""Stateless drawing primitives.

Higher-level operations built on FrameBuffer.
These are your building blocks: boxes, text, borders.
"""

from libs.python.terminal.cell import Style
from libs.python.terminal.framebuffer import FrameBuffer

# ASCII box characters (maximum compatibility)
BOX_ASCII = {
    "tl": "+",  # top-left
    "tr": "+",  # top-right
    "bl": "+",  # bottom-left
    "br": "+",  # bottom-right
    "h": "-",  # horizontal
    "v": "|",  # vertical
}

# Unicode box characters (prettier)
BOX_UNICODE = {
    "tl": "┌",
    "tr": "┐",
    "bl": "└",
    "br": "┘",
    "h": "─",
    "v": "│",
}

# Double line box
BOX_DOUBLE = {
    "tl": "╔",
    "tr": "╗",
    "bl": "╚",
    "br": "╝",
    "h": "═",
    "v": "║",
}


class Renderer:
    """Stateless drawing operations on a FrameBuffer."""

    def __init__(self, fb: FrameBuffer, box_chars: dict | None = None) -> None:
        self.fb = fb
        self.box = box_chars or BOX_ASCII

    def clear(self) -> None:
        """Clear the framebuffer."""
        self.fb.clear()

    def text(self, x: int, y: int, text: str, style: Style | None = None) -> None:
        """Draw text at position."""
        self.fb.put_text(x, y, text, style)

    def char(self, x: int, y: int, char: str, style: Style | None = None) -> None:
        """Draw single character."""
        self.fb.put_char(x, y, char, style)

    def hline(self, x: int, y: int, length: int, style: Style | None = None) -> None:
        """Draw horizontal line."""
        for i in range(length):
            self.fb.put_char(x + i, y, self.box["h"], style)

    def vline(self, x: int, y: int, length: int, style: Style | None = None) -> None:
        """Draw vertical line."""
        for i in range(length):
            self.fb.put_char(x, y + i, self.box["v"], style)

    def box_frame(self, x: int, y: int, w: int, h: int, style: Style | None = None) -> None:
        """Draw a box frame (border only, no fill).

        Args:
            x, y: Top-left corner
            w, h: Width and height (including border)
            style: Border style
        """
        if w < 2 or h < 2:
            return

        # Corners
        self.fb.put_char(x, y, self.box["tl"], style)
        self.fb.put_char(x + w - 1, y, self.box["tr"], style)
        self.fb.put_char(x, y + h - 1, self.box["bl"], style)
        self.fb.put_char(x + w - 1, y + h - 1, self.box["br"], style)

        # Top and bottom edges
        for i in range(1, w - 1):
            self.fb.put_char(x + i, y, self.box["h"], style)
            self.fb.put_char(x + i, y + h - 1, self.box["h"], style)

        # Left and right edges
        for i in range(1, h - 1):
            self.fb.put_char(x, y + i, self.box["v"], style)
            self.fb.put_char(x + w - 1, y + i, self.box["v"], style)

    def fill_rect(self, x: int, y: int, w: int, h: int, char: str = " ", style: Style | None = None) -> None:
        """Fill a rectangle with a character."""
        self.fb.fill(x, y, w, h, char, style)

    def panel(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        title: str = "",
        style: Style | None = None,
        title_style: Style | None = None,
    ) -> None:
        """Draw a panel: box with optional title.

        Interior is cleared (filled with spaces).
        """
        # Draw border
        self.box_frame(x, y, w, h, style)

        # Clear interior
        if w > 2 and h > 2:
            self.fill_rect(x + 1, y + 1, w - 2, h - 2, " ")

        # Title (centered on top border)
        if title and w > 4:
            title_text = f" {title} "
            if len(title_text) > w - 2:
                title_text = title_text[: w - 2]
            tx = x + (w - len(title_text)) // 2
            self.text(tx, y, title_text, title_style or style)

    def text_wrapped(self, x: int, y: int, w: int, h: int, text: str, style: Style | None = None) -> int:
        """Draw text wrapped within a region. Returns lines used."""
        words = text.split()
        lines_used = 0
        line = ""

        for word in words:
            if lines_used >= h:
                break
            if len(line) + len(word) + 1 <= w:
                line = f"{line} {word}".strip()
            else:
                self.text(x, y + lines_used, line[:w], style)
                lines_used += 1
                line = word

        if line and lines_used < h:
            self.text(x, y + lines_used, line[:w], style)
            lines_used += 1

        return lines_used
