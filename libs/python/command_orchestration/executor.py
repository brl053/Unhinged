"""
Command Executor - Re-exported from scription.

This module provides backward compatibility by re-exporting from the canonical
location in /scription/orchestration/lib/command_orchestration.
"""

import sys
from pathlib import Path

# Add scription to path for imports
scription_path = Path(__file__).parent.parent.parent.parent / "scription" / "orchestration" / "lib"
if str(scription_path) not in sys.path:
    sys.path.insert(0, str(scription_path))

from command_orchestration.executor import CommandExecutor, ExecutionResult, DAGExecutionResult

__all__ = ["CommandExecutor", "ExecutionResult", "DAGExecutionResult"]
