"""Raw terminal I/O.

Direct ANSI escape sequences and ioctl calls.
No abstractions - this is what Rich hides from you.
"""

import fcntl
import os
import struct
import sys
import termios
import tty
from dataclasses import dataclass

from libs.python.terminal.cell import Attr, Color, Style


@dataclass
class TerminalSize:
    """Terminal dimensions."""

    width: int
    height: int


class Terminal:
    """Raw terminal control.

    Provides:
    - Size detection (ioctl TIOCGWINSZ)
    - Raw mode (no echo, no line buffering)
    - Cursor control
    - ANSI escape sequence output
    - Alternate screen buffer
    """

    def __init__(self, fd: int | None = None) -> None:
        self.fd = fd if fd is not None else sys.stdout.fileno()
        self._old_settings: list | None = None
        self._in_raw_mode = False
        self._in_alt_screen = False

    # === Size ===

    def get_size(self) -> TerminalSize:
        """Get terminal size via ioctl."""
        try:
            result = fcntl.ioctl(self.fd, termios.TIOCGWINSZ, b"\x00" * 8)
            rows, cols, _, _ = struct.unpack("HHHH", result)
            return TerminalSize(width=cols, height=rows)
        except (OSError, struct.error):
            # Fallback
            return TerminalSize(width=80, height=24)

    # === Raw Mode ===

    def enter_raw_mode(self) -> None:
        """Enter raw mode (no echo, immediate input)."""
        if self._in_raw_mode:
            return
        if not os.isatty(sys.stdin.fileno()):
            return
        self._old_settings = termios.tcgetattr(sys.stdin.fileno())
        tty.setraw(sys.stdin.fileno())
        self._in_raw_mode = True

    def exit_raw_mode(self) -> None:
        """Restore terminal settings."""
        if not self._in_raw_mode or self._old_settings is None:
            return
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, self._old_settings)
        self._in_raw_mode = False

    # === Alternate Screen ===

    def enter_alt_screen(self) -> None:
        """Switch to alternate screen buffer."""
        if self._in_alt_screen:
            return
        self._write("\x1b[?1049h")  # Enter alt screen
        self._write("\x1b[?25l")  # Hide cursor
        self._in_alt_screen = True

    def exit_alt_screen(self) -> None:
        """Return to main screen buffer."""
        if not self._in_alt_screen:
            return
        self._write("\x1b[?25h")  # Show cursor
        self._write("\x1b[?1049l")  # Exit alt screen
        self._in_alt_screen = False

    # === Cursor ===

    def move_cursor(self, x: int, y: int) -> None:
        """Move cursor to position (0-indexed)."""
        # ANSI is 1-indexed
        self._write(f"\x1b[{y + 1};{x + 1}H")

    def hide_cursor(self) -> None:
        self._write("\x1b[?25l")

    def show_cursor(self) -> None:
        self._write("\x1b[?25h")

    # === Output ===

    def clear(self) -> None:
        """Clear entire screen."""
        self._write("\x1b[2J")
        self.move_cursor(0, 0)

    def write_styled(self, text: str, style: Style) -> None:
        """Write text with ANSI styling at current cursor position."""
        self._write(self._style_to_ansi(style))
        self._write(text)
        self._write("\x1b[0m")  # Reset

    def flush(self) -> None:
        """Flush output buffer."""
        os.write(self.fd, b"")  # Force flush
        sys.stdout.flush()

    # === Internal ===

    def _write(self, data: str) -> None:
        """Write raw string to terminal."""
        sys.stdout.write(data)

    def _style_to_ansi(self, style: Style) -> str:
        """Convert Style to ANSI escape sequence."""
        codes: list[str] = []
        self._add_attr_codes(codes, style.attrs)
        self._add_color_codes(codes, style.fg, style.bg)

        if not codes:
            return ""
        return f"\x1b[{';'.join(codes)}m"

    def _add_attr_codes(self, codes: list[str], attrs: int) -> None:
        """Add attribute codes to the list."""
        attr_map = [(Attr.BOLD, "1"), (Attr.DIM, "2"), (Attr.ITALIC, "3"), (Attr.UNDERLINE, "4"), (Attr.REVERSE, "7")]
        for attr, code in attr_map:
            if attrs & attr:
                codes.append(code)

    def _add_color_codes(self, codes: list[str], fg: Color, bg: Color) -> None:
        """Add foreground and background color codes."""
        # Foreground (30-37 normal, 90-97 bright)
        if fg != Color.DEFAULT:
            base = 30 if fg < 8 else 82  # 90 - 8 = 82
            codes.append(str(base + fg))
        # Background (40-47 normal, 100-107 bright)
        if bg != Color.DEFAULT:
            base = 40 if bg < 8 else 92  # 100 - 8 = 92
            codes.append(str(base + bg))
