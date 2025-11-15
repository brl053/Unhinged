from __future__ import annotations

import time
from typing import TYPE_CHECKING

from gi.repository import GLib

if TYPE_CHECKING:  # pragma: no cover - type checking only
    from .chatroom_view import ChatroomView

# Import components
try:
    from ..components import FormInput

    COMPONENTS_AVAILABLE = True
except ImportError:
    COMPONENTS_AVAILABLE = False


class ChatVoiceHandler:
    """Handle voice recording, transcription, and UI updates for ChatroomView."""

    def __init__(self, view: ChatroomView) -> None:
        self.view = view

    def on_voice_recording_started(self, form_input):
        """Handle voice recording started from FormInput"""
        try:
            if hasattr(self.view.app, "session_logger") and self.view.app.session_logger:
                self.view.app.session_logger.log_gui_event(
                    "CHATROOM_VOICE_RECORDING_STARTED", "Voice recording started"
                )
            self.view.app.show_toast("Recording...")
        except Exception as e:
            print(f"❌ Voice recording started error: {e}")

    def on_voice_recording_stopped(self, form_input):
        """Handle voice recording stopped from FormInput"""
        try:
            if hasattr(self.view.app, "session_logger") and self.view.app.session_logger:
                self.view.app.session_logger.log_gui_event(
                    "CHATROOM_VOICE_RECORDING_STOPPED", "Voice recording stopped"
                )
            self.view.app.show_toast("Processing...")
        except Exception as e:
            print(f"❌ Voice recording stopped error: {e}")

    def on_voice_transcription_completed(self, form_input, transcript):
        """Handle voice transcription completed from FormInput"""
        try:
            if hasattr(self.view.app, "session_logger") and self.view.app.session_logger:
                self.view.app.session_logger.log_gui_event(
                    "CHATROOM_VOICE_TRANSCRIPTION_COMPLETED",
                    f"Transcribed: {transcript[:50]}...",
                )
            self.view.app.show_toast("Transcription complete")
        except Exception as e:
            print(f"❌ Voice transcription completed error: {e}")

    def on_chatroom_voice_toggle(self, button):
        """Handle chatroom voice button toggle - start or stop recording."""
        try:
            if not self.view._is_recording:
                self.start_toggle_recording()
            else:
                self.stop_toggle_recording()

        except Exception as e:
            print(f"❌ Chatroom voice toggle error: {e}")
            if hasattr(self.view.app, "show_toast"):
                self.view.app.show_toast(f"Voice recording failed: {e}")

    def start_toggle_recording(self):
        """Start toggle recording with timer and visual feedback"""
        try:
            # Always start recording state and timer (works with both new and legacy)
            self.view._is_recording = True
            self.view._recording_start_time = time.time()

            # Update button appearance
            self.view._chatroom_voice_button.add_css_class("recording-active")
            if hasattr(self.view._chatroom_voice_button, "set_icon_name"):
                self.view._chatroom_voice_button.set_icon_name("media-playback-stop-symbolic")
            elif hasattr(self.view._chatroom_voice_button, "get_widget"):
                widget = self.view._chatroom_voice_button.get_widget()
                if hasattr(widget, "set_icon_name"):
                    widget.set_icon_name("media-playback-stop-symbolic")

            # Start recording timer (always show timer regardless of backend)
            self.start_recording_timer()

            # Update voice visualizer and status
            if self.view._voice_visualizer:
                self.view._voice_visualizer.set_recording_state(True)

            # Show timer display
            if self.view._recording_status_label:
                self.view._recording_status_label.set_text("00:00")
                self.view._recording_status_label.set_visible(True)
                self.view._recording_status_label.remove_css_class("dim-label")
                self.view._recording_status_label.add_css_class("accent")

            # Show minimal feedback
            self.view.app.show_toast("Recording...")

            # Log event
            if hasattr(self.view.app, "session_logger") and self.view.app.session_logger:
                self.view.app.session_logger.log_gui_event(
                    "CHATROOM_TOGGLE_RECORDING_START",
                    "Started toggle recording in chatroom",
                )

            # Use AudioHandler (always available now)
            if hasattr(self.view.app, "audio_handler") and self.view.app.audio_handler:
                self.view.app.audio_handler.start_recording()
            else:
                print("⚠️ AudioHandler not available")

        except Exception as e:
            print(f"❌ Start toggle recording error: {e}")
            self.view.app.show_toast(f"Recording failed: {e}")
            # Reset state on error
            self.view._is_recording = False
            self.stop_recording_timer()
            # Reset button appearance
            self.view._chatroom_voice_button.remove_css_class("recording-active")
            if hasattr(self.view._chatroom_voice_button, "set_icon_name"):
                self.view._chatroom_voice_button.set_icon_name("audio-input-microphone-symbolic")
            elif hasattr(self.view._chatroom_voice_button, "get_widget"):
                widget = self.view._chatroom_voice_button.get_widget()
                if hasattr(widget, "set_icon_name"):
                    widget.set_icon_name("audio-input-microphone-symbolic")
            # Reset timer display
            if self.view._recording_status_label:
                self.view._recording_status_label.set_visible(False)

    def stop_toggle_recording(self):
        """Stop toggle recording and process transcript"""
        try:
            # Always stop recording state and timer
            self.view._is_recording = False

            # Reset button appearance
            self.view._chatroom_voice_button.remove_css_class("recording-active")
            if hasattr(self.view._chatroom_voice_button, "set_icon_name"):
                self.view._chatroom_voice_button.set_icon_name("audio-input-microphone-symbolic")
            elif hasattr(self.view._chatroom_voice_button, "get_widget"):
                widget = self.view._chatroom_voice_button.get_widget()
                if hasattr(widget, "set_icon_name"):
                    widget.set_icon_name("audio-input-microphone-symbolic")

            # Stop timer
            self.stop_recording_timer()

            # Update voice visualizer and status
            if self.view._voice_visualizer:
                self.view._voice_visualizer.set_recording_state(False)
                self.view._voice_visualizer.set_processing_state(True)

            # Hide timer during processing
            if self.view._recording_status_label:
                self.view._recording_status_label.set_visible(False)

            # Show minimal feedback
            self.view.app.show_toast("Processing...")

            # Log event
            if hasattr(self.view.app, "session_logger") and self.view.app.session_logger:
                self.view.app.session_logger.log_gui_event(
                    "CHATROOM_TOGGLE_RECORDING_STOP",
                    "Stopped toggle recording in chatroom",
                )

            # Use AudioHandler (always available now)
            if hasattr(self.view.app, "audio_handler") and self.view.app.audio_handler:
                self.view.app.audio_handler.stop_recording()
            else:
                print("⚠️ AudioHandler not available")
                self.view.app.show_toast("Audio recording not available")

        except Exception as e:
            print(f"❌ Stop toggle recording error: {e}")
            self.view.app.show_toast(f"Stop recording failed: {e}")
            # Reset state on error
            self.view._is_recording = False
            self.stop_recording_timer()

    def start_recording_timer(self):
        """Start the recording timer display"""
        try:

            def update_timer():
                if self.view._is_recording and self.view._recording_start_time:
                    elapsed = time.time() - self.view._recording_start_time
                    minutes = int(elapsed // 60)
                    seconds = int(elapsed % 60)

                    # Update timer display in the UI
                    timer_display = f"{minutes:02d}:{seconds:02d}"
                    if self.view._recording_status_label:
                        self.view._recording_status_label.set_text(timer_display)

                    # Update button tooltip (simplified)
                    tooltip_text = "Click to stop recording"
                    if hasattr(self.view._chatroom_voice_button, "set_tooltip_text"):
                        self.view._chatroom_voice_button.set_tooltip_text(tooltip_text)
                    elif hasattr(self.view._chatroom_voice_button, "get_widget"):
                        widget = self.view._chatroom_voice_button.get_widget()
                        if hasattr(widget, "set_tooltip_text"):
                            widget.set_tooltip_text(tooltip_text)

                    return True  # Continue timer
                return False  # Stop timer

            # Update every second
            self.view._recording_timer_id = GLib.timeout_add_seconds(1, update_timer)

        except Exception as e:
            print(f"❌ Recording timer error: {e}")

    def stop_recording_timer(self):
        """Stop the recording timer"""
        try:
            if self.view._recording_timer_id:
                GLib.source_remove(self.view._recording_timer_id)
                self.view._recording_timer_id = None

        except Exception as e:
            print(f"❌ Stop recording timer error: {e}")

    def add_voice_transcript(self, transcript):
        """Add voice transcript to input field with proper UI refresh (called from parent app)"""
        try:
            # Handle FormInput (new centralized component)
            if COMPONENTS_AVAILABLE and isinstance(self.view._chat_input, FormInput):
                # FormInput handles append/replace based on voice_mode
                self.view._chat_input.append_transcript(transcript)
                new_text = self.view._chat_input.get_value()
            # Handle TextEditor (legacy)
            elif COMPONENTS_AVAILABLE and hasattr(self.view._chat_input, "get_content"):
                current_text = self.view._chat_input.get_content()
                new_text = f"{current_text} {transcript}" if current_text.strip() else transcript
                self.view._chat_input.set_content(new_text)
            else:
                # Fallback for basic TextView
                buffer = self.view._chat_input.get_buffer()
                current_text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False)

                new_text = f"{current_text} {transcript}" if current_text.strip() else transcript

                buffer.set_text(new_text)

            # Enable send button only if there's content AND active session
            has_content = new_text and new_text.strip()
            has_session = self.view._session_status == "active"
            self.view._chatroom_send_button.set_sensitive(has_content and has_session)

            # Reset voice visualizer and status
            if self.view._voice_visualizer:
                self.view._voice_visualizer.set_processing_state(False)

            # Hide timer after completion
            if self.view._recording_status_label:
                self.view._recording_status_label.set_visible(False)

            # Force UI refresh to prevent blank view issue
            GLib.idle_add(self.refresh_ui_after_transcript)

        except Exception as e:
            print(f"❌ Add voice transcript error: {e}")
            if hasattr(self.view.app, "show_toast"):
                self.view.app.show_toast(f"Transcript: {transcript}")

    def refresh_ui_after_transcript(self):
        """Force UI refresh after transcript to prevent blank view (called via GLib.idle_add)"""
        try:
            # Force the input widget to refresh and show the updated content
            if self.view._chat_input and hasattr(self.view._chat_input, "widget") and self.view._chat_input.widget:
                # FormInput is a composite component, so we need to call queue_draw on its widget
                self.view._chat_input.widget.queue_draw()

            # Ensure the input area is visible and focused
            if hasattr(self.view._chat_input, "grab_focus"):
                self.view._chat_input.grab_focus()

            return False  # Don't repeat this idle callback
        except Exception as e:
            print(f"❌ UI refresh after transcript error: {e}")
            return False
