# Bluetooth Workspace Architecture

## Overview

The Bluetooth Workspace is an advanced component for managing Bluetooth devices in the Unhinged desktop application. It provides a clear, intuitive interface for discovering, pairing, and connecting Bluetooth devices with a "Force Grab" feature for stealing headphones from other devices.

## Architecture

### Component Hierarchy

```
BluetoothView (View)
    ↓
BluetoothWorkspace (Component)
    ├── Registered Devices Tab
    │   ├── Registered Devices Table
    │   ├── Force Grab Button (per device)
    │   └── Status Label
    │
    └── Discovering Devices Tab
        ├── Discovering Devices Table
        ├── Pair Button (per device)
        └── Status Label
```

### Key Components

#### 1. **ViewBase** (`views/base.py`)
Abstract base class for all views with lifecycle management.

**Lifecycle Hooks**:
- `on_ready()` - Called when view is displayed
- `on_cleanup()` - Called when view is closed

**Features**:
- Session-based event logging
- Status message display
- Graceful error handling

#### 2. **BluetoothWorkspace** (`components/bluetooth_workspace.py`)
Advanced Bluetooth management component with two separate tables.

**Responsibilities**:
- Manage registered devices (paired/connected)
- Manage discovering devices (registration entry point)
- Continuous discovery loop
- Force Grab feature
- Event framework integration

**Key Methods**:
- `create_content()` - Create UI with two tabs
- `on_ready()` - Start discovery loop
- `on_cleanup()` - Stop discovery loop
- `_perform_discovery()` - One discovery cycle

#### 3. **StatusStack** (`components/status_stack.py`)
High-level status display component.

**Features**:
- Displays 3-5 most recent status messages
- Color-coded by status type
- Session history tracking
- Timestamp for each message

**Status Types**:
- `info` - Informational (blue)
- `success` - Operation succeeded (green)
- `warning` - Warning (yellow)
- `error` - Error (red)
- `pending` - In progress (orange)

## Data Flow

### Discovery Loop

```
on_ready() called
    ↓
_start_discovery_loop()
    ↓
GLib.timeout_add_seconds(3, _perform_discovery)
    ↓
_perform_discovery() runs every 3 seconds
    ├── Get registered devices (paired)
    ├── Get discovering devices (unpaired)
    ├── Update UI labels
    ├── Log event
    └── Return True to continue
    ↓
on_cleanup() called
    ↓
_stop_discovery_loop()
    ↓
GLib.source_remove(timeout_id)
```

### Force Grab Operation

```
User clicks "Force Grab" on device
    ↓
_on_force_grab_clicked(device)
    ↓
StatusStack.push_status("Command launched", "pending")
    ↓
BluetoothMonitor.disconnect_device(other_devices)
    ↓
BluetoothMonitor.connect_device(desktop)
    ↓
StatusStack.push_status("Connected successfully", "success")
    ↓
Event logged to session
```

## Integration Points

### Event Framework

All operations are logged through the event framework:

```python
self._log_event("DISCOVERY_STARTED", "Continuous discovery loop started")
self._log_event("DISCOVERY_CYCLE", f"Registered: {count}, Discovering: {count}")
self._log_event("FORCE_GRAB_STARTED", f"Grabbing {device.name}")
self._log_event("FORCE_GRAB_SUCCESS", f"Connected to {device.name}")
```

### Session Logger

Events are captured in session logs for debugging and analysis:

```
[2025-01-26T10:30:45.123Z] [GUI] BLUETOOTH_WORKSPACE_READY: Bluetooth workspace is now active
[2025-01-26T10:30:46.456Z] [GUI] DISCOVERY_STARTED: Continuous discovery loop started
[2025-01-26T10:30:49.789Z] [GUI] DISCOVERY_CYCLE: Registered: 2, Discovering: 1
```

## Lifecycle Management

### View Lifecycle

1. **Initialization** - View created, `__init__` called
2. **Ready** - View displayed, `on_ready()` called
   - Discovery loop starts
   - Continuous scanning begins
3. **Active** - User interacts with view
   - Discovery runs every 3 seconds
   - Force Grab operations execute
   - Status updates display
4. **Cleanup** - View closed, `on_cleanup()` called
   - Discovery loop stops
   - Resources cleaned up
   - Session logged

### Discovery Loop Lifecycle

```
on_ready()
    ↓
_start_discovery_loop()
    ├── Set discovery_active = True
    ├── Log DISCOVERY_STARTED
    ├── Call _perform_discovery() immediately
    └── Schedule _perform_discovery() every 3 seconds
    ↓
_perform_discovery() (repeats every 3 seconds)
    ├── Check if workspace is active
    ├── Get registered devices
    ├── Get discovering devices
    ├── Update UI
    ├── Log DISCOVERY_CYCLE
    └── Return True to continue
    ↓
on_cleanup()
    ↓
_stop_discovery_loop()
    ├── Remove timeout
    ├── Set discovery_active = False
    └── Log DISCOVERY_STOPPED
```

## Force Grab Feature

### Purpose
Allow users to forcibly disconnect Bluetooth headphones from other devices (phone, tablet) and connect them to the desktop.

### Implementation
1. User clicks "Force Grab" on a registered device
2. System identifies all devices the headphones are connected to
3. Disconnects from all other devices
4. Connects to desktop
5. Status updates show progress

### Status Flow
```
"Command launched" (pending)
    ↓
"Disconnecting from iPhone..." (pending)
    ↓
"Disconnecting from Pixel..." (pending)
    ↓
"Connecting to desktop..." (pending)
    ↓
"Connected successfully" (success)
```

## Error Handling

All operations include error handling:

```python
try:
    # Perform operation
    monitor.connect_device(address)
except Exception as e:
    logger.error(f"Operation failed: {e}")
    self._log_event("OPERATION_ERROR", str(e))
    self.push_status(f"Error: {e}", "error")
```

## Testing

### Unit Tests
- Test discovery loop starts/stops correctly
- Test device list updates
- Test Force Grab operation
- Test event logging

### Integration Tests
- Test with real Bluetooth devices
- Test with multiple devices
- Test Force Grab with actual connections
- Test session logging

## Future Enhancements

1. **Bluetooth Device Registry** - Document-based registry for persistent device state
2. **Connection Profiles** - Save and restore connection configurations
3. **Auto-Connect** - Automatically connect to preferred devices
4. **Notifications** - Alert user when devices connect/disconnect
5. **Advanced Filtering** - Filter by device type, signal strength, etc.

## References

- `libs/event-framework/` - Event logging framework
- `control/gtk4_gui/views/base.py` - View lifecycle base class
- `control/gtk4_gui/components/bluetooth_workspace.py` - Workspace implementation
- `control/gtk4_gui/components/status_stack.py` - Status display component
- `control/gtk4_gui/bluetooth_monitor.py` - Bluetooth operations

