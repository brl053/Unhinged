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

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('Gdk', '4.0')

from typing import Any

from gi.repository import Adw, Gdk, Gio, GLib, GObject, Gtk, Pango

from ..base import AdwComponentBase, ComponentBase
from .action_button import ActionButton

logger = logging.getLogger(__name__)




class CopyButton(ActionButton):
    """
    Generic copy-paste component that extends ActionButton.

    Features:
    - Automatic content detection from various sources
    - Clipboard integration with toast notifications
    - Composable design for use with other components
    - Icon and text support
    - Success/error feedback
    """

    __gsignals__ = {
        'copy-success': (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        'copy-error': (GObject.SignalFlags.RUN_FIRST, None, (str,)),
    }

    def __init__(self,
                 content: str = "",
                 content_source: callable = None,  # Function to get content dynamically
                 label: str = "Copy",
                 icon_name: str = "edit-copy-symbolic",
                 success_message: str = "Copied to clipboard",
                 error_message: str = "Failed to copy",
                 **kwargs):
        self.content = content
        self.content_source = content_source
        self.success_message = success_message
        self.error_message = error_message
        self._original_label = label
        self._original_icon = icon_name

        # Initialize with copy functionality
        super().__init__(
            label=label,
            icon_name=icon_name,
            **kwargs
        )

        # Connect to our own clicked signal to handle copy
        self.connect('clicked', self._on_copy_clicked)

    def _on_copy_clicked(self, button):
        """Handle copy button click."""
        try:
            # Get content to copy
            content_to_copy = self._get_content()

            if not content_to_copy:
                self._show_error("No content to copy")
                return

            # Get clipboard from the window
            clipboard = self._get_clipboard()
            if not clipboard:
                self._show_error("Clipboard not available")
                return

            # Copy to clipboard
            clipboard.set(content_to_copy)

            # Show success feedback
            self._show_success(content_to_copy)

        except Exception as e:
            self._show_error(f"Copy failed: {str(e)}")

    def _get_content(self) -> str:
        """Get content to copy from various sources."""
        if self.content_source and callable(self.content_source):
            try:
                return str(self.content_source())
            except Exception:
                pass

        return self.content or ""

    def _get_clipboard(self):
        """Get clipboard from the window hierarchy."""
        # Walk up the widget hierarchy to find a window
        widget = self.widget
        while widget:
            if isinstance(widget, Gtk.Window):
                return widget.get_clipboard()
            widget = widget.get_parent()

        # Fallback to default display clipboard
        try:
            display = Gdk.Display.get_default()
            if display:
                return display.get_clipboard()
        except:
            pass

        return None

    def _show_success(self, content: str):
        """Show success feedback."""
        # Temporarily change button appearance
        self._show_feedback("✓", "emblem-ok-symbolic", "success")

        # Emit success signal
        self.emit('copy-success', content)
        self.trigger_action('copy-success', content)

        # Show toast if possible
        self._show_toast(self.success_message)

    def _show_error(self, error: str):
        """Show error feedback."""
        # Temporarily change button appearance
        self._show_feedback("✗", "dialog-error-symbolic", "error")

        # Emit error signal
        self.emit('copy-error', error)
        self.trigger_action('copy-error', error)

        # Show toast if possible
        self._show_toast(f"{self.error_message}: {error}")

    def _show_feedback(self, label: str, icon: str, style: str):
        """Show temporary visual feedback."""
        # Change appearance temporarily
        original_style = self.style
        self.set_label(label)
        self.set_icon_name(icon)
        self.set_style(style)

        # Reset after delay
        GLib.timeout_add(1500, self._reset_appearance, original_style)

    def _reset_appearance(self, original_style: str):
        """Reset button to original appearance."""
        self.set_label(self._original_label)
        self.set_icon_name(self._original_icon)
        self.set_style(original_style)
        return False  # Don't repeat timeout

    def _show_toast(self, message: str):
        """Show toast notification if possible."""
        # Walk up to find a window that might have toast capability
        widget = self.widget
        while widget:
            if hasattr(widget, 'show_toast'):
                widget.show_toast(message)
                return
            widget = widget.get_parent()

        # Fallback: print to console (for debugging)
        print(f"Toast: {message}")

    def set_content(self, content: str):
        """Update content to copy."""
        self.content = content

    def set_content_source(self, source: callable):
        """Update content source function."""
        self.content_source = source
