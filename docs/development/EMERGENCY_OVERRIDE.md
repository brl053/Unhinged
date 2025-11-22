# Emergency Override Procedures

> **Purpose**: Document when and how to bypass type safety enforcement  
> **Audience**: Developers facing urgent production issues  
> **Last Updated**: 2025-11-21

---

## When to Use Emergency Override

### ✅ **VALID** Use Cases

1. **Production Hotfix**
   - Critical bug affecting users
   - Fix is time-sensitive (<1 hour)
   - Type errors are in unrelated code

2. **Dependency Update**
   - Third-party library update breaks types
   - Temporary until stubs updated
   - Documented in commit message

3. **Merge Conflict Resolution**
   - Type errors introduced by merge
   - Need to commit to resolve conflict
   - Will fix in follow-up commit

### ❌ **INVALID** Use Cases

1. **Convenience**
   - "I don't want to fix the errors"
   - "It works on my machine"
   - "I'll fix it later" (without ticket)

2. **Lack of Understanding**
   - "I don't understand the error"
   - "Type safety is annoying"
   - "This is taking too long"

3. **Systematic Issues**
   - Multiple files with errors
   - Architectural problems
   - Should be addressed properly

---

## How to Override

### Pre-commit Hooks

```bash
# Bypass all pre-commit hooks (including type safety)
git commit --no-verify -m "hotfix: critical production issue"

# Or set environment variable
SKIP=type-safety-validator git commit -m "hotfix: ..."
```

### CI/CD Checks

CI/CD type checks **cannot be bypassed** for pull requests.

**Workaround for emergencies**:
1. Push directly to main (requires admin access)
2. Or merge with admin override (requires justification)

---

## Required Documentation

When using `--no-verify`, you **MUST**:

1. **Document in commit message**
   ```
   hotfix: fix critical auth bypass vulnerability
   
   Emergency override used: Production security issue
   Type errors in unrelated logging code
   Follow-up ticket: #1234
   ```

2. **Create follow-up ticket**
   - Link to commit
   - Describe type errors
   - Assign to yourself
   - Due within 48 hours

3. **Notify team**
   - Post in #engineering channel
   - Explain why override was necessary
   - Share follow-up ticket

---

## Consequences of Misuse

### First Offense
- ⚠️ Warning from tech lead
- Required to fix errors within 24 hours
- Code review of all future commits for 1 week

### Second Offense
- ❌ Loss of `--no-verify` privilege (branch protection)
- Required pair programming for 1 week
- Mandatory type safety training

### Third Offense
- 🚫 Escalation to engineering manager
- Performance improvement plan
- Potential removal from critical path work

---

## Alternative Solutions

Before using override, try these:

### 1. Ask for Help
```bash
# Post in Slack
"Getting mypy error in foo.py line 42. Anyone know how to fix?"

# Or pair with teammate
"Can you help me understand this type error?"
```

### 2. Use Type Ignore (Targeted)
```python
# Instead of bypassing entire commit, ignore specific line
result = some_dynamic_function()  # type: ignore[no-any-return]
```

### 3. Fix in Separate Commit
```bash
# Commit working code first
git add file_without_errors.py
git commit -m "feat: add new feature"

# Fix type errors in follow-up
git add file_with_errors.py
git commit -m "fix: resolve type errors in feature"
```

### 4. Request Temporary Exemption
```bash
# Add to mypy.ini temporarily
[mypy-my_module.*]
disallow_untyped_defs = False  # TODO: Remove after refactor

# Commit with explanation
git commit -m "temp: disable strict mode for my_module (refactor in progress)"
```

---

## Monitoring

Emergency overrides are tracked:

- **Git log**: `git log --grep="--no-verify"`
- **Weekly report**: Sent to engineering team
- **Metrics dashboard**: Shows override frequency

**Target**: <5% of commits use override

---

## Examples

### ✅ Good Override

```bash
# Production is down, auth service failing
git commit --no-verify -m "hotfix: fix auth token validation

Emergency override: Production outage
Type errors in unrelated metrics code
Follow-up: #5678 (fix metrics types)
ETA: 2 hours"

# Follow-up within 2 hours
git commit -m "fix: resolve type errors in metrics code

Closes #5678
Related to hotfix in commit abc123"
```

### ❌ Bad Override

```bash
# Just don't want to deal with it
git commit --no-verify -m "add feature"

# No explanation, no follow-up, no ticket
```

---

## FAQ

**Q: Can I use `--no-verify` for WIP commits?**  
A: No. Use `git commit --amend` or feature branches instead.

**Q: What if I don't know how to fix the error?**  
A: Ask for help in #engineering. Don't bypass.

**Q: The error is in generated code, not my code.**  
A: Add generated code to mypy exclude list in mypy.ini.

**Q: I'm on a deadline and don't have time.**  
A: Type errors indicate real issues. Fix them or escalate to tech lead.

**Q: Can I bypass for experimental branches?**  
A: Yes, but must fix before merging to main.

---

## Contact

Questions about override policy:
- **Tech Lead**: @tech-lead
- **Engineering Manager**: @eng-manager
- **Slack**: #engineering

---

**Remember**: Type safety exists to catch bugs before production. Bypassing it should be rare and well-justified.

