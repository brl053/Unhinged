"""Shared Rich Console instance for TUI output.

All TUI output routes through this console for consistent theming.
The console respects terminal capabilities and degrades gracefully.
"""

from rich.console import Console
from rich.theme import Theme

# Semantic color theme aligned with design system tokens
# Maps semantic roles to Rich style strings
_theme = Theme(
    {
        # Action colors
        "action.primary": "bold blue",
        "action.secondary": "dim",
        "action.disabled": "dim grey",
        # Feedback colors
        "success": "bold green",
        "warning": "bold yellow",
        "error": "bold red",
        "info": "cyan",
        # Text hierarchy
        "text.primary": "default",
        "text.secondary": "dim",
        "text.muted": "dim grey",
        # Interactive states
        "selected": "bold reverse",
        "highlight": "bold",
    }
)

# Shared console instance - all TUI output goes through here
console = Console(theme=_theme, highlight=False)
