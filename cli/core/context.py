"""CLI context and state management.

Provides shared context for CLI commands, including configuration,
logging, and state tracking.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class CLIContext:
    """Shared context for CLI commands."""

    project_root: Path = field(default_factory=lambda: Path.cwd())
    verbose: bool = False
    debug: bool = False
    config: dict[str, Any] = field(default_factory=dict)
    session_id: str | None = None

    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)

    def set_config(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self.config[key] = value
