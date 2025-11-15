# Static Analysis Integration

## Current State

**Existing System:**
- `build/static_analysis_manager.py` - Sophisticated analysis manager
- `build/checksum_manager.py` - Change detection system
- `build/static_analysis_results.json` - Results cache

**Missing:**
- CLI integration (not exposed in `./unhinged dev`)
- Workflow documentation
- Pre-commit hook integration

## What Static Analysis Does

1. **Change Detection** - Only runs when Python files change (via checksums)
2. **Ruff Integration** - Runs ruff check and fix
3. **Results Caching** - Stores results in JSON
4. **Auto-fix** - Can automatically fix violations
5. **Module-level** - Analyzes by module (control/, libs/, etc)

## Workflow Integration

### Command

```bash
./unhinged dev static-analysis
```

**What it does:**
- Runs on ALL modules (control, libs)
- Only if files changed (via checksums)
- Auto-fixes violations
- Caches results
- BLOCKING: Project unhealthy if fails

### Health Check Order

```bash
# 1. Static Analysis (ruff: imports, style, unused)
./unhinged dev static-analysis

# 2. Unit Tests
./unhinged dev test

# 3. Architecture Linter (size, complexity)
./unhinged dev lint

# All three must pass
```

## Integration Points

1. **Pre-commit hook** - Run before commit
2. **CI/CD** - Run on every push
3. **Development** - Run after making changes
4. **Healing workflow** - Run after each fix

## Benefits

- **Efficiency** - Only analyzes changed files
- **Caching** - Results stored for quick access
- **Automation** - Auto-fixes violations
- **Tracking** - Historical results in JSON

## Next Steps

1. Add `analyze` command to CLI
2. Integrate with pre-commit hooks
3. Add to healing workflow
4. Document in HEALING_ROADMAP.md

