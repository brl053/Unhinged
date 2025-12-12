"""
@llm-type test.e2e.generation
@llm-does end-to-end tests for generation node pipeline flow

E2E Tests for Generation Nodes

These tests verify that generation nodes can be loaded from JSON graphs,
execute with template interpolation, and produce correct output structures.

Tests use mocked services to avoid GPU dependencies in CI.

Tests:
1. test_text_gen_graph_loads_and_executes - Text generation graph flow
2. test_image_gen_graph_loads_and_executes - Image generation graph flow
3. test_audio_gen_graph_loads_and_executes - Audio generation graph flow
4. test_video_gen_graph_loads_and_executes - Video generation graph flow
5. test_generation_with_session_context - Template interpolation from session
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from libs.python.graph import GraphExecutor, load_graph_from_json
from libs.python.graph.context import SessionContext


@pytest.fixture
def mock_text_service():
    """Mock TextGenerationService for testing."""
    with patch(
        "libs.python.clients.text_generation_service.TextGenerationService"
    ) as mock_class:
        service = MagicMock()
        service.generate.return_value = "Generated text about cats"
        mock_class.return_value = service
        yield mock_class


@pytest.fixture
def mock_image_service():
    """Mock ImageGenerationService for testing."""
    with patch(
        "libs.python.clients.image_generation_service.ImageGenerationService"
    ) as mock_class:
        service = MagicMock()
        service.generate_image.return_value = {
            "image_path": "/tmp/generated_image.png",
            "metadata": {"width": 512, "height": 512},
        }
        mock_class.return_value = service
        yield mock_class


@pytest.fixture
def mock_audio_service():
    """Mock TTSService for testing."""
    with patch("libs.python.clients.tts_service.TTSService") as mock_class:
        service = MagicMock()
        service.generate_voiceover.return_value = {
            "audio_path": "/tmp/generated_audio.mp3",
            "duration": 3.5,
        }
        mock_class.return_value = service
        yield mock_class


@pytest.fixture
def mock_video_service():
    """Mock VideoGenerationService for testing."""
    with patch(
        "libs.python.clients.video_generation_service.VideoGenerationService"
    ) as mock_class:
        service = MagicMock()
        service.generate_video.return_value = {
            "video_path": "/tmp/generated_video.mp4",
            "duration": 5.0,
        }
        mock_class.return_value = service
        yield mock_class


class TestGenerationGraphE2E:
    """E2E tests for generation graph loading and execution."""

    @pytest.mark.asyncio
    async def test_text_gen_graph_loads_and_executes(
        self, mock_text_service: MagicMock
    ) -> None:
        """Test text generation graph loads from JSON and executes."""
        graph = load_graph_from_json("examples/graphs/gen_text.json")
        executor = GraphExecutor()

        # initial_inputs maps node_id -> input dict
        initial_inputs = {"generate": {"input": {"topic": "cats"}}}
        result = await executor.execute(graph, initial_inputs=initial_inputs)

        assert result.success is True
        assert "generate" in result.node_results
        node_result = result.node_results["generate"]
        assert node_result.output["success"] is True
        assert node_result.output["text"] == "Generated text about cats"
        assert node_result.output["prompt"] == "cats"

    @pytest.mark.asyncio
    async def test_image_gen_graph_loads_and_executes(
        self, mock_image_service: MagicMock
    ) -> None:
        """Test image generation graph loads from JSON and executes."""
        graph = load_graph_from_json("examples/graphs/gen_image.json")
        executor = GraphExecutor()

        initial_inputs = {"generate": {"input": {"topic": "sunset"}}}
        result = await executor.execute(graph, initial_inputs=initial_inputs)

        assert result.success is True
        assert "generate" in result.node_results
        node_result = result.node_results["generate"]
        assert node_result.output["success"] is True
        assert node_result.output["file_path"] == "/tmp/generated_image.png"
        assert node_result.output["prompt"] == "sunset"

    @pytest.mark.asyncio
    async def test_audio_gen_graph_loads_and_executes(
        self, mock_audio_service: MagicMock
    ) -> None:
        """Test audio generation graph loads from JSON and executes."""
        graph = load_graph_from_json("examples/graphs/gen_audio.json")
        executor = GraphExecutor()

        initial_inputs = {"generate": {"input": {"topic": "Hello world"}}}
        result = await executor.execute(graph, initial_inputs=initial_inputs)

        assert result.success is True
        assert "generate" in result.node_results
        node_result = result.node_results["generate"]
        assert node_result.output["success"] is True
        assert node_result.output["file_path"] == "/tmp/generated_audio.mp3"
        assert node_result.output["duration"] == 3.5

    @pytest.mark.asyncio
    async def test_video_gen_graph_loads_and_executes(
        self, mock_video_service: MagicMock
    ) -> None:
        """Test video generation graph loads from JSON and executes."""
        graph = load_graph_from_json("examples/graphs/gen_video.json")
        executor = GraphExecutor()

        initial_inputs = {"generate": {"input": {"topic": "ocean waves"}}}
        result = await executor.execute(graph, initial_inputs=initial_inputs)

        assert result.success is True
        assert "generate" in result.node_results
        node_result = result.node_results["generate"]
        assert node_result.output["success"] is True
        assert node_result.output["file_path"] == "/tmp/generated_video.mp4"
        assert node_result.output["prompt"] == "ocean waves"

