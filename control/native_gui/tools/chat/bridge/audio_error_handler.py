
# Initialize GUI event logger
gui_logger = create_gui_logger("unhinged-audio-error-handler", "1.0.0")

"""
Audio Error Handler - Comprehensive error handling for audio operations
Provides detailed error analysis and user-friendly error messages.
"""

import platform
import subprocess
from typing import Dict, List, Optional, Tuple
from enum import Enum
from unhinged_events import create_gui_logger


class AudioErrorType(Enum):
    """Types of audio errors"""
    DEVICE_NOT_FOUND = "device_not_found"
    PERMISSION_DENIED = "permission_denied"
    DEVICE_BUSY = "device_busy"
    DRIVER_ERROR = "driver_error"
    FORMAT_UNSUPPORTED = "format_unsupported"
    SYSTEM_ERROR = "system_error"
    UNKNOWN = "unknown"


class AudioErrorHandler:
    """Handles audio errors with detailed analysis and solutions"""
    
    @staticmethod
    def analyze_error(error: Exception) -> Dict[str, str]:
        """Analyze audio error and provide detailed information"""
        error_str = str(error).lower()
        error_type = AudioErrorHandler._classify_error(error_str)
        
        analysis = {
            'type': error_type.value,
            'message': str(error),
            'user_message': AudioErrorHandler._get_user_message(error_type),
            'solution': AudioErrorHandler._get_solution(error_type),
            'platform': platform.system(),
            'technical_details': AudioErrorHandler._get_technical_details(error)
        }
        
        return analysis
    
    @staticmethod
    def _classify_error(error_str: str) -> AudioErrorType:
        """Classify error type based on error message"""
        if any(keyword in error_str for keyword in ['no such file', 'device not found', 'no audio input']):
            return AudioErrorType.DEVICE_NOT_FOUND
        elif any(keyword in error_str for keyword in ['permission denied', 'access denied', 'not permitted']):
            return AudioErrorType.PERMISSION_DENIED
        elif any(keyword in error_str for keyword in ['device unavailable', 'busy', 'in use']):
            return AudioErrorType.DEVICE_BUSY
        elif any(keyword in error_str for keyword in ['driver', 'alsa', 'pulseaudio', 'coreaudio']):
            return AudioErrorType.DRIVER_ERROR
        elif any(keyword in error_str for keyword in ['format', 'sample rate', 'channels']):
            return AudioErrorType.FORMAT_UNSUPPORTED
        elif any(keyword in error_str for keyword in ['system', 'os error', 'errno']):
            return AudioErrorType.SYSTEM_ERROR
        else:
            return AudioErrorType.UNKNOWN
    
    @staticmethod
    def _get_user_message(error_type: AudioErrorType) -> str:
        """Get user-friendly error message"""
        messages = {
            AudioErrorType.DEVICE_NOT_FOUND: "No microphone found. Please connect a microphone and try again.",
            AudioErrorType.PERMISSION_DENIED: "Microphone access denied. Please grant microphone permissions.",
            AudioErrorType.DEVICE_BUSY: "Microphone is being used by another application. Close other apps and try again.",
            AudioErrorType.DRIVER_ERROR: "Audio driver issue detected. Your audio drivers may need updating.",
            AudioErrorType.FORMAT_UNSUPPORTED: "Audio format not supported by your microphone.",
            AudioErrorType.SYSTEM_ERROR: "System audio error. Try restarting the application.",
            AudioErrorType.UNKNOWN: "Unknown audio error occurred. Check your microphone connection."
        }
        return messages.get(error_type, "Audio error occurred.")
    
    @staticmethod
    def _get_solution(error_type: AudioErrorType) -> str:
        """Get platform-specific solution"""
        system = platform.system()
        
        solutions = {
            AudioErrorType.DEVICE_NOT_FOUND: AudioErrorHandler._get_device_solutions(system),
            AudioErrorType.PERMISSION_DENIED: AudioErrorHandler._get_permission_solutions(system),
            AudioErrorType.DEVICE_BUSY: AudioErrorHandler._get_busy_solutions(system),
            AudioErrorType.DRIVER_ERROR: AudioErrorHandler._get_driver_solutions(system),
            AudioErrorType.FORMAT_UNSUPPORTED: "Try using a different microphone or check audio settings.",
            AudioErrorType.SYSTEM_ERROR: "Restart the application or reboot your system.",
            AudioErrorType.UNKNOWN: "Check microphone connection and system audio settings."
        }
        
        return solutions.get(error_type, "Contact support for assistance.")
    
    @staticmethod
    def _get_device_solutions(system: str) -> str:
        """Get device-specific solutions by platform"""
        if system == "Linux":
            return """
1. Check if microphone is connected: lsusb | grep -i audio
2. Install audio packages: sudo apt-get install pulseaudio alsa-utils
3. Test microphone: arecord -l
4. Check PulseAudio: pulseaudio --check -v
"""
        elif system == "Darwin":  # macOS
            return """
1. Check System Preferences > Sound > Input
2. Ensure microphone is selected and not muted
3. Test with built-in microphone first
4. Check Audio MIDI Setup application
"""
        elif system == "Windows":
            return """
1. Check Device Manager > Audio inputs and outputs
2. Right-click sound icon > Recording devices
3. Enable and set microphone as default
4. Update audio drivers from manufacturer
"""
        else:
            return "Check system audio settings and microphone connection."
    
    @staticmethod
    def _get_permission_solutions(system: str) -> str:
        """Get permission-specific solutions by platform"""
        if system == "Linux":
            return """
1. Add user to audio group: sudo usermod -a -G audio $USER
2. Check PulseAudio permissions
3. Restart session after group changes
4. Check AppArmor/SELinux policies if applicable
"""
        elif system == "Darwin":  # macOS
            return """
1. System Preferences > Security & Privacy > Privacy > Microphone
2. Enable microphone access for Terminal/Python
3. May need to restart application after granting permission
4. Check for any parental controls blocking microphone
"""
        elif system == "Windows":
            return """
1. Settings > Privacy > Microphone
2. Enable "Allow apps to access your microphone"
3. Enable for specific applications
4. Check Windows Defender or antivirus settings
"""
        else:
            return "Grant microphone permissions in system settings."
    
    @staticmethod
    def _get_busy_solutions(system: str) -> str:
        """Get solutions for busy device"""
        if system == "Linux":
            return """
1. Check running audio applications: lsof /dev/snd/*
2. Kill processes using audio: sudo fuser -k /dev/snd/*
3. Restart PulseAudio: pulseaudio -k && pulseaudio --start
4. Check for virtual audio devices
"""
        elif system == "Darwin":  # macOS
            return """
1. Check Activity Monitor for audio applications
2. Quit applications using microphone (Zoom, Skype, etc.)
3. Check Audio MIDI Setup for exclusive access
4. Restart Core Audio: sudo killall coreaudiod
"""
        elif system == "Windows":
            return """
1. Close applications using microphone (Skype, Teams, etc.)
2. Check Task Manager for audio processes
3. Restart Windows Audio service
4. Check for exclusive mode in sound settings
"""
        else:
            return "Close other applications using the microphone."
    
    @staticmethod
    def _get_driver_solutions(system: str) -> str:
        """Get driver-specific solutions"""
        if system == "Linux":
            return """
1. Update ALSA: sudo apt-get update && sudo apt-get upgrade alsa-base
2. Reinstall PulseAudio: sudo apt-get install --reinstall pulseaudio
3. Check kernel modules: lsmod | grep snd
4. Try different audio backend
"""
        elif system == "Darwin":  # macOS
            return """
1. Update macOS to latest version
2. Reset Core Audio: sudo killall coreaudiod
3. Check for third-party audio drivers
4. Try different audio interface if available
"""
        elif system == "Windows":
            return """
1. Update audio drivers from Device Manager
2. Download latest drivers from manufacturer website
3. Try Windows generic audio drivers
4. Run Windows Audio troubleshooter
"""
        else:
            return "Update your audio drivers."
    
    @staticmethod
    def _get_technical_details(error: Exception) -> str:
        """Get technical details for debugging"""
        details = [
            f"Error Type: {type(error).__name__}",
            f"Error Message: {str(error)}",
            f"Platform: {platform.system()} {platform.release()}",
            f"Python Version: {platform.python_version()}"
        ]
        
        # Add platform-specific details
        system = platform.system()
        if system == "Linux":
            try:
                # Check audio system
                result = subprocess.run(['pulseaudio', '--version'], 
                                      capture_output=True, text=True, timeout=2)
                if result.returncode == 0:
                    details.append(f"PulseAudio: {result.stdout.strip()}")
            except:
                pass
        
        return "\n".join(details)
    
    @staticmethod
    def get_diagnostic_commands(system: str = None) -> List[str]:
        """Get diagnostic commands for troubleshooting"""
        if system is None:
            system = platform.system()
        
        commands = {
            "Linux": [
                "lsusb | grep -i audio",
                "arecord -l",
                "pulseaudio --check -v",
                "pactl list sources short",
                "lsof /dev/snd/*"
            ],
            "Darwin": [
                "system_profiler SPAudioDataType",
                "ps aux | grep -i audio",
                "sudo lsof | grep -i audio"
            ],
            "Windows": [
                "Get-WmiObject -Class Win32_SoundDevice",
                "Get-Process | Where-Object {$_.ProcessName -like '*audio*'}"
            ]
        }
        
        return commands.get(system, ["echo 'No diagnostic commands available for this platform'"])


def handle_audio_error(error: Exception) -> Dict[str, str]:
    """Main function to handle any audio error"""
    return AudioErrorHandler.analyze_error(error)


def print_audio_error_help(error: Exception):
    """Print comprehensive error help"""
    analysis = handle_audio_error(error)
    
🎤 Audio Error Analysis
{'=' * 50}

Error Type: {analysis['type'].replace('_', ' ').title()}
User Message: {analysis['user_message']}

Solution:
{analysis['solution']}

Technical Details:
{analysis['technical_details']}

Platform: {analysis['platform']}
""")


if __name__ == "__main__":
    # Test error handling
    test_errors = [
        OSError("No such file or directory: '/dev/dsp'"),
        PermissionError("Permission denied: microphone access"),
        RuntimeError("Device unavailable: microphone busy")
    ]
    
    for error in test_errors:
        print_audio_error_help(error)
