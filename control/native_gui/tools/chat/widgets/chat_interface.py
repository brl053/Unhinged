
# Initialize GUI event logger
gui_logger = create_gui_logger("unhinged-chat-interface", "1.0.0")

"""
@llm-type control-system
@llm-legend chat_interface.py - system control component
@llm-key Core functionality for chat_interface
@llm-map Part of the Unhinged system architecture
@llm-axiom Maintains system independence and architectural compliance
@llm-contract Provides standardized interface for system integration
@llm-token chat_interface: system control component
"""
"""
💬 Chat Interface Widget

Main chat interface widget for displaying conversation bubbles and managing
the chat flow with animations and smooth transitions.

Features:
- Conversation bubble display with user/assistant styling
- Smooth scrolling and auto-scroll to bottom
- Message history management
- Loading states for LLM responses
- Animation system for message transitions
"""

import gi
from unhinged_events import create_gui_logger
gi.require_version('Gtk', '4.0')

from gi.repository import Gtk, GLib, Pango
from typing import List, Dict, Any
import time


class MessageBubble(Gtk.Box):
    """Individual message bubble widget"""

    def __init__(self, message: str, is_user: bool = True, is_loading: bool = False):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)

        self.message = message
        self.is_user = is_user
        self.is_loading = is_loading

        self._create_bubble()

    def _create_bubble(self):
        """Create the message bubble UI"""
        # Container for alignment
        container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)

        # Message bubble
        bubble = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        bubble.set_margin_start(16 if not self.is_user else 64)
        bubble.set_margin_end(64 if not self.is_user else 16)
        bubble.set_margin_top(4)
        bubble.set_margin_bottom(4)

        # Message text
        if self.is_loading:
            text_label = Gtk.Label(label="🤖 Thinking...")
            text_label.add_css_class("chat-loading")
        else:
            text_label = Gtk.Label(label=self.message)
            text_label.set_wrap(True)
            text_label.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
            text_label.set_xalign(0.0)
            text_label.set_selectable(True)

        # Apply styling
        if self.is_user:
            bubble.add_css_class("chat-bubble")
            bubble.add_css_class("user")
            text_label.set_xalign(1.0)
        else:
            bubble.add_css_class("chat-bubble")
            bubble.add_css_class("assistant")
            text_label.set_xalign(0.0)

        if self.is_loading:
            bubble.add_css_class("loading")

        bubble.append(text_label)

        # Add timestamp (optional)
        timestamp = time.strftime("%H:%M")
        time_label = Gtk.Label(label=timestamp)
        time_label.add_css_class("chat-timestamp")
        time_label.set_opacity(0.6)
        time_label.set_xalign(1.0 if self.is_user else 0.0)
        bubble.append(time_label)

        # Alignment
        if self.is_user:
            container.set_halign(Gtk.Align.END)
        else:
            container.set_halign(Gtk.Align.START)

        container.append(bubble)
        self.append(container)

    def update_message(self, new_message: str):
        """Update the message content"""
        self.message = new_message
        # Find and update the text label
        # This is a simplified implementation
        # In a real app, you'd want to rebuild or update the specific widget
        self.remove(self.get_first_child())
        self._create_bubble()


class ChatInterface(Gtk.Box):
    """
    Main chat interface widget.

    Displays conversation bubbles and manages chat flow with animations.
    """

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        self.messages = []  # List of message data
        self.message_widgets = []  # List of MessageBubble widgets

        self._create_interface()

    def _create_interface(self):
        """Create the chat interface UI"""
        # Header
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        header.set_margin_start(16)
        header.set_margin_end(16)
        header.set_margin_top(12)
        header.set_margin_bottom(8)

        title = Gtk.Label(label="💬 Conversation")
        title.add_css_class("chat-conversation-title")
        header.append(title)

        # Clear button
        clear_btn = Gtk.Button(label="🗑️")
        clear_btn.set_tooltip_text("Clear conversation")
        clear_btn.add_css_class("flat")
        clear_btn.connect("clicked", self._on_clear_clicked)
        header.append(clear_btn)

        self.append(header)

        # Scrolled window for messages
        self.scroll_window = Gtk.ScrolledWindow()
        self.scroll_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scroll_window.set_vexpand(True)
        self.scroll_window.add_css_class("chat-history")

        # Messages container
        self.messages_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.messages_container.set_margin_start(8)
        self.messages_container.set_margin_end(8)
        self.messages_container.set_margin_top(8)
        self.messages_container.set_margin_bottom(8)

        self.scroll_window.set_child(self.messages_container)
        self.append(self.scroll_window)

    def add_message(self, message: str, is_user: bool = True, animate: bool = True):
        """Add a new message to the conversation"""
        # Store message data
        message_data = {
            'text': message,
            'is_user': is_user,
            'timestamp': time.time()
        }
        self.messages.append(message_data)

        # Create message bubble
        bubble = MessageBubble(message, is_user)
        self.message_widgets.append(bubble)

        # Add to container
        self.messages_container.append(bubble)

        # Animate if requested
        if animate:
            bubble.add_css_class("chat-animate-in")

        # Auto-scroll to bottom
        GLib.timeout_add(100, self._scroll_to_bottom)


    def add_loading_message(self):
        """Add a loading message bubble"""
        bubble = MessageBubble("", is_user=False, is_loading=True)
        self.message_widgets.append(bubble)
        self.messages_container.append(bubble)

        # Auto-scroll to bottom
        GLib.timeout_add(100, self._scroll_to_bottom)

        return bubble  # Return so it can be updated later

    def update_loading_message(self, loading_bubble: MessageBubble, final_message: str):
        """Update a loading message with the final response"""
        # Remove loading bubble
        self.messages_container.remove(loading_bubble)
        if loading_bubble in self.message_widgets:
            self.message_widgets.remove(loading_bubble)

        # Add final message
        self.add_message(final_message, is_user=False, animate=True)

    def _scroll_to_bottom(self):
        """Scroll to the bottom of the conversation"""
        adjustment = self.scroll_window.get_vadjustment()
        adjustment.set_value(adjustment.get_upper() - adjustment.get_page_size())
        return False  # Don't repeat timeout

    def _on_clear_clicked(self, button):
        """Clear all messages"""
        # Remove all message widgets
        for widget in self.message_widgets:
            self.messages_container.remove(widget)

        # Clear data
        self.messages.clear()
        self.message_widgets.clear()


    def get_message_count(self) -> int:
        """Get the number of messages in the conversation"""
        return len(self.messages)

    def get_messages(self) -> List[Dict[str, Any]]:
        """Get all messages as data"""
        return self.messages.copy()
