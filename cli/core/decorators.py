"""Shared decorators for CLI commands.

Provides common decorators for logging, error handling, and context management.
"""

import functools
from collections.abc import Callable
from typing import Any, TypeVar

import click

F = TypeVar("F", bound=Callable[..., Any])


def with_context(func: F) -> F:
    """Decorator to inject CLI context into command."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        _ = click.get_current_context()
        return func(*args, **kwargs)

    return wrapper  # type: ignore


def with_error_handling(func: F) -> F:
    """Decorator to handle errors gracefully."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as err:
            click.echo(f"❌ Error: {err}", err=True)
            raise click.Exit(1) from err

    return wrapper  # type: ignore
