# Strict Mode Migration Roadmap

> **Purpose**: Plan for migrating legacy directories to strict type checking  
> **Status**: In Progress - Phase 2 Complete  
> **Last Updated**: 2025-11-21

---

## Current State

### ✅ Completed (Phase 1-2)
- **14 directories** in enhanced mode (89% of codebase)
- **Pre-commit hooks** blocking on violations
- **CI/CD checks** enforcing clean directories
- **Emergency override** procedures documented

### 🔄 In Progress
- **3 legacy directories** with 27 errors (11% of codebase)
- Migration plan defined
- Quarterly goals set

---

## Legacy Directories Status

| Directory | Lines | Errors | Priority | Target | Status |
|-----------|-------|--------|----------|--------|--------|
| services/image-generation | 561 | 1 | P1 | Week 2 | 🟡 Planned |
| services/graph-service | 1,377 | 6 | P2 | Q1 2025 | 🔴 Not Started |
| services/chat-with-sessions | 1,976 | 20 | P3 | Q1 2025 | 🔴 Not Started |

---

## Migration Process (Per Directory)

### Step 1: Analyze Errors
```bash
# Get detailed error list
mypy --config-file=mypy.ini services/TARGET_DIR > errors.txt

# Categorize errors
grep "Returning Any" errors.txt
grep "Missing type annotation" errors.txt
grep "Incompatible types" errors.txt
```

### Step 2: Fix Errors
Use patterns from TYPE_SAFETY_GUIDE.md:
- Pattern 1: TYPE_CHECKING guards
- Pattern 2: Explicit dict[str, Any]
- Pattern 3: YAML type guards
- Pattern 4: type: ignore[no-any-return]
- Pattern 5: Union narrowing
- Pattern 6: .get() with default

### Step 3: Enable Strict Mode
```ini
# Add to mypy.ini
[mypy-services.TARGET_DIR.*]
check_untyped_defs = True
warn_return_any = True
```

### Step 4: Verify
```bash
# Confirm zero errors
mypy --config-file=mypy.ini services/TARGET_DIR

# Run tests
pytest services/TARGET_DIR/tests/

# Update documentation
```

### Step 5: Document
- Update MYPY_BASELINE_AUDIT.md
- Remove from legacy list
- Add to clean list
- Commit with migration notes

---

## Q1 2025 Migration Plan

### Week 2 (Dec 2024): services/image-generation
**Effort**: 1 hour  
**Errors**: 1  
**Owner**: TBD

**Tasks**:
- [ ] Analyze single error
- [ ] Apply appropriate pattern from guide
- [ ] Enable strict mode in mypy.ini
- [ ] Verify with tests
- [ ] Document migration

**Success Criteria**:
- Zero errors in services/image-generation
- Strict mode enabled
- Tests passing

---

### January 2025: services/graph-service
**Effort**: 4 hours  
**Errors**: 6  
**Owner**: TBD

**Tasks**:
- [ ] Analyze 6 errors
- [ ] Fix errors using TYPE_SAFETY_GUIDE.md patterns
- [ ] Enable strict mode in mypy.ini
- [ ] Run full test suite
- [ ] Document lessons learned

**Success Criteria**:
- Zero errors in services/graph-service
- Strict mode enabled
- All tests passing
- Migration documented

---

### February 2025: services/chat-with-sessions
**Effort**: 8 hours  
**Errors**: 20  
**Owner**: TBD

**Tasks**:
- [ ] Analyze 20 errors
- [ ] Categorize by pattern type
- [ ] Fix in batches (5 errors per session)
- [ ] Enable strict mode in mypy.ini
- [ ] Comprehensive testing
- [ ] Document common patterns found

**Success Criteria**:
- Zero errors in services/chat-with-sessions
- Strict mode enabled
- All tests passing
- Patterns added to TYPE_SAFETY_GUIDE.md if new

---

## Success Metrics

### Immediate (Week 2)
- [ ] services/image-generation migrated
- [ ] 15/17 directories in strict mode (88% → 92%)
- [ ] 26 errors remaining

### Q1 2025 End
- [ ] All 17 directories in strict mode (100%)
- [ ] Zero mypy errors across entire codebase
- [ ] Migration process documented
- [ ] Lessons learned captured

### Ongoing
- [ ] <5% of commits use --no-verify
- [ ] Zero new type errors in strict directories
- [ ] Developer satisfaction >80%

---

## Lessons Learned (To Be Updated)

### Week 2: services/image-generation
- TBD after migration

### January: services/graph-service
- TBD after migration

### February: services/chat-with-sessions
- TBD after migration

---

## Common Patterns (To Be Updated)

As we migrate, we'll document common patterns here:

### Pattern: ServiceLogger Type Issues
- **Problem**: TBD
- **Solution**: TBD
- **Example**: TBD

---

## Rollback Plan

If migration causes issues:

1. **Immediate** (<1 hour)
   - Revert mypy.ini changes for directory
   - Return to permissive mode
   - Document what went wrong

2. **Short-term** (<1 day)
   - Analyze root cause
   - Fix issues
   - Re-attempt migration

3. **Long-term** (<1 week)
   - If persistent issues, defer to next quarter
   - Update migration plan
   - Communicate to team

---

## Resources

- [TYPE_SAFETY_GUIDE.md](TYPE_SAFETY_GUIDE.md) - Patterns and examples
- [MYPY_BASELINE_AUDIT.md](MYPY_BASELINE_AUDIT.md) - Current state
- [EMERGENCY_OVERRIDE.md](EMERGENCY_OVERRIDE.md) - Override procedures
- [mypy.ini](../../mypy.ini) - Configuration

---

## Next Actions

1. **Assign owners** for each migration
2. **Schedule migration sessions** (pair programming recommended)
3. **Set up monitoring** for --no-verify usage
4. **Create feedback channel** for migration issues

---

**Status**: Ready to execute Week 2 migration (services/image-generation)

