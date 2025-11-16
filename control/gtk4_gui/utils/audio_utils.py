"""
Audio processing utilities for Unhinged.

Provides shared audio processing functions including RMS amplitude calculation,
audio device enumeration, and audio format handling.

Eliminates duplicate audio processing code across handlers and monitors.

## Format Detection Architecture

All audio format negotiation logic is isolated in this module for clean refactoring:

- `detect_supported_formats(device_id)` - Probe device for supported formats
- `get_best_format_for_device(device_id, preferred)` - Select best format
- `clear_format_cache()` - Clear cached results

**Contract**: These functions can be replaced wholesale when moving to new audio
backends (e.g., /dev/fb0 graphics, different audio server, etc.) without
affecting the rest of the application.

**Cache**: Global module-level `_FORMAT_CACHE` dictionary. Single-process only.
"""

import logging
import math
import struct
import subprocess
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Global cache for format detection results
# Maps device_id -> list of supported formats
_FORMAT_CACHE: dict[str, list[str]] = {}


@dataclass
class AudioDevice:
    """Represents an audio device."""

    device_id: str
    name: str
    device_type: str  # 'playback' or 'capture'
    card_number: int
    device_number: int


def calculate_rms_amplitude(audio_data: bytes) -> float:
    """
    Calculate RMS (Root Mean Square) amplitude from raw 16-bit audio data.

    Shared implementation used by both audio_handler and audio_monitor.
    Converts raw audio samples to normalized amplitude (0.0 to 1.0).

    Args:
        audio_data: Raw audio bytes in 16-bit signed little-endian format

    Returns:
        Normalized amplitude value (0.0 to 1.0)
    """
    try:
        if not audio_data or len(audio_data) < 2:
            return 0.0

        # Unpack 16-bit signed little-endian samples
        samples = struct.unpack(f"<{len(audio_data) // 2}h", audio_data)

        if not samples:
            return 0.0

        # Calculate RMS (Root Mean Square) amplitude
        rms = math.sqrt(sum(sample * sample for sample in samples) / len(samples))

        # Normalize to 0.0-1.0 range (max value for 16-bit signed is 32767)
        normalized_amplitude = min(1.0, rms / 32767.0)

        return normalized_amplitude

    except Exception as e:
        logger.warning(f"Error calculating amplitude: {e}")
        return 0.0


def parse_audio_device_line(line: str, device_type: str) -> AudioDevice | None:
    """
    Parse a single device line from arecord/aplay output.

    Args:
        line: Single line from arecord -l or aplay -l output
        device_type: 'playback' or 'capture'

    Returns:
        AudioDevice object or None if parsing fails
    """
    try:
        # Format: "card 0: PCH [HDA Intel PCH], device 0: ALC892 Analog [ALC892 Analog]"
        if not line.strip() or not line.startswith("card"):
            return None

        # Extract card number
        card_part = line.split(":")[0].strip()
        card_number = int(card_part.split()[-1])

        # Extract device number
        device_part = line.split("device")[1].split(":")[0].strip()
        device_number = int(device_part)

        # Extract device name (between brackets)
        name_start = line.rfind("[")
        name_end = line.rfind("]")
        device_name = line[name_start + 1 : name_end] if name_start != -1 and name_end != -1 else "Unknown"

        device_id = f"hw:{card_number},{device_number}"

        return AudioDevice(
            device_id=device_id,
            name=device_name,
            device_type=device_type,
            card_number=card_number,
            device_number=device_number,
        )

    except Exception as e:
        logger.debug(f"Error parsing audio device line: {e}")
        return None


def get_playback_devices() -> list[AudioDevice]:
    """
    Get list of audio playback devices using aplay.

    Returns:
        List of AudioDevice objects for playback devices
    """
    devices = []
    try:
        result = subprocess.run(["aplay", "-l"], capture_output=True, text=True, timeout=5)

        if result.returncode == 0:
            for line in result.stdout.split("\n"):
                device = parse_audio_device_line(line, "playback")
                if device:
                    devices.append(device)
        else:
            logger.warning(f"aplay -l failed: {result.stderr}")

    except subprocess.TimeoutExpired:
        logger.warning("aplay -l command timed out")
    except FileNotFoundError:
        logger.warning("aplay command not found")
    except Exception as e:
        logger.warning(f"Error getting playback devices: {e}")

    return devices


