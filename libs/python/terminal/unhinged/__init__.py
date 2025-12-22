"""Unhinged TUI - Native terminal renderer implementation.

This is the in-house terminal renderer for Unhinged CLI.
Built from scratch, integrated with CDC event system.

Entry points:
- run_landing(): Session selection screen
- (future) run_main(): Main voice interface

State:
- LandingState: Session selection
- MainState: Voice interface with transcript and CDC timeline
"""

from libs.python.terminal.unhinged.landing import run_landing
from libs.python.terminal.unhinged.main import run_main
from libs.python.terminal.unhinged.state import (
    LandingState,
    MainState,
    Screen,
    TranscriptEntry,
    TranscriptRole,
    VoiceMode,
    create_landing_state,
    create_main_state,
)

__all__ = [
    # Entry points
    "run_landing",
    "run_main",
    # State
    "LandingState",
    "MainState",
    "Screen",
    "TranscriptEntry",
    "TranscriptRole",
    "VoiceMode",
    # Factories
    "create_landing_state",
    "create_main_state",
]
