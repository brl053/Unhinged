# Git Driver

Centralized Git operations driver for Unhinged project.

## Components

- `hooks.py` - GitHookManager class for programmatic hook management
- `quality_gates.py` - Quality gate enforcement (runs all checks, blocks SKIP)
- `actionable_errors.py` - Actionable error formatting with fix guidance
- `pre-commit-config.yaml` - Pre-commit hook configuration (standard pre-commit framework)

## Installation

```bash
./scripts/install_quality_gates.sh
```

This installs the quality gate enforcement hook that:
- Runs all quality checks (ruff, mypy, custom linter, LLMDocs)
- Blocks SKIP and --no-verify bypass attempts
- Provides actionable fix guidance

## Usage

### Programmatic Hook Management

```python
from pathlib import Path
from libs.python.drivers.git import GitHookManager

manager = GitHookManager(Path.cwd())
manager.install_quality_gate_hook()
```

### Manual Installation

```bash
# Install quality gate enforcement
./scripts/install_quality_gates.sh

# Verify installation
cat .git/hooks/pre-commit
```

## Configuration

The `pre-commit-config.yaml` in this directory is the source of truth for
pre-commit hook configuration. It must be copied to repo root `.pre-commit-config.yaml`
for the pre-commit framework to find it.

The configuration defines:
- `unhinged-lint` - Custom linter (build/lint.py)
- `llmdocs-validator` - LLMDocs validation
- `ruff` - Linter with auto-fix
- `ruff-format` - Code formatter
- `mypy` - Type checker

When updating pre-commit configuration:
1. Edit `libs/python/drivers/git/pre-commit-config.yaml`
2. Copy to repo root: `cp libs/python/drivers/git/pre-commit-config.yaml .pre-commit-config.yaml`
3. Commit both files

## Architecture

All Git-specific operations are centralized in this driver:
- Hook installation and management
- Quality gate enforcement
- Pre-commit configuration
- Error formatting and guidance

This follows the driver pattern where Git is treated as an external system
with its own idiosyncrasies (hooks, SKIP behavior, --no-verify, etc).

