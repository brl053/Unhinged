# Unhinged: Senior Engineer Perspective (2025)

**Author:** Principal Architect  
**Date:** November 16, 2025  
**Audience:** Architecture Review Board, Technical Leadership, Future Contributors

## Technical Foundation

Unhinged is built on **first principles** thinking about operating systems. We reject the assumption that GUIs must be the primary interface. Instead, we're building a kernel-native platform where natural language is the primary abstraction.

## Core Abstractions

### 1. Command Orchestration Pipeline
```
Natural Language → Semantic Search → DAG Construction → Parallel Execution
```

- **Semantic Search**: Vector embeddings of man pages (384-dim, sentence-transformers)
- **DAG Construction**: Topological sort of command dependencies
- **Parallel Execution**: asyncio.gather for independent command groups
- **Reasoning**: Generated explanations for each command selection

### 2. IO Abstraction Layer
Structured event routing to multiple outputs:
- CLI (formatted text)
- Logs (structured JSON)
- UI (widgets in chat)
- Remote (gRPC streaming)

### 3. Service Framework
Polyglot architecture with:
- Python-first implementation
- Kotlin for performance-critical paths
- gRPC for inter-service communication
- Configurable timeouts (not hardcoded)

## Design Decisions

### Why Python-First?
- Rapid iteration and prototyping
- Excellent ML/data science ecosystem
- Strong type system (mypy)
- Clear, readable code

### Why Kernel-Native?
- Direct framebuffer access (no X11/Wayland overhead)
- Full system control
- Transparent to users
- Performance advantages

### Why Semantic Search?
- Handles natural language variations
- Discovers commands by intent, not syntax
- Learns from user feedback
- Scales to millions of commands

## Architecture Patterns

### 1. Document-Based Registry
Reusable for any entity type (tools, users, admins, persons):
- Create/read/update/delete operations
- Graphs/Tools/Entities as first-class documents
- Metrics/Events go to Redis/CRDB (code-driven only)

### 2. Headless-First Development
- Implement backend logic independently
- Verify with tests before UI wiring
- Avoid over-engineering upfront
- Iterate rapidly with real feedback

### 3. Composition Over Inheritance
- Jinja2 templates with fragments
- Reusable components via {% include %}
- DRY principle throughout
- Git-friendly versioning

## Performance Targets

- **Intent Recognition**: <100ms latency
- **Command Discovery**: <500ms for 8000+ man pages
- **DAG Execution**: <1s for typical command chains
- **System Throughput**: 10M+ commands/month

## Security Model

### Safety First
- Dangerous commands require explicit confirmation
- Audit trail of all executed commands
- Dry-run mode for preview
- Rollback capabilities

### Threat Model
- User mistakes (most common)
- Malicious prompts (rare)
- System state corruption (prevented)
- Data loss (prevented)

## Testing Strategy

### Unit Tests
- Individual components (man page indexer, search engine, DAG builder)
- Edge cases and error handling
- Type safety verification

### Integration Tests
- Full pipeline from prompt to execution
- Real command execution in sandbox
- Reasoning verification

### Performance Tests
- Latency benchmarks
- Throughput measurements
- Memory profiling

## Future Directions

### Phase 2 (2026)
- Weaviate persistence for embeddings
- Advanced DAG features (data flow analysis)
- LLM-based reasoning enhancement
- Multi-user session management

### Phase 3 (2027)
- Predictive command suggestions
- Integration with monitoring systems
- Custom domain-specific languages
- Distributed execution across clusters

### Phase 4+ (2028+)
- Autonomous system repair
- Predictive maintenance
- Cross-system orchestration
- AI-driven infrastructure management

## Code Quality Standards

- **Type Safety**: mypy strict mode, no Any types
- **Linting**: ruff with strict rules
- **Testing**: 100% coverage for critical paths
- **Documentation**: LLMDocs for all public APIs
- **Git Hygiene**: Meaningful commits, clean history

## Mentorship & Growth

Senior engineers at Unhinged:
- Guide architectural decisions
- Mentor mid-level engineers
- Review complex implementations
- Contribute to open source ecosystem
- Shape technical culture

This is not a startup. This is a platform for the next decade of computing.

