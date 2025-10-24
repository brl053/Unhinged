"""
💬 Chat Tool - Main Tool Class

Implements the persistent chat experience as a plugin tool for the Control Center.
Provides a native interface for conversing with the LLM operating system.
"""

import gi
gi.require_version('Gtk', '4.0')

from gi.repository import Gtk, GLib
from pathlib import Path

from ...core.tool_manager import BaseTool


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
        self.chat_container = None
        self.text_input = None
        self.mic_button = None
        
        print("💬 Chat tool initialized")
    
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
        
        print("💬 Chat widget created")
        return self.main_container
    
    def _create_centered_input_interface(self):
        """Create the initial centered input interface"""
        # Center container for initial state
        center_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        center_box.set_valign(Gtk.Align.CENTER)
        center_box.set_halign(Gtk.Align.CENTER)
        center_box.set_margin_start(48)
        center_box.set_margin_end(48)
        center_box.set_margin_top(48)
        center_box.set_margin_bottom(48)
        
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
        
        # Input container with text area and microphone
        self.input_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.input_container.set_halign(Gtk.Align.CENTER)
        self.input_container.set_size_request(600, -1)
        
        # Multi-line text input
        self.text_input = Gtk.TextView()
        self.text_input.set_wrap_mode(Gtk.WrapMode.WORD)
        self.text_input.set_size_request(500, 120)
        self.text_input.add_css_class("chat-input")
        
        # Text buffer for placeholder text
        buffer = self.text_input.get_buffer()
        buffer.set_text("Type your message or click the microphone to speak...")
        
        # Scroll container for text input
        scroll_container = Gtk.ScrolledWindow()
        scroll_container.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll_container.set_child(self.text_input)
        scroll_container.add_css_class("chat-input-scroll")
        
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
        submit_button = Gtk.Button(label="Send Message")
        submit_button.add_css_class("chat-submit-button")
        submit_button.set_halign(Gtk.Align.CENTER)
        submit_button.connect("clicked", self._on_submit_clicked)
        center_box.append(submit_button)
        
        # Add center box to main container
        self.main_container.append(center_box)
    
    def _on_mic_clicked(self, button):
        """Handle microphone button click"""
        print("🎤 Microphone clicked - speech recording not yet implemented")
        # TODO: Implement speech-to-text integration
        
        # For now, show a placeholder message
        buffer = self.text_input.get_buffer()
        buffer.set_text("Speech recording will be implemented in the next phase...")
    
    def _on_submit_clicked(self, button):
        """Handle submit button click"""
        buffer = self.text_input.get_buffer()
        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()
        text = buffer.get_text(start_iter, end_iter, False).strip()
        
        if not text or text == "Type your message or click the microphone to speak...":
            print("💬 No message to send")
            return
        
        print(f"💬 Message submitted: {text[:50]}...")
        
        # TODO: Implement chat message flow and LLM integration
        # For now, just clear the input and show a placeholder response
        buffer.set_text("")
        
        # Show placeholder response
        GLib.timeout_add(1000, self._show_placeholder_response, text)
    
    def _show_placeholder_response(self, user_message):
        """Show a placeholder response (temporary)"""
        print(f"🤖 Placeholder response to: {user_message[:30]}...")
        
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
        print("💬 Chat tool activated")
        
        # Focus the text input when activated
        if self.text_input:
            self.text_input.grab_focus()
    
    def on_deactivate(self):
        """Called when the tool becomes inactive"""
        super().on_deactivate()
        print("💬 Chat tool deactivated")
    
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
        print("🗑️ Clear chat clicked")
        if self.text_input:
            buffer = self.text_input.get_buffer()
            buffer.set_text("Type your message or click the microphone to speak...")
    
    def _on_save_chat(self, button):
        """Save the current chat"""
        print("💾 Save chat clicked")
        # TODO: Implement chat persistence
