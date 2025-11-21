# Command Orchestration Architecture

## Overview

Implement a workflow that transforms natural language prompts (e.g., "My headphone volume is too low") into orchestrated Linux command DAGs that execute in parallel with reasoning along edges.

## Architecture Layers

### 1. Man Page Indexing Service
- Extract all Linux man pages from system (`man -k`, `/usr/share/man`)
- Generate vector embeddings using `sentence-transformers/all-MiniLM-L6-v2` (384 dims)
- Store in Weaviate with metadata: command name, section, synopsis, description
- Index: ~2000 common Linux commands
- Refresh: On-demand or periodic (daily)

### 2. Natural Language Search Engine
- Accept user prompt: "My headphone volume is too low"
- Generate embedding of prompt
- Semantic search in Weaviate (threshold: 0.7)
- Return ranked list of relevant commands with reasoning
- Example: `pactl`, `amixer`, `alsamixer`, `pulseaudio-ctl`

### 3. DAG Construction from Command Piping
- Analyze command relationships:
  - stdin/stdout piping (`|`)
  - Data flow dependencies
  - Command prerequisites
- Build DAG where:
  - Nodes = commands
  - Edges = data flow
  - Parallel groups = commands with no dependencies
- Example: `pactl list sinks | grep -i volume` → 2 nodes, 1 edge

### 4. Parallel Command Executor
- Topological sort of DAG
- Execute independent nodes in parallel (asyncio)
- Collect stdout/stderr
- Pass output to dependent nodes
- Handle errors gracefully
- Return aggregated results

### 5. Reasoning Along DAG Edges
- For each edge, generate reasoning:
  - Why this command follows the previous one
  - What data is being passed
  - Expected transformation
- Use LLM to generate human-readable explanations
- Store reasoning in execution trace

## Data Flow

```
User Prompt
    ↓
[Embedding Generation]
    ↓
[Semantic Search in Weaviate]
    ↓
[Ranked Command List + Reasoning]
    ↓
[DAG Construction]
    ↓
[Parallel Execution]
    ↓
[Result Aggregation + Reasoning Trace]
```

## Integration Points

- **Graph Service**: New node type `COMMAND_ORCHESTRATION`
- **CLI**: `unhinged orchestrate "My headphone volume is too low"`
- **Events Framework**: Log all steps to `/build/tmp/`
- **Persistence**: Store command DAGs and execution traces

## Implementation Order

1. Man Page Indexing Service
2. Natural Language Search Engine
3. DAG Construction Logic
4. Parallel Command Executor
5. Graph Service Integration
6. CLI Command
7. Tests & Documentation

