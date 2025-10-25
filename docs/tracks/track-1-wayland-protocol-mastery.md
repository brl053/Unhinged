# 🎯 Track 1: Wayland Protocol Deep Dive - First Principles Mastery

> **Purpose**: Master Wayland protocol fundamentals before any implementation decisions
> **Timeline**: 3 weeks intensive study + hands-on implementation
> **Success Criteria**: Can implement basic Wayland client using raw protocol calls

## 🔥 Why Track 1 First

**Everything cascades from understanding the Wayland protocol at first principles.**

- GPU integration decisions depend on understanding EGL surface creation
- Performance optimization requires knowing message serialization overhead
- Input handling architecture flows from wl_seat protocol mechanics
- Memory management strategy depends on buffer lifecycle understanding

**No shortcuts. Master the protocol first.**

## 📚 Phase 1: Protocol Specification Study (2-3 hours)

### Required Reading Sequence

**Read these documents in EXACT order:**

1. **Wayland Protocol Specification**: https://wayland.freedesktop.org/docs/html/
   - Focus: Request/event model, object lifecycle, protocol state machine
   - Time: 45 minutes deep reading

2. **Architecture Overview**: https://wayland.freedesktop.org/architecture.html
   - Focus: Client/compositor relationship, shared memory model
   - Time: 30 minutes

3. **Protocol Interface Reference**: https://wayland.freedesktop.org/docs/html/apa.html
   - Focus: Core interfaces and their relationships
   - Time: 60 minutes

### Critical Interfaces to Master

**Core Connection Management:**
- `wl_display` - Connection lifecycle, event loop integration
- `wl_registry` - Service discovery, global object enumeration
- `wl_callback` - Synchronization and frame timing

**Surface Management:**
- `wl_compositor` - Surface factory and management
- `wl_surface` - Individual drawable surface lifecycle
- `wl_subsurface` - Hierarchical surface relationships

**Buffer Management:**
- `wl_shm` - Shared memory buffer allocation
- `wl_shm_pool` - Memory pool management
- `wl_buffer` - Individual buffer lifecycle

**Input Handling:**
- `wl_seat` - Input device abstraction
- `wl_pointer` - Mouse/touchpad events
- `wl_keyboard` - Keyboard events and keymap handling
- `wl_touch` - Touch screen events

### Study Methodology

**For each interface:**
1. Read the XML specification
2. Understand the request/event pairs
3. Trace the object lifecycle
4. Identify state dependencies
5. Document the protocol flow

**Example study notes for wl_surface:**
```
wl_surface Protocol Flow:
1. wl_compositor.create_surface() → new wl_surface object
2. wl_surface.attach(buffer) → attach pixel data
3. wl_surface.damage(x, y, w, h) → mark dirty regions
4. wl_surface.commit() → make changes visible
5. wl_surface.frame() → request frame callback
6. wl_callback.done → frame rendered, ready for next
```

## 🔍 Phase 2: Live Protocol Tracing (1-2 hours hands-on)

### Protocol Debugging Setup

**Enable comprehensive protocol logging:**
```bash
# Set debug environment
export WAYLAND_DEBUG=1

# Optional: Filter specific interfaces
export WAYLAND_DEBUG=client  # or server, or specific interface names
```

### Tracing Exercises

**Exercise 1: Connection Handshake Analysis**
```bash
# Trace compositor info tool
WAYLAND_DEBUG=1 weston-info 2>&1 | head -50

# Expected output analysis:
# - wl_display.get_registry request
# - wl_registry.global events for each available interface
# - wl_registry.bind requests for needed interfaces
```

**Exercise 2: Simple Application Tracing**
```bash
# Trace a minimal GTK4 application
WAYLAND_DEBUG=1 gtk4-demo 2>&1 | tee gtk_trace.log

# Analysis tasks:
# 1. Count wl_surface.commit calls per frame
# 2. Identify buffer allocation patterns
# 3. Trace input event flow
# 4. Document object creation sequence
```

