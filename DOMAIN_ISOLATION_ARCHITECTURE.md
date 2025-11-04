# Domain Isolation Architecture - Bluetooth, Output, and Input Tabs

## Overview

This document defines clear domain boundaries and responsibilities for the three audio-related tabs in the Unhinged platform to eliminate duplication and improve UI clarity.

## Domain Boundaries

### 🔵 BLUETOOTH TAB - Device Discovery & Connection Management
**Responsibility**: Manage Bluetooth device lifecycle (discovery, pairing, connection)

**Owns**:
- Device discovery and scanning
- Device pairing and unpairing
- Device connection and disconnection
- Device trust settings (for auto-connect)
- Device filtering and search
- Device type classification
- Connection status display
- Signal strength (RSSI) monitoring
- Device properties and metadata

**Does NOT own**:
- Audio routing decisions
- Volume control
- Audio device enumeration
- Input device selection

**Key Components**:
- `BluetoothView` (views/bluetooth_view.py)
- `BluetoothTable` (components/complex.py)
- `BluetoothRow` (components/primitives.py)
- `BluetoothMonitor` (bluetooth_monitor.py)

**User Actions**:
1. Scan for devices
2. Pair with new device
3. Connect to paired device
4. Disconnect from device
5. Unpair device
6. View device details

---

### 🔊 OUTPUT TAB - Audio Output Device Selection & Volume Control
**Responsibility**: Manage audio output devices and volume settings

**Owns**:
- Audio output device enumeration
- Default audio device selection
- Volume control (master and per-device)
- Mute/unmute functionality
- Audio device filtering
- Connection type display (ALSA, PulseAudio, etc.)
- Device status (active, inactive)

**Does NOT own**:
- Bluetooth device discovery
- Bluetooth pairing
- Bluetooth connection management
- Input device selection

**Key Components**:
- `OutputView` (views/output_view.py)
- `AudioTable` (components/complex.py)
- `AudioDeviceRow` (components/primitives.py)
- `AudioMonitor` (handlers/audio_monitor.py)

**User Actions**:
1. View available audio output devices
2. Select default audio device
3. Adjust master volume
4. Adjust per-device volume
5. Mute/unmute devices
6. Filter devices by type

**Important**: When a Bluetooth device is connected via the Bluetooth tab, it automatically appears in the Output tab as an available audio device. Users select it here for audio routing.

---

### 🎤 INPUT TAB - Audio Input Device Selection
**Responsibility**: Manage audio input devices and selection

**Owns**:
- Audio input device enumeration
- Default input device selection
- Input device filtering
- Device status display
- ALSA configuration for input devices

**Does NOT own**:
- Bluetooth device discovery
- Bluetooth pairing
- Bluetooth connection management
- Output device selection

**Key Components**:
- `InputView` (views/input_view.py)

**User Actions**:
1. View available audio input devices
2. Select default input device
3. Filter devices by type
4. Refresh device list

---

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    BLUETOOTH TAB                            │
│  (Device Discovery, Pairing, Connection Management)         │
│                                                              │
│  User: Scan → Pair → Connect → Device Connected            │
│                                                              │
│  BluetoothMonitor → BlueZ D-Bus → Linux Bluetooth Stack    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ Device Connected Event
                       │ (Bluetooth device now available)
                       ↓
┌─────────────────────────────────────────────────────────────┐
│                    OUTPUT TAB                               │
│  (Audio Output Device Selection & Volume Control)           │
│                                                              │
│  AudioMonitor → ALSA/PulseAudio → Audio Devices            │
│                                                              │
│  User: Select Device → Adjust Volume → Audio Routes        │
└─────────────────────────────────────────────────────────────┘
                       ↑
                       │
                       │ Bluetooth device appears as
                       │ audio output option
                       │
