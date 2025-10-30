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

# Import voice visualizer separately
try:
    from ..components.voice_visualizer import VoiceVisualizerFactory
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
        self._recording_status_label = None

        # Session management state
        self._current_session_id = None
        self._session_status = "no_session"  # no_session, creating, active
        self._session_button = None
        self._session_id_label = None
        self._session_row = None
        
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

        # Create vertical container for text editor and voice controls
        input_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)  # sp_3 spacing

        # Add text editor at the top (expand to fill space)
        text_editor_widget.set_hexpand(True)
        input_container.append(text_editor_widget)

        # Create horizontal row for voice controls (below text editor)
        voice_controls_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)  # sp_2 spacing
        voice_controls_row.add_css_class("voice-controls-row")
        self._chatroom_input_row = voice_controls_row  # Store reference for timer

        # Create recording timer display (left side) - replaces status dots
        recording_timer = Gtk.Label(label="00:00")
        recording_timer.set_halign(Gtk.Align.START)
        recording_timer.add_css_class("caption")
        recording_timer.add_css_class("dim-label")
        recording_timer.add_css_class("recording-timer")
        recording_timer.set_visible(False)  # Hidden by default
        self._recording_status_label = recording_timer
        voice_controls_row.append(recording_timer)

        # Create horizontal waveform visualizer (center, expandable)
        if VOICE_VISUALIZER_AVAILABLE:
            try:
                self._voice_visualizer = VoiceVisualizerFactory.create_waveform_display(width=250)
                self._voice_visualizer.set_hexpand(True)  # Expand to fill available space
                self._voice_visualizer.add_css_class("voice-visualizer")
                voice_controls_row.append(self._voice_visualizer)

                # Connect visualizer to audio handler for real-time feedback
                if hasattr(self.app, 'audio_handler') and self.app.audio_handler:
                    self.app.audio_handler.set_voice_visualizer(self._voice_visualizer)

            except Exception as e:
                print(f"Failed to create voice visualizer: {e}")
                self._voice_visualizer = None

        # Create Voice button (right side)
        if COMPONENTS_AVAILABLE:
            self._chatroom_voice_button = ActionButton(
                text="",
                style="secondary",
                icon_name="audio-input-microphone-symbolic"
            )
            # Connect to click event for toggle recording
            self._chatroom_voice_button.connect("clicked", self._on_chatroom_voice_toggle)
            voice_widget = self._chatroom_voice_button.get_widget()
            voice_widget.set_tooltip_text("Click to start/stop recording")
            voice_controls_row.append(voice_widget)
        else:
            self._chatroom_voice_button = Gtk.Button()
            self._chatroom_voice_button.set_icon_name("audio-input-microphone-symbolic")
            self._chatroom_voice_button.connect("clicked", self._on_chatroom_voice_toggle)
            self._chatroom_voice_button.set_tooltip_text("Click to start/stop recording")
            voice_controls_row.append(self._chatroom_voice_button)

        # Create Send button (far right)
        self._chatroom_send_button = Gtk.Button(label="Send")
        self._chatroom_send_button.add_css_class("suggested-action")
        self._chatroom_send_button.set_sensitive(False)  # Initially disabled

        # Connect send button handler
        self._chatroom_send_button.connect("clicked", self._on_chatroom_send_clicked)

        # Add send button to voice controls row
        voice_controls_row.append(self._chatroom_send_button)

        # Add voice controls row to input container
        input_container.append(voice_controls_row)

        # Add input container to input area
        input_area.append(input_container)

        # Create session management section (before input area)
        session_section = self._create_session_management_section()

        # Add session section and input area to main container
        chatroom_container.append(session_section)
        chatroom_container.append(input_area)

        # Initialize UI state based on session status
        self._update_ui_for_session_state()

        return chatroom_container

    def _create_session_management_section(self):
        """Create session management UI section"""
        # Session management container
        session_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        session_container.set_margin_top(16)
        session_container.set_margin_bottom(8)
        session_container.set_margin_start(16)
        session_container.set_margin_end(16)

        # Session management row
        self._session_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self._session_row.set_halign(Gtk.Align.FILL)

        # Session ID label (left side, initially hidden)
        self._session_id_label = Gtk.Label()
        self._session_id_label.set_halign(Gtk.Align.START)
        self._session_id_label.set_hexpand(True)
        self._session_id_label.add_css_class("caption")
        self._session_id_label.set_visible(False)
        self._session_row.append(self._session_id_label)

        # Session button (right side)
        self._session_button = Gtk.Button()
        self._session_button.set_label("Create Session")
        self._session_button.add_css_class("suggested-action")
        self._session_button.connect("clicked", self._on_session_button_clicked)
        self._session_row.append(self._session_button)

        session_container.append(self._session_row)

        # Add separator
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        separator.set_margin_top(8)
        separator.set_margin_bottom(8)
        session_container.append(separator)

        return session_container

    def _on_session_button_clicked(self, button):
        """Handle session button click (Create Session or New Session)"""
        try:
            if self._session_status == "no_session":
                self._create_new_session()
            elif self._session_status == "active":
                self._create_new_session()  # Replace current session
        except Exception as e:
            print(f"❌ Session button click error: {e}")
            if hasattr(self.app, 'show_toast'):
                self.app.show_toast(f"Session error: {e}")

    def _create_new_session(self):
        """Create a new chat session using gRPC ChatService"""
        try:
            # Update UI to show creating state
            self._session_status = "creating"
            self._update_ui_for_session_state()

            # Create session in background thread
            import threading
            thread = threading.Thread(target=self._create_session_grpc, daemon=True)
            thread.start()

        except Exception as e:
            print(f"❌ Create session error: {e}")
            self._session_status = "no_session"
            self._update_ui_for_session_state()

    def _create_session_grpc(self):
        """Create session via gRPC ChatService.CreateConversation"""
        try:
            # Import gRPC client factory
            import sys
            from pathlib import Path as PathlibPath
            project_root = PathlibPath(__file__).parent.parent.parent
            grpc_lib_path = project_root / "libs" / "python" / "grpc"
            if grpc_lib_path.exists():
                sys.path.insert(0, str(grpc_lib_path.parent))

            from grpc.client_factory import create_chat_client

            # Import protobuf messages
            protobuf_path = project_root / "generated" / "python" / "clients"
            if protobuf_path.exists():
                sys.path.insert(0, str(protobuf_path))

            from unhinged_proto_clients import chat_pb2
            from unhinged_proto_clients import common_pb2

            # Create gRPC client
            client = create_chat_client()

            # Create conversation request
            request = chat_pb2.CreateConversationRequest(
                team_id="unhinged-desktop",
                namespace_id="os-chatroom",
                title=f"OS Chatroom Session {self._get_timestamp()}",
                description="Desktop OS Chatroom conversation session",
                settings=chat_pb2.ConversationSettings(
                    model="llama3.2",
                    temperature=0.7,
                    max_tokens=2048,
                    include_context=True,
                    context_window_size=4096,
                    enable_tools=False
                )
            )

            # Make gRPC call with timeout
            response = client.CreateConversation(request, timeout=10)

            # Check response
            if response and response.response.success:
                conversation_id = response.conversation.metadata.id

                # Update UI on main thread
                from gi.repository import GLib
                GLib.idle_add(self._on_session_created, conversation_id)
            else:
                error_msg = response.response.message if response else "Unknown error"
                GLib.idle_add(self._on_session_creation_failed, f"gRPC error: {error_msg}")

        except ImportError as e:
            # Fallback to simulation if gRPC not available
            print(f"⚠️ gRPC client not available, using simulation: {e}")
            self._simulate_session_creation()
        except Exception as e:
            print(f"❌ gRPC session creation error: {e}")
            from gi.repository import GLib
            GLib.idle_add(self._on_session_creation_failed, str(e))

    def _simulate_session_creation(self):
        """Fallback simulation when gRPC is not available"""
        import time
        import uuid

        time.sleep(0.5)  # Simulate network delay
        session_id = f"sim-{str(uuid.uuid4())[:8]}"  # Short ID for display

        # Update UI on main thread
        from gi.repository import GLib
        GLib.idle_add(self._on_session_created, session_id)

    def _get_timestamp(self):
        """Get current timestamp for session naming"""
        import datetime
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _on_session_created(self, session_id):
        """Handle successful session creation"""
        try:
            self._current_session_id = session_id
            self._session_status = "active"
            self._update_ui_for_session_state()

            # Log session creation
            if hasattr(self.app, 'session_logger') and self.app.session_logger:
                self.app.session_logger.log_gui_event("CHAT_SESSION_CREATED", f"Created chat session: {session_id}")

            # Show success toast
            if hasattr(self.app, 'show_toast'):
                self.app.show_toast(f"Session {session_id[:8]} created successfully")

        except Exception as e:
            print(f"❌ Session created callback error: {e}")

    def _on_session_creation_failed(self, error_message):
        """Handle failed session creation"""
        try:
            self._session_status = "no_session"
            self._update_ui_for_session_state()

            # Log session creation failure
            if hasattr(self.app, 'session_logger') and self.app.session_logger:
                self.app.session_logger.log_gui_event("CHAT_SESSION_FAILED", f"Session creation failed: {error_message}")

            # Show error toast
            if hasattr(self.app, 'show_toast'):
                self.app.show_toast(f"Session creation failed: {error_message}")

        except Exception as e:
            print(f"❌ Session creation failed callback error: {e}")

    def _update_ui_for_session_state(self):
        """Update UI elements based on current session state"""
        try:
            if self._session_status == "no_session":
                # No session: disable chat, show Create Session button
                self._session_button.set_label("Create Session")
                self._session_button.set_sensitive(True)
                self._session_id_label.set_visible(False)
                self._disable_chat_functionality()

            elif self._session_status == "creating":
                # Creating session: disable button, show loading
                self._session_button.set_label("Creating...")
                self._session_button.set_sensitive(False)
                self._session_id_label.set_visible(False)
                self._disable_chat_functionality()

            elif self._session_status == "active":
                # Active session: enable chat, show session ID and New Session button
                self._session_button.set_label("New Session")
                self._session_button.set_sensitive(True)
                self._session_id_label.set_text(f"Session: {self._current_session_id}")
                self._session_id_label.set_visible(True)
                self._enable_chat_functionality()

        except Exception as e:
            print(f"❌ Update UI for session state error: {e}")

    def _disable_chat_functionality(self):
        """Disable chat input and voice controls until session exists"""
        try:
            # Disable text input
            if self._chat_input:
                self._chat_input.set_sensitive(False)

            # Disable send button
            if self._chatroom_send_button:
                self._chatroom_send_button.set_sensitive(False)

            # Disable voice button
            if self._chatroom_voice_button:
                self._chatroom_voice_button.set_sensitive(False)

        except Exception as e:
            print(f"❌ Disable chat functionality error: {e}")

    def _enable_chat_functionality(self):
        """Enable chat input and voice controls when session exists"""
        try:
            # Enable text input
            if self._chat_input:
                self._chat_input.set_sensitive(True)

            # Enable voice button
            if self._chatroom_voice_button:
                self._chatroom_voice_button.set_sensitive(True)

            # Send button will be enabled by content change handler

        except Exception as e:
            print(f"❌ Enable chat functionality error: {e}")

    def _on_chatroom_content_changed(self, text_editor, content):
        """Handle content changes in chatroom text editor"""
        try:
            # Enable/disable send button based on content AND session state
            has_content = content and content.strip()
            has_session = self._session_status == "active"
            self._chatroom_send_button.set_sensitive(has_content and has_session)

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
            # Always start recording state and timer (works with both new and legacy)
            self._is_recording = True
            self._recording_start_time = time.time()

            # Update button appearance
            self._chatroom_voice_button.add_css_class("recording-active")
            if hasattr(self._chatroom_voice_button, 'set_icon_name'):
                self._chatroom_voice_button.set_icon_name("media-playback-stop-symbolic")
            elif hasattr(self._chatroom_voice_button, 'get_widget'):
                widget = self._chatroom_voice_button.get_widget()
                if hasattr(widget, 'set_icon_name'):
                    widget.set_icon_name("media-playback-stop-symbolic")

            # Start recording timer (always show timer regardless of backend)
            self._start_recording_timer()

            # Update voice visualizer and status
            if self._voice_visualizer:
                self._voice_visualizer.set_recording_state(True)

            # Show timer display
            if self._recording_status_label:
                self._recording_status_label.set_text("00:00")
                self._recording_status_label.set_visible(True)
                self._recording_status_label.remove_css_class("dim-label")
                self._recording_status_label.add_css_class("accent")

            # Show minimal feedback
            self.app.show_toast("Recording...")

            # Log event
            if hasattr(self.app, 'session_logger') and self.app.session_logger:
                self.app.session_logger.log_gui_event("CHATROOM_TOGGLE_RECORDING_START", "Started toggle recording in chatroom")

            # Use AudioHandler (always available now)
            if hasattr(self.app, 'audio_handler') and self.app.audio_handler:
                self.app.audio_handler.start_recording()
            else:
                print("⚠️ AudioHandler not available")

        except Exception as e:
            print(f"❌ Start toggle recording error: {e}")
            self.app.show_toast(f"Recording failed: {e}")
            # Reset state on error
            self._is_recording = False
            self._stop_recording_timer()

    def _stop_toggle_recording(self):
        """Stop toggle recording and process transcript"""
        try:
            # Always stop recording state and timer
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

            # Update voice visualizer and status
            if self._voice_visualizer:
                self._voice_visualizer.set_recording_state(False)
                self._voice_visualizer.set_processing_state(True)

            # Hide timer during processing
            if self._recording_status_label:
                self._recording_status_label.set_visible(False)

            # Show minimal feedback
            self.app.show_toast("Processing...")

            # Log event
            if hasattr(self.app, 'session_logger') and self.app.session_logger:
                self.app.session_logger.log_gui_event("CHATROOM_TOGGLE_RECORDING_STOP", "Stopped toggle recording in chatroom")

            # Use AudioHandler (always available now)
            if hasattr(self.app, 'audio_handler') and self.app.audio_handler:
                self.app.audio_handler.stop_recording()
            else:
                print("⚠️ AudioHandler not available")
                self.app.show_toast("Audio recording not available")

        except Exception as e:
            print(f"❌ Stop toggle recording error: {e}")
            self.app.show_toast(f"Stop recording failed: {e}")
            # Reset state on error
            self._is_recording = False
            self._stop_recording_timer()

    def _start_recording_timer(self):
        """Start the recording timer display"""
        try:
            def update_timer():
                if self._is_recording and self._recording_start_time:
                    elapsed = time.time() - self._recording_start_time
                    minutes = int(elapsed // 60)
                    seconds = int(elapsed % 60)

                    # Update timer display in the UI
                    timer_display = f"{minutes:02d}:{seconds:02d}"
                    if self._recording_status_label:
                        self._recording_status_label.set_text(timer_display)

                    # Update button tooltip (simplified)
                    tooltip_text = "Click to stop recording"
                    if hasattr(self._chatroom_voice_button, 'set_tooltip_text'):
                        self._chatroom_voice_button.set_tooltip_text(tooltip_text)
                    elif hasattr(self._chatroom_voice_button, 'get_widget'):
                        widget = self._chatroom_voice_button.get_widget()
                        if hasattr(widget, 'set_tooltip_text'):
                            widget.set_tooltip_text(tooltip_text)

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

            # Add user message to chat with session context
            self._add_chat_message("You", message.strip(), "user")

            # Clear input
            if COMPONENTS_AVAILABLE and hasattr(self._chat_input, 'clear_content'):
                self._chat_input.clear_content()
            else:
                buffer = self._chat_input.get_buffer()
                buffer.set_text("")

            # Disable send button
            self._chatroom_send_button.set_sensitive(False)

            # Send to LLM with session context
            self._send_to_llm_with_session(message.strip())

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

    def _send_to_llm_with_session(self, message):
        """Send message to LLM with session context"""
        try:
            # Log message with session context
            if hasattr(self.app, 'session_logger') and self.app.session_logger:
                self.app.session_logger.log_gui_event("CHAT_MESSAGE_SENT",
                    f"Session {self._current_session_id}: {message[:50]}...")

            # Add session context to message if available
            if self._current_session_id:
                # For now, use the existing LLM method but with session logging
                # In the future, this could use ChatService.SendMessage with conversation_id
                self._send_to_llm(message)
            else:
                # This shouldn't happen due to UI controls, but handle gracefully
                print("⚠️ Attempting to send message without active session")
                if hasattr(self.app, 'show_toast'):
                    self.app.show_toast("No active session - please create a session first")

        except Exception as e:
            print(f"❌ Send to LLM with session error: {e}")
            # Fallback to regular LLM method
            self._send_to_llm(message)

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
        """Add voice transcript to input field with proper UI refresh (called from parent app)"""
        try:
            # Set transcript in input field
            if COMPONENTS_AVAILABLE and hasattr(self._chat_input, 'get_content'):
                current_text = self._chat_input.get_content()
                if current_text.strip():
                    # Append to existing text with space
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

            # Reset voice visualizer and status
            if self._voice_visualizer:
                self._voice_visualizer.set_processing_state(False)

            # Hide timer after completion
            if self._recording_status_label:
                self._recording_status_label.set_visible(False)

            # Force UI refresh to prevent blank view issue
            from gi.repository import GLib
            GLib.idle_add(self._refresh_ui_after_transcript)

        except Exception as e:
            print(f"❌ Add voice transcript error: {e}")
            if hasattr(self.app, 'show_toast'):
                self.app.show_toast(f"Transcript: {transcript}")

    def _refresh_ui_after_transcript(self):
        """Force UI refresh after transcript to prevent blank view (called via GLib.idle_add)"""
        try:
            # Force the input widget to refresh and show the updated content
            if self._chat_input:
                self._chat_input.queue_draw()

            # Ensure the input area is visible and focused
            if hasattr(self._chat_input, 'grab_focus'):
                self._chat_input.grab_focus()

            return False  # Don't repeat this idle callback
        except Exception as e:
            print(f"❌ UI refresh after transcript error: {e}")
            return False
