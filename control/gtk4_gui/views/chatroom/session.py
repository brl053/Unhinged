"""
@llm-doc Chatroom Session Management
@llm-version 1.0.0
@llm-date 2025-11-15

Session creation and lifecycle management.
"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages chatroom session lifecycle."""

    def __init__(self, chatroom_view):
        """Initialize session manager."""
        self.chatroom_view = chatroom_view

    def create_new_session(self):
        """Create a new chat session."""
        try:
            timestamp = self._get_timestamp()
            session_name = f"Chat Session {timestamp}"

            if hasattr(self.chatroom_view.app, "session_logger") and self.chatroom_view.app.session_logger:
                self.chatroom_view.app.session_logger.log_gui_event(
                    "SESSION_CREATE_REQUESTED",
                    f"Creating session: {session_name}",
                )

            self._create_session_grpc(session_name)

        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            self._on_session_creation_failed(str(e))

    def _create_session_grpc(self, session_name):
        """Create session via gRPC (framework-only)."""
        try:
            from libs.services.chat_service import ChatService

            service = ChatService()
            session_id = service.create_session(session_name)

            if session_id:
                self._on_session_created(session_id)
            else:
                self._on_session_creation_failed("Failed to create session via gRPC")

        except ImportError:
            logger.warning("ChatService not available - session creation disabled")
            self._on_session_creation_failed("Chat service not available")
        except Exception as e:
            logger.error(f"gRPC session creation failed: {e}")
            self._on_session_creation_failed(str(e))

    @staticmethod
    def _get_timestamp():
        """Get formatted timestamp."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _on_session_created(self, session_id):
        """Handle successful session creation."""
        self.chatroom_view._current_session_id = session_id
        self.chatroom_view._session_status = "active"

        logger.info(f"✅ Session created: {session_id}")

        if hasattr(self.chatroom_view.app, "session_logger") and self.chatroom_view.app.session_logger:
            self.chatroom_view.app.session_logger.log_gui_event(
                "SESSION_CREATED",
                f"Session ID: {session_id}",
            )

        if hasattr(self.chatroom_view.app, "show_toast"):
            self.chatroom_view.app.show_toast(f"✅ Session created: {session_id[:8]}...")

        # Update UI
        if self.chatroom_view._chatroom_send_button:
            self.chatroom_view._chatroom_send_button.set_sensitive(True)

        if self.chatroom_view._recording_status_label:
            self.chatroom_view._recording_status_label.set_text(f"Session: {session_id[:8]}...")

    def _on_session_creation_failed(self, error_message):
        """Handle session creation failure."""
        self.chatroom_view._session_status = "no_session"
        self.chatroom_view._current_session_id = None

        logger.error(f"❌ Session creation failed: {error_message}")

        if hasattr(self.chatroom_view.app, "session_logger") and self.chatroom_view.app.session_logger:
            self.chatroom_view.app.session_logger.log_gui_event(
                "SESSION_CREATION_FAILED",
                f"Error: {error_message}",
            )

        if hasattr(self.chatroom_view.app, "show_toast"):
            self.chatroom_view.app.show_toast(f"❌ Session creation failed: {error_message}")

        # Update UI
        if self.chatroom_view._chatroom_send_button:
            self.chatroom_view._chatroom_send_button.set_sensitive(False)

        if self.chatroom_view._recording_status_label:
            self.chatroom_view._recording_status_label.set_text("No active session")

