"""
@llm-doc Complex GTK4 Components
@llm-version 1.0.0
@llm-date 2025-10-28

Complex components that combine multiple elements for comprehensive interfaces:
- LogViewer: Advanced log viewer with filtering and search
- ServiceRow: Complete service status row with controls
- SystemStatus: Overall system status display
- PerformanceIndicator: System performance monitoring display
- ProcessTable: Complete process management interface
- BluetoothTable: Bluetooth device management with discovery
- AudioTable: Audio device management with volume control
"""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")


from gi.repository import Adw, Gtk

from ..base import AdwComponentBase
from ..containers import StatusCard


class SystemStatus(AdwComponentBase):
    """
    Overall system status display with service overview.

    Features:
    - Overall health indicator
    - Service count summary
    - Quick actions
    - Status breakdown
    """

    def __init__(self, **kwargs):
        self._services_data = {}
        self._status_card = None
        self._services_summary = None
        self._quick_actions = None

        super().__init__("system-status", **kwargs)

    def _init_component(self, **kwargs):
        """Initialize the system status display."""
        # Create main container
        self.widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)

        # Create status card
        self._status_card = StatusCard(
            title="System Status",
            status="neutral",
            subtitle="Checking services...",
            icon_name="computer-symbolic",
        )
        self.widget.append(self._status_card.get_widget())

        # Create services summary
        self._services_summary = Adw.PreferencesGroup()
        self._services_summary.set_title("Services Overview")
        self.widget.append(self._services_summary)

        # Apply styling
        self.add_css_class("ds-system-status")

    def update_services(self, services_data: dict):
        """Update system status with services data."""
        self._services_data = services_data

        # Calculate overall status
        total_services = len(services_data)
        running_services = sum(1 for data in services_data.values() if data.get("running"))

        # Update status card
        if running_services == total_services:
            status = "success"
            subtitle = f"All {total_services} services running"
        elif running_services == 0:
            status = "error"
            subtitle = "No services running"
        else:
            status = "warning"
            subtitle = f"{running_services}/{total_services} services running"

        self._status_card.set_status(status)
        self._status_card.set_subtitle(subtitle)

        # Update services summary
        self._update_services_summary()

    def _update_services_summary(self):
        """Update the services summary display."""
        # Clear existing summary
        child = self._services_summary.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self._services_summary.remove(child)
            child = next_child

        # Group services by status
        running = []
        stopped = []

        for name, data in self._services_data.items():
            if data.get("running"):
                running.append(name)
            else:
                stopped.append(name)

        # Add running services
        if running:
            running_row = Adw.ActionRow()
            running_row.set_title("Running Services")
            running_row.set_subtitle(", ".join(running))

            running_icon = Gtk.Image.new_from_icon_name("emblem-ok-symbolic")
            running_icon.add_css_class("success")
            running_row.add_prefix(running_icon)

            self._services_summary.add(running_row)

        # Add stopped services
        if stopped:
            stopped_row = Adw.ActionRow()
            stopped_row.set_title("Stopped Services")
            stopped_row.set_subtitle(", ".join(stopped))

            stopped_icon = Gtk.Image.new_from_icon_name("process-stop-symbolic")
            stopped_icon.add_css_class("error")
            stopped_row.add_prefix(stopped_icon)

            self._services_summary.add(stopped_row)
