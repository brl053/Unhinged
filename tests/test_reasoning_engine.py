"""Tests for Reasoning Engine.

@llm-type test.reasoning_engine
@llm-does test LLM-backed reasoning for command selection, DAG edges, and result interpretation
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from libs.python.command_orchestration import ExecutionTrace, ReasoningEngine


class TestReasoningEngine:
    """Tests for LLM-backed reasoning engine."""

    @pytest.mark.asyncio
    async def test_reason_command_selection(self) -> None:
        """Test command selection reasoning generation."""
        engine = ReasoningEngine(provider="anthropic")

        mock_response = {
            "pactl": "Lists audio sinks and their volume levels",
            "amixer": "Shows ALSA mixer controls for volume diagnostics",
        }

        with patch.object(engine, "_call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = json.dumps(mock_response)
            engine._client = MagicMock()

            result = await engine.reason_command_selection(
                query="why is my audio low?",
                commands=["pactl", "amixer"],
            )

            assert result == mock_response
            assert "pactl" in result
            assert "amixer" in result

    @pytest.mark.asyncio
    async def test_reason_command_selection_with_scores(self) -> None:
        """Test command selection reasoning with similarity scores."""
        engine = ReasoningEngine(provider="anthropic")

        mock_response = {
            "pactl": "Primary audio diagnostics tool",
        }

        with patch.object(engine, "_call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = json.dumps(mock_response)
            engine._client = MagicMock()

            result = await engine.reason_command_selection(
                query="audio volume issue",
                commands=["pactl"],
                similarity_scores=[0.95],
            )

            assert result == mock_response

    @pytest.mark.asyncio
    async def test_reason_dag_edge(self) -> None:
        """Test DAG edge reasoning generation."""
        engine = ReasoningEngine(provider="anthropic")

        mock_response = {
            "reasoning": "grep filters pactl output to show only volume-related lines"
        }

        with patch.object(engine, "_call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = json.dumps(mock_response)
            engine._client = MagicMock()

            result = await engine.reason_dag_edge(
                from_command="pactl list sinks",
                to_command="grep -i volume",
            )

            assert "grep filters" in result

    @pytest.mark.asyncio
    async def test_reason_execution_result_success(self) -> None:
        """Test execution result interpretation for successful command."""
        engine = ReasoningEngine(provider="anthropic")

        mock_response = {
            "interpretation": "PipeWire is running as the audio server"
        }

        with patch.object(engine, "_call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = json.dumps(mock_response)
            engine._client = MagicMock()

            result = await engine.reason_execution_result(
                command="ps aux | grep pipewire",
                exit_code=0,
                stdout="user 1234 0.5 0.2 123456 78901 ? Sl 10:00 0:01 /usr/bin/pipewire",
                stderr="",
            )

            assert "PipeWire" in result

    @pytest.mark.asyncio
    async def test_reason_execution_result_failure(self) -> None:
        """Test execution result interpretation for failed command."""
        engine = ReasoningEngine(provider="anthropic")

        mock_response = {
            "interpretation": "Command failed - audio server not responding"
        }

        with patch.object(engine, "_call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = json.dumps(mock_response)
            engine._client = MagicMock()

            result = await engine.reason_execution_result(
                command="pactl list sinks",
                exit_code=1,
                stdout="",
                stderr="Connection refused",
            )

            assert "failed" in result.lower()

    @pytest.mark.asyncio
    async def test_command_selection_reasoning_fallback(self) -> None:
        """Test fallback when LLM fails for command selection."""
        engine = ReasoningEngine(provider="anthropic")

        with patch.object(engine, "_call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.side_effect = Exception("LLM error")
            engine._client = MagicMock()

            result = await engine.reason_command_selection(
                query="test query",
                commands=["cmd1", "cmd2"],
            )

            # Should return fallback reasoning
            assert "cmd1" in result
            assert "cmd2" in result
            assert "diagnostics" in result["cmd1"].lower()

    @pytest.mark.asyncio
    async def test_dag_edge_reasoning_fallback(self) -> None:
        """Test fallback when LLM fails for DAG edge reasoning."""
        engine = ReasoningEngine(provider="anthropic")

        with patch.object(engine, "_call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.side_effect = Exception("LLM error")
            engine._client = MagicMock()

            result = await engine.reason_dag_edge(
                from_command="cmd1",
                to_command="cmd2",
            )

            # Should return fallback reasoning
            assert "cmd2" in result
            assert "cmd1" in result

    @pytest.mark.asyncio
    async def test_result_interpretation_fallback(self) -> None:
        """Test fallback when LLM fails for result interpretation."""
        engine = ReasoningEngine(provider="anthropic")

        with patch.object(engine, "_call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.side_effect = Exception("LLM error")
            engine._client = MagicMock()

            result = await engine.reason_execution_result(
                command="test",
                exit_code=0,
                stdout="output",
                stderr="",
            )

            # Should return fallback reasoning
            assert "succeeded" in result.lower()

    @pytest.mark.asyncio
    async def test_malformed_json_response_command_selection(self) -> None:
        """Test handling of malformed JSON in command selection."""
        engine = ReasoningEngine(provider="anthropic")

        with patch.object(engine, "_call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = "not valid json"
            engine._client = MagicMock()

            result = await engine.reason_command_selection(
                query="test",
                commands=["cmd1"],
            )

            # Should return fallback
            assert "cmd1" in result

    def test_load_client_anthropic(self) -> None:
        """Test loading Anthropic client."""
        engine = ReasoningEngine(provider="anthropic")
        with patch("anthropic.Anthropic"):
            client = engine._load_client()
            assert client is not None

    def test_load_client_openai(self) -> None:
        """Test loading OpenAI client."""
        engine = ReasoningEngine(provider="openai")
        with patch("openai.OpenAI"):
            client = engine._load_client()
            assert client is not None

    def test_load_client_ollama(self) -> None:
        """Test loading Ollama client."""
        engine = ReasoningEngine(provider="ollama")
        with patch("ollama.Client"):
            client = engine._load_client()
            assert client is not None

    def test_load_client_unknown_provider(self) -> None:
        """Test error handling for unknown provider."""
        engine = ReasoningEngine(provider="unknown")
        with pytest.raises(ValueError, match="Unknown provider"):
            engine._load_client()

    def test_execution_trace_dataclass(self) -> None:
        """Test ExecutionTrace dataclass creation."""
        trace = ExecutionTrace(
            query="test query",
            intent_reasoning="diagnose audio",
            command_selection_reasoning={"pactl": "audio diagnostics"},
            dag_edge_reasoning={("pactl", "grep"): "filter output"},
            execution_result_reasoning={"pactl": "audio server running"},
            summary="Audio server is running normally",
        )

        assert trace.query == "test query"
        assert trace.intent_reasoning == "diagnose audio"
        assert "pactl" in trace.command_selection_reasoning

