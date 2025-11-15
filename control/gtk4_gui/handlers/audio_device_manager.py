"""
Audio device management for recording.

Handles device enumeration, format detection, and device validation.
Decoupled from AudioHandler to enable independent testing and reuse.
"""

import logging
import re
import subprocess
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)


class AudioDeviceManager:
    """Manages audio device detection and configuration."""

    def __init__(self):
        """Initialize device manager."""
        # Format to sample width mapping
        self.format_sample_width = {
            'U8': 1, 'S8': 1,
            'S16_LE': 2, 'S16_BE': 2, 'U16_LE': 2, 'U16_BE': 2,
            'S24_LE': 3, 'S24_BE': 3, 'S24_3LE': 3, 'S24_3BE': 3,
            'S32_LE': 4, 'S32_BE': 4, 'U32_LE': 4, 'U32_BE': 4,
        }

    def _parse_device_line(self, line: str) -> tuple[str, str] | None:
        """Parse arecord device line. Returns (device_id, display_name) or None."""
        match = re.match(
            r'card (\d+): (.+?) \[(.+?)\], device (\d+): (.+?) \[(.+?)\]',
            line
        )
        if not match:
            return None

        card_num, card_name, _, device_num, device_name, _ = match.groups()
        device_id = f"hw:{card_num},{device_num}"
        display_name = f"{card_name} - {device_name}"
        return (device_id, display_name)

    def _add_parsed_devices(self, devices: dict, output: str) -> None:
        """Parse arecord output and add devices to dict."""
        for line in output.split('\n'):
            parsed = self._parse_device_line(line)
            if parsed:
                device_id, display_name = parsed
                devices[display_name] = device_id

    def get_available_devices(self) -> dict[str, str]:
        """Get list of available audio input devices.

        Returns:
            Dictionary mapping device names to device identifiers
        """
        devices = {}

        try:
            result = subprocess.run(
                ['arecord', '-l'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                self._add_parsed_devices(devices, result.stdout)

            # Add default devices
            devices["Default (PipeWire)"] = "pipewire"
            devices["Default (ALSA)"] = "default"

        except Exception as e:
            logger.warning(f"Failed to enumerate audio devices: {e}")
            devices = {
                "Default (PipeWire)": "pipewire",
                "Default (ALSA)": "default"
            }

        return devices

    def get_sample_width(self, format_str: str) -> int:
        """Get sample width in bytes for audio format.

        Args:
            format_str: Audio format string (e.g., 'S16_LE', 'S24_3LE')

        Returns:
            Sample width in bytes
        """
        return self.format_sample_width.get(format_str, 2)

    def test_device(
        self,
        device_id: str,
        format_str: str,
        sample_rate: int,
        channels: int,
        duration: int = 2
    ) -> bool:
        """Test if device works with given configuration.

        Args:
            device_id: ALSA device identifier
            format_str: Audio format (e.g., 'S16_LE')
            sample_rate: Sample rate in Hz
            channels: Number of channels
            duration: Test duration in seconds

        Returns:
            True if test recording succeeds
        """
        try:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                test_file = Path(f.name)

            cmd = [
                'arecord',
                '-D', device_id,
                '-f', format_str,
                '-r', str(sample_rate),
                '-c', str(channels),
                '-t', 'wav',
                '-d', str(duration),
                str(test_file)
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=duration + 5
            )

            success = (
                result.returncode == 0 and
                test_file.exists() and
                test_file.stat().st_size > 44
            )

            if test_file.exists():
                test_file.unlink()

            return success

        except Exception as e:
            logger.warning(f"Device test failed: {e}")
            return False

