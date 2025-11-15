"""Unhinged CLI - Main entry point."""

import click

from control.cli.commands import admin, dev, system, vm


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """Unhinged - Native Graphics Platform with Dual-System Architecture.

    Normal usage: unhinged [COMMAND] [OPTIONS]
    Default: unhinged start (start complete system)
    """
    # If no command provided, show help
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# Add command groups
cli.add_command(system)
cli.add_command(dev)
cli.add_command(admin)
cli.add_command(vm)


if __name__ == "__main__":
    cli()
