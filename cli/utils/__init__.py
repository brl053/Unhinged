"""CLI utilities and helpers.

Consolidated from control/cli/utils.py for unified CLI interface.
"""

import subprocess
from pathlib import Path
from typing import Any

import click


def get_python() -> str:
    """Get Python command from venv or system."""
    venv_python = Path("build/python/venv/bin/python")
    if venv_python.exists():
        return str(venv_python)
    return "python3"


def run_command(cmd: Any, *args: Any, **kwargs: Any) -> int:
    """Run a shell command and handle errors."""
    try:
        result = subprocess.run(cmd, *args, **kwargs)
        return result.returncode
    except Exception as e:
        click.echo(click.style(f"❌ Error: {e}", fg="red"), err=True)
        return 1


def log_info(msg: str) -> None:
    """Log info message."""
    click.echo(click.style(f"ℹ️  {msg}", fg="cyan"))


def log_success(msg: str) -> None:
    """Log success message."""
    click.echo(click.style(f"✅ {msg}", fg="green"))


def log_warning(msg: str) -> None:
    """Log warning message."""
    click.echo(click.style(f"⚠️  {msg}", fg="yellow"))


def log_error(msg: str) -> None:
    """Log error message."""
    click.echo(click.style(f"❌ {msg}", fg="red"), err=True)


def check_file_exists(path: str, name: str) -> bool:
    """Check if a file exists, log error if not."""
    if not Path(path).exists():
        log_error(f"{name} not found at {path}")
        return False
    return True


__all__ = [
    "get_python",
    "run_command",
    "log_info",
    "log_success",
    "log_warning",
    "log_error",
    "check_file_exists",
]
