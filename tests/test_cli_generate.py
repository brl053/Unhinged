"""Tests for unhinged generate text CLI command."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from cli.commands.generate import text


@pytest.fixture
def cli_runner():
    """Create CLI runner for testing."""
    return CliRunner()


@pytest.fixture
def mock_text_generation_service():
    """Mock TextGenerationService."""
    with patch("cli.commands.generate.TextGenerationService") as mock:
        service_instance = MagicMock()
        service_instance.generate.return_value = "Generated text response"
        mock.return_value = service_instance
        yield mock


def test_generate_text_with_prompt_argument(cli_runner, mock_text_generation_service):
    """Test text generation with prompt as argument."""
    result = cli_runner.invoke(text, ["write a haiku"])

    assert result.exit_code == 0
    assert "Generated text response" in result.output
    mock_text_generation_service.assert_called_once_with(model="llama2", provider="ollama")


def test_generate_text_with_custom_model(cli_runner, mock_text_generation_service):
    """Test text generation with custom model."""
    result = cli_runner.invoke(text, ["-m", "mistral", "explain quantum computing"])

    assert result.exit_code == 0
    mock_text_generation_service.assert_called_once_with(model="mistral", provider="ollama")


def test_generate_text_with_custom_provider(cli_runner, mock_text_generation_service):
    """Test text generation with custom provider."""
    result = cli_runner.invoke(text, ["-p", "openai", "write a poem"])

    assert result.exit_code == 0
    mock_text_generation_service.assert_called_once_with(model="llama2", provider="openai")


def test_generate_text_with_custom_tokens(cli_runner, mock_text_generation_service):
    """Test text generation with custom token limit."""
    result = cli_runner.invoke(text, ["-t", "1024", "write a story"])

    assert result.exit_code == 0
    service_instance = mock_text_generation_service.return_value
    service_instance.generate.assert_called_once()
    call_kwargs = service_instance.generate.call_args[1]
    assert call_kwargs["max_tokens"] == 1024


def test_generate_text_with_temperature(cli_runner, mock_text_generation_service):
    """Test text generation with custom temperature."""
    result = cli_runner.invoke(text, ["--temperature", "0.5", "write something"])

    assert result.exit_code == 0
    service_instance = mock_text_generation_service.return_value
    call_kwargs = service_instance.generate.call_args[1]
    assert call_kwargs["temperature"] == 0.5


def test_generate_text_from_file(cli_runner, mock_text_generation_service):
    """Test text generation reading prompt from file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("write a haiku about the moon")
        temp_file = f.name

    try:
        result = cli_runner.invoke(text, ["-f", temp_file])
        assert result.exit_code == 0
        assert "Generated text response" in result.output
    finally:
        Path(temp_file).unlink()


def test_generate_text_from_stdin(cli_runner, mock_text_generation_service):
    """Test text generation reading prompt from stdin."""
    result = cli_runner.invoke(text, input="write a haiku\n")

    assert result.exit_code == 0
    assert "Generated text response" in result.output


def test_generate_text_no_prompt_error(cli_runner):
    """Test error when no prompt provided."""
    result = cli_runner.invoke(text, input="")

    assert result.exit_code == 1
    assert "No prompt provided" in result.output or "Prompt cannot be empty" in result.output


def test_generate_text_empty_prompt_error(cli_runner, mock_text_generation_service):
    """Test error when prompt is empty."""
    result = cli_runner.invoke(text, [""])

    assert result.exit_code == 1
    assert "Prompt cannot be empty" in result.output


def test_generate_text_service_error(cli_runner, mock_text_generation_service):
    """Test handling of service errors."""
    service_instance = mock_text_generation_service.return_value
    service_instance.generate.side_effect = RuntimeError("LLM service unavailable")

    result = cli_runner.invoke(text, ["write something"])

    assert result.exit_code == 1
    assert "Text generation failed" in result.output
