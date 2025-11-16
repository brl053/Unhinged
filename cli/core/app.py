"""Unhinged CLI - Main application entry point.

Consolidated from control/cli/main.py for unified CLI interface.
"""


import click

from cli.commands import admin, dev, generate, system, transcribe, vm


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx: click.Context) -> None:
    """Unhinged - Native Graphics Platform with Dual-System Architecture.

    Normal usage: unhinged [COMMAND] [OPTIONS]
    Default: unhinged system start (start complete system)
    """
    # If no command provided, show help
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# Add command groups
cli.add_command(system)
cli.add_command(dev)
cli.add_command(admin)
cli.add_command(vm)
cli.add_command(generate)
cli.add_command(transcribe)


if __name__ == "__main__":
    cli()
