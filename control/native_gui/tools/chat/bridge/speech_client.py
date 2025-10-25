
import logging; gui_logger = logging.getLogger(__name__)

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

# Import our audio capture module
try:
    from .audio_capture import AudioCapture, AudioConfig
    from .audio_utils import AudioDeviceManager
    AUDIO_CAPTURE_AVAILABLE = True
except ImportError as e:
    gui_logger.warn(f" Audio capture not available: {e}")
    AUDIO_CAPTURE_AVAILABLE = False

# gRPC import - relies on PYTHONPATH set by GUI launcher
try:
    import grpc
    GRPC_AVAILABLE = True
except ImportError:
    gui_logger.warn(" gRPC module not available - using mock mode")
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

# Add generated proto clients to path - project root should be in PYTHONPATH
project_root = Path(__file__).parent.parent.parent.parent.parent
generated_path = project_root / "generated" / "python" / "clients"
sys.path.insert(0, str(generated_path))

try:
    from unhinged_proto_clients import audio_pb2, audio_pb2_grpc, common_pb2
    if hasattr(audio_pb2_grpc, 'AudioServiceStub'):
    else:
        gui_logger.warn(" AudioServiceStub not found in proto clients")
except ImportError as e:
    gui_logger.warn(f" Proto clients not available: {e}")
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

        # Initialize audio capture
        self.audio_capture = None
        if AUDIO_CAPTURE_AVAILABLE:
            try:
                self.audio_capture = AudioCapture()
            except Exception as e:
                gui_logger.warn(f" Failed to initialize audio capture: {e}")
                self.audio_capture = None

        self._setup_grpc_connection()

    def _setup_grpc_connection(self):
        """Setup gRPC connection to speech-to-text service"""
        if not GRPC_AVAILABLE:
            gui_logger.warn(" gRPC not available - running in mock mode")
            self.channel = None
            self.stub = None
            return

        try:
            self.channel = grpc.insecure_channel(f"{self.host}:{self.port}")

            # Test connection with a timeout
            grpc.channel_ready_future(self.channel).result(timeout=5)

            if hasattr(audio_pb2_grpc, 'AudioServiceStub'):
                self.stub = audio_pb2_grpc.AudioServiceStub(self.channel)
                gui_logger.info(" gRPC connection established", {"status": "success"})
            else:
                gui_logger.warn(" AudioServiceStub not available (proto mock)")
                self.stub = None

        except grpc.FutureTimeoutError:
            gui_logger.warn(f" gRPC connection timeout to {self.host}:{self.port}")
            self.channel = None
            self.stub = None
        except Exception as e:
            gui_logger.error(f" gRPC connection failed: {e}")
            self.channel = None
            self.stub = None

    def is_connected(self) -> bool:
        """Check if gRPC connection is active"""
        return self.channel is not None and self.stub is not None

    def start_recording(self, callback: Optional[Callable[[str], None]] = None, duration: float = 3.0):
        """Start recording audio for transcription"""
        if self.is_recording:
            return

        self.is_recording = True
        self.audio_data = []

        # Use real audio capture if available
        if self.audio_capture and AUDIO_CAPTURE_AVAILABLE:
            self.recording_thread = threading.Thread(
                target=self._real_recording,
                args=(callback, duration),
                daemon=True
            )
        else:
            # Fallback to simulation
            self.recording_thread = threading.Thread(
                target=self._simulate_recording,
                args=(callback,),
                daemon=True
            )

        self.recording_thread.start()

    def stop_recording(self) -> str:
        """Stop recording and return transcribed text"""
        if not self.is_recording:
            return ""

        self.is_recording = False

        if self.recording_thread:
            self.recording_thread.join(timeout=2)

        # Transcribe the recorded audio
        return self._transcribe_recorded_audio()

    def _real_recording(self, callback: Optional[Callable[[str], None]], duration: float):
        """Real audio recording using AudioCapture"""
        try:
            # Start real audio capture
            if self.audio_capture.start_recording(duration=duration):
                # Wait for recording to complete
                time.sleep(duration + 0.5)  # Small buffer

                # Get the recorded audio data
                audio_bytes = self.audio_capture.stop_recording()

                if audio_bytes:
                    self.audio_data = [audio_bytes]  # Store as single chunk
                else:
                    gui_logger.warn(" No audio data captured")
                    self.audio_data = []
            else:
                gui_logger.error(" Failed to start real audio recording")
                self.audio_data = []

        except Exception as e:
            gui_logger.error(f" Error in real recording: {e}")
            self.audio_data = []

    def _simulate_recording(self, callback: Optional[Callable[[str], None]]):
        """Simulate audio recording (fallback when real capture unavailable)"""
        start_time = time.time()

        while self.is_recording:
            time.sleep(0.1)  # Simulate audio sampling

            # Simulate collecting audio data
            duration = time.time() - start_time
            if duration > 0.5:  # Minimum recording duration
                self.audio_data.append(f"audio_chunk_{len(self.audio_data)}")


    def _transcribe_recorded_audio(self) -> str:
        """Transcribe the recorded audio data"""
        if not self.audio_data:
            return "No audio recorded"

        if not self.is_connected():
            gui_logger.warn(" No gRPC connection, using mock transcription")
            return f"Mock transcription: recorded {len(self.audio_data)} audio chunks"

        try:
            # Create audio stream for gRPC call
            audio_stream = self._create_audio_stream()

            # Call speech-to-text service
            response = self.stub.SpeechToText(audio_stream)

            if response.response.success:
                return response.transcript
            else:
                gui_logger.error(f" Transcription failed: {response.response.message}")
                return f"Transcription error: {response.response.message}"

        except Exception as e:
            gui_logger.error(f" gRPC transcription error: {e}")
            return f"Transcription error: {str(e)}"

    def _create_audio_stream(self) -> Iterator:
        """Create audio stream for gRPC call with real audio data"""
        if not hasattr(common_pb2, 'StreamChunk'):
            gui_logger.warn(" StreamChunk not available, using mock stream")
            return iter([])

        chunks = []

        # Process real audio data if available
        if self.audio_data and isinstance(self.audio_data[0], bytes):
            # Real audio data (bytes)
            audio_bytes = self.audio_data[0]

            # Split large audio into smaller chunks for streaming
            chunk_size = 4096  # 4KB chunks
            sequence = 1

            for i in range(0, len(audio_bytes), chunk_size):
                chunk_data = audio_bytes[i:i + chunk_size]
                is_final = (i + chunk_size) >= len(audio_bytes)

                chunk = common_pb2.StreamChunk()
                chunk.stream_id = "chat_audio_recording"
                chunk.sequence_number = sequence
                chunk.type = getattr(common_pb2, 'CHUNK_TYPE_DATA', 1)
                chunk.data = chunk_data
                chunk.is_final = is_final
                chunk.status = getattr(common_pb2, 'CHUNK_STATUS_COMPLETE', 1)

                chunks.append(chunk)
                sequence += 1


        else:
            # Fallback to mock data for compatibility
            gui_logger.warn(" Using mock audio data for gRPC call")
            chunk = common_pb2.StreamChunk()
            chunk.stream_id = "chat_audio_recording"
            chunk.sequence_number = 1
            chunk.type = getattr(common_pb2, 'CHUNK_TYPE_DATA', 1)
            chunk.data = b"mock_audio_data"
            chunk.is_final = True
            chunk.status = getattr(common_pb2, 'CHUNK_STATUS_COMPLETE', 1)
            chunks.append(chunk)

        return iter(chunks)

    def transcribe_audio(self, audio_data: bytes) -> str:
        """Transcribe provided audio data to text"""
        if not self.is_connected():
            gui_logger.warn(" No gRPC connection for transcription")
            return "Service unavailable"

        try:
            # Validate audio data
            if not audio_data or len(audio_data) < 100:
                gui_logger.warn(" Audio data too small or empty")
                return "No valid audio data"

            # Create stream chunks with proper chunking for large audio
            if not hasattr(common_pb2, 'StreamChunk'):
                return "Proto clients not available"

            chunks = []
            chunk_size = 4096  # 4KB chunks
            sequence = 1

            for i in range(0, len(audio_data), chunk_size):
                chunk_data = audio_data[i:i + chunk_size]
                is_final = (i + chunk_size) >= len(audio_data)

                chunk = common_pb2.StreamChunk()
                chunk.stream_id = "chat_audio_direct"
                chunk.sequence_number = sequence
                chunk.type = getattr(common_pb2, 'CHUNK_TYPE_DATA', 1)
                chunk.data = chunk_data
                chunk.is_final = is_final
                chunk.status = getattr(common_pb2, 'CHUNK_STATUS_COMPLETE', 1)

                chunks.append(chunk)
                sequence += 1


            # Call speech-to-text service
            response = self.stub.SpeechToText(iter(chunks))

            if response.response.success:
                transcript = response.transcript.strip()
                return transcript
            else:
                error_msg = response.response.message
                gui_logger.error(f" Transcription failed: {error_msg}")
                return f"Error: {error_msg}"

        except Exception as e:
            gui_logger.error(f" Direct transcription error: {e}")
            return f"Transcription error: {str(e)}"

    def get_audio_info(self) -> dict:
        """Get information about current audio setup"""
        info = {
            'grpc_connected': self.is_connected(),
            'audio_capture_available': AUDIO_CAPTURE_AVAILABLE,
            'real_audio_enabled': self.audio_capture is not None,
            'host': self.host,
            'port': self.port
        }

        if self.audio_capture and AUDIO_CAPTURE_AVAILABLE:
            try:
                devices = self.audio_capture.get_available_devices()
                info['available_devices'] = len(devices)
                info['device_names'] = [d['name'] for d in devices[:3]]  # First 3
            except:
                info['available_devices'] = 0
                info['device_names'] = []

        return info

    def close(self):
        """Close gRPC connection and cleanup audio resources"""
        if self.is_recording:
            self.stop_recording()

        # Cleanup audio capture
        if self.audio_capture:
            self.audio_capture.cleanup()
            self.audio_capture = None

        if self.channel:
            self.channel.close()
