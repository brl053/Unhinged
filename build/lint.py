#!/usr/bin/env python3
"""
Unhinged Linter Dispatcher - Option C

Routes Python files to appropriate linters based on file type and location.
No external services. Complete control. On-premise only.

Usage:
    python /build/lint.py <file1> <file2> ...
"""

import sys
import subprocess
from pathlib import Path

# Venv-aware tool discovery
BUILD_DIR = Path(__file__).parent
VENV_BIN = BUILD_DIR / 'python' / 'venv' / 'bin'


def find_tool(name: str) -> str:
    """Find tool in venv first, fall back to system PATH."""
    venv_tool = VENV_BIN / name
    if venv_tool.exists():
        return str(venv_tool)
    return name  # Assume it's in PATH


def check_file_length(file_path: str) -> tuple[int, str | None]:
    """Check file line count. Returns (exit_code, message)."""
    try:
        with open(file_path) as f:
            line_count = sum(1 for _ in f)
    except Exception as e:
        return (0, None)  # Skip if can't read

    if line_count > 1000:
        return (1, f"❌ FATAL: {file_path} is {line_count} lines (limit: 1000)")
    elif line_count > 500:
        return (0, f"⚠️  WARNING: {file_path} is {line_count} lines (target: <500)")

    return (0, None)


def get_linter_config(file_path: str) -> dict:
    """Determine linter configuration based on file location and type."""
    path = Path(file_path)
    
    # Skip non-Python files
    if path.suffix != '.py':
        return {'skip': True, 'reason': 'Not a Python file'}
    
    # Skip generated files
    if 'proto' in path.parts or path.name.startswith('pb2_'):
        return {'skip': True, 'reason': 'Generated code'}
    
    # Skip test files (different rules)
    if 'test' in path.parts or path.name.startswith('test_'):
        return {
            'linters': ['ruff'],
            'ruff_args': ['--select', 'E,W,F', '--ignore', 'E501'],
            'type': 'test'
        }
    
    # Build infrastructure (stricter)
    if 'build' in path.parts:
        return {
            'linters': ['ruff'],
            'ruff_args': ['--select', 'E,W,F,C901'],
            'type': 'build'
        }

    # Default: standard Python code
    return {
        'linters': ['ruff'],
        'ruff_args': ['--select', 'E,W,F,C901'],
        'type': 'standard'
    }


def run_ruff(file_path: str, args: list) -> int:
    """Run ruff linter on file."""
    ruff_cmd = find_tool('ruff')
    cmd = [ruff_cmd, 'check', file_path] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout, end='')
    if result.stderr:
        print(result.stderr, end='', file=sys.stderr)
    
    return result.returncode


def lint_file(file_path: str) -> int:
    """Lint a single file. Returns 0 if OK, 1 if violations found."""
    config = get_linter_config(file_path)

    if config.get('skip'):
        return 0

    # Check file length FIRST (architectural constraint)
    length_exit_code, length_message = check_file_length(file_path)
    if length_message:
        print(length_message)
    if length_exit_code != 0:
        return length_exit_code  # Stop immediately on file too long

    exit_code = 0
    for linter in config.get('linters', []):
        if linter == 'ruff':
            args = config.get('ruff_args', [])
            code = run_ruff(file_path, args)
            exit_code = max(exit_code, code)

    return exit_code


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python /build/lint.py <file1> <file2> ...")
        sys.exit(1)
    
    files = sys.argv[1:]
    exit_code = 0
    
    for file_path in files:
        code = lint_file(file_path)
        exit_code = max(exit_code, code)
    
    sys.exit(exit_code)


if __name__ == '__main__':
    main()

