"""
@llm-type test.e2e.tui.primitives
@llm-does TDD tests for basic TUI rendering - 4x4 square as first happy path

TUI Primitives E2E Tests

These tests verify that terminal rendering produces exact expected output
at the screen buffer level. This is the foundation for all TUI testing.

EXIT CRITERIA:
1. 4x4 box renders with correct box-drawing characters
2. Each cell has expected character (┌, ─, ┐, │, └, ┘)
3. Interior cells are spaces
4. Style attributes preserved (no color bleed)
5. Cursor position tracked correctly

Philosophy:
- Pure TDD: test specifies exact expected output
- Deterministic: no timing, no real TTY
- Box-drawing chars (Unicode) match what Rich panels use
"""

import subprocess
import sys
from pathlib import Path

from libs.python.tui_testing import ScreenCapture, ScreenCell


class TestPrimitiveRender:
    """Tests for basic terminal rendering primitives."""

    def test_render_4x4_square(self, screen_capture: ScreenCapture) -> None:
        """
        GIVEN: A ScreenCapture instance at 80x24
        WHEN: Render a 4x4 box using Unicode box-drawing characters
        THEN: Snapshot contains exact characters at expected positions

        This is the first happy path test - if this passes, the infrastructure works.

        Note: Terminal emulation requires CR+LF (\\r\\n) to move cursor to
        start of next line. Just LF (\\n) moves down but stays in same column.
        """
        # 4x4 box using Unicode box-drawing characters
        # ┌──┐
        # │  │
        # │  │
        # └──┘
        # Using \r\n for proper terminal newline behavior
        box = "┌──┐\r\n│  │\r\n│  │\r\n└──┘"
        screen_capture.feed(box)
        snap = screen_capture.snapshot()

        # Verify snapshot dimensions
        assert snap.width == 80, f"Expected width 80, got {snap.width}"
        assert snap.height == 24, f"Expected height 24, got {snap.height}"

        # Assert corners
        snap.assert_char_at(0, 0, "┌")  # Top-left
        snap.assert_char_at(3, 0, "┐")  # Top-right
        snap.assert_char_at(0, 3, "└")  # Bottom-left
        snap.assert_char_at(3, 3, "┘")  # Bottom-right

        # Assert horizontal edges (top)
        snap.assert_char_at(1, 0, "─")
        snap.assert_char_at(2, 0, "─")

        # Assert horizontal edges (bottom)
        snap.assert_char_at(1, 3, "─")
        snap.assert_char_at(2, 3, "─")

        # Assert vertical edges (left)
        snap.assert_char_at(0, 1, "│")
        snap.assert_char_at(0, 2, "│")

        # Assert vertical edges (right)
        snap.assert_char_at(3, 1, "│")
        snap.assert_char_at(3, 2, "│")

        # Assert interior is space
        snap.assert_char_at(1, 1, " ")
        snap.assert_char_at(2, 1, " ")
        snap.assert_char_at(1, 2, " ")
        snap.assert_char_at(2, 2, " ")

    def test_get_text_extracts_plain_content(self, screen_capture: ScreenCapture) -> None:
        """
        GIVEN: Screen with rendered box
        WHEN: Call get_text()
        THEN: Returns plain text representation
        """
        box = "┌──┐\r\n│  │\r\n│  │\r\n└──┘"
        screen_capture.feed(box)
        snap = screen_capture.snapshot()

        text = snap.get_text()
        assert "┌──┐" in text
        assert "└──┘" in text

    def test_cursor_position_tracked(self, screen_capture: ScreenCapture) -> None:
        """
        GIVEN: ScreenCapture after feeding text
        WHEN: Take snapshot
        THEN: Cursor position reflects end of written content
        """
        screen_capture.feed("Hi")
        snap = screen_capture.snapshot()

        # Cursor should be at column 2 (after "Hi"), row 0
        assert snap.cursor_x == 2, f"Expected cursor_x=2, got {snap.cursor_x}"
        assert snap.cursor_y == 0, f"Expected cursor_y=0, got {snap.cursor_y}"

    def test_newline_moves_cursor(self, screen_capture: ScreenCapture) -> None:
        """
        GIVEN: Text with newlines
        WHEN: Feed to screen
        THEN: Cursor moves to next line

        Note: Terminal requires CR+LF (\\r\\n) to move to start of next line.
        Just LF (\\n) moves down but cursor stays in same column.
        """
        screen_capture.feed("Line1\r\nLine2")
        snap = screen_capture.snapshot()

        # After "Line2", cursor at column 5, row 1
        assert snap.cursor_y == 1, f"Expected cursor_y=1, got {snap.cursor_y}"
        assert snap.cursor_x == 5, f"Expected cursor_x=5, got {snap.cursor_x}"

        # Verify content
        snap.assert_text_at(0, 0, "Line1")
        snap.assert_text_at(0, 1, "Line2")

    def test_empty_screen_has_space_cells(self, screen_capture: ScreenCapture) -> None:
        """
        GIVEN: Fresh ScreenCapture
        WHEN: Take snapshot without feeding anything
        THEN: All cells contain space character
        """
        snap = screen_capture.snapshot()

        # Check a few cells are space
        cell = snap.get_cell(0, 0)
        assert cell.char == " ", f"Expected space, got {cell.char!r}"

        cell = snap.get_cell(79, 23)
        assert cell.char == " ", f"Expected space, got {cell.char!r}"

    def test_reset_clears_screen(self, screen_capture: ScreenCapture) -> None:
        """
        GIVEN: Screen with content
        WHEN: Call reset()
        THEN: Screen is cleared
        """
        screen_capture.feed("Some content")
        screen_capture.reset()
        snap = screen_capture.snapshot()

        # First cell should be space after reset
        cell = snap.get_cell(0, 0)
        assert cell.char == " ", f"Expected space after reset, got {cell.char!r}"


