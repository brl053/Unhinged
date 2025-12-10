"""Unhinged CLI - Main application entry point.

Consolidated from control/cli/main.py for unified CLI interface.
"""

import click

from cli.commands import (
    admin,
    chat,
    dev,
    generate,
    graph,
    image,
    orchestrate,
    parse,
    shortform,
    system,
    transcribe,
    video,
    vm,
    voice,
)


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
cli.add_command(image)
cli.add_command(voice)
cli.add_command(video)
cli.add_command(parse)
cli.add_command(shortform)
cli.add_command(chat)
cli.add_command(orchestrate)
cli.add_command(graph)


if __name__ == "__main__":
    cli()
