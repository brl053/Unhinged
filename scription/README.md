# /scription - Canonical Evergreen Documentation & Orchestration

## Purpose

`/scription` is the **single source of truth** for Unhinged's foundational documentation, prompt orchestration system, and command orchestration framework. This directory contains:

1. **Evergreen Documentation** - Vision, architecture, positioning
2. **Organizational Knowledge** - Perspectives from all stakeholder roles
3. **Prompt Orchestration** - Jinja2 templates for memorandums and prompts
4. **Command Orchestration** - Natural language → kernel command pipeline
5. **Semantic Search Index** - Embeddings for LLM context

## Directory Structure

```
scription/
├── README.md                          # This file
├── vision/                            # Strategic vision documents
│   └── UNHINGED_VISION.md
├── architecture/                      # Technical architecture
│   ├── UNHINGED_ARCHITECTURE.md
│   └── UNHINGED_POSITIONING.md
├── organizational/                    # Organizational perspectives & memos
│   ├── ceo_perspective.md
│   ├── product_manager_perspective.md
│   ├── engineering_manager_perspective.md
│   ├── senior_engineer_perspective.md
│   ├── designer_perspective.md
│   ├── MEMORANDUM_HEADER.txt
│   ├── MEMORANDUM_FOOTER.txt
│   ├── MEMORANDUM_PROLOGUE.txt
│   ├── MEMORANDUM_EPILOGUE.txt
│   └── MEMORANDUM_EXECUTIVE_SUMMARY.txt
├── prompts/                           # Jinja2 templates (Prompt Orchestration)
│   ├── templates/
│   │   └── memorandum.j2
│   ├── fragments/
│   │   ├── headers.j2
│   │   ├── executive.j2
│   │   └── signoff.j2
│   └── composed/
└── orchestration/                     # Command & Prompt Orchestration
    └── lib/
        ├── command_orchestration/     # Natural language → kernel commands
        │   ├── __init__.py
        │   ├── man_page_indexer.py
        │   ├── semantic_search.py
        │   ├── dag_builder.py
        │   ├── executor.py
        │   └── document_loader.py
        └── prompt_orchestration/      # Jinja2 template rendering
            ├── __init__.py
            └── render.py
```

## Core Components

### 1. Vision & Architecture (Evergreen Docs)

**vision/UNHINGED_VISION.md**
- Core vision: Operating system for post-GUI era
- Problem statement and solution
- Market opportunity ($50B+)
- 2025-2026 roadmap
- Success metrics

**architecture/UNHINGED_ARCHITECTURE.md**
- Natural language → command pipeline
- Core components and technology stack
- Abstraction layers
- Design principles
- Performance targets

**architecture/UNHINGED_POSITIONING.md**
- Target personas and pain points
- Key differentiators
- Value propositions
- Go-to-market strategy

### 2. Organizational Knowledge

**organizational/\*_perspective.md** (5 files)
- CEO perspective: Vision, market opportunity, strategic positioning
- Product Manager: User personas, feature roadmap, product pillars
- Engineering Manager: Technical strategy, team structure, workflow
- Senior Engineer: Technical foundation, architecture patterns, design decisions
- Designer: Design philosophy, interface paradigms, accessibility

**organizational/MEMORANDUM_\*.txt** (5 files)
- Reusable memo templates for consistent communication
- Header, footer, prologue, epilogue, executive summary
- Used by prompt orchestration system

### 3. Prompt Orchestration (Jinja2 Templates)

**prompts/templates/memorandum.j2**
- Main IBM-style memorandum template
- Includes header, prologue, sections, epilogue, footer
- Supports dynamic content and variables

**prompts/fragments/\*.j2** (3 files)
- Reusable template fragments
- Headers, executive summaries, signoffs
- Composed into larger templates

### 4. Command Orchestration

