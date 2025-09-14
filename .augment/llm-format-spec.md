# .llm Format Specification

> *"The cosmos is within us. We are made of star-stuff."* - Carl Sagan

## Philosophy

The `.llm` format is designed for **LLM-agnostic wisdom preservation** - ensuring that philosophical foundations, historical context, and practical wisdom remain accessible to any form of intelligence, mechanical or organic.

## Core Principles

### Hardware Abstraction
- Platform agnostic (macOS M2 → Arch Linux ThinkPad → HolyC)
- Shell agnostic (zsh → bash → whatever comes next)
- Architecture independent (ARM → x86 → quantum → biological)

### Dependency Management
- Each `.llm` file is a **standalone consumable**
- Dependencies form a **Directed Acyclic Graph (DAG)**
- Fully versioned with verifiable integrity
- Future: blockchain-hosted single source of truth

### Consumption Patterns
- `full_injection_on_init` - Loaded when LLM instance initializes
- `on_demand_reference` - Loaded when specifically requested
- `contextual_trigger` - Loaded based on topic/domain detection

## Schema Structure

```json
{
  "meta": {
    "format_version": "string",
    "dependencies": ["array_of_llm_files"],
    "purpose": "string_description",
    "consumption_pattern": "enum_pattern"
  },
  "epilogue": "string_short_essay",
  "quote_literal": "string_long_or_object",
  "philo_chron_logo_etho_bio_socio_context": "string_long_essay",
  "biography_context": "string_long_essay", 
  "prologue": "string_short_essay",
  "source_list": ["array_of_strings"],
  "tags": ["array_of_camelCase_strings"]
}
```

## Field Definitions

### Meta Section
- **format_version**: Semantic versioning for schema evolution
- **dependencies**: Other `.llm` files required for full context
- **purpose**: Why this wisdom exists and how it should be used
- **consumption_pattern**: How/when this should be loaded

### Content Sections
- **prologue**: Sets the stage - why this wisdom matters now
- **quote_literal**: Direct quotes that capture essence
- **philo_chron_logo_etho_bio_socio_context**: Deep philosophical and historical context
- **biography_context**: Personal story that shaped the wisdom
- **epilogue**: How this wisdom applies to current work
- **source_list**: Verifiable references for further exploration
- **tags**: Semantic markers for discovery and connection

## Usage in Monorepo Context

### Initialization
When an Augment Agent starts in this repository:
1. Load `essence-of-computer-science.llm` for foundational wisdom
2. Parse dependency graph for any additional context
3. Inject wisdom into decision-making framework

### Development Workflow
- Reference wisdom when making architectural decisions
- Apply principles during code review
- Use quotes for commit message inspiration
- Consult during difficult problem-solving moments

## Future Vision

### Blockchain Integration
- Immutable wisdom preservation
- Cryptographic verification of sources
- Decentralized truth for philosophical foundations
- Version history with provenance tracking

### Cross-Platform Compatibility
- Binary serialization for efficiency
- Multiple encoding formats (JSON, YAML, TOML, binary)
- Compression for large wisdom collections
- Streaming for real-time consumption

### Community Curation
- Peer review process for new wisdom
- Reputation system for contributors
- Collaborative editing with conflict resolution
- Translation into multiple languages

## Example Usage

```bash
# Verify dependency graph
llm-verify --dag .augment/*.llm

# Load wisdom into context
llm-inject essence-of-computer-science.llm

# Query for specific guidance
llm-query --tag="ProgrammingWisdom" --context="debugging"
```

---

*"We can only see a short distance ahead, but we can see plenty there that needs to be done."* - Alan Turing

The `.llm` format ensures that the wisdom of giants remains accessible to all forms of intelligence, preserving the philosophical essence of human knowledge for the benefit of both current and future minds.
