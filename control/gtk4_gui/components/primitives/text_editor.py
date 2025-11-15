"""
@llm-doc Primitive GTK4 Components
@llm-version 1.0.0
@llm-date 2025-10-28

Basic building block components with design system integration:
- ActionButton: Enhanced button with semantic styling
- StatusLabel: Label with status styling (success, warning, error)
- ProgressIndicator: Progress bar with semantic styling
- HardwareInfoRow: Hardware information display row
- ProcessRow: Process information display with controls
- BluetoothRow: Bluetooth device display with connection controls
- AudioDeviceRow: Audio device display with volume controls
"""

import logging

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("Gdk", "4.0")


from gi.repository import GObject, Gtk

from ..base import AdwComponentBase

logger = logging.getLogger(__name__)


class TextEditor(AdwComponentBase):
    """
    Multi-line text editor component following design system specification.

    Features:
    - Design system integration with semantic tokens
    - Placeholder text support
    - Word wrapping and text formatting
    - Event handling for content changes
    - Accessibility support
    - Based on text_editor.yaml specification
    """

    __gsignals__ = {
        "content-changed": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        "focus-gained": (GObject.SignalFlags.RUN_FIRST, None, ()),
        "focus-lost": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(
        self,
        content: str = "",
        placeholder: str = "",
        word_wrap: bool = True,
        min_height: int = 120,
        **kwargs,
    ):
        self.content = content
        self.placeholder = placeholder
        self.word_wrap = word_wrap
        self.min_height = min_height
        self._text_buffer = None
        self._text_view = None
        self._placeholder_label = None
        self._is_focused = False

        super().__init__("text-editor", **kwargs)

    def _init_component(self, **kwargs):
        """Initialize the text editor component."""
        # Create main container
        self.widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        # Create overlay for placeholder
        overlay = Gtk.Overlay()

        # Create text view
        self._text_view = Gtk.TextView()
        self._text_view.set_wrap_mode(
            Gtk.WrapMode.WORD_CHAR if self.word_wrap else Gtk.WrapMode.NONE
        )
        self._text_view.set_accepts_tab(True)
        self._text_view.set_vexpand(True)
        self._text_view.set_hexpand(True)

        # Set minimum height
        self._text_view.set_size_request(-1, self.min_height)

        # Get text buffer
        self._text_buffer = self._text_view.get_buffer()

        # Set initial content
        if self.content:
            self._text_buffer.set_text(self.content)

        # Create placeholder label
        if self.placeholder:
            self._placeholder_label = Gtk.Label(label=self.placeholder)
            self._placeholder_label.set_halign(Gtk.Align.START)
            self._placeholder_label.set_valign(Gtk.Align.START)
            self._placeholder_label.set_margin_top(8)
            self._placeholder_label.set_margin_start(8)
            self._placeholder_label.add_css_class("dim-label")
            self._placeholder_label.add_css_class("ds-placeholder")

            # Show/hide placeholder based on content
            self._update_placeholder_visibility()

        # Add to overlay
        overlay.set_child(self._text_view)
        if self._placeholder_label:
            overlay.add_overlay(self._placeholder_label)

        # Add to main widget
        self.widget.append(overlay)

        # Connect signals
        self._text_buffer.connect("changed", self._on_content_changed)

        # Create focus controller for GTK4
        focus_controller = Gtk.EventControllerFocus()
        focus_controller.connect("enter", self._on_focus_in)
        focus_controller.connect("leave", self._on_focus_out)
        self._text_view.add_controller(focus_controller)

        # Apply design system styling
        self._apply_text_editor_styling()

    def _apply_text_editor_styling(self):
        """Apply design system styling to the text editor."""
        # Add design system classes
        self.add_css_class("ds-text-editor")
        self._text_view.add_css_class("ds-text-input")

        # Apply semantic styling based on design system tokens
        if self._text_view:
            # Typography and spacing from design system
            self._text_view.add_css_class("ds-typography-body")

    def _on_content_changed(self, buffer):
        """Handle text buffer changes."""
        # Get current content
        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()
        content = buffer.get_text(start_iter, end_iter, False)

        # Update content property
        self.content = content

        # Update placeholder visibility
        if self._placeholder_label:
            self._update_placeholder_visibility()

        # Emit content changed signal
        self.emit("content-changed", content)

    def _on_focus_in(self, controller):
        """Handle focus in event."""
        self._is_focused = True
        self.add_css_class("ds-focused")
        if self._placeholder_label:
            self._update_placeholder_visibility()
        self.emit("focus-gained")

    def _on_focus_out(self, controller):
        """Handle focus out event."""
        self._is_focused = False
        self.remove_css_class("ds-focused")
        if self._placeholder_label:
            self._update_placeholder_visibility()
        self.emit("focus-lost")

    def _update_placeholder_visibility(self):
        """Show/hide placeholder based on content."""
        if self._placeholder_label:
            has_content = bool(self.content.strip())
            self._placeholder_label.set_visible(not has_content and not self._is_focused)

    def set_content(self, content: str):
        """Set text editor content."""
        self.content = content
        if self._text_buffer:
            self._text_buffer.set_text(content)

    def get_content(self) -> str:
        """Get current text editor content."""
        if self._text_buffer:
            start_iter = self._text_buffer.get_start_iter()
            end_iter = self._text_buffer.get_end_iter()
            return self._text_buffer.get_text(start_iter, end_iter, False)
        return self.content

    def set_placeholder(self, placeholder: str):
        """Set placeholder text."""
        self.placeholder = placeholder
        if self._placeholder_label:
            self._placeholder_label.set_text(placeholder)

    def clear(self):
        """Clear all content."""
        self.set_content("")

    def clear_content(self):
        """Clear all content (alias for clear)."""
        self.clear()

    def focus(self):
        """Focus the text editor."""
        if self._text_view:
            self._text_view.grab_focus()

    def grab_focus(self):
        """Grab focus (alias for focus)."""
        self.focus()

    def queue_draw(self):
        """Queue a redraw of the widget (GTK4 compatibility)."""
        if self._text_view:
            self._text_view.queue_draw()
        if self.widget:
            self.widget.queue_draw()

    def get_buffer(self):
        """Get the underlying text buffer (for compatibility)."""
        return self._text_buffer
