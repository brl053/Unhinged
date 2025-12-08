"""CLI command modules."""

from cli.commands.admin import admin
from cli.commands.chat import chat
from cli.commands.dev import dev
from cli.commands.generate import generate
from cli.commands.graph import graph
from cli.commands.image import image
from cli.commands.parse import parse
from cli.commands.prompt import prompt
from cli.commands.query import query
from cli.commands.shortform import shortform
from cli.commands.system import system
from cli.commands.transcribe import transcribe
from cli.commands.video import video
from cli.commands.vm import vm
from cli.commands.voice import voice

# Lazy import for orchestrate - has broken dependency on 'events' module
try:
    from cli.commands.orchestrate import orchestrate
except ImportError:
    import click

    @click.group()
    def orchestrate():
        """Command orchestration (unavailable - missing dependencies)."""
        pass


__all__ = [
    "system",
    "dev",
    "admin",
    "vm",
    "generate",
    "transcribe",
    "image",
    "voice",
    "chat",
    "video",
    "parse",
    "shortform",
    "orchestrate",
    "prompt",
    "query",
    "graph",
]
