"""
Audio transcription service integration.

Handles transcription API calls, timeout handling, result parsing, and error recovery.
Decoupled from AudioHandler to enable independent testing and reuse.
"""

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))

from audio_types import TranscriptionResult

logger = logging.getLogger(__name__)


class AudioTranscriber:
    """Handles audio transcription via service connector."""

    def __init__(self, service_connector=None):
        """Initialize transcriber.

        Args:
            service_connector: Service connector instance (injected for testing)
        """
        self.service_connector = service_connector

    def _validate_audio_file(self, audio_file: Path) -> bool:
        """Validate audio file exists and has content.

        Args:
            audio_file: Path to audio file

        Returns:
            True if valid

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is empty
        """
        if not audio_file.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_file}")

        file_size = audio_file.stat().st_size
        if file_size <= 44:  # WAV header is 44 bytes
            raise ValueError(f"Audio file is empty: {file_size} bytes")

        return True

    def transcribe(
        self,
        audio_file: Path,
        language: str = "en",
        timeout_seconds: int = 300
    ) -> TranscriptionResult:
        """Transcribe audio file.

        Args:
            audio_file: Path to WAV audio file
            language: Language code (default: "en")
            timeout_seconds: Request timeout in seconds

        Returns:
            TranscriptionResult with transcript and metadata

        Raises:
            FileNotFoundError: If audio file doesn't exist
            ValueError: If audio file is invalid
            Exception: If transcription fails
        """
        try:
            # Validate file
            self._validate_audio_file(audio_file)

            # Call service
            transcript = self.service_connector.transcribe_audio(
                audio_file,
                timeout=timeout_seconds
            )

            # Parse result
            result = TranscriptionResult(
                text=transcript.strip() if transcript else "",
                confidence=1.0,
                duration_seconds=0.0,
                language=language,
                error=None
            )

            logger.info(
                f"Transcription completed: {len(result.text)} characters"
            )

            return result

        except FileNotFoundError as e:
            logger.error(f"Audio file not found: {e}")
            return TranscriptionResult(
                text="",
                confidence=0.0,
                duration_seconds=0.0,
                language=language,
                error=str(e)
            )

        except ValueError as e:
            logger.error(f"Invalid audio file: {e}")
            return TranscriptionResult(
                text="",
                confidence=0.0,
                duration_seconds=0.0,
                language=language,
                error=str(e)
            )

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return TranscriptionResult(
                text="",
                confidence=0.0,
                duration_seconds=0.0,
                language=language,
                error=f"Transcription failed: {str(e)}"
            )

