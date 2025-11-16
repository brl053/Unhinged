"""
ChatroomView - OS Chatroom tab extracted from desktop_app.py

This module contains all the chatroom functionality that was previously
embedded in the monolithic desktop_app.py file.
"""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

# Import component library - FRAMEWORK ONLY
from components import FormInput
from gi.repository import Gtk

# Chatroom handlers
from .handlers.image_handler import ChatImageHandler
from .handlers.input_handler import ChatInputHandler
from .handlers.message_display import ChatMessageDisplay
from .handlers.voice_handler import ChatVoiceHandler
from .llm import LLMInteraction
from .session import SessionManager

# Framework availability - NO FALLBACK
COMPONENTS_AVAILABLE = True

# Import architecture components - FRAMEWORK ONLY

# Import voice visualizer separately
try:
    from components import voice_visualizer  # noqa: F401

    VOICE_VISUALIZER_AVAILABLE = True
except ImportError as e:
    print(f"Voice visualizer not available: {e}")
    VOICE_VISUALIZER_AVAILABLE = False


class ChatroomView:
    """Handles the OS Chatroom tab functionality"""

    def __init__(self, parent_app):
        """Initialize with reference to parent app for now"""
        self.app = parent_app

        # UI references
        self._chatroom_input_row = None
        self._chatroom_voice_button = None
        self._chatroom_send_button = None
        self._chat_input = None
        self._messages_container = None

        # State
        self._typing_timer_id = None

        # Voice recording state
        self._is_recording = False
        self._recording_timer_id = None
        self._recording_start_time = None

        # Voice visualization and status
        self._voice_visualizer = None

        # Handlers
        self.message_display = ChatMessageDisplay(self)
        self.input_handler = ChatInputHandler(self)
        self.voice_handler = ChatVoiceHandler(self)
        self.image_handler = ChatImageHandler(self)
        self.session_manager = SessionManager(self)
        self.llm_interaction = LLMInteraction(self)

        self._recording_status_label = None

        # Session management state
        self._current_session_id = None
        self._session_status = "no_session"

    def create_content(self):
        """Create the OS Chatroom tab content with design system layout utilities."""
        # Create main chat container using design system layout patterns
        chatroom_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        chatroom_container.set_vexpand(True)
        chatroom_container.set_hexpand(True)

        # Apply design system styling
        chatroom_container.add_css_class("ds-chatroom-container")

        # Chat messages area (expandable, will contain chat history)
        # Using design system spacing: sp_4 (16px) for major component margins
        messages_area = Gtk.ScrolledWindow()
        messages_area.set_vexpand(True)
        messages_area.set_hexpand(True)
        messages_area.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        # Messages container with design system padding
        messages_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)  # sp_2 (8px) for element spacing
        messages_container.set_margin_top(16)  # sp_4 - major component margins
        messages_container.set_margin_bottom(16)  # sp_4 - major component margins
        messages_container.set_margin_start(16)  # sp_4 - major component margins
        messages_container.set_margin_end(16)  # sp_4 - major component margins

        messages_area.set_child(messages_container)
        chatroom_container.append(messages_area)

        # Store reference for adding messages
        self._messages_container = messages_container

        # Input area container (fixed at bottom, will contain text editor)
        # Using design system spacing: sp_6 (24px) for section breaks
        input_area = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        input_area.set_margin_top(24)  # sp_6 - section breaks, modal internal spacing
        input_area.set_margin_bottom(16)  # sp_4 - major component margins
        input_area.set_margin_start(16)  # sp_4 - major component margins
        input_area.set_margin_end(16)  # sp_4 - major component margins

        # Create FormInput with voice support (replaces TextEditor + custom voice controls)
        if COMPONENTS_AVAILABLE:
            # Create FormInput with voice-enabled textarea
            # Pass audio_handler if available for actual voice recording
            audio_handler = self.app.audio_handler if hasattr(self.app, "audio_handler") else None
            form_input = FormInput(
                input_type="textarea",
                name="chatroom_message",
                placeholder="Type or speak your message...",
                enable_voice=True,
                voice_mode="append",
                show_visualizer=True,
                visualizer_width=250,
                rows=4,
                audio_handler=audio_handler,
            )

            # Get the widget and apply design system margins
            form_input_widget = form_input.get_widget()
            form_input_widget.set_margin_top(8)  # sp_2 - form field padding
            form_input_widget.set_margin_bottom(8)  # sp_2 - form field padding
            form_input_widget.set_margin_start(8)  # sp_2 - form field padding
            form_input_widget.set_margin_end(8)  # sp_2 - form field padding
            form_input_widget.set_hexpand(True)
            form_input_widget.set_vexpand(True)

            # Connect FormInput events
            form_input.connect("value-changed", self._on_chatroom_content_changed)
            form_input.connect("recording-started", self._on_voice_recording_started)
            form_input.connect("recording-stopped", self._on_voice_recording_stopped)
            form_input.connect("transcription-completed", self._on_voice_transcription_completed)

            # Store references
            self._chat_input = form_input
            self._voice_visualizer = form_input._voice_visualizer
            self._recording_status_label = form_input._recording_timer_label
            self._chatroom_voice_button = form_input._voice_button if hasattr(form_input, "_voice_button") else None
            self._chatroom_input_row = form_input_widget

            # Connect visualizer to audio handler for real-time feedback
            if self._voice_visualizer and hasattr(self.app, "audio_handler") and self.app.audio_handler:
                self.app.audio_handler.set_voice_visualizer(self._voice_visualizer)

            input_area.append(form_input_widget)
        else:
            # Fallback to basic TextView
            text_editor_widget = Gtk.TextView()
            text_editor_widget.set_wrap_mode(Gtk.WrapMode.WORD)
            self._chat_input = text_editor_widget
            input_area.append(text_editor_widget)

        # Create Send button (below input)
        send_button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        send_button_box.set_halign(Gtk.Align.END)

        self._chatroom_send_button = Gtk.Button(label="Send")
        self._chatroom_send_button.add_css_class("suggested-action")
        self._chatroom_send_button.set_sensitive(False)  # Initially disabled

        # Connect send button handler
        self._chatroom_send_button.connect("clicked", self._on_chatroom_send_clicked)
        send_button_box.append(self._chatroom_send_button)

        input_area.append(send_button_box)

        # Add input area to main container
        # NOTE: Session management is now handled in Status tab only
        chatroom_container.append(input_area)

        return chatroom_container

    def _create_new_session(self):
        """Delegate to SessionManager."""
        self.session_manager.create_new_session()

    def _get_timestamp(self):
        """Get current timestamp for session naming"""
        return self.session_manager._get_timestamp()

    def _on_session_created(self, session_id):
        """Handle successful session creation"""
        try:
            self._current_session_id = session_id
            self._session_status = "active"

            # Update session logger with persisted chat session ID
            # This replaces the random desktop app UUID with the real persisted session ID
            if hasattr(self.app, "session_logger") and self.app.session_logger:
                self.app.session_logger.update_session_id(session_id)

            # Update session ID display in Status tab
            if hasattr(self.app, "status_view") and self.app.status_view:
                self.app.status_view.update_session_id(session_id)

            # Log session creation
            if hasattr(self.app, "session_logger") and self.app.session_logger:
                self.app.session_logger.log_gui_event("CHAT_SESSION_CREATED", f"Created chat session: {session_id}")

            # Show success toast
            if hasattr(self.app, "show_toast"):
                self.app.show_toast(f"Session {session_id[:8]} created successfully")

        except Exception as e:
            print(f"❌ Session created callback error: {e}")

    def _on_session_creation_failed(self, error_message):
        """Handle failed session creation"""
        try:
            self._session_status = "no_session"

            # Log session creation failure
            if hasattr(self.app, "session_logger") and self.app.session_logger:
                self.app.session_logger.log_gui_event(
                    "CHAT_SESSION_FAILED", f"Session creation failed: {error_message}"
                )

            # Show error toast
            if hasattr(self.app, "show_toast"):
                self.app.show_toast(f"Session creation failed: {error_message}")

        except Exception as e:
            print(f"❌ Session creation failed callback error: {e}")

    def _on_chatroom_content_changed(self, text_editor, content):
        """Delegate to input_handler"""
        return self.input_handler.on_chatroom_content_changed(text_editor, content)

    def _on_typing_timeout(self):
        """Delegate to input_handler"""
        return self.input_handler.on_typing_timeout()

    def _on_chatroom_focus_gained(self, text_editor):
        """Delegate to input_handler"""
        return self.input_handler.on_chatroom_focus_gained(text_editor)

    def _on_chatroom_focus_lost(self, text_editor):
        """Delegate to input_handler"""
        return self.input_handler.on_chatroom_focus_lost(text_editor)

    def _on_voice_recording_started(self, form_input):
        """Delegate to voice_handler"""
        return self.voice_handler.on_voice_recording_started(form_input)

    def _on_voice_recording_stopped(self, form_input):
        """Delegate to voice_handler"""
        return self.voice_handler.on_voice_recording_stopped(form_input)

    def _on_voice_transcription_completed(self, form_input, transcript):
        """Delegate to voice_handler"""
        return self.voice_handler.on_voice_transcription_completed(form_input, transcript)

    def _on_chatroom_voice_toggle(self, button):
        """Delegate to voice_handler"""
        return self.voice_handler.on_chatroom_voice_toggle(button)

    def _start_toggle_recording(self):
        """Delegate to voice_handler"""
        return self.voice_handler.start_toggle_recording()

    def _stop_toggle_recording(self):
        """Delegate to voice_handler"""
        return self.voice_handler.stop_toggle_recording()

    def _start_recording_timer(self):
        """Delegate to voice_handler"""
        return self.voice_handler.start_recording_timer()

    def _stop_recording_timer(self):
        """Delegate to voice_handler"""
        return self.voice_handler.stop_recording_timer()

    def _on_chatroom_send_clicked(self, button):
        """Handle send button click in chatroom"""
        try:
            # Get message content
            if COMPONENTS_AVAILABLE and isinstance(self._chat_input, FormInput):
                message = self._chat_input.get_value()
            elif COMPONENTS_AVAILABLE and hasattr(self._chat_input, "get_content"):
                message = self._chat_input.get_content()
            else:
                # Fallback for basic TextView
                buffer = self._chat_input.get_buffer()
                start_iter = buffer.get_start_iter()
                end_iter = buffer.get_end_iter()
                message = buffer.get_text(start_iter, end_iter, False)

            if not message or not message.strip():
                return

            # Check for slash commands
            message_stripped = message.strip()
            if message_stripped.startswith("/image "):
                # Handle /image command for GPU-accelerated image generation
                # NOTE: When FormInput gains an 'image' input type, this command will be renamed
                # to avoid naming collision. Current plan: /generate-image or /img
                prompt = message_stripped[7:].strip()  # Remove "/image " prefix
                self.image_handler.handle_slash_image_command(prompt)

                # Clear input
                if COMPONENTS_AVAILABLE and isinstance(self._chat_input, FormInput):
                    self._chat_input.set_value("")
                elif COMPONENTS_AVAILABLE and hasattr(self._chat_input, "clear_content"):
                    self._chat_input.clear_content()
                else:
                    buffer = self._chat_input.get_buffer()
                    buffer.set_text("")

                # Focus input field for next command
                if hasattr(self._chat_input, "grab_focus"):
                    self._chat_input.grab_focus()

                # Disable send button
                self._chatroom_send_button.set_sensitive(False)
                return

            # Add user message to chat with session context
            self._add_chat_message("You", message_stripped, "user")

            # Clear input
            if COMPONENTS_AVAILABLE and isinstance(self._chat_input, FormInput):
                self._chat_input.set_value("")
            elif COMPONENTS_AVAILABLE and hasattr(self._chat_input, "clear_content"):
                self._chat_input.clear_content()
            else:
                buffer = self._chat_input.get_buffer()
                buffer.set_text("")

            # Focus input field for next message
            if hasattr(self._chat_input, "grab_focus"):
                self._chat_input.grab_focus()

            # Disable send button
            self._chatroom_send_button.set_sensitive(False)

            # Send to LLM with session context
            self._send_to_llm_with_session(message_stripped)

        except Exception as e:
            print(f"❌ Chatroom send error: {e}")
            # Re-enable send button so user can retry
            self._chatroom_send_button.set_sensitive(True)
            if hasattr(self.app, "show_toast"):
                self.app.show_toast(f"Send failed: {e}")

    def _add_chat_message(self, sender, message, message_type="user"):
        """Delegate to message_display handler"""
        return self.message_display.add_chat_message(sender, message, message_type)

    def _scroll_to_bottom(self):
        """Delegate to message_display handler"""
        return self.message_display.scroll_to_bottom()

    def _clear_message_container(self):
        """Delegate to message_display handler"""
        return self.message_display.clear_message_container()

    def _display_generated_image(self, thinking_box, result, prompt):
        """Display generated image in chat using GeneratedArtifactWidget"""
        try:
            # Remove thinking indicator
            if thinking_box and thinking_box.get_parent():
                self._messages_container.remove(thinking_box)

            # Import the widget
            from ..components import GeneratedArtifactWidget

            # Create artifact widget
            image_path = result.get("image_path", "")
            generation_time = result.get("generation_time", 0)

            artifact_widget = GeneratedArtifactWidget(
                artifact_type="image",
                artifact_path=image_path,
                artifact_title=f"Generated Image ({generation_time:.1f}s)",
                artifact_metadata={
                    "prompt": prompt,
                    "generation_time": generation_time,
                    "model": result.get("model", "unknown"),
                    "device": result.get("device", "unknown"),
                    "steps": result.get("num_inference_steps", 20),
                },
            )

            # Add widget to chat
            if self._messages_container:
                self._messages_container.append(artifact_widget.get_widget())
                self._scroll_to_bottom()

            # Log generation
            if hasattr(self.app, "session_logger") and self.app.session_logger:
                self.app.session_logger.log_gui_event(
                    "IMAGE_GENERATED",
                    f"Prompt: {prompt[:50]}... | Time: {generation_time:.1f}s | Path: {image_path}",
                )

            # Show toast
            if hasattr(self.app, "show_toast"):
                self.app.show_toast(f"✅ Image generated in {generation_time:.1f}s")

        except Exception as e:
            print(f"❌ Display generated image error: {e}")
            self._add_error_message(f"Failed to display image: {e}")

    def _send_to_llm_with_session(self, message):
        """Delegate to LLMInteraction."""
        self.llm_interaction.send_to_llm_with_session(message)

    def _detect_image_generation_request(self, message_text):
        """Delegate to LLMInteraction."""
        return self.llm_interaction._detect_image_generation_request(message_text)

    def _handle_image_generation_request(self, image_request, original_message):
        """Delegate to LLMInteraction."""
        self.llm_interaction._handle_image_generation_request(image_request, original_message)

    def _image_generation_with_framework(self, image_request, thinking_box, original_message):
        """Delegate to LLMInteraction."""
        self.llm_interaction._image_generation_with_framework(image_request, thinking_box, original_message)

    def _add_error_message(self, error_msg):
        """Delegate to message_display handler"""
        return self.message_display.add_error_message(error_msg)

    def _send_text_message_framework(self, message):
        """Delegate to LLMInteraction."""
        self.llm_interaction._send_text_message_framework(message)

    def _add_thinking_indicator(self):
        """Delegate to message_display handler"""
        return self.message_display.add_thinking_indicator()

    def _text_chat_framework_thread(self, message, thinking_box):
        """Delegate to LLMInteraction."""
        self.llm_interaction._text_chat_framework_thread(message, thinking_box)

    def _handle_text_response(self, response, thinking_box):
        """Delegate to LLMInteraction."""
        self.llm_interaction._handle_text_response(response, thinking_box)

    def _handle_text_error(self, error_msg, thinking_box):
        """Delegate to LLMInteraction."""
        self.llm_interaction._handle_text_error(error_msg, thinking_box)

    def _on_tts_button_clicked(self, button, text):
        """Delegate to message_display handler"""
        return self.message_display._on_tts_button_clicked(button, text)

    def _tts_thread(self, text, button):
        """Delegate to message_display handler"""
        return self.message_display._tts_thread(text, button)

    def _update_tts_button(self, button, label):
        """Delegate to message_display handler"""
        return self.message_display._update_tts_button(button, label)

    def add_voice_transcript(self, transcript):
        """Delegate to voice_handler (called from parent app)"""
        return self.voice_handler.add_voice_transcript(transcript)

    def _refresh_ui_after_transcript(self):
        """Delegate to voice_handler"""
        return self.voice_handler.refresh_ui_after_transcript()
