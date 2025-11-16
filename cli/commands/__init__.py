"""CLI command modules."""

from cli.commands.admin import admin
from cli.commands.dev import dev
from cli.commands.generate import generate
from cli.commands.image import image
from cli.commands.system import system
from cli.commands.transcribe import transcribe
from cli.commands.vm import vm
from cli.commands.voice import voice

__all__ = ["system", "dev", "admin", "vm", "generate", "transcribe", "image", "voice"]
