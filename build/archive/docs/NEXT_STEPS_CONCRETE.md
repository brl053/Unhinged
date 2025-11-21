# Concrete Next Steps: CLI & Analysis Strategy

## Decision Points for You

### 1. Code Analysis Library
**Question**: Use libcst or keep custom AST?

**Recommendation**: Start with libcst
- Industry standard (Ruff uses it)
- Better for upstream/downstream tracking
- Scales to complex queries
- One-time learning curve

**Action**: Approve libcst integration

---

### 2. CLI Consolidation
**Question**: Move control/cli → libs/cli?

**Recommendation**: Yes, consolidate
- Single source of truth
- Easier testing
- Better code reuse
- Cleaner architecture

**Action**: Approve libs/cli consolidation

---

### 3. GTK4 GUI Status
**Question**: Archive or keep active?

**Recommendation**: Archive (move to inactive)
- Focus on headless-first
- Stronger foundation
- Better testability
- GUI can be added later

**Action**: Approve GTK4 archival

---

### 4. Distribution Method
**Question**: ./unhinged vs unhinged command?

**Recommendation**: Both
- Keep ./unhinged for development
- Add Python entry point for distribution
- Document both in README

**Action**: Approve dual approach

---

## If You Approve All Four

### Week 1: Code Analysis
```bash
# 1. Add libcst to requirements
pip install libcst>=0.4.0

# 2. Create libs/cli/commands/analyze.py
# 3. Implement:
#    - find_usages(symbol)
#    - upstream_downstream(filepath, symbol)
#    - import_graph(filepath)

# 4. Wire to CLI:
#    ./unhinged dev analyze usages BuildUtils
#    ./unhinged dev analyze upstream-downstream build/modules/dual_system_builder.py/DualSystemBuilder

# 5. Test with your codebase
```

### Week 2: CLI Consolidation
```bash
# 1. Create libs/cli/ structure
# 2. Move control/cli/ → libs/cli/core/
# 3. Update imports in control/__main__.py
# 4. Consolidate build/cli.py → libs/cli/commands/build.py
# 5. Merge conversation_cli.py → libs/cli/commands/chat.py
# 6. Update ./unhinged shim
# 7. Run all tests
```

### Week 3: Headless-First Shift
```bash
# 1. Archive control/gtk4_gui/ (rename to gtk4_gui_archived/)
# 2. Remove GTK4 from active development docs
# 3. Update README to emphasize CLI/libs
# 4. Remove GTK4 from CI/CD
# 5. Document headless-first development pattern
```

### Week 4: Distribution & Man Pages
```bash
# 1. Create pyproject.toml with entry point
# 2. Generate man pages from Click docstrings
# 3. Create man/man1/unhinged.1 (main)
# 4. Create man/man1/unhinged-dev.1
# 5. Create man/man1/unhinged-analyze.1
# 6. Test: man unhinged
```

---

## Immediate Actions (Today)

### If You Approve This Plan:

1. **Review** the three documents:
   - `build/CLI_ARCHITECTURE_PLAN.md`
   - `build/TECHNICAL_MEMO_CLI_STRATEGY.txt`
   - `build/LIBCST_VS_CUSTOM_AST.md`

2. **Decide** on the four points above

3. **Confirm** which week to start

4. **I will then**:
   - Create detailed implementation tasks
   - Set up libs/cli/ structure
   - Integrate libcst
   - Update documentation

---

## Questions for You

1. **Libcst**: Approve using it for production code analysis?
2. **CLI Consolidation**: Approve moving control/cli → libs/cli?
3. **GTK4**: Approve archiving (not deleting)?
4. **Distribution**: Approve dual approach (./unhinged + pip install)?
5. **Timeline**: Which week to start?

---

## Risk Assessment

### Low Risk
- Adding libcst (new feature, no breaking changes)
- Archiving GTK4 (not deleting, just moving)
- Adding man pages (new documentation)

### Medium Risk
- CLI consolidation (requires careful import updates)
- Distribution setup (needs testing on different systems)

### Mitigation
- All changes are backward compatible
- Keep ./unhinged working during migration
- Comprehensive testing before each phase
- Git commits at each milestone

---

## Success Criteria

✅ Phase 1: `./unhinged dev analyze usages BuildUtils` works
✅ Phase 2: `./unhinged dev build` works from libs/cli
✅ Phase 3: GTK4 archived, README emphasizes CLI
✅ Phase 4: `man unhinged` displays proper man page
✅ Phase 5: `pip install -e .` makes `unhinged` command available

---

## Files Created for Your Review

1. `build/CLI_ARCHITECTURE_PLAN.md` - Detailed architecture
2. `build/TECHNICAL_MEMO_CLI_STRATEGY.txt` - Executive summary
3. `build/LIBCST_VS_CUSTOM_AST.md` - Library comparison
4. `build/NEXT_STEPS_CONCRETE.md` - This file

**Next**: Your approval on the four decision points above.

