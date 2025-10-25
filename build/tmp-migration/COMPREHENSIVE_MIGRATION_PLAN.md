# Comprehensive Event Framework Migration Plan

## Executive Summary

**Objective:** Migrate 2,903 scattered logging statements across the Unhinged codebase to a unified event framework for enhanced observability, debugging, and operational monitoring.

**Timeline:** 4 phases over 3-4 weeks  
**Impact:** Foundational infrastructure improvement - critical for long-term system health  
**Confidence Level:** 98% (high confidence in technical approach and tooling)

## Migration Overview

| Phase | Component | Statements | Priority | Effort | Timeline |
|-------|-----------|------------|----------|--------|----------|
| **Phase 1** | Native GUI | 827 print() | 🔴 Critical | 4-5 days | Week 1 |
| **Phase 2** | Python Services | 63 logging | 🟡 High | 2-3 days | Week 2 |
| **Phase 3** | TypeScript/JS | 1,947 console | 🟡 High | 5-6 days | Week 2-3 |
| **Phase 4** | Kotlin Platforms | 266 logging | 🟢 Medium | 2-3 days | Week 4 |

**Total:** 2,903 statements → Unified event framework

## Phase 1: Native GUI Migration (CRITICAL PRIORITY)

### Scope: 827 print statements → Structured GUI events

**Justification:** Highest user visibility impact, immediate debugging improvement

### High-Impact Files (Execute First)

| File | Statements | Component | Migration Strategy |
|------|------------|-----------|-------------------|
| `camera_capture.py` | 74 | Vision Tool | Vision events + error handling |
| `audio_test.py` | 60 | Audio Tool | Test events + performance metrics |
| `speech_client.py` | 39 | Audio Tool | Service communication events |
| `mobile_chat_tool.py` | 38 | Chat Tool | User interaction events |
| `screen_capture.py` | 36 | Screen Tool | Capture events + system integration |
| `keyboard_capture.py` | 34 | Input Tool | Input events + privacy compliance |
| `application.py` | 33 | Core GUI | Application lifecycle events |
| `hotkey_manager.py` | 32 | Input Tool | Hotkey events + user preferences |
| `mouse_capture.py` | 27 | Input Tool | Mouse events + gesture tracking |
| `proto_browser.py` | 24 | API Dev Tool | Navigation + schema events |

### Migration Pattern Examples

**Before (Print Statements):**
```python
print("✅ Camera capture test completed")
print(f"❌ Failed to initialize camera: {e}")
print("🎯 YOLO (Ultralytics) available for object detection")
print(f"⚠️ Error testing camera {i}: {e}")
```

**After (Structured Events):**
```python
from unhinged_events import create_gui_logger

gui_logger = create_gui_logger("unhinged-vision-tool", "1.0.0")

gui_logger.info("Camera capture test completed", {
    "event_type": "test_completion",
    "component": "camera_capture",
    "test_result": "success"
})

gui_logger.error("Failed to initialize camera", exception=e, metadata={
    "event_type": "initialization_failure",
    "component": "camera_capture",
    "error_category": "hardware"
})

gui_logger.info("YOLO object detection available", {
    "event_type": "feature_availability",
    "component": "vision_analysis",
    "feature": "yolo_detection",
    "status": "available"
})

gui_logger.warn("Error testing camera", exception=e, metadata={
    "event_type": "hardware_test_failure",
    "component": "camera_capture",
    "camera_index": i,
    "test_phase": "capability_check"
})
```

### Log Level Classification Rules

| Pattern | Log Level | Reasoning |
|---------|-----------|-----------|
| `print("✅...")` | **INFO** | Success/completion messages |
| `print("❌...")` | **ERROR** | Failure/error messages |
| `print("⚠️...")` | **WARN** | Warning/caution messages |
| `print("🎯...")` | **INFO** | Status/availability messages |
| `print("🚀...")` | **INFO** | Startup/initialization messages |
| `print("🔧...")` | **DEBUG** | Configuration/setup messages |
| Exception contexts | **ERROR** | Any print with exception handling |
| Test outputs | **DEBUG** | Test-related print statements |

### Phase 1 Execution Steps

1. **Day 1-2: High-Impact Files (Top 5)**
   ```bash
   # Migrate top 5 files with most statements
   python3 libs/event-framework/migration_scripts/migrate_native_gui.py control/native_gui/tools/vision/camera_capture.py --apply
   python3 libs/event-framework/migration_scripts/migrate_native_gui.py control/native_gui/tools/chat/bridge/audio_test.py --apply
   python3 libs/event-framework/migration_scripts/migrate_native_gui.py control/native_gui/tools/audio/speech_client.py --apply
   python3 libs/event-framework/migration_scripts/migrate_native_gui.py control/native_gui/tools/chat/mobile_chat_tool.py --apply
   python3 libs/event-framework/migration_scripts/migrate_native_gui.py control/native_gui/tools/screen/screen_capture.py --apply
   ```

