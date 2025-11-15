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

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')


from gi.repository import Adw, GLib, GObject, Gtk

from ..base import AdwComponentBase
from ..containers import LogContainer, ServicePanel, StatusCard
from ..primitives import ActionButton
from ..primitives import HardwareInfoRow




class ServiceRow(AdwComponentBase):
    """
    Complete service status row with controls and status display.
    
    Features:
    - Service name and status
    - Health indicator with method
    - Start/stop/restart controls
    - Expandable details
    """

    __gsignals__ = {
        'action-requested': (GObject.SignalFlags.RUN_FIRST, None, (str, str)),
    }

    def __init__(self,
                 service_name: str,
                 service_data: dict,
                 **kwargs):
        self.service_name = service_name
        self.service_data = service_data
        self._service_panel = None
        self._action_buttons = {}

        super().__init__("service-row", **kwargs)

    def _init_component(self, **kwargs):
        """Initialize the service row."""
        # Create service panel
        self._service_panel = ServicePanel(
            service_name=self.service_name,
            service_status="running" if self.service_data.get("running") else "stopped",
            port=self.service_data.get("port"),
            health_method=self.service_data.get("health_method", "unknown")
        )

        # Add action buttons
        self._create_action_buttons()

        # Set main widget
        self.widget = self._service_panel.get_widget()

        # Apply styling
        self.add_css_class("ds-service-row")

    def _create_action_buttons(self):
        """Create action buttons for the service."""
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)

        # Start/Stop button
        if self.service_data.get("running"):
            stop_button = ActionButton(
                label="Stop",
                style="destructive",
                icon_name="process-stop-symbolic"
            )
            stop_button.connect('clicked', lambda b: self._on_action_clicked("stop"))
            self._action_buttons["stop"] = stop_button
            button_box.append(stop_button.get_widget())
        else:
            start_button = ActionButton(
                label="Start",
                style="primary",
                icon_name="media-playback-start-symbolic"
            )
            start_button.connect('clicked', lambda b: self._on_action_clicked("start"))
            self._action_buttons["start"] = start_button
            button_box.append(start_button.get_widget())

        # Restart button
        restart_button = ActionButton(
            label="Restart",
            style="secondary",
            icon_name="view-refresh-symbolic"
        )
        restart_button.connect('clicked', lambda b: self._on_action_clicked("restart"))
        self._action_buttons["restart"] = restart_button
        button_box.append(restart_button.get_widget())

        # Add button box to service panel
        self._service_panel.add_action_button(button_box)

    def _on_action_clicked(self, action: str):
        """Handle action button clicks."""
        self.emit('action-requested', self.service_name, action)

    def update_service_data(self, service_data: dict):
        """Update service data and refresh display."""
        self.service_data = service_data

        # Update status
        status = "running" if service_data.get("running") else "stopped"
        self._service_panel.set_service_status(status)

        # Recreate action buttons if status changed
        # This is a simplified approach - in production you'd update buttons more efficiently
        self._create_action_buttons()
