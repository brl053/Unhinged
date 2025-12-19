"""
@llm-type test.e2e.tui
@llm-does TUI end-to-end testing with terminal screen buffer capture

TUI E2E Test Package

Tests terminal rendering at the screen buffer level using pyte.
Captures character cells, styles, and cursor position for assertion.

Philosophy:
- Deterministic: No real TTY, no timing issues
- Pure data: ScreenSnapshot is just dataclasses, fully assertable
- Frame buffer level: Every cell has char + fg + bg + attributes
- Maestro-like: Declarative assertions on screen state

Key concepts:
- ScreenCapture wraps pyte for ANSI sequence processing
- ScreenSnapshot is the "frame" - 2D grid of ScreenCells
- Tests feed Rich output to ScreenCapture and assert on snapshot

Fixtures:
- screen_capture: 80x24 ScreenCapture instance
- test_console: Rich Console configured for capture
"""