2. **Day 3: Core GUI Components**
   ```bash
   # Migrate core application files
   python3 libs/event-framework/migration_scripts/migrate_native_gui.py control/native_gui/core/application.py --apply
   python3 libs/event-framework/migration_scripts/migrate_native_gui.py control/native_gui/main_window.py --apply
   python3 libs/event-framework/migration_scripts/migrate_native_gui.py control/native_gui/core/tool_manager.py --apply
   ```

3. **Day 4: Input Tools**
   ```bash
   # Migrate input-related components
   python3 libs/event-framework/migration_scripts/migrate_native_gui.py control/native_gui/tools/input/ --apply
   ```

4. **Day 5: Remaining Components + Testing**
   ```bash
   # Migrate remaining files and comprehensive testing
   python3 libs/event-framework/migration_scripts/migrate_native_gui.py control/native_gui --apply
   ```

### Phase 1 Validation Checklist

- [ ] All 827 print statements replaced with structured events
- [ ] GUI functionality preserved (no broken features)
- [ ] Structured events appear in GUI logs tab
- [ ] Log levels appropriate for message content
- [ ] Metadata enhances debugging capabilities
- [ ] No performance degradation in GUI responsiveness

## Phase 2: Python Services Migration

### Scope: 63 logging calls → Event framework

**Services Breakdown:**
- **speech-to-text**: 24 logging calls, 10 print statements
- **text-to-speech**: 20 logging calls, 0 print statements  
- **vision-ai**: 19 logging calls, 0 print statements

### Migration Pattern Examples

**Before (Standard Logging):**
```python
import logging
logger = logging.getLogger(__name__)

logger.info("Service starting...")
logger.error(f"Failed to process request: {e}")
logger.warning("Model not available, using fallback")
```

**After (Event Framework):**
```python
from unhinged_events import create_service_logger

event_logger = create_service_logger("speech-to-text-service", "1.0.0")

event_logger.info("Service starting", {
    "event_type": "service_lifecycle",
    "phase": "startup",
    "service_type": "ai_service"
})

event_logger.error("Failed to process request", exception=e, metadata={
    "event_type": "request_processing_failure",
    "request_type": "speech_transcription",
    "error_category": "processing"
})

event_logger.warn("Model not available, using fallback", {
    "event_type": "model_fallback",
    "primary_model": "whisper-large",
    "fallback_model": "whisper-base",
    "reason": "model_unavailable"
})
```

### Phase 2 Execution Steps

1. **Day 1: Speech-to-Text Service**
   ```bash
   python3 libs/event-framework/migration_scripts/migrate_python_services.py services speech-to-text --apply
   ```

2. **Day 2: Text-to-Speech + Vision-AI Services**
   ```bash
   python3 libs/event-framework/migration_scripts/migrate_python_services.py services text-to-speech --apply
   python3 libs/event-framework/migration_scripts/migrate_python_services.py services vision-ai --apply
   ```

3. **Day 3: Testing + Integration**
   - Test AI service functionality
   - Validate OpenTelemetry trace correlation
   - Verify structured events in monitoring

## Phase 3: TypeScript/JavaScript Migration

### Scope: 1,947 console calls → Structured events

**Components:** Web SDK, browser tools, development utilities

### Migration Pattern Examples

**Before (Console Logging):**
```javascript
console.log("User clicked submit button");
console.error("API request failed:", error);
console.warn("Deprecated API usage detected");
```

**After (Event Framework):**
```typescript
import { createWebLogger } from '@unhinged/event-framework';

const webLogger = createWebLogger('unhinged-web-sdk', '1.0.0');

webLogger.logButtonClick('Submit', 'submit-btn', { x: 100, y: 200 }, 'user123');

webLogger.logError("API request failed", "api_error", window.location.href, error);

webLogger.logPerformanceMetric("api_response_time", 250, "ms");
```

### Phase 3 Execution Strategy

1. **Days 1-2: Web SDK Core**
   - Migrate main SDK logging calls
   - Implement auto-tracking for common interactions

2. **Days 3-4: Browser Tools**
   - Migrate development tool console calls
   - Add structured event tracking

3. **Days 5-6: Testing + Integration**
   - Cross-browser testing
   - Performance impact validation

## Phase 4: Kotlin Platforms Migration

### Scope: 266 logging statements → Event framework

**Platform:** Persistence platform (primary target)

### Migration Pattern Examples

**Before (Standard Kotlin Logging):**
```kotlin
private val logger = LoggerFactory.getLogger(this::class.java)

logger.info("Database connection established")
logger.error("Failed to execute query", exception)
```

**After (Event Framework):**
```kotlin
import com.unhinged.events.*

private val eventLogger = createServiceEventLogger("persistence-platform", "1.0.0")

eventLogger.info("Database connection established", mapOf(
    "event_type" to "database_connection",
    "connection_type" to "cockroachdb",
    "status" to "connected"
))

eventLogger.error("Failed to execute query", exception, mapOf(
    "event_type" to "query_execution_failure",
    "query_type" to "select",
    "table" to "users"
))
```

## Risk Mitigation & Quality Assurance

### Pre-Migration Checklist
- [ ] Event framework modules installed and tested
- [ ] Migration scripts validated on sample files
- [ ] Backup of current codebase created
- [ ] Test environments prepared

