#!/usr/bin/env python3
"""
@llm-type driver.git
@llm-does actionable pre-commit hook wrapper with mentorship and fix guidance

Wraps existing pre-commit hooks to provide:
1. Actionable fix instructions for each failure
2. Context on why each failure matters
3. Automated fix suggestions where available
4. Grouped output by fixability (auto-fix vs manual)
5. LLM-agent friendly structured output
"""

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class FixGuidance:
    """Guidance for fixing a specific error pattern."""

    error_pattern: str
    why_it_matters: str
    how_to_fix: str
    auto_fix_command: str | None
    learn_more_url: str | None


# Error pattern database with fix guidance
FIX_GUIDANCE_DB: dict[str, FixGuidance] = {
    "F821": FixGuidance(
        error_pattern="Undefined name",
        why_it_matters="Missing imports cause runtime errors. Type checkers catch this early.",
        how_to_fix="Add the missing import at the top of the file. For `Any`, add: from typing import Any",
        auto_fix_command="ruff check --fix {file}",
        learn_more_url="https://docs.python.org/3/library/typing.html",
    ),
    "F401": FixGuidance(
        error_pattern="Imported but unused",
        why_it_matters="Unused imports clutter code and slow down module loading.",
        how_to_fix="Remove the unused import or use it in the code.",
        auto_fix_command="ruff check --fix {file}",
        learn_more_url=None,
    ),
    "F841": FixGuidance(
        error_pattern="Local variable assigned but never used",
        why_it_matters="Unused variables indicate dead code or incomplete logic.",
        how_to_fix="Remove the variable or use it. If intentionally unused, prefix with underscore: _variable",
        auto_fix_command="ruff check --fix {file}",
        learn_more_url=None,
    ),
    "E501": FixGuidance(
        error_pattern="Line too long",
        why_it_matters="Long lines reduce readability. 120 char limit enforces clean code.",
        how_to_fix="Break the line into multiple lines. Use parentheses for implicit line continuation.",
        auto_fix_command="ruff format {file}",
        learn_more_url=None,
    ),
    "C901": FixGuidance(
        error_pattern="Function is too complex",
        why_it_matters="High complexity (>10 branches) makes code hard to test and maintain.",
        how_to_fix="Extract helper functions. Reduce nested if/else. Use early returns.",
        auto_fix_command=None,
        learn_more_url="https://en.wikipedia.org/wiki/Cyclomatic_complexity",
    ),
    "UP007": FixGuidance(
        error_pattern="Use X | Y for type annotations",
        why_it_matters="Modern Python 3.10+ syntax is cleaner. Optional[X] is deprecated.",
        how_to_fix="Replace Optional[X] with X | None. Replace Union[X, Y] with X | Y.",
        auto_fix_command="ruff check --fix --unsafe-fixes {file}",
        learn_more_url="https://peps.python.org/pep-0604/",
    ),
}


def parse_ruff_output(output: str) -> list[dict[str, Any]]:
    """Parse ruff output into structured errors."""
    errors = []
    lines = output.split("\n")

    for line in lines:
        if not line.strip() or line.startswith("Found"):
            continue

        # Parse: "file.py:line:col: CODE message"
        parts = line.split(":", 3)
        if len(parts) >= 4:
            file_path = parts[0].strip()
            line_num = parts[1].strip()
            col_num = parts[2].strip()
            rest = parts[3].strip()

            # Extract error code (e.g., "F821")
            code_parts = rest.split(" ", 1)
            if len(code_parts) >= 2:
                error_code = code_parts[0].strip()
                message = code_parts[1].strip()

                errors.append(
                    {
                        "file": file_path,
                        "line": line_num,
                        "col": col_num,
                        "code": error_code,
                        "message": message,
                    }
                )

    return errors


def format_actionable_error(error: dict[str, Any]) -> str:
    """Format error with actionable guidance."""
    code = error["code"]
    guidance = FIX_GUIDANCE_DB.get(code)

    output = f"\n{'='*80}\n"
    output += f"❌ ERROR: {error['message']}\n"
    output += f"   File: {error['file']}:{error['line']}:{error['col']}\n"
    output += f"   Code: {code}\n"

    if guidance:
        output += f"\n   WHY THIS MATTERS:\n"
        output += f"   {guidance.why_it_matters}\n"

        output += f"\n   HOW TO FIX:\n"
        output += f"   {guidance.how_to_fix}\n"

        if guidance.auto_fix_command:
            fix_cmd = guidance.auto_fix_command.format(file=error["file"])
            output += f"\n   AUTOMATED FIX AVAILABLE:\n"
            output += f"   Run: {fix_cmd}\n"

        if guidance.learn_more_url:
            output += f"\n   LEARN MORE:\n"
            output += f"   {guidance.learn_more_url}\n"
    else:
        output += f"\n   ⚠️  No automated guidance available for {code}\n"
        output += f"   Consult: https://docs.astral.sh/ruff/rules/{code}\n"

    output += f"{'='*80}\n"
    return output


def main() -> int:
    """Run pre-commit hooks with actionable output."""
    print("🔍 Running pre-commit hooks with actionable guidance...\n")

    # Run ruff check
    result = subprocess.run(
        ["ruff", "check", "."],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        print("✅ All checks passed!\n")
        return 0

    # Parse and format errors
    errors = parse_ruff_output(result.stdout + result.stderr)

    if not errors:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        return result.returncode

    print(f"Found {len(errors)} errors. Providing actionable guidance:\n")

    for error in errors:
        print(format_actionable_error(error))

    print(f"\n{'='*80}")
    print(f"SUMMARY: {len(errors)} errors found")
    print(f"{'='*80}\n")

    return 1


if __name__ == "__main__":
    sys.exit(main())

