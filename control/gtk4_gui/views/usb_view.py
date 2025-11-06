#!/usr/bin/env python3
"""
USB Devices View

Displays raw lsusb output with auto-refresh when tab is active.
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GLib, Pango
import logging

logger = logging.getLogger(__name__)


class USBView:
    """View for displaying USB devices using raw lsusb output"""

    def __init__(self, app):
        """Initialize USB view"""
        self.app = app
        self.widget = None
        self.text_view = None
        self.text_buffer = None
        self.refresh_button = None
        self.status_label = None
        self.auto_refresh_toggle = None
        self.auto_refresh_enabled = True
        self.refresh_timeout_id = None
        self.refresh_interval = 3000  # milliseconds
        
        # Import USB monitor
        try:
            from ..handlers.usb_monitor import USBMonitor
        except ImportError:
            from handlers.usb_monitor import USBMonitor
        
        self.usb_monitor = USBMonitor()

    def create_content(self) -> Gtk.Widget:
        """Create the USB view content"""
        try:
            # Main container
            main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
            main_box.set_margin_top(24)
            main_box.set_margin_bottom(24)
            main_box.set_margin_start(24)
            main_box.set_margin_end(24)

            # Header section
            header_group = Adw.PreferencesGroup()
            header_group.set_title("USB Devices")
            header_group.set_description("Real-time USB device enumeration")

            # Add header row
            info_row = Adw.ActionRow()
            info_row.set_title("USB Device List")
            info_row.set_subtitle("Raw lsusb output, auto-refreshing")

            usb_icon = Gtk.Image.new_from_icon_name("drive-removable-media-symbolic")
            usb_icon.set_icon_size(Gtk.IconSize.LARGE)
            info_row.add_prefix(usb_icon)

            header_group.add(info_row)
            main_box.append(header_group)

            # Control bar
            control_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            control_box.set_margin_bottom(12)

            # Refresh button
            self.refresh_button = Gtk.Button(label="Refresh")
            self.refresh_button.set_icon_name("view-refresh-symbolic")
            self.refresh_button.connect("clicked", self._on_refresh_clicked)
            control_box.append(self.refresh_button)

            # Auto-refresh toggle
            self.auto_refresh_toggle = Gtk.ToggleButton(label="Auto-refresh")
            self.auto_refresh_toggle.set_active(self.auto_refresh_enabled)
            self.auto_refresh_toggle.connect("toggled", self._on_auto_refresh_toggled)
            control_box.append(self.auto_refresh_toggle)

            # Status label
            self.status_label = Gtk.Label(label="Ready")
            self.status_label.set_halign(Gtk.Align.START)
            self.status_label.set_hexpand(True)
            self.status_label.add_css_class("dim-label")
            control_box.append(self.status_label)

            main_box.append(control_box)

            # Text view for lsusb output
            scrolled = Gtk.ScrolledWindow()
            scrolled.set_vexpand(True)
            scrolled.set_hexpand(True)
            scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

            self.text_buffer = Gtk.TextBuffer()
            self.text_view = Gtk.TextView()
            self.text_view.set_buffer(self.text_buffer)
            self.text_view.set_editable(False)
            self.text_view.set_monospace(True)
            self.text_view.set_wrap_mode(Gtk.WrapMode.NONE)

            # Apply monospace font
            font_desc = "Monospace 10"
            self.text_view.set_font_desc(Pango.FontDescription.from_string(font_desc))

            scrolled.set_child(self.text_view)
            main_box.append(scrolled)

            self.widget = main_box

            # Log creation
            if hasattr(self.app, 'session_logger') and self.app.session_logger:
                self.app.session_logger.log_gui_event("USB_VIEW_CREATED", "USB view created")

            return self.widget

        except Exception as e:
            logger.error(f"Error creating USB view: {e}")
            # Fallback error display
            error_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
            error_label = Gtk.Label(label=f"Error: {str(e)}")
            error_box.append(error_label)
            return error_box

    def _on_refresh_clicked(self, button):
        """Handle refresh button click"""
        self.refresh_usb_list()

    def _on_auto_refresh_toggled(self, toggle):
        """Handle auto-refresh toggle"""
        self.auto_refresh_enabled = toggle.get_active()
        
        if self.auto_refresh_enabled:
            self._start_auto_refresh()
        else:
            self._stop_auto_refresh()

    def refresh_usb_list(self):
        """Refresh the USB device list"""
        try:
            self.status_label.set_text("Refreshing...")
            self.refresh_button.set_sensitive(False)

            # Get USB devices
            basic, verbose = self.usb_monitor.refresh()

            # Display basic output
            self.text_buffer.set_text(basic)

            self.status_label.set_text("Updated")
            
            if hasattr(self.app, 'session_logger') and self.app.session_logger:
                self.app.session_logger.log_gui_event("USB_LIST_REFRESHED", "USB device list refreshed")

        except Exception as e:
            logger.error(f"Error refreshing USB list: {e}")
            self.status_label.set_text(f"Error: {str(e)}")
        finally:
            self.refresh_button.set_sensitive(True)

    def _start_auto_refresh(self):
        """Start auto-refresh timer"""
        if self.refresh_timeout_id:
            GLib.source_remove(self.refresh_timeout_id)
        
        self.refresh_timeout_id = GLib.timeout_add(
            self.refresh_interval,
            self._auto_refresh_callback
        )

    def _stop_auto_refresh(self):
        """Stop auto-refresh timer"""
        if self.refresh_timeout_id:
            GLib.source_remove(self.refresh_timeout_id)
            self.refresh_timeout_id = None

    def _auto_refresh_callback(self):
        """Auto-refresh callback"""
        self.refresh_usb_list()
        return True  # Continue timer

    def on_ready(self):
        """Called when view is displayed"""
        logger.info("USB view ready - starting auto-refresh")
        if self.auto_refresh_enabled:
            self._start_auto_refresh()
            self.refresh_usb_list()

    def cleanup(self):
        """Clean up resources"""
        self._stop_auto_refresh()
        if hasattr(self.app, 'session_logger') and self.app.session_logger:
            self.app.session_logger.log_gui_event("USB_VIEW_CLEANUP", "USB view cleaned up")

