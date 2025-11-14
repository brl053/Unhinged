#!/usr/bin/env python3
"""
LLMDocs Validator

Validates Python files follow LLMDocs specification from /build/docs-generation.
Warns on all files, blocks on nothing (initial phase).

Usage:
    python /build/validators/llmdocs_validator.py <file1> <file2> ...
"""

import sys
import re
from pathlib import Path


def check_module_docstring(content: str, file_path: str) -> list:
    """Check for module-level docstring."""
    issues = []
    
    # Skip if file starts with shebang
    lines = content.split('\n')
    start_idx = 1 if lines[0].startswith('#!') else 0
    
    # Check if first non-comment line is a docstring
    for i in range(start_idx, min(start_idx + 5, len(lines))):
        line = lines[i].strip()
        if not line or line.startswith('#'):
            continue
        if not (line.startswith('"""') or line.startswith("'''")):
            issues.append(f"  ⚠️  Missing module docstring at top of file")
        break
    
    return issues


def check_function_docstrings(content: str, file_path: str) -> list:
    """Check for function docstrings on public functions."""
    issues = []
    
    # Find all function definitions
    func_pattern = r'^\s*def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        match = re.match(func_pattern, line)
        if not match:
            continue
        
        func_name = match.group(1)
        
        # Skip private functions
        if func_name.startswith('_'):
            continue
        
        # Check if next non-empty line is a docstring
        for j in range(i + 1, min(i + 3, len(lines))):
            next_line = lines[j].strip()
            if not next_line:
                continue
            if not (next_line.startswith('"""') or next_line.startswith("'''")):
                issues.append(f"  ⚠️  Function '{func_name}' missing docstring (line {i+1})")
            break
    
    return issues


def check_llmdocs_comments(content: str, file_path: str) -> list:
    """Check for LLMDocs comments on complex functions."""
    issues = []
    
    # Look for functions with high complexity (multiple branches)
    func_pattern = r'^\s*def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        match = re.match(func_pattern, line)
        if not match:
            continue
        
        func_name = match.group(1)
        if func_name.startswith('_'):
            continue
        
        # Count branches in function
        func_lines = []
        indent_level = len(line) - len(line.lstrip())
        
        for j in range(i + 1, len(lines)):
            if lines[j].strip() and not lines[j].startswith(' ' * (indent_level + 1)):
                break
            func_lines.append(lines[j])
        
        # Count if/for/while statements
        branches = sum(1 for l in func_lines if re.search(r'\b(if|for|while|try)\b', l))
        
        if branches > 3:
            # Check for LLMDocs comment
            has_llmdocs = any('# LLMDocs' in l or '# llmdocs' in l for l in func_lines[:5])
            if not has_llmdocs:
                issues.append(f"  ℹ️  Function '{func_name}' is complex ({branches} branches), consider LLMDocs comment")
    
    return issues


def validate_file(file_path: str) -> list:
    """Validate a single file. Returns list of issues."""
    path = Path(file_path)
    
    # Skip non-Python files
    if path.suffix != '.py':
        return []
    
    # Skip generated files
    if 'proto' in path.parts or path.name.startswith('pb2_'):
        return []
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
    except Exception as e:
        return [f"  ❌ Error reading file: {e}"]
    
    issues = []
    issues.extend(check_module_docstring(content, file_path))
    issues.extend(check_function_docstrings(content, file_path))
    issues.extend(check_llmdocs_comments(content, file_path))
    
    return issues


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python /build/validators/llmdocs_validator.py <file1> <file2> ...")
        sys.exit(0)
    
    files = sys.argv[1:]
    total_issues = 0
    
    for file_path in files:
        issues = validate_file(file_path)
        if issues:
            print(f"{file_path}:")
            for issue in issues:
                print(issue)
            total_issues += len(issues)
    
    # Informational only - never block
    if total_issues > 0:
        print(f"\n⚠️  Found {total_issues} documentation issues (informational only)")
    
    sys.exit(0)


if __name__ == '__main__':
    main()

