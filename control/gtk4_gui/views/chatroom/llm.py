"""
@llm-doc Chatroom LLM Interaction
@llm-version 1.0.0
@llm-date 2025-11-15

LLM message sending and response handling.
"""

import logging

logger = logging.getLogger(__name__)


class LLMInteraction:
    """Manages LLM interaction and message handling."""

    def __init__(self, chatroom_view):
        """Initialize LLM interaction manager."""
        self.chatroom_view = chatroom_view

    def send_to_llm_with_session(self, message):
        """Send message to LLM with session context."""
        try:
            if hasattr(self.chatroom_view.app, "session_logger") and self.chatroom_view.app.session_logger:
                self.chatroom_view.app.session_logger.log_gui_event(
                    "CHAT_MESSAGE_SENT",
                    f"Session {self.chatroom_view._current_session_id}: {message[:50]}...",
                )

            if self.chatroom_view._current_session_id:
                image_request = self._detect_image_generation_request(message)
                if image_request:
                    self._handle_image_generation_request(image_request, message)
                else:
                    self._send_text_message_framework(message)
            else:
                logger.warning("Attempting to send message without active session")
                if hasattr(self.chatroom_view.app, "show_toast"):
                    self.chatroom_view.app.show_toast("No active session - please create a session first")

        except Exception as e:
            logger.error(f"Send message with session error: {e}")

    @staticmethod
    def _detect_image_generation_request(message_text):
        """Detect image generation requests."""
        return None

    def _handle_image_generation_request(self, image_request, original_message):
        """Handle image generation request."""
        try:
            thinking_box = self.chatroom_view._add_thinking_indicator()
            self._image_generation_with_framework(image_request, thinking_box, original_message)
        except Exception as e:
            logger.error(f"Image generation request error: {e}")

    def _image_generation_with_framework(self, image_request, thinking_box, original_message):
        """Generate image using framework."""
        try:
            from libs.services.image_generation_service import ImageGenerationService

            service = ImageGenerationService()
            result = service.generate_image(image_request)

            if result:
                self.chatroom_view._display_generated_image(thinking_box, result, image_request)
            else:
                self.chatroom_view._add_error_message("Image generation failed")

        except ImportError:
            logger.warning("ImageGenerationService not available")
            self.chatroom_view._add_error_message("Image generation service not available")
        except Exception as e:
            logger.error(f"Image generation error: {e}")
            self.chatroom_view._add_error_message(f"Image generation failed: {e}")

    def _send_text_message_framework(self, message):
        """Send text message using framework."""
        try:
            self.chatroom_view._add_chat_message("You", message, "user")

            thinking_box = self.chatroom_view._add_thinking_indicator()

            import threading

            thread = threading.Thread(
                target=self._text_chat_framework_thread,
                args=(message, thinking_box),
                daemon=True,
            )
            thread.start()

        except Exception as e:
            logger.error(f"Send text message error: {e}")
            self.chatroom_view._add_error_message(f"Failed to send message: {e}")

    def _text_chat_framework_thread(self, message, thinking_box):
        """Handle text chat in background thread."""
        try:
            from libs.services.chat_service import ChatService

            service = ChatService()
            response = service.send_message(
                self.chatroom_view._current_session_id,
                message,
            )

            if response:
                self._handle_text_response(response, thinking_box)
            else:
                self._handle_text_error("No response from service", thinking_box)

        except ImportError:
            logger.warning("ChatService not available")
            self._handle_text_error("Chat service not available", thinking_box)
        except Exception as e:
            logger.error(f"Text chat error: {e}")
            self._handle_text_error(str(e), thinking_box)

    def _handle_text_response(self, response, thinking_box):
        """Handle text response from LLM."""
        try:
            if thinking_box and thinking_box.get_parent():
                self.chatroom_view._messages_container.remove(thinking_box)

            response_text = response.get("text", "")
            if response_text:
                self.chatroom_view._add_chat_message("Assistant", response_text, "assistant")
                self.chatroom_view._scroll_to_bottom()

        except Exception as e:
            logger.error(f"Handle text response error: {e}")

    def _handle_text_error(self, error_msg, thinking_box):
        """Handle text error."""
        try:
            if thinking_box and thinking_box.get_parent():
                self.chatroom_view._messages_container.remove(thinking_box)

            self.chatroom_view._add_error_message(error_msg)

        except Exception as e:
            logger.error(f"Handle text error: {e}")

