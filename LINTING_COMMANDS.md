# Unhinged Linting Commands Cheat Sheet

## Quick Start

```bash
# Install pre-commit hooks
./build/python/venv/bin/pre-commit install

# Run all hooks on all files
./build/python/venv/bin/pre-commit run --all-files

# Run specific hook
./build/python/venv/bin/pre-commit run unhinged-lint --all-files
./build/python/venv/bin/pre-commit run llmdocs-validator --all-files
./build/python/venv/bin/pre-commit run ruff-format --all-files
./build/python/venv/bin/pre-commit run mypy --all-files
```

## Custom Linter (Unhinged Rules)

```bash
# Lint single file
python3 build/lint.py control/gtk4_gui/handlers/audio_handler.py

# Lint multiple files
python3 build/lint.py control/gtk4_gui/handlers/*.py

# Lint all Python files
find control libs -name "*.py" -type f | xargs python3 build/lint.py

# Check specific violations
python3 build/lint.py FILE.py 2>&1 | grep "FATAL"
python3 build/lint.py FILE.py 2>&1 | grep "WARNING"
```

## Ruff (Code Formatter & Linter)

```bash
# Check for violations
./build/python/venv/bin/ruff check FILE.py

# Auto-fix violations
./build/python/venv/bin/ruff check --fix FILE.py

# Format code
./build/python/venv/bin/ruff format FILE.py

# Check all Python files
./build/python/venv/bin/ruff check control/ libs/
```

## LLMDocs Validator

```bash
# Validate single file
python3 build/validators/llmdocs_validator.py FILE.py

# Validate multiple files
python3 build/validators/llmdocs_validator.py control/gtk4_gui/handlers/*.py
```

## Pre-Commit Hooks

```bash
# Install hooks
./build/python/venv/bin/pre-commit install

# Run on staged files (automatic on commit)
./build/python/venv/bin/pre-commit run

# Run on all files
./build/python/venv/bin/pre-commit run --all-files

# Run specific hook
./build/python/venv/bin/pre-commit run HOOK_ID --all-files

# Skip hooks on commit
git commit --no-verify -m "message"

# Update hook versions
./build/python/venv/bin/pre-commit autoupdate
```

## Linting Rules Enforced

| Rule | Limit | Warning | Fatal |
|------|-------|---------|-------|
| File length | 500 | 500+ | 1000+ |
| Function length | 50 | 50+ | 100+ |
| Function branches | 7 | 7+ | 10+ |
| Function parameters | 5 | 5+ | 7+ |
| Class size | 300 | 300+ | 500+ |
| Nesting depth | 4 | 4+ | 5+ |
| Import count | 20 | 20+ | 25+ |
| Wildcard imports | - | - | Always |

## Useful Combinations

```bash
# Find all files with violations
for f in $(find control libs -name "*.py"); do
  python3 build/lint.py "$f" 2>&1 | grep -q "FATAL" && echo "$f"
done

# Count violations by type
python3 build/lint.py control/gtk4_gui/handlers/*.py 2>&1 | grep "❌" | wc -l

# List all warnings
python3 build/lint.py control/gtk4_gui/handlers/*.py 2>&1 | grep "⚠️"

# Auto-fix all ruff violations
./build/python/venv/bin/ruff check --fix control/ libs/
```

## Troubleshooting

```bash
# Pre-commit not found
./build/python/venv/bin/pip install pre-commit

# Ruff not found
./build/python/venv/bin/pip install ruff

# Reinstall hooks
./build/python/venv/bin/pre-commit install -f

# Clear pre-commit cache
./build/python/venv/bin/pre-commit clean
```

