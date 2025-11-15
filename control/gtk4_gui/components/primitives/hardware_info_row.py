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

from typing import Any

from gi.repository import Adw, Gtk

from ..base import AdwComponentBase

logger = logging.getLogger(__name__)


class HardwareInfoRow(AdwComponentBase):
    """
    Specialized row component for displaying hardware details.

    Features:
    - Hardware-specific icons and styling
    - Status indicators for hardware health
    - Expandable details for complex hardware info
    - Semantic color coding
    """

    def __init__(
        self,
        title: str = "",
        subtitle: str = "",
        hardware_type: str = "generic",
        status: str = "normal",
        details: dict[str, Any] | None = None,
        icon_name: str | None = None,
        **kwargs,
    ):
        self.title = title
        self.subtitle = subtitle
        self.hardware_type = hardware_type
        self.status = status
        self.details = details or {}
        self.icon_name = icon_name or self._get_default_icon()

        super().__init__("hardware-info-row", **kwargs)

    def _init_component(self, **kwargs):
        """Initialize the hardware info row widget."""
        self.widget = Adw.ActionRow()
        self.widget.set_title(self.title)
        if self.subtitle:
            self.widget.set_subtitle(self.subtitle)

        # Add hardware icon
        self._setup_icon()

        # Add status indicator
        self._setup_status_indicator()

        # Add details if available
        if self.details:
            self._setup_details_button()

        # Apply styling
        self.add_css_class("ds-hardware-info-row")
        self._apply_hardware_styling()

        # Apply status-based styling
        if self.status in ["good", "normal"]:
            self.add_css_class("status-success")
        elif self.status == "warning":
            self.add_css_class("status-warning")
        elif self.status in ["error", "critical"]:
            self.add_css_class("status-error")
        else:
            self.add_css_class("status-info")

        # Add accessibility attributes
        self.widget.set_accessible_role(Gtk.AccessibleRole.LIST_ITEM)
        self.widget.update_property(
            [Gtk.AccessibleProperty.LABEL], [f"{self.hardware_type}: {self.title}"]
        )
        if self.subtitle:
            self.widget.update_property(
                [Gtk.AccessibleProperty.DESCRIPTION], [self.subtitle]
            )

    def _get_default_icon(self) -> str:
        """Get default icon based on hardware type."""
        icon_map = {
            "cpu": "cpu-symbolic",
            "memory": "memory-symbolic",
            "storage": "drive-harddisk-symbolic",
            "gpu": "video-display-symbolic",
            "network": "network-wired-symbolic",
            "motherboard": "computer-symbolic",
            "generic": "emblem-system-symbolic",
        }
        return icon_map.get(self.hardware_type, "emblem-system-symbolic")

    def _setup_icon(self):
        """Setup hardware icon."""
        icon = Gtk.Image.new_from_icon_name(self.icon_name)
        icon.set_icon_size(Gtk.IconSize.LARGE)
        icon.add_css_class(f"hardware-{self.hardware_type}")
        self.widget.add_prefix(icon)

    def _setup_status_indicator(self):
        """Setup status indicator."""
        status_icon = Gtk.Image()
        status_icon.set_icon_size(Gtk.IconSize.NORMAL)

        # Set icon and styling based on status
        if self.status == "good" or self.status == "normal":
            status_icon.set_from_icon_name("emblem-ok-symbolic")
            status_icon.add_css_class("success")
        elif self.status == "warning":
            status_icon.set_from_icon_name("dialog-warning-symbolic")
            status_icon.add_css_class("warning")
        elif self.status == "error" or self.status == "critical":
            status_icon.set_from_icon_name("dialog-error-symbolic")
            status_icon.add_css_class("error")
        else:
            status_icon.set_from_icon_name("dialog-information-symbolic")
            status_icon.add_css_class("info")

        self.widget.add_suffix(status_icon)

    def _setup_details_button(self):
        """Setup details expansion button."""
        details_button = Gtk.Button()
        details_button.set_icon_name("view-more-symbolic")
        details_button.add_css_class("flat")
        details_button.set_tooltip_text("Show details")
        self.connect_signal(details_button, "clicked", self._on_details_clicked)

        self.widget.add_suffix(details_button)

    def _apply_hardware_styling(self):
        """Apply hardware-specific styling."""
        self.add_css_class(f"hardware-{self.hardware_type}")
        self.add_css_class(f"status-{self.status}")

    def _on_details_clicked(self, button):
        """Handle details button click."""
        # Create details dialog or popover
        dialog = Adw.MessageDialog()
        dialog.set_heading(f"{self.title} Details")

        # Format details as text
        details_text = ""
        for key, value in self.details.items():
            formatted_key = key.replace("_", " ").title()
            details_text += f"{formatted_key}: {value}\n"

        dialog.set_body(details_text)
        dialog.add_response("close", "Close")
        dialog.set_default_response("close")

        # Show dialog
        if hasattr(self.widget, "get_root"):
            root = self.widget.get_root()
            if root:
                dialog.set_transient_for(root)

        dialog.present()

    def update_status(self, new_status: str):
        """Update hardware status."""
        self.status = new_status
        self._apply_hardware_styling()
        # Re-setup status indicator
        # Note: In a full implementation, we'd update the existing indicator

    def update_details(self, new_details: dict[str, Any]):
        """Update hardware details."""
        self.details = new_details
