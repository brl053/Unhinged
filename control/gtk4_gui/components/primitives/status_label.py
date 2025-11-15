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


from gi.repository import Gtk, Pango

from ..base import ComponentBase

logger = logging.getLogger(__name__)


class StatusLabel(ComponentBase):
    """
    Label component with semantic status styling.

    Supports status types: success, warning, error, info, neutral
    """

    def __init__(self, text: str = "", status: str = "neutral", **kwargs):
        self.text = text
        self.status = status

        super().__init__("status-label", **kwargs)

    def _init_component(self, **kwargs):
        """Initialize the label widget."""
        self.widget = Gtk.Label(label=self.text)
        self.widget.set_wrap(True)
        self.widget.set_wrap_mode(Pango.WrapMode.WORD_CHAR)

        # Apply status styling
        self._apply_status_style()

    def _apply_status_style(self):
        """Apply styling based on status type."""
        # Remove existing status classes
        for status_type in ["success", "warning", "error", "info", "neutral"]:
            self.widget.remove_css_class(f"status-{status_type}")

        # Add current status class
        self.widget.add_css_class(f"status-{self.status}")
        self.add_css_class(f"ds-status-{self.status}")

    def set_text(self, text: str):
        """Update label text."""
        self.text = text
        self.widget.set_label(text)

    def set_status(self, status: str):
        """Update status type."""
        self.status = status
        self._apply_status_style()
