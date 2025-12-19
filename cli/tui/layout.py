"""Split pane layout for TUI.

Provides the foundation for left navigation + right widget corral architecture.
Uses Rich's Layout and Columns for flexible composition.

Layout structure:
┌─────────────────────┬────────────────────────────────────────┐
│ Left Nav (fixed)    │  Widget Corral (dynamic)               │
│ - File tree         │  - Graph view                          │
│ - Menu              │  - Details panel                       │
│ - Breadcrumb        │  - Preview                             │
└─────────────────────┴────────────────────────────────────────┘
"""


from rich.console import Group, RenderableType
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text

from cli.tui.console import console


class WidgetCorral:
    """Container for dynamic widgets in the right pane.

    Widgets can be added, removed, and arranged in a grid or stack layout.
    """

    def __init__(self, title: str = "Widgets") -> None:
        self.title = title
        self.widgets: list[tuple[str, RenderableType]] = []

    def add(self, name: str, widget: RenderableType) -> "WidgetCorral":
        """Add a widget to the corral."""
        self.widgets.append((name, widget))
        return self

    def clear(self) -> "WidgetCorral":
        """Clear all widgets."""
        self.widgets.clear()
        return self

    def remove(self, name: str) -> "WidgetCorral":
        """Remove widget by name."""
        self.widgets = [(n, w) for n, w in self.widgets if n != name]
        return self

    def __rich__(self) -> RenderableType:
        """Render widgets as a vertical stack."""
        if not self.widgets:
            return Panel(
                Text("No widgets loaded", style="dim"),
                title=f"[ {self.title} ]",
                border_style="dim",
            )

        items = [w for _, w in self.widgets]
        return Group(*items)


class SplitLayout:
    """Two-pane layout with left nav and right widget corral.

    Left pane: Fixed width navigation (file tree, menu)
    Right pane: Dynamic widget corral (graphs, previews)
    """

    def __init__(
        self,
        left_width: int = 30,
        left_title: str = "Navigation",
        right_title: str = "Widgets",
    ) -> None:
        self.left_width = left_width
        self.left_title = left_title
        self.right_title = right_title
        self.left_content: RenderableType | None = None
        self.corral = WidgetCorral(right_title)

    def set_left(self, content: RenderableType) -> "SplitLayout":
        """Set the left pane content."""
        self.left_content = content
        return self

    def add_widget(self, name: str, widget: RenderableType) -> "SplitLayout":
        """Add a widget to the right pane corral."""
        self.corral.add(name, widget)
        return self

    def clear_widgets(self) -> "SplitLayout":
        """Clear all widgets from the corral."""
        self.corral.clear()
        return self

    def render(self) -> None:
        """Render the split layout to console."""
        layout = self._build_layout()
        console.print()
        console.print(layout)
        console.print()

    def _build_layout(self) -> Layout:
        """Build the Rich Layout."""
        root = Layout()

        # Left pane
        left_content = self.left_content or Text("(empty)", style="dim")
        left_panel = Panel(
            left_content,
            title=f"[ {self.left_title} ]",
            border_style="cyan",
            width=self.left_width,
        )

        # Right pane
        right_panel = Panel(
            self.corral,
            title=f"[ {self.right_title} ]",
            border_style="blue",
        )

        root.split_row(
            Layout(left_panel, name="left", size=self.left_width),
            Layout(right_panel, name="right"),
        )

        return root


def split_layout(
    left: RenderableType,
    right: RenderableType,
    *,
    left_width: int = 30,
    left_title: str = "Navigation",
    right_title: str = "Content",
) -> None:
    """Render a simple two-pane split layout.

    Args:
        left: Content for left pane.
        right: Content for right pane.
        left_width: Width of left pane in characters.
        left_title: Title for left pane.
        right_title: Title for right pane.
    """
    left_panel = Panel(
        left,
        title=f"[ {left_title} ]",
        border_style="cyan",
        width=left_width,
    )

    right_panel = Panel(
        right,
        title=f"[ {right_title} ]",
        border_style="blue",
    )

    layout = Layout()
    layout.split_row(
        Layout(left_panel, name="left", size=left_width),
        Layout(right_panel, name="right"),
    )

    console.print()
    console.print(layout)
    console.print()
