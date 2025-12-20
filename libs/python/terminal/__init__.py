"""In-house terminal renderer.

Low-level terminal control without frameworks.
This is the TempleOS path: understand it from bare metal up.

Components:
- Cell: Single character with style
- FrameBuffer: 2D array of cells with dirty tracking
- Terminal: Raw terminal I/O (ANSI, ioctl)
- Renderer: Stateless drawing primitives
"""

from libs.python.terminal.cell import Cell, Style
from libs.python.terminal.framebuffer import FrameBuffer
from libs.python.terminal.renderer import Renderer
from libs.python.terminal.terminal import Terminal

__all__ = [
    "Cell",
    "Style",
    "FrameBuffer",
    "Terminal",
    "Renderer",
]
