#!/usr/bin/env python3
"""
Lint summary report organized by directory and file.
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

def run_lint():
    """Run linter on all Python files."""
    result = subprocess.run(
        ['find', 'control', 'libs', '-name', '*.py', '-type', 'f'],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent
    )
    
    files = result.stdout.strip().split('\n')
    
    # Run lint on all files
    cmd = ['python3', 'build/lint.py'] + files
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent.parent)
    
    return result.stdout + result.stderr

def parse_violations(output):
    """Parse violations and group by file and directory."""
    violations = defaultdict(lambda: {'fatal': [], 'warning': []})

    for line in output.split('\n'):
        if not line.strip():
            continue

        # Extract file path from violation lines
        # Format: "❌ FATAL: path/to/file.py is X lines"
        # or "⚠️  Function 'name' in path/to/file.py is X lines"
        # or "❌ Line 123: nesting depth 6 in path/to/file.py"

        if '❌' in line or '⚠️' in line:
            # Try to extract filepath
            filepath = None

            # Look for patterns like "control/..." or "libs/..."
            for part in line.split():
                if part.startswith('control/') or part.startswith('libs/'):
                    filepath = part.rstrip(':,')
                    break

            # If not found, try to extract from the line
            if not filepath:
                import re
                match = re.search(r'(control/[^\s:]+|libs/[^\s:]+)', line)
                if match:
                    filepath = match.group(1)

            if filepath:
                if '❌' in line:
                    violations[filepath]['fatal'].append(line.strip())
                elif '⚠️' in line:
                    violations[filepath]['warning'].append(line.strip())

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
    
    total_fatal = sum(len(v['fatal']) for v in violations.values())
    total_warn = sum(len(v['warning']) for v in violations.values())
    
    # Print header
    print(f"\n{CYAN}═══════════════════════════════════════════════════════════{NC}")
    print(f"{CYAN}Lint Report Summary{NC}")
    print(f"{CYAN}═══════════════════════════════════════════════════════════{NC}\n")
    
    if total_fatal > 0:
        print(f"{RED}❌ FATAL: {total_fatal} violations{NC}")
    if total_warn > 0:
        print(f"{YELLOW}⚠️  WARNING: {total_warn} violations{NC}")
    if total_fatal == 0 and total_warn == 0:
        print(f"{GREEN}✅ All checks passed!{NC}")
        return
    
    print()
    
    # Print by directory
    for top_dir in sorted(by_dir.keys()):
        files = by_dir[top_dir]
        dir_fatal = sum(len(v['fatal']) for v in files.values())
        dir_warn = sum(len(v['warning']) for v in files.values())
        
        if dir_fatal == 0 and dir_warn == 0:
            continue
        
        print(f"{CYAN}📁 {top_dir}/{NC} ({dir_fatal} fatal, {dir_warn} warnings)")

        for filepath in sorted(files.keys()):
            issues = files[filepath]
            if not issues['fatal'] and not issues['warning']:
                continue

            # Show file with full path from repo root
            print(f"  📄 {filepath}")
            
            # Show violations
            if verbose:
                for violation in issues['fatal'][:5]:
                    print(f"    {violation}")
                if len(issues['fatal']) > 5:
                    print(f"    ... and {len(issues['fatal']) - 5} more fatal")
                
                for violation in issues['warning'][:3]:
                    print(f"    {violation}")
                if len(issues['warning']) > 3:
                    print(f"    ... and {len(issues['warning']) - 3} more warnings")
            else:
                if issues['fatal']:
                    print(f"    {RED}❌ {len(issues['fatal'])} fatal{NC}")
                if issues['warning']:
                    print(f"    {YELLOW}⚠️  {len(issues['warning'])} warnings{NC}")
        
        print()

if __name__ == '__main__':
    verbose = len(sys.argv) > 1 and sys.argv[1].lower() == 'true'

    output = run_lint()
    violations = parse_violations(output)
    print_summary(violations, verbose)

