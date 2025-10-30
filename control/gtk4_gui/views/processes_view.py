"""
ProcessesView - Process Monitoring tab extracted from desktop_app.py

This module contains all the process monitoring functionality that was previously
embedded in the monolithic desktop_app.py file.
"""

import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Adw, Gtk


class ProcessesView:
    """Handles the Process Monitoring tab functionality"""

    def __init__(self, parent_app):
        """Initialize with reference to parent app"""
        self.app = parent_app

        # Process table reference
        self.process_table = None

    def create_content(self):
        """Create the processes tab content with live process monitoring."""
        try:
            # Import ProcessTable component
            from components.complex import ProcessTable

            # Create main content box
            processes_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
            processes_box.set_margin_top(24)
            processes_box.set_margin_bottom(24)
            processes_box.set_margin_start(24)
            processes_box.set_margin_end(24)
            processes_box.set_vexpand(True)
            processes_box.set_hexpand(True)

            # Create header section
            header_group = Adw.PreferencesGroup()
            header_group.set_title("Process Monitor")
            header_group.set_description("Live process monitoring with aux/top command equivalence")

            # Add header info row
            info_row = Adw.ActionRow()
            info_row.set_title("Process Management")
            info_row.set_subtitle("View, sort, filter, and manage running processes")

            # Add process monitor icon
            monitor_icon = Gtk.Image.new_from_icon_name("utilities-system-monitor-symbolic")
            monitor_icon.set_icon_size(Gtk.IconSize.LARGE)
            monitor_icon.add_css_class("accent")
            info_row.add_prefix(monitor_icon)

            header_group.add(info_row)
            processes_box.append(header_group)

            # Create ProcessTable
            self.process_table = ProcessTable()

            # Create process table group
            table_group = Adw.PreferencesGroup()
            table_group.set_title("Running Processes")

            # Add ProcessTable widget to the group
            table_row = Adw.ActionRow()
            table_row.set_child(self.process_table.get_widget())
            table_group.add(table_row)

            processes_box.append(table_group)

            # Log processes tab creation
            if hasattr(self.app, 'session_logger') and self.app.session_logger:
                self.app.session_logger.log_gui_event("PROCESSES_TAB_CREATED", "Processes tab with ProcessTable created")

            return processes_box

        except Exception as e:
            # Create error fallback
            error_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
            error_box.set_margin_top(24)
            error_box.set_margin_bottom(24)
            error_box.set_margin_start(24)
            error_box.set_margin_end(24)

            error_group = Adw.PreferencesGroup()
            error_group.set_title("Process Monitor Unavailable")
            error_group.set_description("Process monitoring is not available")

            error_row = Adw.ActionRow()
            error_row.set_title("Error Loading Process Monitor")
            error_row.set_subtitle(f"Error: {str(e)}")

            error_icon = Gtk.Image.new_from_icon_name("dialog-error-symbolic")
            error_icon.add_css_class("error")
            error_row.add_prefix(error_icon)

            error_group.add(error_row)
            error_box.append(error_group)

            # Log error
            if hasattr(self.app, 'session_logger') and self.app.session_logger:
                self.app.session_logger.log_gui_event("PROCESSES_TAB_ERROR", f"Failed to create processes tab: {e}")

            return error_box

    def get_process_table(self):
        """Get reference to the process table for external access"""
        return self.process_table

    def refresh_processes(self):
        """Refresh the process list"""
        try:
            if self.process_table and hasattr(self.process_table, 'refresh'):
                self.process_table.refresh()

            # Log refresh
            if hasattr(self.app, 'session_logger') and self.app.session_logger:
                self.app.session_logger.log_gui_event("PROCESSES_REFRESH", "Process list refreshed")

        except Exception as e:
            if hasattr(self.app, 'session_logger') and self.app.session_logger:
                self.app.session_logger.log_gui_event("PROCESSES_REFRESH_ERROR", str(e))

    def cleanup(self):
        """Clean up process monitoring components"""
        try:
            if self.process_table and hasattr(self.process_table, 'cleanup'):
                self.process_table.cleanup()

            # Log cleanup
            if hasattr(self.app, 'session_logger') and self.app.session_logger:
                self.app.session_logger.log_gui_event("PROCESSES_CLEANUP", "Process monitoring components cleaned up")

        except Exception as e:
            if hasattr(self.app, 'session_logger') and self.app.session_logger:
                self.app.session_logger.log_gui_event("PROCESSES_CLEANUP_ERROR", str(e))
