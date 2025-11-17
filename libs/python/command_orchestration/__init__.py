"""
Command Orchestration - Re-exported from scription.

This module provides backward compatibility by re-exporting from the canonical
location in /scription/orchestration/lib/command_orchestration.
"""

import sys
from pathlib import Path

# Add scription to path for imports
scription_path = Path(__file__).parent.parent.parent.parent / "scription" / "orchestration" / "lib"
if str(scription_path) not in sys.path:
    sys.path.insert(0, str(scription_path))

# Also expose submodules for direct imports
from command_orchestration import dag_builder, document_loader, executor, man_page_indexer, semantic_search
from command_orchestration.dag_builder import CommandDAG, CommandNode, DAGBuilder
from command_orchestration.document_loader import DocumentLoader
from command_orchestration.executor import CommandExecutor
from command_orchestration.man_page_indexer import ManPageEntry, ManPageIndexer
from command_orchestration.semantic_search import SearchResult, SemanticSearchEngine

# Import reasoning engine from local module
from libs.python.command_orchestration.reasoning_engine import ExecutionTrace, ReasoningEngine

# Import wrappers for integration with existing components
from libs.python.command_orchestration.semantic_search_wrapper import (
    SemanticSearchWithReasoning,
)
from libs.python.command_orchestration.dag_builder_wrapper import (
    DAGBuilderWithReasoning,
    DAGEdgeReasoning,
    CommandDAGWithReasoning,
)
from libs.python.command_orchestration.executor_wrapper import (
    CommandExecutorWithReasoning,
    ExecutionResultWithInterpretation,
    DAGExecutionResultWithInterpretation,
)

__all__ = [
    "ManPageIndexer",
    "ManPageEntry",
    "SemanticSearchEngine",
    "SearchResult",
    "DAGBuilder",
    "CommandDAG",
    "CommandNode",
    "CommandExecutor",
    "DocumentLoader",
    "ReasoningEngine",
    "ExecutionTrace",
    "SemanticSearchWithReasoning",
    "DAGBuilderWithReasoning",
    "DAGEdgeReasoning",
    "CommandDAGWithReasoning",
    "CommandExecutorWithReasoning",
    "ExecutionResultWithInterpretation",
    "DAGExecutionResultWithInterpretation",
    "dag_builder",
    "document_loader",
    "executor",
    "man_page_indexer",
    "semantic_search",
]
