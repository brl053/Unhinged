# Direction: Project Healing & Feature Development

## CURRENT STATE

**Project Health:** 🔴 UNHEALTHY
- Static Analysis: 2638 errors
- Tests: BROKEN (test_components.py has sys.exit)
- Lint: 2 fatal, 15 warnings

**What's Ready:**
- CLI migrated to Python (550 lines, 11 tests passing)
- Health check system (3-tier)
- Project healing roadmap
- Static analysis integrated

---

## IMMEDIATE PRIORITIES (Next 2 Days)

### PRIORITY 1: UNBLOCK TESTS (2 hours)
**Why:** Can't measure progress without tests
```bash
# 1. Fix test_components.py
grep -n "sys.exit" control/gtk4_gui/tests/test_components.py
# Remove or comment out the sys.exit(1) line

# 2. Verify tests run
./unhinged dev test
```

### PRIORITY 2: FIX STATIC ANALYSIS (4-6 hours)
**Why:** 2638 errors = project is broken
```bash
# 1. Run analysis
./unhinged dev static-analysis

# 2. Auto-fix
./unhinged dev fix

# 3. Format
./unhinged dev format

# 4. Verify
./unhinged dev static-analysis
```

### PRIORITY 3: FIX FATAL LINT VIOLATIONS (4-6 hours)
**Why:** 2 files over size limits block merge
```bash
# 1. Check violations
./unhinged dev lint -v

# 2. Fix system_info.py (1024 → <1000 lines)
# Extract 1 class to separate file

# 3. Fix chatroom_view.py (1720 → <1000 lines)
# Extract 3-4 component files

# 4. Verify
./unhinged dev lint
```

---

## THEN: WARNINGS (8-12 hours)

11 files over size limits. Do incrementally:
- realtime_system_info.py (511 lines)
- test_monitors.py (510 lines)
- form_input.py (550 lines)
- graph_canvas.py (551 lines)
- graph_workspace_view.py (530 lines)
- bluetooth_monitor.py (802 lines)
- audio_handler_backup.py (704 lines)
- desktop_app.py (931 lines)
- system_view.py (997 lines)
- service_launcher.py (580 lines)
- containers.py (1000 lines)

---

## THEN: FEATURE WORK

Once project is healthy:
- Audio device improvements
- Graphics platform features
- Service enhancements
- UI/UX improvements

---

## HEALTH CHECK COMMANDS

```bash
# All three must pass
./unhinged dev static-analysis  # Ruff
./unhinged dev test             # Unit tests
./unhinged dev lint             # Architecture
```

## DOCUMENTATION

- HEALING_QUICK_START.md - Quick reference
- HEALING_ROADMAP.md - Detailed plan
- PROJECT_HEALTH_REPORT.md - Full analysis

---

## SUCCESS CRITERIA

- [ ] test_components.py fixed
- [ ] static-analysis passes
- [ ] All tests pass
- [ ] lint: 0 fatal, <5 warnings
- [ ] All files <500 lines (except approved)
- [ ] Ready for feature development

