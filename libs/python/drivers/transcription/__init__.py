"""Transcription-related drivers.

@llm-type library.drivers.transcription
@llm-does provide drivers for microphone and STT-related workflows
"""

from __future__ import annotations

from .mic import MicTranscriptionDriver

__all__ = ["MicTranscriptionDriver"]
