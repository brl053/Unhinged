"""Orchestration commands: orchestrate, solve.

Transform natural language prompts into orchestrated Linux command DAGs.

@llm-type cli.orchestrate
@llm-does expose `unhinged orchestrate solve` with LLM-backed reasoning
"""

import asyncio
import json

import click

from cli.utils import log_error, log_info, log_success
from libs.python.command_orchestration import (
    CommandExecutor,
    CommandExecutorWithReasoning,
    DAGBuilder,
    ManPageIndexer,
    SemanticSearchEngine,
    SemanticSearchWithReasoning,
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
@click.option(
    "--explain",
    is_flag=True,
    default=False,
    help="Show detailed LLM-backed reasoning for each step (command selection, DAG edges, result interpretation)",
)
def solve(prompt, limit, output, explain):
    """Solve a system problem using command orchestration.

    Example: unhinged orchestrate solve "My headphone volume is too low"
    Example with reasoning: unhinged orchestrate solve --explain "My headphone volume is too low"
    """
    prompt_str = " ".join(prompt)
    log_info(f"Solving: {prompt_str}")

    try:
        # Run async orchestration
        result = asyncio.run(_orchestrate(prompt_str, limit, explain=explain))

        if output == "json":
            click.echo(json.dumps(result, indent=2))
        else:
            _print_text_result(result, explain=explain)

        if result["execution_success"]:
            log_success("Orchestration completed successfully")
        else:
            log_error("Orchestration completed with errors")

    except Exception as e:
        log_error(f"Orchestration failed: {e}")
        raise


async def _orchestrate(prompt: str, limit: int, explain: bool = False) -> dict:
    """Execute orchestration workflow with optional LLM reasoning.

    Parameters
    ----------
    prompt : str
        User query
    limit : int
        Max commands to discover
    explain : bool
        If True, use LLM-backed reasoning for each step

    Returns
    -------
    dict
        Orchestration result with optional reasoning
    """
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

    # Step 2: Search for relevant commands (with optional LLM reasoning)
    log_info("Searching for relevant commands...")
    search_engine = SemanticSearchEngine(entries)

    if explain:
        search_wrapper = SemanticSearchWithReasoning(search_engine)
        search_results = await search_wrapper.search_with_reasoning(
            prompt=prompt,
            limit=limit,
            use_llm_reasoning=True,
        )
    else:
        search_results = search_engine.search(prompt, limit=limit)

    # Step 3: Build DAG (with optional LLM edge reasoning)
    log_info("Building execution DAG...")
    commands = [r.command for r in search_results]
    dag_builder = DAGBuilder()

    # Note: DAGBuilderWithReasoning is available for pipeline-based reasoning
    # but for independent commands, we use the underlying builder
    dag = dag_builder.build_from_commands(commands)

    # Step 4: Execute DAG (with optional LLM result interpretation)
    log_info("Executing commands in parallel...")
    executor = CommandExecutor()

    if explain:
        executor_wrapper = CommandExecutorWithReasoning(executor)
        execution_result_with_interp = await executor_wrapper.execute_dag_with_interpretation(
            dag=dag,
            use_llm_interpretation=True,
        )
        execution_result = execution_result_with_interp.dag_result
        result_interpretations = execution_result_with_interp.result_interpretations
    else:
        execution_result = await executor.execute_dag(dag)
        result_interpretations = {}

    # Build result
    result = {
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

    # Add reasoning if requested
    if explain:
        result["reasoning"] = {
            "command_selection": {r.command: r.reasoning for r in search_results},
            "result_interpretations": {
                node_id: result_interpretations[node_id].interpretation
                for node_id in result_interpretations
                if result_interpretations[node_id].interpretation
            },
        }

    return result


def _print_text_result(result: dict, explain: bool = False) -> None:
    """Print orchestration result in text format.

    Parameters
    ----------
    result : dict
        Orchestration result
    explain : bool
        If True, display detailed reasoning
    """
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

    # Display reasoning if requested
    if explain and "reasoning" in result:
        click.echo("\n" + "-" * 60)
        click.echo("LLM-Backed Reasoning:")
        click.echo("-" * 60)

        if "command_selection" in result["reasoning"]:
            click.echo("\nCommand Selection Reasoning:")
            for cmd, reasoning in result["reasoning"]["command_selection"].items():
                click.echo(f"  • {cmd}:")
                click.echo(f"    {reasoning}")

        if "result_interpretations" in result["reasoning"]:
            click.echo("\nResult Interpretations:")
            for node_id, interpretation in result["reasoning"]["result_interpretations"].items():
                click.echo(f"  • {node_id}:")
                click.echo(f"    {interpretation}")

    click.echo("\nExecution Results:")
    for node_id, res in result["execution_results"].items():
        status = "✓" if res["returncode"] == 0 else "✗"
        click.echo(f"  {status} {node_id}: returncode={res['returncode']}")
        if res["stdout"]:
            click.echo(f"    stdout: {res['stdout'][:100]}...")
