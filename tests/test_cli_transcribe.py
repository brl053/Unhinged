"""Tests for unhinged transcribe audio CLI command."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from cli.commands.transcribe import audio


@pytest.fixture
def cli_runner():
    """Create CLI runner for testing."""
    return CliRunner()


@pytest.fixture
def mock_transcription_service():
    """Mock TranscriptionService."""
    with patch("cli.commands.transcribe.TranscriptionService") as mock:
        service_instance = MagicMock()
        service_instance.transcribe_audio.return_value = "Transcribed text"
        service_instance.transcribe_with_metadata.return_value = {
            "text": "Transcribed text",
            "language": "en",
            "segments": [],
            "duration": 10.5,
        }
        mock.return_value = service_instance
        yield mock


@pytest.fixture
def temp_audio_file():
    """Create a temporary audio file."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(b"fake audio data")
        temp_file = f.name
    yield temp_file
    Path(temp_file).unlink()


def test_transcribe_audio_basic(cli_runner, mock_transcription_service, temp_audio_file):
    """Test basic audio transcription."""
    result = cli_runner.invoke(audio, [temp_audio_file])

    assert result.exit_code == 0
    assert "Transcribed text" in result.output
    mock_transcription_service.assert_called_once_with(model_size="base")


def test_transcribe_audio_with_model(cli_runner, mock_transcription_service, temp_audio_file):
    """Test transcription with custom model."""
    result = cli_runner.invoke(audio, ["-m", "large", temp_audio_file])

    assert result.exit_code == 0
    mock_transcription_service.assert_called_once_with(model_size="large")


def test_transcribe_audio_with_output_file(
    cli_runner, mock_transcription_service, temp_audio_file
):
    """Test transcription with output file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        output_file = f.name

    try:
        result = cli_runner.invoke(audio, ["-o", output_file, temp_audio_file])

        assert result.exit_code == 0
        assert Path(output_file).read_text() == "Transcribed text"
    finally:
        Path(output_file).unlink()


def test_transcribe_audio_with_metadata(
    cli_runner, mock_transcription_service, temp_audio_file
):
    """Test transcription with metadata."""
    result = cli_runner.invoke(audio, ["--metadata", temp_audio_file])

    assert result.exit_code == 0
    mock_transcription_service.return_value.transcribe_with_metadata.assert_called_once()


def test_transcribe_audio_file_not_found(cli_runner, mock_transcription_service):
    """Test error when audio file not found."""
    result = cli_runner.invoke(audio, ["/nonexistent/file.wav"])

    # Click returns exit code 2 for validation errors (file not found)
    assert result.exit_code in (1, 2)
    assert "File not found" in result.output or "not found" in result.output or "does not exist" in result.output


def test_transcribe_audio_service_error(cli_runner, mock_transcription_service, temp_audio_file):
    """Test handling of service errors."""
    service_instance = mock_transcription_service.return_value
    service_instance.transcribe_audio.side_effect = RuntimeError("Whisper model failed")

    result = cli_runner.invoke(audio, [temp_audio_file])

    assert result.exit_code == 1
    assert "Transcription failed" in result.output


def test_transcribe_audio_model_choices(cli_runner, mock_transcription_service, temp_audio_file):
    """Test that only valid model sizes are accepted."""
    # Valid models should work
    for model in ["tiny", "base", "small", "medium", "large"]:
        result = cli_runner.invoke(audio, ["-m", model, temp_audio_file])
        assert result.exit_code == 0

    # Invalid model should fail
    result = cli_runner.invoke(audio, ["-m", "invalid", temp_audio_file])
    assert result.exit_code != 0

