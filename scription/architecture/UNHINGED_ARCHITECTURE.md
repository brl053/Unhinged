# Unhinged: Technical Architecture (2025)

## Core Architecture

Unhinged is built on **first principles** thinking about operating systems. We treat the kernel as a first-class citizen, not a hidden implementation detail.

### Natural Language → Command Pipeline

```
Natural Language Input
    ↓
Semantic Search (Vector Embeddings)
    ↓
Command Discovery (Cosine Similarity)
    ↓
DAG Construction (Topological Sort)
    ↓
Parallel Execution (asyncio)
    ↓
Results + Reasoning
```

## Core Components

### 1. Semantic Search Engine
- **Input:** Natural language prompts
- **Process:** Vector embeddings (384-dim, sentence-transformers)
- **Index:** 8248 documents (8233 man pages + 15 organizational docs)
- **Output:** Ranked commands with similarity scores

### 2. DAG Construction
- **Input:** List of commands
- **Process:** Parse pipelines, analyze dependencies
- **Output:** Directed acyclic graph of execution order

### 3. Parallel Executor
- **Input:** DAG of commands
- **Process:** Execute independent commands in parallel (asyncio.gather)
- **Output:** Results with exit codes, stdout, stderr

### 4. Reasoning Engine
- **Input:** Command selection and execution results
- **Process:** Generate explanations for why commands were chosen
- **Output:** Human-readable reasoning for each step

## Technology Stack

**Core:**
- Python 3.12+ (primary language)
- GTK4 (UI, migrating to framebuffer)
- gRPC (inter-service communication)
- Protobuf (schema definitions)

**Data & ML:**
- Weaviate (vector database)
- sentence-transformers (embeddings)
- Redis (state management)
- CockroachDB (persistence)

**Infrastructure:**
- OrbStack (container orchestration)
- Linux kernel native (no abstraction)
- NVIDIA CUDA (GPU acceleration)
- PipeWire (audio subsystem)

## Abstraction Layers

### 1. IO Abstraction
Structured event routing to multiple outputs:
- CLI (formatted text)
- Logs (structured JSON)
- UI (widgets in chat)
- Remote (gRPC streaming)

### 2. Service Framework
Polyglot architecture with:
- Python-first implementation
- Kotlin for performance-critical paths
- gRPC for inter-service communication
- Configurable timeouts (not hardcoded)

### 3. Document-Based Registry
Reusable for any entity type:
- Create/read/update/delete operations
- Graphs/Tools/Entities as first-class documents
- Metrics/Events go to Redis/CRDB (code-driven only)

## Design Principles

### 1. Headless-First Development
- Implement backend logic independently
- Verify with tests before UI wiring
- Avoid over-engineering upfront
- Iterate rapidly with real feedback

### 2. Composition Over Inheritance
- Jinja2 templates with fragments
- Reusable components via {% include %}
- DRY principle throughout
- Git-friendly versioning

### 3. Safety First
- Dangerous commands require explicit confirmation
- Audit trail of all executed commands
- Dry-run mode for preview
- Rollback capabilities

## Performance Targets

- **Intent Recognition:** <100ms latency
- **Command Discovery:** <500ms for 8000+ man pages
- **DAG Execution:** <1s for typical command chains
- **System Throughput:** 10M+ commands/month

## Scalability

**Phase 1 (Current):** In-memory indexing
**Phase 2:** Weaviate persistence (400TB capacity)
**Phase 3:** Distributed execution across clusters
**Phase 4+:** Autonomous system repair and predictive maintenance

## Security Model

### Threat Model
- User mistakes (most common)
- Malicious prompts (rare)
- System state corruption (prevented)
- Data loss (prevented)

### Mitigation Strategies
- Confirmation flow for dangerous operations
- Dry-run mode for preview
- Audit trail for all operations
- Rollback capabilities
- Safety checks for destructive commands

## Code Quality Standards

- Type Safety: mypy strict mode
- Linting: ruff with strict rules
- Testing: 100% coverage for critical paths
- Documentation: LLMDocs for all public APIs
- Git Hygiene: Meaningful commits, clean history

## Integration Points

- **Graph Service:** COMMAND_ORCHESTRATION node type
- **CLI:** `unhinged orchestrate solve "prompt"`
- **Prompt System:** Jinja2 templates for memo generation
- **Events Framework:** Centralized logging and metrics

