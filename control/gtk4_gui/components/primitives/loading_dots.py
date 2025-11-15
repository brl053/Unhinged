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


class LoadingDots(AdwComponentBase):
    """
    Triple dot wave loading animation component.

    Features:
    - CSS wave animation with customizable timing
    - Motion token integration (150ms-300ms)
    - Gtk.Spinner fallback for accessibility
    - Reduced motion preference support
    - Semantic styling with design system
    """

    __gsignals__ = {
        "animation-complete": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(
        self,
        size: str = "normal",  # "small", "normal", "large"
        speed: str = "normal",  # "slow", "normal", "fast"
        color: str = "primary",  # "primary", "secondary", "muted"
        **kwargs,
    ):
        self.size = size
        self.speed = speed
        self.color = color
        self._dots = []
        self._spinner = None
        self._use_fallback = False

        super().__init__("loading-dots", **kwargs)

    def _init_component(self, **kwargs):
        """Initialize the loading dots component."""
        # Check for reduced motion preference
        self._check_motion_preference()

        if self._use_fallback:
            self._create_spinner_fallback()
        else:
            self._create_dot_animation()

        # Apply styling
        self._apply_loading_styling()

    def _check_motion_preference(self):
        """Check if user prefers reduced motion."""
        # In a real implementation, this would check system settings
        # For now, we'll use an environment variable or default to false
        import os

        self._use_fallback = os.environ.get("PREFER_REDUCED_MOTION", "0") == "1"

    def _create_spinner_fallback(self):
        """Create Gtk.Spinner fallback for accessibility."""
        self.widget = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.widget.set_halign(Gtk.Align.CENTER)
        self.widget.set_valign(Gtk.Align.CENTER)

        self._spinner = Gtk.Spinner()
        self._spinner.set_spinning(True)

        # Size the spinner based on size parameter
        if self.size == "small":
            self._spinner.set_size_request(16, 16)
        elif self.size == "large":
            self._spinner.set_size_request(32, 32)
        else:
            self._spinner.set_size_request(24, 24)

        self.widget.append(self._spinner)

    def _create_dot_animation(self):
        """Create the triple dot wave animation."""
        self.widget = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        self.widget.set_halign(Gtk.Align.CENTER)
        self.widget.set_valign(Gtk.Align.CENTER)

        # Create three dots
        for i in range(3):
            dot = Gtk.Label()
            dot.set_text("●")
            dot.add_css_class("ds-loading-dot")
            dot.add_css_class(f"ds-loading-dot-{i + 1}")  # For animation delay
            self._dots.append(dot)
            self.widget.append(dot)

        # Set accessibility
        self.widget.set_accessible_role(Gtk.AccessibleRole.PROGRESS_BAR)
        self.widget.update_property([Gtk.AccessibleProperty.LABEL], ["Loading"])

    def _apply_loading_styling(self):
        """Apply loading animation styling."""
        self.widget.add_css_class("ds-loading-dots")
        self.widget.add_css_class(f"ds-loading-{self.size}")
        self.widget.add_css_class(f"ds-loading-{self.speed}")
        self.widget.add_css_class(f"ds-loading-{self.color}")

    def start_animation(self):
        """Start the loading animation."""
        if self._spinner:
            self._spinner.set_spinning(True)
        else:
            self.widget.add_css_class("ds-loading-active")

    def stop_animation(self):
        """Stop the loading animation."""
        if self._spinner:
            self._spinner.set_spinning(False)
        else:
            self.widget.remove_css_class("ds-loading-active")

        self.emit("animation-complete")

    def set_speed(self, speed: str):
        """Change animation speed."""
        if self.speed != speed:
            self.widget.remove_css_class(f"ds-loading-{self.speed}")
            self.speed = speed
            self.widget.add_css_class(f"ds-loading-{self.speed}")