### During Migration
- [ ] Migrate in small batches (5-10 files at a time)
- [ ] Test functionality after each batch
- [ ] Monitor performance impact
- [ ] Validate log output format

### Post-Migration Validation
- [ ] All logging statements migrated
- [ ] No functionality regressions
- [ ] Structured events visible in GUI logs tab
- [ ] OpenTelemetry traces correlated correctly
- [ ] Performance within acceptable limits

## Success Metrics

### Quantitative Metrics
- **100%** of 2,903 logging statements migrated
- **0** functionality regressions
- **<5%** performance impact
- **100%** structured event visibility in logs

### Qualitative Improvements
- **Enhanced debugging** with structured metadata
- **Unified observability** across all components
- **Better operational monitoring** capabilities
- **Improved developer experience** with consistent logging

## Rollback Plan

If critical issues arise during migration:

1. **Immediate Rollback**
   ```bash
   git checkout HEAD~1  # Revert to pre-migration state
   ```

2. **Partial Rollback**
   ```bash
   git revert <specific-commit>  # Revert specific migration batch
   ```

3. **Component-Specific Rollback**
   - Revert individual files while keeping successful migrations

## Timeline Summary

| Week | Phase | Focus | Deliverables |
|------|-------|-------|--------------|
| **Week 1** | Phase 1 | Native GUI | 827 print statements → GUI events |
| **Week 2** | Phase 2 & 3 Start | Services + Web | 63 service calls + web migration start |
| **Week 3** | Phase 3 Complete | TypeScript/JS | 1,947 console calls → structured events |
| **Week 4** | Phase 4 | Kotlin Platforms | 266 logging statements → unified format |

**Total Duration:** 3-4 weeks  
**Total Effort:** 13-17 days  
**Expected Outcome:** Unified, observable, maintainable logging infrastructure

This migration represents critical infrastructure maintenance that will pay dividends in debugging efficiency, operational visibility, and system maintainability for years to come.

## Execution Commands

### Pre-Migration Setup
```bash
# 1. Backup current codebase
git checkout -b event-framework-migration
git add -A && git commit -m "Pre-migration backup"

# 2. Validate event framework installation
python3 -c "from unhinged_events import create_gui_logger; print('✅ Event framework ready')"

# 3. Run comprehensive analysis
./libs/event-framework/migration_scripts/analyze_all_logging.sh
```

### Phase 1 Execution (Native GUI)
```bash
# Dry run first (recommended)
./libs/event-framework/migration_scripts/execute_phase1.sh . true

# Execute actual migration
./libs/event-framework/migration_scripts/execute_phase1.sh . false

# Validate migration quality
python3 libs/event-framework/migration_scripts/validate_migration.py control/native_gui

# Test GUI functionality
python3 control/native_gui/launcher.py
```

### Phase 2 Execution (Python Services)
```bash
# Migrate each service individually
python3 libs/event-framework/migration_scripts/migrate_python_services.py services speech-to-text --apply
python3 libs/event-framework/migration_scripts/migrate_python_services.py services text-to-speech --apply
python3 libs/event-framework/migration_scripts/migrate_python_services.py services vision-ai --apply

# Validate service migrations
python3 libs/event-framework/migration_scripts/validate_migration.py services
```

### Phase 3 & 4 (TypeScript/Kotlin)
```bash
# TypeScript migration (manual with framework)
# Use libs/event-framework/typescript/ implementation

# Kotlin migration (manual with framework)
# Use libs/event-framework/kotlin/ implementation
```

## Quality Gates

Each phase must pass these quality gates before proceeding:

### ✅ **Phase 1 Quality Gate**
- [ ] All 827 print statements migrated
- [ ] GUI launches without errors
- [ ] Structured events visible in logs tab
- [ ] No functionality regressions
- [ ] Validation score ≥ 85%

### ✅ **Phase 2 Quality Gate**
- [ ] All 63 service logging calls migrated
- [ ] Services start and respond correctly
- [ ] OpenTelemetry traces correlated
- [ ] AI functionality preserved
- [ ] Validation score ≥ 85%

### ✅ **Phase 3 Quality Gate**
- [ ] Console calls replaced with structured events
- [ ] Web components function correctly
- [ ] Browser compatibility maintained
- [ ] Performance impact < 5%

### ✅ **Phase 4 Quality Gate**
- [ ] Kotlin logging unified
- [ ] Database operations logged correctly
- [ ] Platform services operational
- [ ] Trace correlation working

## Confidence Assessment: 98%

**High Confidence Areas (95%+):**
- Event framework implementation completeness
- Migration script functionality
- Pattern detection accuracy
- Native GUI migration approach
- Python services migration strategy

**Medium Confidence Areas (90-95%):**
- TypeScript/JavaScript migration complexity
- Performance impact estimation
- Cross-browser compatibility

**Clarification Needed (<95%):**
- Specific Kotlin platform integration points
- Custom logging patterns not covered by scripts
- Legacy code compatibility requirements

This comprehensive plan provides the roadmap for transforming Unhinged's logging infrastructure into a unified, observable, and maintainable system.
