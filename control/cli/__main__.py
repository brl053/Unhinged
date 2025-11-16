"""CLI entry point for python -m control.cli.

DEPRECATED: This module is kept for backward compatibility only.
All CLI code has been moved to /cli at the repository root.

Delegates to the consolidated CLI in /cli/core.
"""

from cli.core import cli

if __name__ == "__main__":
    cli()