**Exercise 3: Comparative Protocol Analysis**
```bash
# Compare different application patterns
WAYLAND_DEBUG=1 gnome-calculator 2>&1 > calc_trace.log
WAYLAND_DEBUG=1 firefox 2>&1 > firefox_trace.log

# Analysis: How do different applications use the protocol differently?
```

### Protocol Message Analysis

**Understand message structure:**
```
[timestamp] wl_surface@23.attach(wl_buffer@45, 0, 0)
            ^interface ^object_id ^method ^arguments

[timestamp] wl_surface@23.damage(0, 0, 800, 600)
[timestamp] wl_surface@23.commit()
```

**Key patterns to identify:**
- Object creation sequences
- Buffer lifecycle management
- Frame synchronization patterns
- Input event handling
- Error conditions and recovery

## 🦀 Phase 3: Rust Binding Architecture Analysis (2-3 hours)

### wayland-rs Deep Dive

**Repository study**: https://github.com/smithay/wayland-rs

**Focus areas:**
```
wayland-client/src/
├── lib.rs              # Main client API
├── globals.rs          # GlobalManager implementation
├── event_queue.rs      # Event loop and dispatching
└── protocol/           # Auto-generated bindings

wayland-protocols/
├── protocols/          # XML protocol definitions
└── src/                # Generated Rust code
```

### Code Generation Understanding

**XML to Rust mapping:**
```xml
<!-- wayland.xml -->
<interface name="wl_surface" version="4">
  <request name="attach">
    <arg name="buffer" type="object" interface="wl_buffer" allow-null="true"/>
    <arg name="x" type="int"/>
    <arg name="y" type="int"/>
  </request>
</interface>
```

**Generated Rust code:**
```rust
impl WlSurface {
    pub fn attach(&self, buffer: Option<&WlBuffer>, x: i32, y: i32) {
        // Marshals arguments and sends request
    }
}
```

### High-Level vs Low-Level API

**High-level convenience:**
```rust
let compositor = globals.instantiate_exact::<WlCompositor>(4)?;
let surface = compositor.create_surface();
```

**Underlying protocol mechanics:**
```rust
// What actually happens:
// 1. wl_registry.bind("wl_compositor", 4) → object_id
// 2. wl_compositor@object_id.create_surface() → surface_id
// 3. Store surface_id for future requests
```

## ⚡ Phase 4: Raw Protocol Implementation (3-4 hours)

### Minimal Client Without Abstractions

**Goal**: Implement basic Wayland client using only raw protocol calls.

**Implementation requirements:**
```rust
// No high-level APIs allowed
// ❌ let compositor = globals.instantiate_exact::<WlCompositor>(4)?;
// ✅ Manual protocol implementation

struct RawWaylandClient {
    socket: UnixStream,
    object_map: HashMap<u32, ObjectType>,
    next_object_id: u32,
}

impl RawWaylandClient {
    fn send_request(&mut self, object_id: u32, opcode: u16, args: &[Argument]) {
        // Manual message serialization
        let message = self.serialize_message(object_id, opcode, args);
        self.socket.write_all(&message).unwrap();
    }
    
    fn receive_event(&mut self) -> Event {
        // Manual message deserialization
        let header = self.read_message_header();
        let args = self.read_message_args(header.size - 8);
        self.deserialize_event(header.object_id, header.opcode, args)
    }
}
```

### Wire Protocol Format

**Message structure:**
```
Header (8 bytes):
├── object_id (4 bytes) - Target object
├── size_and_opcode (4 bytes) - Message size (high 16) + opcode (low 16)

Arguments (variable):
├── Each argument type has specific encoding
├── Strings are null-terminated with padding
├── Arrays have length prefix
└── Object IDs are 4-byte integers
```

