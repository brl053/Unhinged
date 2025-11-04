@llm-doc Phase 4e - Integration Example
@llm-version 1.0.0
@llm-date 2025-01-26

# Phase 4e: Integration Example - How to Use Structured Logging

## Example 1: Startup Sequence

### Before (Chaotic Output)

```
✅ Database already running
✅ Redis Cache already running
ℹ️ Creating Bluetooth page successfully
RuntimeWarning: coroutine 'RegistryUI._load_graphs' was never awaited
ℹ️ Bluetooth discovery starting
✅ Found 3 registered devices
```

### After (Structured Output)

```
══════════════════════════════════════════════════════════════════════
[STARTUP]
══════════════════════════════════════════════════════════════════════
✅ Database already running
✅ Redis Cache already running
✅ Event framework initialized
──────────────────────────────────────────────────────────────────────

══════════════════════════════════════════════════════════════════════
[UI]
══════════════════════════════════════════════════════════════════════
✅ Creating Bluetooth page successfully
✅ Bluetooth workspace initialized
──────────────────────────────────────────────────────────────────────

══════════════════════════════════════════════════════════════════════
[DISCOVERY]
══════════════════════════════════════════════════════════════════════
ℹ️ Bluetooth discovery starting
✅ Found 3 registered devices
✅ Found 1 discovering device
──────────────────────────────────────────────────────────────────────
```

## Example 2: Code Changes Required

### In `desktop_app.py`

```python
from events.io_abstraction import emit_info, emit_success, emit_error

class DesktopApp(Adw.Application):
    def __init__(self):
        super().__init__()
        emit_info("Initializing Unhinged Desktop Application", "startup")
    
    def _check_dependencies(self):
        """Check system dependencies"""
        emit_info("Pre-flight checks starting", "startup")
        
        try:
            if self._check_database():
                emit_success("Database already running", "startup")
            else:
                emit_error("Database not running", "startup")
        except Exception as e:
            emit_error(f"Database check failed: {e}", "startup")
        
        try:
            if self._check_redis():
                emit_success("Redis Cache already running", "startup")
            else:
                emit_error("Redis Cache not running", "startup")
        except Exception as e:
            emit_error(f"Redis check failed: {e}", "startup")
```

### In `bluetooth_workspace.py`

```python
from events.io_abstraction import emit_info, emit_success, emit_error

class BluetoothWorkspace(Gtk.Box):
    def on_ready(self):
        """Start discovery loop"""
        emit_info("Bluetooth workspace activated", "bluetooth")
        emit_info("Starting device discovery", "discovery")
        self._start_discovery_loop()
    
    def _update_device_tables(self):
        """Update device tables with current devices"""
        try:
            registered = self.monitor.get_registered_devices()
            discovering = self.monitor.get_discovering_devices()
            
            emit_success(
                f"Found {len(registered)} registered devices",
                "discovery"
            )
            emit_success(
                f"Found {len(discovering)} discovering devices",
                "discovery"
            )
            
            # Update UI tables
            self._populate_registered_table(registered)
            self._populate_discovering_table(discovering)
            
        except Exception as e:
            emit_error(f"Failed to update device tables: {e}", "discovery")
```

### In `bluetooth_row.py`

```python
from events.io_abstraction import emit_info, emit_success, emit_error

class BluetoothRow(Gtk.ListBoxRow):
    def _on_force_grab_clicked(self, button):
        """Handle Force Grab button click"""
        device_name = self.device.name
        emit_info(f"Force grabbing {device_name}", "bluetooth")
        
        try:
            # Disconnect from other devices
            emit_info(f"Disconnecting from other devices", "bluetooth")
            self.monitor.disconnect_all_except(self.device.address)
            
            # Connect to this device
            emit_info(f"Connecting to {device_name}", "bluetooth")
            self.monitor.connect_device(self.device.address)
            
            emit_success(f"Connected to {device_name}", "bluetooth")
            
        except Exception as e:
            emit_error(f"Failed to connect to {device_name}: {e}", "bluetooth")
```

