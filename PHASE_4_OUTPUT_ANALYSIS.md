@llm-doc Phase 4 - Output Analysis & Root Cause Mapping
@llm-version 1.0.0
@llm-date 2025-01-26

# Phase 4: Developer Experience - Output Analysis

## Output Source Map

### 1. GLib RuntimeWarning: coroutine 'RegistryUI._load_graphs' was never awaited

**Source**: `/control/gtk4_gui/components/registry_ui.py:199`

**Root Cause**:
```python
def _load_graphs_idle(self):
    """Idle callback to load graphs when event loop is ready"""
    try:
        asyncio.create_task(self._load_graphs())  # Creates coroutine
    except RuntimeError:
        GLib.idle_add(self._load_graphs_idle)  # Calls itself again
    return False  # Don't repeat
```

The problem: `GLib.idle_add()` is being called with `self._load_graphs_idle` (a method), but when it's called again, it tries to create a task in a context where the event loop might not be properly set up.

**Why it's emitted**: Python's asyncio is warning that a coroutine was created but never awaited. This happens because the GLib event loop and asyncio event loop are not properly synchronized.

**Frequency**: Repeats every 3 seconds (discovery loop cycle)

**Impact**: Non-fatal but indicates improper async/GLib integration

---

### 2. Failed to update device tables: attempted relative import with no known parent package

**Source**: `/control/gtk4_gui/components/bluetooth_workspace.py:283`

**Root Cause**:
```python
def _update_device_tables(self):
    """Update the device tables with current device lists."""
    try:
        from primitives import BluetoothRow  # RELATIVE IMPORT - WRONG!
```

When `bluetooth_workspace.py` is imported as a module, relative imports fail because Python doesn't know the package context.

**Why it's emitted**: The import fails silently (caught by try/except), but the error is logged.

**Frequency**: Every discovery cycle (every 3 seconds)

**Impact**: Device tables never update - critical functionality broken

---

### 3. Info/Success Messages (Pre-flight, Services, Pages)

**Source**: Multiple files in startup sequence

**Examples**:
- `ℹ️ Starting Unhinged dual-system architecture...`
- `✅ Database already running`
- `✅ Created Bluetooth page successfully`

**Why it's emitted**: Normal startup logging - these are intentional

**Impact**: Informational only, but mixed with errors makes output hard to parse

---

## Output Chaos Root Causes

1. **Mixed Concerns**: Startup logs, warnings, errors, and info all on stdout
2. **No Delimiters**: Can't tell where one concern ends and another begins
3. **Async/GLib Mismatch**: Two event loops fighting each other
4. **Import Path Issues**: Relative imports don't work in module context
5. **No Structured Format**: Each component logs differently

---

## Solution Architecture

### Phase 4b: Fix Import Error (CRITICAL)
Change line 283 in bluetooth_workspace.py:
```python
# FROM:
from primitives import BluetoothRow

# TO:
from .primitives import BluetoothRow  # Relative import with dot
# OR:
from control.gtk4_gui.components.primitives import BluetoothRow  # Absolute
```

### Phase 4c: Fix GLib Async Issue
Properly integrate asyncio with GLib event loop:
```python
def _load_graphs_idle(self):
    """Idle callback to load graphs when event loop is ready"""
    try:
        # Use GLib's async support instead of asyncio.create_task
        asyncio.ensure_future(self._load_graphs())
        return False  # Don't repeat
    except RuntimeError:
        # Retry later
        GLib.idle_add(self._load_graphs_idle)
        return False
```

### Phase 4d: Standard IO Abstraction
Create event framework abstraction:
```python
# libs/event_framework/io_abstraction.py
class IOEvent:
    """Abstraction for stdout/stderr events"""
    def __init__(self, message: str, level: str, source: str):
        self.message = message
        self.level = level  # 'info', 'warning', 'error', 'debug'
        self.source = source  # 'startup', 'discovery', 'ui', etc
        self.timestamp = datetime.now()

class IORouter:
    """Routes IO events to appropriate handlers"""
    def __init__(self):
        self.handlers = {}  # level -> [handler1, handler2, ...]
    
    def emit(self, event: IOEvent):
        """Emit IO event to all registered handlers"""
        for handler in self.handlers.get(event.level, []):
            handler(event)
```

### Phase 4e: Structured Logging with Delimiters
```
═══════════════════════════════════════════════════════════════
[STARTUP] Pre-flight Checks
═══════════════════════════════════════════════════════════════
✅ Database already running
✅ Redis Cache already running
───────────────────────────────────────────────────────────────

═══════════════════════════════════════════════════════════════
[DISCOVERY] Bluetooth Device Discovery Cycle
═══════════════════════════════════════════════════════════════
🔍 Scanning for devices...
✅ Found 3 registered devices
✅ Found 1 discovering device
───────────────────────────────────────────────────────────────

═══════════════════════════════════════════════════════════════
[ERRORS] Issues Detected
═══════════════════════════════════════════════════════════════
⚠️ GLib async integration issue (non-fatal)
───────────────────────────────────────────────────────────────
```

---

## Implementation Order

1. **Phase 4b** (CRITICAL): Fix import error - unblocks device table updates
2. **Phase 4c** (HIGH): Fix GLib async - eliminates RuntimeWarning spam
3. **Phase 4a** (MEDIUM): Document all output sources
4. **Phase 4d** (MEDIUM): Create IO abstraction layer
5. **Phase 4e** (LOW): Add delimiters and structured logging

---

## Success Criteria

- [ ] No "attempted relative import" errors
- [ ] No "coroutine was never awaited" warnings
- [ ] Device tables update successfully every 3 seconds
- [ ] Output is organized by concern with clear delimiters
- [ ] Can redirect output to different handlers (CLI, logs, UI)

