"""Cell and Style primitives for terminal rendering.

A Cell is the atomic unit: one character position with styling.
This is what a framebuffer is made of.
"""

from dataclasses import dataclass
from enum import IntEnum


class Color(IntEnum):
    """ANSI 16-color palette.

    0-7: normal colors
    8-15: bright colors
    """

    BLACK = 0
    RED = 1
    GREEN = 2
    YELLOW = 3
    BLUE = 4
    MAGENTA = 5
    CYAN = 6
    WHITE = 7
    # Bright variants (add 8)
    BRIGHT_BLACK = 8
    BRIGHT_RED = 9
    BRIGHT_GREEN = 10
    BRIGHT_YELLOW = 11
    BRIGHT_BLUE = 12
    BRIGHT_MAGENTA = 13
    BRIGHT_CYAN = 14
    BRIGHT_WHITE = 15
    # Default (terminal default)
    DEFAULT = -1


class Attr(IntEnum):
    """Text attributes (bitmask)."""

    NONE = 0
    BOLD = 1
    DIM = 2
    ITALIC = 4
    UNDERLINE = 8
    BLINK = 16
    REVERSE = 32


@dataclass(frozen=True, slots=True)
class Style:
    """Immutable style for a cell."""

    fg: Color = Color.DEFAULT
    bg: Color = Color.DEFAULT
    attrs: int = Attr.NONE  # Bitmask of Attr values

    @classmethod
    def default(cls) -> "Style":
        return cls()

    def with_fg(self, fg: Color) -> "Style":
        return Style(fg=fg, bg=self.bg, attrs=self.attrs)

    def with_bg(self, bg: Color) -> "Style":
        return Style(fg=self.fg, bg=bg, attrs=self.attrs)

    def with_attr(self, attr: Attr) -> "Style":
        return Style(fg=self.fg, bg=self.bg, attrs=self.attrs | attr)

    def bold(self) -> "Style":
        return self.with_attr(Attr.BOLD)

    def dim(self) -> "Style":
        return self.with_attr(Attr.DIM)


@dataclass(frozen=True, slots=True)
class Cell:
    """Single character cell with style.

    Immutable for easy comparison (dirty tracking).
    """

    char: str = " "  # Single character (or space)
    style: Style = Style()

    @classmethod
    def empty(cls) -> "Cell":
        return cls()

    @classmethod
    def from_char(cls, char: str, style: Style | None = None) -> "Cell":
        # Take only first character
        c = char[0] if char else " "
        return cls(char=c, style=style or Style())

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Cell):
            return False
        return self.char == other.char and self.style == other.style