**orchestration/lib/command_orchestration/**
- `man_page_indexer.py` - Extracts and indexes Linux man pages
- `semantic_search.py` - Natural language search with embeddings
- `dag_builder.py` - Constructs command DAGs from pipelines
- `executor.py` - Parallel command execution
- `document_loader.py` - Loads organizational docs for context

**orchestration/lib/prompt_orchestration/**
- `render.py` - Jinja2 template rendering engine

## Usage

### For LLM Seeding

All documents are automatically loaded into the semantic search index:

```python
from libs.python.command_orchestration.document_loader import DocumentLoader

loader = DocumentLoader()
docs = loader.combine_documents()  # Loads all scription docs
indexer.load_organizational_documents(docs)
```

### For Command Orchestration

Transform natural language into orchestrated kernel commands:

```python
from libs.python.command_orchestration import (
    ManPageIndexer,
    SemanticSearchEngine,
    DAGBuilder,
    CommandExecutor
)

# Index man pages
indexer = ManPageIndexer()
entries = indexer.build_index()

# Search for relevant commands
search = SemanticSearchEngine(entries)
results = search.search("My headphone volume is too low")

# Build and execute DAG
dag_builder = DAGBuilder()
dag = dag_builder.build_from_commands([r.command for r in results])
executor = CommandExecutor()
results = executor.execute(dag)
```

### For Prompt Orchestration

Render Jinja2 templates for memorandums:

```python
from libs.python.prompt_orchestration import UnhingedPromptRenderer

renderer = UnhingedPromptRenderer()
memo = renderer.render_template("memorandum.j2", {
    "to": "Chief of Science",
    "from": "Augment Agent",
    "subject": "Phase 2 Completion",
    "sections": [...]
})
```

### For Product Decisions

Reference evergreen documents when:
- Prioritizing features
- Making architectural decisions
- Communicating with stakeholders
- Evaluating new initiatives

### For Onboarding

New team members should read:
1. `vision/UNHINGED_VISION.md` - Understand the vision
2. `architecture/UNHINGED_ARCHITECTURE.md` - Learn the architecture
3. `organizational/senior_engineer_perspective.md` - Technical deep dive
4. `organizational/product_manager_perspective.md` - Product context

## Backward Compatibility

All imports from the old locations still work via wrapper modules:

```python
# Old imports (still work)
from libs.python.command_orchestration import ManPageIndexer
from libs.python.prompt_orchestration import UnhingedPromptRenderer

# These are re-exported from scription/orchestration/lib/
```

## Maintenance

### Quarterly Review
- Verify accuracy of strategic direction
- Update roadmap with new milestones
- Reflect market changes

### Update Process
1. Edit relevant document in `/scription`
2. Commit with clear message explaining changes
3. Update related documents for consistency
4. Notify team of changes

### Example Commit
```
docs: Update UNHINGED_VISION.md with Q1 2026 roadmap

- Added Weaviate integration timeline
- Updated market opportunity TAM
- Clarified competitive positioning

This seeds the LLM with updated strategic direction.
```

## Quality Metrics

- **Documents:** 19 total (4 vision/arch + 10 org + 5 memo templates)
- **Embedding Index:** 8247 entries (man pages + org docs)
- **Embedding Dimensions:** 384-dimensional vectors
- **Search Threshold:** 0.3 (optimized for recall)
- **Tests Passing:** 19/19 (100%)

## Integration Points

- **CLI:** `unhinged orchestrate solve "prompt"`
- **Graph Service:** COMMAND_ORCHESTRATION node type
- **Events Framework:** Centralized logging
- **Semantic Search:** Automatic document loading

## Related Documentation

- `/build/SCRIPTION_SEEDING_COMPLETE.md` - Implementation details
- `/build/COMMAND_ORCHESTRATION_ARCHITECTURE.md` - Architecture deep dive
- `/build/JINJA2_PROMPT_ORCHESTRATION_IMPLEMENTATION.md` - Template system
- `/man/man1/unhinged.1` - CLI documentation