## Example 3: Output Filtering

### Get all errors

```python
from events.io_abstraction import get_io_router, IOLevel

router = get_io_router()
# Find the buffer handler
buffer = None
for handlers in router.handlers.values():
    for handler in handlers:
        if hasattr(handler, 'wrapped_handler'):
            if hasattr(handler.wrapped_handler, 'events'):
                buffer = handler.wrapped_handler
                break

if buffer:
    errors = buffer.get_events_by_level(IOLevel.ERROR)
    for error in errors:
        print(f"[{error.source}] {error.message}")
```

### Get all events from a source

```python
bluetooth_events = buffer.get_events_by_source("bluetooth")
for event in bluetooth_events:
    print(f"[{event.level.value}] {event.message}")
```

## Example 4: Custom Handler

### Create a file logger

```python
from events.io_abstraction import IOHandler, IOEvent
import logging

class FileLogHandler(IOHandler):
    def __init__(self, filename: str):
        self.logger = logging.getLogger("unhinged")
        handler = logging.FileHandler(filename)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def handle(self, event: IOEvent) -> None:
        level_map = {
            IOLevel.DEBUG: logging.DEBUG,
            IOLevel.INFO: logging.INFO,
            IOLevel.SUCCESS: logging.INFO,
            IOLevel.WARNING: logging.WARNING,
            IOLevel.ERROR: logging.ERROR,
        }
        self.logger.log(
            level_map[event.level],
            f"[{event.source}] {event.message}"
        )

# Register it
from events.io_abstraction import get_io_router
router = get_io_router()
router.register_handler(FileLogHandler("/tmp/unhinged.log"))
```

## Example 5: Status Stack Integration

### Create StatusStackHandler

```python
from events.io_abstraction import IOHandler, IOEvent

class StatusStackHandler(IOHandler):
    def __init__(self, status_stack):
        self.status_stack = status_stack
    
    def handle(self, event: IOEvent) -> None:
        # Format message with emoji
        emoji_map = {
            IOLevel.DEBUG: "🔍",
            IOLevel.INFO: "ℹ️",
            IOLevel.SUCCESS: "✅",
            IOLevel.WARNING: "⚠️",
            IOLevel.ERROR: "❌",
        }
        emoji = emoji_map.get(event.level, "•")
        message = f"{emoji} [{event.source}] {event.message}"
        
        # Add to status stack
        self.status_stack.add_message(message, event.level)

# Register it
from events.io_abstraction import get_io_router
router = get_io_router()
router.register_handler(StatusStackHandler(status_stack))
```

## Migration Path

### Phase 1: Add IO abstraction (DONE ✅)
- Created IOEvent, IORouter, IOHandler classes
- Implemented CLIHandler, LogHandler, BufferHandler
- Implemented DelimiterHandler

### Phase 2: Replace print() statements
- In startup sequence
- In discovery loop
- In UI operations
- In error handling

### Phase 3: Add custom handlers
- StatusStackHandler for UI
- FileLogHandler for logging
- JSONHandler for structured logs
- RemoteHandler for server-side logging

### Phase 4: Integrate into all components
- desktop_app.py
- bluetooth_workspace.py
- bluetooth_row.py
- registry_ui.py
- All other components

### Phase 5: LLM-driven analysis
- Collect events in BufferHandler
- Analyze patterns
- Suggest improvements

## Benefits Summary

✅ **Clear Output**: Grouped by source with delimiters
✅ **Flexible Routing**: Same event to multiple handlers
✅ **Debuggability**: Each event has source and timestamp
✅ **Extensibility**: Easy to add new handlers
✅ **Composability**: Handlers can wrap other handlers
✅ **Determinism**: Predictable output structure

## Status

**PHASE 4E COMPLETE** ✅

Structured logging with delimiters is fully implemented and tested. Ready for Phase 5 (custom handlers) and beyond.

