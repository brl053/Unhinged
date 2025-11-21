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
from libs.python.command_orchestration import ReasoningEngine
from libs.python.graph import GraphExecutor
from libs.python.query_planner import (
    build_audio_volume_hypotheses,
    build_audio_volume_plan,
    plan_to_graph,
)


def _prompt_for_hypothesis_selection(hypothesis_set) -> str:
    """Prompt user to select a diagnostic hypothesis.

    Returns the selected hypothesis ID.
    """
    print("\n📋 Multiple diagnostic approaches available:")
    for i, hyp in enumerate(hypothesis_set.hypotheses, 1):
        print(f"  {i}. {hyp.name}")
        print(f"     {hyp.description}")

    while True:
        try:
            choice = input("\nSelect hypothesis (number): ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(hypothesis_set.hypotheses):
                selected = hypothesis_set.hypotheses[idx]
                hypothesis_set.select_hypothesis(selected.id)
                log_info(f"Selected hypothesis: {selected.name}")
                return selected.id
            print(f"Please enter a number between 1 and {len(hypothesis_set.hypotheses)}")
        except ValueError:
            print("Invalid input. Please enter a number.")


async def _generate_plan_reasoning(query_text: str, plan) -> dict[str, str]:
    """Generate LLM-backed reasoning for plan nodes.

    Parameters
    ----------
    query_text : str
        User's natural language query
    plan : QueryPlan
        The generated query plan

    Returns
    -------
    Dict[str, str]
        Mapping of node_id to reasoning text
    """
    reasoning_engine = ReasoningEngine()
    node_reasoning: dict[str, str] = {}

    # Extract command descriptions from plan nodes
    for node in plan.nodes:
        if node.type == "unix_command":
            command = node.params.get("command", "")
            description = node.description

            try:
                # Generate reasoning for why this command is in the plan
                user_message = f"""Query: {query_text}

Command: {command}
Description: {description}

Explain why this command is relevant to the user's query."""

                system_prompt = """You are an expert at explaining why specific diagnostic commands are relevant.
Generate a brief one-sentence explanation of why this command helps diagnose the issue.

Format: Return ONLY valid JSON:
{
  "reasoning": "One sentence explanation"
}"""

                response_text = await reasoning_engine._call_llm(system_prompt, user_message)
                result = json.loads(response_text)
                node_reasoning[node.id] = result.get("reasoning", description)
            except Exception as exc:
                log_error(f"Failed to generate reasoning for {node.id}: {exc}")
                node_reasoning[node.id] = description

    return node_reasoning


def _build_query_result(query_text: str, plan, execute: bool, dry_run: bool) -> dict[str, object]:
    """Build query result without reasoning."""
    result: dict[str, object] = {
        "query": query_text,
        "plan": plan.to_json_compatible(),
    }

    if execute:
        graph = plan_to_graph(plan)
        if dry_run:
            log_info("Dry run: compiled plan into graph; " f"nodes={len(graph.nodes)}, edges={len(graph.edges)}.")
            edges_list = []
            for src, dst, condition in graph.edges:
                edge_dict: dict[str, str | None] = {"from": src, "to": dst}
                if condition is not None:
                    edge_dict["condition"] = condition
                edges_list.append(edge_dict)
            result["execution"] = {
                "dry_run": True,
                "graph": {
                    "nodes": sorted(graph.nodes.keys()),
                    "edges": edges_list,
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

    return result


async def _generate_execution_reasoning(
    reasoning_engine: ReasoningEngine,
    exec_result,
    plan,
) -> dict[str, str]:
    """Generate LLM-backed interpretation of execution results.

    Parameters
    ----------
    reasoning_engine : ReasoningEngine
        The reasoning engine instance
    exec_result : ExecutionResult
        The execution result from GraphExecutor
    plan : QueryPlan
        The original query plan

    Returns
    -------
    Dict[str, str]
        Mapping of node_id to interpretation text
    """
    result_interpretations: dict[str, str] = {}

    for node_id, node_res in exec_result.node_results.items():
        try:
            output_dict = node_res.output
            stdout = str(output_dict.get("stdout", ""))
            stderr = str(output_dict.get("stderr", ""))
            returncode = output_dict.get("returncode", -1)

            # Find the command from the plan
            command = ""
            for node in plan.nodes:
                if node.id == node_id and node.type == "unix_command":
                    command = node.params.get("command", "")
                    break

            if command:
                interpretation = await reasoning_engine.reason_execution_result(
                    command=command,
                    exit_code=returncode,
                    stdout=stdout[:500],
                    stderr=stderr[:500],
                )
                result_interpretations[node_id] = interpretation
        except Exception as exc:
            log_error(f"Failed to generate interpretation for {node_id}: {exc}")
            result_interpretations[node_id] = "Command executed"

    return result_interpretations


async def _generate_and_execute_remediation(
    reasoning_engine: ReasoningEngine,
    query_text: str,
    exec_result,
    plan,
) -> dict[str, Any]:
    """Generate remediation commands based on diagnostic results and execute them.

    Uses LLM-based YAML generation with pattern-based fallback.

    Parameters
    ----------
    reasoning_engine : ReasoningEngine
        The reasoning engine instance
    query_text : str
        Original user query
    exec_result : ExecutionResult
        The execution result from diagnostic phase
    plan : QueryPlan
        The original query plan

    Returns
    -------
    Dict[str, Any]
        Remediation results with commands executed and their outcomes
    """

    remediation_results: dict[str, Any] = {
        "commands_generated": [],
        "commands_executed": [],
        "success": True,
    }

    # Collect diagnostic output
    diagnostic_output = _collect_diagnostic_output(exec_result)

    # For now, skip LLM-based remediation due to performance issues
    # TODO: Implement async LLM call with proper timeout handling
    # Use pattern-based detection as primary approach
    log_info("Using pattern-based remediation...")
    return await _pattern_based_remediation(exec_result)


def _collect_diagnostic_output(exec_result) -> str:
    """Collect diagnostic output from all executed nodes.

    Parameters
    ----------
    exec_result : ExecutionResult
        The execution result from diagnostic phase

    Returns
    -------
    str
        Combined diagnostic output
    """
    diagnostic_output = ""
    for node_id, node_res in exec_result.node_results.items():
        output_dict = node_res.output
        stdout = str(output_dict.get("stdout", ""))
        stderr = str(output_dict.get("stderr", ""))
        returncode = output_dict.get("returncode", -1)
        if stdout:
            diagnostic_output += f"\n=== {node_id} ===\n{stdout}\n"
        if stderr and returncode != 0:
            diagnostic_output += f"Error: {stderr}\n"
    return diagnostic_output


async def _execute_remediation_commands(remediation_data: dict[str, Any]) -> dict[str, Any]:
    """Execute remediation commands from LLM-generated data.

    Parameters
    ----------
    remediation_data : Dict[str, Any]
        Remediation data with diagnosis and remediation_commands

    Returns
    -------
    Dict[str, Any]
        Execution results
    """
    import subprocess

    remediation_results: dict[str, Any] = {
        "commands_generated": [],
        "commands_executed": [],
        "success": True,
    }

    remediation_results["diagnosis"] = remediation_data.get("diagnosis", "")
    remediation_commands = remediation_data.get("remediation_commands", [])

    if not remediation_commands:
        return remediation_results

    log_info(f"Executing {len(remediation_commands)} remediation command(s)...")

    for cmd_spec in remediation_commands:
        command = cmd_spec.get("command", "")
        description = cmd_spec.get("description", "")

        if not command:
            continue

        remediation_results["commands_generated"].append(
            {
                "command": command,
                "description": description,
            }
        )

        try:
            log_info(f"Executing remediation: {description}")
            loop = asyncio.get_event_loop()
            result_proc = await loop.run_in_executor(
                None,
                lambda cmd=command: subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=10,
                ),
            )

            remediation_results["commands_executed"].append(
                {
                    "command": command,
                    "description": description,
                    "success": result_proc.returncode == 0,
                    "stdout": result_proc.stdout[:200],
                    "stderr": result_proc.stderr[:200],
                    "returncode": result_proc.returncode,
                }
            )

            if result_proc.returncode == 0:
                log_success(f"✓ {description}")
            else:
                log_error(f"✗ {description} (exit code: {result_proc.returncode})")
                remediation_results["success"] = False

        except Exception as exc:
            log_error(f"Failed to execute remediation: {exc}")
            remediation_results["success"] = False

    return remediation_results


async def _pattern_based_remediation(exec_result) -> dict[str, Any]:
    """Pattern-based remediation as fallback when LLM fails.

    Parameters
    ----------
    exec_result : ExecutionResult
        The execution result from diagnostic phase

    Returns
    -------
    Dict[str, Any]
        Remediation results
    """
    import re
    import subprocess

    remediation_results: dict[str, Any] = {
        "commands_generated": [],
        "commands_executed": [],
        "success": True,
    }

    # Extract diagnostic data
    alsa_output = ""
    usb_output = ""

    for node_id, node_res in exec_result.node_results.items():
        output_dict = node_res.output
        stdout = str(output_dict.get("stdout", ""))
        if node_id == "alsa_mixer":
            alsa_output = stdout
        elif node_id == "usb_devices":
            usb_output = stdout

    # Pattern 1: Detect low volume on specific ALSA card
    # Look for "Playback XX [YY%]" where YY < 80
    volume_pattern = r"Playback (\d+) \[(\d+)%\]"
    matches = re.findall(volume_pattern, alsa_output)

    if matches:
        # Check if any volume is below 80%
        has_low_volume = any(int(percent_str) < 80 for _, percent_str in matches)

        if has_low_volume:
            # Try to find which card this is
            # For now, assume it's card 1 (Logitech) if we see it in USB devices
            if "Logitech" in usb_output or "PRO X 2" in usb_output:
                card_num = 1
                max_level = 74  # From earlier diagnostics
                command = f"amixer -c {card_num} set PCM {max_level}"
                description = f"Set Logitech PRO X2 volume to maximum (card {card_num})"

                remediation_results["commands_generated"].append(
                    {
                        "command": command,
                        "description": description,
                    }
                )

                try:
                    log_info(f"Executing remediation: {description}")
                    loop = asyncio.get_event_loop()
                    result_proc = await loop.run_in_executor(
                        None,
                        lambda cmd=command: subprocess.run(
                            cmd,
                            shell=True,
                            capture_output=True,
                            text=True,
                            timeout=10,
                        ),
                    )

                    remediation_results["commands_executed"].append(
                        {
                            "command": command,
                            "description": description,
                            "success": result_proc.returncode == 0,
                            "stdout": result_proc.stdout[:200],
                            "stderr": result_proc.stderr[:200],
                            "returncode": result_proc.returncode,
                        }
                    )

                    if result_proc.returncode == 0:
                        log_success(f"✓ {description}")
                    else:
                        log_error(f"✗ {description} (exit code: {result_proc.returncode})")
                        remediation_results["success"] = False

                except Exception as exc:
                    log_error(f"Failed to execute remediation: {exc}")
                    remediation_results["success"] = False

    return remediation_results


async def _query_with_reasoning(query_text: str, execute: bool, dry_run: bool, plan=None) -> dict[str, object]:
    """Build query result with LLM-backed reasoning.

    Generates reasoning for:
    1. Plan generation (why each diagnostic command was selected)
    2. Execution results (what the output means)
    """
    if plan is None:
        plan = build_audio_volume_plan(query_text)

    # Generate reasoning for plan nodes
    log_info("Generating plan reasoning...")
    plan_reasoning = await _generate_plan_reasoning(query_text, plan)

    reasoning_dict: dict[str, object] = {
        "plan_nodes": plan_reasoning,
    }
    result: dict[str, object] = {
        "query": query_text,
        "plan": plan.to_json_compatible(),
        "reasoning": reasoning_dict,
    }

    if execute:
        graph = plan_to_graph(plan)
        if dry_run:
            log_info("Dry run: compiled plan into graph; " f"nodes={len(graph.nodes)}, edges={len(graph.edges)}.")
            edges_list = []
            for src, dst, condition in graph.edges:
                edge_dict: dict[str, str | None] = {"from": src, "to": dst}
                if condition is not None:
                    edge_dict["condition"] = condition
                edges_list.append(edge_dict)
            result["execution"] = {
                "dry_run": True,
                "graph": {
                    "nodes": sorted(graph.nodes.keys()),
                    "edges": edges_list,
                },
            }
        else:
            log_info("Executing plan via graph executor...")
            executor = GraphExecutor()
            exec_result = await executor.execute(graph)

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

            # Generate reasoning for execution results
            log_info("Generating execution result interpretations...")
            reasoning_engine = ReasoningEngine()
            result_interpretations = await _generate_execution_reasoning(
                reasoning_engine,
                exec_result,
                plan,
            )

            result["execution"] = {
                "dry_run": False,
                "success": exec_result.success,
                "error_message": exec_result.error_message,
                "execution_order": exec_result.execution_order,
                "node_results": node_results,
            }

            # Add result interpretations to reasoning
            if result_interpretations:
                reasoning_dict["execution_results"] = result_interpretations

            # Generate and execute remediation commands
            log_info("Generating remediation commands...")
            remediation_result = await _generate_and_execute_remediation(
                reasoning_engine,
                query_text,
                exec_result,
                plan,
            )

            if remediation_result["commands_executed"]:
                result["remediation"] = remediation_result
                if remediation_result["success"]:
                    log_success("✅ Query execution completed successfully with remediation")
                else:
                    log_error("⚠️  Query execution completed with partial remediation")
            elif exec_result.success:
                log_success("Query execution completed successfully")
            else:
                log_error("Query execution completed with errors")

    return result


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
@click.option(
    "--explain",
    is_flag=True,
    default=False,
    help="Show detailed LLM-backed reasoning for plan generation and execution",
)
@click.option(
    "--hypothesis",
    type=int,
    default=None,
    help="Select a specific hypothesis (1-based index) instead of prompting",
)
def query(prompt, file, output, execute, dry_run, explain, hypothesis):  # type: ignore[override]
    """Generate a structured execution plan from a natural language query.

    Usage examples:
      unhinged query "my headphone volume is too low on the logitech pro x2"
      unhinged query "why is my audio low from youtube and the browser?"
      unhinged query --explain "my headphone volume is too low"
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
        # Build hypotheses for the query
        hypothesis_set = build_audio_volume_hypotheses(query_text)

        # Select hypothesis
        if hypothesis is not None:
            # User specified hypothesis via CLI
            if 1 <= hypothesis <= len(hypothesis_set.hypotheses):
                selected_hyp = hypothesis_set.hypotheses[hypothesis - 1]
                hypothesis_set.select_hypothesis(selected_hyp.id)
                log_info(f"Using hypothesis: {selected_hyp.name}")
            else:
                log_error(f"Invalid hypothesis index. Must be 1-{len(hypothesis_set.hypotheses)}")
                sys.exit(1)
        else:
            # Prompt user to select hypothesis
            _prompt_for_hypothesis_selection(hypothesis_set)

        # Get selected plan
        selected_hyp = hypothesis_set.get_selected()
        if not selected_hyp:
            log_error("No hypothesis selected")
            sys.exit(1)

        plan = selected_hyp.plan

        if explain:
            result_dict = asyncio.run(_query_with_reasoning(query_text, execute, dry_run, plan))
        else:
            result_dict = _build_query_result(query_text, plan, execute, dry_run)
    except ValueError as err:
        log_error(str(err))
        sys.exit(1)

    result = result_dict

    # Emit result
    if output == "json":
        click.echo(json.dumps(result, indent=2))
    else:
        click.echo(yaml.safe_dump(result, sort_keys=False))


__all__ = ["query"]
