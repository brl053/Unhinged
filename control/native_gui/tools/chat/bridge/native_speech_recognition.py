#!/usr/bin/env python3
"""
Native Python Speech Recognition
Simple speech-to-text using the speech_recognition library with multiple backends.
"""

import logging; gui_logger = logging.getLogger(__name__)

import threading
import time
from typing import Optional, Callable

# Try to import speech_recognition
SPEECH_RECOGNITION_AVAILABLE = False
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
    gui_logger.info(" speech_recognition library available")
except ImportError:
    gui_logger.debug(" speech_recognition library not available")


class NativeSpeechRecognizer:
    """
    Simple speech recognition using the speech_recognition library.
    Supports multiple backends including Google Web Speech API.
    """
    
    def __init__(self):
        self.available = SPEECH_RECOGNITION_AVAILABLE
        self.recognizer = None
        self.microphone = None
        self.is_recording = False
        
        if self.available:
            self._initialize_recognizer()
    
    def _initialize_recognizer(self):
        """Initialize the speech recognizer"""
        try:
            self.recognizer = sr.Recognizer()
            
            # Try to initialize microphone (may fail without PyAudio)
            try:
                self.microphone = sr.Microphone()
                gui_logger.info(" Microphone initialized successfully")
            except Exception as e:
                gui_logger.debug(f" Microphone initialization failed: {e}")
                self.microphone = None
                
        except Exception as e:
            gui_logger.error(f" Failed to initialize speech recognizer: {e}")
            self.available = False
    
    def is_available(self) -> bool:
        """Check if speech recognition is available"""
        return self.available and self.recognizer is not None
    
    def can_record_audio(self) -> bool:
        """Check if we can record audio from microphone"""
        return self.microphone is not None
    
    def get_status(self) -> dict:
        """Get detailed status information"""
        return {
            'available': self.is_available(),
            'can_record': self.can_record_audio(),
            'library_available': SPEECH_RECOGNITION_AVAILABLE,
            'microphone_available': self.microphone is not None,
            'supported_engines': [
                'google',  # Google Web Speech API
                'sphinx',  # CMU Sphinx (offline)
                'whisper_api',  # OpenAI Whisper API
            ] if self.is_available() else []
        }
    
    def recognize_from_microphone(self, 
                                 duration: float = 3.0,
                                 engine: str = 'google',
                                 callback: Optional[Callable[[str], None]] = None) -> str:
        """
        Record audio from microphone and transcribe it.
        
        Args:
            duration: Recording duration in seconds
            engine: Recognition engine ('google', 'sphinx', 'whisper_api')
            callback: Optional callback for result
            
        Returns:
            Transcribed text or error message
        """
        if not self.is_available():
            return "Speech recognition not available"
        
        if not self.can_record_audio():
            return "Microphone not available - install PyAudio for microphone support"
        
        try:
            self.is_recording = True
            
            with self.microphone as source:
                gui_logger.info(f" Recording for {duration} seconds...")
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                # Record audio
                audio = self.recognizer.listen(source, timeout=duration, phrase_time_limit=duration)
            
            self.is_recording = False
            
            # Transcribe using selected engine
            result = self._transcribe_audio(audio, engine)
            
            if callback:
                callback(result)
                
            return result
            
        except sr.WaitTimeoutError:
            self.is_recording = False
            return "Recording timeout - no speech detected"
        except sr.RequestError as e:
            self.is_recording = False
            return f"Recognition service error: {e}"
        except sr.UnknownValueError:
            self.is_recording = False
            return "Could not understand audio"
        except Exception as e:
            self.is_recording = False
            gui_logger.error(f" Speech recognition error: {e}")
            return f"Speech recognition failed: {e}"
    
    def _transcribe_audio(self, audio, engine: str = 'google') -> str:
        """Transcribe audio using the specified engine"""
        try:
            if engine == 'google':
                # Google Web Speech API (requires internet)
                return self.recognizer.recognize_google(audio)
            elif engine == 'sphinx':
                # CMU Sphinx (offline, requires pocketsphinx)
                return self.recognizer.recognize_sphinx(audio)
            elif engine == 'whisper_api':
                # OpenAI Whisper API (requires API key)
                return self.recognizer.recognize_whisper_api(audio)
            else:
                # Default to Google
                return self.recognizer.recognize_google(audio)
                
        except sr.RequestError as e:
            return f"Recognition service error: {e}"
        except sr.UnknownValueError:
            return "Could not understand audio"
        except Exception as e:
            return f"Transcription error: {e}"
    
    def recognize_from_file(self, audio_file_path: str, engine: str = 'google') -> str:
        """
        Transcribe audio from a file.
        
        Args:
            audio_file_path: Path to audio file
            engine: Recognition engine to use
            
        Returns:
            Transcribed text or error message
        """
        if not self.is_available():
            return "Speech recognition not available"
        
        try:
            with sr.AudioFile(audio_file_path) as source:
                audio = self.recognizer.record(source)
            
            return self._transcribe_audio(audio, engine)
            
        except Exception as e:
            gui_logger.error(f" File transcription error: {e}")
            return f"File transcription failed: {e}"
    
    def start_continuous_recognition(self, 
                                   callback: Callable[[str], None],
                                   engine: str = 'google',
                                   phrase_time_limit: float = 3.0):
        """
        Start continuous speech recognition in background thread.
        
        Args:
            callback: Function to call with transcription results
            engine: Recognition engine to use
            phrase_time_limit: Maximum time for each phrase
        """
        if not self.is_available() or not self.can_record_audio():
            callback("Speech recognition not available")
            return
        
        def recognition_loop():
            try:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source)
                
                while self.is_recording:
                    try:
                        with self.microphone as source:
                            audio = self.recognizer.listen(source, 
                                                         timeout=1, 
                                                         phrase_time_limit=phrase_time_limit)
                        
                        result = self._transcribe_audio(audio, engine)
                        if result and result.strip():
                            callback(result)
                            
                    except sr.WaitTimeoutError:
                        continue  # No speech detected, continue listening
                    except Exception as e:
                        gui_logger.debug(f" Recognition loop error: {e}")
                        continue
                        
            except Exception as e:
                gui_logger.error(f" Continuous recognition error: {e}")
                callback(f"Recognition error: {e}")
        
        self.is_recording = True
        thread = threading.Thread(target=recognition_loop, daemon=True)
        thread.start()
    
    def stop_continuous_recognition(self):
        """Stop continuous recognition"""
        self.is_recording = False
    
    def test_recognition(self) -> dict:
        """Test speech recognition capabilities"""
        status = self.get_status()
        
        if not status['available']:
            return {
                'success': False,
                'message': 'Speech recognition not available',
                'details': status
            }
        
        if not status['can_record']:
            return {
                'success': False,
                'message': 'Microphone not available - install PyAudio for full functionality',
                'details': status,
                'alternative': 'File-based transcription still available'
            }
        
        return {
            'success': True,
            'message': 'Speech recognition ready',
            'details': status
        }


def create_speech_recognizer() -> NativeSpeechRecognizer:
    """Factory function to create a speech recognizer"""
    return NativeSpeechRecognizer()


def test_speech_recognition():
    """Test function for speech recognition"""
    recognizer = create_speech_recognizer()
    test_result = recognizer.test_recognition()
    
    print("🎤 Speech Recognition Test Results:")
    print(f"   Success: {'✅' if test_result['success'] else '❌'}")
    print(f"   Message: {test_result['message']}")
    
    if 'details' in test_result:
        details = test_result['details']
        print(f"   Library Available: {'✅' if details['library_available'] else '❌'}")
        print(f"   Microphone Available: {'✅' if details['microphone_available'] else '❌'}")
        print(f"   Supported Engines: {', '.join(details['supported_engines'])}")
    
    if 'alternative' in test_result:
        print(f"   Alternative: {test_result['alternative']}")


if __name__ == "__main__":
    test_speech_recognition()
