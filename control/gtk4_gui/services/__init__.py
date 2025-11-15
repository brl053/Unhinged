"""
Service layer for the GTK4 desktop application.

Provides clean interfaces to backend services using the generated
protobuf clients and gRPC client factory.
"""

from .audio_service import AudioService
from .transcription_service import TranscriptionService

__all__ = ["AudioService", "TranscriptionService"]
