#!/usr/bin/env python3
"""
@llm-type build.validator
@llm-does enforce quality gates with no SKIP capability and actionable guidance

This script REPLACES the ability to SKIP pre-commit hooks.
It runs all quality checks and provides actionable guidance for failures.

CRITICAL: This script CANNOT be bypassed. It is the gatekeeper for code quality.

Usage:
    python3 build/validators/enforce_quality_gates.py

Exit codes:
    0: All checks passed
    1: Quality gate failures (commit blocked)
    2: Critical error (script failure)
"""

import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CheckResult:
    """Result of a quality check."""

    name: str
    passed: bool
    output: str
    auto_fixable: bool
    fix_command: str | None


def run_check(name: str, command: list[str], auto_fixable: bool = False, fix_command: str | None = None) -> CheckResult:
    """Run a quality check and capture results."""
    print(f"\n{'='*80}")
    print(f"🔍 Running: {name}")
    print(f"{'='*80}\n")

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent.parent,
    )

    passed = result.returncode == 0
    output = result.stdout + result.stderr

    if passed:
        print(f"✅ {name} passed\n")
    else:
        print(f"❌ {name} failed\n")
        print(output)

    return CheckResult(
        name=name,
        passed=passed,
        output=output,
        auto_fixable=auto_fixable,
        fix_command=fix_command,
    )


def check_for_skip_attempt() -> bool:
    """Check if user is trying to SKIP pre-commit hooks."""
    skip_env = os.environ.get("SKIP", "")
    if skip_env:
        print("\n" + "="*80)
        print("🚫 SKIP DETECTED - THIS IS NOT ALLOWED")
        print("="*80)
        print(f"\nYou attempted to skip: {skip_env}")
        print("\nWHY THIS IS BLOCKED:")
        print("Pre-commit hooks enforce code quality. Skipping them creates technical debt.")
        print("\nWHAT TO DO INSTEAD:")
        print("1. Read the error messages below")
        print("2. Fix the issues (automated fixes available for many)")
        print("3. Commit again without SKIP")
        print("\nIf you believe a check is incorrect, discuss with the team.")
        print("Do NOT bypass quality gates.\n")
        return True
    return False


def main() -> int:
    """Run all quality gates with actionable guidance."""
    print("\n" + "="*80)
    print("🛡️  UNHINGED QUALITY GATE ENFORCEMENT")
    print("="*80)
    print("\nRunning all quality checks. This CANNOT be skipped.\n")

    # Check for SKIP attempt
    if check_for_skip_attempt():
        print("❌ Commit blocked due to SKIP attempt.\n")
        return 1

    # Run all checks
    checks = [
        run_check(
            "Unhinged Custom Linter",
            ["python3", "build/lint.py"],
            auto_fixable=False,
            fix_command=None,
        ),
        run_check(
            "LLMDocs Validator",
            ["python3", "build/validators/llmdocs_validator.py"],
            auto_fixable=False,
            fix_command=None,
        ),
        run_check(
            "Ruff Linter",
            ["ruff", "check", ".", "--fix"],
            auto_fixable=True,
            fix_command="ruff check . --fix",
        ),
        run_check(
            "Ruff Formatter",
            ["ruff", "format", "."],
            auto_fixable=True,
            fix_command="ruff format .",
        ),
        run_check(
            "MyPy Type Checker",
            ["mypy", ".", "--exclude", "generated/", "--exclude", "venv/", "--exclude", "build/"],
            auto_fixable=False,
            fix_command=None,
        ),
    ]

    # Analyze results
    failed_checks = [c for c in checks if not c.passed]
    auto_fixable_checks = [c for c in failed_checks if c.auto_fixable]
    manual_fix_checks = [c for c in failed_checks if not c.auto_fixable]

    # Print summary
    print("\n" + "="*80)
    print("📊 QUALITY GATE SUMMARY")
    print("="*80)
    print(f"\nTotal checks: {len(checks)}")
    print(f"Passed: {len(checks) - len(failed_checks)}")
    print(f"Failed: {len(failed_checks)}")
    print(f"  - Auto-fixable: {len(auto_fixable_checks)}")
    print(f"  - Manual fix required: {len(manual_fix_checks)}")

    if not failed_checks:
        print("\n✅ All quality gates passed! Commit allowed.\n")
        return 0

    # Provide actionable guidance
    print("\n" + "="*80)
    print("🔧 ACTIONABLE FIX GUIDANCE")
    print("="*80)

    if auto_fixable_checks:
        print("\n📦 AUTO-FIXABLE ISSUES:")
        print("Run these commands to automatically fix issues:\n")
        for check in auto_fixable_checks:
            if check.fix_command:
                print(f"  {check.fix_command}")
        print("\nThen commit again.")

    if manual_fix_checks:
        print("\n🛠️  MANUAL FIX REQUIRED:")
        print("These issues require manual intervention:\n")
        for check in manual_fix_checks:
            print(f"  - {check.name}")
        print("\nReview the error output above for specific guidance.")

    print("\n" + "="*80)
    print("❌ COMMIT BLOCKED - Fix issues above and try again")
    print("="*80)
    print("\nREMINDER: You CANNOT skip these checks.")
    print("Quality gates exist to prevent technical debt.\n")

    return 1


if __name__ == "__main__":
    sys.exit(main())

