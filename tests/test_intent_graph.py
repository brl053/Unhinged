"""Tests for the IntentAnalysisGraph used by `unhinged query`.

@llm-type test.query_planner.intent_graph
@llm-does unit tests for LLMIntentNode and intent analysis graph wiring
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

try:
    import libs  # type: ignore[import-not-found]
except ModuleNotFoundError:  # pragma: no cover - defensive path setup
    ROOT = Path(__file__).resolve().parents[1]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    import libs  # type: ignore[import-not-found]  # noqa: F401

from libs.python.graph import GraphExecutor
from libs.python.query_planner import (
    INTENT_NODE_ID,
    LLMIntentNode,
    build_intent_analysis_graph,
)


class TestLLMIntentNode:
    """Tests for LLM-backed intent classification."""

    @pytest.mark.asyncio
    async def test_classifies_headphone_volume_query(self) -> None:
        """Test that headphone volume queries are classified correctly."""
        node = LLMIntentNode(node_id=INTENT_NODE_ID, provider="anthropic")

        # Mock the LLM response
        mock_response = {
            "intent": "diagnose",
            "domain": "audio/headphone_volume",
            "confidence": 0.95,
            "reasoning": "User mentions headphones and low volume",
        }

        with patch.object(node, "_call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = json.dumps(mock_response)
            node._client = MagicMock()  # Prevent actual client loading

            query = "The headphone volume on my Logitech Pro X2 is too low"
            result = await node.execute({"stdin": query})

            assert result["success"] is True
            assert result["intent"] == "diagnose"
            assert result["domain"] == "audio/headphone_volume"
            assert result["confidence"] == 0.95
            assert "stdout" in result

    @pytest.mark.asyncio
    async def test_classifies_system_audio_query(self) -> None:
        """Test that system/browser audio queries are classified correctly."""
        node = LLMIntentNode(node_id=INTENT_NODE_ID, provider="anthropic")

        mock_response = {
            "intent": "diagnose",
            "domain": "audio/system_volume",
            "confidence": 0.92,
            "reasoning": "User mentions YouTube/browser audio is too low",
        }

        with patch.object(node, "_call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = json.dumps(mock_response)
            node._client = MagicMock()

            query = "why is my audio low from youtube and the browser? might be all apps idk"
            result = await node.execute({"stdin": query})

            assert result["success"] is True
            assert result["intent"] == "diagnose"
            assert result["domain"] == "audio/system_volume"
            assert result["confidence"] == 0.92

    @pytest.mark.asyncio
    async def test_unknown_query_returns_unknown_intent(self) -> None:
        """Test that unrelated queries return unknown intent."""
        node = LLMIntentNode(node_id=INTENT_NODE_ID, provider="anthropic")

        mock_response = {
            "intent": "unknown",
            "domain": "unknown",
            "confidence": 0.0,
            "reasoning": "Query does not match any known intent/domain",
        }

        with patch.object(node, "_call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = json.dumps(mock_response)
            node._client = MagicMock()

            query = "deploy my app to production"
            result = await node.execute({"stdin": query})

            assert result["success"] is True
            assert result["intent"] == "unknown"
            assert result["domain"] == "unknown"
            assert result["confidence"] == 0.0

    @pytest.mark.asyncio
    async def test_missing_stdin_returns_error(self) -> None:
        """Test that missing stdin returns error."""
        node = LLMIntentNode(node_id=INTENT_NODE_ID, provider="anthropic")

        result = await node.execute({})

        assert result["success"] is False
        assert result["intent"] == "unknown"
        assert "error" in result

    @pytest.mark.asyncio
    async def test_malformed_json_response_returns_error(self) -> None:
        """Test that malformed JSON response is handled gracefully."""
        node = LLMIntentNode(node_id=INTENT_NODE_ID, provider="anthropic")

        with patch.object(node, "_call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = "not valid json"
            node._client = MagicMock()

            result = await node.execute({"stdin": "test query"})

            assert result["success"] is False
            assert result["intent"] == "unknown"
            assert "json_parse_error" in result["reason"]


class TestIntentAnalysisGraph:
    """Tests for the LLM-backed intent analysis graph."""

    @pytest.mark.asyncio
    async def test_graph_execution_with_mocked_llm(self) -> None:
        """Test that the graph executes correctly with mocked LLM."""
        graph = build_intent_analysis_graph()
        executor = GraphExecutor()

        # Mock the LLM response
        mock_response = {
            "intent": "diagnose",
            "domain": "audio/headphone_volume",
            "confidence": 0.95,
            "reasoning": "Headphone volume issue",
        }

        with patch(
            "libs.python.query_planner.intent_graph.LLMIntentNode._call_llm",
            new_callable=AsyncMock,
        ) as mock_llm:
            mock_llm.return_value = json.dumps(mock_response)

            query = "My headphones are too quiet"
            result = await executor.execute(
                graph,
                initial_inputs={INTENT_NODE_ID: {"stdin": query}},
            )

            assert result.success is True
            node_output = result.node_results[INTENT_NODE_ID].output
            assert node_output["success"] is True
            assert node_output["intent"] == "diagnose"
            assert node_output["domain"] == "audio/headphone_volume"
