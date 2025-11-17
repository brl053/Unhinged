"""Query command: structured plans and optional execution.

@llm-type cli.query
@llm-does expose `unhinged query` for intent-driven workflows
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

import click
import yaml

from cli.utils import log_error, log_info, log_success
from libs.python.graph import GraphExecutor
from libs.python.query_planner import build_audio_volume_plan, plan_to_graph


@click.command(name="query")
@click.argument("prompt", nargs=-1, required=False)
@click.option(
    "-f",
    "--file",
    type=click.Path(exists=True),
    help="Read query from file instead of command arguments",
)
@click.option(
    "-o",
    "--output",
    type=click.Choice(["yaml", "json"]),
    default="yaml",
    help="Output format for the plan and optional execution (default: yaml)",
)
@click.option(
    "--execute",
    is_flag=True,
    default=False,
    help="Execute the compiled plan using the graph executor.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Compile the plan into a graph without executing it (with --execute).",
)
def query(prompt, file, output, execute, dry_run):  # type: ignore[override]
    """Generate a structured execution plan from a natural language query.

    Usage examples:
      unhinged query "my headphone volume is too low on the logitech pro x2"
      unhinged query "why is my audio low from youtube and the browser?"
      unhinged query -f query.txt
      echo "headphone volume too low" | unhinged query

    v1 supports low/quiet audio volume diagnostics (headphones + system audio).
    """

    # Determine query text
    if file:
        query_text = Path(file).read_text().strip()
        log_info(f"Reading query from: {file}")
    elif prompt:
        query_text = " ".join(prompt)
    else:
        if not sys.stdin.isatty():
            query_text = sys.stdin.read().strip()
            log_info("Reading query from stdin")
        else:
            log_error("No query provided. Use: unhinged query --help")
            sys.exit(1)

    if not query_text:
        log_error("Query cannot be empty")
        sys.exit(1)

    log_info(f"Planning query: {query_text}")

    try:
        plan = build_audio_volume_plan(query_text)
    except ValueError as err:
        log_error(str(err))
        sys.exit(1)

    result: dict[str, object] = {
        "query": query_text,
        "plan": plan.to_json_compatible(),
    }

    if execute:
        graph = plan_to_graph(plan)
        if dry_run:
            log_info("Dry run: compiled plan into graph; " f"nodes={len(graph.nodes)}, edges={len(graph.edges)}.")
            result["execution"] = {
                "dry_run": True,
                "graph": {
                    "nodes": sorted(graph.nodes.keys()),
                    "edges": [{"from": src, "to": dst} for (src, dst) in graph.edges],
                },
            }
        else:
            log_info("Executing plan via graph executor...")
            executor = GraphExecutor()
            exec_result = asyncio.run(executor.execute(graph))

            node_results = {}
            for node_id, node_res in exec_result.node_results.items():
                output_dict = node_res.output
                stdout = str(output_dict.get("stdout", ""))
                stderr = str(output_dict.get("stderr", ""))
                node_results[node_id] = {
                    "success": node_res.success,
                    "error": node_res.error,
                    "stdout": stdout[:500],
                    "stderr": stderr[:500],
                    "returncode": output_dict.get("returncode"),
                }

            result["execution"] = {
                "dry_run": False,
                "success": exec_result.success,
                "error_message": exec_result.error_message,
                "execution_order": exec_result.execution_order,
                "node_results": node_results,
            }

            if exec_result.success:
                log_success("Query execution completed successfully")
            else:
                log_error("Query execution completed with errors")

    # Emit result
    if output == "json":
        click.echo(json.dumps(result, indent=2))
    else:
        click.echo(yaml.safe_dump(result, sort_keys=False))


__all__ = ["query"]