┌─────────────────────────────────────────────────────────────┐
│                    INPUT TAB                                │
│  (Audio Input Device Selection)                             │
│                                                              │
│  AudioMonitor → ALSA/PulseAudio → Input Devices            │
│                                                              │
│  User: Select Device → Audio Input Routes                  │
└─────────────────────────────────────────────────────────────┘
```

## Interaction Rules

### ✅ ALLOWED Interactions

1. **Bluetooth → Output**: When a Bluetooth device connects, it becomes available in Output tab
2. **Output → Bluetooth**: Output tab can display which Bluetooth device is currently selected
3. **Input → Output**: Independent selection (no direct interaction)
4. **Cross-tab Status**: Each tab can display status from other domains (read-only)

### ❌ FORBIDDEN Interactions

1. **Output → Bluetooth Connection**: Output tab CANNOT initiate Bluetooth connections
2. **Input → Bluetooth Connection**: Input tab CANNOT initiate Bluetooth connections
3. **Bluetooth → Volume Control**: Bluetooth tab CANNOT control audio volume
4. **Duplication**: No Bluetooth controls in Output or Input tabs
5. **Duplication**: No Audio controls in Bluetooth tab

## Implementation Guidelines

### For Bluetooth Tab
- Focus on device discovery and connection state
- Display connection status clearly
- Show signal strength and device type
- Provide pairing/unpairing controls
- Do NOT include audio routing or volume controls

### For Output Tab
- Focus on audio device selection and volume
- Display all available audio devices (including connected Bluetooth)
- Provide volume controls
- Show device connection type
- Do NOT include Bluetooth pairing or connection controls

### For Input Tab
- Focus on input device selection
- Display all available input devices
- Provide device selection controls
- Do NOT include Bluetooth or output controls

## Benefits of This Architecture

1. **Clear Responsibility**: Each tab has a single, well-defined purpose
2. **No Duplication**: Functionality exists in exactly one place
3. **Better UX**: Users know where to find each feature
4. **Easier Maintenance**: Changes to one domain don't affect others
5. **Scalability**: Easy to add new features without breaking existing ones
6. **Testability**: Each domain can be tested independently

## Migration Path

### Phase 1: Deduplication (COMPLETE)
- ✅ Remove Bluetooth selector from Output tab
- ✅ Remove "Pull from Phone" button from AudioTable
- ✅ Remove Bluetooth connection methods from Output tab

### Phase 2: Clarification (IN PROGRESS)
- [ ] Update UI labels to reflect domain boundaries
- [ ] Add help text explaining each tab's purpose
- [ ] Ensure consistent terminology across tabs

### Phase 3: Enhancement (FUTURE)
- [ ] Add cross-tab status indicators
- [ ] Implement device connection notifications
- [ ] Add quick-access shortcuts between related tabs

## Testing Domain Isolation

### Bluetooth Tab Tests
- [ ] Device discovery works
- [ ] Pairing succeeds
- [ ] Connection succeeds
- [ ] No audio controls visible
- [ ] No input device controls visible

### Output Tab Tests
- [ ] Audio devices display correctly
- [ ] Bluetooth devices appear after connection
- [ ] Volume controls work
- [ ] No Bluetooth pairing controls visible
- [ ] No input device controls visible

### Input Tab Tests
- [ ] Input devices display correctly
- [ ] Device selection works
- [ ] No Bluetooth controls visible
- [ ] No output device controls visible

## Future Enhancements

1. **Status Indicators**: Show Bluetooth connection status in Output tab (read-only)
2. **Quick Actions**: "Go to Bluetooth tab" link when no devices connected
3. **Notifications**: Alert user when Bluetooth device connects/disconnects
4. **Profiles**: Save audio routing profiles (e.g., "Headphones", "Speakers")
5. **Automation**: Auto-switch audio output when Bluetooth device connects

## Conclusion

This domain isolation architecture provides clear boundaries, eliminates duplication, and creates a more intuitive user experience. Each tab has a single responsibility and interacts with others only through well-defined interfaces.

