"""Tests for orchestrate CLI command with LLM reasoning.

@llm-type test.orchestrate_cli
@llm-does test orchestrate command with --explain flag
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from click.testing import CliRunner

from cli.commands.orchestrate import _orchestrate, solve


class TestOrchestrateCommand:
    """Test orchestrate CLI command."""

    def test_solve_command_basic(self) -> None:
        """Test basic solve command without reasoning."""
        runner = CliRunner()

        with patch("cli.commands.orchestrate._orchestrate", new_callable=AsyncMock) as mock_orch:
            mock_orch.return_value = {
                "prompt": "test query",
                "commands": ["echo", "cat"],
                "search_results": [
                    {
                        "command": "echo",
                        "similarity": 0.9,
                        "reasoning": "Outputs text",
                    },
                    {
                        "command": "cat",
                        "similarity": 0.8,
                        "reasoning": "Reads files",
                    },
                ],
                "execution_success": True,
                "execution_results": {
                    "cmd_0": {
                        "returncode": 0,
                        "stdout": "hello",
                        "stderr": "",
                    },
                    "cmd_1": {
                        "returncode": 0,
                        "stdout": "world",
                        "stderr": "",
                    },
                },
            }

            result = runner.invoke(solve, ["test query"])
            assert result.exit_code == 0
            assert "test query" in result.output
            assert "echo" in result.output

    def test_solve_command_with_explain_flag(self) -> None:
        """Test solve command with --explain flag."""
        runner = CliRunner()

        with patch("cli.commands.orchestrate._orchestrate", new_callable=AsyncMock) as mock_orch:
            mock_orch.return_value = {
                "prompt": "test query",
                "commands": ["echo"],
                "search_results": [
                    {
                        "command": "echo",
                        "similarity": 0.9,
                        "reasoning": "Outputs text",
                    },
                ],
                "execution_success": True,
                "execution_results": {
                    "cmd_0": {
                        "returncode": 0,
                        "stdout": "hello",
                        "stderr": "",
                    },
                },
                "reasoning": {
                    "command_selection": {
                        "echo": "echo command outputs text to stdout",
                    },
                    "result_interpretations": {
                        "cmd_0": "Command executed successfully and produced output",
                    },
                },
            }

            result = runner.invoke(solve, ["test query", "--explain"])
            assert result.exit_code == 0
            assert "LLM-Backed Reasoning" in result.output
            assert "Command Selection Reasoning" in result.output
            assert "Result Interpretations" in result.output

    def test_solve_command_json_output(self) -> None:
        """Test solve command with JSON output."""
        runner = CliRunner()

        with patch("cli.commands.orchestrate._orchestrate", new_callable=AsyncMock) as mock_orch:
            mock_orch.return_value = {
                "prompt": "test query",
                "commands": ["echo"],
                "search_results": [
                    {
                        "command": "echo",
                        "similarity": 0.9,
                        "reasoning": "Outputs text",
                    },
                ],
                "execution_success": True,
                "execution_results": {
                    "cmd_0": {
                        "returncode": 0,
                        "stdout": "hello",
                        "stderr": "",
                    },
                },
            }

            result = runner.invoke(solve, ["test query", "-o", "json"])
            assert result.exit_code == 0
            # Extract JSON from output (skip log messages and trailing text)
            import re

            json_match = re.search(r"\{.*\}", result.output, re.DOTALL)
            assert json_match is not None
            json_str = json_match.group(0)
            output = json.loads(json_str)
            assert output["prompt"] == "test query"
            assert output["commands"] == ["echo"]


class TestOrchestrateAsync:
    """Test async orchestration function."""

    @pytest.mark.asyncio
    async def test_orchestrate_without_reasoning(self) -> None:
        """Test orchestration without LLM reasoning."""
        with (
            patch("cli.commands.orchestrate.ManPageIndexer") as mock_indexer_class,
            patch("cli.commands.orchestrate.DocumentLoader") as mock_loader_class,
            patch("cli.commands.orchestrate.SemanticSearchEngine") as mock_search_class,
            patch("cli.commands.orchestrate.DAGBuilder") as mock_dag_class,
            patch("cli.commands.orchestrate.CommandExecutor") as mock_exec_class,
        ):
            # Setup mocks
            mock_indexer = MagicMock()
            mock_indexer.build_index.return_value = {}
            mock_indexer_class.return_value = mock_indexer

            mock_loader = MagicMock()
            mock_loader.combine_documents.return_value = None
            mock_loader_class.return_value = mock_loader

            mock_search = MagicMock()
            mock_search.search.return_value = [
                MagicMock(command="echo", similarity=0.9, reasoning="Outputs text"),
            ]
            mock_search_class.return_value = mock_search

            mock_dag = MagicMock()
            mock_dag.build_from_commands.return_value = MagicMock()
            mock_dag_class.return_value = mock_dag

            mock_exec = MagicMock()
            mock_exec.execute_dag = AsyncMock(
                return_value=MagicMock(
                    success=True,
                    results={
                        "cmd_0": MagicMock(
                            returncode=0,
                            stdout="hello",
                            stderr="",
                        ),
                    },
                )
            )
            mock_exec_class.return_value = mock_exec

            result = await _orchestrate("test query", limit=5, explain=False)

            assert result["prompt"] == "test query"
            assert result["commands"] == ["echo"]
            assert result["execution_success"] is True
            assert "reasoning" not in result

    @pytest.mark.asyncio
    async def test_orchestrate_with_reasoning(self) -> None:
        """Test orchestration with LLM reasoning."""
        with (
            patch("cli.commands.orchestrate.ManPageIndexer") as mock_indexer_class,
            patch("cli.commands.orchestrate.DocumentLoader") as mock_loader_class,
            patch("cli.commands.orchestrate.SemanticSearchEngine") as mock_search_class,
            patch("cli.commands.orchestrate.SemanticSearchWithReasoning") as mock_search_wrapper_class,
            patch("cli.commands.orchestrate.DAGBuilder") as mock_dag_class,
            patch("cli.commands.orchestrate.CommandExecutor") as mock_exec_class,
            patch("cli.commands.orchestrate.CommandExecutorWithReasoning") as mock_exec_wrapper_class,
        ):
            # Setup mocks
            mock_indexer = MagicMock()
            mock_indexer.build_index.return_value = {}
            mock_indexer_class.return_value = mock_indexer

            mock_loader = MagicMock()
            mock_loader.combine_documents.return_value = None
            mock_loader_class.return_value = mock_loader

            mock_search = MagicMock()
            mock_search_class.return_value = mock_search

            mock_search_wrapper = MagicMock()
            mock_search_wrapper.search_with_reasoning = AsyncMock(
                return_value=[
                    MagicMock(
                        command="echo",
                        similarity=0.9,
                        reasoning="LLM: echo outputs text",
                    ),
                ]
            )
            mock_search_wrapper_class.return_value = mock_search_wrapper

            mock_dag = MagicMock()
            mock_dag.build_from_commands.return_value = MagicMock()
            mock_dag_class.return_value = mock_dag

            mock_exec = MagicMock()
            mock_exec_class.return_value = mock_exec

            mock_exec_wrapper = MagicMock()
            mock_exec_wrapper.execute_dag_with_interpretation = AsyncMock(
                return_value=MagicMock(
                    dag_result=MagicMock(
                        success=True,
                        results={
                            "cmd_0": MagicMock(
                                returncode=0,
                                stdout="hello",
                                stderr="",
                            ),
                        },
                    ),
                    result_interpretations={
                        "cmd_0": MagicMock(
                            interpretation="Command executed successfully",
                        ),
                    },
                )
            )
            mock_exec_wrapper_class.return_value = mock_exec_wrapper

            result = await _orchestrate("test query", limit=5, explain=True)

            assert result["prompt"] == "test query"
            assert result["commands"] == ["echo"]
            assert result["execution_success"] is True
            assert "reasoning" in result
            assert "command_selection" in result["reasoning"]
            assert "result_interpretations" in result["reasoning"]
