#!/usr/bin/env python3
"""
Unhinged Linter Dispatcher - Option C

Routes Python files to appropriate linters based on file type and location.
No external services. Complete control. On-premise only.

Usage:
    python /build/lint.py <file1> <file2> ...
"""

import sys
import re
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


def check_import_count(file_path: str) -> tuple[int, str | None]:
    """Check number of import statements. Returns (exit_code, message)."""
    try:
        with open(file_path) as f:
            lines = f.readlines()
    except Exception:
        return (0, None)

    import_count = 0
    for line in lines[:100]:  # Only check top of file
        if line.strip().startswith(('import ', 'from ')):
            import_count += 1

    if import_count > 20:
        return (1, f"❌ FATAL: {file_path} has {import_count} imports (limit: 20)")
    elif import_count > 15:
        return (0, f"⚠️  WARNING: {file_path} has {import_count} imports (target: <15)")

    return (0, None)


def check_wildcard_imports(file_path: str) -> tuple[int, list[str]]:
    """Detect wildcard imports. Returns (exit_code, messages)."""
    issues = []
    try:
        with open(file_path) as f:
            lines = f.readlines()
    except Exception:
        return (0, [])

    for i, line in enumerate(lines, 1):
        if re.search(r'^\s*from\s+\S+\s+import\s+\*', line):
            issues.append(f"❌ Line {i}: wildcard import (use explicit imports)")

    exit_code = 1 if issues else 0
    return (exit_code, issues)


def check_function_length(file_path: str) -> tuple[int, list[str]]:
    """Check function lengths. Returns (exit_code, messages)."""
    issues = []
    try:
        with open(file_path) as f:
            lines = f.readlines()
    except Exception:
        return (0, [])

    in_function = False
    func_name = None
    func_start = 0
    indent_level = 0

    for i, line in enumerate(lines, 1):
        # Detect function definition
        if match := re.match(r'^(\s*)def\s+([a-zA-Z_][a-zA-Z0-9_]*)', line):
            if in_function:
                # Previous function ended
                length = i - func_start
                if length > 100:
                    issues.append(f"❌ Function '{func_name}' is {length} lines (limit: 100)")
                elif length > 50:
                    issues.append(f"⚠️  Function '{func_name}' is {length} lines (target: <50)")

            in_function = True
            func_name = match.group(2)
            func_start = i
            indent_level = len(match.group(1))

        # Detect end of function (dedent or EOF)
        elif in_function and line.strip() and not line.startswith(' ' * (indent_level + 1)):
            length = i - func_start
            if length > 100:
                issues.append(f"❌ Function '{func_name}' is {length} lines (limit: 100)")
            elif length > 50:
                issues.append(f"⚠️  Function '{func_name}' is {length} lines (target: <50)")
            in_function = False

    # Check last function if file ends while in function
    if in_function:
        length = len(lines) - func_start + 1
        if length > 100:
            issues.append(f"❌ Function '{func_name}' is {length} lines (limit: 100)")
        elif length > 50:
            issues.append(f"⚠️  Function '{func_name}' is {length} lines (target: <50)")

    exit_code = 1 if any('❌' in msg for msg in issues) else 0
    return (exit_code, issues)


def check_nesting_depth(file_path: str) -> tuple[int, list[str]]:
    """Check indentation depth. Returns (exit_code, messages)."""
    issues = []
    try:
        with open(file_path) as f:
            lines = f.readlines()
    except Exception:
        return (0, [])

    for i, line in enumerate(lines, 1):
        if not line.strip():
            continue

        indent = len(line) - len(line.lstrip())
        depth = indent // 4

        if depth > 5:
            issues.append(f"❌ Line {i}: nesting depth {depth} (limit: 5)")
        elif depth > 4:
            issues.append(f"⚠️  Line {i}: nesting depth {depth} (target: <4)")

    exit_code = 1 if any('❌' in msg for msg in issues) else 0
    return (exit_code, issues)


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

    exit_code = 0

    # Check file length (architectural constraint)
    length_exit_code, length_message = check_file_length(file_path)
    if length_message:
        print(length_message)
    exit_code = max(exit_code, length_exit_code)

    # Check import count
    import_exit_code, import_message = check_import_count(file_path)
    if import_message:
        print(import_message)
    exit_code = max(exit_code, import_exit_code)

    # Check wildcard imports
    wildcard_exit_code, wildcard_messages = check_wildcard_imports(file_path)
    for msg in wildcard_messages:
        print(msg)
    exit_code = max(exit_code, wildcard_exit_code)

    # Check function length
    func_exit_code, func_messages = check_function_length(file_path)
    for msg in func_messages:
        print(msg)
    exit_code = max(exit_code, func_exit_code)

    # Check nesting depth
    nesting_exit_code, nesting_messages = check_nesting_depth(file_path)
    for msg in nesting_messages:
        print(msg)
    exit_code = max(exit_code, nesting_exit_code)

    # Run ruff linter
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

