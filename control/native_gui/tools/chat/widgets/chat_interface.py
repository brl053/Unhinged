"""
💬 Chat Interface Widget

Main chat interface widget for displaying conversation bubbles and managing
the chat flow. This will be implemented in Phase 2 with animations.

Features (to be implemented):
- Conversation bubble display
- Smooth scrolling
- Message history management
- Loading states for LLM responses
"""

import gi
gi.require_version('Gtk', '4.0')

from gi.repository import Gtk, GLib


class ChatInterface(Gtk.Box):
    """
    Main chat interface widget.
    
    Displays conversation bubbles and manages chat flow.
    Will be implemented in Phase 2 with full animation support.
    """
    
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        
        print("💬 ChatInterface widget created (placeholder)")
        
        # TODO: Implement in Phase 2
        # - Conversation bubble display
        # - Smooth scrolling
        # - Message history
        # - Loading states
