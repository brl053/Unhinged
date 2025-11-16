"""Tests for unhinged image generate CLI command."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from cli.commands.image import generate


@pytest.fixture
def cli_runner():
    """Create CLI runner for testing."""
    return CliRunner()


@pytest.fixture
def mock_image_generation_service():
    """Mock ImageGenerationService."""
    with patch("cli.commands.image.ImageGenerationService") as mock:
        service_instance = MagicMock()
        service_instance.generate_image.return_value = {
            "image_path": "/tmp/generated_image.png",
            "generation_time": 5.2,
            "prompt": "test prompt",
        }
        mock.return_value = service_instance
        yield mock


def test_image_generate_with_prompt(cli_runner, mock_image_generation_service):
    """Test image generation with prompt argument."""
    result = cli_runner.invoke(generate, ["a sunset over mountains"])

    assert result.exit_code == 0
    assert "Image generated" in result.output or "generated" in result.output.lower()


def test_image_generate_with_dimensions(cli_runner, mock_image_generation_service):
    """Test image generation with custom dimensions."""
    result = cli_runner.invoke(generate, ["-w", "768", "-h", "768", "a cat"])

    assert result.exit_code == 0
    service_instance = mock_image_generation_service.return_value
    call_kwargs = service_instance.generate_image.call_args[1]
    assert call_kwargs["width"] == 768
    assert call_kwargs["height"] == 768


def test_image_generate_with_steps(cli_runner, mock_image_generation_service):
    """Test image generation with custom inference steps."""
    result = cli_runner.invoke(generate, ["--steps", "30", "a dog"])

    assert result.exit_code == 0
    service_instance = mock_image_generation_service.return_value
    call_kwargs = service_instance.generate_image.call_args[1]
    assert call_kwargs["num_inference_steps"] == 30


def test_image_generate_with_guidance(cli_runner, mock_image_generation_service):
    """Test image generation with custom guidance scale."""
    result = cli_runner.invoke(generate, ["--guidance", "8.0", "a landscape"])

    assert result.exit_code == 0
    service_instance = mock_image_generation_service.return_value
    call_kwargs = service_instance.generate_image.call_args[1]
    assert call_kwargs["guidance_scale"] == 8.0


def test_image_generate_from_file(cli_runner, mock_image_generation_service):
    """Test image generation reading prompt from file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("a beautiful landscape")
        temp_file = f.name

    try:
        result = cli_runner.invoke(generate, ["-f", temp_file])
        assert result.exit_code == 0
    finally:
        Path(temp_file).unlink()


def test_image_generate_from_stdin(cli_runner, mock_image_generation_service):
    """Test image generation reading prompt from stdin."""
    result = cli_runner.invoke(generate, input="a portrait\n")

    assert result.exit_code == 0


def test_image_generate_no_prompt_error(cli_runner):
    """Test error when no prompt provided."""
    result = cli_runner.invoke(generate, input="")

    assert result.exit_code == 1
    assert "Prompt cannot be empty" in result.output


def test_image_generate_service_error(cli_runner, mock_image_generation_service):
    """Test handling of service errors."""
    service_instance = mock_image_generation_service.return_value
    service_instance.generate_image.side_effect = RuntimeError("GPU out of memory")

    result = cli_runner.invoke(generate, ["a test image"])

    assert result.exit_code == 1
    assert "Image generation failed" in result.output
