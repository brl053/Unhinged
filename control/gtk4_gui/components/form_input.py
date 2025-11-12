"""
@llm-doc FormInput Component - Swiss Army Knife Input
@llm-version 1.0.0
@llm-date 2025-11-12

Reusable input component supporting multiple input types:
- text: Single-line text input
- textarea: Multi-line text input
- select: Dropdown selection
- checkbox: Boolean toggle
- hidden: Internal state (no widget)
- voice: Voice recording with transcription and waveform visualizer

FUTURE: Will add 'image' type for image generation UI, which will require
renaming the /image slash command in OS Chatroom to avoid naming collision.
"""

import gi
import time
import threading

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from typing import Any, Callable, Optional
from gi.repository import Gtk, GObject, GLib, Pango

from .base import ComponentBase


class FormInput(ComponentBase):
    """
    Reusable input component for all form types.
    
    Supports: text, textarea, select, checkbox, hidden, voice
    """

    __gsignals__ = {
        'value-changed': (GObject.SignalFlags.RUN_FIRST, None, (object,)),
        'focus-in': (GObject.SignalFlags.RUN_FIRST, None, ()),
        'focus-out': (GObject.SignalFlags.RUN_FIRST, None, ()),
        'validation-error': (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        'recording-started': (GObject.SignalFlags.RUN_FIRST, None, ()),
        'recording-stopped': (GObject.SignalFlags.RUN_FIRST, None, ()),
        'transcription-started': (GObject.SignalFlags.RUN_FIRST, None, ()),
        'transcription-completed': (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        'transcription-error': (GObject.SignalFlags.RUN_FIRST, None, (str,)),
    }

    def __init__(self,
                 input_type: str = "text",
                 name: str = "",
                 label: str = "",
                 value: Any = "",
                 required: bool = False,
                 placeholder: str = "",
                 help_text: str = "",
                 disabled: bool = False,
                 readonly: bool = False,
                 min_length: int = 0,
                 max_length: Optional[int] = None,
                 rows: int = 4,
                 options: Optional[list] = None,
                 enable_voice: bool = False,
                 voice_language: str = "en-US",
                 voice_mode: str = "append",
                 show_visualizer: bool = True,
                 visualizer_width: int = 250,
                 audio_handler: Optional[object] = None,
                 **kwargs):

        self.input_type = input_type
        self.name = name
        self.label_text = label
        self.value = value
        self.required = required
        self.placeholder = placeholder
        self.help_text = help_text
        self.disabled = disabled
        self.readonly = readonly
        self.min_length = min_length
        self.max_length = max_length
        self.rows = rows
        self.options = options or []
        self.enable_voice = enable_voice
        self.voice_language = voice_language
        self.voice_mode = voice_mode
        self.show_visualizer = show_visualizer
        self.visualizer_width = visualizer_width
        self.audio_handler = audio_handler

        # Voice state
        self._is_recording = False
        self._recording_start_time = None
        self._recording_timer_id = None
        self._voice_visualizer = None
        self._recording_timer_label = None

        # Error state
        self.error_message = ""
        self._error_label = None

        # Input widget reference
        self._input_widget = None

        super().__init__("form-input", **kwargs)

    def _init_component(self, **kwargs):
        """Initialize the form input component."""
        # Create main container
        self.widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        
        # Add label if provided
        if self.label_text:
            label = Gtk.Label(label=self.label_text)
            label.set_halign(Gtk.Align.START)
            label.add_css_class("form-label")
            self.widget.append(label)
        
        # Create input widget based on type
        self._create_input_widget()
        
        # Add help text if provided
        if self.help_text:
            help_label = Gtk.Label(label=self.help_text)
            help_label.set_halign(Gtk.Align.START)
            help_label.set_wrap(True)
            help_label.add_css_class("form-help-text")
            help_label.add_css_class("dim-label")
            self.widget.append(help_label)
        
        # Add error label (initially hidden)
        self._error_label = Gtk.Label()
        self._error_label.set_halign(Gtk.Align.START)
        self._error_label.set_wrap(True)
        self._error_label.add_css_class("form-error-text")
        self._error_label.add_css_class("error")
        self._error_label.set_visible(False)
        self.widget.append(self._error_label)

    def _create_input_widget(self):
        """Create the appropriate input widget based on type."""
        if self.input_type == "text":
            self._create_text_input()
        elif self.input_type == "textarea":
            self._create_textarea_input()
        elif self.input_type == "select":
            self._create_select_input()
        elif self.input_type == "checkbox":
            self._create_checkbox_input()
        elif self.input_type == "voice":
            self._create_voice_input()
        elif self.input_type == "hidden":
            # Hidden input - no widget
            pass

    def _create_text_input(self):
        """Create text input widget."""
        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)

        entry = Gtk.Entry()
        entry.set_placeholder_text(self.placeholder)
        entry.set_text(str(self.value) if self.value else "")
        entry.set_sensitive(not self.disabled)
        entry.set_editable(not self.readonly)

        if self.max_length:
            entry.set_max_length(self.max_length)

        entry.connect('changed', self._on_text_changed)

        container.append(entry)
        self._input_widget = entry

        # Add voice button if enabled
        if self.enable_voice:
            self._add_voice_button_to_container(container)

        self.widget.append(container)

    def _create_textarea_input(self):
        """Create textarea input widget."""
        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_hexpand(True)
        scrolled.set_min_content_height(self.rows * 30)

        text_view = Gtk.TextView()
        text_view.set_wrap_mode(Gtk.WrapMode.WORD)
        text_view.set_editable(not self.readonly)
        text_view.set_sensitive(not self.disabled)

        buffer = text_view.get_buffer()
        buffer.set_text(str(self.value) if self.value else "")
        buffer.connect('changed', self._on_text_changed)

        scrolled.set_child(text_view)
        container.append(scrolled)
        self._input_widget = text_view

        # Add voice button if enabled
        if self.enable_voice:
            self._add_voice_button_to_container(container)

        self.widget.append(container)

    def _create_select_input(self):
        """Create select/dropdown input widget."""
        combo = Gtk.ComboBoxText()
        
        for option in self.options:
            combo.append(option.get('value', ''), option.get('label', ''))
        
        if self.value:
            combo.set_active_id(str(self.value))
        
        combo.set_sensitive(not self.disabled)
        combo.connect('changed', self._on_select_changed)
        
        self.widget.append(combo)
        self._input_widget = combo

    def _create_checkbox_input(self):
        """Create checkbox input widget."""
        check = Gtk.CheckButton(label=self.label_text)
        check.set_active(bool(self.value))
        check.set_sensitive(not self.disabled)
        check.connect('toggled', self._on_checkbox_toggled)
        
        self.widget.append(check)
        self._input_widget = check

    def _create_voice_input(self):
        """Create voice input widget with visualizer."""
        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)

        # Text display area
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_hexpand(True)
        scrolled.set_min_content_height(100)

        text_view = Gtk.TextView()
        text_view.set_wrap_mode(Gtk.WrapMode.WORD)
        text_view.set_editable(True)

        buffer = text_view.get_buffer()
        buffer.set_text(str(self.value) if self.value else "")
        buffer.connect('changed', self._on_text_changed)

        scrolled.set_child(text_view)
        container.append(scrolled)
        self._input_widget = text_view
        
        # Voice controls row
        controls_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        
        # Recording timer
        timer_label = Gtk.Label(label="00:00")
        timer_label.set_halign(Gtk.Align.START)
        timer_label.add_css_class("monospace")
        timer_label.set_visible(False)
        controls_row.append(timer_label)
        self._recording_timer_label = timer_label
        
        # Waveform visualizer placeholder
        if self.show_visualizer:
            try:
                from .voice_visualizer import VoiceVisualizerFactory
                visualizer = VoiceVisualizerFactory.create_waveform_display(width=self.visualizer_width)
                visualizer.set_hexpand(True)
                controls_row.append(visualizer)
                self._voice_visualizer = visualizer
            except Exception as e:
                print(f"Failed to create voice visualizer: {e}")
        
        # Voice button
        voice_btn = Gtk.Button()
        voice_btn.set_icon_name("audio-input-microphone-symbolic")
        voice_btn.set_tooltip_text("Click to start/stop recording")
        voice_btn.connect('clicked', self._on_voice_button_clicked)
        controls_row.append(voice_btn)
        self._voice_button = voice_btn
        
        container.append(controls_row)
        self.widget.append(container)

    def _add_voice_button_to_container(self, container):
        """Add voice button to text/textarea container."""
        controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        
        voice_btn = Gtk.Button()
        voice_btn.set_icon_name("audio-input-microphone-symbolic")
        voice_btn.set_tooltip_text("Click to record voice")
        voice_btn.connect('clicked', self._on_voice_button_clicked)
        controls.append(voice_btn)
        
        container.append(controls)
        self._voice_button = voice_btn

    def _on_voice_button_clicked(self, button):
        """Handle voice button click."""
        if not self._is_recording:
            self._start_recording()
        else:
            self._stop_recording()

    def _start_recording(self):
        """Start voice recording via audio handler."""
        try:
            # If audio handler is available, use it for actual recording
            if self.audio_handler and hasattr(self.audio_handler, 'start_recording'):
                # Subscribe to transcription completion BEFORE starting
                # Audio handler emits transcript via AMPLITUDE_UPDATED event
                if hasattr(self.audio_handler, 'subscribe_to_events'):
                    from ..utils.event_bus import AudioEvents
                    # Subscribe to amplitude updates (which includes transcripts)
                    self.audio_handler.subscribe_to_events(
                        AudioEvents.AMPLITUDE_UPDATED,
                        self._on_audio_event
                    )
                    # Also subscribe to errors
                    self.audio_handler.subscribe_to_events(
                        AudioEvents.ERROR,
                        self._on_audio_error
                    )

                # Now start recording
                self.audio_handler.start_recording()

            self._is_recording = True
            self._recording_start_time = time.time()
            self.emit('recording-started')

            if self._recording_timer_label:
                self._recording_timer_label.set_visible(True)

            if self._voice_visualizer:
                self._voice_visualizer.set_recording_state(True)

            # Start timer
            self._start_timer()
        except Exception as e:
            print(f"❌ Start recording error: {e}")
            self._is_recording = False
            self.emit('transcription-error', str(e))

    def _stop_recording(self):
        """Stop voice recording via audio handler."""
        try:
            self._is_recording = False

            # If audio handler is available, stop it
            if self.audio_handler and hasattr(self.audio_handler, 'stop_recording'):
                self.audio_handler.stop_recording()

            self.emit('recording-stopped')

            if self._recording_timer_id:
                GLib.source_remove(self._recording_timer_id)
                self._recording_timer_id = None

            if self._recording_timer_label:
                self._recording_timer_label.set_visible(False)

            if self._voice_visualizer:
                self._voice_visualizer.set_recording_state(False)
        except Exception as e:
            print(f"❌ Stop recording error: {e}")
            self.emit('transcription-error', str(e))

    def _start_timer(self):
        """Start recording timer."""
        def update_timer():
            if self._is_recording and self._recording_start_time:
                elapsed = int(time.time() - self._recording_start_time)
                minutes = elapsed // 60
                seconds = elapsed % 60
                if self._recording_timer_label:
                    self._recording_timer_label.set_text(f"{minutes:02d}:{seconds:02d}")
            return self._is_recording
        
        self._recording_timer_id = GLib.timeout_add(1000, update_timer)

    def _on_text_changed(self, *args):
        """Handle text change."""
        self.value = self.get_value()
        self.emit('value-changed', self.value)

    def _on_select_changed(self, combo):
        """Handle select change."""
        self.value = combo.get_active_id()
        self.emit('value-changed', self.value)

    def _on_checkbox_toggled(self, check):
        """Handle checkbox toggle."""
        self.value = check.get_active()
        self.emit('value-changed', self.value)

    def get_value(self) -> Any:
        """Get current input value."""
        if self.input_type == "hidden":
            return self.value
        elif self.input_type == "checkbox":
            return self._input_widget.get_active() if self._input_widget else False
        elif self.input_type == "select":
            return self._input_widget.get_active_id() if self._input_widget else None
        elif self.input_type in ("text", "voice"):
            return self._input_widget.get_text() if self._input_widget else ""
        elif self.input_type == "textarea":
            if self._input_widget:
                buffer = self._input_widget.get_buffer()
                return buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False)
            return ""
        return ""

    def set_value(self, value: Any):
        """Set input value."""
        self.value = value
        if self.input_type == "text":
            self._input_widget.set_text(str(value) if value else "")
        elif self.input_type == "textarea":
            buffer = self._input_widget.get_buffer()
            buffer.set_text(str(value) if value else "")
        elif self.input_type == "checkbox":
            self._input_widget.set_active(bool(value))
        elif self.input_type == "select":
            self._input_widget.set_active_id(str(value) if value else "")

    def validate(self) -> bool:
        """Validate input."""
        if self.required and not self.get_value():
            self.set_error("This field is required")
            return False
        
        value = str(self.get_value())
        if self.min_length and len(value) < self.min_length:
            self.set_error(f"Minimum {self.min_length} characters required")
            return False
        
        if self.max_length and len(value) > self.max_length:
            self.set_error(f"Maximum {self.max_length} characters allowed")
            return False
        
        self.clear_error()
        return True

    def set_error(self, message: str):
        """Set error message."""
        self.error_message = message
        if self._error_label:
            self._error_label.set_text(message)
            self._error_label.set_visible(True)
        self.emit('validation-error', message)

    def clear_error(self):
        """Clear error message."""
        self.error_message = ""
        if self._error_label:
            self._error_label.set_visible(False)

    def append_transcript(self, text: str):
        """Append transcribed text to existing value."""
        current = self.get_value()
        if current.strip():
            new_value = f"{current} {text}"
        else:
            new_value = text
        self.set_value(new_value)
        self.emit('transcription-completed', text)

    def set_transcript(self, text: str):
        """Replace value with transcribed text."""
        self.set_value(text)
        self.emit('transcription-completed', text)

    def get_recording_time(self) -> int:
        """Get elapsed recording time in seconds."""
        if self._is_recording and self._recording_start_time:
            return int(time.time() - self._recording_start_time)
        return 0

    def _on_audio_event(self, event):
        """Handle audio events from audio handler (including transcription)."""
        try:
            # Check if this event contains a transcript
            if hasattr(event, 'data') and isinstance(event.data, dict):
                transcript = event.data.get('transcript')
                if transcript:
                    # Emit transcription started signal
                    self.emit('transcription-started')

                    # Append or replace based on voice_mode
                    if self.voice_mode == "append":
                        self.append_transcript(transcript)
                    else:
                        self.set_transcript(transcript)
        except Exception as e:
            print(f"❌ Audio event error: {e}")
            self.emit('transcription-error', str(e))

    def _on_audio_error(self, event):
        """Handle audio errors from audio handler."""
        try:
            error_msg = ""
            if hasattr(event, 'data') and isinstance(event.data, dict):
                error_msg = event.data.get('error', 'Unknown error')
            else:
                error_msg = str(event)

            print(f"❌ Audio error: {error_msg}")
            self.emit('transcription-error', error_msg)
        except Exception as e:
            print(f"❌ Error handling audio error: {e}")

