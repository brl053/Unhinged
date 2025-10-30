"""
Audio devices hook - React hook-like functionality for managing audio devices.

Provides a clean interface for audio device management that can be used
across different views and components.
"""

import subprocess
import time
from dataclasses import dataclass
from typing import List, Optional, Callable
from pathlib import Path

from ..models.audio_types import AudioDevice, AudioDeviceState, AudioDeviceType

@dataclass
class AudioDevicesHook:
    """Hook return type for audio device management (like React hook return)."""
    state: AudioDeviceState
    refresh: Callable[[], None]
    set_default: Callable[[AudioDevice], bool]
    get_current_default: Callable[[], Optional[AudioDevice]]
    is_device_active: Callable[[AudioDevice], bool]

class AudioDeviceManager:
    """Internal manager for audio device operations."""
    
    def __init__(self):
        self._cache_duration = 2.0  # Cache for 2 seconds
        self._last_update = 0
        self._cached_state: Optional[AudioDeviceState] = None
    
    def get_input_devices(self) -> List[AudioDevice]:
        """Get list of audio input devices using arecord."""
        devices = []
        
        try:
            # Use arecord -l to list input devices
            result = subprocess.run(
                ['arecord', '-l'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                import re
                
                for line in result.stdout.split('\n'):
                    line = line.strip()
                    
                    # Parse card line: "card 1: LIGHTSPEED [PRO X 2 LIGHTSPEED], device 0: USB Audio [USB Audio]"
                    card_match = re.match(
                        r'card (\d+): (\w+) \[([^\]]+)\], device (\d+): ([^[]+) \[([^\]]+)\]', 
                        line
                    )
                    
                    if card_match:
                        card_id = int(card_match.group(1))
                        card_name = card_match.group(2)
                        card_desc = card_match.group(3)
                        device_id = int(card_match.group(4))
                        device_name = card_match.group(5).strip()
                        device_desc = card_match.group(6)
                        
                        # Determine device type and icon
                        device_type = AudioDeviceType.UNKNOWN
                        icon = "audio-input-microphone-symbolic"
                        
                        if "camera" in card_desc.lower() or "webcam" in card_desc.lower():
                            device_type = AudioDeviceType.CAMERA
                            icon = "camera-web-symbolic"
                        elif "headset" in card_desc.lower() or "lightspeed" in card_desc.lower():
                            device_type = AudioDeviceType.HEADSET
                            icon = "audio-headphones-symbolic"
                        else:
                            device_type = AudioDeviceType.MICROPHONE
                            icon = "audio-input-microphone-symbolic"
                        
                        device = AudioDevice(
                            name=card_desc,
                            description=f"Card {card_id}, Device {device_id} - {device_desc}",
                            card_id=card_id,
                            device_id=device_id,
                            alsa_device=f"hw:{card_id},{device_id}",
                            icon=icon,
                            device_type=device_type
                        )
                        
                        devices.append(device)
                        
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            # Return empty list on any error
            pass
        
        return devices
    
    def get_current_default_device(self) -> Optional[AudioDevice]:
        """Get the current default input device from the system."""
        try:
            # Try to get default source from wpctl (PipeWire)
            result = subprocess.run(
                ['wpctl', 'status'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                # Parse wpctl output to find default source
                lines = result.stdout.split('\n')
                in_sources_section = False
                
                for line in lines:
                    if 'Sources:' in line:
                        in_sources_section = True
                        continue
                    elif in_sources_section and ('├─' in line or '└─' in line):
                        # Check if this line has an asterisk (default device)
                        if '*' in line:
                            import re
                            match = re.search(r'(\d+)\.\s+([^[]+)', line)
                            if match:
                                device_id = match.group(1).strip()
                                device_name = match.group(2).strip()
                                
                                # Create a minimal AudioDevice for the current default
                                return AudioDevice(
                                    name=device_name,
                                    description=f"PipeWire Source {device_id}",
                                    card_id=0,  # Unknown
                                    device_id=int(device_id),
                                    alsa_device=f"pipewire:{device_id}",
                                    icon="audio-input-microphone-symbolic",
                                    device_type=AudioDeviceType.MICROPHONE,
                                    is_default=True,
                                    is_active=True
                                )
                    elif in_sources_section and ('Sinks:' in line or line.strip() == ''):
                        # End of sources section
                        break
                        
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            pass
        
        # Fallback: try to get from ALSA default device
        try:
            asoundrc_path = Path.home() / ".asoundrc"
            if asoundrc_path.exists():
                with open(asoundrc_path, 'r') as f:
                    content = f.read()
                    import re
                    match = re.search(r'hw:(\d+),(\d+)', content)
                    if match:
                        card_id = int(match.group(1))
                        device_id = int(match.group(2))
                        
                        return AudioDevice(
                            name="ALSA Default Device",
                            description=f"ALSA hw:{card_id},{device_id}",
                            card_id=card_id,
                            device_id=device_id,
                            alsa_device=f"hw:{card_id},{device_id}",
                            icon="audio-input-microphone-symbolic",
                            device_type=AudioDeviceType.MICROPHONE,
                            is_default=True,
                            is_active=True
                        )
        except Exception:
            pass
        
        return None
    
    def set_default_device(self, device: AudioDevice) -> bool:
        """Set the selected device as the default input device."""
        try:
            # Create ALSA configuration for default input device
            asoundrc_content = f"""# ALSA configuration - Default input device set by Unhinged
# Device: {device.name} ({device.alsa_device})

pcm.!default {{
    type plug
    slave {{
        pcm "hw:{device.card_id},{device.device_id}"
    }}
}}

ctl.!default {{
    type hw
    card {device.card_id}
}}
"""
            
            # Write to ~/.asoundrc
            asoundrc_path = Path.home() / ".asoundrc"
            with open(asoundrc_path, 'w') as f:
                f.write(asoundrc_content)
            
            return True
            
        except Exception:
            return False
    
    def get_state(self, force_refresh: bool = False) -> AudioDeviceState:
        """Get current audio device state with caching."""
        current_time = time.time()
        
        if (not force_refresh and 
            self._cached_state and 
            current_time - self._last_update < self._cache_duration):
            return self._cached_state
        
        # Refresh state
        devices = self.get_input_devices()
        current_device = self.get_current_default_device()
        
        # Mark devices as default/active based on current device
        for device in devices:
            if current_device:
                device.is_default = self._is_same_device(device, current_device)
                device.is_active = device.is_default
        
        self._cached_state = AudioDeviceState(
            devices=devices,
            current_device=current_device,
            is_loading=False,
            error=None,
            last_updated=current_time
        )
        
        self._last_update = current_time
        return self._cached_state
    
    def _is_same_device(self, device1: AudioDevice, device2: AudioDevice) -> bool:
        """Check if two devices are the same."""
        # Match by name (for PipeWire devices)
        if device1.name in device2.name or device2.name in device1.name:
            return True
        
        # Match by card/device ID (for ALSA devices)
        if (device1.card_id == device2.card_id and 
            device1.device_id == device2.device_id):
            return True
        
        return False

# Global manager instance
_audio_manager = AudioDeviceManager()

def use_audio_devices() -> AudioDevicesHook:
    """
    Hook for managing audio devices (React hook-like).
    
    Returns:
        AudioDevicesHook with current state and action functions
    """
    
    def refresh():
        """Refresh the audio devices list."""
        _audio_manager.get_state(force_refresh=True)
    
    def set_default(device: AudioDevice) -> bool:
        """Set the selected device as default."""
        success = _audio_manager.set_default_device(device)
        if success:
            # Refresh state after setting default
            refresh()
        return success
    
    def get_current_default() -> Optional[AudioDevice]:
        """Get the current default device."""
        return _audio_manager.get_current_default_device()
    
    def is_device_active(device: AudioDevice) -> bool:
        """Check if a device is currently active."""
        current = get_current_default()
        if not current:
            return False
        return _audio_manager._is_same_device(device, current)
    
    return AudioDevicesHook(
        state=_audio_manager.get_state(),
        refresh=refresh,
        set_default=set_default,
        get_current_default=get_current_default,
        is_device_active=is_device_active
    )
