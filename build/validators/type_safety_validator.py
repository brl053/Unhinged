#!/usr/bin/env python3
"""
@llm-type util.validator
@llm-purpose Validate type safety patterns from TYPE_SAFETY_GUIDE.md

Automated validation of type safety patterns learned from 179 mypy fixes.
Prevents regression to anti-patterns.
"""

import ast
import sys
from pathlib import Path
from typing import Any


class TypeSafetyValidator(ast.NodeVisitor):
    """Validate type safety patterns in Python code."""

    def __init__(self, filename: str):
        self.filename = filename
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.in_type_checking = False

    def visit_If(self, node: ast.If) -> None:
        """Track TYPE_CHECKING blocks."""
        # Check if this is: if TYPE_CHECKING:
        if isinstance(node.test, ast.Name) and node.test.id == "TYPE_CHECKING":
            self.in_type_checking = True
            self.generic_visit(node)
            self.in_type_checking = False
        else:
            self.generic_visit(node)

    def visit_Try(self, node: ast.Try) -> None:
        """Detect try/except ImportError without TYPE_CHECKING guard."""
        # Check if this is try/except ImportError pattern
        has_import_error = any(
            isinstance(handler.type, ast.Name) and handler.type.id == "ImportError"
            for handler in node.handlers
            if handler.type
        )

        if has_import_error:
            # Check if there's a class definition in except block
            for handler in node.handlers:
                for stmt in handler.body:
                    if isinstance(stmt, ast.ClassDef):
                        self.warnings.append(
                            f"{self.filename}:{node.lineno}: "
                            "Consider using TYPE_CHECKING guard for import fallback pattern. "
                            "See docs/development/TYPE_SAFETY_GUIDE.md Pattern 1"
                        )
                        break

        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        """Check for dict literals without explicit type annotation."""
        # Check if value is a dict literal
        if isinstance(node.value, ast.Dict):
            # Check if annotation is missing or not explicit
            if not node.annotation:
                self.warnings.append(
                    f"{self.filename}:{node.lineno}: "
                    "Dict literal without type annotation. "
                    "Consider: var: dict[str, Any] = {...}. "
                    "See docs/development/TYPE_SAFETY_GUIDE.md Pattern 2"
                )

        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """Check for yaml.safe_load() without type guard."""
        # Check if this is yaml.safe_load() or json.loads()
        if isinstance(node.func, ast.Attribute):
            if (
                isinstance(node.func.value, ast.Name)
                and node.func.value.id in ("yaml", "json")
                and node.func.attr in ("safe_load", "load", "loads")
            ):
                # This is a heuristic - we can't easily check if there's a type guard
                # Just warn if it's a direct return
                parent = getattr(node, "parent", None)
                if isinstance(parent, ast.Return):
                    self.warnings.append(
                        f"{self.filename}:{node.lineno}: "
                        "YAML/JSON load in return statement. "
                        "Consider adding type guard with isinstance(). "
                        "See docs/development/TYPE_SAFETY_GUIDE.md Pattern 3"
                    )

        self.generic_visit(node)


def validate_file(filepath: Path) -> tuple[list[str], list[str]]:
    """
    Validate type safety patterns in a Python file.

    Returns:
        (errors, warnings) tuple
    """
    try:
        with open(filepath, encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(filepath))

        validator = TypeSafetyValidator(str(filepath))
        validator.visit(tree)

        return validator.errors, validator.warnings

    except SyntaxError as e:
        return [f"{filepath}:{e.lineno}: Syntax error: {e.msg}"], []
    except Exception as e:
        return [f"{filepath}: Validation error: {e}"], []


def main() -> int:
    """Run type safety validation on provided files."""
    if len(sys.argv) < 2:
        print("Usage: type_safety_validator.py <file1.py> [file2.py ...]")
        return 1

    all_errors: list[str] = []
    all_warnings: list[str] = []

    for filepath_str in sys.argv[1:]:
        filepath = Path(filepath_str)
        if not filepath.exists() or filepath.suffix != ".py":
            continue

        errors, warnings = validate_file(filepath)
        all_errors.extend(errors)
        all_warnings.extend(warnings)

    # Print results
    if all_warnings:
        print("\n⚠️  Type Safety Warnings:")
        for warning in all_warnings:
            print(f"  {warning}")
        print(f"\n💡 See docs/development/TYPE_SAFETY_GUIDE.md for patterns")

    if all_errors:
        print("\n❌ Type Safety Errors:")
        for error in all_errors:
            print(f"  {error}")
        print(f"\n💡 Fix errors or use 'git commit --no-verify' for emergencies")
        return 1

    # BLOCKING: Treat warnings as errors for strict enforcement
    if all_warnings:
        print(f"\n❌ Commit blocked: {len(all_warnings)} type safety violations")
        print("💡 Fix violations or use 'git commit --no-verify' for emergencies")
        return 1

    print("✅ Type safety validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())

