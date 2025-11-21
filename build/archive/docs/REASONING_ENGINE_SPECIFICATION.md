# Reasoning Engine - Technical Specification

**Component**: `libs/python/command_orchestration/reasoning_engine.py`  
**Purpose**: Generate LLM-backed explanations for command selection, DAG execution, and result interpretation  
**Status**: Design Phase

---

## API Design

### ReasoningEngine Class

```python
class ReasoningEngine:
    """Generate LLM-backed reasoning for command orchestration."""
    
    def __init__(
        self,
        model: str = "claude-3-5-sonnet-20241022",
        provider: str = "anthropic",
    ):
        """Initialize reasoning engine with LLM provider."""
        
    async def reason_command_selection(
        self,
        query: str,
        commands: List[str],
        similarity_scores: List[float],
    ) -> Dict[str, str]:
        """Generate reasoning for why commands were selected.
        
        Returns: {command: reasoning_text}
        """
        
    async def reason_dag_edge(
        self,
        from_command: str,
        to_command: str,
        data_flow: str,  # e.g., "stdout → stdin"
    ) -> str:
        """Generate reasoning for DAG edge (data flow)."""
        
    async def reason_execution_result(
        self,
        command: str,
        exit_code: int,
        stdout: str,
        stderr: str,
    ) -> str:
        """Generate interpretation of execution result."""
        
    async def reason_execution_trace(
        self,
        query: str,
        intent: Dict[str, Any],
        commands: List[str],
        dag_edges: List[Tuple[str, str]],
        execution_results: Dict[str, ExecutionResult],
    ) -> ExecutionTrace:
        """Generate complete reasoning trace for entire pipeline."""
```

### ExecutionTrace Data Structure

```python
@dataclass
class ExecutionTrace:
    """Complete reasoning trace for command orchestration."""
    query: str
    intent_reasoning: str
    command_selection_reasoning: Dict[str, str]
    dag_edge_reasoning: Dict[Tuple[str, str], str]
    execution_result_reasoning: Dict[str, str]
    summary: str
```

---

## System Prompts

### Command Selection Reasoning
```
You are an expert at explaining why specific Linux commands are relevant
to a user's problem. Given a user query and a list of selected commands,
generate a brief explanation for each command explaining why it was chosen.

Consider:
- How the command relates to the user's problem
- What information the command provides
- How it contributes to solving the problem

Format: One sentence per command, clear and concise.
```

### DAG Edge Reasoning
```
You are an expert at explaining data flow in command pipelines.
Given two commands connected by a pipe (stdout → stdin), explain:
- Why command B follows command A
- What data is being passed
- What transformation occurs

Format: One sentence explaining the data flow relationship.
```

### Result Interpretation
```
You are an expert at interpreting Linux command output.
Given a command, its exit code, stdout, and stderr, generate a brief
interpretation of what the result means and what it tells us about
the system state.

Format: One sentence summarizing the result's significance.
```

---

## Integration Points

### 1. SemanticSearchEngine
**Current**: Returns static reasoning  
**Change**: Call `reasoning_engine.reason_command_selection()`

### 2. DAGBuilder
**Current**: No edge reasoning  
**Change**: For each edge, call `reasoning_engine.reason_dag_edge()`

### 3. CommandExecutor
**Current**: Returns raw results  
**Change**: Collect reasoning trace during execution

### 4. CLI Output
**Current**: YAML plan only  
**Change**: Add `--explain` flag to display reasoning

---

## Implementation Phases

### Phase 1: Core Engine (200 lines)
- LLM client loading (lazy)
- System prompt generation
- Command selection reasoning
- DAG edge reasoning
- Result interpretation

### Phase 2: Integration (100 lines)
- Update semantic search
- Update DAG builder
- Update executor
- Export from __init__.py

### Phase 3: Testing (150 lines)
- Mock LLM tests
- Integration tests
- Trace validation

### Phase 4: CLI (50 lines)
- Add --explain flag
- Format reasoning output
- Display execution trace

---

## Success Criteria

✅ All reasoning generated via LLM (no hardcoded strings)  
✅ Lazy-load LLM clients for performance  
✅ Support multiple providers (Anthropic, OpenAI, Ollama)  
✅ Complete execution trace with reasoning at each stage  
✅ All tests pass (24+ existing + new reasoning tests)  
✅ Zero mypy errors  
✅ LLMDocs annotations throughout  
✅ Pre-commit hooks passing

