# Reasoning Engine Investigation

**Date**: 2025-11-17  
**Status**: Investigation Complete  
**Scope**: Identify missing Reasoning Engine component and design implementation strategy

---

## Executive Summary

The Unhinged architecture defines a **Reasoning Engine** as a core component (Section 4 of UNHINGED_ARCHITECTURE.md), but it is **not yet implemented**. The engine should generate human-readable explanations for:

1. **Command Selection**: Why specific commands were chosen from semantic search
2. **DAG Execution**: Reasoning along DAG edges (data flow transformations)
3. **Result Interpretation**: Explanations for execution outcomes

---

## Current Architecture Gap

### Defined (in scription/architecture/UNHINGED_ARCHITECTURE.md)

```
### 4. Reasoning Engine
- **Input:** Command selection and execution results
- **Process:** Generate explanations for why commands were chosen
- **Output:** Human-readable reasoning for each step
```

### Implemented Components

✅ **Semantic Search Engine** (`libs/python/command_orchestration/semantic_search.py`)
- Returns `SearchResult` with `reasoning` field (currently static)
- Example: "Matches audio volume diagnostics"

✅ **DAG Builder** (`libs/python/command_orchestration/dag_builder.py`)
- Constructs execution DAGs from command pipelines
- No reasoning generation for edges

✅ **Command Executor** (`libs/python/command_orchestration/executor.py`)
- Executes DAGs in parallel
- Returns results but no reasoning trace

❌ **Reasoning Engine** (MISSING)
- No LLM-backed reasoning generation
- No edge reasoning (data flow explanations)
- No result interpretation

---

## Design Requirements

### 1. Semantic Search Reasoning
**Current**: Static reasoning strings  
**Required**: LLM-generated explanations for why commands match the user query

### 2. DAG Edge Reasoning
**Current**: None  
**Required**: For each edge in DAG, explain:
- Why command B follows command A
- What data is being passed (stdout → stdin)
- Expected transformation

### 3. Result Interpretation
**Current**: Raw stdout/stderr  
**Required**: LLM-generated interpretation of execution results

### 4. Execution Trace
**Current**: None  
**Required**: Complete reasoning trace with:
- Query → Intent classification
- Intent → Command selection (with reasoning)
- Commands → DAG construction (with edge reasoning)
- DAG → Execution results (with interpretation)

---

## Implementation Strategy

### Phase 1: Reasoning Engine Core
- Create `libs/python/command_orchestration/reasoning_engine.py`
- Implement `ReasoningEngine` class with LLM-backed reasoning
- Support multiple providers (Anthropic, OpenAI, Ollama)
- Lazy-load LLM clients (pattern from `LLMIntentNode`)

### Phase 2: Integration Points
- Update `SemanticSearchEngine` to use reasoning engine
- Update `DAGBuilder` to generate edge reasoning
- Update `CommandExecutor` to collect reasoning trace

### Phase 3: Execution Trace
- Create `ExecutionTrace` data structure
- Collect reasoning at each pipeline stage
- Return complete trace with results

### Phase 4: CLI Integration
- Update `cli/commands/orchestrate.py` to display reasoning
- Add `--explain` flag for detailed reasoning output
- Format reasoning for human readability

---

## Files to Create/Modify

### Create
- `libs/python/command_orchestration/reasoning_engine.py` (~200 lines)
- `tests/test_reasoning_engine.py` (~150 lines)

### Modify
- `libs/python/command_orchestration/semantic_search.py` - Use reasoning engine
- `libs/python/command_orchestration/dag_builder.py` - Add edge reasoning
- `libs/python/command_orchestration/executor.py` - Collect trace
- `libs/python/command_orchestration/__init__.py` - Export reasoning engine
- `cli/commands/orchestrate.py` - Display reasoning

---

## Next Steps

1. **Design** reasoning engine API (input/output contracts)
2. **Implement** core reasoning engine with LLM support
3. **Integrate** with existing components
4. **Test** with comprehensive test suite
5. **Document** reasoning engine in LLMDocs format

