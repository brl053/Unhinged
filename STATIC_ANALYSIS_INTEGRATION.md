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

## Proposed Workflow Integration

### Add to CLI

```python
# control/cli/commands/dev.py - add new command

@dev.command()
@click.argument("module", required=False, default="control")
def analyze(module):
    """Run static analysis on module (only if changed)."""
    from build.static_analysis_manager import StaticAnalysisManager
    
    sam = StaticAnalysisManager()
    if not sam.should_run_analysis(module):
        log_info(f"No changes in {module}, skipping analysis")
        return 0
    
    log_info(f"Running static analysis on {module}...")
    result = sam.run_analysis(module, auto_fix=True)
    
    if result.passed:
        log_success(f"Analysis passed ({result.fixed_count} auto-fixed)")
    else:
        log_error(f"Analysis failed: {len(result.errors)} errors")
        for error in result.errors[:5]:
            print(f"  - {error}")
    
    return 0 if result.passed else 1
```

### Updated Workflow

```bash
# Check what changed
./unhinged dev analyze control

# Only runs if control/ has changes
# Auto-fixes violations
# Caches results

# Run on all modules
./unhinged dev analyze

# Run on specific module
./unhinged dev analyze control/gtk4_gui
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

