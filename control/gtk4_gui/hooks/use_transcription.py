"""
Transcription hook - React hook-like functionality for speech-to-text.

Provides a clean interface for transcription operations that can be used
across different views and components.
"""

from dataclasses import dataclass
from typing import Optional, Callable, Dict, Any

from ..services.transcription_service import TranscriptionService

@dataclass
class TranscriptionHook:
    """Hook return type for transcription operations (like React hook return)."""
    transcribe: Callable[[str], Dict[str, Any]]
    is_service_available: Callable[[], bool]
    get_service_info: Callable[[], Dict[str, Any]]
    test_connection: Callable[[], Dict[str, Any]]

class TranscriptionManager:
    """Internal manager for transcription operations."""
    
    def __init__(self):
        self._service = TranscriptionService()
        self._service_status_cache: Optional[Dict[str, Any]] = None
    
    def transcribe_audio_file(self, audio_file_path: str) -> Dict[str, Any]:
        """Transcribe an audio file."""
        return self._service.transcribe_audio_file(audio_file_path)
    
    def is_service_available(self) -> bool:
        """Check if the transcription service is available."""
        if self._service_status_cache is None:
            self._service_status_cache = self._service.test_connection()
        return self._service_status_cache.get('available', False)
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get transcription service information."""
        return self._service.get_service_info()
    
    def test_connection(self) -> Dict[str, Any]:
        """Test connection to transcription service."""
        # Clear cache and test fresh
        self._service_status_cache = None
        result = self._service.test_connection()
        self._service_status_cache = result
        return result

# Global manager instance
_transcription_manager = TranscriptionManager()

def use_transcription() -> TranscriptionHook:
    """
    Hook for transcription operations (React hook-like).
    
    Returns:
        TranscriptionHook with transcription functions
    """
    
    def transcribe(audio_file_path: str) -> Dict[str, Any]:
        """Transcribe an audio file."""
        return _transcription_manager.transcribe_audio_file(audio_file_path)
    
    def is_service_available() -> bool:
        """Check if transcription service is available."""
        return _transcription_manager.is_service_available()
    
    def get_service_info() -> Dict[str, Any]:
        """Get service information."""
        return _transcription_manager.get_service_info()
    
    def test_connection() -> Dict[str, Any]:
        """Test service connection."""
        return _transcription_manager.test_connection()
    
    return TranscriptionHook(
        transcribe=transcribe,
        is_service_available=is_service_available,
        get_service_info=get_service_info,
        test_connection=test_connection
    )
