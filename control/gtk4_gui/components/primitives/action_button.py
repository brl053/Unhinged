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


class ActionButton(AdwComponentBase):
    """
    Enhanced button component with design system integration.

    Features:
    - Semantic styling (primary, secondary, destructive)
    - Loading states with spinner
    - Icon support
    - Keyboard accessibility
    """

    __gsignals__ = {
        "clicked": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(
        self,
        label: str = "",
        style: str = "primary",
        icon_name: str | None = None,
        **kwargs,
    ):
        self.label = label
        self.style = style
        self.icon_name = icon_name
        self._loading = False
        self._spinner = None
        self._original_child = None

        super().__init__("action-button", **kwargs)

    def _init_component(self, **kwargs):
        """Initialize the button widget."""
        self.widget = Gtk.Button()

        # Set up button content
        self._setup_button_content()

        # Apply styling
        self._apply_button_style()

        # Connect signals
        self.widget.connect("clicked", self._on_clicked)

        # Set accessibility
        if self.label:
            self.widget.set_tooltip_text(self.label)

        # Add ARIA attributes
        self.widget.set_accessible_role(Gtk.AccessibleRole.BUTTON)
        if self.label:
            self.widget.update_property([Gtk.AccessibleProperty.LABEL], [self.label])

    def _setup_button_content(self):
        """Setup button content with optional icon."""
        if self.icon_name:
            # Button with icon and label
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

            icon = Gtk.Image.new_from_icon_name(self.icon_name)
            box.append(icon)

            if self.label:
                label = Gtk.Label(label=self.label)
                box.append(label)

            self.widget.set_child(box)
            self._original_child = box
        else:
            # Text-only button
            self.widget.set_label(self.label)
            self._original_child = None

    def _apply_button_style(self):
        """Apply semantic styling based on button style."""
        style_classes = {
            "primary": "suggested-action",
            "secondary": "",
            "destructive": "destructive-action",
            "flat": "flat",
        }

        css_class = style_classes.get(self.style, "")
        if css_class:
            self.widget.add_css_class(css_class)

        # Add design system class
        self.add_css_class(f"ds-action-{self.style}")

    def _on_clicked(self, button):
        """Handle button click."""
        if not self._loading:
            self.emit("clicked")
            self.trigger_action("clicked")

    def set_loading(self, loading: bool):
        """Set loading state with spinner."""
        if self._loading == loading:
            return

        self._loading = loading

        if loading:
            # Show spinner
            self._spinner = Gtk.Spinner()
            self._spinner.set_spinning(True)
            self.widget.set_child(self._spinner)
            self.widget.set_sensitive(False)
        else:
            # Restore original content
            if self._original_child:
                self.widget.set_child(self._original_child)
            else:
                self.widget.set_label(self.label)
            self.widget.set_sensitive(True)
            self._spinner = None

    def set_label(self, label: str):
        """Update button label."""
        self.label = label
        if not self._loading:
            if self._original_child is None:
                self.widget.set_label(label)
            else:
                self._setup_button_content()
