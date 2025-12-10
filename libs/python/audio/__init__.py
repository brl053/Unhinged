"""
Audio utilities for the Unhinged platform.

Provides microphone capture and streaming transcription utilities
for local, gRPC-free workflows.
"""

from .mic_capture import MicCaptureError, iter_audio_chunks
from .streaming_transcription import new_session, stream_transcription_from_chunks

__all__ = [
    "MicCaptureError",
    "iter_audio_chunks",
    "new_session",
    "stream_transcription_from_chunks",
]
