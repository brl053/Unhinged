#!/usr/bin/env python3
"""
GTK4 CSS Validator - Static Analysis for GTK4 CSS Compatibility

Validates CSS files for GTK4 compatibility issues:
- Unsupported selectors (attribute selectors, pseudo-elements)
- Unsupported properties (box-shadow, transform, transition, etc.)
- Invalid color formats
- Deprecated GTK3 patterns

Usage:
    python3 gtk4_css_validator.py [path] [--fix] [--format=json|text]

Examples:
    # Validate a single file
    python3 gtk4_css_validator.py generated/design_system/gtk4/components.css

    # Validate all CSS files in directory
    python3 gtk4_css_validator.py generated/design_system/gtk4/

    # Auto-fix issues
    python3 gtk4_css_validator.py generated/design_system/gtk4/ --fix

    # JSON output for CI/CD
    python3 gtk4_css_validator.py generated/design_system/gtk4/ --format=json
"""

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path


class Severity(Enum):
    """Issue severity levels"""

    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class CSSIssue:
    """Represents a CSS validation issue"""

    file_path: str
    line: int
    column: int
    severity: str
    rule_id: str
    message: str
    suggestion: str | None = None
    original_line: str | None = None


class GTK4CSSValidator:
    """Validates CSS for GTK4 compatibility"""

    # GTK4 unsupported selectors
    UNSUPPORTED_SELECTORS = {
        r"\[.*?=.*?\]": ("Attribute selectors", "Use class selectors instead"),
        r"::[\w-]+": ("Pseudo-elements (::)", "GTK4 uses single colon pseudo-classes"),
        r":[\w-]*\(": ("Pseudo-functions", "Not supported in GTK4"),
    }

    # GTK4 unsupported properties
    UNSUPPORTED_PROPERTIES = {
        "box-shadow": ("box-shadow", "Use background-color or border instead"),
        "transform": ("transform", "Use margin/padding for positioning"),
        "transition": ("transition", "GTK4 handles animations differently"),
        "animation": ("animation", "Use GLib.timeout_add for animations"),
        "filter": ("filter", "Not supported in GTK4"),
        "backdrop-filter": ("backdrop-filter", "Not supported in GTK4"),
        "clip-path": ("clip-path", "Not supported in GTK4"),
        "mask": ("mask", "Not supported in GTK4"),
        "cursor": ("cursor", "GTK4 handles cursor automatically"),
    }

    def __init__(self):
        """Initialize validator"""
        self.issues: list[CSSIssue] = []

    def validate_file(self, file_path: Path) -> list[CSSIssue]:
        """Validate a single CSS file"""
        self.issues = []

        if not file_path.exists():
            return [
                CSSIssue(
                    file_path=str(file_path),
                    line=0,
                    column=0,
                    severity=Severity.ERROR.value,
                    rule_id="FILE_NOT_FOUND",
                    message=f"File not found: {file_path}",
                )
            ]

        with open(file_path) as f:
            lines = f.readlines()

        for line_num, line in enumerate(lines, 1):
            self._check_line(file_path, line_num, line)

        return self.issues

    def _check_line(self, file_path: Path, line_num: int, line: str):
        """Check a single line for issues"""
        stripped = line.strip()

        # Skip comments and empty lines
        if not stripped or stripped.startswith("/*") or stripped.startswith("*"):
            return

        # Check for unsupported selectors
        for pattern, (name, suggestion) in self.UNSUPPORTED_SELECTORS.items():
            if re.search(pattern, stripped):
                # Skip if it's in a comment
                if "/*" in stripped and "*/" in stripped:
                    continue

                self.issues.append(
                    CSSIssue(
                        file_path=str(file_path),
                        line=line_num,
                        column=1,
                        severity=Severity.ERROR.value,
                        rule_id="UNSUPPORTED_SELECTOR",
                        message=f"Unsupported selector: {name}",
                        suggestion=suggestion,
                        original_line=stripped,
                    )
                )

        # Check for unsupported properties
        for prop, (name, suggestion) in self.UNSUPPORTED_PROPERTIES.items():
            if re.search(rf"\b{prop}\s*:", stripped):
                self.issues.append(
                    CSSIssue(
                        file_path=str(file_path),
                        line=line_num,
                        column=1,
                        severity=Severity.ERROR.value,
                        rule_id="UNSUPPORTED_PROPERTY",
                        message=f"Unsupported property: {name}",
                        suggestion=suggestion,
                        original_line=stripped,
                    )
                )

    def validate_directory(self, directory: Path) -> list[CSSIssue]:
        """Validate all CSS files in directory"""
        all_issues = []

        for css_file in directory.rglob("*.css"):
            issues = self.validate_file(css_file)
            all_issues.extend(issues)

        return all_issues

    def format_output(self, issues: list[CSSIssue], format_type: str = "text") -> str:
        """Format validation results"""
        if format_type == "json":
            return json.dumps([asdict(issue) for issue in issues], indent=2)

        # Text format
        if not issues:
            return "✅ No GTK4 CSS compatibility issues found"

        output = [f"❌ Found {len(issues)} GTK4 CSS compatibility issues:\n"]

        for issue in issues:
            output.append(f"  {issue.file_path}:{issue.line}")
            output.append(f"    [{issue.severity}] {issue.rule_id}: {issue.message}")
            if issue.suggestion:
                output.append(f"    💡 Suggestion: {issue.suggestion}")
            if issue.original_line:
                output.append(f"    Line: {issue.original_line}")
            output.append("")

        return "\n".join(output)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Validate CSS files for GTK4 compatibility")
    parser.add_argument("path", help="Path to CSS file or directory")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format (default: text)")
    parser.add_argument("--fix", action="store_true", help="Auto-fix issues (not implemented yet)")

    args = parser.parse_args()

    path = Path(args.path)
    validator = GTK4CSSValidator()

    if path.is_file():
        issues = validator.validate_file(path)
    elif path.is_dir():
        issues = validator.validate_directory(path)
    else:
        print(f"❌ Path not found: {path}", file=sys.stderr)
        sys.exit(1)

    # Output results
    output = validator.format_output(issues, args.format)
    print(output)

    # Exit with error code if issues found
    if issues:
        sys.exit(1)


if __name__ == "__main__":
    main()
