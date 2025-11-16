"""
Audio Handler for Unhinged Desktop GUI - Refactored Coordinator

Coordinates audio recording and transcription by delegating to specialized
components. Maintains backward compatibility with existing UI callbacks.
"""

import logging
import os
import sys
import tempfile
import threading
import time
from collections.abc import Callable
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))
sys.path.insert(0, str(Path(__file__).parent))

from audio_device_manager import AudioDeviceManager
from audio_processor import AudioProcessor
from audio_recorder import AudioRecorder
from audio_transcriber import AudioTranscriber
from audio_types import RecordingConfig, RecordingState
from audio_utils import get_best_format_for_device
from event_bus import AudioEvents, Event, get_event_bus

try:
    from .audio_monitor import AudioVisualizationBridge
    from .config import app_config
    from .exceptions import AudioRecordingError
except ImportError:
    from audio_monitor import AudioVisualizationBridge
    from config import app_config
    from exceptions import AudioRecordingError

# Import direct transcription service
import sys
from pathlib import Path as PathlibPath

project_root = PathlibPath(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from libs.services import TranscriptionService

logger = logging.getLogger(__name__)


class AudioHandler:
    """Coordinates audio recording and transcription operations."""

    def __init__(self):
        """Initialize handler with component delegation."""
        self._state = RecordingState.IDLE
        self._temp_file: Path | None = None
        self._recording_thread: threading.Thread | None = None
        self._start_time: float | None = None

        # Event bus for UI updates
        self._event_bus = get_event_bus()

        # Real-time audio visualization
        self._visualization_bridge = AudioVisualizationBridge()

        # Legacy callback support
        self._state_callback: Callable[[RecordingState], None] | None = None
        self._result_callback: Callable[[str], None] | None = None
        self._error_callback: Callable[[Exception], None] | None = None
        self._progress_callback: Callable[[float], None] | None = None

        # Delegated components
        self.device_manager = AudioDeviceManager()
        self.processor = AudioProcessor()
        self.transcription_service = TranscriptionService(model_size="base")
        self.transcriber = AudioTranscriber(self.transcription_service)
        self.recorder: AudioRecorder | None = None

        # Audio format detection
        self._detected_format: str | None = None
        self._detected_sample_width: int | None = None
        self._initialize_audio_format()

    @property
    def state(self) -> RecordingState:
        """Get current recording state."""
        return self._state

    @property
    def is_recording(self) -> bool:
        """Check if currently recording."""
        return self._state == RecordingState.RECORDING

    @property
    def is_processing(self) -> bool:
        """Check if currently processing."""
        return self._state == RecordingState.PROCESSING

    @property
    def is_busy(self) -> bool:
        """Check if handler is busy."""
        return self._state in [RecordingState.RECORDING, RecordingState.PROCESSING]

    def subscribe_to_events(self, event_type: str, callback: Callable[[Event], None]) -> Callable[[], None]:
        """Subscribe to audio events via event bus."""
        return self._event_bus.subscribe(event_type, callback)

    def set_callbacks(
        self,
        state_callback: Callable[[RecordingState], None] | None = None,
        result_callback: Callable[[str], None] | None = None,
        error_callback: Callable[[Exception], None] | None = None,
        progress_callback: Callable[[float], None] | None = None,
    ) -> None:
        """Set legacy callbacks for recording state, results, and errors.

        DEPRECATED: Use event bus subscriptions instead.

        Migration path:
        - RECORDING_STARTED/STOPPED events replace state_callback
        - TRANSCRIPTION_COMPLETED event replaces result_callback
        - TRANSCRIPTION_ERROR event replaces error_callback
        - TRANSCRIPTION_PROGRESS event replaces progress_callback

        Callbacks will be removed in a future version when COMPONENTS_AVAILABLE
        becomes permanently true and all consumers migrate to event bus.

        Args:
            state_callback: Called when recording state changes (DEPRECATED)
            result_callback: Called when transcription completes with transcript text (DEPRECATED)
            error_callback: Called when an error occurs (DEPRECATED)
            progress_callback: Called with progress updates (0.0 to 1.0) (DEPRECATED)
        """
        logger.warning(
            "set_callbacks() is deprecated. Use event bus subscriptions instead. "
            "See AudioEvents.TRANSCRIPTION_* for replacement events."
        )
        self._state_callback = state_callback
        self._result_callback = result_callback
        self._error_callback = error_callback
        self._progress_callback = progress_callback

    def _initialize_audio_format(self) -> None:
        """Initialize audio format detection."""
        try:
            self._detected_format = get_best_format_for_device(app_config.audio_device, app_config.audio_format)
            self._detected_sample_width = self.device_manager.get_sample_width(self._detected_format)
            logger.info(
                f"Audio handler initialized: device={app_config.audio_device} "
                f"format={self._detected_format} "
                f"sample_width={self._detected_sample_width}bytes"
            )
        except Exception as e:
            logger.warning(f"Failed to detect audio format: {e}, using defaults")
            self._detected_format = app_config.audio_format
            self._detected_sample_width = 2

    def set_voice_visualizer(self, visualizer) -> None:
        """Connect voice visualizer for real-time feedback."""
        self._visualization_bridge.set_voice_visualizer(visualizer)

    def _get_sample_width(self, format_str: str) -> int:
        """Get sample width for audio format (backward compatibility)."""
        return self.device_manager.get_sample_width(format_str)

    def _set_state(self, state: RecordingState) -> None:
        """Set recording state and notify listeners."""
        self._state = state
        if self._state_callback:
            self._state_callback(state)
        if state == RecordingState.RECORDING:
            self._event_bus.emit_simple(AudioEvents.RECORDING_STARTED)
        elif state == RecordingState.IDLE:
            self._event_bus.emit_simple(AudioEvents.RECORDING_STOPPED)

    def _handle_error(self, error: Exception) -> None:
        """Handle errors and notify UI."""
        logger.error(f"Audio handler error: {error}")
        self._cleanup()
        self._set_state(RecordingState.ERROR)

        error_data = {
            "error": str(error),
            "type": error.__class__.__name__,
            "message": getattr(error, "message", str(error)),
            "device": getattr(error, "device", None),
            "details": getattr(error, "details", {}),
        }

        # Emit granular transcription error event (preferred)
        self._event_bus.emit_simple(AudioEvents.TRANSCRIPTION_ERROR, error_data)

        # Legacy error event for backward compatibility (DEPRECATED)
        self._event_bus.emit_simple(AudioEvents.ERROR, error_data)

        # Legacy callback for backward compatibility (DEPRECATED)
        if self._error_callback:
            self._error_callback(error)

    def _cleanup(self) -> None:
        """Clean up resources."""
        if self._temp_file and self._temp_file.exists():
            try:
                self._temp_file.unlink()
            except Exception as e:
                logger.warning(f"Failed to clean up temp file: {e}")
        self._temp_file = None

        if self.recorder:
            self.recorder.cleanup()
            self.recorder = None

    def start_recording(self, duration: int | None = None) -> None:
        """Start audio recording.

        Args:
            duration: Recording duration (ignored, records until stopped)

        Raises:
            AudioRecordingError: If recording cannot be started
        """
        if self.is_busy:
            raise AudioRecordingError("Already recording or processing")

        # No health check needed - direct service call

        try:
            # Create temp file
            temp_fd, temp_path = tempfile.mkstemp(suffix=".wav")
            self._temp_file = Path(temp_path)
            os.close(temp_fd)

            # Create recorder with config
            config = RecordingConfig(
                device_id=app_config.audio_device,
                sample_rate=app_config.audio_sample_rate,
                format=self._detected_format or app_config.audio_format,
                channels=app_config.audio_channels,
            )
            self.recorder = AudioRecorder(config)

            # Start recording in background thread
            self._recording_thread = threading.Thread(target=self._record_and_transcribe, daemon=True)
            self._set_state(RecordingState.RECORDING)
            self._start_time = time.time()
            self._recording_thread.start()

            logger.info("Started recording")

        except Exception as e:
            self._cleanup()
            raise AudioRecordingError(f"Failed to start recording: {e}") from e

    def stop_recording(self) -> None:
        """Stop current recording."""
        if not self.is_recording:
            return

        try:
            if self.recorder:
                self.recorder.stop_recording()
            logger.info("Recording stopped")
        except Exception as e:
            logger.error(f"Error stopping recording: {e}")
            self._handle_error(AudioRecordingError(f"Failed to stop: {e}"))

    def _record_and_transcribe(self) -> None:
        """Record audio and transcribe (runs in background thread)."""
        try:
            if not self.recorder or not self._temp_file:
                raise AudioRecordingError("Recording not initialized")

            # Start recording
            self.recorder.start_recording(self._temp_file)

            # Wait for completion
            (
                arecord_code,
                arecord_stderr,
                tee_stderr,
            ) = self.recorder.wait_for_completion()

            # Validate recording
            self.recorder.validate_recording()

            # Convert raw to WAV
            self.processor.convert_raw_to_wav(
                self._temp_file,
                self._temp_file,
                app_config.audio_sample_rate,
                app_config.audio_channels,
                self._detected_sample_width or 2,
            )

            # Validate WAV file
            self.processor.validate_wav_file(self._temp_file)

            # Start transcription
            self._set_state(RecordingState.PROCESSING)
            self._event_bus.emit_simple(AudioEvents.TRANSCRIPTION_STARTED, {})
            result = self.transcriber.transcribe(self._temp_file)

            # Clean up
            self._cleanup()
            self._set_state(RecordingState.IDLE)

            # Emit granular transcription event (preferred)
            self._event_bus.emit_simple(
                AudioEvents.TRANSCRIPTION_COMPLETED,
                {
                    "transcript": result.text,
                    "duration": time.time(),  # Timestamp for audit trail
                }
            )

            # Legacy event for backward compatibility (DEPRECATED)
            self._event_bus.emit_simple(AudioEvents.AMPLITUDE_UPDATED, {"transcript": result.text})

            # Legacy callback for backward compatibility (DEPRECATED)
            if self._result_callback:
                self._result_callback(result.text)

            logger.info(f"Transcription completed: {len(result.text)} chars")

        except Exception as e:
            self._handle_error(e)

    def get_available_devices(self) -> dict[str, str]:
        """Get list of available audio input devices."""
        return self.device_manager.get_available_devices()

    def test_recording(self, duration: int = 2) -> bool:
        """Test if recording works with current settings."""
        if self.is_busy:
            return False

        return self.device_manager.test_device(
            app_config.audio_device,
            self._detected_format or app_config.audio_format,
            app_config.audio_sample_rate,
            app_config.audio_channels,
            duration,
        )
