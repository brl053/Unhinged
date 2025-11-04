"""
@llm-doc BluetoothView - Bluetooth Management Tab
@llm-version 2.0.0
@llm-date 2025-01-26
@llm-author Unhinged Team

Bluetooth device management view with lifecycle management, continuous discovery,
and force grab functionality.

## Features
- Lifecycle management (on_ready, on_cleanup)
- Continuous Bluetooth device discovery
- Two-table architecture (Registered vs Discovering)
- Force Grab feature for stealing headphones
- Event framework integration
- Status stack for operation feedback

@llm-principle Clear lifecycle management for deterministic behavior
@llm-culture Honest device state representation
"""

import gi
import logging

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Adw, Gtk

from views.base import ViewBase
from components.bluetooth_workspace import BluetoothWorkspace
from components.status_stack import StatusStack

logger = logging.getLogger(__name__)


class BluetoothView(ViewBase):
    """
    @llm-doc Bluetooth Management View with Lifecycle Management

    Extends ViewBase to provide lifecycle management for Bluetooth operations.
    Integrates BluetoothWorkspace for device discovery and StatusStack for feedback.
    """

    def __init__(self, parent_app):
        """Initialize with reference to parent app"""
        super().__init__(parent_app, "bluetooth")

        # Bluetooth components
        self.bluetooth_table = None
        self.workspace = None
        self.status_stack = None

    def create_content(self):
        """Create the Bluetooth tab content with device discovery and management."""
        try:
            # Create main content box
            bluetooth_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
            bluetooth_box.set_margin_top(24)
            bluetooth_box.set_margin_bottom(24)
            bluetooth_box.set_margin_start(24)
            bluetooth_box.set_margin_end(24)
            bluetooth_box.set_vexpand(True)
            bluetooth_box.set_hexpand(True)

            # Create header section
            header_group = Adw.PreferencesGroup()
            header_group.set_title("Bluetooth Manager")
            header_group.set_description("Discover, pair, and manage Bluetooth devices")

            # Add header info row
            info_row = Adw.ActionRow()
            info_row.set_title("Device Management")
            info_row.set_subtitle("Scan for devices, manage connections, and configure pairing")

            # Add Bluetooth icon
            bluetooth_icon = Gtk.Image.new_from_icon_name("bluetooth-symbolic")
            bluetooth_icon.set_icon_size(Gtk.IconSize.LARGE)
            bluetooth_icon.add_css_class("accent")
            info_row.add_prefix(bluetooth_icon)

            header_group.add(info_row)
            bluetooth_box.append(header_group)

            # Create status stack at top
            self.status_stack = StatusStack(max_messages=5)
            status_group = Adw.PreferencesGroup()
            status_group.set_title("Operation Status")
            status_group.add(self.status_stack.create_widget())
            bluetooth_box.append(status_group)

            # Create BluetoothWorkspace
            self.workspace = BluetoothWorkspace(
                parent_app=self.app,
                session_logger=self.session_logger
            )
            workspace_content = self.workspace.create_content()

            # Add workspace to a group
            workspace_group = Adw.PreferencesGroup()
            workspace_group.set_title("Bluetooth Devices")
            workspace_group.add(workspace_content)
            bluetooth_box.append(workspace_group)

            # Log Bluetooth tab creation
            self._log_event("BLUETOOTH_TAB_CREATED", "Bluetooth tab with BluetoothWorkspace created")

            return bluetooth_box

        except Exception as e:
            logger.error(f"Failed to create Bluetooth tab: {e}")
            self._log_event("BLUETOOTH_TAB_ERROR", f"Failed to create Bluetooth tab: {e}")

            # Create error fallback
            error_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
            error_box.set_margin_top(24)
            error_box.set_margin_bottom(24)
            error_box.set_margin_start(24)
            error_box.set_margin_end(24)

            error_group = Adw.PreferencesGroup()
            error_group.set_title("Bluetooth Manager Unavailable")
            error_group.set_description("Bluetooth management is not available")

            error_row = Adw.ActionRow()
            error_row.set_title("Error Loading Bluetooth Manager")
            error_row.set_subtitle(f"Error: {str(e)}")

            error_icon = Gtk.Image.new_from_icon_name("dialog-error-symbolic")
            error_icon.add_css_class("error")
            error_row.add_prefix(error_icon)

            error_group.add(error_row)
            error_box.append(error_group)

            return error_box

    def on_ready(self):
        """Called when view is displayed - start discovery loop"""
        super().on_ready()

        try:
            if self.workspace:
                self.workspace.on_ready()
                logger.info("Bluetooth workspace ready - discovery loop started")
        except Exception as e:
            logger.error(f"Failed to start workspace: {e}")
            self._log_event("WORKSPACE_START_ERROR", str(e))

    def on_cleanup(self):
        """Called when view is closed - stop discovery loop"""
        try:
            if self.workspace:
                self.workspace.on_cleanup()
                logger.info("Bluetooth workspace cleanup - discovery loop stopped")
        except Exception as e:
            logger.error(f"Failed to cleanup workspace: {e}")
            self._log_event("WORKSPACE_CLEANUP_ERROR", str(e))

        super().on_cleanup()

    def get_bluetooth_table(self):
        """Get reference to the bluetooth table for external access"""
        return self.bluetooth_table

    def get_status_stack(self):
        """Get reference to the status stack for external access"""
        return self.status_stack

    def get_workspace(self):
        """Get reference to the workspace for external access"""
        return self.workspace

    def cleanup(self):
        """Clean up bluetooth components (legacy method for compatibility)"""
        self.on_cleanup()
