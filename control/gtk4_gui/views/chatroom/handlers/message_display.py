from __future__ import annotations

from typing import TYPE_CHECKING

from gi.repository import GLib, Gtk, Pango

if TYPE_CHECKING:  # pragma: no cover - type checking only
    from .chatroom_view import ChatroomView


class ChatMessageDisplay:
    """Handle message display, TTS, and thinking indicators for ChatroomView."""

    def __init__(self, view: ChatroomView) -> None:
        self.view = view
        self._tts_service = None

    def add_chat_message(self, sender, message, message_type="user"):
        """Add a message to the chat display"""
        try:
            if not self.view._messages_container:
                return

            # Create message container
            message_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            message_box.set_margin_bottom(12)

            # Create sender label
            sender_label = Gtk.Label(label=sender)
            sender_label.set_halign(Gtk.Align.START)
            sender_label.add_css_class("caption")

            if message_type == "user":
                sender_label.add_css_class("accent")
            elif message_type == "assistant":
                sender_label.add_css_class("success")
            elif message_type == "error":
                sender_label.add_css_class("error")
            elif message_type == "system":
                sender_label.add_css_class("dim-label")
            elif message_type == "tool":
                sender_label.add_css_class("warning")

            message_box.append(sender_label)

            # Create message label
            message_label = Gtk.Label(label=message)
            message_label.set_halign(Gtk.Align.START)
            message_label.set_wrap(True)
            message_label.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
            message_label.set_selectable(True)
            message_label.set_max_width_chars(80)

            message_box.append(message_label)

            # Add microphone button for assistant messages
            if message_type == "assistant":
                button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
                button_box.set_halign(Gtk.Align.START)
                button_box.set_margin_top(8)

                mic_button = Gtk.Button(label="🎤 Hear")
                mic_button.set_tooltip_text("Play text-to-speech audio")
                mic_button.connect("clicked", self._on_tts_button_clicked, message)

                button_box.append(mic_button)
                message_box.append(button_box)

            # Add to messages container
            self.view._messages_container.append(message_box)

            # Auto-scroll to bottom
            self.scroll_to_bottom()

        except Exception as e:
            print(f"❌ Add chat message error: {e}")

    def scroll_to_bottom(self):
        """Scroll chat to bottom"""
        try:
            if not self.view._messages_container:
                return

            # Find the scrolled window parent
            parent = self.view._messages_container.get_parent()
            while parent and not isinstance(parent, Gtk.ScrolledWindow):
                parent = parent.get_parent()

            if parent:
                vadj = parent.get_vadjustment()
                if vadj:
                    # Use idle_add to ensure scroll happens after widget is rendered
                    GLib.idle_add(lambda: vadj.set_value(vadj.get_upper() - vadj.get_page_size()))

        except Exception as e:
            print(f"❌ Scroll to bottom error: {e}")

    def clear_message_container(self):
        """Clear all messages from the chat display"""
        try:
            if not self.view._messages_container:
                return

            # Remove all child widgets
            while True:
                child = self.view._messages_container.get_first_child()
                if not child:
                    break
                self.view._messages_container.remove(child)

        except Exception as e:
            print(f"❌ Clear message container error: {e}")

    def add_error_message(self, error_msg):
        """Add error message to chat"""
        try:
            error_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            error_container.add_css_class("message-container")
            error_container.add_css_class("error-message")
            error_container.set_margin_top(8)
            error_container.set_margin_bottom(8)
            error_container.set_margin_start(12)
            error_container.set_margin_end(12)

            # Add error icon
            icon = Gtk.Image.new_from_icon_name("dialog-error-symbolic")
            icon.add_css_class("error")
            error_container.append(icon)

            # Add error label
            label = Gtk.Label()
            label.set_markup(f"<b>Error:</b> {error_msg}")
            label.set_halign(Gtk.Align.START)
            label.set_wrap(True)
            error_container.append(label)

            self.view._messages_container.append(error_container)
            self.scroll_to_bottom()

        except Exception as e:
            print(f"❌ Add error message error: {e}")

    def add_thinking_indicator(self):
        """Add thinking indicator to chat"""
        try:
            thinking_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            thinking_box.set_margin_bottom(12)

            # Assistant label
            assistant_label = Gtk.Label(label="Assistant")
            assistant_label.set_halign(Gtk.Align.START)
            assistant_label.add_css_class("caption")
            assistant_label.add_css_class("success")

            # Thinking indicator
            thinking_label = Gtk.Label(label="Thinking...")
            thinking_label.set_halign(Gtk.Align.START)
            thinking_label.add_css_class("dim-label")

            thinking_box.append(assistant_label)
            thinking_box.append(thinking_label)

            self.view._messages_container.append(thinking_box)
            self.scroll_to_bottom()

            return thinking_box

        except Exception as e:
            print(f"❌ Add thinking indicator error: {e}")
            return None

    def _on_tts_button_clicked(self, button, text):
        """Handle TTS button click - generate and play audio"""
        try:
            button.set_sensitive(False)
            button.set_label("🎤 Playing...")

            # Run TTS in background thread
            import threading

            thread = threading.Thread(target=self._tts_thread, args=(text, button), daemon=True)
            thread.start()

        except Exception as e:
            print(f"❌ TTS button click error: {e}")
            button.set_sensitive(True)
            button.set_label("🎤 Hear")

    def _tts_thread(self, text, button):
        """Generate and play TTS audio in background thread"""
        try:
            import subprocess
            import tempfile
            from pathlib import Path

            from libs.services import TTSService

            # Create TTS service instance
            if not self._tts_service:
                self._tts_service = TTSService()

            # Generate speech audio
            audio_data = self._tts_service.generate_voiceover(text, voice="default")

            if audio_data:
                # Save audio to temporary file
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                    f.write(audio_data)
                    audio_file = f.name

                # Play audio using system player
                try:
                    subprocess.run(["aplay", audio_file], check=True, timeout=60)
                except FileNotFoundError:
                    # Fallback to paplay if aplay not available
                    subprocess.run(["paplay", audio_file], check=True, timeout=60)
                finally:
                    # Clean up temp file
                    Path(audio_file).unlink(missing_ok=True)

                # Update button on main thread
                GLib.idle_add(lambda: self._update_tts_button(button, "✅ Done"))
                GLib.idle_add(lambda: button.set_sensitive(True))
                # Reset button label after 2 seconds
                GLib.timeout_add(2000, lambda: self._update_tts_button(button, "🎤 Hear"))
            else:
                GLib.idle_add(lambda: self._update_tts_button(button, "❌ Failed"))
                GLib.idle_add(lambda: button.set_sensitive(True))
                # Reset button label after 2 seconds
                GLib.timeout_add(2000, lambda: self._update_tts_button(button, "🎤 Hear"))

        except Exception as e:
            print(f"❌ TTS thread error: {e}")
            GLib.idle_add(lambda: self._update_tts_button(button, "❌ Error"))
            GLib.idle_add(lambda: button.set_sensitive(True))
            # Reset button label after 2 seconds
            GLib.timeout_add(2000, lambda: self._update_tts_button(button, "🎤 Hear"))

    def _update_tts_button(self, button, label):
        """Update TTS button label"""
        try:
            button.set_label(label)
        except Exception as e:
            print(f"❌ Update TTS button error: {e}")
