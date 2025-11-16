"""Development commands: dev, build, test, lint."""

import subprocess
import sys

import click

from cli.commands.analyze import analyze
from cli.utils import (
    get_python,
    log_info,
    log_success,
)


@click.group()
def dev():
    """Development commands: build, test, lint, static-analysis.

    Health Check Order:
      1. ./unhinged dev static-analysis  (mypy: type checking)
      2. ./unhinged dev test             (unit tests)
      3. ./unhinged dev lint             (architecture: size, complexity)

    All three must pass for project to be healthy.
    """
    pass


@dev.command()
def build():
    """Build project."""
    log_info("Building project...")
    result = subprocess.run(["make", "build"])
    return result.returncode


@dev.command()
@click.argument("pattern", required=False, default="")
def test(pattern):
    """Run tests (all or matching pattern)."""
    python_cmd = get_python()

    if not pattern:
        log_info("Running all tests...")
    else:
        log_info(f"Running tests matching: {pattern}")

    # Run individual test files
    result = subprocess.run(
        [python_cmd, "-m", "pytest", "control/gtk4_gui/tests/", "-v"] + (["-k", pattern] if pattern else [])
    )
    return result.returncode


@dev.command()
@click.option("-v", "--verbose", is_flag=True, help="Show all violations")
def lint(verbose):
    """Check code for linting violations."""
    python_cmd = get_python()

    log_info("Checking all Python files...")
    verbose_arg = "true" if verbose else "false"
    result = subprocess.run([python_cmd, "build/lint_summary.py", verbose_arg])
    return result.returncode


@dev.command()
@click.argument("file", required=False, default="")
def fix(file):
    """Auto-fix linting violations."""
    log_info("Auto-fixing violations...")

    if file:
        result = subprocess.run(["build/python/venv/bin/ruff", "check", "--fix", file])
    else:
        result = subprocess.run(
            [
                "build/python/venv/bin/ruff",
                "check",
                "--fix",
                "control/",
                "libs/",
                "--exclude",
                "build/python/venv",
            ]
        )

    if result.returncode == 0:
        log_success("Auto-fixed violations. Run 'lint' to verify.")

    return result.returncode


@dev.command()
@click.argument("file", required=False, default="")
def format(file):
    """Format code with ruff."""
    log_info("Formatting code...")

    if file:
        result = subprocess.run(["build/python/venv/bin/ruff", "format", file])
    else:
        result = subprocess.run(
            [
                "build/python/venv/bin/ruff",
                "format",
                "control/",
                "libs/",
                "--exclude",
                "build/python/venv",
            ]
        )

    if result.returncode == 0:
        log_success("Code formatted.")

    return result.returncode


@dev.command(name="static-analysis")
@click.option("-v", "--verbose", is_flag=True, help="Show all violations")
def static_analysis(verbose):
    """Run static analysis on all modules (mypy).

    Checks: type safety, type mismatches, None errors.
    Runs on all Python files in control/ and libs/.

    BLOCKING: Project is unhealthy if this fails.
    """
    python_cmd = get_python()

    log_info("Running static analysis (mypy type checking)...")
    verbose_arg = "true" if verbose else "false"
    result = subprocess.run([python_cmd, "build/mypy_analysis_summary.py", verbose_arg])
    sys.exit(result.returncode)


@dev.command()
def clean():
    """Clean development artifacts and caches."""
    log_info("Cleaning development artifacts...")
    result = subprocess.run(["make", "clean"])
    return result.returncode


# Add analyze subcommand group
dev.add_command(analyze)
