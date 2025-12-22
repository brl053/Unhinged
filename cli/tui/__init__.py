"""Unhinged CLI output utilities.

Rich-based output helpers for CLI commands.
For the main TUI, use libs/python/terminal/unhinged instead.

Components:
- console: Shared Rich console with semantic theme
- panel, loading, select, confirm: Basic output components
- Menu: Interactive selection menus
- graph_tree: Graph visualization as tree
"""

from cli.tui.components import confirm, loading, panel, select
from cli.tui.console import console
from cli.tui.menu import Menu
from cli.tui.tree import graph_tree

__all__ = [
    # Core
    "console",
    # Components
    "confirm",
    "loading",
    "panel",
    "select",
    # Menu
    "Menu",
    # Visualization
    "graph_tree",
]
