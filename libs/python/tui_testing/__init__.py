"""
@llm-type lib.tui_testing
@llm-does Terminal screen capture utilities for TUI testing

TUI Testing Library

Provides infrastructure for capturing and asserting terminal output.
Uses pyte for ANSI sequence processing.

Exports:
- ScreenCapture: Feeds ANSI output, produces snapshots
- ScreenSnapshot: 2D grid of cells with metadata
- ScreenCell: Single cell with char, colors, attributes
"""

from libs.python.tui_testing.screen_capture import (
    ScreenCapture,
    ScreenCell,
    ScreenSnapshot,
)

__all__ = [
    "ScreenCapture",
    "ScreenCell",
    "ScreenSnapshot",
]
