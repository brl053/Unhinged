# Unhinged Roadmap

## Vision Overview

Unhinged is a multi-stage evolution toward an LLM-native operating system, starting as a SaaS product and evolving into a ring-zero OS replacement.

## Stage 1: SaaS Product (Current)
- React frontend + backend API
- Agent orchestration framework
- Local hosting with full system control
- Event-driven architecture with PostgreSQL persistence

## Stage 2: Ring Zero Operating System (Future)
- Fork repository for OS-level implementation
- LLM-native OS with dynamic UI rendering
- Complete vertical integration

## Directory Structure

```
roadmap/
├── README.md                    # This file
├── stage-1-saas/              # Current development focus
│   ├── architecture.md         # System architecture
│   ├── patterns.md            # Development patterns
│   ├── entities.md            # CRUD entity patterns
│   └── milestones.md          # Development milestones
├── stage-2-os/                # Future OS development
│   ├── vision.md              # OS vision and requirements
│   ├── kernel-integration.md  # Ring zero integration
│   └── ui-rendering.md        # Dynamic UI system
├── infrastructure/            # System infrastructure
│   ├── database.md           # PostgreSQL + document store
│   ├── events.md             # Event system architecture
│   ├── caching.md            # Redis integration
│   └── analytics.md          # Big data processing
└── patterns/                  # Reusable patterns
    ├── crud-pattern.md       # E2E CRUD template
    ├── event-pattern.md      # Event emission patterns
    └── agent-pattern.md      # Agent orchestration patterns
```

## Current Priority

Establish E2E CRUD pattern for rapid entity replication across the system.
