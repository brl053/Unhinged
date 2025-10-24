"""
@llm-type control-system
@llm-legend speech_client.py - system control component
@llm-key Core functionality for speech_client
@llm-map Part of the Unhinged system architecture
@llm-axiom Maintains system independence and architectural compliance
@llm-contract Provides standardized interface for system integration
@llm-token speech_client: system control component
"""
"""
🎤 Speech Client - gRPC Integration

Real gRPC client for speech-to-text service integration.
Connects to the existing speech-to-text service on port 9091.

Features:
- gRPC calls to speech-to-text service
- Audio data streaming
- Error handling and loading states
- Simple audio recording simulation
"""

import sys
import os
import tempfile
import threading
import time
from typing import Optional, Callable, Iterator
from pathlib import Path

# Add centralized Python environment to path
project_root = Path(__file__).parent.parent.parent.parent.parent
centralized_python_path = project_root / "build" / "python" / "venv" / "lib" / "python3.12" / "site-packages"
sys.path.insert(0, str(centralized_python_path))

# gRPC import from centralized environment
try:
    import grpc
    GRPC_AVAILABLE = True
    print("🎤 gRPC module available from centralized environment")
except ImportError:
    print("⚠️ gRPC module not available - using mock mode")
    GRPC_AVAILABLE = False
    # Create mock grpc module
    class MockGRPC:
        class FutureTimeoutError(Exception):
            pass

        @staticmethod
        def insecure_channel(target):
            return None

        @staticmethod
        def channel_ready_future(channel):
            class MockFuture:
                def result(self, timeout=None):
                    raise MockGRPC.FutureTimeoutError("Mock timeout")
            return MockFuture()

    grpc = MockGRPC()

# Add generated proto clients to path
generated_path = project_root / "generated" / "python" / "clients"
sys.path.insert(0, str(generated_path))

try:
    from unhinged_proto_clients import audio_pb2, audio_pb2_grpc, common_pb2
    print("🎤 Proto clients imported successfully from centralized generation")
    if hasattr(audio_pb2_grpc, 'AudioServiceStub'):
        print("🎤 AudioServiceStub available for real gRPC connection")
    else:
        print("⚠️ AudioServiceStub not found in proto clients")
except ImportError as e:
    print(f"⚠️ Proto clients not available: {e}")
    # Create mock classes for development
    class MockProto:
        pass
    audio_pb2 = MockProto()
    audio_pb2_grpc = MockProto()
    common_pb2 = MockProto()


