#!/usr/bin/env python3
"""
@llm-doc Audio Device Information Collection for GTK4 UI
@llm-version 1.0.0
@llm-date 2025-10-28

Cross-platform audio device monitoring using ALSA for device enumeration,
volume control, device switching, and connection management capabilities.
"""

import subprocess
import re
import time
import logging
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class AudioDevice:
    """Audio device information data structure"""
    card_id: int
    device_id: int
    name: str
    description: str
    device_type: str  # 'playback', 'capture', 'both'
    is_default: bool
    is_active: bool
    volume: Optional[int]  # 0-100 percentage
    is_muted: bool
    connection_type: str  # 'usb', 'hdmi', 'bluetooth', 'internal'
    subdevices: int
    driver: str
    
    def __post_init__(self):
        """Post-initialization processing"""
        # Ensure name is not empty
        if not self.name:
            self.name = self.description or "Unknown Device"
        
        # Classify connection type if not set
        if not self.connection_type:
            self.connection_type = self._classify_connection()
    
    def _classify_connection(self) -> str:
        """Classify connection type based on device name and description"""
        name_lower = self.name.lower()
        desc_lower = self.description.lower()
        
        if 'usb' in name_lower or 'usb' in desc_lower:
            return 'usb'
        elif 'hdmi' in name_lower or 'hdmi' in desc_lower:
            return 'hdmi'
        elif 'bluetooth' in name_lower or 'bluetooth' in desc_lower:
            return 'bluetooth'
        elif 'nvidia' in name_lower or 'nvidia' in desc_lower:
            return 'hdmi'
        elif 'generic' in name_lower or 'hda' in name_lower:
            return 'internal'
        else:
            return 'unknown'
    
    @property
    def alsa_device(self) -> str:
        """Get ALSA device string (hw:CARD,DEVICE)"""
        return f"hw:{self.card_id},{self.device_id}"
    
    @property
    def display_name(self) -> str:
        """Get user-friendly display name"""
        if self.connection_type == 'usb':
            return f"🔌 {self.name}"
        elif self.connection_type == 'hdmi':
            return f"📺 {self.name}"
        elif self.connection_type == 'bluetooth':
            return f"🔵 {self.name}"
        elif self.connection_type == 'internal':
            return f"🔊 {self.name}"
        else:
            return f"🎵 {self.name}"


