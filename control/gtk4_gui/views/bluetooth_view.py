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

import logging

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gtk
from views.base import ViewBase

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
        """Create the Bluetooth tab content - currently disabled due to D-Bus blocking."""
        # Create main content box
        bluetooth_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        bluetooth_box.set_margin_top(24)
        bluetooth_box.set_margin_bottom(24)
        bluetooth_box.set_margin_start(24)
        bluetooth_box.set_margin_end(24)
        bluetooth_box.set_vexpand(True)
        bluetooth_box.set_hexpand(True)

        # Create disabled notice
        notice_group = Adw.PreferencesGroup()
        notice_group.set_title("Bluetooth Manager")
        notice_group.set_description("Bluetooth functionality")

        notice_row = Adw.ActionRow()
        notice_row.set_title("Bluetooth Tab Disabled")
        notice_row.set_subtitle(
            "Bluetooth device discovery is currently disabled to prevent UI freezing"
        )

        notice_icon = Gtk.Image.new_from_icon_name("dialog-information-symbolic")
        notice_icon.add_css_class("info")
        notice_row.add_prefix(notice_icon)

        notice_group.add(notice_row)
        bluetooth_box.append(notice_group)

        # Log that Bluetooth tab is disabled
        self._log_event(
            "BLUETOOTH_TAB_DISABLED", "Bluetooth tab disabled to prevent D-Bus blocking"
        )

        return bluetooth_box

    def on_ready(self):
        """Called when view is displayed - Bluetooth tab is disabled"""
        super().on_ready()
        # Bluetooth tab is disabled to prevent D-Bus blocking
        logger.info("Bluetooth tab displayed (disabled)")

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
