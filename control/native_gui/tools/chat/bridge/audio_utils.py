
import logging; gui_logger = logging.getLogger(__name__)

"""
Audio Utilities and Device Management
Provides helper functions for audio device detection and configuration.
"""

import pyaudio
import platform
import subprocess
from typing import List, Dict, Optional


class AudioDeviceManager:
    """Manages audio device detection and configuration"""
    
    @staticmethod
    def get_system_info() -> Dict[str, str]:
        """Get system audio information"""
        system = platform.system()
        
        info = {
            'platform': system,
            'architecture': platform.architecture()[0],
            'python_version': platform.python_version()
        }
        
        # Platform-specific audio system info
        if system == "Linux":
            try:
                # Check for PulseAudio
                result = subprocess.run(['pulseaudio', '--version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    info['audio_system'] = 'PulseAudio'
                    info['pulseaudio_version'] = result.stdout.strip()
            except:
                try:
                    # Check for ALSA
                    result = subprocess.run(['aplay', '--version'], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        info['audio_system'] = 'ALSA'
                except:
                    info['audio_system'] = 'Unknown'
        
        elif system == "Darwin":  # macOS
            info['audio_system'] = 'CoreAudio'
        
        elif system == "Windows":
            info['audio_system'] = 'WASAPI/DirectSound'
        
        return info
    
    @staticmethod
    def check_audio_permissions() -> bool:
        """Check if audio recording permissions are available"""
        try:
            # Try to initialize PyAudio briefly
            p = pyaudio.PyAudio()
            
            # Try to get default input device
            default_input = p.get_default_input_device_info()
            
            # Try to open a test stream
            test_stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=1024,
                input_device_index=default_input['index']
            )
            
            # Close immediately
            test_stream.close()
            p.terminate()
            
            return True
            
        except Exception as e:
            gui_logger.warn(f" Audio permission check failed: {e}")
            return False
    
    @staticmethod
    def get_recommended_device() -> Optional[Dict]:
        """Get recommended audio input device"""
        try:
            p = pyaudio.PyAudio()
            
            # Get default input device
            try:
                default_device = p.get_default_input_device_info()
                p.terminate()
                
                return {
                    'index': default_device['index'],
                    'name': default_device['name'],
                    'channels': default_device['maxInputChannels'],
                    'sample_rate': int(default_device['defaultSampleRate']),
                    'is_default': True
                }
            except:
                # If no default, find first available input device
                device_count = p.get_device_count()
                
                for i in range(device_count):
                    device_info = p.get_device_info_by_index(i)
                    if device_info['maxInputChannels'] > 0:
                        p.terminate()
                        return {
                            'index': i,
                            'name': device_info['name'],
                            'channels': device_info['maxInputChannels'],
                            'sample_rate': int(device_info['defaultSampleRate']),
                            'is_default': False
                        }
                
                p.terminate()
                return None
                
        except Exception as e:
            gui_logger.error(f" Failed to get recommended device: {e}")
            return None
    
    @staticmethod
    def test_device_compatibility(device_index: int) -> Dict[str, bool]:
        """Test device compatibility with different audio formats"""
        results = {
            'basic_access': False,
            'mono_16khz': False,
            'stereo_44khz': False,
            'low_latency': False
        }
        
        try:
            p = pyaudio.PyAudio()
            
            # Test basic access
            try:
                device_info = p.get_device_info_by_index(device_index)
                results['basic_access'] = device_info['maxInputChannels'] > 0
            except:
                p.terminate()
                return results
            
            # Test mono 16kHz (Whisper format)
            try:
                stream = p.open(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    input=True,
                    frames_per_buffer=1024,
                    input_device_index=device_index
                )
                stream.close()
                results['mono_16khz'] = True
            except:
                pass
            
            # Test stereo 44.1kHz (CD quality)
            try:
                stream = p.open(
                    format=pyaudio.paInt16,
                    channels=2,
                    rate=44100,
                    input=True,
                    frames_per_buffer=1024,
                    input_device_index=device_index
                )
                stream.close()
                results['stereo_44khz'] = True
            except:
                pass
            
            # Test low latency (small buffer)
            try:
                stream = p.open(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    input=True,
                    frames_per_buffer=256,  # Smaller buffer
                    input_device_index=device_index
                )
                stream.close()
                results['low_latency'] = True
            except:
                pass
            
            p.terminate()
            
        except Exception as e:
            gui_logger.error(f" Device compatibility test failed: {e}")
        
        return results
    
    @staticmethod
    def get_installation_instructions() -> Dict[str, str]:
        """Get platform-specific installation instructions for audio dependencies"""
        system = platform.system()
        
        instructions = {
            'platform': system,
            'pyaudio_install': '',
            'system_deps': '',
            'troubleshooting': ''
        }
        
        if system == "Linux":
            instructions.update({
                'pyaudio_install': 'pip install pyaudio',
                'system_deps': 'sudo apt-get install portaudio19-dev python3-pyaudio',
                'troubleshooting': 'If permission denied: sudo usermod -a -G audio $USER'
            })
        
        elif system == "Darwin":  # macOS
            instructions.update({
                'pyaudio_install': 'pip install pyaudio',
                'system_deps': 'brew install portaudio',
                'troubleshooting': 'Grant microphone permission in System Preferences > Security & Privacy'
            })
        
        elif system == "Windows":
            instructions.update({
                'pyaudio_install': 'pip install pyaudio',
                'system_deps': 'No additional system dependencies required',
                'troubleshooting': 'Grant microphone permission in Windows Privacy Settings'
            })
        
        return instructions


def print_audio_system_info():
    """Print comprehensive audio system information"""
    
    # System info
    system_info = AudioDeviceManager.get_system_info()
    for key, value in system_info.items():
    
    
    # Permission check
    has_permissions = AudioDeviceManager.check_audio_permissions()
    
    # Recommended device
    recommended = AudioDeviceManager.get_recommended_device()
    if recommended:
        
        # Test compatibility
        compat = AudioDeviceManager.test_device_compatibility(recommended['index'])
        for test, result in compat.items():
            status = "✅" if result else "❌"
    else:
    
    
    # Installation instructions
    if not has_permissions:
        instructions = AudioDeviceManager.get_installation_instructions()
        gui_logger.debug(" Installation Instructions:", {"event_type": "configuration"})


if __name__ == "__main__":
    print_audio_system_info()
