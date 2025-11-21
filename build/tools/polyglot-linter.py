#!/usr/bin/env python3
"""
Polyglot Linter - LLM-Biased Code Analysis Tool

A comprehensive linting tool that analyzes multiple programming languages
with special focus on LLM-friendly patterns and conventions.

Usage:
    python3 polyglot-linter.py [path] [--llm] [--format=json|text] [--languages=py,js,ts,kt,c]

Features:
- Multi-language support (Python, TypeScript, JavaScript, Kotlin, C/C++)
- LLM-biased analysis (readability, documentation, naming conventions)
- Rationale output for LLM training and understanding
- Integration with build system for CI/CD
"""

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path


class Severity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class LintIssue:
    file_path: str
    line: int
    column: int
    severity: Severity
    rule_id: str
    message: str
    rationale: str | None = None
    suggestion: str | None = None
    llm_context: str | None = None


class PolyglotLinter:
    """Main linter class supporting multiple programming languages."""

    def __init__(self, include_llm_rationale: bool = False):
        self.include_llm_rationale = include_llm_rationale
        self.issues: list[LintIssue] = []

        # Language-specific patterns
        self.language_patterns = {
            "python": {
                "extensions": [".py"],
                "rules": self._get_python_rules(),
            },
            "typescript": {
                "extensions": [".ts", ".tsx"],
                "rules": self._get_typescript_rules(),
            },
            "javascript": {
                "extensions": [".js", ".jsx"],
                "rules": self._get_javascript_rules(),
            },
            "kotlin": {
                "extensions": [".kt", ".kts"],
                "rules": self._get_kotlin_rules(),
            },
            "c": {
                "extensions": [".c", ".cpp", ".cc", ".cxx", ".h", ".hpp"],
                "rules": self._get_c_rules(),
            },
        }

    def _get_python_rules(self) -> list[dict]:
        """Python-specific linting rules with LLM bias."""
        return [
            {
                "id": "PY001",
                "pattern": r"^def\s+[a-z_][a-z0-9_]*\([^)]*\):\s*$",
                "severity": Severity.WARNING,
                "message": "Function missing docstring",
                "rationale": "LLMs benefit from clear function documentation to understand intent and usage patterns.",
                "check": lambda line, next_lines: not any(
                    line.strip().startswith('"""') or line.strip().startswith("'''") for line in next_lines[:3]
                ),
            },
            {
                "id": "PY002",
                "pattern": r"^\s*#\s*TODO\s*:",
                "severity": Severity.INFO,
                "message": "TODO comment found",
                "rationale": "TODO comments indicate incomplete work that LLMs should be aware of for context.",
                "suggestion": "Consider creating a GitHub issue for tracking",
            },
            {
                "id": "PY003",
                "pattern": r"^\s*print\s*\(",
                "severity": Severity.WARNING,
                "message": "Print statement in production code",
                "rationale": "Print statements should be replaced with proper logging for LLM-readable execution traces.",
                "suggestion": "Use logging.info() or logging.debug() instead",
            },
        ]

    def _get_typescript_rules(self) -> list[dict]:
        """TypeScript-specific linting rules with LLM bias."""
        return [
            {
                "id": "TS001",
                "pattern": r"function\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\([^)]*\)\s*{",
                "severity": Severity.WARNING,
                "message": "Function missing JSDoc comment",
                "rationale": "JSDoc comments help LLMs understand function contracts and expected behavior.",
                "suggestion": "Add /** @description */ comment above function",
            },
            {
                "id": "TS002",
                "pattern": r":\s*any\s*[,;=)]",
                "severity": Severity.ERROR,
                "message": 'Avoid using "any" type',
                "rationale": "Specific types provide better context for LLMs to understand data flow and constraints.",
                "suggestion": "Use specific types or union types instead",
            },
        ]

    def _get_javascript_rules(self) -> list[dict]:
        """JavaScript-specific linting rules."""
        return [
            {
                "id": "JS001",
                "pattern": r"console\.log\s*\(",
                "severity": Severity.WARNING,
                "message": "Console.log in production code",
                "rationale": "Console statements should be replaced with structured logging for better LLM analysis.",
                "suggestion": "Use a proper logging library",
            }
        ]

    def _get_kotlin_rules(self) -> list[dict]:
        """Kotlin-specific linting rules."""
        return [
            {
                "id": "KT001",
                "pattern": r"fun\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\([^)]*\)\s*{",
                "severity": Severity.WARNING,
                "message": "Function missing KDoc comment",
                "rationale": "KDoc comments provide essential context for LLMs analyzing Kotlin code patterns.",
                "suggestion": "Add /** */ comment above function",
            }
        ]

    def _get_c_rules(self) -> list[dict]:
        """C/C++ specific linting rules."""
        return [
            {
                "id": "C001",
                "pattern": r"^\s*//\s*TODO\s*:",
                "severity": Severity.INFO,
                "message": "TODO comment found",
                "rationale": "TODO comments in C code indicate areas needing attention for LLM context.",
                "suggestion": "Document the required work or create an issue",
            }
        ]

    def lint_file(self, file_path: Path) -> list[LintIssue]:
        """Lint a single file based on its extension."""
        issues = []

        # Determine language
        language = self._detect_language(file_path)
        if not language:
            return issues

        try:
            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()
        except (OSError, UnicodeDecodeError):
            return issues

        rules = self.language_patterns[language]["rules"]

        for line_num, line in enumerate(lines, 1):
            for rule in rules:
                if re.search(rule["pattern"], line):
                    # Additional check if rule has custom validation
                    if "check" in rule:
                        next_lines = lines[line_num : line_num + 5] if line_num < len(lines) else []
                        if not rule["check"](line, next_lines):
                            continue

                    issue = LintIssue(
                        file_path=str(file_path),
                        line=line_num,
                        column=1,
                        severity=rule["severity"],
                        rule_id=rule["id"],
                        message=rule["message"],
                        rationale=rule.get("rationale") if self.include_llm_rationale else None,
                        suggestion=rule.get("suggestion"),
                        llm_context=f"Language: {language}, Pattern: {rule['pattern']}"
                        if self.include_llm_rationale
                        else None,
                    )
                    issues.append(issue)

        return issues

    def _detect_language(self, file_path: Path) -> str | None:
        """Detect programming language from file extension."""
        suffix = file_path.suffix.lower()

        for language, config in self.language_patterns.items():
            if suffix in config["extensions"]:
                return language

        return None

    def lint_directory(self, directory: Path, languages: list[str] | None = None) -> list[LintIssue]:
        """Recursively lint all files in a directory."""
        all_issues = []

        # Filter languages if specified
        active_languages = languages or list(self.language_patterns.keys())

        for root, dirs, files in os.walk(directory):
            # Skip common ignore directories
            dirs[:] = [d for d in dirs if d not in {".git", "node_modules", "__pycache__", "venv", "build", "dist"}]

            for file in files:
                file_path = Path(root) / file
                language = self._detect_language(file_path)

                if language and language in active_languages:
                    issues = self.lint_file(file_path)
                    all_issues.extend(issues)

        return all_issues

    def format_output(self, issues: list[LintIssue], format_type: str = "text") -> str:
        """Format linting results for output."""
        if format_type == "json":
            return json.dumps([asdict(issue) for issue in issues], indent=2, default=str)

        # Text format
        output = []
        output.append(f"🔍 Polyglot Linter Results - {len(issues)} issues found\n")

        if not issues:
            output.append("✅ No issues found!")
            return "\n".join(output)

        # Group by severity
        by_severity = {}
        for issue in issues:
            severity = issue.severity.value
            if severity not in by_severity:
                by_severity[severity] = []
            by_severity[severity].append(issue)

        for severity in ["critical", "error", "warning", "info"]:
            if severity in by_severity:
                output.append(f"\n{severity.upper()} ({len(by_severity[severity])} issues):")
                output.append("=" * 50)

                for issue in by_severity[severity]:
                    output.append(f"📁 {issue.file_path}:{issue.line}:{issue.column}")
                    output.append(f"   {issue.rule_id}: {issue.message}")

                    if issue.suggestion:
                        output.append(f"   💡 Suggestion: {issue.suggestion}")

                    if self.include_llm_rationale and issue.rationale:
                        output.append(f"   🤖 LLM Rationale: {issue.rationale}")

                    if self.include_llm_rationale and issue.llm_context:
                        output.append(f"   🔍 Context: {issue.llm_context}")

                    output.append("")

        return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description="Polyglot Linter - LLM-Biased Code Analysis")
    parser.add_argument("path", nargs="?", default=".", help="Path to lint (file or directory)")
    parser.add_argument("--llm", action="store_true", help="Include LLM-specific rationale and context")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    parser.add_argument("--languages", help="Comma-separated list of languages to check (py,js,ts,kt,c)")

    args = parser.parse_args()

    # Parse languages
    languages = None
    if args.languages:
        languages = [lang.strip() for lang in args.languages.split(",")]

    # Initialize linter
    linter = PolyglotLinter(include_llm_rationale=args.llm)

    # Lint path
    path = Path(args.path)
    if path.is_file():
        issues = linter.lint_file(path)
    elif path.is_dir():
        issues = linter.lint_directory(path, languages)
    else:
        print(f"❌ Path not found: {path}", file=sys.stderr)
        sys.exit(1)

    # Output results
    output = linter.format_output(issues, args.format)
    print(output)

    # Exit with error code if critical/error issues found
    critical_errors = [i for i in issues if i.severity in {Severity.CRITICAL, Severity.ERROR}]
    if critical_errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