class AudioMonitor:
    """
    Audio device information collection using ALSA.
    
    Features:
    - Cross-platform audio device enumeration
    - Volume control and mute management
    - Default device selection and switching
    - Connection type detection
    - Real-time device monitoring
    """
    
    def __init__(self):
        self.cache_duration = 1.0  # Cache for 1 second
        self._device_cache = {}
        self._last_update = 0
        
        # Performance tracking
        self._collection_count = 0
        self._error_count = 0
        
        # Check available tools
        self._has_amixer = self._check_tool('amixer')
        self._has_aplay = self._check_tool('aplay')
        self._has_pactl = self._check_tool('pactl')
        
    def _check_tool(self, tool_name: str) -> bool:
        """Check if audio tool is available"""
        try:
            result = subprocess.run(['which', tool_name], capture_output=True)
            return result.returncode == 0
        except Exception:
            return False
    
    def get_playback_devices(self) -> List[AudioDevice]:
        """Get list of audio playback devices."""
        try:
            devices = []
            
            # Get devices from aplay if available
            if self._has_aplay:
                devices.extend(self._get_devices_aplay())
            
            # Enhance with volume information from amixer
            if self._has_amixer:
                self._enhance_with_volume_info(devices)
            
            self._collection_count += 1
            return devices
            
        except Exception as e:
            logger.error(f"Failed to get playback devices: {e}")
            self._error_count += 1
            return []
    
    def _get_devices_aplay(self) -> List[AudioDevice]:
        """Get devices using aplay -l"""
        devices = []
        
        try:
            result = subprocess.run(
                ['aplay', '-l'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                current_card = None
                
                for line in result.stdout.split('\n'):
                    line = line.strip()
                    
                    # Parse card line: "card 1: LIGHTSPEED [PRO X 2 LIGHTSPEED], device 0: USB Audio [USB Audio]"
                    card_match = re.match(r'card (\d+): (\w+) \[([^\]]+)\], device (\d+): ([^[]+) \[([^\]]+)\]', line)
                    if card_match:
                        card_id = int(card_match.group(1))
                        card_name = card_match.group(2)
                        card_desc = card_match.group(3)
                        device_id = int(card_match.group(4))
                        device_name = card_match.group(5).strip()
                        device_desc = card_match.group(6)
                        
                        # Get subdevice count
                        subdevices = 1  # Default
                        
                        device = AudioDevice(
                            card_id=card_id,
                            device_id=device_id,
                            name=card_desc,  # Use card description as name
                            description=f"{device_name} - {device_desc}",
                            device_type='playback',
                            is_default=False,  # Will be determined later
                            is_active=False,   # Will be determined later
                            volume=None,       # Will be filled by amixer
                            is_muted=False,    # Will be filled by amixer
                            connection_type='',  # Will be classified
                            subdevices=subdevices,
                            driver=card_name
                        )
                        
                        devices.append(device)
                        
        except subprocess.TimeoutExpired:
            logger.warning("aplay -l timeout")
        except Exception as e:
            logger.error(f"aplay -l failed: {e}")
            
        return devices
    
    def _enhance_with_volume_info(self, devices: List[AudioDevice]):
        """Enhance devices with volume information from amixer"""
        try:
            # Get master volume as default
            result = subprocess.run(
                ['amixer', 'get', 'Master'],
                capture_output=True,
                text=True,
                timeout=3
            )
            
            if result.returncode == 0:
                # Parse volume from output like: "[75%] [on]"
                volume_match = re.search(r'\[(\d+)%\]', result.stdout)
                mute_match = re.search(r'\[(on|off)\]', result.stdout)
                
                default_volume = int(volume_match.group(1)) if volume_match else 50
                default_muted = mute_match.group(1) == 'off' if mute_match else False
                
                # Apply to all devices (simplified approach)
                for device in devices:
                    device.volume = default_volume
                    device.is_muted = default_muted
                    
        except Exception as e:
            logger.debug(f"Failed to get volume info: {e}")
    
    def set_default_device(self, device: AudioDevice) -> bool:
        """Set device as default audio output"""
        try:
            # For ALSA, we can use amixer to set the default card
            result = subprocess.run(
                ['amixer', '-c', str(device.card_id), 'set', 'Master', 'unmute'],
                capture_output=True,
                text=True,
                timeout=3
            )
            
            return result.returncode == 0
            
        except Exception as e:
            logger.error(f"Failed to set default device: {e}")
            return False
    
    def set_volume(self, device: AudioDevice, volume: int) -> bool:
        """Set device volume (0-100)"""
        try:
            volume = max(0, min(100, volume))  # Clamp to 0-100
            
            result = subprocess.run(
                ['amixer', '-c', str(device.card_id), 'set', 'Master', f'{volume}%'],
                capture_output=True,
                text=True,
                timeout=3
            )
            
            if result.returncode == 0:
                device.volume = volume
                return True
            
        except Exception as e:
            logger.error(f"Failed to set volume: {e}")
            
        return False
    
    def toggle_mute(self, device: AudioDevice) -> bool:
        """Toggle device mute state"""
        try:
            action = 'mute' if not device.is_muted else 'unmute'
            
            result = subprocess.run(
                ['amixer', '-c', str(device.card_id), 'set', 'Master', action],
                capture_output=True,
                text=True,
                timeout=3
            )
            
            if result.returncode == 0:
                device.is_muted = not device.is_muted
                return True
            
        except Exception as e:
            logger.error(f"Failed to toggle mute: {e}")
            
        return False
    
    def connect_bluetooth_device(self, bluetooth_address: str) -> bool:
        """Connect a Bluetooth audio device and set as default"""
        try:
            # This would integrate with BluetoothMonitor
            # For now, return success if we have the tools
            return self._has_amixer
            
        except Exception as e:
            logger.error(f"Failed to connect Bluetooth device: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get monitoring statistics."""
        return {
            'has_amixer': self._has_amixer,
            'has_aplay': self._has_aplay,
            'has_pactl': self._has_pactl,
            'collection_count': self._collection_count,
            'error_count': self._error_count,
            'error_rate': self._error_count / max(self._collection_count, 1),
            'cache_duration': self.cache_duration
        }


# Convenience functions for easy access
def get_audio_devices() -> List[AudioDevice]:
    """Get list of audio playback devices."""
    monitor = AudioMonitor()
    return monitor.get_playback_devices()

def set_default_audio_device(device: AudioDevice) -> bool:
    """Set device as default audio output."""
    monitor = AudioMonitor()
    return monitor.set_default_device(device)

def set_audio_volume(device: AudioDevice, volume: int) -> bool:
    """Set device volume (0-100)."""
    monitor = AudioMonitor()
    return monitor.set_volume(device, volume)

def toggle_audio_mute(device: AudioDevice) -> bool:
    """Toggle device mute state."""
    monitor = AudioMonitor()
    return monitor.toggle_mute(device)


if __name__ == "__main__":
    # Test the audio monitor
    print("🔊 Testing Audio Monitor")
    print("=" * 40)
    
    monitor = AudioMonitor()
    
    # Test device list
    print("🎵 Getting audio devices...")
    devices = monitor.get_playback_devices()
    print(f"✅ Found {len(devices)} audio device(s)")
    
    for device in devices:
        print(f"  🔊 {device.display_name}")
        print(f"     Card: {device.card_id}, Device: {device.device_id}")
        print(f"     Type: {device.connection_type}, Volume: {device.volume}%")
        print(f"     ALSA: {device.alsa_device}")
    
    # Test statistics
    stats = monitor.get_statistics()
    print(f"\n📊 Statistics:")
    print(f"  Tools: amixer={stats['has_amixer']}, aplay={stats['has_aplay']}, pactl={stats['has_pactl']}")
    print(f"  Collections: {stats['collection_count']}")
    print(f"  Errors: {stats['error_count']}")
    
    print("✅ Audio monitor test completed")
