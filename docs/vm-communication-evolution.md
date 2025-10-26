# VM Communication Evolution Design

**@llm-doc VM Communication System Evolution**  
**@llm-version 2.0.0**  
**@llm-date 2025-01-26**  
**@llm-author Unhinged Team**

## Overview

Design for evolving the VM communication system from unidirectional (Phase 1) to bidirectional (Phase 2) while preserving the Makefile as the core build system.

## Current State (Phase 1) ✅

### Unidirectional Communication: VM → Host
- **Channel**: Serial console output via QEMU `-serial stdio`
- **Flow**: VM console output → Host terminal running `make start`
- **Implementation**: `control/simple_vm_launcher.py`
- **Reliability**: ✅ Tested and working
- **Visibility**: ✅ VM output appears in host terminal immediately

### Integration Points
- **Makefile**: `make start` → `make start-simple` → `SIMPLE_VM_COMMUNICATION`
- **Build System**: Preserved as core system
- **Quality of Life**: `make start` provides zero-friction launch

## Phase 2 Design: Bidirectional Communication

### Architecture Principles

1. **Makefile Preservation**: Makefile remains the core build system
2. **QoL Evolution**: `make start` evolves to handle bidirectional communication
3. **Behind-the-Scenes**: New launcher calls Makefile targets internally
4. **Incremental**: Build on Phase 1 foundation

### Communication Channels

#### Primary Channel: Enhanced Serial Console
```
Host ←→ VM via QEMU Monitor + Serial Console
- VM → Host: Serial console output (existing)
- Host → VM: QEMU monitor commands
- Protocol: Text-based with structured messages
```

#### Secondary Channel: Shared Directory (Optional)
```
Host ←→ VM via 9p filesystem
- VM → Host: Status files, logs
- Host → VM: Command files, configuration
- Protocol: File-based JSON messages
```

### Implementation Strategy

#### Phase 2A: Enhanced Launcher
Create `control/enhanced_vm_launcher.py` that:
1. Extends `simple_vm_launcher.py`
2. Adds QEMU monitor interface for Host → VM
3. Maintains serial console for VM → Host
4. Provides bidirectional message protocol

#### Phase 2B: QoL Interface Evolution
Create `control/unhinged_launcher.py` that:
1. Replaces direct Makefile calls in `make start`
2. Calls Makefile targets "behind the scenes"
3. Provides enhanced user experience
4. Handles real-time bidirectional communication

### Detailed Design

#### Enhanced VM Launcher

```python
class EnhancedVMLauncher(SimpleVMLauncher):
    """
    Bidirectional VM communication launcher
    Extends simple launcher with Host → VM capabilities
    """
    
    def __init__(self):
        super().__init__()
        self.monitor_socket = None
        self.command_queue = []
        
    def launch_vm_with_bidirectional_communication(self):
        """Launch VM with both directions of communication"""
        # QEMU with monitor socket for Host → VM
        cmd = [
            'qemu-system-x86_64',
            '-enable-kvm',
            '-m', '1G', '-smp', '2',
            '-drive', f'file={disk_path},format=qcow2',
            '-cdrom', iso_path,
            '-serial', 'stdio',  # VM → Host (existing)
            '-monitor', 'unix:/tmp/qemu-monitor.sock,server,nowait',  # Host → VM
            '-display', 'none'
        ]
        
    def send_to_vm(self, command):
        """Send command to VM via QEMU monitor"""
        # Implementation for Host → VM communication
        
    def process_vm_output(self, line):
        """Process VM output with bidirectional protocol"""
        # Enhanced processing for structured messages
```

#### QoL Interface (Unhinged Launcher)

```python
class UnhingedLauncher:
    """
    Quality-of-life launcher that calls Makefile behind the scenes
    Provides enhanced user experience while preserving build system
    """
    
    def __init__(self):
        self.makefile_path = Path("Makefile")
        self.vm_launcher = EnhancedVMLauncher()
        
    def start(self):
        """Enhanced start that calls Makefile targets internally"""
        # 1. Call Makefile setup targets
        self.call_makefile("setup-python")
        self.call_makefile("deps-install-essential")
        
        # 2. Launch VM with bidirectional communication
        self.vm_launcher.launch_vm_with_bidirectional_communication()
        
        # 3. Handle real-time communication
        self.handle_bidirectional_communication()
        
    def call_makefile(self, target):
        """Call Makefile target behind the scenes"""
        subprocess.run(['make', target], cwd=self.project_root)
```

### Makefile Evolution

#### Current Integration
```makefile
# Phase 1: Simple unidirectional
SIMPLE_VM_COMMUNICATION := python3 control/simple_vm_launcher.py

start: ## Current implementation
    @$(SIMPLE_VM_COMMUNICATION)
```

#### Phase 2 Integration
```makefile
# Phase 2: Enhanced bidirectional
ENHANCED_VM_COMMUNICATION := python3 control/enhanced_vm_launcher.py
UNHINGED_LAUNCHER := python3 control/unhinged_launcher.py

start: ## Enhanced start with bidirectional communication
    @$(UNHINGED_LAUNCHER)

start-enhanced: ## Direct enhanced VM launcher
    @$(ENHANCED_VM_COMMUNICATION)

start-simple: ## Keep simple launcher for testing
    @$(SIMPLE_VM_COMMUNICATION)
```

### Communication Protocol

#### Message Format
```json
{
    "timestamp": "2025-01-26T10:30:00Z",
    "direction": "vm-to-host" | "host-to-vm",
    "type": "status" | "command" | "graphics" | "error",
    "data": {
        "message": "string",
        "details": {}
    }
}
```

#### VM → Host Messages
- **Status**: System status, boot progress, service states
- **Graphics**: Rendering events, display updates
- **Error**: Error conditions, failures
- **Heartbeat**: Periodic alive signals

#### Host → VM Commands
- **Control**: Start/stop services, configuration changes
- **Graphics**: Display commands, window management
- **System**: Shutdown, restart, diagnostics

### Implementation Plan

#### Step 1: Enhanced VM Launcher
1. Create `control/enhanced_vm_launcher.py`
2. Add QEMU monitor socket support
3. Implement Host → VM command interface
4. Test bidirectional communication

#### Step 2: QoL Interface
1. Create `control/unhinged_launcher.py`
2. Implement Makefile integration
3. Add enhanced user experience features
4. Test end-to-end workflow

#### Step 3: Makefile Integration
1. Update Makefile with new targets
2. Preserve existing functionality
3. Add backward compatibility
4. Update documentation

#### Step 4: Testing & Validation
1. Test all communication directions
2. Verify Makefile preservation
3. Validate user experience
4. Performance testing

### Backward Compatibility

- **Phase 1**: `make start-simple` always available
- **Makefile**: All existing targets preserved
- **Build System**: No changes to core build functionality
- **Migration**: Gradual adoption, no breaking changes

### Success Criteria

1. ✅ **Bidirectional Communication**: Host ↔ VM working reliably
2. ✅ **Makefile Preservation**: Core build system unchanged
3. ✅ **Enhanced UX**: `make start` provides better experience
4. ✅ **Real-time**: Immediate communication in both directions
5. ✅ **Reliability**: Robust error handling and recovery

## Next Steps

1. **Implement Enhanced VM Launcher** (Phase 2A)
2. **Create QoL Interface** (Phase 2B)
3. **Update Makefile Integration**
4. **Test & Validate**
5. **Document & Deploy**

---

**@llm-principle** Evolution preserves foundation while adding capabilities  
**@llm-culture** Independence through enhanced but simple communication  
**@llm-next-phase** Implement enhanced VM launcher with bidirectional support
