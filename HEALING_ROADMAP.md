# Project Healing Roadmap

## STATIC ANALYSIS INTEGRATION

**New Command Available:**
```bash
./unhinged dev analyze [module]    # Run static analysis
./unhinged dev analyze control     # Analyze control/ module
./unhinged dev analyze             # Analyze all modules
```

**What it does:**
- Detects changed files (via checksums)
- Runs ruff static analysis
- Auto-fixes violations
- Caches results

**Current Status:**
- 2438 ruff errors found in control/
- Mostly unused imports and style issues
- Can be auto-fixed with `./unhinged dev fix`

---

## PHASE 1: UNBLOCK TESTING (Priority: CRITICAL)

**Time: 30 minutes**

### Task 1.1: Fix test_components.py
```bash
# Find the sys.exit(1) call
grep -n "sys.exit" control/gtk4_gui/tests/test_components.py

# Either:
# A) Remove the sys.exit() line
# B) Comment it out
# C) Fix the underlying issue causing the exit
```

**Why:** Blocks all pytest discovery. Can't run any tests.

### Task 1.2: Run tests
```bash
./unhinged dev test
```

**Expected:** All tests pass or show real failures (not import errors)

---

## PHASE 2: FIX FATAL VIOLATIONS (Priority: HIGH)

**Time: 4-6 hours**

### Task 2.1: system_info.py (1024 → <1000 lines)
- Only 24 lines over
- Likely: 2-3 classes
- Action: Extract 1 class to separate file
- Estimated: 1 hour

### Task 2.2: chatroom_view.py (1720 → <1000 lines)
- 720 lines over (major)
- 55+ methods in single class
- Action: Extract into 3-4 component files
  - ChatroomUI (UI creation)
  - ChatroomSession (session management)
  - ChatroomChat (chat events)
  - ChatroomVoice (voice recording)
- Estimated: 3-5 hours

---

## PHASE 3: FIX WARNINGS (Priority: MEDIUM)

**Time: 8-12 hours (do incrementally)**

### Group A: Large Files (500-600 lines)
- realtime_system_info.py (511 lines)
- test_monitors.py (510 lines)
- form_input.py (550 lines)
- graph_canvas.py (551 lines)
- graph_workspace_view.py (530 lines)

**Pattern:** Extract 1-2 helper classes per file

### Group B: Very Large Files (700+ lines)
- bluetooth_monitor.py (802 lines)
- audio_handler_backup.py (704 lines)
- service_launcher.py (580 lines)
- desktop_app.py (931 lines)

**Pattern:** Extract 2-3 classes per file

### Group C: Imports
- audio_handler.py (23 imports, target: <20)
- audio_handler_refactored.py (23 imports)

**Action:** Consolidate imports, remove unused

### Group D: Libs
- gui_session_logger.py (568 lines)
- io_abstraction.py (614 lines)

**Action:** Extract modules

---

## EXECUTION STRATEGY

**Do NOT do all at once.** Pick one file, fix it, test, commit.

### Recommended Order:
1. **system_info.py** (easiest, 1 hour)
2. **test_monitors.py** (easy, 30 min)
3. **realtime_system_info.py** (easy, 30 min)
4. **audio_handler imports** (easy, 15 min)
5. **chatroom_view.py** (hardest, 3-5 hours)

---

## COMMANDS TO USE

```bash
# Check specific file
./unhinged dev lint -v | grep "system_info"

# Auto-fix what you can
./unhinged dev fix

# Format after changes
./unhinged dev format

# Run tests
./unhinged dev test

# Commit when done
git add .
git commit -m "refactor: reduce system_info.py from 1024 to <1000 lines"
```

---

## SUCCESS CRITERIA

- [ ] All tests pass
- [ ] 0 fatal violations
- [ ] <10 warnings
- [ ] All files <500 lines (except approved exceptions)
- [ ] All functions <50 lines
- [ ] All classes <300 lines

