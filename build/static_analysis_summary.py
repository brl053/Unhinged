#!/usr/bin/env python3
"""
Static analysis summary report with formatted output.
"""

import subprocess
import sys
from collections import defaultdict
from pathlib import Path

# Color codes
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
GREEN = '\033[0;32m'
CYAN = '\033[0;36m'
NC = '\033[0m'


def run_static_analysis():
    """Run ruff on all Python files and return output."""
    project_root = Path(__file__).parent.parent
    
    # Run ruff check on control and libs
    result = subprocess.run(
        [
            'build/python/venv/bin/ruff',
            'check',
            'control',
            'libs',
            '--output-format=concise'
        ],
        capture_output=True,
        text=True,
        cwd=project_root
    )
    
    return result.stdout + result.stderr, result.returncode


def parse_violations(output):
    """Parse ruff output and group by file."""
    violations = defaultdict(list)
    
    for line in output.split('\n'):
        if not line.strip():
            continue
            
        # Ruff concise format: path/to/file.py:line:col: CODE message
        parts = line.split(':', 3)
        if len(parts) >= 4:
            filepath = parts[0]
            line_num = parts[1]
            col = parts[2]
            rest = parts[3].strip()
            
            # Extract error code and message
            if ' ' in rest:
                code, message = rest.split(' ', 1)
                violations[filepath].append({
                    'line': line_num,
                    'col': col,
                    'code': code,
                    'message': message,
                    'full': line.strip()
                })
    
    return violations


def print_summary(violations, verbose=False):
    """Print organized summary."""
    # Group by top-level directory
    by_dir = defaultdict(dict)
    
    for filepath, issues in violations.items():
        parts = filepath.split('/')
        top_dir = parts[0] if parts else 'other'
        
        if top_dir not in by_dir:
            by_dir[top_dir] = {}
        by_dir[top_dir][filepath] = issues
    
    total_violations = sum(len(v) for v in violations.values())
    
    # Print header
    print(f"\n{CYAN}═══════════════════════════════════════════════════════════{NC}")
    print(f"{CYAN}Static Analysis Report (Ruff){NC}")
    print(f"{CYAN}═══════════════════════════════════════════════════════════{NC}\n")
    
    if total_violations > 0:
        print(f"{RED}❌ {total_violations} violations found{NC}")
    else:
        print(f"{GREEN}✅ All checks passed!{NC}")
        return 0
    
    print()
    
    # Print by directory
    for top_dir in sorted(by_dir.keys()):
        files = by_dir[top_dir]
        dir_violations = sum(len(v) for v in files.values())
        
        if dir_violations == 0:
            continue
        
        print(f"{CYAN}📁 {top_dir}/{NC} ({dir_violations} violations)")

        for filepath in sorted(files.keys()):
            issues = files[filepath]
            if not issues:
                continue

            # Show file with full path from repo root
            print(f"  📄 {filepath}")
            
            # Group by error code for summary
            by_code = defaultdict(list)
            for issue in issues:
                by_code[issue['code']].append(issue)
            
            if verbose:
                # Show all violations
                for code in sorted(by_code.keys()):
                    code_issues = by_code[code]
                    for issue in code_issues[:10]:  # Limit to 10 per code
                        print(f"    {RED}{code}{NC} Line {issue['line']}:{issue['col']} - {issue['message']}")
                    if len(code_issues) > 10:
                        print(f"    ... and {len(code_issues) - 10} more {code} violations")
            else:
                # Show summary by code
                for code in sorted(by_code.keys()):
                    count = len(by_code[code])
                    # Show first violation as example
                    example = by_code[code][0]
                    print(f"    {RED}{code}{NC} ({count}x) - {example['message']}")
                    print(f"       --> {filepath}:{example['line']}:{example['col']}")
        
        print()
    
    return 1


if __name__ == '__main__':
    verbose = len(sys.argv) > 1 and sys.argv[1].lower() == 'true'

    output, returncode = run_static_analysis()
    violations = parse_violations(output)
    exit_code = print_summary(violations, verbose)
    
    sys.exit(exit_code)

