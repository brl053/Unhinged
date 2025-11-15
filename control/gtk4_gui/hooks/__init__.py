"""
Custom "hooks" for the GTK4 desktop application.

These modules provide React hook-like functionality for managing
state and side effects in the desktop application.
"""

from .use_audio_devices import AudioDevicesHook, use_audio_devices
from .use_transcription import TranscriptionHook, use_transcription

__all__ = [
    "use_audio_devices",
    "AudioDevicesHook",
    "use_transcription",
    "TranscriptionHook",
]
