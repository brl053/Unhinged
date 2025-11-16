#!/usr/bin/env python3
"""
Deterministic usage finder using AST.
Finds all references to a symbol in a Python file.
"""

import ast
import sys
from pathlib import Path
from typing import Any


class UsageAnalyzer(ast.NodeVisitor):
    """Find all usages of a specific name"""

    def __init__(self, target_name: str, source_lines: list[str]):
        self.target_name = target_name
        self.source_lines = source_lines
        self.usages: list[dict[str, Any]] = []

    def visit_Name(self, node: ast.Name) -> None:
        """Find direct name references"""
        if node.id == self.target_name:
            self.usages.append(
                {
                    "line": node.lineno,
                    "col": node.col_offset,
                    "type": "name_reference",
                    "context": node.ctx.__class__.__name__,
                    "code": self.source_lines[node.lineno - 1].strip(),
                }
            )
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        """Find attribute access (obj.method)"""
        if isinstance(node.value, ast.Name) and node.value.id == self.target_name:
            self.usages.append(
                {
                    "line": node.lineno,
                    "col": node.col_offset,
                    "type": "attribute_access",
                    "attribute": node.attr,
                    "code": self.source_lines[node.lineno - 1].strip(),
                }
            )
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        """Find imports"""
        for alias in node.names:
            if self.target_name in alias.name:
                self.usages.append(
                    {
                        "line": node.lineno,
                        "col": node.col_offset,
                        "type": "import",
                        "module": alias.name,
                        "code": self.source_lines[node.lineno - 1].strip(),
                    }
                )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Find from imports"""
        for alias in node.names:
            if alias.name == self.target_name or alias.name == "*":
                self.usages.append(
                    {
                        "line": node.lineno,
                        "col": node.col_offset,
                        "type": "from_import",
                        "module": node.module,
                        "name": alias.name,
                        "code": self.source_lines[node.lineno - 1].strip(),
                    }
                )
        self.generic_visit(node)


def find_usages(filepath: str, target_name: str) -> list[dict[str, Any]]:
    """Find all usages of a symbol in a file"""
    with open(filepath) as f:
        source = f.read()
        source_lines = source.split("\n")

    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        print(f"❌ Syntax error in {filepath}: {e}")
        return []

    analyzer = UsageAnalyzer(target_name, source_lines)
    analyzer.visit(tree)

    return analyzer.usages


def main():
    if len(sys.argv) < 3:
        print("Usage: python find_usages.py <filepath> <symbol_name>")
        print("Example: python find_usages.py build/modules/dual_system_builder.py BuildUtils")
        sys.exit(1)

    filepath = sys.argv[1]
    target_name = sys.argv[2]

    if not Path(filepath).exists():
        print(f"❌ File not found: {filepath}")
        sys.exit(1)

    usages = find_usages(filepath, target_name)

    if not usages:
        print(f"✅ No usages of '{target_name}' found in {filepath}")
        return

    print(f"\n📍 Found {len(usages)} usages of '{target_name}' in {filepath}\n")

    for i, usage in enumerate(usages, 1):
        print(f"{i}. Line {usage['line']}:{usage['col']} ({usage['type']})")
        print(f"   Code: {usage['code']}")
        if "attribute" in usage:
            print(f"   Attribute: {usage['attribute']}")
        print()


if __name__ == "__main__":
    main()