class SpeechClient:
    """
    gRPC client for speech-to-text service.

    Integrates with the existing speech-to-text service
    to provide voice input for the chat interface.
    """

    def __init__(self, host: str = "localhost", port: int = 1191):
        self.host = host
        self.port = port
        self.channel = None
        self.stub = None
        self.is_recording = False
        self.recording_thread = None
        self.audio_data = []

        print(f"🎤 SpeechClient initialized for {host}:{port}")
        self._setup_grpc_connection()

    def _setup_grpc_connection(self):
        """Setup gRPC connection to speech-to-text service"""
        if not GRPC_AVAILABLE:
            print("⚠️ gRPC not available - running in mock mode")
            self.channel = None
            self.stub = None
            return

        try:
            self.channel = grpc.insecure_channel(f"{self.host}:{self.port}")

            # Test connection with a timeout
            grpc.channel_ready_future(self.channel).result(timeout=5)

            if hasattr(audio_pb2_grpc, 'AudioServiceStub'):
                self.stub = audio_pb2_grpc.AudioServiceStub(self.channel)
                print("✅ gRPC connection established")
            else:
                print("⚠️ AudioServiceStub not available (proto mock)")
                self.stub = None

        except grpc.FutureTimeoutError:
            print(f"⚠️ gRPC connection timeout to {self.host}:{self.port}")
            self.channel = None
            self.stub = None
        except Exception as e:
            print(f"❌ gRPC connection failed: {e}")
            self.channel = None
            self.stub = None

    def is_connected(self) -> bool:
        """Check if gRPC connection is active"""
        return self.channel is not None and self.stub is not None

    def start_recording(self, callback: Optional[Callable[[str], None]] = None):
        """Start recording audio for transcription"""
        if self.is_recording:
            print("🎤 Already recording")
            return

        print("🎤 Starting audio recording...")
        self.is_recording = True
        self.audio_data = []

        # For now, simulate recording with a simple timer
        # In a real implementation, this would capture microphone audio
        self.recording_thread = threading.Thread(
            target=self._simulate_recording,
            args=(callback,),
            daemon=True
        )
        self.recording_thread.start()

    def stop_recording(self) -> str:
        """Stop recording and return transcribed text"""
        if not self.is_recording:
            print("🎤 Not currently recording")
            return ""

        print("🎤 Stopping audio recording...")
        self.is_recording = False

        if self.recording_thread:
            self.recording_thread.join(timeout=2)

        # Transcribe the recorded audio
        return self._transcribe_recorded_audio()

    def _simulate_recording(self, callback: Optional[Callable[[str], None]]):
        """Simulate audio recording (placeholder for real microphone capture)"""
        start_time = time.time()

        while self.is_recording:
            time.sleep(0.1)  # Simulate audio sampling

            # Simulate collecting audio data
            duration = time.time() - start_time
            if duration > 0.5:  # Minimum recording duration
                self.audio_data.append(f"audio_chunk_{len(self.audio_data)}")

        print(f"🎤 Recording simulation complete: {len(self.audio_data)} chunks")

    def _transcribe_recorded_audio(self) -> str:
        """Transcribe the recorded audio data"""
        if not self.audio_data:
            return "No audio recorded"

        if not self.is_connected():
            print("⚠️ No gRPC connection, using mock transcription")
            return f"Mock transcription: recorded {len(self.audio_data)} audio chunks"

        try:
            # Create audio stream for gRPC call
            audio_stream = self._create_audio_stream()

            # Call speech-to-text service
            response = self.stub.SpeechToText(audio_stream)

            if response.response.success:
                print(f"✅ Transcription successful: {response.transcript[:50]}...")
                return response.transcript
            else:
                print(f"❌ Transcription failed: {response.response.message}")
                return f"Transcription error: {response.response.message}"

        except Exception as e:
            print(f"❌ gRPC transcription error: {e}")
            return f"Transcription error: {str(e)}"

    def _create_audio_stream(self) -> Iterator:
        """Create audio stream for gRPC call"""
        # For now, create a simple mock audio stream
        # In a real implementation, this would stream actual audio data

        if not hasattr(common_pb2, 'StreamChunk'):
            print("⚠️ StreamChunk not available, using mock stream")
            return iter([])

        chunks = []

        # Create mock audio chunk
        chunk = common_pb2.StreamChunk()
        chunk.stream_id = "chat_audio_recording"
        chunk.sequence_number = 1
        chunk.type = getattr(common_pb2, 'CHUNK_TYPE_DATA', 1)
        chunk.data = b"mock_audio_data"  # In real implementation: actual audio bytes
        chunk.is_final = True
        chunk.status = getattr(common_pb2, 'CHUNK_STATUS_COMPLETE', 1)

        chunks.append(chunk)
        return iter(chunks)

    def transcribe_audio(self, audio_data: bytes) -> str:
        """Transcribe provided audio data to text"""
        if not self.is_connected():
            print("⚠️ No gRPC connection for transcription")
            return "Service unavailable"

        try:
            # Create stream chunk with audio data
            if not hasattr(common_pb2, 'StreamChunk'):
                return "Proto clients not available"

            chunk = common_pb2.StreamChunk()
            chunk.stream_id = "chat_audio_direct"
            chunk.sequence_number = 1
            chunk.type = getattr(common_pb2, 'CHUNK_TYPE_DATA', 1)
            chunk.data = audio_data
            chunk.is_final = True
            chunk.status = getattr(common_pb2, 'CHUNK_STATUS_COMPLETE', 1)

            # Call speech-to-text service
            response = self.stub.SpeechToText(iter([chunk]))

            if response.response.success:
                return response.transcript
            else:
                return f"Error: {response.response.message}"

        except Exception as e:
            print(f"❌ Direct transcription error: {e}")
            return f"Transcription error: {str(e)}"

    def close(self):
        """Close gRPC connection"""
        if self.is_recording:
            self.stop_recording()

        if self.channel:
            self.channel.close()
            print("🎤 gRPC connection closed")
