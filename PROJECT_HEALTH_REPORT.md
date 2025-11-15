# Project Health Report

**Generated:** 2025-11-15
**Status:** 🟡 NEEDS HEALING

---

## EXECUTIVE SUMMARY

| Metric | Status | Details |
|--------|--------|---------|
| **Linting** | 🔴 FAILING | 2 fatal, 15 warnings |
| **Tests** | 🔴 BROKEN | test_components.py has sys.exit(1) |
| **Architecture** | 🟢 GOOD | CLI migrated to Python, 550 lines |
| **Code Quality** | 🟡 DEGRADED | 17 files over size limits |

---

## LINTING STATUS: 2 FATAL, 15 WARNINGS

### FATAL (MUST FIX)

**1. control/gtk4_gui/system_info.py** - 1024 lines (limit: 1000)
   - 24 lines over limit
   - Likely: Multiple classes/responsibilities
   - Action: Extract 1-2 classes to separate files

**2. control/gtk4_gui/views/chatroom_view.py** - 1720 lines (limit: 1000)
   - 720 lines over limit
   - Likely: 55+ methods in single class
   - Action: Decompose into 3-4 component files

### WARNINGS (SHOULD FIX)

**File Length Warnings (11 files):**
- control/gtk4_gui/bluetooth_monitor.py - 802 lines
- control/gtk4_gui/components/containers.py - 1000 lines
- control/gtk4_gui/components/form_input.py - 550 lines
- control/gtk4_gui/components/graph_canvas.py - 551 lines
- control/gtk4_gui/desktop_app.py - 931 lines
- control/gtk4_gui/handlers/audio_handler_backup.py - 704 lines
- control/gtk4_gui/realtime_system_info.py - 511 lines
- control/gtk4_gui/tests/test_monitors.py - 510 lines
- control/gtk4_gui/views/graph_workspace_view.py - 530 lines
- control/gtk4_gui/views/system_view.py - 997 lines
- control/service_launcher.py - 580 lines

**Import Count Warnings (2 files):**
- control/gtk4_gui/handlers/audio_handler.py - 23 imports (target: <20)
- control/gtk4_gui/handlers/audio_handler_refactored.py - 23 imports

**Libs Warnings (2 files):**
- libs/event-framework/python/src/events/gui_session_logger.py - 568 lines
- libs/event-framework/python/src/events/io_abstraction.py - 614 lines

---

## TESTING STATUS: BROKEN

**Issue:** control/gtk4_gui/tests/test_components.py has `sys.exit(1)` at module level
- Prevents pytest from running
- Blocks all test discovery
- Action: Remove sys.exit() or fix test file

**Working Tests:**
- control/gtk4_gui/tests/test_audio_handler.py - 7 tests ✅
- control/cli/tests/test_cli.py - 11 tests ✅

---

## WORK BREAKDOWN

### PHASE 1: UNBLOCK TESTING (1 hour)
1. Fix test_components.py (remove sys.exit)
2. Run full test suite
3. Fix any broken tests

### PHASE 2: FIX FATAL VIOLATIONS (4-6 hours)
1. **system_info.py** (24 lines over) - Extract 1 class
2. **chatroom_view.py** (720 lines over) - Extract 3-4 components

### PHASE 3: FIX WARNINGS (8-12 hours)
1. File length warnings (11 files) - Extract classes/functions
2. Import warnings (2 files) - Consolidate imports
3. Libs warnings (2 files) - Extract modules

### PHASE 4: VERIFY (1 hour)
1. Run full lint check
2. Run full test suite
3. Verify all metrics pass

---

## NEXT STEPS

**Immediate (today):**
```bash
./unhinged dev lint -v          # See all violations
./unhinged dev test             # Identify test issues
```

**Then pick one phase above and execute.**

