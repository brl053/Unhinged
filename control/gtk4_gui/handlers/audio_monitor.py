"""
Real-time Audio Monitor for Voice Visualization

This module provides real-time audio level monitoring that works alongside
the existing arecord-based recording system. It captures live audio amplitude
data for visualization without interfering with the main recording process.
"""

import subprocess
import threading
import time
import sys
from collections.abc import Callable
from pathlib import Path

# Add utils to path for audio_utils import
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))

from audio_utils import calculate_rms_amplitude
from event_bus import get_event_bus, AudioEvents, Event

try:
    from ..models.audio_types import AudioDevice, AudioDeviceType
except ImportError:
    try:
        from models.audio_types import AudioDevice, AudioDeviceType
    except ImportError:
        # Fallback for testing - create minimal device class
        from dataclasses import dataclass
        from enum import Enum

        class AudioDeviceType(Enum):
            MICROPHONE = "microphone"
            SPEAKER = "speaker"
            UNKNOWN = "unknown"

        @dataclass
        class AudioDevice:
            name: str
            description: str
            card_id: int
            device_id: int
            alsa_device: str
            icon: str
            device_type: AudioDeviceType = AudioDeviceType.UNKNOWN
            connection_type: str = "unknown"
            driver: str = "ALSA"
            subdevices: int = 1
            is_default: bool = False
            is_active: bool = False
            volume: float | None = None
            is_muted: bool = False


try:
    from .config import app_config
except ImportError:
    try:
        from config import app_config
    except ImportError:
        # Fallback for testing - use default device
        class MockConfig:
            audio_device = "pipewire"

        app_config = MockConfig()


class AudioLevelMonitor:
    """Real-time audio level monitor using native ALSA tools"""

    def __init__(self):
        self.is_monitoring = False
        self.monitor_thread: threading.Thread | None = None
        self.monitor_process: subprocess.Popen | None = None

        # Event bus for amplitude updates (replaces callbacks)
        self._event_bus = get_event_bus()

        # Legacy callback for backward compatibility
        self.amplitude_callback: Callable[[float], None] | None = None
        self.sample_rate = 16000
        self.channels = 1
        self.format = "S16_LE"  # 16-bit signed little endian

    def set_amplitude_callback(self, callback: Callable[[float], None]) -> None:
        """Set callback function to receive amplitude updates (DEPRECATED: use event_bus instead)"""
        self.amplitude_callback = callback

    def subscribe_to_amplitude(
        self, callback: Callable[[Event], None]
    ) -> Callable[[], None]:
        """Subscribe to amplitude updates via event bus

        Args:
            callback: Function to call when amplitude is updated

        Returns:
            Unsubscribe function
        """
        return self._event_bus.subscribe(AudioEvents.AMPLITUDE_UPDATED, callback)

    def start_monitoring(self) -> bool:
        """Start real-time audio level monitoring"""
        if self.is_monitoring:
            return True

        try:
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(
                target=self._monitor_audio_levels, daemon=True
            )
            self.monitor_thread.start()
            return True

        except Exception as e:
            print(f"Failed to start audio monitoring: {e}")
            self.is_monitoring = False
            return False

    def stop_monitoring(self) -> None:
        """Stop audio level monitoring"""
        self.is_monitoring = False

        if self.monitor_process:
            try:
                self.monitor_process.terminate()
                self.monitor_process.wait(timeout=2)
            except Exception as e:
                print(f"Error stopping monitor process: {e}")
            finally:
                self.monitor_process = None

    def _monitor_audio_levels(self) -> None:
        """Monitor audio levels in background thread"""
        try:
            # Use arecord to capture raw audio data in small chunks
            cmd = [
                "arecord",
                "-D",
                app_config.audio_device,
                "-f",
                self.format,
                "-r",
                str(self.sample_rate),
                "-c",
                str(self.channels),
                "-t",
                "raw",  # Raw format for easier processing
                "--buffer-size=1024",  # Small buffer for low latency
                "-",  # Output to stdout
            ]

            self.monitor_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=0,  # Unbuffered for real-time processing
            )

            # Process audio data in chunks
            chunk_size = 1024  # 1024 bytes = 512 samples for S16_LE

            while self.is_monitoring and self.monitor_process:
                try:
                    # Read audio chunk
                    audio_data = self.monitor_process.stdout.read(chunk_size)

                    if not audio_data:
                        break

                    # Calculate amplitude from raw audio data
                    amplitude = self._calculate_amplitude(audio_data)

                    # Emit amplitude event via event bus
                    self._event_bus.emit_simple(
                        AudioEvents.AMPLITUDE_UPDATED, {"amplitude": amplitude}
                    )

                    # Legacy callback support
                    if self.amplitude_callback:
                        self.amplitude_callback(amplitude)

                    # Small delay to prevent overwhelming the UI
                    time.sleep(0.02)  # 50 FPS update rate

                except Exception as e:
                    if (
                        self.is_monitoring
                    ):  # Only log if we're still supposed to be monitoring
                        print(f"Audio monitoring error: {e}")
                    break

        except Exception as e:
            print(f"Failed to start audio monitoring process: {e}")
        finally:
            self.stop_monitoring()

    def _calculate_amplitude(self, audio_data: bytes) -> float:
        """Calculate amplitude from raw audio data"""
        return calculate_rms_amplitude(audio_data)

    def get_playback_devices(self):
        """Get available audio playback devices (for compatibility with complex.py)"""
        from audio_utils import get_playback_devices as get_playback_devices_util

        # Get devices from utility function
        util_devices = get_playback_devices_util()

        # Convert to AudioDevice format for compatibility
        devices = []
        for util_device in util_devices:
            device = AudioDevice(
                name=util_device.name,
                description=util_device.name,
                card_id=util_device.card_number,
                device_id=util_device.device_number,
                alsa_device=util_device.device_id,
                icon="audio-speakers-symbolic",
                device_type=AudioDeviceType.SPEAKER,
                driver="ALSA",
                subdevices=1,
                is_default=False,
                is_active=False,
                volume=None,
                is_muted=False,
            )
            devices.append(device)

        return devices

    def get_capture_devices(self):
        """Get available audio capture devices"""
        from audio_utils import get_capture_devices as get_capture_devices_util

        # Get devices from utility function
        util_devices = get_capture_devices_util()

        # Convert to AudioDevice format for compatibility
        devices = []
        for util_device in util_devices:
            device = AudioDevice(
                name=util_device.name,
                description=util_device.name,
                card_id=util_device.card_number,
                device_id=util_device.device_number,
                alsa_device=util_device.device_id,
                icon="audio-input-microphone-symbolic",
                device_type=AudioDeviceType.MICROPHONE,
                driver="ALSA",
                subdevices=1,
                is_default=False,
                is_active=False,
                volume=None,
                is_muted=False,
            )
            devices.append(device)

        return devices


