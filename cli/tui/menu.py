"""Interactive menu component.

Displays a numbered list of items and prompts for selection.
Supports actions like run, view, edit, delete on selected item.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from rich.prompt import Prompt
from rich.table import Table

from cli.tui.console import console


@dataclass
class MenuItem:
    """Single menu item with display data and payload."""

    key: str  # Display key (e.g., "1", "a")
    label: str  # Primary display text
    description: str = ""  # Secondary text
    data: Any = None  # Arbitrary payload for callbacks


@dataclass
class MenuAction:
    """Action that can be performed on a menu item."""

    key: str  # Keyboard shortcut (e.g., "r", "v", "d")
    label: str  # Display label
    callback: Callable[[MenuItem], Any]  # Called with selected item


class Menu:
    """Interactive numbered menu with action dispatch.

    Usage:
        menu = Menu("Select a graph")
        menu.add_item("1", "Email Workflow", "3 nodes", data=graph_doc)
        menu.add_item("2", "Build Script", "1 node", data=graph_doc2)
        menu.add_action("r", "Run", run_graph)
        menu.add_action("v", "View", view_graph)
        menu.add_action("q", "Quit", lambda _: None)
        menu.run()
    """

    def __init__(self, title: str = "Menu") -> None:
        self.title = title
        self.items: list[MenuItem] = []
        self.actions: list[MenuAction] = []

    def add_item(
        self,
        key: str,
        label: str,
        description: str = "",
        *,
        data: Any = None,
    ) -> None:
        """Add an item to the menu."""
        self.items.append(MenuItem(key=key, label=label, description=description, data=data))

    def add_action(
        self,
        key: str,
        label: str,
        callback: Callable[[MenuItem], Any],
    ) -> None:
        """Add an action that can be performed on selected items."""
        self.actions.append(MenuAction(key=key, label=label, callback=callback))

    def _render_table(self) -> Table:
        """Build Rich Table for display."""
        table = Table(title=self.title, show_header=True, header_style="bold")
        table.add_column("#", style="dim", width=4)
        table.add_column("Name", style="text.primary")
        table.add_column("Description", style="text.secondary")

        for item in self.items:
            table.add_row(item.key, item.label, item.description)

        return table

    def _render_actions(self) -> str:
        """Build action hint string."""
        parts = [f"[bold]{a.key.upper()}[/bold]{a.label[1:]}" for a in self.actions]
        return "  ".join(parts)

    def _find_item(self, key: str) -> MenuItem | None:
        """Find item by key."""
        for item in self.items:
            if key == item.key:
                return item
        return None

    def _find_action(self, key: str) -> MenuAction | None:
        """Find action by key."""
        for action in self.actions:
            if key == action.key:
                return action
        return None

    def _display_menu(self) -> None:
        """Display the menu table and actions."""
        console.print()
        console.print(self._render_table())
        console.print()
        console.print(f"Actions: {self._render_actions()}", style="text.secondary")
        console.print()

    def _prompt_action(self, selected: MenuItem) -> Any:
        """Prompt for and execute action on selected item."""
        console.print(f"\nSelected: [highlight]{selected.label}[/highlight]")
        action_keys = "/".join(a.key for a in self.actions)
        action_response: str = Prompt.ask(f"Action [{action_keys}]", console=console)
        action_response = action_response.strip().lower()[:1]  # First char only

        action = self._find_action(action_response)
        if action is None:
            console.print("[warning]Invalid action[/warning]")
            return "continue"
        if action.callback is None or action_response == "q":
            return None
        return action.callback(selected)

    def run(self) -> Any:
        """Display menu and handle selection loop.

        Returns:
            Result of action callback, or None if quit.
        """
        while True:
            self._display_menu()
            response: str = Prompt.ask("Select item # or action", console=console)
            response = response.strip().lower()

            # Check for quit action
            if response == "q":
                return None

            # Check if it's an item key
            selected = self._find_item(response)
            if selected is None:
                console.print("[warning]Invalid selection[/warning]")
                continue

            result = self._prompt_action(selected)
            if result != "continue":
                return result
