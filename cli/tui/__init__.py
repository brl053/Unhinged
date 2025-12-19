"""TUI components for Unhinged CLI.

Rich-based text user interface primitives.
All CLI visual output routes through this module.
"""

from cli.tui.app import main as run_app
from cli.tui.components import confirm, loading, panel, select
from cli.tui.console import console
from cli.tui.file_tree import file_tree, file_tree_data, file_tree_panel
from cli.tui.graph_render import graph_dag, graph_dag_panel
from cli.tui.input import Key, KeyboardInput, KeyEvent
from cli.tui.layout import SplitLayout, WidgetCorral, split_layout
from cli.tui.menu import Menu
from cli.tui.state import AppState, IntentResult, VoiceState, create_initial_state
from cli.tui.tree import graph_tree
from cli.tui.wizard import Wizard, WizardStep

__all__ = [
    # Console
    "console",
    # Components
    "panel",
    "loading",
    "select",
    "confirm",
    "Menu",
    "Wizard",
    "WizardStep",
    # Graph rendering
    "graph_tree",
    "graph_dag",
    "graph_dag_panel",
    # File tree
    "file_tree",
    "file_tree_panel",
    "file_tree_data",
    # Layout
    "split_layout",
    "SplitLayout",
    "WidgetCorral",
    # Input (raw keyboard)
    "Key",
    "KeyEvent",
    "KeyboardInput",
    # State
    "AppState",
    "IntentResult",
    "VoiceState",
    "create_initial_state",
    # App entry
    "run_app",
]
