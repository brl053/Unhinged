# DEPRECATED: build/python/ Directory

**⚠️ This directory contains deprecated Python setup scripts.**

## What happened?

This directory was part of an old ML/AI ETL setup system that created multiple competing Python environments:

- `build/python/setup.py` → Created `build/python/venv/`
- `build/setup-unified-venv.py` → Created `.venv/`
- `venv-production/` → The actual working environment

## Current Status

**Use `venv-production/` instead:**

```bash
# Correct way to setup Python environment:
make setup-python

# This creates and uses venv-production/ with:
# - All required dependencies
# - Static analysis tools (ruff)
# - Git hooks for code quality
```

## Migration

The Makefile has been updated to use `venv-production/` as the single source of truth for Python environment.

**Old commands that used this directory:**
- `cd build/python && python3 setup.py` ❌
- `build/python/venv/bin/python` ❌

**New commands:**
- `make setup-python` ✅
- `./venv-production/bin/python` ✅

## Files in this directory

- `setup.py` - Old ML/AI ETL setup (deprecated)
- `run.py` - Universal Python runner (still used)
- `requirements.txt` - Old requirements (use `build/requirements-core.txt`)
- `venv/` - Old virtual environment (use `venv-production/`)

## Cleanup

This directory will be removed in a future cleanup once all references are migrated to the unified `venv-production/` system.
