# Reasoning Engine - Investigation Findings

**Investigation Date**: 2025-11-17  
**Investigator**: Augment Agent  
**Status**: Complete

---

## What is "The Engine"?

The user's request to "add the engine" refers to the **Reasoning Engine**, a core architectural component defined in `scription/architecture/UNHINGED_ARCHITECTURE.md` (Section 4) but not yet implemented.

---

## Current State

### ✅ Implemented Components

1. **Semantic Search Engine** - Finds relevant commands via embeddings
2. **DAG Builder** - Constructs execution DAGs from command pipelines
3. **Command Executor** - Executes DAGs in parallel with asyncio
4. **Intent Analysis Graph** - LLM-backed intent classification (just completed)

### ❌ Missing Component

**Reasoning Engine** - Should generate LLM-backed explanations for:
- Why specific commands were selected
- How data flows through DAG edges
- What execution results mean

---

## Architecture Gap

### Current Pipeline
```
User Query
    ↓
Intent Classification (LLM) ✅
    ↓
Semantic Search (embeddings) ✅
    ↓
DAG Construction ✅
    ↓
Parallel Execution ✅
    ↓
Raw Results (no reasoning) ❌
```

### Required Pipeline
```
User Query
    ↓
Intent Classification (LLM) ✅
    ↓
Semantic Search + Reasoning (LLM) ❌
    ↓
DAG Construction + Edge Reasoning (LLM) ❌
    ↓
Parallel Execution ✅
    ↓
Result Interpretation (LLM) ❌
    ↓
Complete Execution Trace with Reasoning
```

---

## Design Approach

### Pattern: Reuse LLMIntentNode Design
The Reasoning Engine should follow the same pattern as `LLMIntentNode`:
- Lazy-load LLM clients
- Support multiple providers (Anthropic, OpenAI, Ollama)
- System prompts with semantic guidance
- Structured output (JSON)
- Comprehensive error handling

### Key Differences
- **LLMIntentNode**: Single classification task
- **ReasoningEngine**: Multiple reasoning tasks (selection, edges, results)

---

## Implementation Scope

### Files to Create
- `libs/python/command_orchestration/reasoning_engine.py` (~200 lines)
- `tests/test_reasoning_engine.py` (~150 lines)

### Files to Modify
- `semantic_search.py` - Use reasoning engine for command selection
- `dag_builder.py` - Generate edge reasoning
- `executor.py` - Collect reasoning trace
- `__init__.py` - Export reasoning engine
- `cli/commands/orchestrate.py` - Display reasoning

### Estimated Effort
- **Design**: 30 min (complete)
- **Implementation**: 2-3 hours
- **Testing**: 1-2 hours
- **Integration**: 1 hour
- **Total**: ~5-6 hours

---

## Deliverables

### Phase 1: Core Engine
- ReasoningEngine class with LLM support
- System prompts for 3 reasoning tasks
- Lazy client loading
- Error handling

### Phase 2: Integration
- Update semantic search
- Update DAG builder
- Update executor
- Export from __init__.py

### Phase 3: Testing
- 6+ test cases with mocked LLM
- Integration tests
- Trace validation

### Phase 4: CLI
- `--explain` flag for reasoning output
- Formatted execution trace display

---

## Success Metrics

✅ All reasoning generated via LLM  
✅ Complete execution trace at each pipeline stage  
✅ All 24+ tests pass  
✅ Zero mypy errors  
✅ Pre-commit hooks passing  
✅ LLMDocs annotations throughout

---

## Recommendation

**Proceed with implementation** following the design in `REASONING_ENGINE_SPECIFICATION.md`. The pattern is well-established (LLMIntentNode), and the scope is clear and bounded.

