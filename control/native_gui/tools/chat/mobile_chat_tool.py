"""
@llm-type control-system
@llm-legend mobile_chat_tool.py - system control component
@llm-key Core functionality for mobile_chat_tool
@llm-map Part of the Unhinged system architecture
@llm-axiom Maintains system independence and architectural compliance
@llm-contract Provides standardized interface for system integration
@llm-token mobile_chat_tool: system control component
"""
"""
💬 Mobile-First Chat Tool

Responsive chat interface optimized for mobile-first design.
Features touch-friendly input, adaptive layout, and modern Material Design 3 styling.
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GLib, Pango
from typing import Optional, List, Dict, Any
import json
import asyncio
from pathlib import Path

from ...core.tool_manager import BaseTool

# Try to import LLM client (optional)
try:
    from ...services.llm_client import LLMServiceClient
    LLM_CLIENT_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ LLM client not available: {e}")
    LLM_CLIENT_AVAILABLE = False

# Try to import Speech client (optional)
try:
    from .bridge.speech_client import SpeechClient
    SPEECH_CLIENT_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Speech client not available: {e}")
    SPEECH_CLIENT_AVAILABLE = False
    LLMServiceClient = None


class MobileChatMessage(Gtk.Box):
    """
    Mobile-optimized chat message component.
    
    Features:
    - Touch-friendly sizing
    - Responsive text wrapping
    - Material Design 3 styling
    - Swipe gestures (future)
    """
    
    def __init__(self, message: str, is_user: bool = False, timestamp: str = ""):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        
        self.message = message
        self.is_user = is_user
        
        # Add appropriate CSS classes
        self.add_css_class("chat-message")
        if is_user:
            self.add_css_class("user-message")
            self.set_halign(Gtk.Align.END)
        else:
            self.add_css_class("assistant-message")
            self.set_halign(Gtk.Align.START)
        
        # Message bubble
        bubble = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        bubble.add_css_class("message-bubble")
        bubble.set_margin_start(16 if not is_user else 48)
        bubble.set_margin_end(48 if not is_user else 16)
        bubble.set_margin_top(4)
        bubble.set_margin_bottom(4)
        
        # Message text
        text_label = Gtk.Label(label=message)
        text_label.set_wrap(True)
        text_label.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
        text_label.set_halign(Gtk.Align.START if not is_user else Gtk.Align.END)
        text_label.set_selectable(True)
        text_label.add_css_class("message-text")
        bubble.append(text_label)
        
        # Timestamp (if provided)
        if timestamp:
            time_label = Gtk.Label(label=timestamp)
            time_label.add_css_class("message-timestamp")
            time_label.set_halign(Gtk.Align.END if is_user else Gtk.Align.START)
            bubble.append(time_label)
        
        self.append(bubble)


class MobileChatInput(Gtk.Box):
    """
    Mobile-optimized chat input component.

    Features:
    - Large touch-friendly input area
    - Send button with haptic feedback
    - Voice input button with speech-to-text
    - Auto-resize text area
    """

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        
        self.add_css_class("mobile-chat-input-container")
        self.set_margin_start(16)
        self.set_margin_end(16)
        self.set_margin_top(8)
        self.set_margin_bottom(16)
        
        # Text input
        self.text_view = Gtk.TextView()
        self.text_view.add_css_class("mobile-chat-input")
        self.text_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.text_view.set_accepts_tab(False)
        
        # Set placeholder text
        buffer = self.text_view.get_buffer()
        buffer.set_text("Type your message...")
        
        # Input container with border
        input_frame = Gtk.Frame()
        input_frame.add_css_class("chat-input-frame")
        input_frame.set_child(self.text_view)
        input_frame.set_hexpand(True)
        
        self.append(input_frame)
        
        # Send button
        self.send_button = Gtk.Button()
        self.send_button.add_css_class("mobile-chat-send-button")
        self.send_button.set_label("➤")
        self.send_button.set_tooltip_text("Send message")

        # Microphone button for speech-to-text
        self.mic_button = Gtk.Button()
        self.mic_button.add_css_class("mobile-chat-mic-button")
        self.mic_button.set_label("🎤")
        self.mic_button.set_tooltip_text("Voice input (speech-to-text)")

        # Button container
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        button_box.append(self.mic_button)
        button_box.append(self.send_button)

        self.append(button_box)
        
        # Connect signals
        self.send_button.connect("clicked", self._on_send_clicked)
        self.mic_button.connect("clicked", self._on_mic_clicked)
        
        # Key press handling
        key_controller = Gtk.EventControllerKey()
        key_controller.connect("key-pressed", self._on_key_pressed)
        self.text_view.add_controller(key_controller)
        
        # Callback for message sending
        self.on_message_send: Optional[callable] = None
        
        print("📱 Mobile chat input created")
    
    def get_text(self) -> str:
        """Get current input text"""
        buffer = self.text_view.get_buffer()
        start = buffer.get_start_iter()
        end = buffer.get_end_iter()
        return buffer.get_text(start, end, False).strip()
    
    def clear_text(self):
        """Clear input text"""
        buffer = self.text_view.get_buffer()
        buffer.set_text("")
    
    def focus_input(self):
        """Focus the input field"""
        self.text_view.grab_focus()
    
    def _on_send_clicked(self, button):
        """Handle send button click"""
        self._send_message()
    
    def _on_key_pressed(self, controller, keyval, keycode, state):
        """Handle key press in text view"""
        # Send on Enter (without Shift)
        if keyval == 65293 and not (state & 1):  # Enter without Shift
            self._send_message()
            return True
        return False
    
    def _send_message(self):
        """Send the current message"""
        text = self.get_text()
        if text and self.on_message_send:
            self.on_message_send(text)
            self.clear_text()

    def _on_mic_clicked(self, button):
        """Handle microphone button click for speech-to-text"""
        if hasattr(self, 'on_voice_input') and self.on_voice_input:
            self.on_voice_input()
        else:
            print("🎤 Voice input not configured")


class MobileChatTool(BaseTool):
    """
    Mobile-first chat tool implementation.
    
    Features:
    - Responsive chat interface
    - Touch-optimized input
    - Message history
    - Typing indicators
    - Voice input with speech-to-text
    """
    
    def __init__(self):
        super().__init__()

        # Set tool properties
        self.name = "💬 Chat"
        self.icon = "💬"
        self.description = "AI-powered chat interface optimized for mobile"
        
        self.messages: List[Dict[str, Any]] = []
        self.chat_history_file = Path("chat_history_mobile.json")

        # Initialize LLM service client (if available)
        if LLM_CLIENT_AVAILABLE:
            self.llm_client = LLMServiceClient(preferred_service="ollama")
            self.llm_initialized = False
        else:
            self.llm_client = None
            self.llm_initialized = False
            print("⚠️ Running in offline mode - LLM client not available")

        # Initialize Speech client (if available)
        if SPEECH_CLIENT_AVAILABLE:
            self.speech_client = SpeechClient()
            self.speech_initialized = False
            print("🎤 Speech client available")
        else:
            self.speech_client = None
            self.speech_initialized = False
            print("⚠️ Speech-to-text not available - speech client not found")

        # Load chat history
        self._load_chat_history()

        print("📱 Mobile chat tool initialized")
    
    def create_widget(self) -> Gtk.Widget:
        """Create the mobile chat interface"""
        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        main_box.add_css_class("mobile-chat-interface")
        
        # Chat header
        header = self._create_chat_header()
        main_box.append(header)
        
        # Messages area
        self.messages_container = self._create_messages_area()
        main_box.append(self.messages_container)
        
        # Input area
        self.chat_input = MobileChatInput()
        self.chat_input.on_message_send = self._on_message_send
        self.chat_input.on_voice_input = self._on_voice_input
        main_box.append(self.chat_input)
        
        # Load existing messages
        self._populate_messages()
        
        # Initialize LLM client asynchronously (if available)
        if LLM_CLIENT_AVAILABLE and self.llm_client:
            GLib.timeout_add(100, self._initialize_llm_client)
        else:
            GLib.timeout_add(100, self._set_offline_status)

        # Focus input
        GLib.timeout_add(200, lambda: self.chat_input.focus_input())

        return main_box

    def _initialize_llm_client(self) -> bool:
        """Initialize LLM client using synchronous health checks"""
        def run_sync_init():
            try:
                # Test Ollama availability using requests
                import requests
                response = requests.get("http://localhost:1500/api/tags", timeout=5)
                if response.status_code == 200:
                    self.llm_initialized = True
                    print("🤖 LLM client initialized successfully (Ollama available)")
                else:
                    self.llm_initialized = False
                    print(f"❌ Ollama unhealthy (status: {response.status_code})")

            except ImportError:
                print("⚠️ requests not available - marking LLM as unavailable")
                self.llm_initialized = False
            except Exception as e:
                print(f"❌ LLM client initialization failed: {e}")
                self.llm_initialized = False

            # Update status in UI
            GLib.idle_add(self._update_service_status)

        # Run in background thread
        import threading
        thread = threading.Thread(target=run_sync_init, daemon=True)
        thread.start()

        return False  # Don't repeat

    def _set_offline_status(self) -> bool:
        """Set offline status in UI"""
        if hasattr(self, 'status_label'):
            self.status_label.set_text("🔴 Offline Mode")
        return False  # Don't repeat

    def _update_service_status(self):
        """Update service status in UI"""
        if hasattr(self, 'status_label'):
            if self.llm_initialized:
                status = self.llm_client.get_service_status()
                service_name = status.get('current_service', 'Unknown')
                self.status_label.set_text(f"🟢 {service_name}")
            else:
                self.status_label.set_text("🔴 Offline")

    def _create_chat_header(self) -> Gtk.Widget:
        """Create mobile chat header"""
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        header.add_css_class("mobile-chat-header")
        header.set_margin_start(16)
        header.set_margin_end(16)
        header.set_margin_top(16)
        header.set_margin_bottom(8)
        
        # Title
        title_label = Gtk.Label(label="💬 AI Assistant")
        title_label.add_css_class("chat-header-title")
        title_label.set_halign(Gtk.Align.START)
        title_label.set_hexpand(True)
        header.append(title_label)
        
        # Status indicator
        self.status_label = Gtk.Label(label="🔄 Connecting...")
        self.status_label.add_css_class("chat-status")
        header.append(self.status_label)
        
        return header
    
    def _create_messages_area(self) -> Gtk.Widget:
        """Create scrollable messages area"""
        # Scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)
        scrolled.add_css_class("chat-messages-scroll")
        
        # Messages container
        self.messages_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.messages_box.add_css_class("chat-messages")
        self.messages_box.set_margin_start(8)
        self.messages_box.set_margin_end(8)
        self.messages_box.set_margin_top(8)
        self.messages_box.set_margin_bottom(8)
        
        scrolled.set_child(self.messages_box)
        
        return scrolled
    
    def _populate_messages(self):
        """Populate messages from history"""
        for message_data in self.messages:
            message_widget = MobileChatMessage(
                message=message_data["content"],
                is_user=message_data["role"] == "user",
                timestamp=message_data.get("timestamp", "")
            )
            self.messages_box.append(message_widget)
        
        # Scroll to bottom
        GLib.timeout_add(100, self._scroll_to_bottom)
    
    def _on_message_send(self, text: str):
        """Handle message send"""
        # Add user message
        user_message = {
            "role": "user",
            "content": text,
            "timestamp": GLib.DateTime.new_now_local().format("%H:%M")
        }
        self.messages.append(user_message)
        
        # Create user message widget
        user_widget = MobileChatMessage(
            message=text,
            is_user=True,
            timestamp=user_message["timestamp"]
        )
        self.messages_box.append(user_widget)
        
        # Show typing indicator
        typing_widget = self._create_typing_indicator()
        self.messages_box.append(typing_widget)
        
        # Scroll to bottom
        self._scroll_to_bottom()
        
        # Get real AI response
        self._get_ai_response(typing_widget, text)
        
        # Save history
        self._save_chat_history()
        
        print(f"📱 Message sent: {text}")
    
    def _create_typing_indicator(self) -> Gtk.Widget:
        """Create typing indicator"""
        indicator = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        indicator.add_css_class("typing-indicator")
        indicator.set_margin_start(16)
        indicator.set_margin_top(8)
        
        # Typing dots animation
        dots_label = Gtk.Label(label="💭 AI is thinking...")
        dots_label.add_css_class("typing-dots")
        indicator.append(dots_label)
        
        return indicator

    def _get_ai_response(self, typing_widget: Gtk.Widget, user_message: str):
        """Get real AI response from LLM service"""
        def run_async_response():
            try:
                # Prepare conversation history for context
                history = []
                for msg in self.messages[-10:]:  # Last 10 messages for context
                    if msg["role"] == "user":
                        history.append({"user": msg["content"]})
                    elif msg["role"] == "assistant" and history:
                        history[-1]["assistant"] = msg["content"]

                # Get AI response using requests (synchronous) to avoid event loop issues
                if self.llm_initialized and self.llm_client:
                    response = self._send_sync_message(user_message, history)
                elif not LLM_CLIENT_AVAILABLE:
                    response = "🤖 Offline Mode: This is a mock response. To enable real AI chat, please install dependencies: pip install aiohttp requests"
                else:
                    response = "❌ LLM service not available. Please start services with 'make up' or 'make dev-up'"

                # Update UI in main thread
                GLib.idle_add(self._display_ai_response, typing_widget, response)

            except Exception as e:
                error_response = f"❌ Error getting AI response: {str(e)}"
                GLib.idle_add(self._display_ai_response, typing_widget, error_response)

        # Run in background thread
        import threading
        thread = threading.Thread(target=run_async_response, daemon=True)
        thread.start()

    def _send_sync_message(self, message: str, history: list = None) -> str:
        """Send message using synchronous requests to avoid event loop issues"""
        try:
            import requests

            # Use Ollama API directly with requests
            url = "http://localhost:1500/api/generate"

            # Build prompt with history
            prompt = message
            if history:
                context = "\n".join([f"User: {h.get('user', '')}\nAssistant: {h.get('assistant', '')}"
                                   for h in history[-5:]])  # Last 5 exchanges
                prompt = f"Context:\n{context}\n\nUser: {message}\nAssistant:"

            payload = {
                "model": "llama3.2:1b",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 500
                }
            }

            response = requests.post(url, json=payload, timeout=30)
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "No response from Ollama")
            else:
                return f"❌ Ollama error ({response.status_code}): {response.text[:100]}..."

        except ImportError:
            return "❌ requests library not available. Please install: pip install requests"
        except Exception as e:
            return f"❌ Service error: {str(e)}"

    def _display_ai_response(self, typing_widget: Gtk.Widget, response: str):
        """Display AI response in UI (called from main thread)"""
        # Remove typing indicator
        self.messages_box.remove(typing_widget)

        # Add AI message
        ai_message = {
            "role": "assistant",
            "content": response,
            "timestamp": GLib.DateTime.new_now_local().format("%H:%M")
        }
        self.messages.append(ai_message)

        # Create AI message widget
        ai_widget = MobileChatMessage(
            message=response,
            is_user=False,
            timestamp=ai_message["timestamp"]
        )
        self.messages_box.append(ai_widget)

        # Scroll to bottom
        self._scroll_to_bottom()

        # Save history
        self._save_chat_history()

    def _simulate_ai_response(self, typing_widget: Gtk.Widget, user_message: str) -> bool:
        """Simulate AI response (replace with actual AI integration)"""
        # Remove typing indicator
        self.messages_box.remove(typing_widget)
        
        # Generate response based on user message
        if "hello" in user_message.lower():
            response = "Hello! I'm your AI assistant. How can I help you today?"
        elif "chat" in user_message.lower():
            response = "This is the mobile-first chat interface! It's optimized for touch interaction and responsive design."
        elif "mobile" in user_message.lower():
            response = "Yes! This interface is designed mobile-first with responsive components that adapt to different screen sizes."
        else:
            response = f"I understand you said: '{user_message}'. This is a demo response from the mobile chat interface!"
        
        # Add AI message
        ai_message = {
            "role": "assistant",
            "content": response,
            "timestamp": GLib.DateTime.new_now_local().format("%H:%M")
        }
        self.messages.append(ai_message)
        
        # Create AI message widget
        ai_widget = MobileChatMessage(
            message=response,
            is_user=False,
            timestamp=ai_message["timestamp"]
        )
        self.messages_box.append(ai_widget)
        
        # Scroll to bottom
        self._scroll_to_bottom()
        
        # Save history
        self._save_chat_history()
        
        return False  # Don't repeat
    
    def _scroll_to_bottom(self):
        """Scroll messages to bottom"""
        # Get the scrolled window
        scrolled = self.messages_box.get_parent()
        if scrolled and isinstance(scrolled, Gtk.ScrolledWindow):
            vadj = scrolled.get_vadjustment()
            vadj.set_value(vadj.get_upper() - vadj.get_page_size())

    def _on_voice_input(self):
        """Handle voice input request"""
        if not SPEECH_CLIENT_AVAILABLE or not self.speech_client:
            self._show_voice_error("Speech-to-text service not available")
            return

        # Change mic button to indicate recording
        self.chat_input.mic_button.set_label("🔴")
        self.chat_input.mic_button.set_tooltip_text("Recording... Click to stop")
        self.chat_input.mic_button.set_sensitive(False)
        self.chat_input.mic_button.add_css_class("recording")

        # Start speech recognition in background thread
        def run_speech_recognition():
            try:
                print("🎤 Starting speech recognition...")

                # Use speech client to get transcription
                transcription = self._get_speech_transcription()

                # Update UI in main thread
                GLib.idle_add(self._on_speech_result, transcription)

            except Exception as e:
                error_msg = f"Speech recognition error: {str(e)}"
                print(f"❌ {error_msg}")
                GLib.idle_add(self._on_speech_error, error_msg)

        # Run in background thread
        import threading
        thread = threading.Thread(target=run_speech_recognition, daemon=True)
        thread.start()

    def _get_speech_transcription(self) -> str:
        """Get speech transcription using the local speech client"""
        if not self.speech_client:
            raise Exception("Speech client not available")

        # Start recording
        self.speech_client.start_recording()

        # Record for a few seconds (in real implementation, this would be user-controlled)
        import time
        time.sleep(3)  # Record for 3 seconds

        # Stop recording and get transcription
        transcription = self.speech_client.stop_recording()

        if not transcription or transcription.strip() == "":
            raise Exception("No speech detected")

        return transcription.strip()

    def _on_speech_result(self, transcription: str):
        """Handle successful speech transcription"""
        # Reset mic button
        self.chat_input.mic_button.set_label("🎤")
        self.chat_input.mic_button.set_tooltip_text("Voice input (speech-to-text)")
        self.chat_input.mic_button.set_sensitive(True)
        self.chat_input.mic_button.remove_css_class("recording")

        if transcription and transcription.strip():
            # Add transcribed text to input
            current_text = self.chat_input.get_text()
            if current_text and not current_text.endswith(" "):
                transcription = " " + transcription

            self.chat_input.text_view.get_buffer().set_text(current_text + transcription)
            print(f"🎤 Speech transcribed: {transcription}")
        else:
            self._show_voice_error("No speech detected")

    def _on_speech_error(self, error_msg: str):
        """Handle speech recognition error"""
        # Reset mic button
        self.chat_input.mic_button.set_label("🎤")
        self.chat_input.mic_button.set_tooltip_text("Voice input (speech-to-text)")
        self.chat_input.mic_button.set_sensitive(True)
        self.chat_input.mic_button.remove_css_class("recording")

        self._show_voice_error(error_msg)

    def _show_voice_error(self, message: str):
        """Show voice input error message"""
        print(f"🎤 Voice input error: {message}")
        # Could show a toast notification here in the future

    def _load_chat_history(self):
        """Load chat history from file"""
        try:
            if self.chat_history_file.exists():
                with open(self.chat_history_file, 'r') as f:
                    self.messages = json.load(f)
                print(f"📱 Loaded {len(self.messages)} messages from history")
        except Exception as e:
            print(f"⚠️ Failed to load chat history: {e}")
            self.messages = []
    
    def _save_chat_history(self):
        """Save chat history to file"""
        try:
            with open(self.chat_history_file, 'w') as f:
                json.dump(self.messages, f, indent=2)
        except Exception as e:
            print(f"⚠️ Failed to save chat history: {e}")
    
    def get_tool_actions(self) -> List[Gtk.Widget]:
        """Get tool-specific actions for header bar"""
        actions = []
        
        # Clear chat button
        clear_button = Gtk.Button()
        clear_button.set_icon_name("edit-clear-symbolic")
        clear_button.set_tooltip_text("Clear chat history")
        clear_button.connect("clicked", self._on_clear_chat)
        actions.append(clear_button)
        
        return actions
    
    def _on_clear_chat(self, button):
        """Clear chat history"""
        self.messages.clear()
        
        # Clear messages from UI
        child = self.messages_box.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self.messages_box.remove(child)
            child = next_child
        
        # Save empty history
        self._save_chat_history()
        
        print("📱 Chat history cleared")
