"""Tests for TextGenerationService."""

from unittest.mock import MagicMock, patch

import pytest

from libs.services.text_generation_service import TextGenerationService


@pytest.fixture
def text_gen_service():
    """Create TextGenerationService instance."""
    return TextGenerationService(model="llama2", provider="ollama")


def test_text_generation_service_init():
    """Test service initialization."""
    service = TextGenerationService(model="mistral", provider="ollama")

    assert service.model == "mistral"
    assert service.provider == "ollama"
    assert service.client is None
    assert service.model_loaded is False


def test_text_generation_service_ollama(text_gen_service):
    """Test Ollama provider initialization."""
    with patch("builtins.__import__", side_effect=__import__) as mock_import:
        mock_ollama = MagicMock()
        mock_ollama.generate.return_value = {"response": "Generated text"}

        # Mock the import of ollama
        import sys

        sys.modules["ollama"] = mock_ollama

        try:
            text_gen_service._load_client()
            assert text_gen_service.model_loaded is True
            assert text_gen_service.client is not None
        finally:
            del sys.modules["ollama"]


def test_text_generation_service_openai():
    """Test OpenAI provider initialization."""
    service = TextGenerationService(model="gpt-4", provider="openai")

    with patch("builtins.__import__") as mock_import:
        mock_openai_module = MagicMock()
        mock_openai_module.OpenAI = MagicMock()

        import sys

        sys.modules["openai"] = mock_openai_module

        try:
            service._load_client()
            assert service.model_loaded is True
        finally:
            del sys.modules["openai"]


def test_text_generation_service_anthropic():
    """Test Anthropic provider initialization."""
    service = TextGenerationService(model="claude-3", provider="anthropic")

    with patch("builtins.__import__") as mock_import:
        mock_anthropic_module = MagicMock()
        mock_anthropic_module.Anthropic = MagicMock()

        import sys

        sys.modules["anthropic"] = mock_anthropic_module

        try:
            service._load_client()
            assert service.model_loaded is True
        finally:
            del sys.modules["anthropic"]


def test_generate_text_ollama(text_gen_service):
    """Test text generation with Ollama."""
    import sys

    mock_ollama = MagicMock()
    mock_ollama.generate.return_value = {"response": "Generated haiku"}
    sys.modules["ollama"] = mock_ollama

    try:
        result = text_gen_service.generate("write a haiku")
        assert result == "Generated haiku"
        mock_ollama.generate.assert_called_once()
    finally:
        del sys.modules["ollama"]


def test_generate_text_with_parameters(text_gen_service):
    """Test text generation with custom parameters."""
    import sys

    mock_ollama = MagicMock()
    mock_ollama.generate.return_value = {"response": "Generated text"}
    sys.modules["ollama"] = mock_ollama

    try:
        result = text_gen_service.generate(
            prompt="write something",
            max_tokens=1024,
            temperature=0.5,
        )
        assert result == "Generated text"
    finally:
        del sys.modules["ollama"]


def test_generate_text_with_metadata(text_gen_service):
    """Test text generation with metadata."""
    import sys

    mock_ollama = MagicMock()
    mock_ollama.generate.return_value = {"response": "Generated text"}
    sys.modules["ollama"] = mock_ollama

    try:
        result = text_gen_service.generate_with_metadata("write something")
        assert result["text"] == "Generated text"
        assert result["model"] == "llama2"
        assert result["provider"] == "ollama"
        assert "prompt_length" in result
        assert "text_length" in result
    finally:
        del sys.modules["ollama"]


def test_generate_text_error_handling(text_gen_service):
    """Test error handling in text generation."""
    import sys

    mock_ollama = MagicMock()
    mock_ollama.generate.side_effect = Exception("Connection failed")
    sys.modules["ollama"] = mock_ollama

    try:
        with pytest.raises(RuntimeError, match="Failed to generate text"):
            text_gen_service.generate("write something")
    finally:
        del sys.modules["ollama"]


def test_generate_text_invalid_provider():
    """Test error with invalid provider."""
    service = TextGenerationService(model="test", provider="invalid")

    with pytest.raises(ValueError, match="Unknown provider"):
        service._load_client()


def test_lazy_loading(text_gen_service):
    """Test that client is lazily loaded."""
    import sys

    assert text_gen_service.client is None

    mock_ollama = MagicMock()
    sys.modules["ollama"] = mock_ollama

    try:
        text_gen_service._load_client()
        assert text_gen_service.model_loaded is True

        # Second call should not reload
        text_gen_service._load_client()
        assert text_gen_service.model_loaded is True
    finally:
        del sys.modules["ollama"]
