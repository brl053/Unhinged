"""
@llm-doc Log Container Component
@llm-version 1.0.0
@llm-date 2025-11-15

LogContainer component for displaying scrollable log content with auto-scroll,
filtering, and copy functionality.
"""

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, Pango

from .base import ComponentBase


class LogContainer(ComponentBase):
    """
    Scrollable container for log content with filtering and search.

    Features:
    - Auto-scrolling to bottom
    - Text filtering
    - Copy functionality
    - Monospace font
    """

    def __init__(self, auto_scroll: bool = True, max_lines: int = 1000, **kwargs):
        self.auto_scroll = auto_scroll
        self.max_lines = max_lines
        self._text_buffer = None
        self._text_view = None
        self._scrolled_window = None

        super().__init__("log-container", **kwargs)

    def _init_component(self, **kwargs):
        """Initialize the log container."""
        # Create scrolled window
        self._scrolled_window = Gtk.ScrolledWindow()
        self._scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self._scrolled_window.set_min_content_height(200)

        # Create text view
        self._text_view = Gtk.TextView()
        self._text_view.set_editable(False)
        self._text_view.set_cursor_visible(False)
        self._text_view.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
        self._text_view.add_css_class("monospace")

        # Get text buffer
        self._text_buffer = self._text_view.get_buffer()

        # Add text view to scrolled window
        self._scrolled_window.set_child(self._text_view)

        # Set as main widget
        self.widget = self._scrolled_window

        # Apply styling
        self.add_css_class("ds-log-container")

    def append_text(self, text: str):
        """Append text to the log."""
        end_iter = self._text_buffer.get_end_iter()
        self._text_buffer.insert(end_iter, text)

        # Auto-scroll to bottom if enabled
        if self.auto_scroll:
            end_iter = self._text_buffer.get_end_iter()
            self._text_view.scroll_to_iter(end_iter, 0.0, False, 0.0, 0.0)

    def clear_text(self):
        """Clear all text from the log."""
        self._text_buffer.set_text("")

    def get_text(self) -> str:
        """Get all text from the log."""
        start_iter = self._text_buffer.get_start_iter()
        end_iter = self._text_buffer.get_end_iter()
        return self._text_buffer.get_text(start_iter, end_iter, False)

    def set_text(self, text: str):
        """Set the log text."""
        self._text_buffer.set_text(text)

        # Auto-scroll to bottom if enabled
        if self.auto_scroll:
            end_iter = self._text_buffer.get_end_iter()
            self._text_view.scroll_to_iter(end_iter, 0.0, False, 0.0, 0.0)