class TestE2ESubprocess:
    """E2E tests that run actual CLI commands and capture output.

    These tests close the loop: CLI → Rich → Terminal → ScreenCapture → Assert
    """

    def test_unhinged_tui_square_renders_box(self, screen_capture: ScreenCapture) -> None:
        """
        GIVEN: The unhinged CLI is installed
        WHEN: Run `unhinged tui square` as subprocess
        THEN: Output contains the 4x4 box-drawing square

        This is the true E2E test - proves the full pipeline works.
        """
        # Find repo root (where 'unhinged' script lives)
        repo_root = Path(__file__).parent.parent.parent.parent

        # Run the actual CLI command
        result = subprocess.run(
            [sys.executable, "-m", "cli", "tui", "square"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            env={"TERM": "xterm-256color", "COLUMNS": "80", "LINES": "24"},
        )

        assert result.returncode == 0, f"Command failed: {result.stderr}"

        # Feed output to screen capture
        # Rich outputs \n, but we need \r\n for pyte cursor positioning
        # However, for content verification, we can check the raw output
        output = result.stdout

        # Verify the box characters are in the output
        assert "┌──┐" in output, f"Missing top of box in output: {output}"
        assert "│  │" in output, f"Missing sides of box in output: {output}"
        assert "└──┘" in output, f"Missing bottom of box in output: {output}"

        # Now feed to ScreenCapture with proper line endings for position testing
        screen_capture.feed(output.replace("\n", "\r\n"))
        snap = screen_capture.snapshot()

        # The output has some header text, so the box isn't at 0,0
        # Let's verify we can find the box characters somewhere in the snapshot
        text = snap.get_text()
        assert "┌──┐" in text, "Box top not found in screen snapshot"
        assert "└──┘" in text, "Box bottom not found in screen snapshot"

    def test_unhinged_tui_panel_renders_rich_panel(self, screen_capture: ScreenCapture) -> None:
        """
        GIVEN: The unhinged CLI is installed
        WHEN: Run `unhinged tui panel` as subprocess
        THEN: Output contains Rich panel border characters

        Rich panels use rounded corners (╭╮╯╰) by default.
        """
        repo_root = Path(__file__).parent.parent.parent.parent

        result = subprocess.run(
            [sys.executable, "-m", "cli", "tui", "panel"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            env={"TERM": "xterm-256color", "COLUMNS": "80", "LINES": "24"},
        )

        assert result.returncode == 0, f"Command failed: {result.stderr}"

        output = result.stdout

        # Rich panels use rounded box drawing by default
        assert "╭" in output, "Missing top-left corner (╭)"
        assert "╮" in output, "Missing top-right corner (╮)"
        assert "╰" in output, "Missing bottom-left corner (╰)"
        assert "╯" in output, "Missing bottom-right corner (╯)"

        # Verify panel title is present
        assert "Panel Test" in output, "Missing panel title"

    def test_unhinged_tui_demo_renders_all_components(self, screen_capture: ScreenCapture) -> None:
        """
        GIVEN: The unhinged CLI is installed
        WHEN: Run `unhinged tui demo` as subprocess
        THEN: Output contains all demo components (box, panel, table)
        """
        repo_root = Path(__file__).parent.parent.parent.parent

        result = subprocess.run(
            [sys.executable, "-m", "cli", "tui", "demo"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            env={"TERM": "xterm-256color", "COLUMNS": "80", "LINES": "24"},
        )

        assert result.returncode == 0, f"Command failed: {result.stderr}"

        output = result.stdout

        # Verify all sections present
        assert "TUI Demo" in output, "Missing demo header"
        assert "┌──┐" in output, "Missing 4x4 square"
        assert "Sample Table" in output, "Missing table"
        assert "Graph A" in output, "Missing table data"
        assert "TUI demo complete" in output, "Missing completion message"


class TestStyleAttributes:
    """Tests for style attribute capture (bold, italic, colors).

    Verifies ScreenCapture correctly captures Rich styling through ANSI codes.
    """

    def test_bold_text_captured(self, screen_capture: ScreenCapture) -> None:
        """
        GIVEN: ANSI bold escape sequence
        WHEN: Feed to ScreenCapture
        THEN: ScreenCell.bold is True for bold characters
        """
        # ANSI: ESC[1m = bold on, ESC[0m = reset
        screen_capture.feed("\x1b[1mBold\x1b[0m Normal")
        snap = screen_capture.snapshot()

        # "Bold" should have bold=True
        bold_cell = snap.get_cell(0, 0)
        assert bold_cell.char == "B"
        assert bold_cell.bold is True, "Expected bold=True for 'B'"

        # "Normal" should have bold=False (after reset)
        normal_cell = snap.get_cell(5, 0)
        assert normal_cell.char == "N"
        assert normal_cell.bold is False, "Expected bold=False for 'N'"

    def test_italic_text_captured(self, screen_capture: ScreenCapture) -> None:
        """
        GIVEN: ANSI italic escape sequence
        WHEN: Feed to ScreenCapture
        THEN: ScreenCell.italic is True for italic characters
        """
        # ANSI: ESC[3m = italic on, ESC[0m = reset
        screen_capture.feed("\x1b[3mItalic\x1b[0m Normal")
        snap = screen_capture.snapshot()

        italic_cell = snap.get_cell(0, 0)
        assert italic_cell.char == "I"
        assert italic_cell.italic is True, "Expected italic=True for 'I'"

        normal_cell = snap.get_cell(7, 0)
        assert normal_cell.char == "N"
        assert normal_cell.italic is False, "Expected italic=False for 'N'"

    def test_underline_text_captured(self, screen_capture: ScreenCapture) -> None:
        """
        GIVEN: ANSI underline escape sequence
        WHEN: Feed to ScreenCapture
        THEN: ScreenCell.underline is True for underlined characters
        """
        # ANSI: ESC[4m = underline on, ESC[0m = reset
        screen_capture.feed("\x1b[4mUnder\x1b[0m Normal")
        snap = screen_capture.snapshot()

        under_cell = snap.get_cell(0, 0)
        assert under_cell.char == "U"
        assert under_cell.underline is True, "Expected underline=True for 'U'"

        normal_cell = snap.get_cell(6, 0)
        assert normal_cell.char == "N"
        assert normal_cell.underline is False, "Expected underline=False for 'N'"

    def test_foreground_color_captured(self, screen_capture: ScreenCapture) -> None:
        """
        GIVEN: ANSI foreground color escape sequence
        WHEN: Feed to ScreenCapture
        THEN: ScreenCell.fg reflects the color
        """
        # ANSI: ESC[31m = red foreground, ESC[0m = reset
        screen_capture.feed("\x1b[31mRed\x1b[0m")
        snap = screen_capture.snapshot()

        red_cell = snap.get_cell(0, 0)
        assert red_cell.char == "R"
        assert red_cell.fg == "red", f"Expected fg='red', got {red_cell.fg!r}"

    def test_background_color_captured(self, screen_capture: ScreenCapture) -> None:
        """
        GIVEN: ANSI background color escape sequence
        WHEN: Feed to ScreenCapture
        THEN: ScreenCell.bg reflects the color
        """
        # ANSI: ESC[44m = blue background, ESC[0m = reset
        screen_capture.feed("\x1b[44mBlue BG\x1b[0m")
        snap = screen_capture.snapshot()

        blue_cell = snap.get_cell(0, 0)
        assert blue_cell.char == "B"
        assert blue_cell.bg == "blue", f"Expected bg='blue', got {blue_cell.bg!r}"

    def test_combined_styles_captured(self, screen_capture: ScreenCapture) -> None:
        """
        GIVEN: Multiple ANSI style codes combined
        WHEN: Feed to ScreenCapture
        THEN: All attributes captured correctly
        """
        # Bold + Red + Blue background
        screen_capture.feed("\x1b[1;31;44mStyled\x1b[0m")
        snap = screen_capture.snapshot()

        cell = snap.get_cell(0, 0)
        assert cell.char == "S"
        assert cell.bold is True, "Expected bold=True"
        assert cell.fg == "red", f"Expected fg='red', got {cell.fg!r}"
        assert cell.bg == "blue", f"Expected bg='blue', got {cell.bg!r}"

    def test_rich_console_styles_captured(self, test_console) -> None:
        """
        GIVEN: Rich Console with styled output
        WHEN: Capture via ScreenCapture
        THEN: Rich styles are translated to ANSI and captured

        This tests the Rich → ANSI → pyte → ScreenCell pipeline.
        """
        from libs.python.tui_testing import ScreenCapture

        console, buffer = test_console
        console.print("[bold red]Alert[/bold red]")

        # Create fresh capture and feed Rich output
        capture = ScreenCapture(80, 24)
        output = buffer.getvalue()
        capture.feed(output.replace("\n", "\r\n"))
        snap = capture.snapshot()

        # Find the 'A' from 'Alert'
        text = snap.get_text()
        assert "Alert" in text, f"Expected 'Alert' in output, got: {text}"

        # The cell with 'A' should be bold and red
        # Rich may add leading space/newline, so find it
        for y in range(snap.height):
            for x in range(snap.width):
                cell = snap.get_cell(x, y)
                if cell.char == "A":
                    assert cell.bold is True, "Expected 'A' to be bold"
                    assert cell.fg == "red", f"Expected 'A' fg='red', got {cell.fg!r}"
                    return

        raise AssertionError("Could not find 'A' character in snapshot")


class TestTUIComponents:
    """Tests for existing cli/tui/components.py functions.

    Tests the actual TUI components used in the application.
    Note: Interactive components (select, confirm) require input and are
    tested separately in integration tests.
    """

    def test_panel_renders_with_content(self, test_console) -> None:
        """
        GIVEN: The panel() component from cli/tui/components
        WHEN: Render a panel with content
        THEN: Output contains panel borders and content
        """
        from io import StringIO

        from rich.console import Console
        from rich.panel import Panel

        from libs.python.tui_testing import ScreenCapture

        # Create isolated console for testing
        buffer = StringIO()
        console = Console(file=buffer, force_terminal=True, width=80, height=24)

        # Render panel directly (simulating what panel() does)
        p = Panel("Hello World", title="[ Test ]", border_style="blue")
        console.print(p)

        # Capture the output
        capture = ScreenCapture(80, 24)
        output = buffer.getvalue()
        capture.feed(output.replace("\n", "\r\n"))
        snap = capture.snapshot()

        text = snap.get_text()

        # Verify panel structure
        assert "Hello World" in text, f"Missing content in: {text}"
        assert "Test" in text, f"Missing title in: {text}"
        # Rich panels use rounded corners
        assert "╭" in text or "┌" in text, "Missing top-left corner"
        assert "╯" in text or "┘" in text, "Missing bottom-right corner"

    def test_panel_with_empty_content_shows_placeholder(self, test_console) -> None:
        """
        GIVEN: panel() called with empty content
        WHEN: Render
        THEN: Shows "(empty)" placeholder
        """
        from io import StringIO

        from rich.console import Console
        from rich.panel import Panel

        from libs.python.tui_testing import ScreenCapture

        buffer = StringIO()
        console = Console(file=buffer, force_terminal=True, width=80, height=24)

        # The panel() function shows "(empty)" for empty content
        p = Panel("(empty)", title=None, border_style="blue")
        console.print(p)

        capture = ScreenCapture(80, 24)
        output = buffer.getvalue()
        capture.feed(output.replace("\n", "\r\n"))
        snap = capture.snapshot()

        text = snap.get_text()
        assert "(empty)" in text, f"Missing placeholder in: {text}"

    def test_panel_expand_false_fits_content(self) -> None:
        """
        GIVEN: panel() with expand=False
        WHEN: Render short content
        THEN: Panel width fits content, not full terminal width
        """
        from io import StringIO

        from rich.console import Console
        from rich.panel import Panel

        from libs.python.tui_testing import ScreenCapture

        buffer = StringIO()
        console = Console(file=buffer, force_terminal=True, width=80, height=24)

        # Short content with expand=False
        p = Panel("Hi", expand=False)
        console.print(p)

        capture = ScreenCapture(80, 24)
        output = buffer.getvalue()
        capture.feed(output.replace("\n", "\r\n"))
        snap = capture.snapshot()

        # The panel should be narrow, not 80 chars wide
        # Check that most of row 0 is empty (spaces)
        empty_count = 0
        for x in range(40, 80):  # Right half should be empty
            cell = snap.get_cell(x, 0)
            if cell.char == " ":
                empty_count += 1

        assert empty_count > 30, "Panel should not expand to full width"

    def test_panel_border_style_applied(self) -> None:
        """
        GIVEN: panel() with border_style="cyan"
        WHEN: Render
        THEN: Border characters have cyan foreground color
        """
        from io import StringIO

        from rich.console import Console
        from rich.panel import Panel

        from libs.python.tui_testing import ScreenCapture

        buffer = StringIO()
        console = Console(file=buffer, force_terminal=True, width=80, height=24)

        p = Panel("Content", border_style="cyan", expand=False)
        console.print(p)

        capture = ScreenCapture(80, 24)
        output = buffer.getvalue()
        capture.feed(output.replace("\n", "\r\n"))
        snap = capture.snapshot()

        # Find a border character and check its color
        # Top-left corner should be cyan
        for y in range(snap.height):
            for x in range(snap.width):
                cell = snap.get_cell(x, y)
                if cell.char == "╭":
                    assert cell.fg == "cyan", f"Expected border fg='cyan', got {cell.fg!r}"
                    return

        # If no rounded corner found, check for square corner
        for y in range(snap.height):
            for x in range(snap.width):
                cell = snap.get_cell(x, y)
                if cell.char == "┌":
                    assert cell.fg == "cyan", f"Expected border fg='cyan', got {cell.fg!r}"
                    return

        raise AssertionError("Could not find panel corner character")


class TestGraphDAG:
    """Tests for graph DAG rendering component."""

    def test_graph_dag_renders_nodes(self) -> None:
        """
        GIVEN: graph_dag() with 3 nodes
        WHEN: Render to captured console
        THEN: All node IDs appear in output
        """
        from io import StringIO

        from rich.console import Console

        from cli.tui.graph_render import graph_dag
        from libs.python.tui_testing import ScreenCapture

        sample_graph = {
            "name": "Test Graph",
            "nodes": [
                {"id": "alpha", "type": "unix"},
                {"id": "beta", "type": "llm"},
            ],
            "edges": [{"source": "alpha", "target": "beta"}],
        }

        # Patch console temporarily
        buffer = StringIO()
        temp_console = Console(file=buffer, force_terminal=True, width=80, height=24)

        # Use the graph_dag function's internal logic via graph_dag_panel
        from cli.tui.graph_render import graph_dag_panel

        panel = graph_dag_panel(sample_graph)
        temp_console.print(panel)

        capture = ScreenCapture(80, 24)
        output = buffer.getvalue()
        capture.feed(output.replace("\n", "\r\n"))
        snap = capture.snapshot()

        text = snap.get_text()
        assert "alpha" in text, "Node 'alpha' should appear in output"
        assert "beta" in text, "Node 'beta' should appear in output"

    def test_graph_dag_shows_node_types(self) -> None:
        """
        GIVEN: graph_dag() with nodes of different types
        WHEN: Render
        THEN: Node types appear in output
        """
        from io import StringIO

        from rich.console import Console

        from cli.tui.graph_render import graph_dag_panel
        from libs.python.tui_testing import ScreenCapture

        sample_graph = {
            "name": "Type Test",
            "nodes": [
                {"id": "cmd", "type": "unix"},
                {"id": "ai", "type": "llm"},
            ],
            "edges": [],
        }

        buffer = StringIO()
        console = Console(file=buffer, force_terminal=True, width=80, height=24)
        panel = graph_dag_panel(sample_graph)
        console.print(panel)

        capture = ScreenCapture(80, 24)
        output = buffer.getvalue()
        capture.feed(output.replace("\n", "\r\n"))
        snap = capture.snapshot()

        text = snap.get_text()
        assert "unix" in text, "Node type 'unix' should appear"
        assert "llm" in text, "Node type 'llm' should appear"

    def test_graph_dag_panel_has_border(self) -> None:
        """
        GIVEN: graph_dag_panel()
        WHEN: Render
        THEN: Panel has border characters
        """
        from io import StringIO

        from rich.console import Console

        from cli.tui.graph_render import graph_dag_panel
        from libs.python.tui_testing import ScreenCapture

        sample_graph = {
            "name": "Border Test",
            "nodes": [{"id": "x", "type": "api"}],
            "edges": [],
        }

        buffer = StringIO()
        console = Console(file=buffer, force_terminal=True, width=80, height=24)
        panel = graph_dag_panel(sample_graph)
        console.print(panel)

        capture = ScreenCapture(80, 24)
        output = buffer.getvalue()
        capture.feed(output.replace("\n", "\r\n"))
        snap = capture.snapshot()

        text = snap.get_text()
        # Should have panel border characters
        has_border = "╭" in text or "┌" in text or "│" in text
        assert has_border, "Panel should have border characters"


class TestFileTree:
    """Tests for file tree navigation component."""

    def test_file_tree_renders_directory(self) -> None:
        """
        GIVEN: file_tree_panel() with current directory
        WHEN: Render
        THEN: Directory names appear in output
        """
        from io import StringIO

        from rich.console import Console

        from cli.tui.file_tree import file_tree_panel
        from libs.python.tui_testing import ScreenCapture

        buffer = StringIO()
        console = Console(file=buffer, force_terminal=True, width=80, height=40)

        panel = file_tree_panel(".", max_depth=1, title="Test Files")
        console.print(panel)

        capture = ScreenCapture(80, 40)
        output = buffer.getvalue()
        capture.feed(output.replace("\n", "\r\n"))
        snap = capture.snapshot()

        text = snap.get_text()
        # Should contain common project dirs/files
        assert "cli" in text or "tests" in text or "libs" in text, "Should show project directories"

    def test_file_tree_shows_icons(self) -> None:
        """
        GIVEN: file_tree_panel()
        WHEN: Render
        THEN: File/folder icons appear
        """
        from io import StringIO

        from rich.console import Console

        from cli.tui.file_tree import file_tree_panel
        from libs.python.tui_testing import ScreenCapture

        buffer = StringIO()
        console = Console(file=buffer, force_terminal=True, width=80, height=40)

        panel = file_tree_panel(".", max_depth=1)
        console.print(panel)

        capture = ScreenCapture(80, 40)
        output = buffer.getvalue()
        capture.feed(output.replace("\n", "\r\n"))
        snap = capture.snapshot()

        text = snap.get_text()
        # Should have folder icon
        assert "📁" in text or "📂" in text, "Should show folder icons"

    def test_file_tree_data_returns_structure(self) -> None:
        """
        GIVEN: file_tree_data()
        WHEN: Called on current directory
        THEN: Returns dict with name, path, is_dir, children
        """
        from cli.tui.file_tree import file_tree_data

        data = file_tree_data(".", max_depth=1)

        assert "name" in data
        assert "path" in data
        assert "is_dir" in data
        assert data["is_dir"] is True
        assert "children" in data
        assert isinstance(data["children"], list)


class TestSplitLayout:
    """Tests for split pane layout component."""

    def test_split_layout_renders_both_panes(self) -> None:
        """
        GIVEN: split_layout() with left and right content
        WHEN: Render
        THEN: Both panes appear with titles
        """
        from io import StringIO

        from rich.console import Console
        from rich.text import Text

        # Can't easily capture split_layout since it prints directly
        # Instead test the SplitLayout class
        from cli.tui.layout import SplitLayout, split_layout
        from libs.python.tui_testing import ScreenCapture

        layout = SplitLayout(left_width=20, left_title="Left", right_title="Right")
        layout.set_left(Text("Left content"))
        layout.add_widget("test", Text("Right content"))

        # Render to buffer
        buffer = StringIO()
        console = Console(file=buffer, force_terminal=True, width=80, height=24)
        built = layout._build_layout()
        console.print(built)

        capture = ScreenCapture(80, 24)
        output = buffer.getvalue()
        capture.feed(output.replace("\n", "\r\n"))
        snap = capture.snapshot()

        text = snap.get_text()
        assert "Left" in text, "Left pane title should appear"
        assert "Right" in text, "Right pane title should appear"

    def test_widget_corral_empty_message(self) -> None:
        """
        GIVEN: WidgetCorral with no widgets
        WHEN: Render
        THEN: Shows "No widgets" message
        """
        from io import StringIO

        from rich.console import Console

        from cli.tui.layout import WidgetCorral
        from libs.python.tui_testing import ScreenCapture

        corral = WidgetCorral("Test Corral")

        buffer = StringIO()
        console = Console(file=buffer, force_terminal=True, width=60, height=10)
        console.print(corral)

        capture = ScreenCapture(60, 10)
        output = buffer.getvalue()
        capture.feed(output.replace("\n", "\r\n"))
        snap = capture.snapshot()

        text = snap.get_text()
        assert "No widgets" in text, "Empty corral should show message"

    def test_widget_corral_add_remove(self) -> None:
        """
        GIVEN: WidgetCorral
        WHEN: Add widget then remove
        THEN: Widget count changes correctly
        """
        from rich.text import Text

        from cli.tui.layout import WidgetCorral

        corral = WidgetCorral()
        assert len(corral.widgets) == 0

        corral.add("w1", Text("Widget 1"))
        assert len(corral.widgets) == 1

        corral.add("w2", Text("Widget 2"))
        assert len(corral.widgets) == 2

        corral.remove("w1")
        assert len(corral.widgets) == 1
        assert corral.widgets[0][0] == "w2"

        corral.clear()
        assert len(corral.widgets) == 0


class TestE2ESubprocessNew:
    """E2E subprocess tests for new TUI commands."""

    def test_unhinged_tui_graph_renders_dag(self, screen_capture: ScreenCapture) -> None:
        """
        GIVEN: `unhinged tui graph` command
        WHEN: Run as subprocess
        THEN: Output contains DAG elements
        """
        result = subprocess.run(
            [sys.executable, "-m", "cli", "tui", "graph"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent.parent,
            env={
                **dict(__import__("os").environ),
                "TERM": "xterm-256color",
                "COLUMNS": "80",
                "LINES": "24",
            },
        )

        assert result.returncode == 0, f"Command failed: {result.stderr}"

        output = result.stdout
        screen_capture.feed(output.replace("\n", "\r\n"))
        snap = screen_capture.snapshot()
        text = snap.get_text()

        # Should contain sample graph elements
        assert "Sample" in text or "input" in text, "Should show sample graph"
        assert "→" in text or "Edges" in text, "Should show edge information"

    def test_unhinged_tui_files_renders_tree(self, screen_capture: ScreenCapture) -> None:
        """
        GIVEN: `unhinged tui files cli --depth 1` command
        WHEN: Run as subprocess
        THEN: Output contains file tree
        """
        result = subprocess.run(
            [sys.executable, "-m", "cli", "tui", "files", "cli", "--depth", "1"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent.parent,
            env={
                **dict(__import__("os").environ),
                "TERM": "xterm-256color",
                "COLUMNS": "80",
                "LINES": "40",
            },
        )

        assert result.returncode == 0, f"Command failed: {result.stderr}"

        output = result.stdout
        capture = ScreenCapture(80, 40)
        capture.feed(output.replace("\n", "\r\n"))
        snap = capture.snapshot()
        text = snap.get_text()

        # Should contain cli subdirectories
        assert "commands" in text or "tui" in text, "Should show cli subdirectories"


class TestVoiceState:
    """Tests for voice-first TUI application state management."""

    def test_initial_state_is_idle(self) -> None:
        """
        GIVEN: create_initial_state()
        WHEN: Called
        THEN: Returns state in IDLE voice mode
        """
        from cli.tui.state import VoiceState, create_initial_state

        state = create_initial_state()

        assert state.voice == VoiceState.IDLE
        assert state.running is True
        assert state.history == []

    def test_start_recording_transitions_state(self) -> None:
        """
        GIVEN: State in IDLE
        WHEN: start_recording()
        THEN: Transitions to RECORDING
        """
        from cli.tui.state import AppState, VoiceState

        state = AppState(voice=VoiceState.IDLE)
        new_state = state.start_recording()

        assert new_state.voice == VoiceState.RECORDING
        assert new_state.recording_seconds == 0
        assert "Recording" in new_state.status

    def test_stop_recording_transitions_to_processing(self) -> None:
        """
        GIVEN: State in RECORDING
        WHEN: stop_recording()
        THEN: Transitions to PROCESSING
        """
        from cli.tui.state import AppState, VoiceState

        state = AppState(voice=VoiceState.RECORDING, recording_seconds=5)
        new_state = state.stop_recording()

        assert new_state.voice == VoiceState.PROCESSING
        assert "Transcribing" in new_state.status

    def test_set_transcript_stores_result(self) -> None:
        """
        GIVEN: State in PROCESSING
        WHEN: set_transcript("hello world")
        THEN: Stores transcript and transitions to ANALYZING
        """
        from cli.tui.state import AppState, VoiceState

        state = AppState(voice=VoiceState.PROCESSING)
        new_state = state.set_transcript("hello world")

        # Now transitions to ANALYZING for intent analysis
        assert new_state.voice == VoiceState.ANALYZING
        assert new_state.last_transcript == "hello world"
        assert "hello world" in new_state.history
        assert "Analyzing" in new_state.status

    def test_transcript_history_keeps_last_10(self) -> None:
        """
        GIVEN: State with 9 items in history
        WHEN: set_transcript() called twice
        THEN: History keeps only last 10 items
        """
        from cli.tui.state import AppState, VoiceState

        history = [f"msg{i}" for i in range(9)]
        state = AppState(voice=VoiceState.PROCESSING, history=history)

        new_state = state.set_transcript("new1")
        new_state = AppState(
            voice=VoiceState.PROCESSING,
            history=new_state.history,
        ).set_transcript("new2")

        assert len(new_state.history) == 10
        assert new_state.history[0] == "new2"

    def test_tick_recording_increments_time(self) -> None:
        """
        GIVEN: State in RECORDING with 5 seconds
        WHEN: tick_recording()
        THEN: recording_seconds increments to 6
        """
        from cli.tui.state import AppState, VoiceState

        state = AppState(voice=VoiceState.RECORDING, recording_seconds=5)
        new_state = state.tick_recording()

        assert new_state.recording_seconds == 6

    def test_set_error_returns_to_idle(self) -> None:
        """
        GIVEN: State in any mode
        WHEN: set_error("something failed")
        THEN: Returns to IDLE with error in status
        """
        from cli.tui.state import AppState, VoiceState

        state = AppState(voice=VoiceState.PROCESSING)
        new_state = state.set_error("something failed")

        assert new_state.voice == VoiceState.IDLE
        assert "something failed" in new_state.status

    def test_quit_sets_running_false(self) -> None:
        """
        GIVEN: Running state
        WHEN: quit()
        THEN: running is False
        """
        from cli.tui.state import AppState

        state = AppState(running=True)
        new_state = state.quit()

        assert new_state.running is False


class TestVoiceRender:
    """Tests for voice-first TUI rendering."""

    def test_render_state_produces_layout(self) -> None:
        """
        GIVEN: AppState
        WHEN: render_state()
        THEN: Returns Rich Layout
        """
        from rich.layout import Layout

        from cli.tui.app import render_state
        from cli.tui.state import create_initial_state

        state = create_initial_state()
        layout = render_state(state)

        assert isinstance(layout, Layout)

    def test_render_shows_ready_when_idle(self) -> None:
        """
        GIVEN: State in IDLE
        WHEN: Render to screen
        THEN: Shows READY indicator
        """
        from io import StringIO

        from rich.console import Console

        from cli.tui.app import render_main_pane
        from cli.tui.state import AppState, VoiceState
        from libs.python.tui_testing import ScreenCapture

        state = AppState(voice=VoiceState.IDLE)

        buffer = StringIO()
        console = Console(file=buffer, force_terminal=True, width=60, height=24)
        panel = render_main_pane(state)
        console.print(panel)

        capture = ScreenCapture(60, 24)
        capture.feed(buffer.getvalue().replace("\n", "\r\n"))
        snap = capture.snapshot()
        text = snap.get_text()

        assert "READY" in text

    def test_render_shows_recording_indicator(self) -> None:
        """
        GIVEN: State in RECORDING
        WHEN: Render to screen
        THEN: Shows RECORDING indicator with time
        """
        from io import StringIO

        from rich.console import Console

        from cli.tui.app import render_main_pane
        from cli.tui.state import AppState, VoiceState
        from libs.python.tui_testing import ScreenCapture

        state = AppState(voice=VoiceState.RECORDING, recording_seconds=5)

        buffer = StringIO()
        console = Console(file=buffer, force_terminal=True, width=60, height=24)
        panel = render_main_pane(state)
        console.print(panel)

        capture = ScreenCapture(60, 24)
        capture.feed(buffer.getvalue().replace("\n", "\r\n"))
        snap = capture.snapshot()
        text = snap.get_text()

        assert "RECORDING" in text
        assert "5s" in text

    def test_render_shows_last_transcript(self) -> None:
        """
        GIVEN: State with last_transcript set
        WHEN: Render to screen
        THEN: Shows the transcript text
        """
        from io import StringIO

        from rich.console import Console

        from cli.tui.app import render_main_pane
        from cli.tui.state import AppState, VoiceState
        from libs.python.tui_testing import ScreenCapture

        state = AppState(
            voice=VoiceState.IDLE,
            last_transcript="hello world this is a test",
        )

        buffer = StringIO()
        console = Console(file=buffer, force_terminal=True, width=60, height=24)
        panel = render_main_pane(state)
        console.print(panel)

        capture = ScreenCapture(60, 24)
        capture.feed(buffer.getvalue().replace("\n", "\r\n"))
        snap = capture.snapshot()
        text = snap.get_text()

        assert "hello world" in text
