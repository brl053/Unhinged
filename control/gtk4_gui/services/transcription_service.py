"""
Transcription service client.

Provides a clean interface to the speech-to-text gRPC service
using the generated protobuf clients.
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any

# Add libs to path for gRPC client factory
project_root = Path(__file__).parent.parent.parent.parent
libs_path = project_root / "libs" / "python"
if libs_path.exists() and str(libs_path) not in sys.path:
    sys.path.insert(0, str(libs_path))

try:
    from libs.python.grpc import create_audio_client
except ImportError:
    # Fallback: create a simple mock client for testing
    def create_audio_client(address):
        class MockClient:
            def SpeechToText(self, chunks, timeout=30):
                class MockResponse:
                    def __init__(self):
                        self.response = type('obj', (object,), {'success': False, 'message': 'Service unavailable'})()
                        self.transcript = ''
                        self.confidence = 0.0
                return MockResponse()
        return MockClient()

    print("⚠️  Using mock transcription client - gRPC client factory not available")

class TranscriptionService:
    """Service for speech-to-text transcription using gRPC."""
    
    def __init__(self, address: str = 'localhost:1191'):
        self.address = address
        self._client = None
    
    @property
    def client(self):
        """Get or create the gRPC client."""
        if self._client is None:
            self._client = create_audio_client(self.address)
        return self._client
    
    def transcribe_audio_file(self, audio_file_path: str, timeout: float = 30.0) -> Dict[str, Any]:
        """
        Transcribe an audio file using the speech-to-text service.
        
        Args:
            audio_file_path: Path to the WAV audio file
            timeout: Request timeout in seconds
            
        Returns:
            Dict with transcription results:
            {
                'success': bool,
                'transcript': str,
                'confidence': float,
                'error': Optional[str]
            }
        """
        try:
            # Import protobuf modules
            from unhinged_proto_clients import common_pb2
            
            # Read audio file
            with open(audio_file_path, 'rb') as f:
                audio_data = f.read()
            
            if len(audio_data) <= 44:  # WAV header is 44 bytes
                return {
                    'success': False,
                    'transcript': '',
                    'confidence': 0.0,
                    'error': 'Audio file is empty or contains no audio data'
                }
            
            # Create gRPC stream chunk
            def generate_audio_chunks():
                chunk = common_pb2.StreamChunk()
                chunk.data = audio_data
                chunk.type = common_pb2.CHUNK_TYPE_DATA
                chunk.is_final = True
                yield chunk
            
            # Send to speech-to-text service
            response = self.client.SpeechToText(generate_audio_chunks(), timeout=timeout)
            
            return {
                'success': response.response.success,
                'transcript': response.transcript.strip(),
                'confidence': response.confidence,
                'error': response.response.message if not response.response.success else None
            }
            
        except Exception as e:
            return {
                'success': False,
                'transcript': '',
                'confidence': 0.0,
                'error': f'Transcription failed: {str(e)}'
            }
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test connection to the transcription service.
        
        Returns:
            Dict with connection status:
            {
                'available': bool,
                'error': Optional[str]
            }
        """
        try:
            # Try to create a client and test basic connectivity
            client = create_audio_client(self.address)
            
            # For now, just check if we can create the client
            # In the future, we could add a health check call
            return {
                'available': True,
                'error': None
            }
            
        except Exception as e:
            return {
                'available': False,
                'error': str(e)
            }
    
    def get_service_info(self) -> Dict[str, Any]:
        """
        Get information about the transcription service.
        
        Returns:
            Dict with service information
        """
        return {
            'service_name': 'Speech-to-Text',
            'address': self.address,
            'protocol': 'gRPC',
            'description': 'Whisper-based speech transcription service'
        }
