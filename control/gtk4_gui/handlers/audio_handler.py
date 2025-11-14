"""
Audio Handler for Unhinged Desktop GUI

This module handles all audio recording and transcription operations,
providing a clean interface for the UI layer.
"""

import logging
import math
import os
import struct
import subprocess
import tempfile
import threading
import time
import sys
from collections.abc import Callable
from enum import Enum
from pathlib import Path

# Add utils to path for audio_utils import
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))

from audio_utils import calculate_rms_amplitude, get_best_format_for_device
from event_bus import get_event_bus, AudioEvents, Event

try:
    from .audio_monitor import AudioVisualizationBridge
    from .config import app_config
    from .exceptions import (
        AudioFileSizeError,
        AudioRecordingError,
        AudioTranscriptionError,
        ServiceUnavailableError,
    )
    from .service_connector import service_connector
except ImportError:
    # Fallback for direct execution
    from config import app_config
    from exceptions import (
        AudioFileSizeError,
        AudioRecordingError,
        AudioTranscriptionError,
        ServiceUnavailableError,
    )
    from service_connector import service_connector

    from .audio_monitor import AudioVisualizationBridge

logger = logging.getLogger(__name__)


class RecordingState(Enum):
    """States for audio recording"""
    IDLE = "idle"
    RECORDING = "recording"
    PROCESSING = "processing"
    ERROR = "error"