**Implementation tasks:**
1. **Message Serialization** - Convert Rust types to wire format
2. **Message Deserialization** - Parse wire format to Rust types
3. **Object ID Management** - Track object lifecycle manually
4. **Event Loop** - Handle asynchronous events from compositor
5. **Error Handling** - Process protocol errors and disconnections

### Raw Implementation Milestones

**Milestone 1: Connection Establishment**
```rust
// Connect to compositor
let socket = connect_to_wayland_socket();

// Send wl_display.get_registry(callback_id)
send_get_registry_request(&socket, callback_id);

// Receive wl_registry.global events
let globals = receive_global_events(&socket);
```

**Milestone 2: Surface Creation**
```rust
// Bind to wl_compositor
let compositor_id = bind_global(&socket, "wl_compositor", 4);

// Create surface
let surface_id = create_surface(&socket, compositor_id);
```

**Milestone 3: Buffer Management**
```rust
// Create shared memory pool
let shm_id = bind_global(&socket, "wl_shm", 1);
let pool_id = create_shm_pool(&socket, shm_id, fd, size);

// Create buffer from pool
let buffer_id = create_buffer(&socket, pool_id, offset, width, height, stride, format);

// Attach buffer to surface
attach_buffer(&socket, surface_id, buffer_id, 0, 0);
```

## 🚀 Phase 5: Incremental Feature Development (1 week)

### Feature Implementation Order

**Week 1 Daily Goals:**

**Day 1: Surface Creation**
- Implement surface allocation and basic properties
- Understand surface states (pending, current, committed)
- Test surface creation/destruction lifecycle

**Day 2: Buffer Management**
- Implement shared memory buffer allocation
- Understand buffer formats and stride calculations
- Test buffer attach/commit cycles

**Day 3: Input Event Handling**
- Process keyboard, mouse, and touch events
- Implement event filtering and dispatch
- Test input event ordering and timing

**Day 4: Damage Tracking**
- Implement efficient region invalidation
- Understand partial vs full surface updates
- Test damage accumulation and optimization

**Day 5: Multi-Surface Management**
- Handle surface z-ordering and relationships
- Implement subsurface hierarchies
- Test complex surface arrangements

### Implementation Validation

**For each feature:**
1. **Raw Protocol First** - Implement using manual message handling
2. **High-Level Comparison** - Compare with wayland-client API
3. **Protocol Documentation** - Document message sequences
4. **Multi-Compositor Testing** - Test on GNOME Shell, KDE Plasma, Sway
5. **Performance Analysis** - Measure message overhead and latency

### Success Validation

**Protocol Mastery Checklist:**
- [ ] Can implement basic Wayland client without high-level libraries
- [ ] Understands message serialization format and overhead
- [ ] Can debug protocol issues using WAYLAND_DEBUG output
- [ ] Knows object lifecycle and state management requirements
- [ ] Understands compositor differences and compatibility issues

## 🎯 Track 1 Completion Criteria

### Technical Mastery
- **Wire Protocol Understanding** - Can read/write raw Wayland messages
- **Object Lifecycle Management** - Understands creation, binding, destruction
- **Event Loop Integration** - Can handle asynchronous compositor events
- **Buffer Management** - Knows shared memory allocation and attachment
- **Input Event Processing** - Can handle keyboard, mouse, touch events

### Practical Skills
- **Protocol Debugging** - Can diagnose issues using protocol traces
- **Performance Analysis** - Understands message overhead and optimization
- **Compositor Compatibility** - Knows differences between implementations
- **Error Handling** - Can recover from protocol errors gracefully

### Implementation Readiness
- **GPU Integration Decisions** - Ready to evaluate EGL surface creation
- **Performance Optimization** - Understands protocol bottlenecks
- **Architecture Choices** - Can make informed rendering pipeline decisions

**Upon Track 1 completion, proceed to Track 2 decision point with full understanding of Wayland protocol constraints and opportunities.**
