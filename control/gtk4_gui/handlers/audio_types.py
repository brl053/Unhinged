"""
Audio handler data types and configuration classes.

Defines immutable data structures for audio recording, processing, and transcription.
Eliminates need for passing 25+ parameters to functions.
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class RecordingState(Enum):
    """Audio recording state machine."""

    IDLE = "idle"
    RECORDING = "recording"
    PROCESSING = "processing"
    TRANSCRIBING = "transcribing"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class RecordingConfig:
    """Configuration for audio recording session."""

    device_id: str
    sample_rate: int
    format: str
    channels: int
    chunk_size: int = 4096

    def __post_init__(self):
        """Validate configuration."""
        if self.sample_rate <= 0:
            raise ValueError("sample_rate must be positive")
        if self.channels <= 0:
            raise ValueError("channels must be positive")
        if self.chunk_size <= 0:
            raise ValueError("chunk_size must be positive")


@dataclass
class AudioChunk:
    """Single chunk of audio data."""

    data: bytes
    timestamp: float
    sample_count: int
    amplitude: float = 0.0

    def duration_ms(self, sample_rate: int) -> float:
        """Calculate duration in milliseconds."""
        return (self.sample_count / sample_rate) * 1000


@dataclass
class RecordingMetrics:
    """Metrics for a recording session."""

    start_time: float
    end_time: float | None = None
    total_chunks: int = 0
    total_samples: int = 0
    peak_amplitude: float = 0.0

    @property
    def duration_seconds(self) -> float:
        """Calculate total duration."""
        if self.end_time is None:
            return 0.0
        return self.end_time - self.start_time


@dataclass
class TranscriptionRequest:
    """Request for audio transcription."""

    audio_file: Path
    language: str = "en"
    model: str = "base"
    timeout_seconds: int = 300

    def __post_init__(self):
        """Validate request."""
        if not self.audio_file.exists():
            raise FileNotFoundError(f"Audio file not found: {self.audio_file}")


@dataclass
class TranscriptionResult:
    """Result of audio transcription."""

    text: str
    confidence: float
    duration_seconds: float
    language: str
    error: str | None = None

    @property
    def success(self) -> bool:
        """Check if transcription succeeded."""
        return self.error is None