def get_capture_devices() -> list[AudioDevice]:
    """
    Get list of audio capture devices using arecord.

    Returns:
        List of AudioDevice objects for capture devices
    """
    devices = []
    try:
        result = subprocess.run(["arecord", "-l"], capture_output=True, text=True, timeout=5)

        if result.returncode == 0:
            for line in result.stdout.split("\n"):
                device = parse_audio_device_line(line, "capture")
                if device:
                    devices.append(device)
        else:
            logger.warning(f"arecord -l failed: {result.stderr}")

    except subprocess.TimeoutExpired:
        logger.warning("arecord -l command timed out")
    except FileNotFoundError:
        logger.warning("arecord command not found")
    except Exception as e:
        logger.warning(f"Error getting capture devices: {e}")

    return devices


def get_audio_devices(device_type: str = "capture") -> list[AudioDevice]:
    """
    Get audio devices of specified type.

    Args:
        device_type: 'capture' or 'playback'

    Returns:
        List of AudioDevice objects
    """
    if device_type == "capture":
        return get_capture_devices()
    elif device_type == "playback":
        return get_playback_devices()
    else:
        logger.warning(f"Unknown device type: {device_type}")
        return []


def detect_supported_formats(device_id: str, use_cache: bool = True) -> list[str]:
    """
    Detect supported audio formats for a device.

    Results are cached per device to avoid repeated subprocess calls.

    Args:
        device_id: ALSA device identifier (e.g., 'hw:4,0', 'default', 'pipewire')
        use_cache: If True, return cached results if available (default: True)

    Returns:
        List of supported format strings (e.g., ['S16_LE', 'S24_3LE'])
    """
    # Return cached result if available
    if use_cache and device_id in _FORMAT_CACHE:
        cached_formats = _FORMAT_CACHE[device_id]
        logger.info(f"Audio format detection: device={device_id} cache_hit=true formats={cached_formats}")
        return cached_formats

    # Common formats to test, in order of preference
    formats_to_test = ["S16_LE", "S24_3LE", "S32_LE", "U8", "S8"]
    supported_formats = []

    for fmt in formats_to_test:
        try:
            # Try to record 1 second of audio with this format
            # Use integer duration only (arecord doesn't support fractional seconds)
            result = subprocess.run(
                [
                    "arecord",
                    "-D",
                    device_id,
                    "-f",
                    fmt,
                    "-r",
                    "16000",
                    "-c",
                    "1",
                    "-t",
                    "raw",
                    "-d",
                    "1",  # 1 second test
                    "/dev/null",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )

            stderr_str = result.stderr.lower()

            # Check if format is NOT supported
            if "sample format non available" in stderr_str:
                logger.debug(f"Device {device_id} does NOT support format: {fmt}")
                continue

            # Format is supported if we got here (exit code might be non-zero due to signal)
            supported_formats.append(fmt)
            logger.debug(f"Device {device_id} supports format: {fmt}")

        except subprocess.TimeoutExpired:
            # Timeout might mean the format is supported but recording is slow
            logger.debug(f"Format {fmt} test timed out (assuming supported)")
            supported_formats.append(fmt)
        except Exception as e:
            logger.debug(f"Error testing format {fmt} on device {device_id}: {e}")

    # If no formats detected, return defaults
    if not supported_formats:
        logger.warning(f"Could not detect formats for device {device_id}, using defaults")
        supported_formats = ["S16_LE", "S24_3LE"]

    # Cache the result
    _FORMAT_CACHE[device_id] = supported_formats
    logger.info(f"Audio format detection: device={device_id} cache_hit=false formats={supported_formats}")

    return supported_formats


def get_best_format_for_device(device_id: str, preferred_format: str = "S16_LE") -> str:
    """
    Get the best supported format for a device.

    Args:
        device_id: ALSA device identifier
        preferred_format: Preferred format if supported

    Returns:
        Best supported format string
    """
    supported = detect_supported_formats(device_id)

    # Return preferred format if supported
    if preferred_format in supported:
        return preferred_format

    # Otherwise return first supported format
    if supported:
        return supported[0]

    # Fallback
    return "S16_LE"


def clear_format_cache(device_id: str | None = None) -> None:
    """
    Clear cached format detection results.

    Args:
        device_id: If provided, clear only this device's cache. Otherwise clear all.
    """
    global _FORMAT_CACHE
    if device_id:
        if device_id in _FORMAT_CACHE:
            del _FORMAT_CACHE[device_id]
            logger.debug(f"Cleared format cache for device {device_id}")
    else:
        _FORMAT_CACHE.clear()
        logger.debug("Cleared all format cache entries")
