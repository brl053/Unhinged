"""
Handlers package for Unhinged Desktop GUI

This package contains handler classes that manage specific functionality
domains like audio, platform control, and chat operations.
"""

from .audio_handler import AudioHandler, RecordingState

__all__ = ['AudioHandler', 'RecordingState']
