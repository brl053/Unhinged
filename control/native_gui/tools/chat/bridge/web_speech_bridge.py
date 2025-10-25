#!/usr/bin/env python3
"""
@llm-type web-speech-bridge
@llm-legend WebKit-based bridge for browser Web Speech API integration
@llm-key Embedded browser speech recognition using native Web Speech API capabilities
@llm-map Future enhancement component for browser-native voice transcription
@llm-axiom Browser-native APIs provide superior user experience to system-level audio capture
@llm-contract WebKit bridge interface for Web Speech API integration in native applications
@llm-token web-speech-bridge: Browser API integration for voice transcription
"""
"""
🌐 Web Speech API Bridge - Browser-Native Voice Processing

WebKit-based bridge component that enables integration of browser Web Speech API
capabilities within the native GUI application framework.

This component represents a future enhancement path that leverages browser-native
speech recognition APIs, potentially providing superior user experience compared
to system-level audio capture approaches.

Key Design Principles:
- Browser-native Web Speech API integration
- WebKit embedded browser component
- JavaScript ↔ Python communication bridge
- No external audio library dependencies
- Native browser permission handling

Architecture Vision:
GUI → WebKit WebView → Web Speech API → JavaScript Bridge → Python → Transcript

Currently implemented as future enhancement foundation, with primary voice pipeline
using native audio capture → Whisper service approach.
"""

import logging; gui_logger = logging.getLogger(__name__)

import json
import tempfile
import threading
import time
from typing import Optional, Callable
from pathlib import Path

# Try to import WebKit for embedded browser
WEBKIT_AVAILABLE = False
try:
    import gi
    gi.require_version('WebKit2', '4.0')
    from gi.repository import WebKit2, GLib
    WEBKIT_AVAILABLE = True
    gui_logger.info(" WebKit2 available for Web Speech API")
except (ImportError, ValueError) as e:
    gui_logger.debug(f" WebKit2 not available: {e}")


class WebSpeechBridge:
    """
    Bridge to use Web Speech API through embedded WebKit browser.
    This provides native speech recognition without PyAudio dependencies.
    """
    
    def __init__(self):
        self.available = WEBKIT_AVAILABLE
        self.webview = None
        self.is_recording = False
        self.current_callback = None
        self.speech_result = None
        
        if self.available:
            self._initialize_webview()
    
    def _initialize_webview(self):
        """Initialize the WebKit webview for speech recognition"""
        try:
            # Create a hidden webview for speech recognition
            self.webview = WebKit2.WebView()
            
            # Connect to script message received
            content_manager = self.webview.get_user_content_manager()
            content_manager.connect('script-message-received::speech', self._on_speech_message)
            content_manager.register_script_message_handler('speech')
            
            # Load the speech recognition HTML
            self._load_speech_html()
            
            gui_logger.info(" Web Speech API bridge initialized")
            
        except Exception as e:
            gui_logger.error(f" Failed to initialize WebKit webview: {e}")
            self.available = False
    
    def _load_speech_html(self):
        """Load HTML with Web Speech API implementation"""
        html_content = self._get_speech_html()
        
        # Create temporary HTML file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(html_content)
            html_path = f.name
        
        # Load the HTML
        self.webview.load_uri(f"file://{html_path}")
    
    def _get_speech_html(self) -> str:
        """Get HTML content with Web Speech API implementation"""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>Speech Recognition Bridge</title>
    <meta charset="utf-8">
