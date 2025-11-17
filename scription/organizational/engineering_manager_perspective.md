# Unhinged: Engineering Manager Perspective (2025)

**Author:** VP Engineering  
**Date:** November 16, 2025  
**Audience:** Engineering Leadership, Tech Leads, Architecture Review Board

## Technical Strategy

Unhinged is built on a **Python-first, polyglot-capable** architecture. We're consolidating from Kotlin microservices to a unified Python platform with selective performance-critical components in compiled languages.

## Architecture Principles

### 1. Headless-First Development
- Implement backend logic independently
- Wire UI to display results (not vice versa)
- Avoid over-engineering upfront
- Iterate rapidly with real feedback

### 2. Abstraction Layers
- **IO Abstraction**: Structured event routing (CLI, logs, UI, remote)
- **Service Framework**: Polyglot gRPC with configurable timeouts
- **Persistence Platform**: Redis (real-time) + CRDB (durability)
- **Events Framework**: OTEL-equivalent centralized logging

### 3. Code Quality Standards
- Mozilla-grade engineering rigor
- Pre-commit hooks (5-layer validation)
- Type safety (mypy strict mode)
- LLMDocs specification throughout
- Zero technical debt tolerance

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

## Team Structure

**Senior Engineers (45-60 years old):**
- Architecture decisions
- Complex system design
- Mentorship and code review
- Strategic technical planning

**Mid-Level Engineers (30-40 years old):**
- Feature implementation
- System integration
- Performance optimization
- Junior engineer mentorship

**Junior Engineers (22-28 years old):**
- Feature development
- Bug fixes
- Test coverage
- Learning and growth

## Development Workflow

1. **Plan from UI perspective** - Understand user needs
2. **Implement headless-first** - Data contracts, schemas, protos
3. **Wire UI** - Display results in chat/widgets
4. **Iterate** - 5-6 cycles with LLM pattern matching
5. **Finalize** - Cleanup, versioning, git semantics

## Quality Gates

- **Static Analysis**: ruff, mypy, custom linters
- **Testing**: 100% coverage for critical paths
- **Performance**: <100ms latency targets
- **Security**: No dangerous commands without confirmation
- **Documentation**: LLMDocs for all public APIs

## 2025 Milestones

- **Q4**: Command orchestration MVP (11 tests passing)
- **Q1 2026**: Weaviate integration, advanced DAGs
- **Q2 2026**: Framebuffer migration, performance optimization
- **Q3 2026**: Multi-user sessions, enterprise features
- **Q4 2026**: Production release (1.0)

## Hiring & Growth

**Seeking:**
- Senior engineers (architecture, systems)
- Mid-level engineers (full-stack)
- Junior engineers (eager to learn)
- DevOps engineers (infrastructure)
- ML engineers (semantic search optimization)

**Culture:**
- Autonomous decision-making
- Continuous learning
- Open source mindset
- Rigorous code review
- Mentorship at all levels

## Risk Management

- **Technical Debt**: Zero tolerance, addressed immediately
- **Performance**: Continuous profiling and optimization
- **Security**: Regular audits, safety-first design
- **Scalability**: Designed for 10M+ commands/month

