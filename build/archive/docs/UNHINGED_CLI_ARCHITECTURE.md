# Unhinged CLI Architecture

## Overview

The Unhinged CLI is a consolidated Python Click-based command framework that provides intent-driven workflows through the `unhinged` command. The architecture follows a layered design with clear separation of concerns.

## Entry Points

### Bash Shim: `./unhinged`
- Located at repository root
- Resolves venv Python or falls back to system Python
- Delegates to: `python -m control.cli`

### Python Entry Point: `control.cli.__main__`
- Imports and delegates to `cli.core.app.cli`
- Kept for backward compatibility

### Main CLI Group: `cli.core.app.cli`
- Click group that registers all command groups
- Registered commands: system, dev, admin, vm, generate, transcribe, image, voice, video, parse, shortform, chat, orchestrate, prompt, query

## The `unhinged query` Command

### Purpose
Generates structured execution plans from natural language queries and optionally executes them. Currently supports audio volume diagnostics (v1).

### Command Signature
```bash
unhinged query [OPTIONS] [PROMPT]
```

### Options
- `-f, --file`: Read query from file
- `-o, --output`: Output format (yaml|json, default: yaml)
- `--execute`: Execute the compiled plan
- `--dry-run`: Compile to graph without executing
- `--explain`: Show LLM-backed reasoning
- `--hypothesis`: Select specific hypothesis (1-based index)

### Execution Flow

1. **Input Parsing** (`cli/commands/query.py:595-625`)
   - Accepts prompt from args, file, or stdin
   - Validates non-empty query

2. **Hypothesis Generation** (`libs/python/query_planner/dsl.py`)
   - `build_audio_volume_hypotheses()` creates diagnostic hypotheses
   - Returns `HypothesisSet` with multiple approaches

3. **Hypothesis Selection** (`cli/commands/query.py:632-644`)
   - If `--hypothesis` provided: use directly
   - Otherwise: prompt user to select from list

4. **Plan Generation** (`libs/python/query_planner/dsl.py`)
   - `build_audio_volume_plan()` creates `QueryPlan`
   - Plan contains nodes (unix commands) and edges (dependencies)

5. **Plan Compilation** (`libs/python/query_planner/dsl.py`)
   - `plan_to_graph()` converts QueryPlan to DAG
   - Creates `Graph` with nodes and edges

6. **Execution** (if `--execute`)
   - **Dry Run**: Output graph structure (nodes + edges)
   - **Full Execution**: `GraphExecutor.execute()` runs DAG in parallel
     - Topological sort via Kahn's algorithm
     - Parallel execution of independent nodes
     - Collects stdout/stderr/returncode per node

7. **Reasoning** (if `--explain`)
   - `ReasoningEngine` generates LLM-backed explanations
   - Plan node reasoning: why each command was selected
   - Execution result interpretation: what output means
   - Remediation generation: suggested fixes

8. **Output** (`cli/commands/query.py:665-668`)
   - YAML or JSON format
   - Includes plan, execution results, reasoning, remediation

## Key Components

### Query Planner (`libs/python/query_planner/`)
- **dsl.py**: QueryPlan, PlanNode, PlanEdge, build_audio_volume_plan
- **hypothesis.py**: Hypothesis, HypothesisSet for multi-approach diagnostics
- **intent_graph.py**: Intent taxonomy and LLM-based intent analysis

### Graph Library (`libs/python/graph/`)
- **graph.py**: Graph, GraphExecutor, GraphExecutionResult
- **nodes.py**: GraphNode, UnixCommandNode, UserInputNode, SubgraphNode
- Async DAG executor with parallel execution support

### Reasoning Engine (`libs/python/command_orchestration/`)
- LLM-backed reasoning for plan generation and execution interpretation
- Pattern-based remediation fallback for audio volume issues

### CLI Commands (`cli/commands/`)
- Modular command structure
- Each command is a Click group or command
- Unified logging via `cli.utils`

## Data Flow Example: Audio Volume Diagnosis

```
User Query: "my headphone volume is too low"
    ↓
build_audio_volume_hypotheses()
    ↓
HypothesisSet with 2-3 approaches:
  1. Check ALSA mixer levels
  2. Check USB device status
  3. Check PipeWire configuration
    ↓
User selects hypothesis (or --hypothesis 1)
    ↓
build_audio_volume_plan() creates QueryPlan:
  - Node: "alsa_mixer" → amixer -c 1 get PCM
  - Node: "usb_devices" → lsusb
  - Edge: alsa_mixer → usb_devices (dependency)
    ↓
plan_to_graph() creates DAG
    ↓
GraphExecutor.execute() runs in parallel:
  - alsa_mixer and usb_devices can run in parallel
  - Collects output
    ↓
Output results + optional LLM reasoning
```

## Testing

All tests pass with conftest.py adding project root to Python path:
- `tests/test_cli_query.py`: 6 tests covering plan generation, execution, dry-run, explain flag
- Run: `./unhinged dev test test_cli_query`

## Architecture Principles

1. **Headless-First**: Backend logic works independently before UI integration
2. **Intent-Driven**: Natural language queries map to structured plans
3. **DAG-Based Execution**: Parallel execution of independent operations
4. **LLM-Backed Reasoning**: Optional explanations for diagnostics and remediation
5. **Modular Commands**: Each command is self-contained and testable

