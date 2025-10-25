# Event Framework Migration Analysis

This document tracks existing logging patterns across the Unhinged codebase and provides a migration plan to the new unified event framework.

## Current Logging Inventory

### 🖥️ Native GUI (`control/native_gui/`)

**Current State:**
- **829 print statements** - Heavy use of print() for debugging and user feedback
- **6 logging instances** - Limited use of Python's logging module
- **Patterns Found:**
  - Status messages: `print("✅ GTK4 and Adwaita available")`
  - Error messages: `print(f"❌ Failed to start native GUI: {e}")`
  - Debug info: `print("🎯 Application activating...")`
  - User feedback: `print("🚀 Launching mobile-first control center...")`

**Key Files with Heavy Logging:**
```
control/native_gui/launcher.py              - 23 print statements
control/native_gui/__init__.py               - 15 print statements  
control/native_gui/bridge/grpc_client.py    - 12 print statements
control/native_gui/bridge/http_client.py    - 8 print statements
control/native_gui/bridge/proto_scanner.py  - 10 print statements
control/native_gui/health_client.py         - 6 logging calls
```

**Existing Logging Infrastructure:**
```python
# health_client.py - Already uses proper logging
import logging
logger = logging.getLogger(__name__)
logger.warning(f"gRPC error for {service_name}: {e.code()}")
logger.error(f"Unexpected error for {service_name}: {e}")
```

### 🐍 Python Services (`services/`)

**Current State:**
- **Mixed logging patterns** - Some services use logging, others use print
- **Key Services:**
  - `speech-to-text/main.py` - 13 logging calls
  - `speech-to-text/grpc_server.py` - 17 logging calls
  - `text-to-speech/main.py` - 15 logging calls
  - `vision-ai/main.py` - 12 logging calls

**Patterns Found:**
```python
# Typical service logging pattern
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Service starting...")
```

### ☕ Kotlin Platforms (`platforms/`)

**Current State:**
- **Structured logging present** - Most Kotlin code uses proper logging
- **Key Files:**
  - `PersistencePlatformApplication.kt` - 34 logging calls
  - `CockroachDbCrudTest.kt` - 40 logging calls
  - `ObservabilityManager.kt` - 19 logging calls

**Patterns Found:**
```kotlin
// Typical Kotlin logging pattern
private val logger = LoggerFactory.getLogger(this::class.java)
logger.info("Database connection established")
logger.error("Failed to execute query", exception)
```

### 🌐 Control Systems (`control/`)

**Current State:**
- **Mixed patterns** - Some structured logging, many print statements
- **Key Files:**
  - `deployment/deploy.py` - 41 logging calls
  - `system/system_controller.py` - 18 logging calls
  - `network/service_registry.py` - 15 logging calls

## Migration Priority Matrix

### 🔴 **HIGH PRIORITY** (Immediate Migration)

1. **Native GUI (`control/native_gui/`)**
   - **Impact:** 829 print statements affecting user experience
   - **Benefit:** Centralized GUI event logging, better debugging
   - **Effort:** Medium (need to replace print with gui_logger calls)

2. **Health Client (`control/native_gui/health_client.py`)**
   - **Impact:** Already uses logging, easy to migrate
   - **Benefit:** Structured health monitoring events
   - **Effort:** Low (already structured)

### 🟡 **MEDIUM PRIORITY** (Next Phase)

3. **Python Services (`services/`)**
   - **Impact:** Core AI services need structured logging
   - **Benefit:** Better observability for AI operations
   - **Effort:** Medium (replace logging with event framework)

4. **Control Systems (`control/`)**
   - **Impact:** System operations and deployment logging
   - **Benefit:** Better operational visibility
   - **Effort:** Medium

### 🟢 **LOW PRIORITY** (Future Enhancement)

5. **Kotlin Platforms (`platforms/`)**
   - **Impact:** Already well-structured
   - **Benefit:** Unified format across languages
   - **Effort:** Low (mostly configuration changes)

## Migration Plan

### Phase 1: Native GUI Migration

**Target:** Replace 829 print statements with structured GUI events

**Before:**
```python
print("✅ GTK4 and Adwaita available")
print(f"❌ Failed to start native GUI: {e}")
print("🎯 Application activating...")
```

