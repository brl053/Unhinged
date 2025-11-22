#!/usr/bin/env python3
"""
Mypy static analysis summary report with formatted output.
"""

import subprocess
import sys
from collections import defaultdict
from pathlib import Path

# Color codes
RED = "\033[0;31m"
YELLOW = "\033[1;33m"
GREEN = "\033[0;32m"
CYAN = "\033[0;36m"
NC = "\033[0m"


def run_mypy_analysis():
    """Run mypy on all Python files and return output."""
    project_root = Path(__file__).parent.parent

    # Run mypy on control and libs
    result = subprocess.run(
        [
            "build/python/venv/bin/mypy",
            "--config-file=mypy.ini",
            "control",
            "libs",
        ],
        capture_output=True,
        text=True,
        cwd=project_root,
    )

    return result.stdout + result.stderr, result.returncode


def parse_mypy_output(output):
    """Parse mypy output into structured violations."""
    violations = defaultdict(list)

    for line in output.split("\n"):
        if not line.strip():
            continue

        # Mypy format: path/to/file.py:line: error: message
        # Only count actual errors, not notes
        if "error:" in line:
            # Split on first 3 colons: filepath:line: error/note: message
            parts = line.split(":", 3)
            if len(parts) >= 3:
                filepath = parts[0].strip()
                try:
                    line_num = int(parts[1].strip())
                    # parts[2] contains " error" or " note"
                    msg_type = "error" if "error" in parts[2] else "note"
                    message = parts[3].strip() if len(parts) > 3 else ""

                    violations[filepath].append(
                        {
                            "line": line_num,
                            "col": 0,  # Mypy doesn't output column in summary
                            "type": msg_type,
                            "message": message,
                            "full_line": line,
                        }
                    )
                except (ValueError, IndexError):
                    pass

    return violations


def print_summary(violations, verbose=False):
    """Print organized summary."""
    by_dir = defaultdict(dict)

    for filepath, issues in violations.items():
        parts = filepath.split("/")
        top_dir = parts[0] if parts else "other"

        if top_dir not in by_dir:
            by_dir[top_dir] = {}
        by_dir[top_dir][filepath] = issues

    total_violations = sum(len(v) for v in violations.values())

    # Print header
    print(f"\n{CYAN}═══════════════════════════════════════════════════════════{NC}")
    print(f"{CYAN}Static Analysis Report (Mypy Type Checking){NC}")
    print(f"{CYAN}═══════════════════════════════════════════════════════════{NC}\n")

    if total_violations > 0:
        print(f"{RED}❌ {total_violations} type errors found{NC}\n")

        for top_dir in sorted(by_dir.keys()):
            dir_violations = by_dir[top_dir]
            dir_total = sum(len(v) for v in dir_violations.values())
            print(f"📁 {top_dir}/ ({dir_total} errors)")

            for filepath in sorted(dir_violations.keys()):
                issues = dir_violations[filepath]
                print(f"  📄 {filepath}")

                for issue in issues[:5]:
                    error_marker = f"{RED}error{NC}" if issue["type"] == "error" else f"{YELLOW}note{NC}"
                    print(f"    {error_marker} Line {issue['line']}:{issue['col']} - {issue['message']}")

                if len(issues) > 5:
                    print(f"    ... and {len(issues) - 5} more errors")
            print()

        return 1
    else:
        print(f"{GREEN}✅ All type checks passed!{NC}\n")
        return 0


def main():
    """Main entry point."""
    verbose = sys.argv[1].lower() == "true" if len(sys.argv) > 1 else False

    output, returncode = run_mypy_analysis()
    violations = parse_mypy_output(output)

    exit_code = print_summary(violations, verbose)

    if verbose and output:
        print(f"\n{CYAN}Full Mypy Output:{NC}")
        print(output)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
