"""
@llm-doc Status Container Components
@llm-version 1.0.0
@llm-date 2025-11-15

StatusCard and ServicePanel components for displaying status information
with icons, actions, and status-based styling.
"""


import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gtk, Pango

from .base import AdwComponentBase


class StatusCard(AdwComponentBase):
    """
    Card component for displaying status information.

    Features:
    - Status icon and title
    - Optional subtitle and description
    - Action buttons
    - Status-based styling
    """

    def __init__(
        self,
        title: str,
        status: str = "neutral",
        subtitle: str | None = None,
        description: str | None = None,
        icon_name: str | None = None,
        **kwargs,
    ):
        self.title = title
        self.status = status
        self.subtitle = subtitle
        self.description = description
        self.icon_name = icon_name
        self._action_buttons = []

        super().__init__("status-card", **kwargs)

    def _init_component(self, **kwargs):
        """Initialize the status card."""
        # Create main card
        self.widget = Adw.PreferencesGroup()

        # Create status row
        self._status_row = Adw.ActionRow()
        self._status_row.set_title(self.title)

        if self.subtitle:
            self._status_row.set_subtitle(self.subtitle)

        # Add icon if provided
        if self.icon_name:
            icon = Gtk.Image.new_from_icon_name(self.icon_name)
            self._status_row.add_prefix(icon)

        self.widget.add(self._status_row)

        # Add description if provided
        if self.description:
            desc_row = Adw.ActionRow()
            desc_label = Gtk.Label(label=self.description)
            desc_label.set_wrap(True)
            desc_label.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
            desc_label.add_css_class("caption")
            desc_row.set_child(desc_label)
            self.widget.add(desc_row)

        # Apply status styling
        self._apply_status_styling()

    def _apply_status_styling(self):
        """Apply styling based on status."""
        # Status-based CSS classes
        status_classes = {
            "success": "success",
            "warning": "warning",
            "error": "error",
            "info": "accent",
            "neutral": "",
        }

        css_class = status_classes.get(self.status, "")
        if css_class:
            self.widget.add_css_class(css_class)

        self.add_css_class(f"ds-status-{self.status}")

    def add_action_button(self, button: Gtk.Widget):
        """Add an action button to the card."""
        self._action_buttons.append(button)
        self._status_row.add_suffix(button)

    def set_title(self, title: str):
        """Update card title."""
        self.title = title
        self._status_row.set_title(title)

    def set_subtitle(self, subtitle: str | None):
        """Update card subtitle."""
        self.subtitle = subtitle
        self._status_row.set_subtitle(subtitle or "")

    def set_status(self, status: str):
        """Update card status."""
        # Remove old status class
        old_class = f"ds-status-{self.status}"
        self.remove_css_class(old_class)

        self.status = status
        self._apply_status_styling()


class ServicePanel(AdwComponentBase):
    """
    Panel for displaying service information and controls.

    Features:
    - Service name and status
    - Health indicator
    - Control buttons
    - Expandable details
    """

    def __init__(
        self,
        service_name: str,
        service_status: str = "unknown",
        port: int | None = None,
        health_method: str | None = None,
        **kwargs,
    ):
        self.service_name = service_name
        self.service_status = service_status
        self.port = port
        self.health_method = health_method
        self._expandable_row = None
        self._details_group = None

        super().__init__("service-panel", **kwargs)

    def _init_component(self, **kwargs):
        """Initialize the service panel."""
        # Create expandable row
        self._expandable_row = Adw.ExpanderRow()
        self._expandable_row.set_title(self.service_name)

        # Set status subtitle
        self._update_status_display()

        # Add status icon
        self._status_icon = Gtk.Image()
        self._update_status_icon()
        self._expandable_row.add_prefix(self._status_icon)

        # Create details group for expanded content
        self._details_group = Adw.PreferencesGroup()

        # Add port information
        if self.port:
            port_row = Adw.ActionRow()
            port_row.set_title("Port")
            port_row.set_subtitle(str(self.port))
            self._details_group.add(port_row)

        # Add health method information
        if self.health_method:
            health_row = Adw.ActionRow()
            health_row.set_title("Health Check")
            health_row.set_subtitle(self.health_method)
            self._details_group.add(health_row)

        # Create main container
        self.widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.widget.append(self._expandable_row)
        self.widget.append(self._details_group)

        # Apply styling
        self.add_css_class("ds-service-panel")

    def _update_status_display(self):
        """Update the status display."""
        status_text = self.service_status.replace("-", " ").title()
        self._expandable_row.set_subtitle(status_text)

    def _update_status_icon(self):
        """Update the status icon."""
        if self.service_status == "running":
            icon_name = "emblem-ok-symbolic"
            css_class = "success"
        elif self.service_status == "stopped":
            icon_name = "process-stop-symbolic"
            css_class = "error"
        elif self.service_status == "starting":
            icon_name = "content-loading-symbolic"
            css_class = "warning"
        else:
            icon_name = "dialog-question-symbolic"
            css_class = "neutral"

        self._status_icon.set_from_icon_name(icon_name)

        # Remove old status classes
        for status in ["success", "error", "warning", "neutral"]:
            self._status_icon.remove_css_class(status)

        self._status_icon.add_css_class(css_class)

    def set_service_status(self, status: str):
        """Update service status."""
        self.service_status = status
        self._update_status_display()
        self._update_status_icon()

    def add_action_button(self, button: Gtk.Widget):
        """Add an action button to the service panel."""
        self._expandable_row.add_suffix(button)
