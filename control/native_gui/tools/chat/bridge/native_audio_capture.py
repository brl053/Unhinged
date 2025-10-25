#!/usr/bin/env python3
"""
Native Audio Capture for Ubuntu
Uses the system's native audio capture (ALSA/PipeWire) instead of Python libraries.
This is the correct approach - let the OS handle audio, not Python.
"""

import logging; gui_logger = logging.getLogger(__name__)

import subprocess
import tempfile
import requests
import threading
import time
from typing import Optional, Callable
from pathlib import Path


class NativeAudioCapture:
    """
    Native audio capture using Ubuntu's built-in audio system.
    No Python audio libraries needed - uses arecord/PipeWire directly.
    """
    
    def __init__(self, whisper_url: str = "http://localhost:1101"):
        self.whisper_url = whisper_url
        self.is_recording = False
        self.recording_process = None
        
        # Check if native audio tools are available
        self.arecord_available = self._check_command("arecord")
        self.pipewire_available = self._check_command("pipewire")
        
        if self.arecord_available:
            gui_logger.info(" Native audio capture available (arecord)")
        else:
            gui_logger.warn(" Native audio capture not available")
    
    def _check_command(self, command: str) -> bool:
        """Check if a command is available"""
        try:
            subprocess.run(["which", command], capture_output=True, check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def is_available(self) -> bool:
        """Check if native audio capture is available"""
        return self.arecord_available
    
    def check_whisper_service(self) -> bool:
        """Check if Whisper service is available"""
        try:
            response = requests.get(f"{self.whisper_url}/health", timeout=5)
            return response.status_code == 200
        except Exception as e:
            gui_logger.debug(f" Whisper service check failed: {e}")
            return False
    
    def record_and_transcribe(self, 
                            duration: float = 3.0,
                            callback: Optional[Callable[[str], None]] = None) -> str:
        """
        Record audio using native system tools and send to Whisper service.
        This is the correct approach - no Python audio libraries needed.
        """
        if not self.is_available():
            return "Native audio capture not available"
        
        if not self.check_whisper_service():
            return "Whisper service not available - start the speech-to-text service"
        
        try:
            self.is_recording = True
            gui_logger.info(f" Recording audio for {duration} seconds using native system...")
            
            # Create temporary file for recording
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_path = temp_file.name
            
            try:
                # Record audio using native arecord (ALSA)
                cmd = [
                    "arecord",
                    "-f", "cd",  # CD quality (16-bit, 44.1kHz, stereo)
                    "-t", "wav",  # WAV format
                    "-d", str(int(duration)),  # Duration in seconds
                    temp_path
                ]
                
                gui_logger.info(f" Running: {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=duration + 5)
                
                if result.returncode != 0:
                    gui_logger.error(f" arecord failed: {result.stderr}")
                    return f"Recording failed: {result.stderr}"
                
                self.is_recording = False
                
                # Check if file was created and has content
                if not Path(temp_path).exists() or Path(temp_path).stat().st_size == 0:
                    return "No audio recorded"
                
                gui_logger.info(f" Audio recorded to {temp_path} ({Path(temp_path).stat().st_size} bytes)")
                
                # Send to Whisper service
                result = self._send_to_whisper(temp_path)
                
                if callback:
                    callback(result)
                    
                return result
                
            finally:
                # Clean up temp file
                Path(temp_path).unlink(missing_ok=True)
                
        except subprocess.TimeoutExpired:
            self.is_recording = False
            return "Recording timeout"
        except Exception as e:
            self.is_recording = False
            gui_logger.error(f" Recording error: {e}")
            return f"Recording failed: {e}"
    
    def _send_to_whisper(self, audio_file_path: str) -> str:
        """Send audio file to Whisper service for transcription"""
        try:
            # Send to Whisper service
            with open(audio_file_path, 'rb') as audio_file:
                files = {'audio': ('recording.wav', audio_file, 'audio/wav')}
                
                # Try different endpoints that might exist
                endpoints = [
                    f"{self.whisper_url}/transcribe",
                    f"{self.whisper_url}/api/transcribe", 
                    f"{self.whisper_url}/stt",
                    f"{self.whisper_url}/speech-to-text"
                ]
                
                for endpoint in endpoints:
                    try:
                        gui_logger.info(f" Trying Whisper endpoint: {endpoint}")
                        response = requests.post(endpoint, files=files, timeout=30)
                        if response.status_code == 200:
                            result = response.json()
                            transcript = self._extract_transcript(result)
                            gui_logger.info(f" Whisper transcription: {transcript}")
                            return transcript
                        else:
                            gui_logger.debug(f" Endpoint {endpoint} returned {response.status_code}")
                    except Exception as e:
                        gui_logger.debug(f" Endpoint {endpoint} failed: {e}")
                        continue
                
                return "Whisper service endpoint not found"
                
        except Exception as e:
            gui_logger.error(f" Whisper service error: {e}")
            return f"Transcription service error: {e}"
    
    def _extract_transcript(self, response_data) -> str:
        """Extract transcript from Whisper service response"""
        # Handle various response formats
        if isinstance(response_data, dict):
            # Try common transcript field names
            for field in ['transcript', 'text', 'result', 'transcription']:
                if field in response_data:
                    return response_data[field]
            
            # Try nested structures
            if 'data' in response_data and isinstance(response_data['data'], dict):
                for field in ['transcript', 'text', 'result']:
                    if field in response_data['data']:
                        return response_data['data'][field]
        
        # Fallback
        return str(response_data)
    
    def start_continuous_recording(self, 
                                 callback: Callable[[str], None],
                                 phrase_duration: float = 3.0):
        """Start continuous recording with callback"""
        if not self.is_available():
            callback("Native audio capture not available")
            return
        
        def recording_loop():
            while self.is_recording:
                try:
                    result = self.record_and_transcribe(duration=phrase_duration)
                    if result and not result.startswith("Recording") and not result.startswith("Native"):
                        callback(result)
                    time.sleep(0.5)  # Brief pause between recordings
                except Exception as e:
                    gui_logger.error(f" Continuous recording error: {e}")
                    break
        
        self.is_recording = True
        thread = threading.Thread(target=recording_loop, daemon=True)
        thread.start()
    
    def stop_recording(self):
        """Stop recording"""
        self.is_recording = False
        if self.recording_process:
            try:
                self.recording_process.terminate()
                self.recording_process.wait(timeout=2)
            except:
                self.recording_process.kill()
            self.recording_process = None
    
    def test_audio_devices(self) -> dict:
        """Test available audio devices"""
        devices = {}
        
        try:
            # List audio devices
            result = subprocess.run(["arecord", "-l"], capture_output=True, text=True)
            if result.returncode == 0:
                devices['arecord_devices'] = result.stdout
            else:
                devices['arecord_error'] = result.stderr
        except Exception as e:
            devices['arecord_error'] = str(e)
        
        return devices
    
    def get_status(self) -> dict:
        """Get comprehensive status"""
        return {
            'available': self.is_available(),
            'arecord_available': self.arecord_available,
            'pipewire_available': self.pipewire_available,
            'whisper_service': self.check_whisper_service(),
            'whisper_url': self.whisper_url,
            'recording': self.is_recording
        }


def test_native_audio_capture():
    """Test the native audio capture"""
    capture = NativeAudioCapture()
    status = capture.get_status()
    
    print("🎤 Native Audio Capture Test:")
    print(f"   Available: {'✅' if status['available'] else '❌'}")
    print(f"   arecord: {'✅' if status['arecord_available'] else '❌'}")
    print(f"   PipeWire: {'✅' if status['pipewire_available'] else '❌'}")
    print(f"   Whisper Service: {'✅' if status['whisper_service'] else '❌'}")
    print(f"   Whisper URL: {status['whisper_url']}")
    
    if status['available']:
        print("\n🔊 Audio Devices:")
        devices = capture.test_audio_devices()
        if 'arecord_devices' in devices:
            print(devices['arecord_devices'])
        else:
            print(f"   Error: {devices.get('arecord_error', 'Unknown error')}")
    
    if not status['whisper_service']:
        print("💡 Start the Whisper service with: docker compose up speech-to-text")


if __name__ == "__main__":
    test_native_audio_capture()
