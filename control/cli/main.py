"""Unhinged CLI - Main entry point."""

import click

from control.cli.commands import admin, dev, system, vm
from control.cli.utils import log_info


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """Unhinged - Native Graphics Platform with Dual-System Architecture.

    Normal usage: unhinged [COMMAND] [OPTIONS]
    Default: unhinged start (start complete system and launch GUI)
    """
    # If no command provided, start the complete system with GUI
    if ctx.invoked_subcommand is None:
        log_info("🚀 Starting Unhinged complete system...")
        ctx.invoke(system.start)
        log_info("📺 Launching GUI...")
        ctx.invoke(system.gui)


# Add command groups
cli.add_command(system)
cli.add_command(dev)
cli.add_command(admin)
cli.add_command(vm)


if __name__ == "__main__":
    cli()
