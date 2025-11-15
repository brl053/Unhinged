#!/usr/bin/env python3
"""
GPU Devices View

Displays raw nvidia-smi output with auto-refresh when tab is active.
"""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

import logging

from gi.repository import Adw, GLib, Gtk

logger = logging.getLogger(__name__)


class GPUView:
    """View for displaying GPU devices using raw nvidia-smi output"""

    def __init__(self, app):
        """Initialize GPU view"""
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

        # Import GPU monitor
        try:
            from ..handlers.gpu_monitor import GPUMonitor
        except ImportError:
            from handlers.gpu_monitor import GPUMonitor

        self.gpu_monitor = GPUMonitor()

    def create_content(self) -> Gtk.Widget:
        """Create the GPU view content"""
        try:
            # Main container
            main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
            main_box.set_margin_top(24)
            main_box.set_margin_bottom(24)
            main_box.set_margin_start(24)
            main_box.set_margin_end(24)

            # Header section
            header_group = Adw.PreferencesGroup()
            header_group.set_title("GPU Devices")
            header_group.set_description("Real-time GPU device enumeration")

            # Add header row
            info_row = Adw.ActionRow()
            info_row.set_title("GPU Device List")
            info_row.set_subtitle("Raw nvidia-smi output, auto-refreshing")

            gpu_icon = Gtk.Image.new_from_icon_name("video-card-symbolic")
            gpu_icon.set_icon_size(Gtk.IconSize.LARGE)
            info_row.add_prefix(gpu_icon)

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

            # Text view for nvidia-smi output
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

            # Apply monospace font via CSS class
            self.text_view.add_css_class("monospace")

            scrolled.set_child(self.text_view)
            main_box.append(scrolled)

            self.widget = main_box

            # Log creation
            if hasattr(self.app, "session_logger") and self.app.session_logger:
                self.app.session_logger.log_gui_event("GPU_VIEW_CREATED", "GPU view created")

            # Load initial data immediately
            GLib.idle_add(self.refresh_gpu_list)

            return self.widget

        except Exception as e:
            logger.error(f"Error creating GPU view: {e}")
            # Fallback error display
            error_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
            error_label = Gtk.Label(label=f"Error: {str(e)}")
            error_box.append(error_label)
            return error_box

    def _on_refresh_clicked(self, button):
        """Handle refresh button click"""
        self.refresh_gpu_list()

    def _on_auto_refresh_toggled(self, toggle):
        """Handle auto-refresh toggle"""
        self.auto_refresh_enabled = toggle.get_active()

        if self.auto_refresh_enabled:
            self._start_auto_refresh()
        else:
            self._stop_auto_refresh()

    def refresh_gpu_list(self):
        """Refresh the GPU device list"""
        try:
            self.status_label.set_text("Refreshing...")
            self.refresh_button.set_sensitive(False)

            # Get GPU devices
            basic, detailed = self.gpu_monitor.refresh()

            # Display basic output
            self.text_buffer.set_text(basic)

            self.status_label.set_text("Updated")

            if hasattr(self.app, "session_logger") and self.app.session_logger:
                self.app.session_logger.log_gui_event(
                    "GPU_LIST_REFRESHED", "GPU device list refreshed"
                )

        except Exception as e:
            logger.error(f"Error refreshing GPU list: {e}")
            self.status_label.set_text(f"Error: {str(e)}")
        finally:
            self.refresh_button.set_sensitive(True)

    def _start_auto_refresh(self):
        """Start auto-refresh timer"""
        if self.refresh_timeout_id:
            GLib.source_remove(self.refresh_timeout_id)

        self.refresh_timeout_id = GLib.timeout_add(
            self.refresh_interval, self._auto_refresh_callback
        )

    def _stop_auto_refresh(self):
        """Stop auto-refresh timer"""
        if self.refresh_timeout_id:
            GLib.source_remove(self.refresh_timeout_id)
            self.refresh_timeout_id = None

    def _auto_refresh_callback(self):
        """Auto-refresh callback"""
        self.refresh_gpu_list()
        return True  # Continue timer

    def on_ready(self):
        """Called when view is displayed"""
        logger.info("GPU view ready - starting auto-refresh")
        if self.auto_refresh_enabled:
            self._start_auto_refresh()
            self.refresh_gpu_list()

    def cleanup(self):
        """Clean up resources"""
        self._stop_auto_refresh()
        if hasattr(self.app, "session_logger") and self.app.session_logger:
            self.app.session_logger.log_gui_event("GPU_VIEW_CLEANUP", "GPU view cleaned up")
