"""Streaming-style transcription helpers (transport-agnostic).

@llm-type library.services.streaming.transcription
@llm-does provide async helpers to stream transcription segments from audio chunks

This module does NOT talk to the microphone or network directly. Callers are
responsible for providing audio bytes (e.g., from a subprocess recording
command). The helpers here convert those audio chunks into
TranscriptionSegment / TranscriptionSession models using TranscriptionService.
"""

from __future__ import annotations

from collections.abc import AsyncIterable, AsyncIterator
from datetime import datetime
from uuid import uuid4

from libs.python.models.transcription.schema import (
    TranscriptionMode,
    TranscriptionSegment,
    TranscriptionSession,
)
from libs.services.transcription_service import TranscriptionService


async def stream_transcription_from_chunks(
    audio_chunks: AsyncIterable[bytes],
    *,
    model_size: str = "base",
    chunk_seconds: int = 5,
    mode: TranscriptionMode = TranscriptionMode.MIC,
) -> AsyncIterator[TranscriptionSegment]:
    """Yield TranscriptionSegment objects for each audio chunk.

    This is a thin wrapper over :class:`TranscriptionService` that assumes each
    ``audio_chunks`` element represents roughly ``chunk_seconds`` of audio in a
    Whisper-compatible format.

    The function itself does not assemble a TranscriptionSession; callers that
    need aggregated state should build a session and append segments as they
    are yielded.
    """

    service = TranscriptionService(model_size=model_size)
    sequence = 0
    current_time = 0.0

    async for chunk in audio_chunks:
        # Transcribe this chunk as a standalone audio blob.
        text = service.transcribe_audio_data(chunk)

        seg = TranscriptionSegment(
            id=str(uuid4()),
            text=text,
            start_time=current_time,
            end_time=current_time + float(chunk_seconds),
            sequence=sequence,
            is_final=True,
        )

        yield seg

        sequence += 1
        current_time += float(chunk_seconds)


def new_session(
    *,
    mode: TranscriptionMode,
    model_size: str,
    chunk_seconds: int,
) -> TranscriptionSession:
    """Create a new :class:`TranscriptionSession` with sane defaults."""

    return TranscriptionSession(
        session_id=str(uuid4()),
        mode=mode,
        created_at=datetime.utcnow(),
        model_size=model_size,
        chunk_seconds=chunk_seconds,
    )
