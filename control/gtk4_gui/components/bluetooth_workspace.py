"""
@llm-doc Bluetooth Workspace Component for Unhinged Desktop Application
@llm-version 1.0.0
@llm-date 2025-01-26
@llm-author Unhinged Team

## Overview
Advanced Bluetooth management workspace with two separate tables:
1. Registered Devices - Devices already known to the system (paired/connected)
2. Discovering Devices - Devices currently being discovered (registration entry point)

## Features
- Continuous discovery loop while workspace is open
- Separate tables for registered vs discovering devices
- Force Grab feature to steal headphones from other devices
- Event framework integration for all operations
- Session-based logging

## Architecture
- Extends AdwComponentBase for consistency
- Uses BluetoothTable as foundation
- Adds discovery management and force grab functionality
- Integrates with event framework for status tracking

@llm-principle Clear separation between registered and discovering devices
@llm-culture Honest device state representation
"""

import gi
import logging
from typing import Optional, List

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GLib

logger = logging.getLogger(__name__)


class BluetoothWorkspace:
    """
    @llm-doc Advanced Bluetooth management workspace
    
    Manages Bluetooth device discovery and connection with two separate tables:
    - Registered Devices: Devices already paired/connected
    - Discovering Devices: Devices currently discoverable
    
    Provides Force Grab feature to disconnect from other devices and connect to desktop.
    """

    def __init__(self, parent_app=None, session_logger=None):
        """
        Initialize Bluetooth workspace.
        
        Args:
            parent_app: Reference to parent application
            session_logger: Session logger for event tracking
        """
        self.app = parent_app
        self.session_logger = session_logger
        self.is_active = False
        self.discovery_timeout_id = None
        self.discovery_active = False
        
        # Device lists
        self.registered_devices = []
        self.discovering_devices = []
        
        # UI Components
        self.registered_table = None
        self.discovering_table = None
        self.discovery_status_label = None
        self.registered_status_label = None
        
        logger.info("Bluetooth workspace initialized")
        self._log_event("WORKSPACE_INIT", "Bluetooth workspace created")

    def create_content(self) -> Gtk.Widget:
        """
        Create the workspace content with two tables.
        
        Returns:
            Gtk.Widget: The root widget for the workspace
        """
        try:
            # Create main container
            workspace_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
            workspace_box.set_vexpand(True)
            workspace_box.set_hexpand(True)
            
            # Create notebook for tabs
            notebook = Gtk.Notebook()
            notebook.set_vexpand(True)
            notebook.set_hexpand(True)
            
            # Tab 1: Registered Devices
            registered_page = self._create_registered_devices_page()
            notebook.append_page(registered_page, Gtk.Label(label="Registered Devices"))
            
            # Tab 2: Discovering Devices
            discovering_page = self._create_discovering_devices_page()
            notebook.append_page(discovering_page, Gtk.Label(label="Discovering"))
            
            workspace_box.append(notebook)
            
            self._log_event("WORKSPACE_CREATED", "Bluetooth workspace UI created")
            return workspace_box
            
        except Exception as e:
            logger.error(f"Failed to create workspace content: {e}")
            self._log_event("WORKSPACE_ERROR", f"Failed to create content: {e}")
            
            # Return error widget
            error_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
            error_label = Gtk.Label(label=f"Error: {str(e)}")
            error_box.append(error_label)
            return error_box

    def _create_registered_devices_page(self) -> Gtk.Widget:
        """
        Create the registered devices page with device list.

        Returns:
            Gtk.Widget: Page widget
        """
        page_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        page_box.set_margin_top(12)
        page_box.set_margin_bottom(12)
        page_box.set_margin_start(12)
        page_box.set_margin_end(12)
        page_box.set_vexpand(True)
        page_box.set_hexpand(True)

        # Status label
        self.registered_status_label = Gtk.Label(label="Loading registered devices...")
        self.registered_status_label.add_css_class("ds-text-caption")
        page_box.append(self.registered_status_label)

        # Create scrolled window for device list
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_hexpand(True)
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        # Create list box for devices
        self.registered_table = Gtk.ListBox()
        self.registered_table.set_selection_mode(Gtk.SelectionMode.NONE)
        self.registered_table.add_css_class("ds-device-list")
        scrolled.set_child(self.registered_table)

        page_box.append(scrolled)

        return page_box

    def _create_discovering_devices_page(self) -> Gtk.Widget:
        """
        Create the discovering devices page with device list.

        Returns:
            Gtk.Widget: Page widget
        """
        page_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        page_box.set_margin_top(12)
        page_box.set_margin_bottom(12)
        page_box.set_margin_start(12)
        page_box.set_margin_end(12)
        page_box.set_vexpand(True)
        page_box.set_hexpand(True)

        # Status label
        self.discovery_status_label = Gtk.Label(label="Scanning for devices...")
        self.discovery_status_label.add_css_class("ds-text-caption")
        page_box.append(self.discovery_status_label)

        # Create scrolled window for device list
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_hexpand(True)
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        # Create list box for devices
        self.discovering_table = Gtk.ListBox()
        self.discovering_table.set_selection_mode(Gtk.SelectionMode.NONE)
        self.discovering_table.add_css_class("ds-device-list")
        scrolled.set_child(self.discovering_table)

        page_box.append(scrolled)

        return page_box

    def on_ready(self):
        """
        Called when workspace is displayed.
        Starts continuous discovery loop.
        """
        self.is_active = True
        logger.info("Bluetooth workspace ready - starting discovery loop")
        self._log_event("WORKSPACE_READY", "Bluetooth workspace is now active")
        self._start_discovery_loop()

    def on_cleanup(self):
        """
        Called when workspace is closed.
        Stops discovery loop and cleans up resources.
        """
        self.is_active = False
        logger.info("Bluetooth workspace cleanup - stopping discovery loop")
        self._log_event("WORKSPACE_CLEANUP", "Bluetooth workspace cleaned up")
        self._stop_discovery_loop()

    def _start_discovery_loop(self):
        """Start continuous Bluetooth device discovery."""
        if self.discovery_timeout_id:
            GLib.source_remove(self.discovery_timeout_id)
        
        self.discovery_active = True
        self._log_event("DISCOVERY_STARTED", "Continuous discovery loop started")
        
        # Start discovery immediately, then repeat every 3 seconds
        self._perform_discovery()
        self.discovery_timeout_id = GLib.timeout_add_seconds(3, self._perform_discovery)

    def _stop_discovery_loop(self):
        """Stop continuous Bluetooth device discovery."""
        if self.discovery_timeout_id:
            GLib.source_remove(self.discovery_timeout_id)
            self.discovery_timeout_id = None
        
        self.discovery_active = False
        self._log_event("DISCOVERY_STOPPED", "Continuous discovery loop stopped")

    def _perform_discovery(self) -> bool:
        """
        Perform one discovery cycle.

        Returns:
            bool: True to continue loop, False to stop
        """
        if not self.is_active:
            return False

        try:
            import sys
            from pathlib import Path
            sys.path.append(str(Path(__file__).parent.parent))
            from bluetooth_monitor import BluetoothMonitor

            monitor = BluetoothMonitor()

            # Get registered devices (paired)
            self.registered_devices = monitor.get_devices(include_unpaired=False)

            # Get discovering devices (unpaired, discoverable)
            self.discovering_devices = monitor.get_devices(include_unpaired=True)

            # Update status labels
            if self.registered_status_label:
                self.registered_status_label.set_text(
                    f"Found {len(self.registered_devices)} registered device(s)"
                )

            if self.discovery_status_label:
                self.discovery_status_label.set_text(
                    f"Found {len(self.discovering_devices)} discoverable device(s)"
                )

            self._log_event("DISCOVERY_CYCLE",
                f"Registered: {len(self.registered_devices)}, Discovering: {len(self.discovering_devices)}")

            # Update device tables
            self._update_device_tables()

        except Exception as e:
            logger.error(f"Discovery cycle failed: {e}")
            self._log_event("DISCOVERY_ERROR", str(e))

        return True  # Continue loop

    def _update_device_tables(self):
        """Update the device tables with current device lists."""
        try:
            from .primitives import BluetoothRow

            # Update registered devices table
            if self.registered_table:
                # Clear existing rows
                while True:
                    row = self.registered_table.get_row_at_index(0)
                    if not row:
                        break
                    self.registered_table.remove(row)

                # Add device rows
                for device in self.registered_devices:
                    try:
                        device_row = BluetoothRow(device)
                        self.registered_table.append(device_row)
                    except Exception as e:
                        logger.error(f"Failed to create row for {device.name}: {e}")

            # Update discovering devices table
            if self.discovering_table:
                # Clear existing rows
                while True:
                    row = self.discovering_table.get_row_at_index(0)
                    if not row:
                        break
                    self.discovering_table.remove(row)

                # Add device rows
                for device in self.discovering_devices:
                    try:
                        device_row = BluetoothRow(device)
                        self.discovering_table.append(device_row)
                    except Exception as e:
                        logger.error(f"Failed to create row for {device.name}: {e}")

        except Exception as e:
            logger.error(f"Failed to update device tables: {e}")

    def force_grab_device(self, device_address: str, device_name: str) -> bool:
        """
        Force grab a Bluetooth device - disconnect from all other devices and connect to desktop.

        Args:
            device_address: MAC address of device to grab
            device_name: Name of device for logging

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            import sys
            from pathlib import Path
            sys.path.append(str(Path(__file__).parent.parent))
            from bluetooth_monitor import BluetoothMonitor

            self._log_event("FORCE_GRAB_STARTED", f"Force grabbing {device_name} ({device_address})")

            monitor = BluetoothMonitor()

            # Get all connected devices to find what this device is connected to
            all_devices = monitor.get_devices(include_unpaired=False)

            # Disconnect from all other devices (simulate disconnecting from phone, tablet, etc.)
            for device in all_devices:
                if device.address != device_address and device.connected:
                    logger.info(f"Disconnecting {device.name} to free up {device_name}")
                    monitor.disconnect_device(device.address)

            # Connect to desktop
            success = monitor.connect_device(device_address)

            if success:
                self._log_event("FORCE_GRAB_SUCCESS", f"Successfully connected to {device_name}")
                logger.info(f"Force grab successful: {device_name}")
            else:
                self._log_event("FORCE_GRAB_FAILED", f"Failed to connect to {device_name}")
                logger.error(f"Force grab failed: {device_name}")

            return success

        except Exception as e:
            logger.error(f"Force grab error: {e}")
            self._log_event("FORCE_GRAB_ERROR", str(e))
            return False

    def _log_event(self, event_type: str, details: str = ""):
        """Log an event through the session logger."""
        if self.session_logger:
            try:
                self.session_logger.log_gui_event(event_type, details)
            except Exception as e:
                logger.error(f"Failed to log event {event_type}: {e}")

    def cleanup(self):
        """Clean up workspace resources."""
        self.on_cleanup()

