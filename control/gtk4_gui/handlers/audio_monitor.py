"""
Real-time Audio Monitor for Voice Visualization

This module provides real-time audio level monitoring that works alongside
the existing arecord-based recording system. It captures live audio amplitude
data for visualization without interfering with the main recording process.
"""

import subprocess
import threading
import time
import struct
import math
from typing import Optional, Callable
from pathlib import Path

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
        self.monitor_thread: Optional[threading.Thread] = None
        self.monitor_process: Optional[subprocess.Popen] = None
        self.amplitude_callback: Optional[Callable[[float], None]] = None
        self.sample_rate = 16000
        self.channels = 1
        self.format = 'S16_LE'  # 16-bit signed little endian
        
    def set_amplitude_callback(self, callback: Callable[[float], None]) -> None:
        """Set callback function to receive amplitude updates"""
        self.amplitude_callback = callback
    
    def start_monitoring(self) -> bool:
        """Start real-time audio level monitoring"""
        if self.is_monitoring:
            return True
            
        try:
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(
                target=self._monitor_audio_levels,
                daemon=True
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
                'arecord',
                '-D', app_config.audio_device,
                '-f', self.format,
                '-r', str(self.sample_rate),
                '-c', str(self.channels),
                '-t', 'raw',  # Raw format for easier processing
                '--buffer-size=1024',  # Small buffer for low latency
                '-'  # Output to stdout
            ]
            
            self.monitor_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=0  # Unbuffered for real-time processing
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
                    
                    # Send amplitude to callback
                    if self.amplitude_callback:
                        self.amplitude_callback(amplitude)
                    
                    # Small delay to prevent overwhelming the UI
                    time.sleep(0.02)  # 50 FPS update rate
                    
                except Exception as e:
                    if self.is_monitoring:  # Only log if we're still supposed to be monitoring
                        print(f"Audio monitoring error: {e}")
                    break
                    
        except Exception as e:
            print(f"Failed to start audio monitoring process: {e}")
        finally:
            self.stop_monitoring()
    
    def _calculate_amplitude(self, audio_data: bytes) -> float:
        """Calculate amplitude from raw audio data"""
        try:
            # Convert bytes to 16-bit signed integers
            samples = struct.unpack(f'<{len(audio_data)//2}h', audio_data)
            
            # Calculate RMS (Root Mean Square) amplitude
            if samples:
                rms = math.sqrt(sum(sample * sample for sample in samples) / len(samples))
                # Normalize to 0.0-1.0 range (16-bit max is 32767)
                normalized_amplitude = min(1.0, rms / 32767.0)
                return normalized_amplitude
            else:
                return 0.0
                
        except Exception as e:
            print(f"Error calculating amplitude: {e}")
            return 0.0

    def get_playback_devices(self):
        """Get available audio playback devices (for compatibility with complex.py)"""
        try:
            # Use aplay to list playback devices
            result = subprocess.run(['aplay', '-l'], capture_output=True, text=True)
            devices = []

            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'card' in line and ':' in line:
                        # Parse device info from aplay output
                        parts = line.split(':')
                        if len(parts) >= 2:
                            device_info = {
                                'name': parts[1].strip(),
                                'id': parts[0].strip(),
                                'type': 'playback',
                                'is_default': False,  # Add missing attribute
                                'is_enabled': True,   # Add missing attribute
                                'description': parts[1].strip()  # Add description
                            }
                            devices.append(device_info)

            return devices

        except Exception as e:
            print(f"Error getting playback devices: {e}")
            return []

    def get_capture_devices(self):
        """Get available audio capture devices"""
        try:
            # Use arecord to list capture devices
            result = subprocess.run(['arecord', '-l'], capture_output=True, text=True)
            devices = []

            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'card' in line and ':' in line:
                        # Parse device info from arecord output
                        parts = line.split(':')
                        if len(parts) >= 2:
                            device_info = {
                                'name': parts[1].strip(),
                                'id': parts[0].strip(),
                                'type': 'capture',
                                'is_default': False,  # Add missing attribute
                                'is_enabled': True,   # Add missing attribute
                                'description': parts[1].strip()  # Add description
                            }
                            devices.append(device_info)

            return devices

        except Exception as e:
            print(f"Error getting capture devices: {e}")
            return []


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
        bar = '█' * bar_length + '░' * (50 - bar_length)
        print(f"\rAmplitude: {amplitude:.3f} |{bar}|", end='', flush=True)
    
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
