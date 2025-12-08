#!/usr/bin/env python3
"""Minimal entry point for graph session.

Usage:
    python3 -m cli.session
    python3 -m cli.session session

This bypasses the full CLI which has broken dependencies.
"""

import sys


def main():
    # Avoid importing the full cli.commands package
    # Import graph module directly
    import importlib.util

    import click

    spec = importlib.util.spec_from_file_location("graph", "cli/commands/graph.py")
    graph_module = importlib.util.module_from_spec(spec)
    sys.modules["cli.commands.graph"] = graph_module
    spec.loader.exec_module(graph_module)

    @click.group(invoke_without_command=True)
    @click.pass_context
    def cli(ctx):
        """Graph session CLI.

        Run 'session' to start interactive voice-driven graph execution.
        """
        if ctx.invoked_subcommand is None:
            # Default to session
            ctx.invoke(graph_module.session)

    cli.add_command(graph_module.graph)

    cli()


if __name__ == "__main__":
    main()
