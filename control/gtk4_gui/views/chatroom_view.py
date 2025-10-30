"""
ChatroomView - OS Chatroom tab extracted from desktop_app.py

This module contains all the chatroom functionality that was previously
embedded in the monolithic desktop_app.py file.
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GLib, Pango
import threading
import time
import requests
import json

# Import architecture components
try:
    from ..config import app_config
    from ..audio_handler import AudioHandler, RecordingState
    from ..exceptions import get_user_friendly_message
    ARCHITECTURE_AVAILABLE = True
except ImportError:
    ARCHITECTURE_AVAILABLE = False

# Import component library
try:
    from ..components import TextEditor, ActionButton
    COMPONENTS_AVAILABLE = True
except ImportError:
    COMPONENTS_AVAILABLE = False


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
        messages_container.set_margin_top(16)     # sp_4 - major component margins
        messages_container.set_margin_bottom(16)  # sp_4 - major component margins
        messages_container.set_margin_start(16)   # sp_4 - major component margins
        messages_container.set_margin_end(16)     # sp_4 - major component margins

        messages_area.set_child(messages_container)
        chatroom_container.append(messages_area)
        
        # Store reference for adding messages
        self._messages_container = messages_container

        # Input area container (fixed at bottom, will contain text editor)
        # Using design system spacing: sp_6 (24px) for section breaks
        input_area = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        input_area.set_margin_top(24)     # sp_6 - section breaks, modal internal spacing
        input_area.set_margin_bottom(16)  # sp_4 - major component margins
        input_area.set_margin_start(16)   # sp_4 - major component margins
        input_area.set_margin_end(16)     # sp_4 - major component margins

        # Import and create TextEditor component
        if COMPONENTS_AVAILABLE:
            from ..components import TextEditor

            # Create proper text editor component following design system specification
            text_editor = TextEditor(
                placeholder="Type your message here...",
                word_wrap=True,
                min_height=120
            )

            # Apply design system margins (already handled by TextEditor component)
            text_editor_widget = text_editor.get_widget()
            text_editor_widget.set_margin_top(8)     # sp_2 - form field padding
            text_editor_widget.set_margin_bottom(8)  # sp_2 - form field padding
            text_editor_widget.set_margin_start(8)   # sp_2 - form field padding
            text_editor_widget.set_margin_end(8)     # sp_2 - form field padding

            # Connect text editor events
            text_editor.connect('content-changed', self._on_chatroom_content_changed)
            text_editor.connect('focus-gained', self._on_chatroom_focus_gained)
            text_editor.connect('focus-lost', self._on_chatroom_focus_lost)
            
            # Store reference
            self._chat_input = text_editor
        else:
            # Fallback to basic TextView
            text_editor_widget = Gtk.TextView()
            text_editor_widget.set_wrap_mode(Gtk.WrapMode.WORD)
            self._chat_input = text_editor_widget

        # Create horizontal box for text editor and send button
        input_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)  # sp_2 spacing
        self._chatroom_input_row = input_row  # Store reference for timer

        # Add text editor to horizontal box (expand to fill space)
        text_editor_widget.set_hexpand(True)
        input_row.append(text_editor_widget)

        # Create Voice button for chatroom
        if COMPONENTS_AVAILABLE:
            self._chatroom_voice_button = ActionButton(
                text="",
                style="secondary",
                icon_name="audio-input-microphone-symbolic"
            )
            # Connect to click event for toggle recording
            self._chatroom_voice_button.connect("clicked", self._on_chatroom_voice_toggle)
            voice_widget = self._chatroom_voice_button.get_widget()
            voice_widget.set_valign(Gtk.Align.END)  # Align to bottom of text editor
            voice_widget.set_tooltip_text("Click to start/stop recording")
            input_row.append(voice_widget)
        else:
            self._chatroom_voice_button = Gtk.Button()
            self._chatroom_voice_button.set_icon_name("audio-input-microphone-symbolic")
            self._chatroom_voice_button.connect("clicked", self._on_chatroom_voice_toggle)
            self._chatroom_voice_button.set_valign(Gtk.Align.END)
            self._chatroom_voice_button.set_tooltip_text("Click to start/stop recording")
            input_row.append(self._chatroom_voice_button)

        # Create Send button
        self._chatroom_send_button = Gtk.Button(label="Send")
        self._chatroom_send_button.add_css_class("suggested-action")
        self._chatroom_send_button.set_valign(Gtk.Align.END)  # Align to bottom of text editor
        self._chatroom_send_button.set_sensitive(False)  # Initially disabled

        # Connect send button handler
        self._chatroom_send_button.connect("clicked", self._on_chatroom_send_clicked)

        # Add send button to input row
        input_row.append(self._chatroom_send_button)

        # Add input row to input area
        input_area.append(input_row)

        # Add input area to main container
        chatroom_container.append(input_area)

        return chatroom_container

    def _on_chatroom_content_changed(self, text_editor, content):
        """Handle content changes in chatroom text editor"""
        try:
            # Enable/disable send button based on content
            has_content = content and content.strip()
            self._chatroom_send_button.set_sensitive(has_content)

            # Reset typing timer
            if self._typing_timer_id:
                GLib.source_remove(self._typing_timer_id)
                self._typing_timer_id = None

            # Set new timer if there's content
            if has_content:
                self._typing_timer_id = GLib.timeout_add_seconds(3, self._on_typing_timeout)

        except Exception as e:
            print(f"❌ Chatroom content change error: {e}")

    def _on_typing_timeout(self):
        """Handle typing timeout"""
        self._typing_timer_id = None
        return False  # Don't repeat

    def _on_chatroom_focus_gained(self, text_editor):
        """Handle focus gained in chatroom"""
        try:
            if hasattr(self.app, 'session_logger') and self.app.session_logger:
                self.app.session_logger.log_gui_event("CHATROOM_FOCUS_GAINED", "User focused on chatroom input")
        except Exception as e:
            print(f"❌ Chatroom focus gained error: {e}")

    def _on_chatroom_focus_lost(self, text_editor):
        """Handle focus lost in chatroom"""
        try:
            if hasattr(self.app, 'session_logger') and self.app.session_logger:
                self.app.session_logger.log_gui_event("CHATROOM_FOCUS_LOST", "User left chatroom input")
        except Exception as e:
            print(f"❌ Chatroom focus lost error: {e}")

    def _on_chatroom_voice_toggle(self, button):
        """Handle chatroom voice button toggle - start or stop recording."""
        try:
            if not self._is_recording:
                self._start_toggle_recording()
            else:
                self._stop_toggle_recording()

        except Exception as e:
            print(f"❌ Chatroom voice toggle error: {e}")
            if hasattr(self.app, 'show_toast'):
                self.app.show_toast(f"Voice recording failed: {e}")

    def _start_toggle_recording(self):
        """Start toggle recording with timer and visual feedback"""
        try:
            # Check if AudioHandler is available
            if ARCHITECTURE_AVAILABLE and hasattr(self.app, 'audio_handler') and self.app.audio_handler:
                # Use new AudioHandler
                self.app.audio_handler.start_recording()
                self._is_recording = True

                # Update button appearance
                self._chatroom_voice_button.add_css_class("recording-active")
                if hasattr(self._chatroom_voice_button, 'set_icon_name'):
                    self._chatroom_voice_button.set_icon_name("media-playback-stop-symbolic")
                elif hasattr(self._chatroom_voice_button, 'get_widget'):
                    widget = self._chatroom_voice_button.get_widget()
                    if hasattr(widget, 'set_icon_name'):
                        widget.set_icon_name("media-playback-stop-symbolic")

                # Start recording timer
                self._recording_start_time = time.time()
                self._start_recording_timer()

                # Show feedback
                self.app.show_toast("🎤 Recording... (click to stop)")

                # Log event
                if hasattr(self.app, 'session_logger') and self.app.session_logger:
                    self.app.session_logger.log_gui_event("CHATROOM_TOGGLE_RECORDING_START", "Started toggle recording in chatroom")

            else:
                # Fallback to basic recording
                if hasattr(self.app, 'on_record_voice_clicked'):
                    self.app.on_record_voice_clicked(self._chatroom_voice_button)
                else:
                    self.app.show_toast("Voice recording not available")

        except Exception as e:
            print(f"❌ Start toggle recording error: {e}")
            self.app.show_toast(f"Recording failed: {e}")

    def _stop_toggle_recording(self):
        """Stop toggle recording and process transcript"""
        try:
            if ARCHITECTURE_AVAILABLE and hasattr(self.app, 'audio_handler') and self.app.audio_handler:
                # Stop recording
                self.app.audio_handler.stop_recording()
                self._is_recording = False

                # Reset button appearance
                self._chatroom_voice_button.remove_css_class("recording-active")
                if hasattr(self._chatroom_voice_button, 'set_icon_name'):
                    self._chatroom_voice_button.set_icon_name("audio-input-microphone-symbolic")
                elif hasattr(self._chatroom_voice_button, 'get_widget'):
                    widget = self._chatroom_voice_button.get_widget()
                    if hasattr(widget, 'set_icon_name'):
                        widget.set_icon_name("audio-input-microphone-symbolic")

                # Stop timer
                self._stop_recording_timer()

                # Show feedback
                self.app.show_toast("🔄 Processing recording...")

                # Log event
                if hasattr(self.app, 'session_logger') and self.app.session_logger:
                    self.app.session_logger.log_gui_event("CHATROOM_TOGGLE_RECORDING_STOP", "Stopped toggle recording in chatroom")

            else:
                print("⚠️ AudioHandler not available for toggle recording")

        except Exception as e:
            print(f"❌ Stop toggle recording error: {e}")
            self.app.show_toast(f"Stop recording failed: {e}")

    def _start_recording_timer(self):
        """Start the recording timer display"""
        try:
            def update_timer():
                if self._is_recording and self._recording_start_time:
                    elapsed = time.time() - self._recording_start_time
                    minutes = int(elapsed // 60)
                    seconds = int(elapsed % 60)

                    # Update button tooltip with timer
                    timer_text = f"🎤 Recording {minutes:02d}:{seconds:02d} (click to stop)"

                    if hasattr(self._chatroom_voice_button, 'set_tooltip_text'):
                        self._chatroom_voice_button.set_tooltip_text(timer_text)
                    elif hasattr(self._chatroom_voice_button, 'get_widget'):
                        widget = self._chatroom_voice_button.get_widget()
                        if hasattr(widget, 'set_tooltip_text'):
                            widget.set_tooltip_text(timer_text)

                    return True  # Continue timer
                return False  # Stop timer

            # Update every second
            self._recording_timer_id = GLib.timeout_add_seconds(1, update_timer)

        except Exception as e:
            print(f"❌ Recording timer error: {e}")

    def _stop_recording_timer(self):
        """Stop the recording timer"""
        try:
            if self._recording_timer_id:
                GLib.source_remove(self._recording_timer_id)
                self._recording_timer_id = None

            # Reset tooltip
            if hasattr(self._chatroom_voice_button, 'set_tooltip_text'):
                self._chatroom_voice_button.set_tooltip_text("Click to start/stop recording")
            elif hasattr(self._chatroom_voice_button, 'get_widget'):
                widget = self._chatroom_voice_button.get_widget()
                if hasattr(widget, 'set_tooltip_text'):
                    widget.set_tooltip_text("Click to start/stop recording")

        except Exception as e:
            print(f"❌ Stop recording timer error: {e}")

    def _on_chatroom_send_clicked(self, button):
        """Handle send button click in chatroom"""
        try:
            # Get message content
            if COMPONENTS_AVAILABLE and hasattr(self._chat_input, 'get_content'):
                message = self._chat_input.get_content()
            else:
                # Fallback for basic TextView
                buffer = self._chat_input.get_buffer()
                start_iter = buffer.get_start_iter()
                end_iter = buffer.get_end_iter()
                message = buffer.get_text(start_iter, end_iter, False)

            if not message or not message.strip():
                return

            # Add user message to chat
            self._add_chat_message("You", message.strip(), "user")

            # Clear input
            if COMPONENTS_AVAILABLE and hasattr(self._chat_input, 'clear_content'):
                self._chat_input.clear_content()
            else:
                buffer = self._chat_input.get_buffer()
                buffer.set_text("")

            # Disable send button
            self._chatroom_send_button.set_sensitive(False)

            # Send to LLM
            self._send_to_llm(message.strip())

        except Exception as e:
            print(f"❌ Chatroom send error: {e}")
            if hasattr(self.app, 'show_toast'):
                self.app.show_toast(f"Send failed: {e}")

    def _add_chat_message(self, sender, message, message_type="user"):
        """Add a message to the chat display"""
        try:
            if not self._messages_container:
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

            message_box.append(sender_label)

            # Create message label
            message_label = Gtk.Label(label=message)
            message_label.set_halign(Gtk.Align.START)
            message_label.set_wrap(True)
            message_label.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
            message_label.set_selectable(True)

            message_box.append(message_label)

            # Add to messages container
            self._messages_container.append(message_box)

            # Auto-scroll to bottom
            self._scroll_to_bottom()

        except Exception as e:
            print(f"❌ Add chat message error: {e}")

    def _scroll_to_bottom(self):
        """Scroll chat to bottom"""
        try:
            if not self._messages_container:
                return

            # Find the scrolled window parent
            parent = self._messages_container.get_parent()
            while parent and not isinstance(parent, Gtk.ScrolledWindow):
                parent = parent.get_parent()

            if parent:
                vadj = parent.get_vadjustment()
                if vadj:
                    # Use idle_add to ensure scroll happens after widget is rendered
                    GLib.idle_add(lambda: vadj.set_value(vadj.get_upper() - vadj.get_page_size()))

        except Exception as e:
            print(f"❌ Scroll to bottom error: {e}")

    def _send_to_llm(self, message):
        """Send message to LLM service"""
        try:
            # Add thinking indicator
            thinking_box = self._add_thinking_indicator()

            # Send in background thread
            thread = threading.Thread(target=self._llm_request_thread, args=(message, thinking_box), daemon=True)
            thread.start()

        except Exception as e:
            print(f"❌ Send to LLM error: {e}")
            if hasattr(self.app, 'show_toast'):
                self.app.show_toast(f"LLM request failed: {e}")

    def _add_thinking_indicator(self):
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

            self._messages_container.append(thinking_box)
            self._scroll_to_bottom()

            return thinking_box

        except Exception as e:
            print(f"❌ Add thinking indicator error: {e}")
            return None

    def _llm_request_thread(self, message, thinking_box):
        """Handle LLM request in background thread"""
        try:
            # Get LLM endpoint from config or fallback
            if ARCHITECTURE_AVAILABLE:
                from ..config import get_service_endpoint
                llm_endpoint = get_service_endpoint('llm')
                llm_url = f"http://{llm_endpoint.address}/api/generate"
            else:
                llm_url = "http://localhost:1500/api/generate"

            # Prepare request
            payload = {
                "model": "llama3.2:3b",
                "prompt": message,
                "stream": False
            }

            # Make request
            response = requests.post(llm_url, json=payload, timeout=30)

            if response.status_code == 200:
                response_data = response.json()
                llm_response = response_data.get('response', 'No response received')

                # Update UI on main thread
                GLib.idle_add(self._handle_llm_response, llm_response, thinking_box)
            else:
                error_msg = f"LLM service error: {response.status_code}"
                GLib.idle_add(self._handle_llm_error, error_msg, thinking_box)

        except requests.exceptions.Timeout:
            GLib.idle_add(self._handle_llm_error, "LLM request timed out", thinking_box)
        except requests.exceptions.ConnectionError:
            GLib.idle_add(self._handle_llm_error, "Cannot connect to LLM service", thinking_box)
        except Exception as e:
            GLib.idle_add(self._handle_llm_error, f"LLM request failed: {e}", thinking_box)

    def _handle_llm_response(self, response, thinking_box):
        """Handle LLM response on main thread"""
        try:
            # Remove thinking indicator
            if thinking_box and thinking_box.get_parent():
                self._messages_container.remove(thinking_box)

            # Add assistant response
            self._add_chat_message("Assistant", response, "assistant")

            # Log the interaction
            if hasattr(self.app, 'session_logger') and self.app.session_logger:
                self.app.session_logger.log_gui_event("LLM_RESPONSE_RECEIVED", f"Response length: {len(response)}")

        except Exception as e:
            print(f"❌ Handle LLM response error: {e}")

    def _handle_llm_error(self, error_msg, thinking_box):
        """Handle LLM error on main thread"""
        try:
            # Remove thinking indicator
            if thinking_box and thinking_box.get_parent():
                self._messages_container.remove(thinking_box)

            # Add error message
            self._add_chat_message("System", f"Error: {error_msg}", "error")

            # Show toast
            if hasattr(self.app, 'show_toast'):
                self.app.show_toast(error_msg)

        except Exception as e:
            print(f"❌ Handle LLM error: {e}")

    def add_voice_transcript(self, transcript):
        """Add voice transcript to chat input (called from parent app)"""
        try:
            if COMPONENTS_AVAILABLE and hasattr(self._chat_input, 'get_content'):
                current_text = self._chat_input.get_content()
                if current_text.strip():
                    # Append to existing text
                    new_text = f"{current_text} {transcript}"
                else:
                    # Set as new text
                    new_text = transcript

                self._chat_input.set_content(new_text)
            else:
                # Fallback for basic TextView
                buffer = self._chat_input.get_buffer()
                current_text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False)

                if current_text.strip():
                    new_text = f"{current_text} {transcript}"
                else:
                    new_text = transcript

                buffer.set_text(new_text)

            # Enable send button
            self._chatroom_send_button.set_sensitive(True)

            if hasattr(self.app, 'show_toast'):
                self.app.show_toast("Voice transcript added to chat")

        except Exception as e:
            print(f"❌ Add voice transcript error: {e}")
            if hasattr(self.app, 'show_toast'):
                self.app.show_toast(f"Transcript: {transcript}")
