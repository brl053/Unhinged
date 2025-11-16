"""Code analysis commands: analyze upstream/downstream, usages, imports."""


import click

from cli.utils import log_error, log_success


@click.group()
def analyze():
    """Code analysis commands using libcst.

    Analyze Python code structure, dependencies, and usage patterns.
    """
    pass


@analyze.command(name="upstream-downstream")
@click.argument("target")
def upstream_downstream(target):
    """Analyze upstream/downstream dependencies for a symbol.

    TARGET format: filepath/SymbolName or filepath.py/function_name

    Examples:
      ./unhinged dev analyze upstream-downstream build/modules/dual_system_builder.py/DualSystemBuilder
      ./unhinged dev analyze upstream-downstream control/cli/main.py/cli
    """
    try:
        from cli.analysis.libcst_analyzer import LibcstAnalyzer

        analyzer = LibcstAnalyzer()
        result = analyzer.analyze_upstream_downstream(target)

        if result["success"]:
            log_success(f"Analysis complete for {target}")
            _print_analysis_result(result)
            return 0
        else:
            log_error(result.get("error", "Analysis failed"))
            return 1

    except ImportError:
        log_error("libcst not installed. Run: pip install libcst>=0.4.0")
        return 1
    except Exception as e:
        log_error(f"Analysis failed: {e}")
        return 1


@analyze.command(name="usages")
@click.argument("symbol")
@click.option(
    "-p",
    "--path",
    default=".",
    help="Search path (default: current directory)",
)
def usages(symbol, path):
    """Find all usages of a symbol in the codebase.

    Examples:
      ./unhinged dev analyze usages BuildUtils
      ./unhinged dev analyze usages get_python -p control/
    """
    try:
        from cli.analysis.libcst_analyzer import LibcstAnalyzer

        analyzer = LibcstAnalyzer()
        result = analyzer.find_usages(symbol, path)

        if result["success"]:
            log_success(f"Found {len(result['usages'])} usages of '{symbol}'")
            _print_usages_result(result)
            return 0
        else:
            log_error(result.get("error", "Search failed"))
            return 1

    except ImportError:
        log_error("libcst not installed. Run: pip install libcst>=0.4.0")
        return 1
    except Exception as e:
        log_error(f"Search failed: {e}")
        return 1


@analyze.command(name="imports")
@click.argument("filepath")
def imports(filepath):
    """Analyze imports in a Python file.

    Shows all imports, their sources, and usage patterns.

    Examples:
      ./unhinged dev analyze imports control/cli/main.py
      ./unhinged dev analyze imports libs/event-framework/event_bus.py
    """
    try:
        from cli.analysis.libcst_analyzer import LibcstAnalyzer

        analyzer = LibcstAnalyzer()
        result = analyzer.analyze_imports(filepath)

        if result["success"]:
            log_success(f"Import analysis for {filepath}")
            _print_imports_result(result)
            return 0
        else:
            log_error(result.get("error", "Analysis failed"))
            return 1

    except ImportError:
        log_error("libcst not installed. Run: pip install libcst>=0.4.0")
        return 1
    except Exception as e:
        log_error(f"Analysis failed: {e}")
        return 1


def _print_analysis_result(result):
    """Pretty-print upstream/downstream analysis result."""
    click.echo("\n" + "=" * 60)
    click.echo(f"Symbol: {result.get('symbol', 'N/A')}")
    click.echo(f"File: {result.get('file', 'N/A')}")
    click.echo("=" * 60)

    upstream = result.get("upstream", [])
    if upstream:
        click.echo("\n📤 UPSTREAM (dependencies):")
        for item in upstream:
            click.echo(f"  • {item}")
    else:
        click.echo("\n📤 UPSTREAM: None")

    downstream = result.get("downstream", [])
    if downstream:
        click.echo("\n📥 DOWNSTREAM (dependents):")
        for item in downstream:
            click.echo(f"  • {item}")
    else:
        click.echo("\n📥 DOWNSTREAM: None")

    click.echo()


def _print_usages_result(result):
    """Pretty-print usages result."""
    click.echo("\n" + "=" * 60)
    click.echo(f"Symbol: {result.get('symbol', 'N/A')}")
    click.echo("=" * 60 + "\n")

    for usage in result.get("usages", []):
        click.echo(f"  {usage['file']}:{usage['line']}")
        click.echo(f"    {usage['context']}")
        click.echo()


def _print_imports_result(result):
    """Pretty-print imports analysis result."""
    click.echo("\n" + "=" * 60)
    click.echo(f"File: {result.get('file', 'N/A')}")
    click.echo("=" * 60 + "\n")

    for imp in result.get("imports", []):
        click.echo(f"  {imp['type']}: {imp['module']}")
        if imp.get("items"):
            for item in imp["items"]:
                click.echo(f"    • {item}")
    click.echo()
