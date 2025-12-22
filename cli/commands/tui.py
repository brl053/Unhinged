"""TUI command - Native terminal user interface.

Entry point for the Unhinged terminal UI.
Uses in-house terminal renderer (libs/python/terminal).

Usage:
    unhinged tui           # Launch native TUI (main interface)
    unhinged tui demo      # Rich component demo
"""

import click

from cli.tui.console import console


@click.group(invoke_without_command=True)
@click.pass_context
def tui(ctx: click.Context) -> None:
    """TUI - Terminal User Interface.

    Run without subcommand to launch the native terminal interface.
    """
    if ctx.invoked_subcommand is None:
        # Default: launch native TUI
        from libs.python.terminal.unhinged import run_landing

        run_landing()


@tui.command()
def square() -> None:
    """Render a 4x4 square using box-drawing characters.

    This is the first happy path test rendered live.
    Verifies Unicode box-drawing works in your terminal.
    """
    console.print()
    console.print("[bold cyan]4x4 Box-Drawing Square[/bold cyan]")
    console.print()

    # The exact same box from our e2e test
    box = "┌──┐\n│  │\n│  │\n└──┘"
    console.print(box)

    console.print()
    console.print("[dim]Characters: ┌ ┐ └ ┘ │ ─[/dim]")
    console.print("[dim]If you see boxes or ? marks, your terminal lacks UTF-8 support.[/dim]")
    console.print()


@tui.command()
def panel() -> None:
    """Render a Rich panel to verify styling.

    Shows how Rich panels use box-drawing characters.
    """
    from rich.panel import Panel

    console.print()
    console.print(
        Panel(
            "This is a Rich panel.\nIt uses box-drawing characters for borders.",
            title="[ Panel Test ]",
            border_style="cyan",
        )
    )
    console.print()


@tui.command()
def demo() -> None:
    """Full TUI demo showing all primitives.

    Renders multiple components to verify complete TUI stack.
    """
    from rich.panel import Panel
    from rich.table import Table

    console.print()
    console.print("[bold magenta]═══ TUI Demo ═══[/bold magenta]")
    console.print()

    # 1. Raw box-drawing
    console.print("[bold]1. Raw Box-Drawing (4x4 square):[/bold]")
    console.print("┌──┐")
    console.print("│  │")
    console.print("│  │")
    console.print("└──┘")
    console.print()

    # 2. Rich Panel
    console.print("[bold]2. Rich Panel:[/bold]")
    console.print(Panel("Panel content", title="Title", border_style="blue"))
    console.print()

    # 3. Rich Table
    console.print("[bold]3. Rich Table:[/bold]")
    table = Table(title="Sample Table")
    table.add_column("#", style="dim")
    table.add_column("Name", style="cyan")
    table.add_column("Status", style="green")
    table.add_row("1", "Graph A", "Ready")
    table.add_row("2", "Graph B", "Pending")
    console.print(table)
    console.print()

    # 4. Style test
    console.print("[bold]4. Style Attributes:[/bold]")
    console.print("  [bold]Bold[/bold]  [italic]Italic[/italic]  [underline]Underline[/underline]")
    console.print("  [red]Red[/red]  [green]Green[/green]  [blue]Blue[/blue]  [yellow]Yellow[/yellow]")
    console.print()

    console.print("[bold green]✓ TUI demo complete[/bold green]")
    console.print()
