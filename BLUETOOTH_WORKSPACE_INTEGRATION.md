# Bluetooth Workspace Integration Guide

## Overview

This document describes how to integrate the Bluetooth Workspace component into the Unhinged desktop application. The workspace provides advanced Bluetooth device management with continuous discovery, force grab functionality, and event framework integration.

## Components

### 1. ViewBase (`control/gtk4_gui/views/base.py`)
Abstract base class for all views with lifecycle management.

**Key Methods**:
- `on_ready()` - Called when view is displayed
- `on_cleanup()` - Called when view is closed
- `_log_event(event_type, details)` - Log events to session
- `show_status(message, status_type)` - Display status messages

### 2. BluetoothWorkspace (`control/gtk4_gui/components/bluetooth_workspace.py`)
Advanced Bluetooth management component.

**Key Methods**:
- `create_content()` - Create UI with two tabs
- `on_ready()` - Start discovery loop
- `on_cleanup()` - Stop discovery loop
- `force_grab_device(address, name)` - Force grab a device
- `_perform_discovery()` - One discovery cycle

### 3. StatusStack (`control/gtk4_gui/components/status_stack.py`)
Status display component for operation feedback.

**Key Methods**:
- `create_widget()` - Create status stack widget
- `push_status(message, status_type)` - Add status message
- `get_session_history()` - Get all messages
- `get_status_summary()` - Get status counts

## Integration Steps

### Step 1: Update BluetoothView to Use ViewBase

```python
from views.base import ViewBase
from components.bluetooth_workspace import BluetoothWorkspace
from components.status_stack import StatusStack

class BluetoothView(ViewBase):
    def __init__(self, parent_app):
        super().__init__(parent_app, "bluetooth")
        self.workspace = None
        self.status_stack = None
    
    def create_content(self):
        # Create main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        
        # Create status stack at top
        self.status_stack = StatusStack(max_messages=5)
        main_box.append(self.status_stack.create_widget())
        
        # Create workspace
        self.workspace = BluetoothWorkspace(
            parent_app=self.app,
            session_logger=self.session_logger
        )
        main_box.append(self.workspace.create_content())
        
        return main_box
    
    def on_ready(self):
        super().on_ready()
        if self.workspace:
            self.workspace.on_ready()
    
    def on_cleanup(self):
        if self.workspace:
            self.workspace.on_cleanup()
        super().on_cleanup()
```

### Step 2: Update Desktop App to Call Lifecycle Hooks

In `desktop_app.py`, when switching views:

```python
def _on_view_changed(self, view_name):
    # Cleanup previous view
    if self.current_view and hasattr(self.current_view, 'on_cleanup'):
        self.current_view.on_cleanup()
    
    # Switch to new view
    self.current_view = self.views[view_name]
    
    # Call on_ready for new view
    if hasattr(self.current_view, 'on_ready'):
        self.current_view.on_ready()
```

### Step 3: Integrate Status Stack with Operations

In components that perform operations:

```python
# In BluetoothRow or similar component
def _on_force_grab_clicked(self, button):
    try:
        # Show pending status
        if hasattr(self.app, 'status_stack'):
            self.app.status_stack.push_status(
                f"Force grabbing {self.device_info.name}...",
                "pending"
            )
        
        # Perform operation
        workspace = BluetoothWorkspace(self.app, self.app.session_logger)
        success = workspace.force_grab_device(
            self.device_info.address,
            self.device_info.name
        )
        
        # Show result
        if success:
            self.app.status_stack.push_status(
                f"Connected to {self.device_info.name}",
                "success"
            )
        else:
            self.app.status_stack.push_status(
                f"Failed to connect to {self.device_info.name}",
                "error"
            )
    except Exception as e:
        self.app.status_stack.push_status(f"Error: {e}", "error")
```

## Event Framework Integration

All operations are logged through the event framework:

### Discovery Events
```
DISCOVERY_STARTED - Continuous discovery loop started
DISCOVERY_CYCLE - Discovery cycle completed (with counts)
DISCOVERY_STOPPED - Discovery loop stopped
DISCOVERY_ERROR - Discovery failed
```

### Force Grab Events
```
FORCE_GRAB_STARTED - Force grab operation started
FORCE_GRAB_SUCCESS - Device successfully connected
FORCE_GRAB_FAILED - Connection failed
FORCE_GRAB_ERROR - Unexpected error
```

### Workspace Events
```
WORKSPACE_INIT - Workspace created
WORKSPACE_CREATED - UI created
WORKSPACE_READY - Workspace displayed
WORKSPACE_CLEANUP - Workspace closed
```

## Session Logging

All events are captured in session logs:

```
[2025-01-26T10:30:45.123Z] [GUI] WORKSPACE_READY: Bluetooth workspace is now active
[2025-01-26T10:30:46.456Z] [GUI] DISCOVERY_STARTED: Continuous discovery loop started
[2025-01-26T10:30:49.789Z] [GUI] DISCOVERY_CYCLE: Registered: 2, Discovering: 1
[2025-01-26T10:31:00.000Z] [GUI] FORCE_GRAB_STARTED: Force grabbing Logitech Pro X2 (AA:BB:CC:DD:EE:FF)
[2025-01-26T10:31:05.000Z] [GUI] FORCE_GRAB_SUCCESS: Successfully connected to Logitech Pro X2
```

## Testing

### Unit Tests

```python
def test_discovery_loop():
    workspace = BluetoothWorkspace()
    workspace.on_ready()
    assert workspace.discovery_active
    workspace.on_cleanup()
    assert not workspace.discovery_active

def test_force_grab():
    workspace = BluetoothWorkspace()
    success = workspace.force_grab_device("AA:BB:CC:DD:EE:FF", "Test Device")
    assert isinstance(success, bool)

def test_status_stack():
    stack = StatusStack(max_messages=5)
    stack.push_status("Test message", "info")
    assert len(stack.messages) == 1
    assert stack.messages[0][2] == "Test message"
```

### Integration Tests

1. Open Bluetooth workspace
2. Verify discovery starts automatically
3. Verify devices appear in both tables
4. Click Force Grab on a device
5. Verify status updates show progress
6. Verify device connects to desktop
7. Close workspace
8. Verify discovery stops

## Troubleshooting

### Discovery Not Starting
- Check BluetoothMonitor.start_discovery() is working
- Verify D-Bus is available
- Check bluetoothctl is installed

### Force Grab Not Working
- Verify device is paired
- Check BluetoothMonitor.connect_device() works
- Verify sudo access (if needed)

### Status Stack Not Showing
- Verify StatusStack widget is added to view
- Check session_logger is initialized
- Verify push_status() is called

## References

- `BLUETOOTH_WORKSPACE_ARCHITECTURE.md` - Architecture overview
- `control/gtk4_gui/views/base.py` - View lifecycle base class
- `control/gtk4_gui/components/bluetooth_workspace.py` - Workspace implementation
- `control/gtk4_gui/components/status_stack.py` - Status display
- `control/gtk4_gui/bluetooth_monitor.py` - Bluetooth operations
- `libs/event-framework/` - Event logging framework

