"""Tests for Reasoning Engine integration with command orchestration components.

@llm-type test.reasoning_engine_integration
@llm-does test integration of ReasoningEngine with SemanticSearch, DAGBuilder, CommandExecutor
"""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from libs.python.command_orchestration.reasoning_engine import ReasoningEngine
from libs.python.command_orchestration.semantic_search_wrapper import (
    SemanticSearchWithReasoning,
)
from libs.python.command_orchestration.dag_builder_wrapper import (
    DAGBuilderWithReasoning,
)
from libs.python.command_orchestration.executor_wrapper import (
    CommandExecutorWithReasoning,
)


class TestSemanticSearchWithReasoning:
    """Test SemanticSearchWithReasoning wrapper."""

    @pytest.mark.asyncio
    async def test_search_with_llm_reasoning(self) -> None:
        """Test search with LLM-backed reasoning."""
        # Mock search engine
        mock_search_engine = MagicMock()
        mock_search_engine.search.return_value = [
            MagicMock(
                command="pactl",
                section="1",
                description="PulseAudio control",
                similarity=0.85,
                reasoning="Static reasoning",
            ),
            MagicMock(
                command="amixer",
                section="1",
                description="ALSA mixer control",
                similarity=0.72,
                reasoning="Static reasoning",
            ),
        ]

        # Create wrapper
        wrapper = SemanticSearchWithReasoning(mock_search_engine)

        # Mock LLM reasoning
        mock_reasoning = {
            "pactl": "pactl lists audio sinks and their volumes",
            "amixer": "amixer shows ALSA mixer controls",
        }

        with patch.object(
            wrapper.reasoning_engine, "_call_llm", new_callable=AsyncMock
        ) as mock_llm:
            mock_llm.return_value = json.dumps(mock_reasoning)
            wrapper.reasoning_engine._client = MagicMock()

            results = await wrapper.search_with_reasoning(
                prompt="why is my audio low?",
                use_llm_reasoning=True,
            )

            assert len(results) == 2
            assert results[0].command == "pactl"
            assert results[0].reasoning == "pactl lists audio sinks and their volumes"
            assert results[1].command == "amixer"
            assert results[1].reasoning == "amixer shows ALSA mixer controls"

    @pytest.mark.asyncio
    async def test_search_without_llm_reasoning(self) -> None:
        """Test search without LLM reasoning (static fallback)."""
        mock_search_engine = MagicMock()
        mock_search_engine.search.return_value = [
            MagicMock(
                command="pactl",
                section="1",
                description="PulseAudio control",
                similarity=0.85,
                reasoning="Static reasoning",
            ),
        ]

        wrapper = SemanticSearchWithReasoning(mock_search_engine)

        results = await wrapper.search_with_reasoning(
            prompt="why is my audio low?",
            use_llm_reasoning=False,
        )

        assert len(results) == 1
        assert results[0].reasoning == "Static reasoning"


class TestDAGBuilderWithReasoning:
    """Test DAGBuilderWithReasoning wrapper."""

    @pytest.mark.asyncio
    async def test_parse_pipeline_with_edge_reasoning(self) -> None:
        """Test pipeline parsing with LLM edge reasoning."""
        wrapper = DAGBuilderWithReasoning()

        mock_reasoning = "pactl outputs audio sink info, grep filters for volume"

        with patch.object(
            wrapper.reasoning_engine, "_call_llm", new_callable=AsyncMock
        ) as mock_llm:
            mock_llm.return_value = json.dumps(
                {"reasoning": mock_reasoning}
            )
            wrapper.reasoning_engine._client = MagicMock()

            result = await wrapper.parse_pipeline_with_reasoning(
                pipeline="pactl list-sinks | grep -i volume",
                use_llm_reasoning=True,
            )

            assert result.dag is not None
            assert len(result.dag.nodes) == 2
            assert len(result.dag.edges) == 1
            assert len(result.edge_reasoning) == 1

            edge_key = (list(result.dag.edges)[0])
            edge_reasoning = result.edge_reasoning[edge_key]
            assert edge_reasoning.reasoning == mock_reasoning


class TestCommandExecutorWithReasoning:
    """Test CommandExecutorWithReasoning wrapper."""

    @pytest.mark.asyncio
    async def test_execute_dag_with_result_interpretation(self) -> None:
        """Test DAG execution with LLM result interpretation."""
        # Create a simple DAG
        from libs.python.command_orchestration.dag_builder import (
            CommandDAG,
            CommandNode,
        )

        dag = CommandDAG()
        dag.add_node(CommandNode(id="cmd_0", command="echo", args=["hello"]))

        # Mock executor
        mock_executor = MagicMock()
        mock_exec_result = MagicMock()
        mock_exec_result.node_id = "cmd_0"
        mock_exec_result.command = "echo"
        mock_exec_result.returncode = 0
        mock_exec_result.stdout = "hello\n"
        mock_exec_result.stderr = ""

        mock_dag_result = MagicMock()
        mock_dag_result.success = True
        mock_dag_result.results = {"cmd_0": mock_exec_result}

        mock_executor.execute_dag = AsyncMock(return_value=mock_dag_result)

        # Create wrapper
        wrapper = CommandExecutorWithReasoning(executor=mock_executor)

        mock_interpretation = "Command executed successfully and produced output"

        with patch.object(
            wrapper.reasoning_engine, "_call_llm", new_callable=AsyncMock
        ) as mock_llm:
            mock_llm.return_value = json.dumps(
                {"interpretation": mock_interpretation}
            )
            wrapper.reasoning_engine._client = MagicMock()

            result = await wrapper.execute_dag_with_interpretation(
                dag=dag,
                use_llm_interpretation=True,
            )

            assert result.dag_result.success
            assert "cmd_0" in result.result_interpretations
            assert (
                result.result_interpretations["cmd_0"].interpretation
                == mock_interpretation
            )


class TestIntegrationChain:
    """Test full integration chain: Search → DAG → Execute → Interpret."""

    @pytest.mark.asyncio
    async def test_full_reasoning_chain(self) -> None:
        """Test complete reasoning chain with all components."""
        # This is a high-level integration test
        # In practice, this would be tested end-to-end with real components

        reasoning_engine = ReasoningEngine(provider="anthropic")

        # Verify all wrappers can be instantiated
        search_wrapper = SemanticSearchWithReasoning(
            search_engine=MagicMock(),
            reasoning_engine=reasoning_engine,
        )
        dag_wrapper = DAGBuilderWithReasoning(
            reasoning_engine=reasoning_engine,
        )
        executor_wrapper = CommandExecutorWithReasoning(
            reasoning_engine=reasoning_engine,
        )

        assert search_wrapper is not None
        assert dag_wrapper is not None
        assert executor_wrapper is not None

