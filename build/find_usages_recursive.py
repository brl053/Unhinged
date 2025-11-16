#!/usr/bin/env python3
"""
Recursive usage finder - searches entire codebase for symbol usages.
"""

import ast
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


class UsageAnalyzer(ast.NodeVisitor):
    """Find all usages of a specific name"""

    def __init__(self, target_name: str, source_lines: list[str]):
        self.target_name = target_name
        self.source_lines = source_lines
        self.usages: list[dict[str, Any]] = []

    def visit_Name(self, node: ast.Name) -> None:
        if node.id == self.target_name:
            self.usages.append(
                {
                    "line": node.lineno,
                    "col": node.col_offset,
                    "type": "name_reference",
                    "code": self.source_lines[node.lineno - 1].strip() if node.lineno <= len(self.source_lines) else "",
                }
            )
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if isinstance(node.value, ast.Name) and node.value.id == self.target_name:
            self.usages.append(
                {
                    "line": node.lineno,
                    "col": node.col_offset,
                    "type": "attribute_access",
                    "attribute": node.attr,
                    "code": self.source_lines[node.lineno - 1].strip() if node.lineno <= len(self.source_lines) else "",
                }
            )
        self.generic_visit(node)


def find_usages_in_file(filepath: str, target_name: str) -> list[dict[str, Any]]:
    """Find usages in a single file"""
    try:
        with open(filepath) as f:
            source = f.read()
            source_lines = source.split("\n")
        tree = ast.parse(source)
    except (SyntaxError, UnicodeDecodeError):
        return []

    analyzer = UsageAnalyzer(target_name, source_lines)
    analyzer.visit(tree)
    return analyzer.usages


def find_usages_recursive(root_dir: str, target_name: str, exclude_dirs: set[str] = None) -> dict[str, list[dict]]:
    """Find usages across entire codebase"""
    if exclude_dirs is None:
        exclude_dirs = {"venv", ".venv", "__pycache__", ".git", "build/python"}

    results = defaultdict(list)
    root = Path(root_dir)

    for py_file in root.rglob("*.py"):
        # Skip excluded directories
        if any(excluded in py_file.parts for excluded in exclude_dirs):
            continue

        usages = find_usages_in_file(str(py_file), target_name)
        if usages:
            results[str(py_file.relative_to(root))] = usages

    return dict(results)


def main():
    if len(sys.argv) < 2:
        print("Usage: python find_usages_recursive.py <symbol_name> [root_dir]")
        print("Example: python find_usages_recursive.py BuildUtils")
        sys.exit(1)

    target_name = sys.argv[1]
    root_dir = sys.argv[2] if len(sys.argv) > 2 else "."

    print(f"🔍 Searching for '{target_name}' in {root_dir}...\n")

    results = find_usages_recursive(root_dir, target_name)

    if not results:
        print(f"✅ No usages of '{target_name}' found")
        return

    total_usages = sum(len(usages) for usages in results.values())
    print(f"📊 Found {total_usages} usages in {len(results)} files\n")

    for filepath in sorted(results.keys()):
        usages = results[filepath]
        print(f"📄 {filepath} ({len(usages)} usages)")
        for usage in usages[:3]:  # Show first 3
            print(f"   Line {usage['line']}: {usage['code'][:60]}")
        if len(usages) > 3:
            print(f"   ... and {len(usages) - 3} more")
        print()


if __name__ == "__main__":
    main()
