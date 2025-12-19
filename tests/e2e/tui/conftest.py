"""
@llm-type test.e2e.tui.fixtures
@llm-does pytest fixtures for TUI e2e testing with screen capture

TUI Test Fixtures

Provides:
- check_utf8_locale: Session-scoped, auto-use. Fails fast if UTF-8 not set.
- screen_capture: Function-scoped ScreenCapture at 80x24 (VT100 baseline).
- test_console: Rich Console configured for capture (record=True, StringIO).

Usage:
    def test_something(screen_capture):
        screen_capture.feed("Hello")
        snap = screen_capture.snapshot()
        snap.assert_text_at(0, 0, "Hello")
"""

import locale
from io import StringIO

import pytest
from rich.console import Console

from libs.python.tui_testing import ScreenCapture


@pytest.fixture(scope="session", autouse=True)
def check_utf8_locale():
    """
    Ensure UTF-8 locale is set.

    Box-drawing characters (U+2500, U+2502, etc.) require UTF-8.
    Tests will silently fail with wrong locale - fail fast here.
    """
    enc = locale.getpreferredencoding()
    assert "utf" in enc.lower(), f"TUI tests require UTF-8 locale, got {enc}. " "Set LANG=en_US.UTF-8 or equivalent."


@pytest.fixture(scope="function")
def screen_capture():
    """
    ScreenCapture at standard 80x24 dimensions.

    Fixed size for Phase 1 - no resize handling needed.
    For testing different sizes, create separate fixtures.
    """
    return ScreenCapture(width=80, height=24)


@pytest.fixture(scope="function")
def test_console():
    """
    Rich Console configured for output capture.

    Returns (console, buffer) tuple.
    Console writes to buffer; read with buffer.getvalue().

    Usage:
        def test_panel(test_console, screen_capture):
            console, buffer = test_console
            console.print(Panel("Hello"))
            screen_capture.feed(buffer.getvalue())
            snap = screen_capture.snapshot()
    """
    buffer = StringIO()
    console = Console(
        file=buffer,
        force_terminal=True,
        width=80,
        height=24,
        record=True,
        highlight=False,
    )
    return console, buffer
