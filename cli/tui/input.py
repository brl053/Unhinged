"""Raw keyboard input for TUI.

Provides single-keypress reading without echo or line buffering.
Uses termios for Unix terminal control - this is the primitive level.

This is educational: when you're at frame buffer level, this is all you have.
No frameworks, no abstractions - just terminal modes and file descriptors.
"""

import sys
import termios
import tty
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum, auto


class Key(Enum):
    """Named keys for special key handling."""

    # Navigation
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()

    # Actions
    ENTER = auto()
    ESCAPE = auto()
    TAB = auto()
    BACKSPACE = auto()
    DELETE = auto()

    # Modifiers
    CTRL_C = auto()
    CTRL_D = auto()
    CTRL_Q = auto()
    ALT_C = auto()  # Alt+C for copy

    # Unknowns
    UNKNOWN = auto()


@dataclass
class KeyEvent:
    """Represents a keyboard event.

    For printable characters, `char` is set and `key` is None.
    For special keys, `key` is set and `char` is None.
    """

    char: str | None = None
    key: Key | None = None
    raw: bytes = b""

    @property
    def is_char(self) -> bool:
        """True if this is a printable character."""
        return self.char is not None

    @property
    def is_special(self) -> bool:
        """True if this is a special key."""
        return self.key is not None

    def __repr__(self) -> str:
        if self.char:
            return f"KeyEvent(char={self.char!r})"
        return f"KeyEvent(key={self.key})"


# ANSI escape sequence mappings
_ESCAPE_SEQUENCES: dict[bytes, Key] = {
    b"\x1b[A": Key.UP,
    b"\x1b[B": Key.DOWN,
    b"\x1b[C": Key.RIGHT,
    b"\x1b[D": Key.LEFT,
    b"\x1b[3~": Key.DELETE,
    b"\x1bOA": Key.UP,  # Alternative sequences
    b"\x1bOB": Key.DOWN,
    b"\x1bOC": Key.RIGHT,
    b"\x1bOD": Key.LEFT,
    b"\x1bc": Key.ALT_C,  # Alt+C (ESC + c)
    b"\x1bC": Key.ALT_C,  # Alt+Shift+C
}

# Single byte special keys
_SPECIAL_BYTES: dict[int, Key] = {
    3: Key.CTRL_C,  # ^C
    4: Key.CTRL_D,  # ^D (EOF)
    9: Key.TAB,  # Tab
    10: Key.ENTER,  # Enter (LF)
    13: Key.ENTER,  # Enter (CR)
    17: Key.CTRL_Q,  # ^Q
    27: Key.ESCAPE,  # Escape (alone)
    127: Key.BACKSPACE,  # Backspace
}


@contextmanager
def raw_mode() -> Generator[None, None, None]:
    """Context manager for raw terminal mode.

    Disables:
    - Line buffering (characters available immediately)
    - Echo (typed characters not displayed)
    - Canonical mode (no line editing)

    Restores original settings on exit.

    Usage:
        with raw_mode():
            key = read_key()
    """
    if not sys.stdin.isatty():
        # Not a terminal, can't set raw mode
        yield
        return

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    try:
        tty.setraw(fd)
        yield
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def _read_escape_sequence(first: bytes) -> KeyEvent:
    """Read and parse an escape sequence starting with ESC."""
    import select

    more_bytes = first
    while True:
        ready, _, _ = select.select([sys.stdin], [], [], 0.05)
        if not ready:
            break
        next_byte = sys.stdin.buffer.read(1)
        if not next_byte:
            break
        more_bytes += next_byte
        if more_bytes in _ESCAPE_SEQUENCES:
            return KeyEvent(key=_ESCAPE_SEQUENCES[more_bytes], raw=more_bytes)

    if more_bytes in _ESCAPE_SEQUENCES:
        return KeyEvent(key=_ESCAPE_SEQUENCES[more_bytes], raw=more_bytes)
    if more_bytes == b"\x1b":
        return KeyEvent(key=Key.ESCAPE, raw=more_bytes)
    return KeyEvent(key=Key.UNKNOWN, raw=more_bytes)


def read_key_raw() -> KeyEvent:
    """Read a single key from stdin in raw mode.

    MUST be called within raw_mode() context. Blocks until a key is pressed.
    """
    first = sys.stdin.buffer.read(1)
    if not first:
        return KeyEvent(key=Key.CTRL_D, raw=b"")

    byte_val = first[0]

    if byte_val == 27:  # ESC - escape sequence
        return _read_escape_sequence(first)
    if byte_val in _SPECIAL_BYTES:
        return KeyEvent(key=_SPECIAL_BYTES[byte_val], raw=first)
    if 32 <= byte_val < 127:
        return KeyEvent(char=chr(byte_val), raw=first)
    return KeyEvent(key=Key.UNKNOWN, raw=first)


class KeyboardInput:
    """High-level keyboard input handler.

    Manages raw mode and provides key reading.
    Use as context manager for automatic cleanup.

    Usage:
        with KeyboardInput() as kb:
            while True:
                event = kb.read()
                if event.key == Key.ESCAPE:
                    break
    """

    def __init__(self) -> None:
        self._old_settings: list | None = None
        self._active = False

    def __enter__(self) -> "KeyboardInput":
        self.start()
        return self

    def __exit__(self, *args) -> None:
        self.stop()

    def start(self) -> None:
        """Enter raw mode."""
        if self._active:
            return

        if not sys.stdin.isatty():
            self._active = True
            return

        fd = sys.stdin.fileno()
        self._old_settings = termios.tcgetattr(fd)
        tty.setraw(fd)
        self._active = True

    def stop(self) -> None:
        """Exit raw mode, restore terminal."""
        if not self._active:
            return

        if self._old_settings is not None:
            fd = sys.stdin.fileno()
            termios.tcsetattr(fd, termios.TCSADRAIN, self._old_settings)
            self._old_settings = None

        self._active = False

    def read(self, timeout: float | None = None) -> KeyEvent | None:
        """Read a single key event.

        Args:
            timeout: If None, blocks until a key is pressed.
                    If set, returns None if no key within timeout seconds.

        Returns:
            KeyEvent or None if timeout elapsed.
        """
        if not self._active:
            raise RuntimeError("KeyboardInput not active - use as context manager")

        if timeout is not None:
            import select

            ready, _, _ = select.select([sys.stdin], [], [], timeout)
            if not ready:
                return None

        return read_key_raw()
