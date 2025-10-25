#!/usr/bin/env python3
"""
@llm-type dependency-installer
@llm-legend Automated audio dependency installation and setup guidance system
@llm-key Cross-platform audio dependency detection, installation, and user guidance
@llm-map Support component providing installation guidance for voice transcription pipeline
@llm-axiom Clear installation guidance reduces user friction in voice feature adoption
@llm-contract Platform-specific dependency detection and automated installation assistance
@llm-token audio-installer: Dependency management for voice transcription components
"""
"""
🔧 Audio Dependencies Installer - Voice Pipeline Setup Assistant

Comprehensive audio dependency management system providing automated detection,
installation guidance, and setup assistance for the voice transcription pipeline.

This component ensures users can easily enable voice functionality by providing
clear, platform-specific installation instructions and automated setup where possible.

Key Design Principles:
- Cross-platform dependency detection
- Automated installation where possible
- Clear user guidance for manual steps
- Graceful degradation when dependencies unavailable
- Platform-specific instruction customization

Supported Platforms:
- Linux: PortAudio, ALSA, PulseAudio development libraries
- macOS: Homebrew-based PortAudio installation
- Windows: Pre-compiled wheel installation guidance

Integration:
Voice Pipeline → Dependency Check → This Component → Installation Guidance → User
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

import logging; gui_logger = logging.getLogger(__name__)


class AudioInstaller:
    """Handles audio dependency installation and setup"""
    
    @staticmethod
    def check_system_requirements():
        """Check what system audio dependencies are available"""
        system = platform.system()
        requirements = {
            'system': system,
            'portaudio_available': False,
            'python_dev_available': False,
            'can_install_sudo': False,
            'alternative_available': False
        }
        
        if system == "Linux":
            # Check if PortAudio is available
            try:
                result = subprocess.run(['pkg-config', '--exists', 'portaudio-2.0'], 
                                      capture_output=True, timeout=5)
                requirements['portaudio_available'] = result.returncode == 0
            except:
                pass
            
            # Check if we can use apt
            try:
                result = subprocess.run(['which', 'apt'], capture_output=True, timeout=5)
                requirements['can_install_sudo'] = result.returncode == 0
            except:
                pass
                
        return requirements
    
    @staticmethod
    def get_installation_instructions():
        """Get platform-specific installation instructions"""
        system = platform.system()
        
        if system == "Linux":
            return {
                'title': 'Audio Dependencies Installation (Linux)',
                'required_packages': [
                    'portaudio19-dev',
                    'python3-dev',
                    'libasound2-dev'  # ALSA development headers
                ],
                'commands': [
                    'sudo apt update',
                    'sudo apt install -y portaudio19-dev python3-dev libasound2-dev',
                    'pip install pyaudio sounddevice'
                ],
                'explanation': 'These packages provide the system libraries needed for audio capture.',
                'alternative': 'If you cannot install system packages, voice input will be disabled but text chat will work normally.'
            }
        elif system == "Darwin":  # macOS
            return {
                'title': 'Audio Dependencies Installation (macOS)',
                'required_packages': ['portaudio'],
                'commands': [
                    'brew install portaudio',
                    'pip install pyaudio sounddevice'
                ],
                'explanation': 'PortAudio is required for microphone access on macOS.',
                'alternative': 'Voice input requires microphone permissions in System Preferences.'
            }
        elif system == "Windows":
            return {
                'title': 'Audio Dependencies Installation (Windows)',
                'required_packages': ['Microsoft Visual C++ Build Tools'],
                'commands': [
                    'pip install pyaudio sounddevice'
                ],
                'explanation': 'PyAudio should install automatically on Windows.',
                'alternative': 'If installation fails, download pre-compiled wheels from unofficial sources.'
            }
        else:
            return {
                'title': f'Audio Dependencies Installation ({system})',
                'required_packages': ['portaudio', 'python development headers'],
                'commands': ['pip install pyaudio sounddevice'],
                'explanation': 'Audio capture requires system audio libraries.',
                'alternative': 'Voice input may not be available on this platform.'
            }
    
    @staticmethod
    def attempt_automatic_installation():
        """Attempt to install audio dependencies automatically"""
        venv_path = Path(__file__).parent.parent.parent.parent.parent.parent / "build" / "python" / "venv"
        pip_path = venv_path / "bin" / "pip"
        
        if not pip_path.exists():
            return False, "Virtual environment not found"
        
        try:
            # Try installing PyAudio first
            result = subprocess.run([
                str(pip_path), 'install', 'pyaudio'
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                return True, "PyAudio installed successfully"
            else:
                # Try sounddevice as alternative
                result = subprocess.run([
                    str(pip_path), 'install', 'sounddevice'
                ], capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    return True, "sounddevice installed as PyAudio alternative"
                else:
                    return False, f"Installation failed: {result.stderr}"
                    
        except subprocess.TimeoutExpired:
            return False, "Installation timed out"
        except Exception as e:
            return False, f"Installation error: {e}"
    
    @staticmethod
    def print_installation_help():
        """Print comprehensive installation help"""
        print("\n" + "="*60)
        print("🎤 AUDIO DEPENDENCIES SETUP")
        print("="*60)
        
        requirements = AudioInstaller.check_system_requirements()
        instructions = AudioInstaller.get_installation_instructions()
        
        print(f"\n📋 System: {requirements['system']}")
        print(f"🔊 PortAudio Available: {'✅' if requirements['portaudio_available'] else '❌'}")
        print(f"🐍 Python Dev Headers: {'✅' if requirements['python_dev_available'] else '❌'}")
        
        print(f"\n📖 {instructions['title']}")
        print(f"📦 Required packages: {', '.join(instructions['required_packages'])}")
        
        print(f"\n🔧 Installation commands:")
        for cmd in instructions['commands']:
            print(f"   {cmd}")
        
        print(f"\n💡 {instructions['explanation']}")
        print(f"🔄 Alternative: {instructions['alternative']}")
        
        print("\n" + "="*60)


def main():
    """Main function for standalone execution"""
    AudioInstaller.print_installation_help()
    
    print("\n🚀 Attempting automatic installation...")
    success, message = AudioInstaller.attempt_automatic_installation()
    
    if success:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")
        print("\n📋 Please run the installation commands above manually.")


if __name__ == "__main__":
    main()
