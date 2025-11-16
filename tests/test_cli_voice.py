"""Tests for unhinged voice generate CLI command."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from cli.commands.voice import generate


@pytest.fixture
def cli_runner():
    """Create CLI runner for testing."""
    return CliRunner()


@pytest.fixture
def mock_tts_service():
    """Mock TTSService."""
    with patch("cli.commands.voice.TTSService") as mock:
        service_instance = MagicMock()
        service_instance.generate_voiceover.return_value = {
            "audio_path": "/tmp/generated_audio.mp3",
            "duration": 3.5,
            "voice": "nova",
        }
        mock.return_value = service_instance
        yield mock


def test_voice_generate_with_text(cli_runner, mock_tts_service):
    """Test voice generation with text argument."""
    result = cli_runner.invoke(generate, ["Hello world"])

    assert result.exit_code == 0
    assert "Audio generated" in result.output or "generated" in result.output.lower()


def test_voice_generate_with_voice(cli_runner, mock_tts_service):
    """Test voice generation with custom voice."""
    result = cli_runner.invoke(generate, ["-v", "echo", "Hello world"])

    assert result.exit_code == 0
    service_instance = mock_tts_service.return_value
    call_kwargs = service_instance.generate_voiceover.call_args[1]
    assert call_kwargs["voice"] == "echo"


def test_voice_generate_with_speed(cli_runner, mock_tts_service):
    """Test voice generation with custom speed."""
    result = cli_runner.invoke(generate, ["--speed", "1.5", "Hello world"])

    assert result.exit_code == 0
    service_instance = mock_tts_service.return_value
    call_kwargs = service_instance.generate_voiceover.call_args[1]
    assert call_kwargs["speed"] == 1.5


def test_voice_generate_with_emotion(cli_runner, mock_tts_service):
    """Test voice generation with emotion."""
    result = cli_runner.invoke(generate, ["-e", "happy", "I love this!"])

    assert result.exit_code == 0
    service_instance = mock_tts_service.return_value
    call_kwargs = service_instance.generate_voiceover.call_args[1]
    assert call_kwargs["emotion"] == "happy"


def test_voice_generate_from_file(cli_runner, mock_tts_service):
    """Test voice generation reading text from file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("This is a test script")
        temp_file = f.name

    try:
        result = cli_runner.invoke(generate, ["-f", temp_file])
        assert result.exit_code == 0
    finally:
        Path(temp_file).unlink()


def test_voice_generate_from_stdin(cli_runner, mock_tts_service):
    """Test voice generation reading text from stdin."""
    result = cli_runner.invoke(generate, input="Hello from stdin\n")

    assert result.exit_code == 0


def test_voice_generate_no_text_error(cli_runner):
    """Test error when no text provided."""
    result = cli_runner.invoke(generate, input="")

    assert result.exit_code == 1
    assert "Text cannot be empty" in result.output


def test_voice_generate_voice_choices(cli_runner, mock_tts_service):
    """Test that only valid voices are accepted."""
    # Valid voices should work
    for voice in ["nova", "echo", "sage", "shimmer"]:
        result = cli_runner.invoke(generate, ["-v", voice, "test"])
        assert result.exit_code == 0

    # Invalid voice should fail
    result = cli_runner.invoke(generate, ["-v", "invalid", "test"])
    assert result.exit_code != 0


def test_voice_generate_emotion_choices(cli_runner, mock_tts_service):
    """Test that only valid emotions are accepted."""
    # Valid emotions should work
    for emotion in ["neutral", "happy", "sad", "angry"]:
        result = cli_runner.invoke(generate, ["-e", emotion, "test"])
        assert result.exit_code == 0

    # Invalid emotion should fail
    result = cli_runner.invoke(generate, ["-e", "invalid", "test"])
    assert result.exit_code != 0


def test_voice_generate_service_error(cli_runner, mock_tts_service):
    """Test handling of service errors."""
    service_instance = mock_tts_service.return_value
    service_instance.generate_voiceover.side_effect = RuntimeError("TTS engine failed")

    result = cli_runner.invoke(generate, ["test text"])

    assert result.exit_code == 1
    assert "Voice generation failed" in result.output
