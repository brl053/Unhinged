"""
Audio processing for recording and transcription.

Handles amplitude extraction, WAV conversion, and chunk processing.
Decoupled from AudioHandler to enable independent testing and reuse.
"""

import logging
import sys
import wave
from pathlib import Path

# Add utils to path for audio_utils import
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))

from audio_types import AudioChunk
from audio_utils import calculate_rms_amplitude

logger = logging.getLogger(__name__)


class AudioProcessor:
    """Processes audio data during and after recording."""

    CHUNK_SIZE = 1024  # 1024 bytes = 512 samples for S16_LE

    def calculate_amplitude(self, audio_data: bytes) -> float:
        """Calculate RMS amplitude from raw audio chunk.

        Args:
            audio_data: Raw audio bytes

        Returns:
            Normalized amplitude (0.0 to 1.0)
        """
        return calculate_rms_amplitude(audio_data)

    def process_chunk(self, audio_data: bytes, timestamp: float, sample_rate: int) -> AudioChunk:
        """Process a single audio chunk.

        Args:
            audio_data: Raw audio bytes
            timestamp: Chunk timestamp
            sample_rate: Sample rate in Hz

        Returns:
            AudioChunk with metadata
        """
        amplitude = self.calculate_amplitude(audio_data)
        sample_count = len(audio_data) // 2  # 16-bit samples

        return AudioChunk(
            data=audio_data,
            timestamp=timestamp,
            sample_count=sample_count,
            amplitude=amplitude,
        )

    def convert_raw_to_wav(
        self,
        raw_file: Path,
        wav_file: Path,
        sample_rate: int,
        channels: int,
        sample_width: int = 2,
    ) -> None:
        """Convert raw audio data to WAV format.

        Args:
            raw_file: Path to raw audio file
            wav_file: Path to output WAV file
            sample_rate: Sample rate in Hz
            channels: Number of channels
            sample_width: Sample width in bytes (2 for S16_LE)

        Raises:
            IOError: If conversion fails
        """
        try:
            with open(raw_file, "rb") as f:
                raw_data = f.read()

            with wave.open(str(wav_file), "wb") as wav:
                wav.setnchannels(channels)
                wav.setsampwidth(sample_width)
                wav.setframerate(sample_rate)
                wav.writeframes(raw_data)

            logger.debug(f"Converted raw audio to WAV: {wav_file}")

        except Exception as e:
            logger.error(f"Failed to convert raw audio to WAV: {e}")
            raise

    def validate_wav_file(self, file_path: Path, min_size: int = 44) -> bool:
        """Validate WAV file.

        Args:
            file_path: Path to WAV file
            min_size: Minimum file size in bytes

        Returns:
            True if file is valid

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is too small
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        file_size = file_path.stat().st_size
        if file_size < min_size:
            raise ValueError(f"File too small: {file_size} bytes (min: {min_size})")

        return True
