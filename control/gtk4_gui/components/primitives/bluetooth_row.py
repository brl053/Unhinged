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

from gi.repository import Gio, Gtk

from .hardware_info_row import HardwareInfoRow

logger = logging.getLogger(__name__)


class BluetoothRow(HardwareInfoRow):
    """
    Individual Bluetooth device display extending hardware row pattern.

    Features:
    - Device data display (name, address, type, connection status)
    - Connection/pairing action controls
    - Device type icons and status indicators
    - Real-time connection state updates
    """

    def __init__(self, device_info, **kwargs):
        # Import required modules
        import sys
        from pathlib import Path

        sys.path.append(str(Path(__file__).parent.parent))

        self.device_info = device_info
        self.action_menu = None
        self.connection_button = None
        self.status_icon = None

        # Determine hardware type and status from device info
        hardware_type = "bluetooth"
        status = self._determine_status()

        # Create title and subtitle
        title = device_info.name or device_info.alias or "Unknown Device"
        subtitle = f"{device_info.address} • {device_info.device_type.title()}"

        # Add connection status to subtitle
        if device_info.connected:
            subtitle += " • Connected"
        elif device_info.paired:
            subtitle += " • Paired"
        else:
            subtitle += " • Discovered"

        super().__init__(
            title=title,
            subtitle=subtitle,
            hardware_type=hardware_type,
            status=status,
            details=self._create_device_details(),
            icon_name=self._get_device_icon(),
            **kwargs,
        )

    def _determine_status(self) -> str:
        """Determine device status for styling."""
        if self.device_info.blocked:
            return "error"
        elif self.device_info.connected:
            return "success"
        elif self.device_info.paired:
            return "warning"
        else:
            return "normal"

    def _get_device_icon(self) -> str:
        """Get appropriate icon for device type."""
        device_type_icons = {
            "computer": "computer-symbolic",
            "phone": "phone-symbolic",
            "audio": "audio-headphones-symbolic",
            "peripheral": "input-mouse-symbolic",
            "imaging": "camera-photo-symbolic",
            "wearable": "preferences-system-symbolic",
            "toy": "applications-games-symbolic",
            "health": "applications-science-symbolic",
            "unknown": "bluetooth-symbolic",
        }

        return device_type_icons.get(self.device_info.device_type, "bluetooth-symbolic")

    def _create_device_details(self) -> dict[str, Any]:
        """Create detailed device information."""
        details = {
            "Address": self.device_info.address,
            "Type": self.device_info.device_type.title(),
            "Paired": "Yes" if self.device_info.paired else "No",
            "Connected": "Yes" if self.device_info.connected else "No",
            "Trusted": "Yes" if self.device_info.trusted else "No",
            "Blocked": "Yes" if self.device_info.blocked else "No",
        }

        if self.device_info.rssi is not None:
            details["Signal Strength"] = f"{self.device_info.rssi} dBm"

        if self.device_info.uuids:
            details["Services"] = f"{len(self.device_info.uuids)} available"

        return details

    def _init_component(self, **kwargs):
        """Initialize the Bluetooth device row."""
        # Call parent initialization
        super()._init_component(**kwargs)

        # Add Bluetooth-specific action controls
        self._add_bluetooth_actions()

        # Apply Bluetooth-specific styling
        self.add_css_class("ds-bluetooth-row")

        # Add connection status styling
        if self.device_info.connected:
            self.add_css_class("bluetooth-connected")
        elif self.device_info.paired:
            self.add_css_class("bluetooth-paired")
        else:
            self.add_css_class("bluetooth-discovered")

    def _add_bluetooth_actions(self):
        """Add Bluetooth-specific action controls."""
        # Create action button box
        action_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        # Connection/Pairing button
        if self.device_info.connected:
            self.connection_button = Gtk.Button()
            self.connection_button.set_label("Disconnect")
            self.connection_button.set_icon_name(
                "network-wireless-disconnected-symbolic"
            )
            self.connection_button.add_css_class("destructive-action")
            self.connection_button.connect("clicked", self._on_disconnect_clicked)
        elif self.device_info.paired:
            self.connection_button = Gtk.Button()
            self.connection_button.set_label("Connect")
            self.connection_button.set_icon_name("network-wireless-symbolic")
            self.connection_button.add_css_class("suggested-action")
            self.connection_button.connect("clicked", self._on_connect_clicked)
        else:
            self.connection_button = Gtk.Button()
            self.connection_button.set_label("Pair")
            self.connection_button.set_icon_name("bluetooth-symbolic")
            self.connection_button.add_css_class("suggested-action")
            self.connection_button.connect("clicked", self._on_pair_clicked)

        action_box.append(self.connection_button)

        # Action menu button
        self.action_menu = Gtk.MenuButton()
        self.action_menu.set_icon_name("view-more-symbolic")
        self.action_menu.set_tooltip_text("Device actions")

        # Create action menu
        menu_model = Gio.Menu()

        if self.device_info.paired:
            if not self.device_info.trusted:
                menu_model.append("Trust Device", "bluetooth.trust")
            else:
                menu_model.append("Untrust Device", "bluetooth.untrust")

            menu_model.append("Remove Device", "bluetooth.remove")

        if not self.device_info.blocked:
            menu_model.append("Block Device", "bluetooth.block")
        else:
            menu_model.append("Unblock Device", "bluetooth.unblock")

        menu_model.append("Device Info", "bluetooth.info")

        self.action_menu.set_menu_model(menu_model)
        action_box.append(self.action_menu)

        # Add action box to the row
        if hasattr(self, "_main_row"):
            self._main_row.add_suffix(action_box)

    def _on_connect_clicked(self, button):
        """Handle connect button click."""
        import sys
        from pathlib import Path

        sys.path.append(str(Path(__file__).parent.parent))

        from bluetooth_monitor import BluetoothMonitor

        logger.info(
            f"🔵 Connecting to {self.device_info.name} ({self.device_info.address})"
        )

        # Disable button during operation
        button.set_sensitive(False)
        button.set_label("Connecting...")

        try:
            monitor = BluetoothMonitor()
            success = monitor.connect_device(self.device_info.address)

            if success:
                logger.info(f"✅ Successfully connected to {self.device_info.name}")
                # Update device info to reflect connected state
                self.device_info.connected = True
                self.update_device_data(self.device_info)
            else:
                logger.error(f"❌ Failed to connect to {self.device_info.name}")
                button.set_label("Connect")
                button.set_sensitive(True)

        except Exception as e:
            logger.error(f"❌ Connection error: {e}")
            button.set_label("Connect")
            button.set_sensitive(True)

    def _on_disconnect_clicked(self, button):
        """Handle disconnect button click."""
        import sys
        from pathlib import Path

        sys.path.append(str(Path(__file__).parent.parent))

        from bluetooth_monitor import BluetoothMonitor

        logger.info(
            f"🔵 Disconnecting from {self.device_info.name} ({self.device_info.address})"
        )

        # Disable button during operation
        button.set_sensitive(False)
        button.set_label("Disconnecting...")

        try:
            monitor = BluetoothMonitor()
            success = monitor.disconnect_device(self.device_info.address)

            if success:
                logger.info(
                    f"✅ Successfully disconnected from {self.device_info.name}"
                )
                # Update device info to reflect disconnected state
                self.device_info.connected = False
                self.update_device_data(self.device_info)
            else:
                logger.error(f"❌ Failed to disconnect from {self.device_info.name}")
                button.set_label("Disconnect")
                button.set_sensitive(True)

        except Exception as e:
            logger.error(f"❌ Disconnection error: {e}")
            button.set_label("Disconnect")
            button.set_sensitive(True)

    def _on_pair_clicked(self, button):
        """Handle pair button click."""
        import sys
        from pathlib import Path

        sys.path.append(str(Path(__file__).parent.parent))

        from bluetooth_monitor import BluetoothMonitor

        logger.info(
            f"🔵 Pairing with {self.device_info.name} ({self.device_info.address})"
        )

        # Disable button during operation
        button.set_sensitive(False)
        button.set_label("Pairing...")

        try:
            monitor = BluetoothMonitor()
            success = monitor.pair_device(self.device_info.address)

            if success:
                logger.info(f"✅ Successfully paired with {self.device_info.name}")
                # Set device as trusted to enable auto-connect
                monitor.set_trusted(self.device_info.address, True)
                # Update device info to reflect paired state
                self.device_info.paired = True
                self.device_info.trusted = True
                self.update_device_data(self.device_info)
            else:
                logger.error(f"❌ Failed to pair with {self.device_info.name}")
                button.set_label("Pair")
                button.set_sensitive(True)

        except Exception as e:
            logger.error(f"❌ Pairing error: {e}")
            button.set_label("Pair")
            button.set_sensitive(True)

    def update_device_data(self, new_device_info):
        """Update device data and refresh display."""
        old_connected = self.device_info.connected
        old_paired = self.device_info.paired

        self.device_info = new_device_info

        # Update title and subtitle
        title = new_device_info.name or new_device_info.alias or "Unknown Device"
        subtitle = f"{new_device_info.address} • {new_device_info.device_type.title()}"

        if new_device_info.connected:
            subtitle += " • Connected"
        elif new_device_info.paired:
            subtitle += " • Paired"
        else:
            subtitle += " • Discovered"

        # Update the row content
        if hasattr(self, "_main_row"):
            self._main_row.set_title(title)
            self._main_row.set_subtitle(subtitle)

        # Update styling if connection status changed
        if (
            old_connected != new_device_info.connected
            or old_paired != new_device_info.paired
        ):
            # Remove old status classes
            self.remove_css_class("bluetooth-connected")
            self.remove_css_class("bluetooth-paired")
            self.remove_css_class("bluetooth-discovered")

            # Add new status class
            if new_device_info.connected:
                self.add_css_class("bluetooth-connected")
            elif new_device_info.paired:
                self.add_css_class("bluetooth-paired")
            else:
                self.add_css_class("bluetooth-discovered")

            # Update connection button
            self._update_connection_button()

    def _update_connection_button(self):
        """Update connection button based on current state."""
        if not self.connection_button:
            return

        if self.device_info.connected:
            self.connection_button.set_label("Disconnect")
            self.connection_button.set_icon_name(
                "network-wireless-disconnected-symbolic"
            )
            self.connection_button.remove_css_class("suggested-action")
            self.connection_button.add_css_class("destructive-action")
        elif self.device_info.paired:
            self.connection_button.set_label("Connect")
            self.connection_button.set_icon_name("network-wireless-symbolic")
            self.connection_button.remove_css_class("destructive-action")
            self.connection_button.add_css_class("suggested-action")
        else:
            self.connection_button.set_label("Pair")
            self.connection_button.set_icon_name("bluetooth-symbolic")
            self.connection_button.remove_css_class("destructive-action")
            self.connection_button.add_css_class("suggested-action")
