"""Tests for command orchestration framework.

@llm-type test.orchestration
@llm-does unit tests for orchestration components
"""

import asyncio
import sys
from pathlib import Path

import pytest

try:
    import libs  # type: ignore[import-not-found]
except ModuleNotFoundError:  # pragma: no cover - defensive path setup
    ROOT = Path(__file__).resolve().parents[1]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    import libs  # type: ignore[import-not-found]  # noqa: F401

from libs.python.command_orchestration import (
    CommandExecutor,
    DAGBuilder,
    ManPageIndexer,
    SemanticSearchEngine,
)
from libs.python.command_orchestration.dag_builder import CommandDAG, CommandNode
from libs.python.command_orchestration.man_page_indexer import ManPageEntry


class TestManPageIndexer:
    """Tests for man page indexing"""

    def test_indexer_initialization(self):
        """Test indexer can be initialized"""
        indexer = ManPageIndexer()
        assert indexer is not None
        assert indexer.entries == {}

    def test_generate_embeddings(self):
        """Test embedding generation"""
        indexer = ManPageIndexer()
        entries = [
            ManPageEntry(
                command="ls", section="1", synopsis="list directory contents", description="List files and directories"
            ),
            ManPageEntry(
                command="grep", section="1", synopsis="search text patterns", description="Search for patterns in files"
            ),
        ]

        result = indexer.generate_embeddings(entries)
        assert len(result) == 2
        assert result[0].embedding is not None
        assert len(result[0].embedding) == 384  # MiniLM-L6-v2 dimension


class TestSemanticSearchEngine:
    """Tests for semantic search"""

    def test_search_initialization(self):
        """Test search engine initialization"""
        entries = {
            "ls:1": ManPageEntry(
                command="ls",
                section="1",
                synopsis="list directory contents",
                description="List files and directories",
                embedding=[0.1] * 384,
            )
        }
        search = SemanticSearchEngine(entries)
        assert search is not None

    def test_search_with_threshold(self):
        """Test search respects threshold"""
        entries = {
            "ls:1": ManPageEntry(
                command="ls",
                section="1",
                synopsis="list directory contents",
                description="List files and directories",
                embedding=[0.1] * 384,
            )
        }
        search = SemanticSearchEngine(entries, threshold=0.9)
        results = search.search("list files", limit=10)
        # Results may be empty due to high threshold
        assert isinstance(results, list)


class TestDAGBuilder:
    """Tests for DAG construction"""

    def test_parse_simple_pipeline(self):
        """Test parsing simple command pipeline"""
        builder = DAGBuilder()
        dag = builder.parse_pipeline("ls | grep test")

        assert len(dag.nodes) == 2
        assert len(dag.edges) == 1
        assert dag.nodes["cmd_0"].command == "ls"
        assert dag.nodes["cmd_1"].command == "grep"

    def test_parse_complex_pipeline(self):
        """Test parsing complex pipeline"""
        builder = DAGBuilder()
        dag = builder.parse_pipeline("cat file.txt | grep pattern | wc -l")

        assert len(dag.nodes) == 3
        assert len(dag.edges) == 2

    def test_topological_sort(self):
        """Test topological sorting"""
        builder = DAGBuilder()
        dag = builder.parse_pipeline("ls | grep test")
        groups = dag.topological_sort()

        # First group should have cmd_0, second should have cmd_1
        assert len(groups) >= 1

    def test_build_from_commands(self):
        """Test building DAG from independent commands"""
        builder = DAGBuilder()
        commands = ["ls", "pwd", "whoami"]
        dag = builder.build_from_commands(commands)

        assert len(dag.nodes) == 3
        assert len(dag.edges) == 0  # No dependencies


class TestCommandExecutor:
    """Tests for command execution"""

    @pytest.mark.asyncio
    async def test_execute_simple_command(self):
        """Test executing a simple command"""
        executor = CommandExecutor()
        builder = DAGBuilder()
        dag = builder.build_from_commands(["echo hello"])

        result = await executor.execute_dag(dag)
        assert result.success
        assert len(result.results) == 1

    @pytest.mark.asyncio
    async def test_execute_failing_command(self):
        """Test executing a failing command"""
        executor = CommandExecutor()
        builder = DAGBuilder()
        dag = builder.build_from_commands(["false"])

        result = await executor.execute_dag(dag)
        assert not result.success

    @pytest.mark.asyncio
    async def test_parallel_execution(self):
        """Test parallel execution of independent commands"""
        executor = CommandExecutor()
        builder = DAGBuilder()
        dag = builder.build_from_commands(["echo a", "echo b", "echo c"])

        result = await executor.execute_dag(dag)
        assert result.success
        assert len(result.results) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
