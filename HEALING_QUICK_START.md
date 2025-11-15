# Project Healing - Quick Start

## Current Status

```
❌ FATAL: 2 violations
⚠️  WARNING: 15 violations
🔴 TESTS: BROKEN (sys.exit in test_components.py)
```

## Commands You Need

```bash
# See all violations (custom linter)
./unhinged dev lint -v

# Run static analysis (ruff, change-aware)
./unhinged dev analyze control

# Auto-fix what you can
./unhinged dev fix

# Format code
./unhinged dev format

# Run tests
./unhinged dev test
```

## Workflow with Static Analysis

```bash
# 1. Check what changed
./unhinged dev analyze control

# 2. Auto-fix violations
./unhinged dev fix

# 3. Format code
./unhinged dev format

# 4. Run tests
./unhinged dev test

# 5. Check custom linter
./unhinged dev lint -v
```

## Files to Fix (Priority Order)

### MUST FIX (Blocking)
1. **test_components.py** - Remove sys.exit(1) at module level
2. **system_info.py** - 1024 lines (24 over limit)
3. **chatroom_view.py** - 1720 lines (720 over limit)

### SHOULD FIX (Easy Wins)
4. test_monitors.py - 510 lines (10 over)
5. realtime_system_info.py - 511 lines (11 over)
6. form_input.py - 550 lines (50 over)

### NICE TO FIX (Medium Effort)
7. bluetooth_monitor.py - 802 lines
8. audio_handler_backup.py - 704 lines
9. desktop_app.py - 931 lines
10. system_view.py - 997 lines

## Workflow

```bash
# 1. Pick a file
FILE="control/gtk4_gui/system_info.py"

# 2. Check violations
./unhinged dev lint -v | grep "system_info"

# 3. Make changes (extract classes, etc)
# Edit the file...

# 4. Auto-fix
./unhinged dev fix "$FILE"

# 5. Format
./unhinged dev format "$FILE"

# 6. Test
./unhinged dev test

# 7. Commit
git add "$FILE"
git commit -m "refactor: reduce $FILE to <500 lines"
```

## See Full Details

- `PROJECT_HEALTH_REPORT.md` - Complete analysis
- `HEALING_ROADMAP.md` - Detailed work plan
- `QUICK_REFERENCE.md` - Command reference

## Start Here

```bash
# 1. Fix test_components.py first
# 2. Then fix system_info.py
# 3. Then fix chatroom_view.py
# 4. Then tackle warnings
```

**Estimated total time: 12-16 hours**

