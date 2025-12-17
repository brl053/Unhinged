"""Reusable TUI components.

Primitives: panel, loading, select, confirm.
These replace cli/utils display_transcript and loading_indicator.
"""

from contextlib import contextmanager
from typing import Any

from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.status import Status

from cli.tui.console import console


def panel(
    content: str,
    *,
    title: str = "",
    border_style: str = "blue",
    expand: bool = False,
) -> None:
    """Display content in a bordered panel.

    Replaces display_transcript with Rich Panel.

    Args:
        content: Text to display inside the panel.
        title: Optional title for the panel border.
        border_style: Rich style for the border (default: blue).
        expand: Whether to expand panel to terminal width.
    """
    p = Panel(
        content or "(empty)",
        title=f"[ {title} ]" if title else None,
        border_style=border_style,
        expand=expand,
    )
    console.print(p)


@contextmanager
def loading(message: str) -> Any:
    """Display a loading spinner during long-running work.

    Replaces loading_indicator context manager.

    Usage:
        with loading("Processing..."):
            do_work()

    Args:
        message: Status message to display with spinner.

    Yields:
        Rich Status instance (rarely needed).
    """
    with Status(message, console=console, spinner="dots") as status:
        yield status


def select(
    prompt: str,
    choices: list[str],
    *,
    default: str | None = None,
) -> str:
    """Prompt user to select from a list of choices.

    Args:
        prompt: Question to display.
        choices: List of valid choices.
        default: Default selection if user presses enter.

    Returns:
        Selected choice string.
    """
    choices_str = ", ".join(choices)
    full_prompt = f"{prompt} [{choices_str}]"
    while True:
        result: str = Prompt.ask(full_prompt, console=console, default=default or "")
        if result in choices:
            return result
        console.print(f"[warning]Invalid choice. Options: {choices_str}[/warning]")


def confirm(prompt: str, *, default: bool = False) -> bool:
    """Prompt user for yes/no confirmation.

    Args:
        prompt: Question to display.
        default: Default value if user presses enter.

    Returns:
        True if confirmed, False otherwise.
    """
    result: bool = Confirm.ask(prompt, console=console, default=default)
    return result
