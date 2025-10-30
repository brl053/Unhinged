"""
Custom "hooks" for the GTK4 desktop application.

These modules provide React hook-like functionality for managing
state and side effects in the desktop application.
"""

from .use_audio_devices import use_audio_devices, AudioDevicesHook
from .use_transcription import use_transcription, TranscriptionHook

__all__ = [
    'use_audio_devices',
    'AudioDevicesHook',
    'use_transcription',
    'TranscriptionHook'
]
