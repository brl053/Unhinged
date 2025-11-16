# LibCST vs Custom AST: Comparison

## Quick Comparison

| Feature | Custom AST | LibCST | Mypy | Ruff |
|---------|-----------|--------|------|------|
| **Usage Finding** | ✅ Yes | ✅ Yes | ❌ No | ❌ No |
| **Upstream/Downstream** | ⚠️ Basic | ✅ Full | ❌ No | ❌ No |
| **Preserves Formatting** | ❌ No | ✅ Yes | ❌ No | ✅ Yes |
| **Refactoring Support** | ❌ No | ✅ Yes | ❌ No | ✅ Yes |
| **Type Awareness** | ❌ No | ⚠️ Limited | ✅ Full | ❌ No |
| **External Dependency** | ❌ No | ✅ Yes | ✅ Yes | ✅ Yes |
| **Performance** | ✅ Fast | ⚠️ Medium | ❌ Slow | ✅ Fast |
| **Industry Use** | ❌ Rare | ✅ Meta, Google | ✅ Everywhere | ✅ Everywhere |

---

## Custom AST (Current Implementation)

### Pros
- No external dependencies
- Fast for simple queries
- Good for learning
- Sufficient for basic usage tracking

### Cons
- Loses formatting/comments
- No refactoring support
- Limited semantic analysis
- Doesn't scale to complex queries
- Not suitable for production tools

### Example: Find usages of `BuildUtils`
```python
import ast

class UsageAnalyzer(ast.NodeVisitor):
    def visit_Name(self, node):
        if node.id == 'BuildUtils':
            print(f"Line {node.lineno}: {node.id}")
```

**Output:**
```
Line 80: BuildUtils
Line 104: BuildUtils
Line 236: BuildUtils
```

**Problem:** Doesn't track method calls, attributes, or refactoring context.

---

## LibCST (Recommended for Production)

### Pros
- Preserves formatting/comments (concrete syntax tree)
- Full refactoring support
- Semantic analysis capabilities
- Used by Ruff, Meta, Google
- Scales to complex queries
- Better for upstream/downstream tracking

### Cons
- External dependency (libcst)
- Slightly slower than raw AST
- Steeper learning curve

### Example: Find usages + refactoring context
```python
import libcst as cst

class UsageFinder(cst.CSTVisitor):
    def visit_Name(self, node: cst.Name) -> None:
        if node.value == 'BuildUtils':
            # Can access parent context, formatting, etc.
            print(f"Found: {node.value}")
    
    def visit_Call(self, node: cst.Call) -> None:
        # Can track method calls
        if isinstance(node.func, cst.Attribute):
            if isinstance(node.func.value, cst.Name):
                if node.func.value.value == 'BuildUtils':
                    print(f"Method call: {node.func.attr.value}")
```

**Output:**
```
Found: BuildUtils
Method call: calculate_directory_hash
Method call: check_tool_available
Method call: create_build_artifact
```

**Benefit:** Can track method calls, refactor safely, preserve formatting.

---

## Upstream/Downstream Tracking

### What It Means
- **Upstream**: What calls this symbol?
- **Downstream**: What does this symbol call?

### Example
```python
# File: build/modules/dual_system_builder.py

class DualSystemBuilder:
    def build(self):
        self.validate_environment()  # Downstream: calls validate_environment
        BuildUtils.create_build_artifact(...)  # Downstream: calls BuildUtils

# File: build/modules/__init__.py
builder = DualSystemBuilder()  # Upstream: creates DualSystemBuilder
```

### LibCST Approach
```python
# Find all classes that inherit from DualSystemBuilder (upstream)
# Find all methods called by DualSystemBuilder.build() (downstream)
# Find all files that import DualSystemBuilder (upstream)
```

### Custom AST Limitation
- Can find direct references
- Cannot track inheritance chains
- Cannot resolve imports across files
- Cannot track method resolution order

---

## Recommendation

### Use Custom AST If:
- Simple, one-off queries
- No external dependencies allowed
- Performance critical
- Learning/prototyping

### Use LibCST If:
- Production code analysis tool
- Need refactoring support
- Need upstream/downstream tracking
- Need to preserve formatting
- Building IDE-like features

---

## Implementation Path

### Phase 1: Prototype with Custom AST
```bash
python build/find_usages.py build/modules/dual_system_builder.py BuildUtils
```
✅ Works, proves concept

### Phase 2: Migrate to LibCST
```bash
./unhinged dev analyze usages BuildUtils
./unhinged dev analyze upstream-downstream build/modules/dual_system_builder.py/DualSystemBuilder
```
✅ Production-ready, scalable

### Phase 3: Integrate with IDE
- Language Server Protocol (LSP) support
- Real-time analysis in VS Code
- Refactoring suggestions

---

## Installation

```bash
# Add to requirements
pip install libcst>=0.4.0

# Verify
python -c "import libcst; print(libcst.__version__)"
```

---

## Conclusion

**For Unhinged's needs:**
- **Now**: Keep custom AST for reference
- **Next**: Migrate to LibCST for production
- **Future**: Build IDE integration on top of LibCST

LibCST is the industry standard for Python code analysis and refactoring.

