# CLI Architecture Plan: Headless-First Development

## 1. Code Analysis Library Integration

### Current State
- Custom AST-based scripts: `build/find_usages.py`, `build/find_usages_recursive.py`
- Mypy for type checking (no usage tracking)
- Ruff for linting (no semantic analysis)

### Mature Library Options
**Recommended: `libcst` (Concrete Syntax Tree)**
- Used by Ruff internally
- Preserves formatting/comments
- Semantic analysis capabilities
- Industry standard (Meta, Google use it)
- Better than raw AST for refactoring

**Alternative: `ast` (built-in)**
- Already available
- Sufficient for basic usage tracking
- No external dependency

### Implementation
```bash
# Add to requirements
pip install libcst>=0.4.0

# New command
./unhinged dev analyze upstream-downstream <filepath>/<symbol>
./unhinged dev analyze usages <symbol>
./unhinged dev analyze imports <filepath>
```

---

## 2. CLI Consolidation: `control/cli` → `libs/cli`

### Current Scattered State
- `control/cli/` - Main CLI (Click app)
- `control/conversation_cli.py` - Separate CLI
- `build/cli.py` - Build system CLI
- `build/orchestrator.py` - Orchestration logic
- Multiple command modules scattered

### Proposed Structure
```
libs/cli/
├── __init__.py
├── core/
│   ├── app.py              # Main Click app
│   ├── context.py          # CLI context/state
│   └── decorators.py       # Common decorators
├── commands/
│   ├── dev.py              # Development commands
│   ├── build.py            # Build commands
│   ├── system.py           # System commands
│   ├── analyze.py          # NEW: Code analysis
│   └── __init__.py
├── utils/
│   ├── output.py           # Formatting/colors
│   ├── process.py          # Subprocess handling
│   └── paths.py            # Path resolution
└── tests/
    └── test_cli.py
```

### Migration Path
1. Move `control/cli/` → `libs/cli/`
2. Update imports in `control/__main__.py`
3. Consolidate `build/cli.py` logic into `libs/cli/commands/build.py`
4. Unify `conversation_cli.py` as `libs/cli/commands/chat.py`
5. Update `./unhinged` shim to reference new location

---

## 3. Headless-First Development Strategy

### Shift Away From GTK4
- Archive `control/gtk4_gui/` (don't delete, keep for reference)
- Focus on `libs/cli/` as primary interface
- Build data contracts first (proto/schemas)
- Wire CLI commands to libraries
- GUI becomes optional visualization layer later

### Development Loop
1. **Define**: Proto schemas in `proto/`
2. **Implement**: Headless library in `libs/`
3. **Test**: Unit tests for library
4. **CLI**: Wire library to `libs/cli/commands/`
5. **Verify**: Test via CLI
6. **GUI** (optional): Later visualization

---

## 4. `./unhinged` vs `unhinged` Command

### Current: `./unhinged` (relative path)
- Requires being in project directory
- Works for development
- Not suitable for distribution

### Options for Distribution

**Option A: Install to `/usr/local/bin`**
```bash
# In Makefile or install script
install:
    cp unhinged /usr/local/bin/unhinged
    chmod +x /usr/local/bin/unhinged
```
- Requires absolute path in shim
- Works system-wide
- Needs installation step

**Option B: Python Package Entry Point**
```bash
# setup.py or pyproject.toml
entry_points={
    'console_scripts': [
        'unhinged=control.cli:main',
    ],
}
pip install -e .
```
- Most Pythonic
- Works after `pip install`
- Best for distribution

**Option C: Symlink in PATH**
```bash
ln -s /path/to/unhinged ~/.local/bin/unhinged
export PATH="$HOME/.local/bin:$PATH"
```
- User-level installation
- No system-wide changes
- Requires PATH setup

### Recommendation
**Use Option B (Python entry point)** for production distribution, but keep `./unhinged` for development.

---

## 5. Man Page Enhancement

### Current State
- Only `man/man1/unhinged-generate.1` exists
- Main `unhinged.1` missing

### Plan
```bash
man/man1/
├── unhinged.1              # Main command
├── unhinged-dev.1          # Dev subcommand
├── unhinged-build.1        # Build subcommand
├── unhinged-system.1       # System subcommand
├── unhinged-analyze.1      # NEW: Analysis subcommand
└── unhinged-generate.1     # Generate subcommand
```

### Auto-Generation from Click
```python
# Generate man pages from Click app
from click.testing import CliRunner
from click_man.core import man_page_for_click_command

# Generates proper man pages from Click docstrings
```

---

## Implementation Priority

1. **Phase 1**: Add libcst-based analysis to `./unhinged dev analyze`
2. **Phase 2**: Consolidate CLI to `libs/cli/`
3. **Phase 3**: Archive GTK4, shift to headless-first
4. **Phase 4**: Generate comprehensive man pages
5. **Phase 5**: Create Python package entry point for distribution

