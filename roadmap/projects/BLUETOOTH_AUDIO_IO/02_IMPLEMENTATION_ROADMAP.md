# Bluetooth & Audio IO - Implementation Roadmap

## REVISED: Hardware Availability is the Blocker

**Finding**: This system has no Bluetooth hardware. The D-Bus "timeout" is expected behavior when querying for non-existent hardware.

**Decision**: Cannot test Bluetooth code without hardware. Two paths forward:

---

## Path A: Add Bluetooth Hardware (Recommended for Real Testing)

### Option 1: USB Bluetooth Adapter
- Cost: $15-30
- Setup: Plug in, drivers load automatically
- Benefit: Real hardware testing

### Option 2: Logitech Pro X2 Bluetooth Mode
- Current: Using LIGHTSPEED (USB receiver)
- Alternative: Switch to Bluetooth mode
- Benefit: Test with actual target hardware

---

## Path B: Mock Bluetooth for Testing (No Hardware)

### Phase 1: Create Mock D-Bus Objects

**Goal**: Simulate Bluetooth hardware for testing

**Tasks**:
1. Create mock BlueZ D-Bus service
2. Simulate adapter and device objects
3. Implement mock connection/pairing operations
4. Create test fixtures for UI testing

**Success Criteria**:
- Can test Bluetooth UI without hardware
- Mock responds to D-Bus queries
- Device discovery works in tests

**Estimated Effort**: 2-3 days

### Phase 2: Test Bluetooth Code Against Mock

**Goal**: Verify Bluetooth code works correctly

**Tasks**:
1. Write unit tests using mock D-Bus
2. Test device discovery
3. Test pairing and connection
4. Test error handling

**Success Criteria**:
- 80%+ test coverage
- All operations work against mock
- Error cases handled

**Estimated Effort**: 2-3 days

---

## Path C: Focus on Audio (What Actually Works)

### Phase 1: Improve Audio Device Management

**Goal**: Enhance audio subsystem (which is working)

**Tasks**:
1. Add PipeWire support alongside ALSA
2. Implement device hotplug detection
3. Add per-device volume control
4. Improve default device selection

**Success Criteria**:
- Works on both ALSA and PipeWire systems
- Detects device connect/disconnect
- Smooth audio device switching

**Estimated Effort**: 3-4 days

### Phase 2: Prepare for Bluetooth Integration

**Goal**: Build infrastructure for future Bluetooth support

**Tasks**:
1. Design AudioRouter component (ready for Bluetooth)
2. Create event bus for device state changes
3. Implement state machine pattern
4. Add error handling and logging

**Success Criteria**:
- Architecture ready for Bluetooth
- Can add Bluetooth routing without refactoring
- Well-tested and documented

**Estimated Effort**: 2-3 days

---

## Recommendation

**Do Path B (Mock Bluetooth) + Path C (Improve Audio)**:

1. **Week 1**: Create mock D-Bus for Bluetooth testing
2. **Week 2**: Test Bluetooth code against mock
3. **Week 3**: Improve audio device management
4. **Week 4**: Prepare infrastructure for Bluetooth integration

**When Bluetooth hardware becomes available**:
- Swap mock for real hardware
- Bluetooth code already tested and working
- Integration layer ready to connect

---

## Phase 2: Implement State Machine (🟡 High)

### Goal
Replace polling with event-driven state management

### Tasks
1. Define BluetoothDeviceState enum (UNKNOWN → DISCOVERED → PAIRED → CONNECTED)
2. Implement BluetoothDeviceStateMachine class
3. Replace 3-second polling with event-driven updates
4. Add state transition validation

### Success Criteria
- Device state changes trigger UI updates
- No polling loop
- State transitions validated

### Estimated Effort
- 2-3 days

---

## Phase 3: Bluetooth-Audio Integration (🟡 High)

### Goal
Automatic audio routing when Bluetooth device connects

### Tasks
1. Create AudioRouter component
2. Detect Bluetooth audio profiles (A2DP, HFP/HSP)
3. Automatically set audio output when device connects
4. Handle disconnection gracefully

### Success Criteria
- Bluetooth device connects → audio automatically routes
- User doesn't need to manually select output
- Works with Logitech Pro X2

### Estimated Effort
- 3-4 days

---

## Phase 4: PipeWire Support (🟡 High)

### Goal
Support modern Linux systems using PipeWire

### Tasks
1. Add PipeWire device enumeration (wpctl)
2. Detect PipeWire vs ALSA at runtime
3. Support both backends simultaneously
4. Test on PipeWire-based systems

### Success Criteria
- Works on both ALSA and PipeWire systems
- Automatic backend detection
- No user configuration needed

### Estimated Effort
- 2-3 days

---

## Phase 5: Error Recovery & Testing (🟠 Medium)

### Goal
Robust error handling and test coverage

### Tasks
1. Implement error recovery with retry logic
2. Add specific exception types (DBusTimeout, DeviceNotFound, etc.)
3. Write unit tests for Bluetooth operations
4. Write integration tests for audio routing
5. Mock D-Bus for testing

### Success Criteria
- Silent failures eliminated
- User sees meaningful error messages
- 80%+ test coverage for critical paths

### Estimated Effort
- 3-4 days

---

## Implementation Order

1. **Phase 1** (Critical) - Fix D-Bus blocking
2. **Phase 2** (High) - State machine
3. **Phase 3** (High) - Bluetooth-Audio integration
4. **Phase 4** (High) - PipeWire support
5. **Phase 5** (Medium) - Error recovery & testing

---

## Expert Review Questions

Before implementation, need expert guidance on:

1. **Async Pattern**: GLib async vs asyncio vs dbus-python async?
2. **State Machine**: Recommended pattern for device lifecycle?
3. **Audio Routing**: How to detect and route Bluetooth audio profiles?
4. **PipeWire**: Migration strategy for ALSA → PipeWire?
5. **Testing**: Best practices for mocking D-Bus?

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|-----------|
| D-Bus API changes | Low | Use stable BlueZ API |
| PipeWire adoption | Medium | Support both ALSA and PipeWire |
| Audio profile detection | Medium | Test with multiple devices |
| Async complexity | Medium | Use proven patterns (GLib) |
| Testing D-Bus | Medium | Use dbus-python mock |

---

## Success Metrics

- ✅ No UI freezes during Bluetooth operations
- ✅ Automatic audio routing on device connection
- ✅ Works on ALSA and PipeWire systems
- ✅ 80%+ test coverage
- ✅ Logitech Pro X2 works seamlessly

---

## Timeline

- **Phase 1**: Week 1
- **Phase 2**: Week 1-2
- **Phase 3**: Week 2-3
- **Phase 4**: Week 3
- **Phase 5**: Week 3-4

**Total**: ~4 weeks (with expert guidance)

