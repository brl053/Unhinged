"""CLI utilities and helpers.

Consolidated from control/cli/utils.py for unified CLI interface.

This module also defines small UX helpers (logging, loading indicators)
that act as the design system for the CLI experience.
"""

import subprocess
import sys
import threading
import time
from contextlib import contextmanager
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


@contextmanager
def loading_indicator(message: str, *, delay: float = 0.1) -> Any:
    """Display a simple spinner-style loading indicator.

    Designed as a small, reusable building block for CLI loading states.
    Use it as a context manager around long-running work::

        with loading_indicator("Transcribing recorded audio..."):
            service.transcribe_audio(path)

    The indicator is intentionally minimal and side-effect free beyond
    writing to stdout, so it can be adopted across commands (text, image,
    graph, etc.) without pulling in additional dependencies.
    """

    stop = threading.Event()

    def _worker() -> None:
        frames = ["|", "/", "-", "\\"]
        idx = 0
        while not stop.is_set():
            frame = frames[idx % len(frames)]
            idx += 1
            sys.stdout.write("\r" + message + " " + frame)
            sys.stdout.flush()
            time.sleep(delay)

        # Clear the line on completion
        sys.stdout.write("\r" + " " * (len(message) + 2) + "\r")
        sys.stdout.flush()

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()
    try:
        yield
    finally:
        stop.set()
        thread.join()


def display_transcript(text: str, *, title: str = "Transcription") -> None:
    """Display transcription text in a visually distinct boxed area.

    Creates a bordered box around the transcript text for clear presentation.
    Handles empty text, long lines (with wrapping), and multi-line content.

    ASCII-only, no colors per design requirements.
    """
    import shutil
    import textwrap

    # Get terminal width, default to 80 if not available
    term_width = shutil.get_terminal_size((80, 24)).columns
    # Box width: leave room for borders and padding
    box_width = min(term_width - 2, 78)
    content_width = box_width - 4  # 2 for borders, 2 for padding

    # Handle empty text
    if not text or not text.strip():
        text = "(no speech detected)"

    # Wrap text to fit content width
    wrapped_lines = []
    for line in text.split("\n"):
        if line.strip():
            wrapped_lines.extend(textwrap.wrap(line, width=content_width) or [""])
        else:
            wrapped_lines.append("")

    # Build the box (ASCII only)
    top_border = "+" + "-" * (box_width - 2) + "+"
    bottom_border = "+" + "-" * (box_width - 2) + "+"
    separator = "+" + "-" * (box_width - 2) + "+"

    # Title line
    title_text = f"[ {title} ]"
    title_padding = content_width - len(title_text)
    title_line = "| " + title_text + " " * title_padding + " |"

    # Print the box
    click.echo()
    click.echo(top_border)
    click.echo(title_line)
    click.echo(separator)

    for line in wrapped_lines:
        padding = content_width - len(line)
        click.echo("| " + line + " " * padding + " |")

    click.echo(bottom_border)
    click.echo()


__all__ = [
    "get_python",
    "run_command",
    "log_info",
    "log_success",
    "log_warning",
    "log_error",
    "check_file_exists",
    "loading_indicator",
    "display_transcript",
]
