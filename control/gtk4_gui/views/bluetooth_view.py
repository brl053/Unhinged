"""
BluetoothView - Bluetooth Management tab extracted from desktop_app.py

This module contains all the Bluetooth device management functionality that was previously
embedded in the monolithic desktop_app.py file.
"""

import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Adw, Gtk


class BluetoothView:
    """Handles the Bluetooth Management tab functionality"""

    def __init__(self, parent_app):
        """Initialize with reference to parent app"""
        self.app = parent_app

        # Bluetooth table reference
        self.bluetooth_table = None

    def create_content(self):
        """Create the Bluetooth tab content with device discovery and management."""
        try:
            # Import BluetoothTable component
            from components.complex import BluetoothTable

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

            # Create BluetoothTable
            self.bluetooth_table = BluetoothTable()

            # Create Bluetooth table group
            table_group = Adw.PreferencesGroup()
            table_group.set_title("Bluetooth Devices")

            # Add BluetoothTable widget to the group
            table_row = Adw.ActionRow()
            table_row.set_child(self.bluetooth_table.get_widget())
            table_group.add(table_row)

            bluetooth_box.append(table_group)

            # Log Bluetooth tab creation
            if hasattr(self.app, 'session_logger') and self.app.session_logger:
                self.app.session_logger.log_gui_event("BLUETOOTH_TAB_CREATED", "Bluetooth tab with BluetoothTable created")

            return bluetooth_box

        except Exception as e:
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

            # Log error
            if hasattr(self.app, 'session_logger') and self.app.session_logger:
                self.app.session_logger.log_gui_event("BLUETOOTH_TAB_ERROR", f"Failed to create Bluetooth tab: {e}")

            return error_box

    def get_bluetooth_table(self):
        """Get reference to the bluetooth table for external access"""
        return self.bluetooth_table

    def cleanup(self):
        """Clean up bluetooth components"""
        try:
            if self.bluetooth_table and hasattr(self.bluetooth_table, 'cleanup'):
                self.bluetooth_table.cleanup()

            # Log cleanup
            if hasattr(self.app, 'session_logger') and self.app.session_logger:
                self.app.session_logger.log_gui_event("BLUETOOTH_CLEANUP", "Bluetooth components cleaned up")

        except Exception as e:
            if hasattr(self.app, 'session_logger') and self.app.session_logger:
                self.app.session_logger.log_gui_event("BLUETOOTH_CLEANUP_ERROR", str(e))