class AudioHandler:
    """Handles audio recording and transcription operations"""

    def __init__(self):
        self._state = RecordingState.IDLE
        self._recording_process: subprocess.Popen | None = None  # tee process
        self._arecord_process: subprocess.Popen | None = None  # arecord process
        self._temp_file: Path | None = None
        self._recording_thread: threading.Thread | None = None
        self._amplitude_thread: threading.Thread | None = None
        self._temp_pipe: Path | None = None
        self._start_time: float | None = None

        # Event bus for UI updates (replaces callbacks)
        self._event_bus = get_event_bus()

        # Real-time audio visualization
        self._visualization_bridge = AudioVisualizationBridge()

        # Legacy callback support (for backward compatibility)
        self._state_callback: Callable[[RecordingState], None] | None = None
        self._error_callback: Callable[[Exception], None] | None = None
        self._progress_callback: Callable[[float], None] | None = None

        # Audio format detection (done once during initialization)
        self._detected_format: str | None = None
        self._detected_sample_width: int | None = None
        self._initialize_audio_format()

    @property
    def state(self) -> RecordingState:
        """Get current recording state"""
        return self._state

    @property
    def is_recording(self) -> bool:
        """Check if currently recording"""
        return self._state == RecordingState.RECORDING

    @property
    def is_processing(self) -> bool:
        """Check if currently processing"""
        return self._state == RecordingState.PROCESSING

    @property
    def is_busy(self) -> bool:
        """Check if handler is busy (recording or processing)"""
        return self._state in [RecordingState.RECORDING, RecordingState.PROCESSING]

    def subscribe_to_events(self, event_type: str, callback: Callable[[Event], None]) -> Callable[[], None]:
        """Subscribe to audio events via event bus

        Args:
            event_type: Event type (use AudioEvents constants)
            callback: Function to call when event is emitted

        Returns:
            Unsubscribe function
        """
        return self._event_bus.subscribe(event_type, callback)

    def _initialize_audio_format(self) -> None:
        """Initialize audio format detection during handler setup.

        This runs once during __init__ to avoid per-recording overhead.
        Format detection results are cached globally.
        """
        try:
            self._detected_format = get_best_format_for_device(
                app_config.audio_device,
                app_config.audio_format
            )
            self._detected_sample_width = self._get_sample_width(self._detected_format)
            logger.info(
                f"Audio handler initialized: device={app_config.audio_device} "
                f"format={self._detected_format} sample_width={self._detected_sample_width}bytes"
            )
        except Exception as e:
            logger.warning(f"Failed to detect audio format: {e}, using defaults")
            self._detected_format = app_config.audio_format
            self._detected_sample_width = 2
            logger.info(
                f"Audio handler initialized (fallback): device={app_config.audio_device} "
                f"format={self._detected_format} sample_width={self._detected_sample_width}bytes"
            )

    def set_voice_visualizer(self, visualizer) -> None:
        """Connect voice visualizer for real-time feedback"""
        self._visualization_bridge.set_voice_visualizer(visualizer)

    def start_recording(self, duration: int | None = None) -> None:
        """Start audio recording
        
        Args:
            duration: Recording duration in seconds (defaults to config value)
            
        Raises:
            AudioRecordingError: If recording cannot be started
        """
        if self.is_busy:
            raise AudioRecordingError("Already recording or processing")

        # Check if speech-to-text service is available
        if not service_connector.check_service_health('speech_to_text'):
            raise ServiceUnavailableError('speech_to_text', 'unknown')

        # IGNORE duration - record continuously until stopped

        try:
            # Create temporary file
            temp_fd, temp_path = tempfile.mkstemp(suffix='.wav')
            self._temp_file = Path(temp_path)

            # Close the file descriptor since arecord will write to it
            import os
            os.close(temp_fd)

            # Start recording in background thread (NO DURATION LIMIT)
            self._recording_thread = threading.Thread(
                target=self._record_audio_continuous,
                daemon=True
            )

            self._set_state(RecordingState.RECORDING)
            self._start_time = time.time()
            self._recording_thread.start()

            logger.info(f"Started recording (continuous, no duration limit)")

        except Exception as e:
            self._cleanup()
            raise AudioRecordingError(f"Failed to start recording: {e}")

    def stop_recording(self) -> None:
        """Stop current recording"""
        if not self.is_recording:
            return

        try:
            # Send SIGTERM to arecord process (not tee) for graceful shutdown
            if self._arecord_process and self._arecord_process.poll() is None:
                import signal
                self._arecord_process.send_signal(signal.SIGTERM)

                # Wait for arecord to finish
                try:
                    self._arecord_process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    # Force terminate if graceful shutdown fails
                    logger.warning("Graceful arecord stop timed out, force terminating")
                    self._arecord_process.terminate()
                    self._arecord_process.wait(timeout=2)

            logger.info("Recording stopped")

        except Exception as e:
            logger.error(f"Error stopping recording: {e}")
            self._handle_error(AudioRecordingError(f"Failed to stop recording: {e}"))

    def _record_audio_continuous(self) -> None:
        """Record audio continuously until stopped using pipe-based architecture.

        Uses a named pipe to split the audio stream:
        - One copy goes to the WAV file for transcription
        - One copy goes to amplitude extraction for visualization
        This ensures only ONE arecord process accesses the device.

        Format detection was performed during __init__ to avoid per-recording overhead.
        """
        try:
            # Create named pipe for amplitude extraction
            import tempfile as tf
            pipe_dir = Path(tf.gettempdir())
            self._temp_pipe = pipe_dir / f"audio_pipe_{os.getpid()}_{int(time.time() * 1000)}"

            try:
                os.mkfifo(str(self._temp_pipe))
                logger.debug(f"Created named pipe: {self._temp_pipe}")
            except FileExistsError:
                self._temp_pipe.unlink()
                os.mkfifo(str(self._temp_pipe))

            # Start amplitude extraction thread (reads from pipe)
            self._amplitude_thread = threading.Thread(
                target=self._extract_amplitude_from_pipe,
                daemon=False
            )
            self._amplitude_thread.start()

            # Use arecord with tee to split stream: one to file, one to pipe
            # arecord outputs raw audio to stdout, tee splits it
            arecord_cmd = [
                'arecord',
                '-D', app_config.audio_device,
                '-f', self._detected_format,
                '-r', str(app_config.audio_sample_rate),
                '-c', str(app_config.audio_channels),
                '-t', 'raw',  # Output raw audio (not WAV) for amplitude extraction
                '-'  # Output to stdout
            ]

            tee_cmd = [
                'tee',
                str(self._temp_pipe)  # First copy to pipe for amplitude extraction
            ]

            # Start arecord process - capture stderr to detect device/format errors
            self._arecord_process = subprocess.Popen(
                arecord_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Start tee process to split the stream
            # tee writes raw audio to pipe AND to file
            # We'll convert raw to WAV after recording completes
            self._recording_process = subprocess.Popen(
                tee_cmd,
                stdin=self._arecord_process.stdout,
                stdout=open(str(self._temp_file), 'wb'),
                stderr=subprocess.PIPE
            )

            # Close the reference in parent so pipe closes when arecord exits
            self._arecord_process.stdout.close()

            # Monitor progress continuously
            self._monitor_recording_progress_continuous()

            # Wait for tee process to complete
            tee_stdout, tee_stderr = self._recording_process.communicate()

            # Wait for arecord process to complete and capture its stderr
            arecord_stdout, arecord_stderr = self._arecord_process.communicate()

            # Wait for amplitude thread to finish
            if self._amplitude_thread and self._amplitude_thread.is_alive():
                self._amplitude_thread.join(timeout=5)

            # Check if arecord process failed (this is the actual recording process)
            # When arecord is terminated by signal (SIGTERM), it exits with code 1 and writes "Aborted by signal" to stderr
            # This is NORMAL when user stops recording - not an error
            # Only raise error if it's an actual failure (format error, device error, etc.)
            if self._arecord_process.returncode is not None and self._arecord_process.returncode != 0:
                arecord_stderr_str = arecord_stderr.decode('utf-8', errors='replace').strip() if arecord_stderr else "Unknown error"

                # Check if this is a signal termination (normal) vs actual error
                signal_messages = ["Aborted by signal", "Interrupted by signal", "Terminated"]
                is_signal_exit = any(msg in arecord_stderr_str for msg in signal_messages)

                if not is_signal_exit:
                    # This is an actual error (format error, device error, etc.)
                    raise AudioRecordingError(
                        f"Recording failed: {arecord_stderr_str}",
                        device=app_config.audio_device,
                        details={"arecord_stderr": arecord_stderr_str}
                    )
                # If it's a signal exit, continue - this is normal

            # Check if tee process failed (should not happen if arecord succeeded)
            if self._recording_process.returncode != 0:
                signal_messages = ["Aborted by signal", "Interrupted by signal", "Terminated"]
                is_signal_exit = any(msg in tee_stderr for msg in signal_messages) if tee_stderr else False

                if is_signal_exit and self._temp_file and self._temp_file.exists():
                    file_size = self._temp_file.stat().st_size
                    if file_size > 44:
                        logger.info(f"Recording stopped by signal - file saved successfully ({file_size} bytes)")
                    else:
                        raise AudioRecordingError(f"Recording stopped by signal but file is too small: {file_size} bytes")
                else:
                    tee_stderr_str = tee_stderr.decode('utf-8', errors='replace').strip() if tee_stderr else "Unknown error"
                    raise AudioRecordingError(f"Recording failed: {tee_stderr_str}")

            # Both processes succeeded - validate the recorded file
            if not self._temp_file or not self._temp_file.exists():
                raise AudioRecordingError("Recording failed: no output file created")

            file_size = self._temp_file.stat().st_size
            if file_size <= 4:  # Raw audio should be at least a few bytes
                raise AudioRecordingError(f"Recording file too small: {file_size} bytes")

            logger.info(f"Recording completed successfully ({file_size} bytes of raw audio)")

            # Convert raw audio to WAV format for transcription
            _convert_raw_to_wav(
                self._temp_file,
                self._temp_file,  # Overwrite with WAV version
                app_config.audio_sample_rate,
                app_config.audio_channels,
                self._detected_sample_width or 2
            )

            # Validate recorded file
            self._validate_recorded_file()

            # Start transcription
            self._set_state(RecordingState.PROCESSING)
            self._transcribe_audio()

        except Exception as e:
            self._handle_error(e)
        finally:
            # Clean up named pipe
            if self._temp_pipe and self._temp_pipe.exists():
                try:
                    self._temp_pipe.unlink()
                    logger.debug(f"Cleaned up named pipe: {self._temp_pipe}")
                except Exception as e:
                    logger.warning(f"Failed to clean up named pipe: {e}")

    def _extract_amplitude_from_pipe(self) -> None:
        """Extract amplitude data from the named pipe and send to visualizer.

        This runs in a separate thread and reads audio data from the pipe
        that is being written to by the tee process.
        """
        try:
            if not self._temp_pipe or not self._temp_pipe.exists():
                logger.warning("Named pipe does not exist")
                return

            # Open pipe for reading (non-blocking would be better but Python doesn't support it easily)
            with open(str(self._temp_pipe), 'rb') as pipe:
                chunk_size = 1024  # 1024 bytes = 512 samples for S16_LE

                while self._state == RecordingState.RECORDING:
                    try:
                        # Read audio chunk from pipe
                        audio_chunk = pipe.read(chunk_size)

                        if not audio_chunk:
                            break

                        # Calculate amplitude from raw audio data
                        amplitude = self._calculate_amplitude_from_chunk(audio_chunk)

                        # Send to visualizer
                        if self._visualization_bridge and self._visualization_bridge.voice_visualizer:
                            self._visualization_bridge.voice_visualizer.set_amplitude(amplitude)

                    except Exception as e:
                        logger.warning(f"Error reading from amplitude pipe: {e}")
                        break

        except Exception as e:
            logger.error(f"Error in amplitude extraction: {e}")

    def _calculate_amplitude_from_chunk(self, audio_data: bytes) -> float:
        """Calculate RMS amplitude from raw audio chunk."""
        return calculate_rms_amplitude(audio_data)

    def _get_sample_width(self, format_str: str) -> int:
        """Get sample width in bytes for a given audio format.

        Args:
            format_str: Audio format string (e.g., 'S16_LE', 'S24_3LE', 'S32_LE')

        Returns:
            Sample width in bytes
        """
        format_map = {
            'U8': 1,
            'S8': 1,
            'S16_LE': 2,
            'S16_BE': 2,
            'U16_LE': 2,
            'U16_BE': 2,
            'S24_LE': 3,
            'S24_BE': 3,
            'S24_3LE': 3,
            'S24_3BE': 3,
            'S32_LE': 4,
            'S32_BE': 4,
            'U32_LE': 4,
            'U32_BE': 4,
        }
        return format_map.get(format_str, 2)  # Default to 2 bytes (S16_LE)

    def _monitor_recording_progress_continuous(self) -> None:
        """Monitor continuous recording progress (no duration limit)"""
        while self._recording_process and self._recording_process.poll() is None:
            # For continuous recording, we don't have a progress percentage
            # Just keep the UI updated that recording is active
            elapsed = time.time() - self._start_time if self._start_time else 0

            # Emit event via event bus
            self._event_bus.emit_simple(AudioEvents.AMPLITUDE_UPDATED, {"elapsed": elapsed})

            # Legacy callback support
            if self._progress_callback:
                self._progress_callback(elapsed)

            time.sleep(0.1)  # Update every 100ms

    def _validate_recorded_file(self) -> None:
        """Validate the recorded audio file"""
        if not self._temp_file or not self._temp_file.exists():
            raise AudioRecordingError("Recording file not found")

        # Wait for file system to flush
        time.sleep(0.5)

        file_size = self._temp_file.stat().st_size
        min_size = 44  # Minimum WAV header size

        if file_size < min_size:
            raise AudioFileSizeError(file_size, min_size=min_size)

        logger.debug(f"Recorded file size: {file_size} bytes")

    def _transcribe_audio(self) -> None:
        """Transcribe the recorded audio"""
        try:
            if not self._temp_file:
                raise AudioTranscriptionError("No audio file to transcribe")

            # Use service connector for transcription
            transcript = service_connector.transcribe_audio(self._temp_file)

            # Clean up temp file
            self._cleanup_temp_file()

            # Set state back to idle
            self._set_state(RecordingState.IDLE)

            # Notify UI of result via event bus
            self._event_bus.emit_simple(AudioEvents.AMPLITUDE_UPDATED, {"transcript": transcript})

            logger.info(f"Transcription completed: {len(transcript)} characters")

        except Exception as e:
            self._handle_error(e)

    def _set_state(self, new_state: RecordingState) -> None:
        """Update recording state and notify UI via event bus"""
        if self._state != new_state:
            self._state = new_state
            logger.debug(f"Recording state changed to: {new_state.value}")

            # Emit event via event bus
            event_type = (AudioEvents.RECORDING_STARTED if new_state == RecordingState.RECORDING
                         else AudioEvents.RECORDING_STOPPED)
            self._event_bus.emit_simple(event_type, {"state": new_state.value})

            # Legacy callback support
            if self._state_callback:
                self._state_callback(new_state)

    def _handle_error(self, error: Exception) -> None:
        """Handle errors and notify UI via event bus

        Emits full exception object with details for proper error diagnostics.
        Preserves device context and stderr output for debugging.
        """
        logger.error(f"Audio handler error: {error}")

        self._cleanup()
        self._set_state(RecordingState.ERROR)

        # Emit error event via event bus with full exception details
        # This preserves device context, stderr output, and other metadata
        error_data = {
            "error": str(error),
            "type": error.__class__.__name__,
            "message": getattr(error, 'message', str(error)),
            "device": getattr(error, 'device', None),
            "details": getattr(error, 'details', {})
        }
        self._event_bus.emit_simple(AudioEvents.ERROR, error_data)

        # Legacy callback support
        if self._error_callback:
            self._error_callback(error)

    def _cleanup(self) -> None:
        """Clean up resources"""
        # Stop arecord process if running
        if self._arecord_process and self._arecord_process.poll() is None:
            try:
                self._arecord_process.terminate()
                self._arecord_process.wait(timeout=2)
            except Exception as e:
                logger.warning(f"Error terminating arecord process: {e}")

        # Stop tee process if running
        if self._recording_process and self._recording_process.poll() is None:
            try:
                self._recording_process.terminate()
                self._recording_process.wait(timeout=2)
            except Exception as e:
                logger.warning(f"Error terminating tee process: {e}")

        # Wait for amplitude thread to finish
        if self._amplitude_thread and self._amplitude_thread.is_alive():
            try:
                self._amplitude_thread.join(timeout=2)
            except Exception as e:
                logger.warning(f"Error waiting for amplitude thread: {e}")

        # Clean up named pipe
        if self._temp_pipe and self._temp_pipe.exists():
            try:
                self._temp_pipe.unlink()
            except Exception as e:
                logger.warning(f"Error cleaning up named pipe: {e}")

        self._arecord_process = None
        self._recording_process = None
        self._amplitude_thread = None
        self._temp_pipe = None
        self._cleanup_temp_file()
        self._recording_thread = None
        self._start_time = None

    def _cleanup_temp_file(self) -> None:
        """Clean up temporary audio file"""
        if self._temp_file and self._temp_file.exists():
            try:
                self._temp_file.unlink()
                logger.debug(f"Cleaned up temp file: {self._temp_file}")
            except Exception as e:
                logger.warning(f"Failed to clean up temp file: {e}")

        self._temp_file = None

    def get_available_devices(self) -> dict[str, str]:
        """Get list of available audio input devices
        
        Returns:
            Dictionary mapping device names to device identifiers
        """
        devices = {}

        try:
            # Use arecord -l to list devices
            result = subprocess.run(
                ['arecord', '-l'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                # Parse arecord output
                import re
                for line in result.stdout.split('\n'):
                    match = re.match(r'card (\d+): (.+?) \[(.+?)\], device (\d+): (.+?) \[(.+?)\]', line)
                    if match:
                        card_num, card_name, card_desc, device_num, device_name, device_desc = match.groups()
                        device_id = f"hw:{card_num},{device_num}"
                        device_display = f"{card_name} - {device_name}"
                        devices[device_display] = device_id

            # Add default devices
            devices["Default (PipeWire)"] = "pipewire"
            devices["Default (ALSA)"] = "default"

        except Exception as e:
            logger.warning(f"Failed to enumerate audio devices: {e}")
            # Fallback to common devices
            devices = {
                "Default (PipeWire)": "pipewire",
                "Default (ALSA)": "default"
            }

        return devices

    def test_recording(self, duration: int = 2) -> bool:
        """Test if recording works with current settings
        
        Args:
            duration: Test recording duration in seconds
            
        Returns:
            True if test recording succeeds
        """
        if self.is_busy:
            return False

        try:
            # Create temporary file for test
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                test_file = Path(f.name)

            # Build test command
            cmd = [
                'arecord',
                '-D', app_config.audio_device,
                '-f', app_config.audio_format,
                '-r', str(app_config.audio_sample_rate),
                '-c', str(app_config.audio_channels),
                '-t', 'wav',
                '-d', str(duration),
                str(test_file)
            ]

            # Run test recording
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=duration + 5)

            # Check if successful
            success = (
                result.returncode == 0 and
                test_file.exists() and
                test_file.stat().st_size > 44  # Minimum WAV size
            )

            # Clean up
            if test_file.exists():
                test_file.unlink()

            return success

        except Exception as e:
            logger.warning(f"Recording test failed: {e}")
            return False


def _convert_raw_to_wav(raw_file: Path, wav_file: Path, sample_rate: int, channels: int, sample_width: int = 2) -> None:
    """Convert raw audio data to WAV format.

    Args:
        raw_file: Path to raw audio file
        wav_file: Path to output WAV file
        sample_rate: Sample rate in Hz
        channels: Number of channels
        sample_width: Sample width in bytes (2 for S16_LE)
    """
    import wave

    try:
        # Read raw audio data
        with open(raw_file, 'rb') as f:
            raw_data = f.read()

        # Write WAV file
        with wave.open(str(wav_file), 'wb') as wav:
            wav.setnchannels(channels)
            wav.setsampwidth(sample_width)
            wav.setframerate(sample_rate)
            wav.writeframes(raw_data)

        logger.debug(f"Converted raw audio to WAV: {wav_file}")
    except Exception as e:
        logger.error(f"Failed to convert raw audio to WAV: {e}")
        raise
