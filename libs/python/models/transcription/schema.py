"""Transcription domain models used across the system.

@llm-type library.models.transcription
@llm-does define core transcription types for MIC/FILE workflows and streaming STT
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class TranscriptionMode(str, Enum):
    """Source / mode of a transcription session."""

    MIC = "MIC"
    FILE = "FILE"


@dataclass
class TranscriptionSegment:
    """One segment (chunk) of transcribed audio.

    Segments are ordered by ``sequence`` and cover a half-open interval
    ``[start_time, end_time)`` relative to the session start.
    """

    id: str
    text: str
    start_time: float
    end_time: float
    sequence: int
    is_final: bool = True


@dataclass
class TranscriptionSession:
    """Aggregate view of a transcription session.

    This is intentionally transport-agnostic so it can back CLI, HTTP, or
    in-process integrations.
    """

    session_id: str
    mode: TranscriptionMode
    created_at: datetime
    model_size: str
    chunk_seconds: int
    segments: list[TranscriptionSegment] = field(default_factory=list)

    @property
    def duration_seconds(self) -> float:
        """Approximate duration based on last segment end_time.

        Returns 0.0 if there are no segments yet.
        """

        if not self.segments:
            return 0.0
        return max(seg.end_time for seg in self.segments)

    @property
    def text(self) -> str:
        """Concatenated transcript text across all segments."""

        return " ".join(seg.text.strip() for seg in self.segments if seg.text.strip())