**After:**
```python
from unhinged_events import create_gui_logger

gui_logger = create_gui_logger("unhinged-control-center", "1.0.0")

gui_logger.info("GTK4 and Adwaita available", {"status": "dependencies_ok"})
gui_logger.error("Failed to start native GUI", exception=e, metadata={"component": "launcher"})
gui_logger.info("Application activating", {"event_type": "app_lifecycle", "phase": "activation"})
```

**Migration Script Pattern:**
```bash
# Find and replace common patterns
sed -i 's/print("✅/gui_logger.info("/g' control/native_gui/*.py
sed -i 's/print("❌/gui_logger.error("/g' control/native_gui/*.py
sed -i 's/print("🎯/gui_logger.debug("/g' control/native_gui/*.py
```

### Phase 2: Service Migration

**Target:** Migrate Python services to event framework

**Before:**
```python
import logging
logger = logging.getLogger(__name__)
logger.info("Service starting...")
```

**After:**
```python
from unhinged_events import create_service_logger

logger = create_service_logger("speech-to-text-service", "1.0.0")
logger.info("Service starting", {"service_type": "ai_service", "component": "speech_to_text"})
```

### Phase 3: Kotlin Integration

**Target:** Integrate Kotlin services with event framework

**Before:**
```kotlin
private val logger = LoggerFactory.getLogger(this::class.java)
logger.info("Database connection established")
```

**After:**
```kotlin
import com.unhinged.events.*

private val eventLogger = createServiceEventLogger("persistence-platform", "1.0.0")
eventLogger.info("Database connection established", mapOf(
    "component" to "database",
    "connection_type" to "cockroachdb"
))
```

## Migration Tracking

### Files Requiring Migration

#### Native GUI (High Priority)
- [ ] `control/native_gui/launcher.py` (23 prints → GUI events)
- [ ] `control/native_gui/__init__.py` (15 prints → GUI events)
- [ ] `control/native_gui/bridge/grpc_client.py` (12 prints → service events)
- [ ] `control/native_gui/bridge/http_client.py` (8 prints → service events)
- [ ] `control/native_gui/bridge/proto_scanner.py` (10 prints → debug events)
- [x] `control/native_gui/health_client.py` (6 logging → structured events) - **READY**

#### Python Services (Medium Priority)
- [ ] `services/speech-to-text/main.py` (13 logging → service events)
- [ ] `services/speech-to-text/grpc_server.py` (17 logging → service events)
- [ ] `services/text-to-speech/main.py` (15 logging → service events)
- [ ] `services/vision-ai/main.py` (12 logging → service events)

#### Kotlin Platforms (Low Priority)
- [ ] `platforms/persistence/src/main/kotlin/com/unhinged/persistence/PersistencePlatformApplication.kt`
- [ ] `platforms/persistence/src/main/kotlin/com/unhinged/persistence/monitoring/ObservabilityManager.kt`
- [ ] `platforms/persistence/src/repository/CockroachDbCrud.kt`

#### Control Systems (Medium Priority)
- [ ] `control/deployment/deploy.py` (41 logging → deployment events)
- [ ] `control/system/system_controller.py` (18 logging → system events)
- [ ] `control/network/service_registry.py` (15 logging → network events)

## Migration Benefits

### Before Migration
- **Inconsistent formats** across languages and components
- **No centralized logging** - logs scattered across stdout, files, etc.
- **Limited observability** - hard to correlate events across services
- **No structured metadata** - difficult to query and analyze

### After Migration
- **Unified YAML format** across all components
- **Centralized event collection** - all logs appear in GUI and CLI
- **Rich metadata** - structured context for better debugging
- **OpenTelemetry integration** - automatic trace correlation
- **Better user experience** - GUI events properly logged and displayed

## Next Steps

1. **Start with Native GUI** - Highest impact, most visible improvements
2. **Create migration scripts** - Automate common print → event_logger replacements
3. **Update documentation** - Guide developers on new logging patterns
4. **Gradual rollout** - Migrate one component at a time
5. **Monitor and adjust** - Ensure new logging doesn't impact performance

## Estimated Timeline

- **Phase 1 (Native GUI):** 2-3 days
- **Phase 2 (Python Services):** 3-4 days  
- **Phase 3 (Kotlin Platforms):** 2-3 days
- **Phase 4 (Control Systems):** 2-3 days

**Total Estimated Effort:** 9-13 days for complete migration
