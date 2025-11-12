"""
Audio processing utilities for Unhinged.

Provides shared audio processing functions including RMS amplitude calculation,
audio device enumeration, and audio format handling.

Eliminates duplicate audio processing code across handlers and monitors.
"""

import struct
import math
import subprocess
import logging
from typing import Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


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
        samples = struct.unpack(f'<{len(audio_data)//2}h', audio_data)
        
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


def parse_audio_device_line(line: str, device_type: str) -> Optional[AudioDevice]:
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
        if not line.strip() or not line.startswith('card'):
            return None
        
        # Extract card number
        card_part = line.split(':')[0].strip()
        card_number = int(card_part.split()[-1])
        
        # Extract device number
        device_part = line.split('device')[1].split(':')[0].strip()
        device_number = int(device_part)
        
        # Extract device name (between brackets)
        name_start = line.rfind('[')
        name_end = line.rfind(']')
        if name_start != -1 and name_end != -1:
            device_name = line[name_start + 1:name_end]
        else:
            device_name = "Unknown"
        
        device_id = f"hw:{card_number},{device_number}"
        
        return AudioDevice(
            device_id=device_id,
            name=device_name,
            device_type=device_type,
            card_number=card_number,
            device_number=device_number
        )
        
    except Exception as e:
        logger.debug(f"Error parsing audio device line: {e}")
        return None


def get_playback_devices() -> List[AudioDevice]:
    """
    Get list of audio playback devices using aplay.
    
    Returns:
        List of AudioDevice objects for playback devices
    """
    devices = []
    try:
        result = subprocess.run(
            ['aplay', '-l'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                device = parse_audio_device_line(line, 'playback')
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


def get_capture_devices() -> List[AudioDevice]:
    """
    Get list of audio capture devices using arecord.
    
    Returns:
        List of AudioDevice objects for capture devices
    """
    devices = []
    try:
        result = subprocess.run(
            ['arecord', '-l'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                device = parse_audio_device_line(line, 'capture')
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


def get_audio_devices(device_type: str = 'capture') -> List[AudioDevice]:
    """
    Get audio devices of specified type.
    
    Args:
        device_type: 'capture' or 'playback'
        
    Returns:
        List of AudioDevice objects
    """
    if device_type == 'capture':
        return get_capture_devices()
    elif device_type == 'playback':
        return get_playback_devices()
    else:
        logger.warning(f"Unknown device type: {device_type}")
        return []

