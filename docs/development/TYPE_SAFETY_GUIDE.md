# Type Safety Guide - Unhinged Platform

> **Purpose**: Systematic patterns for type safety learned from 179 mypy error fixes
> **Status**: Production patterns extracted from real fixes
> **Last Updated**: 2025-11-22

## Core Principles

1. **Explicit over Implicit**: Always annotate heterogeneous data structures
2. **Pragmatic Ignores**: Use `type: ignore` for inherently dynamic operations
3. **TYPE_CHECKING Guards**: Separate type-checking from runtime imports
4. **Type Guards**: Validate dynamic data (YAML, JSON, DB) before use

---

## Pattern 1: TYPE_CHECKING for Import Fallbacks

**Problem**: try/except ImportError defines classes twice → mypy "already defined" error

**Solution**: Use TYPE_CHECKING guard to separate type-checking from runtime

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Type checker always sees real types
    from modules import BuildModule, BuildContext
else:
    # Runtime uses fallback if import fails
    try:
        from modules import BuildModule, BuildContext
    except ImportError:
        class BuildModule:
            def __init__(self, context): ...
        class BuildContext:
            def __init__(self): ...
```

**When to Use**:
- Optional dependencies with fallback implementations
- Build system modules with complex import paths
- Development vs production import differences

---

## Pattern 2: Explicit dict[str, Any] for Heterogeneous Data

**Problem**: Heterogeneous dict literals → mypy infers `object` type

**Solution**: Explicit type annotation on variable

```python
# ❌ BAD - mypy infers object
summary = {
    "healthy": [],      # list
    "total": 0,         # int
    "percentage": 0.0,  # float
}

# ✅ GOOD - explicit annotation
summary: dict[str, Any] = {
    "healthy": [],
    "total": 0,
    "percentage": 0.0,
}
```

**When to Use**:
- Mixed-type dictionaries (lists + ints + floats)
- API responses with varied field types
- Configuration objects
- Summary/report data structures

---

## Pattern 3: Type Guards for Dynamic Data

**Problem**: yaml.safe_load(), json.loads(), DB queries return Any

**Solution**: isinstance() check after loading

```python
# ❌ BAD - returns Any
def load_config() -> dict[str, Any]:
    with open(path) as f:
        return yaml.safe_load(f)  # mypy error: Returning Any

# ✅ GOOD - type guard
def load_config() -> dict[str, Any]:
    with open(path) as f:
        result = yaml.safe_load(f)
        if not isinstance(result, dict):
            raise ValueError("Config must be a dictionary")
        return result  # mypy happy
```

**When to Use**:
- YAML/JSON parsing
- Database query results
- External API responses
- User input validation

---

## Pattern 4: Pragmatic type: ignore for Inherently Dynamic Operations

**Problem**: Dict access, DB cursors, protobuf fields return Any

**Solution**: Use `type: ignore[no-any-return]` with comment

```python
def get_token(spec: dict[str, Any], path: str) -> dict[str, Any]:
    """Extract design token from specification."""
    # Dict access is inherently dynamic - validated at runtime
    return spec['tokens'][path]  # type: ignore[no-any-return]

def query_db(cursor, query: str) -> bool:
    """Execute database query."""
    cursor.execute(query)
    # DB cursor.fetchone() returns Any - can't be typed
    return cursor.fetchone()[0]  # type: ignore[no-any-return]
```

**When to Use**:
- Nested dict access with runtime validation
- Database cursor operations
- Protobuf field access
- Redis/cache operations

**Guidelines**:
- Add comment explaining why it's dynamic
- Ensure runtime validation exists
- Limit scope to single return statement

---

## Pattern 5: Union Type Narrowing Workarounds

**Problem**: hasattr() doesn't narrow union types in mypy

**Solution**: Use `type: ignore[union-attr]` or isinstance()

```python
# EventLogger | Logger union
logger: EventLogger | Logger

# ❌ BAD - mypy doesn't narrow
if hasattr(logger, "warn"):
    logger.warn("message")  # mypy error: Logger has no warn

# ✅ OPTION 1 - type: ignore
if hasattr(logger, "warn"):
    logger.warn("message")  # type: ignore[union-attr]

# ✅ OPTION 2 - isinstance (preferred if possible)
if isinstance(logger, EventLogger):
    logger.warn("message")  # mypy happy
```

**When to Use**:
- Optional dependencies with different APIs
- Backward compatibility layers
- Plugin systems with varying interfaces

---

## Pattern 6: .get() with Default for Optional Callables

**Problem**: dict.get() returns Callable | None, called without check

**Solution**: Use .get(key, default) pattern

```python
# ❌ BAD - None not callable
handler = level_map.get(level)
handler(message)  # mypy error: None not callable

# ✅ GOOD - provide default
handler = level_map.get(level, self.logger.info)
handler(message)  # mypy happy
```

---

## Mypy Configuration Best Practices

### For New Code (Strict)
```ini
[mypy]
disallow_untyped_defs = True
check_untyped_defs = True
warn_return_any = True
```

### For Legacy Code (Gradual)
```ini
[mypy]
disallow_untyped_defs = False
check_untyped_defs = False
warn_return_any = True  # Still warn about Any returns
```

---

## Quick Reference

| Situation | Pattern | Example |
|-----------|---------|---------|
| Import fallback | TYPE_CHECKING guard | Pattern 1 |
| Mixed-type dict | dict[str, Any] annotation | Pattern 2 |
| YAML/JSON load | isinstance() check | Pattern 3 |
| Dict/DB access | type: ignore[no-any-return] | Pattern 4 |
| Union narrowing | type: ignore[union-attr] | Pattern 5 |
| Optional callable | .get(key, default) | Pattern 6 |

---

## See Also

- [mypy.ini](../../mypy.ini) - Project mypy configuration
- [ruff.toml](../../ruff.toml) - Linting rules
- [LLMDOCS_EVOLVED_SPEC.md](../architecture/LLMDOCS_EVOLVED_SPEC.md) - Documentation standards

