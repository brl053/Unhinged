"""Orchestration commands: orchestrate, solve.

Transform natural language prompts into orchestrated Linux command DAGs.
"""

import asyncio
import json

import click

from cli.utils import log_error, log_info, log_success
from libs.python.command_orchestration import (
    CommandExecutor,
    DAGBuilder,
    ManPageIndexer,
    SemanticSearchEngine,
)
from libs.python.command_orchestration.document_loader import DocumentLoader


@click.group()
def orchestrate():
    """Command orchestration: transform prompts into DAGs.

    Solves system problems by discovering relevant Linux commands,
    building execution DAGs, and running them in parallel.
    """
    pass


@orchestrate.command()
@click.argument("prompt", nargs=-1, required=True)
@click.option("-l", "--limit", type=int, default=5, help="Max commands to discover (default: 5)")
@click.option(
    "-o", "--output", type=click.Choice(["text", "json"]), default="text", help="Output format (default: text)"
)
def solve(prompt, limit, output):
    """Solve a system problem using command orchestration.

    Example: unhinged orchestrate solve "My headphone volume is too low"
    """
    prompt_str = " ".join(prompt)
    log_info(f"Solving: {prompt_str}")

    try:
        # Run async orchestration
        result = asyncio.run(_orchestrate(prompt_str, limit))

        if output == "json":
            click.echo(json.dumps(result, indent=2))
        else:
            _print_text_result(result)

        if result["execution_success"]:
            log_success("Orchestration completed successfully")
        else:
            log_error("Orchestration completed with errors")

    except Exception as e:
        log_error(f"Orchestration failed: {e}")
        raise


async def _orchestrate(prompt: str, limit: int) -> dict:
    """Execute orchestration workflow"""
    # Step 1: Index man pages
    log_info("Indexing man pages...")
    indexer = ManPageIndexer()
    entries = indexer.build_index()

    # Step 1b: Load organizational documents for context
    log_info("Loading organizational context...")
    doc_loader = DocumentLoader()
    org_docs = doc_loader.combine_documents()
    if org_docs:
        indexer.load_organizational_documents(org_docs)

    # Step 2: Search for relevant commands
    log_info("Searching for relevant commands...")
    search_engine = SemanticSearchEngine(entries)
    search_results = search_engine.search(prompt, limit=limit)

    # Step 3: Build DAG
    log_info("Building execution DAG...")
    commands = [r.command for r in search_results]
    dag_builder = DAGBuilder()
    dag = dag_builder.build_from_commands(commands)

    # Step 4: Execute DAG
    log_info("Executing commands in parallel...")
    executor = CommandExecutor()
    execution_result = await executor.execute_dag(dag)

    return {
        "prompt": prompt,
        "commands": commands,
        "search_results": [
            {
                "command": r.command,
                "similarity": r.similarity,
                "reasoning": r.reasoning,
            }
            for r in search_results
        ],
        "execution_success": execution_result.success,
        "execution_results": {
            node_id: {
                "returncode": result.returncode,
                "stdout": result.stdout[:200],
                "stderr": result.stderr[:200],
            }
            for node_id, result in execution_result.results.items()
        },
    }


def _print_text_result(result: dict) -> None:
    """Print orchestration result in text format"""
    click.echo("\n" + "=" * 60)
    click.echo(f"Prompt: {result['prompt']}")
    click.echo("=" * 60)

    click.echo("\nDiscovered Commands:")
    for i, cmd in enumerate(result["commands"], 1):
        click.echo(f"  {i}. {cmd}")

    click.echo("\nSearch Results:")
    for r in result["search_results"]:
        click.echo(f"  • {r['command']} (similarity: {r['similarity']:.2f})")
        click.echo(f"    {r['reasoning']}")

    click.echo("\nExecution Results:")
    for node_id, res in result["execution_results"].items():
        status = "✓" if res["returncode"] == 0 else "✗"
        click.echo(f"  {status} {node_id}: returncode={res['returncode']}")
        if res["stdout"]:
            click.echo(f"    stdout: {res['stdout'][:100]}...")
