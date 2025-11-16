"""CLI command modules."""

from cli.commands.admin import admin
from cli.commands.dev import dev
from cli.commands.system import system
from cli.commands.vm import vm

__all__ = ["system", "dev", "admin", "vm"]
