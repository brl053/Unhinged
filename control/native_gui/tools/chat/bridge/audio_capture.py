"""
Audio Capture Module for Real-time Microphone Recording
Provides PyAudio-based audio capture for speech-to-text integration.
"""

import pyaudio
import wave
import threading
import time
import io
import collections
import numpy as np
from typing import Optional, Iterator, Callable, Deque
from dataclasses import dataclass


@dataclass
class AudioConfig:
    """Audio capture configuration"""
    sample_rate: int = 16000  # Whisper-compatible sample rate
    channels: int = 1         # Mono audio
    format: int = pyaudio.paInt16  # 16-bit PCM
    chunk_size: int = 1024    # Buffer size
    record_seconds: float = 3.0  # Default recording duration
    buffer_size: int = 100    # Circular buffer size (chunks)
    silence_threshold: float = 0.01  # Silence detection threshold
    noise_gate: bool = True   # Enable noise gate


class AudioCapture:
    """Real-time audio capture using PyAudio with advanced buffering"""

    def __init__(self, config: Optional[AudioConfig] = None):
        self.config = config or AudioConfig()
        self.pyaudio_instance = None
        self.stream = None
        self.is_recording = False

        # Advanced buffering system
        self.audio_buffer: Deque[bytes] = collections.deque(maxlen=self.config.buffer_size)
        self.circular_buffer: Deque[bytes] = collections.deque(maxlen=self.config.buffer_size)
        self.recording_thread = None
        self.buffer_lock = threading.Lock()

        # Callbacks and monitoring
        self.on_audio_data: Optional[Callable[[bytes], None]] = None
        self.on_silence_detected: Optional[Callable[[], None]] = None
        self.on_voice_detected: Optional[Callable[[], None]] = None

        # Audio level monitoring
        self.current_level = 0.0
        self.peak_level = 0.0
        self.silence_duration = 0.0

        # Initialize PyAudio
        self._initialize_pyaudio()
    
    def _initialize_pyaudio(self):
        """Initialize PyAudio instance with comprehensive error handling"""
        try:
            self.pyaudio_instance = pyaudio.PyAudio()

            # Check for available input devices
            device_count = self.pyaudio_instance.get_device_count()
            input_devices = []

            for i in range(device_count):
                try:
                    device_info = self.pyaudio_instance.get_device_info_by_index(i)
                    if device_info['maxInputChannels'] > 0:
                        input_devices.append({
                            'index': i,
                            'name': device_info['name'],
                            'channels': device_info['maxInputChannels'],
                            'sample_rate': device_info['defaultSampleRate']
                        })
                except Exception as device_error:
                    print(f"⚠️ Error checking device {i}: {device_error}")
                    continue

            if not input_devices:
                raise RuntimeError("No audio input devices found. Check microphone connections and permissions.")

            print(f"🎤 Found {len(input_devices)} audio input device(s)")
            for device in input_devices[:3]:  # Show first 3 devices
                print(f"   - {device['name']} ({device['channels']} channels)")

        except ImportError as e:
            raise RuntimeError(f"PyAudio not installed: {e}. Install with: pip install pyaudio")
        except OSError as e:
            if "No such file or directory" in str(e):
                raise RuntimeError(f"Audio system not available: {e}. Install system audio libraries.")
            else:
                raise RuntimeError(f"Audio system error: {e}")
        except Exception as e:
            print(f"❌ Failed to initialize PyAudio: {e}")
            raise RuntimeError(f"Audio initialization failed: {e}")
    
    def get_available_devices(self) -> list:
        """Get list of available audio input devices"""
        if not self.pyaudio_instance:
            return []
            
        devices = []
        device_count = self.pyaudio_instance.get_device_count()
        
        for i in range(device_count):
            try:
                device_info = self.pyaudio_instance.get_device_info_by_index(i)
                if device_info['maxInputChannels'] > 0:
                    devices.append({
                        'index': i,
                        'name': device_info['name'],
                        'channels': device_info['maxInputChannels'],
                        'sample_rate': int(device_info['defaultSampleRate'])
                    })
            except Exception as e:
                print(f"⚠️ Error getting device {i}: {e}")
                
        return devices
    
    def start_recording(self, duration: Optional[float] = None) -> bool:
        """Start audio recording with comprehensive error handling"""
        if self.is_recording:
            print("⚠️ Already recording")
            return False

        if not self.pyaudio_instance:
            print("❌ PyAudio not initialized")
            return False

        try:
            # Clear previous buffer
            self.audio_buffer.clear()
            self.circular_buffer.clear()
            self.reset_peak_level()

            # Test device availability first
            try:
                test_stream = self.pyaudio_instance.open(
                    format=self.config.format,
                    channels=self.config.channels,
                    rate=self.config.sample_rate,
                    input=True,
                    frames_per_buffer=self.config.chunk_size,
                    start=False  # Don't start immediately
                )
                test_stream.close()
            except Exception as test_error:
                raise RuntimeError(f"Audio device test failed: {test_error}")

            # Open audio stream for real recording
            self.stream = self.pyaudio_instance.open(
                format=self.config.format,
                channels=self.config.channels,
                rate=self.config.sample_rate,
                input=True,
                frames_per_buffer=self.config.chunk_size
            )

            self.is_recording = True
            record_duration = duration or self.config.record_seconds

            # Start recording thread
            self.recording_thread = threading.Thread(
                target=self._recording_loop,
                args=(record_duration,),
                daemon=True
            )
            self.recording_thread.start()

            print(f"🎤 Started recording for {record_duration:.1f} seconds...")
            return True

        except OSError as e:
            error_msg = f"Audio device error: {e}"
            if "Device unavailable" in str(e):
                error_msg += " (Microphone may be in use by another application)"
            elif "Permission denied" in str(e):
                error_msg += " (Microphone permission denied)"
            print(f"❌ {error_msg}")
            self.is_recording = False
            return False

        except Exception as e:
            print(f"❌ Failed to start recording: {e}")
            self.is_recording = False
            return False
    
    def stop_recording(self) -> bytes:
        """Stop recording and return audio data as WAV bytes"""
        if not self.is_recording:
            print("⚠️ Not currently recording")
            return b""
            
        self.is_recording = False
        
        # Wait for recording thread to finish
        if self.recording_thread and self.recording_thread.is_alive():
            self.recording_thread.join(timeout=1.0)
        
        # Close audio stream
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        
        # Convert buffer to WAV bytes
        audio_data = self._buffer_to_wav()
        print(f"🎤 Recording stopped. Captured {len(audio_data)} bytes")
        
        return audio_data
    
    def _recording_loop(self, duration: float):
        """Advanced recording loop with real-time audio analysis"""
        start_time = time.time()
        silence_start = None

        try:
            while self.is_recording and (time.time() - start_time) < duration:
                if self.stream:
                    # Read audio data
                    data = self.stream.read(self.config.chunk_size, exception_on_overflow=False)

                    # Calculate audio level
                    audio_level = self._calculate_audio_level(data)
                    self.current_level = audio_level
                    self.peak_level = max(self.peak_level, audio_level)

                    # Noise gate and silence detection
                    is_voice = audio_level > self.config.silence_threshold

                    if is_voice:
                        if silence_start is not None:
                            # Voice detected after silence
                            if self.on_voice_detected:
                                self.on_voice_detected()
                            silence_start = None

                        # Add to both buffers
                        with self.buffer_lock:
                            self.audio_buffer.append(data)
                            self.circular_buffer.append(data)
                    else:
                        # Silence detected
                        if silence_start is None:
                            silence_start = time.time()

                        self.silence_duration = time.time() - silence_start

                        if not self.config.noise_gate:
                            # Still record silence if noise gate is disabled
                            with self.buffer_lock:
                                self.audio_buffer.append(data)
                                self.circular_buffer.append(data)

                        # Trigger silence callback after 1 second of silence
                        if self.silence_duration > 1.0 and self.on_silence_detected:
                            self.on_silence_detected()

                    # Call data callback
                    if self.on_audio_data:
                        self.on_audio_data(data)

                time.sleep(0.001)  # Small delay to prevent CPU spinning

        except Exception as e:
            print(f"❌ Error in recording loop: {e}")
        finally:
            self.is_recording = False

    def _calculate_audio_level(self, data: bytes) -> float:
        """Calculate RMS audio level from raw audio data"""
        try:
            # Convert bytes to numpy array
            audio_array = np.frombuffer(data, dtype=np.int16)

            # Calculate RMS level
            rms = np.sqrt(np.mean(audio_array.astype(np.float32) ** 2))

            # Normalize to 0-1 range
            normalized_level = min(rms / 32768.0, 1.0)

            return normalized_level

        except Exception as e:
            print(f"⚠️ Error calculating audio level: {e}")
            return 0.0

    def get_current_level(self) -> float:
        """Get current audio input level (0.0 to 1.0)"""
        return self.current_level

    def get_peak_level(self) -> float:
        """Get peak audio level since recording started"""
        return self.peak_level

    def reset_peak_level(self):
        """Reset peak level counter"""
        self.peak_level = 0.0
    
    def _buffer_to_wav(self) -> bytes:
        """Convert audio buffer to WAV format bytes"""
        if not self.audio_buffer:
            return b""
            
        # Combine all audio chunks
        audio_data = b''.join(self.audio_buffer)
        
        # Create WAV file in memory
        wav_buffer = io.BytesIO()
        
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(self.config.channels)
            wav_file.setsampwidth(self.pyaudio_instance.get_sample_size(self.config.format))
            wav_file.setframerate(self.config.sample_rate)
            wav_file.writeframes(audio_data)
        
        wav_bytes = wav_buffer.getvalue()
        wav_buffer.close()
        
        return wav_bytes
    
    def get_audio_stream(self) -> Iterator[bytes]:
        """Get real-time audio stream for gRPC streaming"""
        chunk_duration = self.config.chunk_size / self.config.sample_rate

        with self.buffer_lock:
            buffer_copy = list(self.audio_buffer)

        for chunk in buffer_copy:
            yield chunk
            time.sleep(chunk_duration)  # Simulate real-time streaming

    def get_live_audio_stream(self) -> Iterator[bytes]:
        """Get live audio stream that yields data as it's captured"""
        last_buffer_size = 0

        while self.is_recording:
            with self.buffer_lock:
                current_size = len(self.audio_buffer)

                # Yield new chunks since last check
                if current_size > last_buffer_size:
                    new_chunks = list(self.audio_buffer)[last_buffer_size:]
                    for chunk in new_chunks:
                        yield chunk
                    last_buffer_size = current_size

            time.sleep(0.01)  # Check for new data every 10ms

    def get_circular_buffer_stream(self) -> Iterator[bytes]:
        """Get audio stream from circular buffer (last N chunks)"""
        with self.buffer_lock:
            buffer_copy = list(self.circular_buffer)

        chunk_duration = self.config.chunk_size / self.config.sample_rate

        for chunk in buffer_copy:
            yield chunk
            time.sleep(chunk_duration)

    def create_grpc_stream_chunks(self) -> Iterator[dict]:
        """Create gRPC-compatible stream chunks with metadata"""
        chunk_id = 0

        for audio_chunk in self.get_audio_stream():
            chunk_id += 1

            # Create StreamChunk-compatible data
            stream_chunk = {
                'chunk_id': chunk_id,
                'data': audio_chunk,
                'timestamp': int(time.time() * 1000),  # Milliseconds
                'metadata': {
                    'sample_rate': self.config.sample_rate,
                    'channels': self.config.channels,
                    'format': 'pcm_s16le',
                    'chunk_size': len(audio_chunk),
                    'audio_level': self.current_level
                }
            }

            yield stream_chunk

    def export_to_file(self, filename: str) -> bool:
        """Export captured audio to WAV file"""
        try:
            audio_data = self._buffer_to_wav()

            if not audio_data:
                print("⚠️ No audio data to export")
                return False

            with open(filename, 'wb') as f:
                f.write(audio_data)

            print(f"✅ Audio exported to {filename} ({len(audio_data)} bytes)")
            return True

        except Exception as e:
            print(f"❌ Failed to export audio: {e}")
            return False
    
    def cleanup(self):
        """Clean up PyAudio resources"""
        if self.is_recording:
            self.stop_recording()
            
        if self.stream:
            self.stream.close()
            
        if self.pyaudio_instance:
            self.pyaudio_instance.terminate()
            self.pyaudio_instance = None
            
        print("🎤 Audio capture cleaned up")
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()


# Test function for standalone testing
def test_audio_capture():
    """Test audio capture functionality"""
    print("🎤 Testing audio capture...")
    
    try:
        capture = AudioCapture()
        devices = capture.get_available_devices()
        
        print(f"Available devices: {len(devices)}")
        for device in devices:
            print(f"  - {device['name']}")
        
        # Test recording
        if capture.start_recording(duration=2.0):
            time.sleep(2.5)  # Wait for recording to complete
            audio_data = capture.stop_recording()
            print(f"Captured {len(audio_data)} bytes of audio")
        
        capture.cleanup()
        print("✅ Audio capture test completed")
        
    except Exception as e:
        print(f"❌ Audio capture test failed: {e}")


if __name__ == "__main__":
    test_audio_capture()
