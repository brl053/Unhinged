# Bluetooth Workspace Implementation Guide

## Overview

This guide provides detailed implementation instructions for the Bluetooth Workspace component, including lifecycle management, event framework integration, and force grab functionality.

## Architecture Principles

### 1. Lifecycle Management
- Views have explicit lifecycle: `on_ready()` and `on_cleanup()`
- Resources are acquired in `on_ready()` and released in `on_cleanup()`
- Discovery loop runs only while view is active
- No resource leaks or dangling timers

### 2. Event Framework Integration
- All operations logged through event framework
- Session history maintained for debugging
- Status updates flow through StatusStack
- Events are YAML-formatted for consistency

### 3. Two-Table Architecture
- **Registered Devices**: Paired/connected devices (registration complete)
- **Discovering Devices**: Unpaired/discoverable devices (registration entry point)
- Clear separation of concerns
- Different operations per table (Connect vs Pair)

### 4. Force Grab Feature
- Disconnect device from all other connections
- Connect to desktop
- No confirmation dialogs
- Status feedback through StatusStack

## Implementation Details

### ViewBase Lifecycle

```python
class ViewBase(ABC):
    def __init__(self, parent_app, view_name):
        self.app = parent_app
        self.view_name = view_name
        self.is_active = False
        self.session_logger = getattr(parent_app, 'session_logger', None)
    
    @abstractmethod
    def create_content(self):
        """Create view UI"""
        pass
    
    def on_ready(self):
        """Called when view is displayed"""
        self.is_active = True
        self._log_event("VIEW_READY", f"View {self.view_name} is now active")
    
    def on_cleanup(self):
        """Called when view is closed"""
        self.is_active = False
        self._log_event("VIEW_CLEANUP", f"View {self.view_name} cleaned up")
```

### BluetoothWorkspace Discovery Loop

```python
def on_ready(self):
    self.is_active = True
    self._log_event("WORKSPACE_READY", "Bluetooth workspace is now active")
    self._start_discovery_loop()

def _start_discovery_loop(self):
    if self.discovery_timeout_id:
        GLib.source_remove(self.discovery_timeout_id)
    
    self.discovery_active = True
    self._log_event("DISCOVERY_STARTED", "Continuous discovery loop started")
    
    # Start immediately, then repeat every 3 seconds
    self._perform_discovery()
    self.discovery_timeout_id = GLib.timeout_add_seconds(3, self._perform_discovery)

def _perform_discovery(self) -> bool:
    if not self.is_active:
        return False
    
    try:
        monitor = BluetoothMonitor()
        self.registered_devices = monitor.get_devices(include_unpaired=False)
        self.discovering_devices = monitor.get_devices(include_unpaired=True)
        
        # Update UI
        self._update_status_labels()
        self._log_event("DISCOVERY_CYCLE", 
            f"Registered: {len(self.registered_devices)}, Discovering: {len(self.discovering_devices)}")
    except Exception as e:
        logger.error(f"Discovery cycle failed: {e}")
        self._log_event("DISCOVERY_ERROR", str(e))
    
    return True  # Continue loop

def on_cleanup(self):
    self.is_active = False
    self._log_event("WORKSPACE_CLEANUP", "Bluetooth workspace cleaned up")
    self._stop_discovery_loop()

def _stop_discovery_loop(self):
    if self.discovery_timeout_id:
        GLib.source_remove(self.discovery_timeout_id)
        self.discovery_timeout_id = None
    
    self.discovery_active = False
    self._log_event("DISCOVERY_STOPPED", "Continuous discovery loop stopped")
```

### Force Grab Implementation

```python
def force_grab_device(self, device_address: str, device_name: str) -> bool:
    try:
        self._log_event("FORCE_GRAB_STARTED", 
            f"Force grabbing {device_name} ({device_address})")
        
        monitor = BluetoothMonitor()
        
        # Get all connected devices
        all_devices = monitor.get_devices(include_unpaired=False)
        
        # Disconnect from all other devices
        for device in all_devices:
            if device.address != device_address and device.connected:
                logger.info(f"Disconnecting {device.name} to free up {device_name}")
                monitor.disconnect_device(device.address)
        
        # Connect to desktop
        success = monitor.connect_device(device_address)
        
        if success:
            self._log_event("FORCE_GRAB_SUCCESS", 
                f"Successfully connected to {device_name}")
        else:
            self._log_event("FORCE_GRAB_FAILED", 
                f"Failed to connect to {device_name}")
        
        return success
    except Exception as e:
        logger.error(f"Force grab error: {e}")
        self._log_event("FORCE_GRAB_ERROR", str(e))
        return False
```

### StatusStack Integration

```python
class StatusStack:
    def __init__(self, max_messages: int = 5):
        self.max_messages = max(3, min(5, max_messages))
        self.messages = deque(maxlen=self.max_messages)
        self.session_history = []
    
    def push_status(self, message: str, status_type: str = "info"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.messages.append((timestamp, status_type, message))
        self.session_history.append((timestamp, status_type, message))
        self._update_display()
    
    def _create_message_widget(self, timestamp, status_type, message):
        message_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        message_row.add_css_class(f"status-{status_type}")
        
        # Add timestamp, type, and message labels
        # ...
        
        return message_row
```

## Event Logging Pattern

All operations follow this pattern:

```python
def operation(self):
    try:
        self._log_event("OPERATION_STARTED", "Starting operation...")
        
        # Perform operation
        result = do_something()
        
        if result:
            self._log_event("OPERATION_SUCCESS", "Operation completed")
        else:
            self._log_event("OPERATION_FAILED", "Operation did not complete")
        
        return result
    except Exception as e:
        logger.error(f"Operation error: {e}")
        self._log_event("OPERATION_ERROR", str(e))
        return False
```

## Testing Strategy

### Unit Tests
- Test lifecycle hooks (on_ready, on_cleanup)
- Test discovery loop starts/stops
- Test force grab logic
- Test event logging

### Integration Tests
- Test with real Bluetooth devices
- Test discovery finds devices
- Test force grab connects device
- Test status updates display

### Manual Testing
1. Open Bluetooth workspace
2. Verify discovery starts automatically
3. Verify devices appear in tables
4. Click Force Grab
5. Verify status updates
6. Close workspace
7. Verify discovery stops

## Performance Considerations

- Discovery runs every 3 seconds (configurable)
- Status stack limited to 5 messages (configurable)
- Session history maintained in memory
- GLib timeout used for non-blocking discovery

## Security Considerations

- Force Grab requires device to be paired
- No confirmation dialog (user responsibility)
- All operations logged for audit trail
- Session logs stored in `/build/tmp/`

## Future Enhancements

1. Configurable discovery interval
2. Device filtering by type/signal strength
3. Connection profiles
4. Auto-connect on boot
5. Bluetooth device registry
6. Advanced status reporting

