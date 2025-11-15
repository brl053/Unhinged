#!/usr/bin/env python3
"""
Transcription Service

Speech-to-text transcription using Whisper.
Direct Python implementation - no gRPC overhead.
"""

import logging
import tempfile
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class TranscriptionService:
    """Speech-to-text transcription using OpenAI Whisper"""

    def __init__(self, model_size: str = "base"):
        """
        Initialize transcription service.

        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
        """
        self.model_size = model_size
        self.model = None
        self.model_loaded = False

        logger.info(f"TranscriptionService initialized (model: {model_size})")

    def _load_model(self):
        """Load Whisper model (lazy loading)"""
        if self.model_loaded:
            return

        try:
            import whisper

            logger.info(f"Loading Whisper model: {self.model_size}")
            self.model = whisper.load_model(self.model_size)
            self.model_loaded = True
            logger.info("Whisper model loaded successfully")

        except ImportError:
            logger.error("whisper not installed. Run: pip install openai-whisper")
            raise
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise

    def transcribe_audio(self, audio_file_path: Path | str) -> str:
        """
        Transcribe audio file to text.

        Args:
            audio_file_path: Path to audio file (WAV, MP3, etc.)

        Returns:
            Transcribed text

        Raises:
            FileNotFoundError: If audio file doesn't exist
            RuntimeError: If transcription fails
        """
        audio_path = Path(audio_file_path)

        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        # Lazy load model
        self._load_model()

        try:
            logger.info(f"Transcribing audio: {audio_path}")

            # Transcribe using Whisper
            result = self.model.transcribe(str(audio_path))

            transcript = result.get("text", "").strip()
            logger.info(f"Transcription complete: {len(transcript)} characters")

            return transcript

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise RuntimeError(f"Failed to transcribe audio: {e}") from e

    def transcribe_audio_data(self, audio_data: bytes, format: str = "wav") -> str:
        """
        Transcribe audio data (bytes) to text.

        Args:
            audio_data: Raw audio data
            format: Audio format (wav, mp3, etc.)

        Returns:
            Transcribed text
        """
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix=f".{format}", delete=False) as temp_file:
            temp_file.write(audio_data)
            temp_path = Path(temp_file.name)

        try:
            return self.transcribe_audio(temp_path)
        finally:
            # Clean up temporary file
            if temp_path.exists():
                temp_path.unlink()

    def transcribe_with_metadata(self, audio_file_path: Path | str) -> dict[str, Any]:
        """
        Transcribe audio and return detailed metadata.

        Args:
            audio_file_path: Path to audio file

        Returns:
            Dict with transcript, language, segments, etc.
        """
        audio_path = Path(audio_file_path)

        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        # Lazy load model
        self._load_model()

        try:
            logger.info(f"Transcribing audio with metadata: {audio_path}")

            # Transcribe using Whisper
            result = self.model.transcribe(str(audio_path))

            return {
                "text": result.get("text", "").strip(),
                "language": result.get("language", "unknown"),
                "segments": result.get("segments", []),
                "duration": audio_path.stat().st_size / 16000,  # Rough estimate
            }

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise RuntimeError(f"Failed to transcribe audio: {e}") from e

