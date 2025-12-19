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
    tui,
    video,
    vm,
    voice,
)


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx: click.Context) -> None:
    """Unhinged - Native Graphics Platform with Dual-System Architecture.

    Run without arguments to launch interactive TUI.
    Or use: unhinged [COMMAND] [OPTIONS]
    """
    # If no command provided, launch TUI
    if ctx.invoked_subcommand is None:
        from cli.tui import run_app

        run_app()


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
cli.add_command(tui)


if __name__ == "__main__":
    cli()
