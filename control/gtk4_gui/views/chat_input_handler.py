from __future__ import annotations

from typing import TYPE_CHECKING

from gi.repository import GLib

if TYPE_CHECKING:  # pragma: no cover - type checking only
    from .chatroom_view import ChatroomView




class ChatInputHandler:
    """Handle text input, send button, and focus events for ChatroomView."""

    def __init__(self, view: ChatroomView) -> None:
        self.view = view

    def on_chatroom_content_changed(self, text_editor, content):
        """Handle content changes in chatroom text editor"""
        try:
            # Enable/disable send button based on content AND session state
            has_content = content and content.strip()
            has_session = self.view._session_status == "active"
            self.view._chatroom_send_button.set_sensitive(has_content and has_session)

            # Reset typing timer
            if self.view._typing_timer_id:
                GLib.source_remove(self.view._typing_timer_id)
                self.view._typing_timer_id = None

            # Set new timer if there's content
            if has_content:
                self.view._typing_timer_id = GLib.timeout_add_seconds(3, self.on_typing_timeout)

        except Exception as e:
            print(f"❌ Chatroom content change error: {e}")

    def on_typing_timeout(self):
        """Handle typing timeout"""
        self.view._typing_timer_id = None
        return False  # Don't repeat

    def on_chatroom_focus_gained(self, text_editor):
        """Handle focus gained in chatroom"""
        try:
            if hasattr(self.view.app, "session_logger") and self.view.app.session_logger:
                self.view.app.session_logger.log_gui_event("CHATROOM_FOCUS_GAINED", "User focused on chatroom input")
        except Exception as e:
            print(f"❌ Chatroom focus gained error: {e}")

    def on_chatroom_focus_lost(self, text_editor):
        """Handle focus lost in chatroom"""
        try:
            if hasattr(self.view.app, "session_logger") and self.view.app.session_logger:
                self.view.app.session_logger.log_gui_event("CHATROOM_FOCUS_LOST", "User left chatroom input")
        except Exception as e:
            print(f"❌ Chatroom focus lost error: {e}")
