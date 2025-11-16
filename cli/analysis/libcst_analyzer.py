"""Libcst-based code analysis for upstream/downstream tracking."""

from pathlib import Path
from typing import Any

import libcst as cst


class LibcstAnalyzer:
    """Analyze Python code using libcst (Concrete Syntax Tree)."""

    def __init__(self):
        """Initialize analyzer."""
        self.project_root = Path.cwd()

    def analyze_upstream_downstream(self, target: str) -> dict[str, Any]:
        """Analyze upstream/downstream dependencies for a symbol.

        Args:
            target: Format "filepath/SymbolName"

        Returns:
            Dict with success, symbol, file, upstream, downstream
        """
        import re

        try:
            parts = target.rsplit("/", 1)
            if len(parts) != 2:
                return {
                    "success": False,
                    "error": f"Invalid target format: {target}. Use: filepath/SymbolName",
                }

            filepath, symbol = parts
            file_path = self.project_root / filepath

            if not file_path.exists():
                return {"success": False, "error": f"File not found: {filepath}"}

            with open(file_path) as f:
                source = f.read()

            pattern = re.compile(r"^(?:def|class)\s+" + re.escape(symbol) + r"\b", re.MULTILINE)
            if not pattern.search(source):
                return {
                    "success": False,
                    "error": f"Symbol '{symbol}' not found in {filepath}",
                }

            upstream = self._extract_imports(source)
            downstream = self._find_dependents(filepath, symbol)

            return {
                "success": True,
                "symbol": symbol,
                "file": filepath,
                "upstream": upstream,
                "downstream": downstream,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _extract_imports(self, source: str) -> list[str]:
        """Extract import statements from source."""

        imports: list[str] = []
        for line in source.split("\n"):
            line = line.strip()
            if line.startswith("import ") or line.startswith("from "):
                imports.append(line)
        return imports

    def _find_dependents(self, filepath: str, symbol: str) -> list[str]:
        """Find files that depend on this symbol."""
        dependents: list[str] = []
        file_path = self.project_root / filepath
        module_name = filepath.replace("/", ".").replace(".py", "")

        for py_file in self.project_root.rglob("*.py"):
            if py_file == file_path:
                continue
            try:
                with open(py_file) as f:
                    content = f.read()
                if symbol in content and module_name in content:
                    rel_path = py_file.relative_to(self.project_root)
                    dependents.append(str(rel_path))
            except Exception:
                pass

        return dependents

    def find_usages(self, symbol: str, search_path: str = ".") -> dict[str, Any]:
        """Find all usages of a symbol in the codebase.

        Args:
            symbol: Symbol name to search for
            search_path: Path to search in (default: current directory)

        Returns:
            Dict with success, symbol, usages list
        """
        import re

        try:
            search_root = self.project_root / search_path
            if not search_root.exists():
                return {"success": False, "error": f"Path not found: {search_path}"}

            usages = []
            pattern = re.compile(r"\b" + re.escape(symbol) + r"\b")

            for py_file in search_root.rglob("*.py"):
                try:
                    with open(py_file) as f:
                        lines = f.readlines()

                    for line_num, line in enumerate(lines, 1):
                        if pattern.search(line):
                            rel_path = py_file.relative_to(self.project_root)
                            usages.append(
                                {
                                    "file": str(rel_path),
                                    "line": line_num,
                                    "context": line.strip(),
                                }
                            )
                except Exception:
                    pass

            return {
                "success": True,
                "symbol": symbol,
                "usages": usages,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def analyze_imports(self, filepath: str) -> dict[str, Any]:
        """Analyze imports in a Python file.

        Args:
            filepath: Path to Python file

        Returns:
            Dict with success, file, imports list
        """
        import re

        try:
            file_path = self.project_root / filepath
            if not file_path.exists():
                return {"success": False, "error": f"File not found: {filepath}"}

            with open(file_path) as f:
                lines = f.readlines()

            imports = []
            for line in lines:
                line = line.strip()
                if line.startswith("import "):
                    module = line.replace("import ", "").split(" as ")[0].strip()
                    imports.append({"type": "import", "module": module, "items": []})
                elif line.startswith("from "):
                    match = re.match(r"from\s+([\w.]+)\s+import\s+(.*)", line)
                    if match:
                        module = match.group(1)
                        items_str = match.group(2)
                        items = [item.split(" as ")[0].strip() for item in items_str.split(",")]
                        imports.append({"type": "from", "module": module, "items": items})

            return {
                "success": True,
                "file": filepath,
                "imports": imports,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}


class SymbolVisitor(cst.CSTVisitor):
    """Find symbol definition and its dependencies."""

    def __init__(self, symbol: str):
        """Initialize visitor."""
        self.symbol = symbol
        self.found = False
        self.upstream = []
        self.downstream = []

    def visit_ClassDef(self, node: cst.ClassDef) -> None:
        """Visit class definitions."""
        if node.name.value == self.symbol:
            self.found = True

    def visit_FunctionDef(self, node: cst.FunctionDef) -> None:
        """Visit function definitions."""
        if node.name.value == self.symbol:
            self.found = True


class UsageVisitor(cst.CSTVisitor):
    """Find usages of a symbol."""

    def __init__(self, symbol: str, source: str = ""):
        """Initialize visitor."""
        self.symbol = symbol
        self.usages = []
        self.source_lines = source.split("\n") if source else []
        self.current_line = 1

    def visit_Name(self, node: cst.Name) -> None:
        """Visit name references."""
        if node.value == self.symbol:
            pos = node.metadata.position if hasattr(node, "metadata") else None
            line = pos.start.line if pos else self.current_line
            context = (
                self.source_lines[line - 1].strip() if line <= len(self.source_lines) else f"Reference: {self.symbol}"
            )
            self.usages.append((line, context))


class ImportVisitor(cst.CSTVisitor):
    """Extract import statements."""

    def __init__(self):
        """Initialize visitor."""
        self.imports = []

    def visit_ImportFrom(self, node: cst.ImportFrom) -> None:
        """Visit from...import statements."""
        module = node.module
        if module:
            module_name = self._get_name(module)
            items = []
            if isinstance(node.names, cst.ImportStar):
                items = ["*"]
            elif isinstance(node.names, list | tuple):
                for name in node.names:
                    if isinstance(name, cst.ImportAlias):
                        items.append(name.name.value)

            self.imports.append({"type": "from", "module": module_name, "items": items})

    def visit_Import(self, node: cst.Import) -> None:
        """Visit import statements."""
        for name in node.names:
            if isinstance(name, cst.ImportAlias):
                self.imports.append({"type": "import", "module": name.name.value, "items": []})

    @staticmethod
    def _get_name(node: Any) -> str:
        """Extract name from node."""
        if isinstance(node, cst.Name):
            return node.value
        elif isinstance(node, cst.Attribute):
            return f"{LibcstAnalyzer._get_name(node.value)}.{node.attr.value}"
        return str(node)
