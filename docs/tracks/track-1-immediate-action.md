# ⚡ Track 1 Immediate Action - Protocol Debugging Session

> **Execute this debugging session RIGHT NOW to start Track 1**
> **Time Required**: 30 minutes
> **Goal**: Understand your current Wayland implementation at the protocol level

## 🔍 Immediate Debugging Session

### Step 1: Enable Protocol Tracing

```bash
# Navigate to your Wayland hello-world project
cd /path/to/unhinged_wayland_hello

# Enable comprehensive protocol logging
export WAYLAND_DEBUG=1

# Optional: Enable client-side only (reduces noise)
export WAYLAND_DEBUG=client
```

### Step 2: Capture Protocol Trace

```bash
# Run your current implementation with full tracing
./target/release/unhinged_wayland_hello 2>&1 | tee wayland_trace.log

# If not built yet:
cargo build --release
./target/release/unhinged_wayland_hello 2>&1 | tee wayland_trace.log
```

### Step 3: Analyze Protocol Output

```bash
# Capture the first 100 lines of protocol output
head -100 wayland_trace.log

# Look for these specific patterns:
grep "wl_display" wayland_trace.log | head -10
grep "wl_registry" wayland_trace.log | head -10
grep "wl_compositor" wayland_trace.log | head -10
grep "wl_surface" wayland_trace.log | head -10
```

## 📊 Expected Output Analysis

### Connection Establishment Sequence

**Look for this pattern:**
```
[timestamp] wl_display@1.get_registry(new id wl_registry@2)
[timestamp] wl_registry@2.global(1, "wl_compositor", 4)
[timestamp] wl_registry@2.global(2, "wl_shm", 1)
[timestamp] wl_registry@2.global(3, "wl_seat", 7)
...
[timestamp] wl_registry@2.bind(1, "wl_compositor", 4, new id [unknown]@3)
```

**Analysis questions:**
1. How many global objects are advertised by your compositor?
2. Which interfaces does your application actually bind to?
3. What version numbers are being negotiated?

### Surface Creation Protocol

**Look for this pattern:**
```
[timestamp] wl_compositor@3.create_surface(new id wl_surface@4)
[timestamp] wl_surface@4.attach(wl_buffer@5, 0, 0)
[timestamp] wl_surface@4.damage(0, 0, 800, 600)
[timestamp] wl_surface@4.commit()
```

**Analysis questions:**
1. How many surfaces does your application create?
2. What buffer format and size is being used?
3. How often are commit() calls made?

### Buffer Allocation Pattern

**Look for this pattern:**
```
[timestamp] wl_shm@6.create_pool(new id wl_shm_pool@7, fd 4, 1920000)
[timestamp] wl_shm_pool@7.create_buffer(new id wl_buffer@8, 0, 800, 600, 3200, 1)
```

**Analysis questions:**
1. What size shared memory pool is being allocated?
2. What pixel format is being used? (format=1 is typically ARGB8888)
3. How is the stride calculated? (width * 4 for ARGB8888)

## 🎯 Key Insights to Document

### Protocol Message Overhead

**Count messages per frame:**
```bash
# Count surface commits (indicates frame rate)
grep "wl_surface.*commit" wayland_trace.log | wc -l

# Count buffer operations
grep "wl_buffer" wayland_trace.log | wc -l

# Count input events
grep -E "(wl_pointer|wl_keyboard|wl_touch)" wayland_trace.log | wc -l
```

### Object Lifecycle Tracking

**Identify object creation pattern:**
```bash
# Extract object IDs and their types
grep "new id" wayland_trace.log | head -20

# Example output analysis:
# wl_registry@2 - Global service registry
# wl_compositor@3 - Surface factory
# wl_surface@4 - Drawable surface
# wl_shm@6 - Shared memory manager
# wl_shm_pool@7 - Memory pool
# wl_buffer@8 - Pixel buffer
```

### Performance Characteristics

**Measure protocol overhead:**
```bash
# Count total protocol messages
wc -l wayland_trace.log

# Calculate messages per second (if you know runtime)
# messages_per_second = total_messages / runtime_seconds

# Identify most frequent operations
cut -d'.' -f2 wayland_trace.log | cut -d'(' -f1 | sort | uniq -c | sort -nr | head -10
```

## 📝 Documentation Template

**Create this analysis document:**

```markdown
# Wayland Protocol Analysis - Current Implementation

## Connection Establishment
- Compositor: [GNOME Shell/KDE Plasma/Sway]
- Global objects discovered: [count]
- Interfaces bound: [list]

## Surface Management
- Surfaces created: [count]
- Buffer format: [ARGB8888/XRGB8888/etc]
- Buffer size: [width x height]
- Shared memory pool size: [bytes]

## Message Patterns
- Total protocol messages: [count]
- Messages per frame: [estimate]
- Most frequent operations: [list top 5]

## Performance Observations
- Protocol overhead: [high/medium/low]
- Buffer allocation strategy: [per-frame/pooled/cached]
- Commit frequency: [every frame/on-demand]

## Questions for Investigation
1. Why does the application bind to [specific interfaces]?
2. How could buffer allocation be optimized?
3. What is the actual frame rate vs commit rate?
4. Are there unnecessary protocol round-trips?
```

## 🚀 Next Steps After Analysis

### Immediate Follow-up (same session)

1. **Compare with Simple Application**
   ```bash
   # Trace a minimal application for comparison
   WAYLAND_DEBUG=1 weston-simple-shm 2>&1 | head -50
   ```

2. **Identify Optimization Opportunities**
   - Are buffers being allocated every frame?
   - Are there unnecessary surface commits?
   - Is the application using optimal buffer formats?

3. **Document Protocol Dependencies**
   - Which interfaces are absolutely required?
   - What happens if optional interfaces are unavailable?
   - How does the application handle protocol errors?

### Preparation for Phase 2

**Set up for deeper protocol study:**
```bash
# Install protocol debugging tools
sudo apt install wayland-utils weston

# Clone wayland-rs for source study
git clone https://github.com/smithay/wayland-rs.git
cd wayland-rs

# Locate XML protocol definitions
find . -name "*.xml" | head -10
```

## 🎯 Success Criteria for This Session

**You should be able to answer:**
1. What Wayland interfaces does your current implementation use?
2. How many protocol messages are sent per frame?
3. What buffer allocation strategy is being used?
4. Where are the potential performance bottlenecks?

**If you can't answer these questions from the trace output, repeat the debugging session with more focused analysis.**

**This debugging session provides the foundation for all subsequent Track 1 learning. The protocol trace reveals exactly how your current implementation works, giving you concrete examples to study during the specification reading phase.**
