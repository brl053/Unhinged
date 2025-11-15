"""
Audio recording lifecycle management.

Handles subprocess orchestration, state machine, and event emission.
Decomposes the 152-line _record_audio_continuous into manageable pieces.
"""

import logging
import os
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))

from audio_types import RecordingConfig

logger = logging.getLogger(__name__)


class AudioRecorder:
    """Manages audio recording lifecycle and subprocess orchestration."""

    SIGNAL_MESSAGES = ["Aborted by signal", "Interrupted by signal", "Terminated"]

    def __init__(self, config: RecordingConfig):
        """Initialize recorder with configuration.

        Args:
            config: RecordingConfig with device, format, sample rate, channels
        """
        self.config = config
        self.arecord_process = None
        self.recording_process = None
        self.temp_pipe = None
        self.temp_file = None

    def _create_named_pipe(self) -> Path:
        """Create named pipe for amplitude extraction.

        Returns:
            Path to created pipe

        Raises:
            OSError: If pipe creation fails
        """
        pipe_dir = Path(tempfile.gettempdir())
        pipe_path = pipe_dir / f"audio_pipe_{os.getpid()}_{int(time.time() * 1000)}"

        try:
            os.mkfifo(str(pipe_path))
            logger.debug(f"Created named pipe: {pipe_path}")
        except FileExistsError:
            pipe_path.unlink()
            os.mkfifo(str(pipe_path))

        return pipe_path

    def _start_arecord_process(self) -> subprocess.Popen:
        """Start arecord subprocess.

        Returns:
            Popen object for arecord process
        """
        cmd = [
            'arecord',
            '-D', self.config.device_id,
            '-f', self.config.format,
            '-r', str(self.config.sample_rate),
            '-c', str(self.config.channels),
            '-t', 'raw',
            '-'
        ]

        return subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

    def _start_tee_process(self, arecord_stdout, output_file: Path) -> subprocess.Popen:
        """Start tee subprocess to split audio stream.

        Args:
            arecord_stdout: stdout from arecord process
            output_file: Path to write audio data

        Returns:
            Popen object for tee process
        """
        cmd = ['tee', str(self.temp_pipe)]

        return subprocess.Popen(
            cmd,
            stdin=arecord_stdout,
            stdout=open(str(output_file), 'wb'),
            stderr=subprocess.PIPE
        )

    def _is_signal_exit(self, stderr: bytes) -> bool:
        """Check if process exited due to signal (normal) vs error.

        Args:
            stderr: stderr output from process

        Returns:
            True if exit was due to signal
        """
        if not stderr:
            return False

        stderr_str = stderr.decode('utf-8', errors='replace').strip()
        return any(msg in stderr_str for msg in self.SIGNAL_MESSAGES)

    def start_recording(self, output_file: Path, amplitude_callback=None) -> None:
        """Start recording to file with amplitude extraction.

        Args:
            output_file: Path to write raw audio
            amplitude_callback: Optional callback for amplitude updates

        Raises:
            OSError: If recording setup fails
        """
        self.temp_file = output_file
        self.temp_pipe = self._create_named_pipe()

        try:
            self.arecord_process = self._start_arecord_process()
            self.recording_process = self._start_tee_process(
                self.arecord_process.stdout,
                output_file
            )
            self.arecord_process.stdout.close()

            logger.info("Recording started")

        except Exception:
            self.cleanup()
            raise

    def stop_recording(self) -> None:
        """Stop recording gracefully."""
        if not self.arecord_process or self.arecord_process.poll() is not None:
            return

        try:
            self.arecord_process.send_signal(signal.SIGTERM)
            self.arecord_process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            logger.warning("Graceful stop timed out, force terminating")
            self.arecord_process.terminate()
            self.arecord_process.wait(timeout=2)

    def wait_for_completion(self) -> tuple[int, bytes, bytes]:
        """Wait for recording processes to complete.

        Returns:
            Tuple of (arecord_returncode, arecord_stderr, tee_stderr)
        """
        tee_stdout, tee_stderr = self.recording_process.communicate()
        arecord_stdout, arecord_stderr = self.arecord_process.communicate()

        return (self.arecord_process.returncode, arecord_stderr, tee_stderr)

    def validate_recording(self, min_size: int = 4) -> bool:
        """Validate recorded file.

        Args:
            min_size: Minimum file size in bytes

        Returns:
            True if valid

        Raises:
            OSError: If validation fails
        """
        if not self.temp_file or not self.temp_file.exists():
            raise OSError("Recording file not created")

        file_size = self.temp_file.stat().st_size
        if file_size <= min_size:
            raise OSError(f"Recording too small: {file_size} bytes")

        return True

    def cleanup(self) -> None:
        """Clean up resources."""
        if self.temp_pipe and self.temp_pipe.exists():
            try:
                self.temp_pipe.unlink()
                logger.debug(f"Cleaned up pipe: {self.temp_pipe}")
            except Exception as e:
                logger.warning(f"Failed to clean up pipe: {e}")