</head>
<body>
    <div id="status">Ready for speech recognition</div>
    
    <script>
        // Web Speech API implementation
        let recognition = null;
        let isRecording = false;
        
        // Initialize speech recognition
        function initSpeechRecognition() {
            if ('webkitSpeechRecognition' in window) {
                recognition = new webkitSpeechRecognition();
            } else if ('SpeechRecognition' in window) {
                recognition = new SpeechRecognition();
            } else {
                sendMessage('error', 'Speech recognition not supported');
                return false;
            }
            
            // Configure recognition
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-US';
            
            // Event handlers
            recognition.onstart = function() {
                isRecording = true;
                sendMessage('started', 'Recording started');
            };
            
            recognition.onresult = function(event) {
                const result = event.results[0][0].transcript;
                const confidence = event.results[0][0].confidence;
                sendMessage('result', {
                    transcript: result,
                    confidence: confidence
                });
            };
            
            recognition.onerror = function(event) {
                sendMessage('error', 'Recognition error: ' + event.error);
            };
            
            recognition.onend = function() {
                isRecording = false;
                sendMessage('ended', 'Recording ended');
            };
            
            return true;
        }
        
        // Send message to Python
        function sendMessage(type, data) {
            window.webkit.messageHandlers.speech.postMessage({
                type: type,
                data: data,
                timestamp: Date.now()
            });
        }
        
        // Start recording
        function startRecording() {
            if (!recognition) {
                if (!initSpeechRecognition()) {
                    return;
                }
            }
            
            if (!isRecording) {
                try {
                    recognition.start();
                } catch (e) {
                    sendMessage('error', 'Failed to start recording: ' + e.message);
                }
            }
        }
        
        // Stop recording
        function stopRecording() {
            if (recognition && isRecording) {
                recognition.stop();
            }
        }
        
        // Check if speech recognition is available
        function checkAvailability() {
            const available = 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window;
            sendMessage('availability', {
                available: available,
                userAgent: navigator.userAgent
            });
        }
        
        // Initialize on load
        window.addEventListener('load', function() {
            checkAvailability();
            sendMessage('ready', 'Web Speech API bridge ready');
        });
        
        // Expose functions globally for Python to call
        window.speechBridge = {
            start: startRecording,
            stop: stopRecording,
            check: checkAvailability
        };
    </script>
</body>
</html>
        """
    
    def _on_speech_message(self, content_manager, result):
        """Handle messages from the Web Speech API"""
        try:
            message_data = result.get_js_value().to_string()
            message = json.loads(message_data)
            
            msg_type = message.get('type')
            data = message.get('data')
            
            if msg_type == 'ready':
                gui_logger.info(" Web Speech API ready")
            elif msg_type == 'availability':
                available = data.get('available', False)
                gui_logger.info(f" Web Speech API available: {available}")
            elif msg_type == 'started':
                gui_logger.info(" Speech recording started")
                self.is_recording = True
            elif msg_type == 'result':
                transcript = data.get('transcript', '')
                confidence = data.get('confidence', 0.0)
                gui_logger.info(f" Speech result: {transcript} (confidence: {confidence:.2f})")
                self.speech_result = transcript
                if self.current_callback:
                    GLib.idle_add(self.current_callback, transcript)
            elif msg_type == 'error':
                gui_logger.error(f" Speech recognition error: {data}")
                if self.current_callback:
                    GLib.idle_add(self.current_callback, f"Error: {data}")
            elif msg_type == 'ended':
                gui_logger.info(" Speech recording ended")
                self.is_recording = False
                
        except Exception as e:
            gui_logger.error(f" Error handling speech message: {e}")
    
    def is_available(self) -> bool:
        """Check if Web Speech API bridge is available"""
        return self.available and self.webview is not None
    
    def start_recording(self, callback: Optional[Callable[[str], None]] = None):
        """Start speech recognition"""
        if not self.is_available():
            if callback:
                callback("Web Speech API not available")
            return
        
        self.current_callback = callback
        
        # Execute JavaScript to start recording
        self.webview.run_javascript("window.speechBridge.start();", None, None, None)
    
    def stop_recording(self):
        """Stop speech recognition"""
        if not self.is_available():
            return
        
        # Execute JavaScript to stop recording
        self.webview.run_javascript("window.speechBridge.stop();", None, None, None)
        self.is_recording = False
    
    def get_status(self) -> dict:
        """Get status information"""
        return {
            'available': self.is_available(),
            'webkit_available': WEBKIT_AVAILABLE,
            'recording': self.is_recording,
            'backend': 'Web Speech API' if self.is_available() else None
        }


def create_web_speech_bridge() -> WebSpeechBridge:
    """Factory function to create a Web Speech API bridge"""
    return WebSpeechBridge()


def test_web_speech():
    """Test function for Web Speech API bridge"""
    bridge = create_web_speech_bridge()
    status = bridge.get_status()
    
    print("🌐 Web Speech API Bridge Test:")
    print(f"   Available: {'✅' if status['available'] else '❌'}")
    print(f"   WebKit Available: {'✅' if status['webkit_available'] else '❌'}")
    print(f"   Backend: {status['backend'] or 'None'}")
    
    if not status['available']:
        print("💡 Web Speech API requires WebKit2 for embedded browser support")
        print("   Install with: sudo apt install libwebkit2gtk-4.0-dev")


if __name__ == "__main__":
    test_web_speech()
