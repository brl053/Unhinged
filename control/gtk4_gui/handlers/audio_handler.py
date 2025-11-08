"""
Audio Handler for Unhinged Desktop GUI

This module handles all audio recording and transcription operations,
providing a clean interface for the UI layer.
"""

import logging
import subprocess
import tempfile
import threading
import time
from collections.abc import Callable
from enum import Enum
from pathlib import Path

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
        self._recording_process: subprocess.Popen | None = None
        self._temp_file: Path | None = None
        self._recording_thread: threading.Thread | None = None
        self._start_time: float | None = None

        # Callbacks for UI updates
        self._state_callback: Callable[[RecordingState], None] | None = None
        self._progress_callback: Callable[[float], None] | None = None
        self._result_callback: Callable[[str], None] | None = None
        self._error_callback: Callable[[Exception], None] | None = None

        # Real-time audio visualization
        self._visualization_bridge = AudioVisualizationBridge()

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

    def set_callbacks(self,
                     state_callback: Callable[[RecordingState], None] | None = None,
                     progress_callback: Callable[[float], None] | None = None,
                     result_callback: Callable[[str], None] | None = None,
                     error_callback: Callable[[Exception], None] | None = None):
        """Set callbacks for UI updates
        
        Args:
            state_callback: Called when recording state changes
            progress_callback: Called with recording progress (0.0 to 1.0)
            result_callback: Called with transcription result
            error_callback: Called when an error occurs
        """
        self._state_callback = state_callback
        self._progress_callback = progress_callback
        self._result_callback = result_callback
        self._error_callback = error_callback

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

            # NOTE: Disabled separate audio monitor to avoid device access conflicts
            # The visualizer will use simulated animation instead of real audio data
            # This prevents the "two processes accessing same device" issue
            # self._visualization_bridge.start_recording_visualization()

            logger.info(f"Started recording (continuous, no duration limit)")

        except Exception as e:
            self._cleanup()
            raise AudioRecordingError(f"Failed to start recording: {e}")

    def stop_recording(self) -> None:
        """Stop current recording"""
        if not self.is_recording:
            return

        try:
            if self._recording_process and self._recording_process.poll() is None:
                # Send SIGTERM for graceful shutdown (better than SIGINT for arecord)
                import signal
                self._recording_process.send_signal(signal.SIGTERM)

                # Wait for process to finish
                try:
                    self._recording_process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    # Force terminate if graceful shutdown fails
                    logger.warning("Graceful recording stop timed out, force terminating")
                    self._recording_process.terminate()
                    self._recording_process.wait(timeout=2)

            logger.info("Recording stopped")

        except Exception as e:
            logger.error(f"Error stopping recording: {e}")
            self._handle_error(AudioRecordingError(f"Failed to stop recording: {e}"))

    def _record_audio_continuous(self) -> None:
        """Record audio continuously until stopped (NO DURATION LIMIT)"""
        try:
            # Use arecord without duration - will be stopped by signal
            cmd = [
                'arecord',
                '-D', app_config.audio_device,
                '-f', app_config.audio_format,
                '-r', str(app_config.audio_sample_rate),
                '-c', str(app_config.audio_channels),
                '-t', 'wav',
                # NO duration - record until stopped
                str(self._temp_file)
            ]

            # Start recording process
            self._recording_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Monitor progress continuously
            self._monitor_recording_progress_continuous()

            # Wait for recording to complete
            stdout, stderr = self._recording_process.communicate()

            # Handle recording completion - arecord exits with non-zero when stopped by signal
            if self._recording_process.returncode != 0:
                # Check if this is a signal exit with valid file
                signal_messages = ["Aborted by signal", "Interrupted by signal", "Terminated"]
                is_signal_exit = any(msg in stderr for msg in signal_messages)

                if is_signal_exit and self._temp_file and self._temp_file.exists():
                    file_size = self._temp_file.stat().st_size
                    if file_size > 44:  # Valid WAV file
                        logger.info(f"Recording stopped by signal - file saved successfully ({file_size} bytes)")
                    else:
                        raise AudioRecordingError(f"Recording stopped by signal but file is too small: {file_size} bytes")
                else:
                    raise AudioRecordingError(f"Recording failed: {stderr}")

            # Validate recorded file
            self._validate_recorded_file()

            # NOTE: Visualization bridge stop is no longer needed since we disabled the monitor

            # Start transcription
            self._set_state(RecordingState.PROCESSING)
            self._transcribe_audio()

        except Exception as e:
            self._handle_error(e)

    def _monitor_recording_progress_continuous(self) -> None:
        """Monitor continuous recording progress (no duration limit)"""
        while self._recording_process and self._recording_process.poll() is None:
            # For continuous recording, we don't have a progress percentage
            # Just keep the UI updated that recording is active
            if self._progress_callback:
                # Send elapsed time instead of progress percentage
                elapsed = time.time() - self._start_time if self._start_time else 0
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

            # Notify UI of result
            if self._result_callback:
                self._result_callback(transcript)

            logger.info(f"Transcription completed: {len(transcript)} characters")

        except Exception as e:
            self._handle_error(e)

    def _set_state(self, new_state: RecordingState) -> None:
        """Update recording state and notify UI"""
        if self._state != new_state:
            self._state = new_state
            logger.debug(f"Recording state changed to: {new_state.value}")

            if self._state_callback:
                self._state_callback(new_state)

    def _handle_error(self, error: Exception) -> None:
        """Handle errors and notify UI"""
        logger.error(f"Audio handler error: {error}")

        self._cleanup()
        self._set_state(RecordingState.ERROR)

        if self._error_callback:
            self._error_callback(error)

    def _cleanup(self) -> None:
        """Clean up resources"""
        # Stop recording process if running
        if self._recording_process and self._recording_process.poll() is None:
            try:
                self._recording_process.terminate()
                self._recording_process.wait(timeout=2)
            except Exception as e:
                logger.warning(f"Error terminating recording process: {e}")

        self._recording_process = None
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
