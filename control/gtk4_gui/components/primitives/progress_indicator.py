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

logger = logging.getLogger(__name__)




class ProgressIndicator(ComponentBase):
    """
    Progress indicator with semantic styling and optional text.
    
    Supports determinate and indeterminate progress.
    """

    def __init__(self,
                 progress: float = 0.0,
                 text: str | None = None,
                 show_percentage: bool = False,
                 **kwargs):
        self.progress = progress
        self.text = text
        self.show_percentage = show_percentage
        self._progress_bar = None
        self._label = None

        super().__init__("progress-indicator", **kwargs)

    def _init_component(self, **kwargs):
        """Initialize the progress indicator."""
        # Create container
        self.widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)

        # Create progress bar
        self._progress_bar = Gtk.ProgressBar()
        self._progress_bar.set_fraction(self.progress)
        self.widget.append(self._progress_bar)

        # Create optional label
        if self.text or self.show_percentage:
            self._label = Gtk.Label()
            self._label.add_css_class("caption")
            self.widget.append(self._label)
            self._update_label()

        # Apply styling
        self.add_css_class("ds-progress-indicator")

    def _update_label(self):
        """Update the progress label."""
        if not self._label:
            return

        label_text = ""
        if self.text:
            label_text = self.text

        if self.show_percentage:
            percentage = int(self.progress * 100)
            if label_text:
                label_text += f" ({percentage}%)"
            else:
                label_text = f"{percentage}%"

        self._label.set_label(label_text)

    def set_progress(self, progress: float):
        """Set progress value (0.0 to 1.0)."""
        self.progress = max(0.0, min(1.0, progress))
        self._progress_bar.set_fraction(self.progress)
        self._update_label()

    def set_text(self, text: str | None):
        """Set progress text."""
        self.text = text
        self._update_label()

    def pulse(self):
        """Pulse the progress bar for indeterminate progress."""
        self._progress_bar.pulse()

    def set_indeterminate(self, indeterminate: bool):
        """Set indeterminate mode."""
        if indeterminate:
            self._progress_bar.set_fraction(0.0)
            self._progress_bar.pulse()
        else:
            self._progress_bar.set_fraction(self.progress)
