"""TUI command - Terminal UI primitives and testing.

Renders TUI components directly to terminal for visual verification.
This is the entry point for TUI development and testing.

Usage:
    unhinged tui           # Show TUI demo menu
    unhinged tui square    # Render 4x4 square
    unhinged tui panel     # Render Rich panel
"""

import click

from cli.tui.console import console


@click.group(invoke_without_command=True)
@click.pass_context
def tui(ctx: click.Context) -> None:
    """TUI - Terminal User Interface.

    Run without subcommand to launch interactive TUI app.
    Use subcommands for component testing and previews.
    """
    if ctx.invoked_subcommand is None:
        # Default: launch interactive TUI app
        from cli.tui.app import run_app

        run_app()


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


@tui.command("graph")
@click.argument("name", default="sample")
def graph_cmd(name: str) -> None:
    """Render a graph as visual DAG.

    Shows nodes as boxes and edges as arrows in topological layers.

    Examples:
        unhinged tui graph          # Sample graph
        unhinged tui graph email    # Named graph (if exists)
    """
    from cli.tui import graph_dag

    # Sample graph for demo
    sample_graph = {
        "name": name if name != "sample" else "Sample Workflow",
        "description": "Demo graph visualization",
        "nodes": [
            {"id": "input", "type": "user_input"},
            {"id": "process", "type": "unix"},
            {"id": "llm", "type": "llm"},
            {"id": "output", "type": "api"},
        ],
        "edges": [
            {"source": "input", "target": "process"},
            {"source": "process", "target": "llm"},
            {"source": "llm", "target": "output"},
        ],
    }

    graph_dag(sample_graph)


@tui.command("files")
@click.argument("path", default=".")
@click.option("--depth", "-d", default=3, help="Max depth to traverse")
@click.option("--pattern", "-p", multiple=True, help="Include patterns (glob)")
def files_cmd(path: str, depth: int, pattern: tuple[str, ...]) -> None:
    """Render a file tree.

    Shows directory structure for navigation.

    Examples:
        unhinged tui files              # Current directory
        unhinged tui files cli          # cli/ directory
        unhinged tui files . -p "*.py"  # Only Python files
    """
    from cli.tui import file_tree

    patterns = list(pattern) if pattern else None
    file_tree(path, max_depth=depth, patterns=patterns)


@tui.command("layout")
def layout_cmd() -> None:
    """Render split pane layout demo.

    Shows the left nav + right widget corral architecture.
    This is the foundation for the full TUI interface.
    """
    from cli.tui import file_tree_panel, graph_dag_panel, split_layout

    # Sample graph for right pane
    sample_graph = {
        "name": "Email Workflow",
        "nodes": [
            {"id": "fetch", "type": "api"},
            {"id": "parse", "type": "unix"},
            {"id": "respond", "type": "llm"},
        ],
        "edges": [
            {"source": "fetch", "target": "parse"},
            {"source": "parse", "target": "respond"},
        ],
    }

    # Left: file tree, Right: graph
    left = file_tree_panel(".", max_depth=2, title=None)
    right = graph_dag_panel(sample_graph)

    console.print()
    console.print("[bold]Split Pane Layout Demo[/bold]")
    split_layout(left, right, left_title="Files", right_title="Graph")


@tui.command("commands")
def commands_cmd() -> None:
    """List available TUI subcommands."""
    console.print()
    console.print("[bold]TUI Commands[/bold]")
    console.print()
    console.print("[dim]Primitives:[/dim]")
    console.print("  [cyan]unhinged tui square[/cyan]   - Render 4x4 box-drawing square")
    console.print("  [cyan]unhinged tui panel[/cyan]    - Render Rich panel")
    console.print("  [cyan]unhinged tui demo[/cyan]     - Full TUI demo")
    console.print()
    console.print("[dim]Components:[/dim]")
    console.print("  [cyan]unhinged tui graph[/cyan]    - Render graph as visual DAG")
    console.print("  [cyan]unhinged tui files[/cyan]    - Render file tree")
    console.print("  [cyan]unhinged tui layout[/cyan]   - Split pane layout demo")
    console.print()
    console.print("[dim]Debug:[/dim]")
    console.print("  [cyan]unhinged tui preview[/cyan]  - Static layout preview")
    console.print("  [cyan]unhinged tui commands[/cyan] - This help")
    console.print()


@tui.command("preview")
def preview_cmd() -> None:
    """Static preview of TUI layout (no interaction).

    Renders the TUI layout once without keyboard input.
    Useful for debugging layout issues.
    """
    import shutil

    from cli.tui.app import render_state
    from cli.tui.state import create_initial_state

    # Get terminal size
    term_width, term_height = shutil.get_terminal_size((80, 24))

    console.print()
    console.print("[bold]TUI Layout Preview[/bold]")
    console.print(f"[dim]Terminal size: {term_width}x{term_height}[/dim]")
    console.print()

    # Create a mock session for preview
    from libs.python.graph.context import ContextStore

    context_store = ContextStore()
    session_id = "preview-session"
    session_ctx = context_store.create(session_id)
    state = create_initial_state(session_id, session_ctx)

    # Render the current voice-first layout
    layout = render_state(state)
    console.print(layout)
