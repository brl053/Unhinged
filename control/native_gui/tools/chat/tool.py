
# Initialize GUI event logger
gui_logger = create_gui_logger("unhinged-tool", "1.0.0")

"""
@llm-type control-system
@llm-legend tool.py - system control component
@llm-key Core functionality for tool
@llm-map Part of the Unhinged system architecture
@llm-axiom Maintains system independence and architectural compliance
@llm-contract Provides standardized interface for system integration
@llm-token tool: system control component
"""
"""
💬 Chat Tool - Main Tool Class

Implements the persistent chat experience as a plugin tool for the Control Center.
Provides a native interface for conversing with the LLM operating system.
"""

import gi
from unhinged_events import create_gui_logger
gi.require_version('Gtk', '4.0')

from gi.repository import Gtk, GLib
from pathlib import Path

from ...core.tool_manager import BaseTool
from .bridge.speech_client import SpeechClient
from .widgets.chat_interface import ChatInterface


class ChatTool(BaseTool):
    """
    Chat tool plugin for persistent LLM conversation.
    
    Provides a native chat interface with:
    - Speech-to-text input via microphone
    - Animated chat bubbles for conversation flow
    - Real-time LLM responses
    - Persistent conversation history
    """
    
    def __init__(self):
        super().__init__()
        self.name = "Chat"
        self.icon = "💬"
        self.description = "Chat with OS - Persistent LLM conversation interface"
        self.shortcut = "Ctrl+6"
        
        # Chat state
        self.messages = []  # List of conversation messages
        self.is_waiting_for_response = False
        self.current_conversation_id = None

        # UI components (will be created in create_widget)
        self.main_container = None
        self.input_container = None
        self.chat_interface = None
        self.text_input = None
        self.mic_button = None
        self.submit_button = None

        # UI state
        self.is_conversation_mode = False
        self.centered_container = None

        # Speech integration
        self.speech_client = SpeechClient()
        self.is_recording = False
        
    
    def create_widget(self):
        """Create the chat tool widget"""
        # Main container with vertical layout
        self.main_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.main_container.set_vexpand(True)
        self.main_container.set_hexpand(True)
        
        # Create the initial centered input interface
        self._create_centered_input_interface()
        
        # Apply CSS classes for theming
        self.main_container.add_css_class("chat-tool")
        
        return self.main_container
    
    def _create_centered_input_interface(self):
        """Create the initial centered input interface"""
        # Center container for initial state - wider to accommodate larger input
        center_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        center_box.set_valign(Gtk.Align.CENTER)
        center_box.set_halign(Gtk.Align.CENTER)
        center_box.set_margin_start(24)  # Reduced margins to fit wider input
        center_box.set_margin_end(24)
        center_box.set_margin_top(48)
        center_box.set_margin_bottom(48)
        center_box.set_hexpand(True)  # Allow horizontal expansion
        
        # Title
        title_label = Gtk.Label(label="💬 Chat with OS")
        title_label.add_css_class("chat-title")
        title_label.set_markup("<span size='x-large' weight='bold'>💬 Chat with OS</span>")
        center_box.append(title_label)
        
        # Subtitle
        subtitle_label = Gtk.Label(label="Converse with your operating system using speech or text")
        subtitle_label.add_css_class("chat-subtitle")
        subtitle_label.set_opacity(0.7)
        center_box.append(subtitle_label)
        
        # Input container with text area and microphone - centered and wider
        self.input_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.input_container.set_halign(Gtk.Align.CENTER)
        self.input_container.set_size_request(3000, -1)  # 5x wider container

        # Multi-line text input - 5x wider
        self.text_input = Gtk.TextView()
        self.text_input.set_wrap_mode(Gtk.WrapMode.WORD)
        self.text_input.set_size_request(2500, 120)  # 5x wider text input (500 * 5 = 2500)
        self.text_input.add_css_class("chat-input")

        # Text buffer for placeholder text
        buffer = self.text_input.get_buffer()
        buffer.set_text("Type your message or click the microphone to speak...")

        # Scroll container for text input
        scroll_container = Gtk.ScrolledWindow()
        scroll_container.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll_container.set_child(self.text_input)
        scroll_container.add_css_class("chat-input-scroll")
        scroll_container.set_hexpand(True)  # Allow horizontal expansion

        self.input_container.append(scroll_container)
        
        # Microphone button
        self.mic_button = Gtk.Button()
        self.mic_button.set_label("🎤")
        self.mic_button.set_size_request(60, 60)
        self.mic_button.set_valign(Gtk.Align.START)
        self.mic_button.add_css_class("chat-mic-button")
        self.mic_button.set_tooltip_text("Click to record speech")
        self.mic_button.connect("clicked", self._on_mic_clicked)
        
        self.input_container.append(self.mic_button)
        
        center_box.append(self.input_container)
        
        # Submit button
        self.submit_button = Gtk.Button(label="Send Message")
        self.submit_button.add_css_class("chat-submit-button")
        self.submit_button.set_halign(Gtk.Align.CENTER)
        self.submit_button.connect("clicked", self._on_submit_clicked)
        center_box.append(self.submit_button)

        # Store reference to centered container for animation
        self.centered_container = center_box

        # Add center box to main container
        self.main_container.append(center_box)
    
    def _on_mic_clicked(self, button):
        """Handle microphone button click"""
        if self.is_recording:
            # Stop recording
            self._stop_recording()
        else:
            # Start recording
            self._start_recording()
    
    def _on_submit_clicked(self, button):
        """Handle submit button click - trigger animation to conversation mode"""
        buffer = self.text_input.get_buffer()
        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()
        text = buffer.get_text(start_iter, end_iter, False).strip()

        if not text or text == "Type your message or click the microphone to speak...":
            return


        # Clear input immediately
        buffer.set_text("")

        # Trigger animation to conversation mode
        if not self.is_conversation_mode:
            self._animate_to_conversation_mode(text)
        else:
            # Already in conversation mode, just add message
            self._add_user_message(text)

    def _start_recording(self):
        """Start speech recording"""
        self.is_recording = True

        # Update microphone button appearance
        self.mic_button.set_label("🔴")  # Red circle to indicate recording
        self.mic_button.add_css_class("chat-mic-recording")
        self.mic_button.set_tooltip_text("Click to stop recording")

        # Update text input to show recording status
        buffer = self.text_input.get_buffer()
        buffer.set_text("🎤 Recording... Click microphone to stop")

        # Start recording with speech client
        self.speech_client.start_recording(self._on_transcription_complete)

    def _stop_recording(self):
        """Stop speech recording and transcribe"""
        self.is_recording = False

        # Update microphone button appearance
        self.mic_button.set_label("🎤")
        self.mic_button.remove_css_class("chat-mic-recording")
        self.mic_button.set_tooltip_text("Click to record speech")

        # Show transcription in progress
        buffer = self.text_input.get_buffer()
        buffer.set_text("🔄 Transcribing audio...")

        # Stop recording and get transcription
        GLib.timeout_add(100, self._process_transcription)

    def _process_transcription(self):
        """Process the transcription result"""
        try:
            transcript = self.speech_client.stop_recording()

            # Update text input with transcription
            buffer = self.text_input.get_buffer()
            if transcript and transcript.strip():
                buffer.set_text(transcript.strip())
            else:
                buffer.set_text("No speech detected. Try again.")
                gui_logger.warn(" No transcription result")

        except Exception as e:
            gui_logger.error(f" Transcription error: {e}")
            buffer = self.text_input.get_buffer()
            buffer.set_text("Transcription failed. Please try again.")

        return False  # Don't repeat the timeout

    def _on_transcription_complete(self, transcript: str):
        """Callback for when transcription is complete"""

        # Update UI on main thread
        GLib.idle_add(self._update_transcription_ui, transcript)

    def _update_transcription_ui(self, transcript: str):
        """Update UI with transcription result (called on main thread)"""
        if transcript and transcript.strip():
            buffer = self.text_input.get_buffer()
            buffer.set_text(transcript.strip())
        return False  # Don't repeat
    
    def _show_placeholder_response(self, user_message):
        """Show a placeholder response (temporary)"""
        
        # TODO: Replace with actual chat interface and LLM integration
        buffer = self.text_input.get_buffer()
        if "terry davis" in user_message.lower():
            response = "Terry Davis was a brilliant programmer who created TempleOS..."
        else:
            response = f"I received your message: '{user_message}'. Full chat interface coming soon!"
        
        buffer.set_text(f"Response: {response}")
        return False  # Don't repeat the timeout
    
    def on_activate(self):
        """Called when the tool becomes active"""
        super().on_activate()
        
        # Focus the text input when activated
        if self.text_input:
            self.text_input.grab_focus()
    
    def on_deactivate(self):
        """Called when the tool becomes inactive"""
        super().on_deactivate()
    
    def get_actions(self):
        """Get tool-specific header actions"""
        return [
            {
                'label': '🗑️ Clear',
                'css_class': 'destructive-action',
                'callback': self._on_clear_chat
            },
            {
                'label': '💾 Save',
                'css_class': 'suggested-action', 
                'callback': self._on_save_chat
            }
        ]
    
    def _on_clear_chat(self, button):
        """Clear the current chat"""
        if self.text_input:
            buffer = self.text_input.get_buffer()
            buffer.set_text("Type your message or click the microphone to speak...")
    
    def _on_save_chat(self, button):
        """Save the current chat"""
        # TODO: Implement chat persistence

    def _animate_to_conversation_mode(self, first_message: str):
        """Animate from centered input to conversation mode"""

        # Mark as conversation mode
        self.is_conversation_mode = True

        # Add animation class to centered container
        self.centered_container.add_css_class("chat-animate-out")

        # Create conversation interface
        self.chat_interface = ChatInterface()

        # Create new input area at bottom
        self._create_conversation_input_area()

        # Schedule the transition
        GLib.timeout_add(300, self._complete_conversation_transition, first_message)

    def _complete_conversation_transition(self, first_message: str):
        """Complete the transition to conversation mode"""
        # Remove centered container
        self.main_container.remove(self.centered_container)

        # Add conversation interface
        self.main_container.append(self.chat_interface)

        # Add input area at bottom
        self.main_container.append(self.input_container)

        # Add the first message
        self._add_user_message(first_message)

        gui_logger.info(" Conversation mode activated", {"status": "success"})
        return False  # Don't repeat timeout

    def _create_conversation_input_area(self):
        """Create the input area for conversation mode"""
        # Input area container - centered
        self.input_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.input_container.add_css_class("chat-input-area")
        self.input_container.set_margin_start(16)
        self.input_container.set_margin_end(16)
        self.input_container.set_margin_top(8)
        self.input_container.set_margin_bottom(16)
        self.input_container.set_halign(Gtk.Align.CENTER)  # Center the input area

        # Input row - centered and wider
        input_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        input_row.set_halign(Gtk.Align.CENTER)
        input_row.set_size_request(2600, -1)  # Wide input row

        # Text input (maintain width in conversation mode)
        self.text_input = Gtk.TextView()
        self.text_input.set_wrap_mode(Gtk.WrapMode.WORD)
        self.text_input.set_size_request(2500, 60)  # Keep 5x width, smaller height
        self.text_input.add_css_class("chat-input")

        # Scroll container for text input
        scroll_container = Gtk.ScrolledWindow()
        scroll_container.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll_container.set_child(self.text_input)
        scroll_container.add_css_class("chat-input-scroll")
        scroll_container.set_hexpand(True)

        input_row.append(scroll_container)

        # Microphone button (smaller)
        self.mic_button = Gtk.Button()
        self.mic_button.set_label("🎤")
        self.mic_button.set_size_request(50, 50)  # Smaller
        self.mic_button.add_css_class("chat-mic-button")
        self.mic_button.set_tooltip_text("Click to record speech")
        self.mic_button.connect("clicked", self._on_mic_clicked)

        input_row.append(self.mic_button)

        # Send button (smaller)
        self.submit_button = Gtk.Button(label="Send")
        self.submit_button.add_css_class("chat-submit-button")
        self.submit_button.connect("clicked", self._on_submit_clicked)

        input_row.append(self.submit_button)

        self.input_container.append(input_row)

    def _add_user_message(self, message: str):
        """Add user message and generate LLM response"""
        # Add user message to conversation
        self.chat_interface.add_message(message, is_user=True)

        # Add loading message for LLM response
        loading_bubble = self.chat_interface.add_loading_message()

        # Generate LLM response (placeholder for now)
        GLib.timeout_add(1500, self._generate_llm_response, loading_bubble, message)

    def _generate_llm_response(self, loading_bubble, user_message: str):
        """Generate LLM response (placeholder implementation)"""
        # Placeholder response logic
        if "terry davis" in user_message.lower():
            response = ("Terry Davis was a brilliant programmer who created TempleOS, "
                       "a 64-bit operating system he developed single-handedly. He was known "
                       "for his exceptional programming skills and his unique perspective on "
                       "computing. TempleOS was designed as a modern Commodore 64, featuring "
                       "a custom compiler, graphics system, and even games.")
        elif "templeos" in user_message.lower():
            response = ("TempleOS is a biblical-themed operating system created by Terry Davis. "
                       "It features a 640x480 16-color display, HolyC programming language, "
                       "and was designed to be God's third temple. The OS includes a unique "
                       "flight simulator, 3D graphics capabilities, and a complete development "
                       "environment all written from scratch.")
        else:
            response = f"I understand you're asking about: '{user_message}'. This is a placeholder response. Full LLM integration will be implemented in Phase 2.3."

        # Update loading message with response
        self.chat_interface.update_loading_message(loading_bubble, response)

        return False  # Don't repeat timeout