class AudioVisualizationBridge:
    """Bridge between AudioHandler and VoiceVisualizer for real-time feedback"""

    def __init__(self):
        self.audio_monitor = AudioLevelMonitor()
        self.voice_visualizer = None
        self.is_recording = False

    def set_voice_visualizer(self, visualizer) -> None:
        """Set the voice visualizer component"""
        self.voice_visualizer = visualizer
        # Set up amplitude callback
        self.audio_monitor.set_amplitude_callback(self._on_amplitude_update)

    def start_recording_visualization(self) -> bool:
        """Start real-time visualization during recording"""
        self.is_recording = True
        return self.audio_monitor.start_monitoring()

    def stop_recording_visualization(self) -> None:
        """Stop real-time visualization"""
        self.is_recording = False
        self.audio_monitor.stop_monitoring()

    def _on_amplitude_update(self, amplitude: float) -> None:
        """Handle amplitude updates from audio monitor"""
        if self.is_recording and self.voice_visualizer:
            # Send real amplitude data to visualizer
            self.voice_visualizer.set_amplitude(amplitude)


# Test function for development
def test_audio_monitoring():
    """Test the audio monitoring functionality"""
    print("🎤 Testing real-time audio monitoring...")

    def amplitude_callback(amplitude):
        # Create simple ASCII visualization
        bar_length = int(amplitude * 50)
        bar = "█" * bar_length + "░" * (50 - bar_length)
        print(f"\rAmplitude: {amplitude:.3f} |{bar}|", end="", flush=True)

    monitor = AudioLevelMonitor()
    monitor.set_amplitude_callback(amplitude_callback)

    print("Starting monitoring (speak into microphone)...")
    if monitor.start_monitoring():
        try:
            time.sleep(10)  # Monitor for 10 seconds
        except KeyboardInterrupt:
            pass
        finally:
            monitor.stop_monitoring()
            print("\n✅ Monitoring stopped")
    else:
        print("❌ Failed to start monitoring")


if __name__ == "__main__":
    test_audio_monitoring()
