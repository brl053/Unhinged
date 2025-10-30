"""
Audio-related type definitions.

Dataclasses that represent audio devices, recording states, and audio system information.
Similar to TypeScript interfaces in React applications.
"""

from dataclasses import dataclass
from enum import Enum


class AudioDeviceType(Enum):
    """Audio device types."""
    MICROPHONE = "microphone"
    CAMERA = "camera"
    HEADSET = "headset"
    SPEAKER = "speaker"
    UNKNOWN = "unknown"

    def title(self):
        """Return title-cased version of the enum value for UI display"""
        return self.value.title()

class VoiceRecordingStatus(Enum):
    """Voice recording status states."""
    IDLE = "idle"
    RECORDING = "recording"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"

@dataclass
class AudioDevice:
    """Represents an audio input/output device."""
    name: str
    description: str
    card_id: int
    device_id: int
    alsa_device: str
    icon: str
    device_type: AudioDeviceType = AudioDeviceType.UNKNOWN
    connection_type: str = "unknown"  # "usb", "hdmi", "bluetooth", "internal", "unknown"
    driver: str = "ALSA"  # Audio driver name
    subdevices: int = 1  # Number of subdevices available on this audio device
    is_default: bool = False
    is_active: bool = False
    volume: float | None = None
    is_muted: bool = False

    @property
    def display_name(self) -> str:
        """Get display-friendly device name."""
        return self.name

    @property
    def full_description(self) -> str:
        """Get full device description with status."""
        status_parts = []
        if self.is_default:
            status_parts.append("Default")
        if self.is_active:
            status_parts.append("Active")
        if self.is_muted:
            status_parts.append("Muted")

        status = f" • {', '.join(status_parts)}" if status_parts else ""
        return f"{self.description}{status}"

@dataclass
class AudioDeviceState:
    """State container for audio device management (like React state)."""
    devices: list[AudioDevice]
    current_device: AudioDevice | None
    is_loading: bool
    error: str | None
    last_updated: float | None = None

    @property
    def has_devices(self) -> bool:
        """Check if any devices are available."""
        return len(self.devices) > 0

    @property
    def default_device(self) -> AudioDevice | None:
        """Get the default device."""
        return next((d for d in self.devices if d.is_default), None)

@dataclass
class VoiceRecordingState:
    """State container for voice recording (like React state)."""
    status: VoiceRecordingStatus
    is_recording: bool
    duration: float
    file_path: str | None
    file_size: int
    transcription: str | None
    error: str | None

    @property
    def is_active(self) -> bool:
        """Check if recording is currently active."""
        return self.status == VoiceRecordingStatus.RECORDING

    @property
    def has_audio_data(self) -> bool:
        """Check if recording has actual audio data."""
        return self.file_size > 44  # WAV header is 44 bytes

    @property
    def duration_display(self) -> str:
        """Get formatted duration string."""
        minutes = int(self.duration // 60)
        seconds = int(self.duration % 60)
        return f"{minutes:02d}:{seconds:02d}"

@dataclass
class AudioSystemInfo:
    """Information about the audio system."""
    audio_server: str  # "PipeWire", "PulseAudio", "ALSA"
    default_source: str | None
    default_sink: str | None
    sample_rate: int
    buffer_size: int

    @property
    def is_pipewire(self) -> bool:
        """Check if using PipeWire."""
        return self.audio_server.lower() == "pipewire"

    @property
    def is_pulseaudio(self) -> bool:
        """Check if using PulseAudio."""
        return self.audio_server.lower() == "pulseaudio"
