# DEPRECATED: Top-Level Files

**⚠️ These top-level files are deprecated and should be removed:**

## Deprecated Files

### `activate-venv.sh`
- **Purpose**: Activation script for `.venv/` 
- **Problem**: Points to non-working `.venv/` instead of `venv-production/`
- **Replacement**: `source venv-production/bin/activate`

### `build/setup-unified-venv.py`
- **Purpose**: "Unified" venv setup that creates `.venv/`
- **Problem**: Conflicts with working `venv-production/`
- **Replacement**: `make setup-python` (uses `venv-production/`)

## Current Working System

**Single Python Environment: `venv-production/`**

```bash
# Setup (creates venv-production/ with everything)
make setup-python

# Activate manually if needed
source venv-production/bin/activate

# Run scripts
./venv-production/bin/python script.py

# Static analysis
make check-code
```

## The Problem We Fixed

Before cleanup:
- `build/python/venv/` ← Makefile expected this
- `.venv/` ← "Unified" setup created this  
- `venv-production/` ← Actually worked and had ruff

After cleanup:
- `venv-production/` ← Single source of truth
- Makefile uses this
- Static analysis works
- Git hooks work

## Migration Status

✅ **Makefile updated** to use `venv-production/`
✅ **Git hooks updated** to use `venv-production/`
✅ **Static analysis working** with `venv-production/`
✅ **All scripts updated** to use `venv-production/`

🚧 **TODO**: Remove deprecated files after verification
# Test change
