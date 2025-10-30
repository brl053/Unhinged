"""
StatusView - Status tab extracted from desktop_app.py
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw

# Import component library
try:
    from ..components import StatusCard, StatusLabel
    COMPONENTS_AVAILABLE = True
except ImportError:
    COMPONENTS_AVAILABLE = False


class StatusView:
    """Handles the Status tab functionality"""
    
    def __init__(self, parent_app):
        """Initialize with reference to parent app"""
        self.app = parent_app
        
    def create_content(self):
        """Create the new minimal status tab content using component library."""
        # Create status content box
        status_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        status_box.set_margin_top(24)
        status_box.set_margin_bottom(24)
        status_box.set_margin_start(24)
        status_box.set_margin_end(24)

        # Header section
        header_group = Adw.PreferencesGroup()
        header_group.set_title("New Status Tab")
        header_group.set_description("Minimal academic first step - parallel to existing status")
        status_box.append(header_group)

        # Use component library if available
        if COMPONENTS_AVAILABLE:
            # Status card using component library
            status_card = StatusCard(
                title="Platform Status",
                status="info",
                subtitle="Component library integration",
                description="This tab demonstrates the new component library in a minimal way.",
                icon_name="dialog-information-symbolic"
            )
            status_box.append(status_card.get_widget())

            # Status labels section
            labels_group = Adw.PreferencesGroup()
            labels_group.set_title("Status Examples")

            labels_row = Adw.ActionRow()
            labels_row.set_title("Component Status Labels")
            labels_row.set_subtitle("Different status types using the component library")

            # Create a box for status labels
            labels_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

            # Add different status labels
            for status_type in ["success", "warning", "error", "info"]:
                status_label = StatusLabel(
                    text=status_type.title(),
                    status=status_type
                )
                labels_box.append(status_label.get_widget())

            labels_row.add_suffix(labels_box)
            labels_group.add(labels_row)
            status_box.append(labels_group)

        else:
            # Fallback to basic widgets
            fallback_group = Adw.PreferencesGroup()
            fallback_group.set_title("Basic Status")

            fallback_row = Adw.ActionRow()
            fallback_row.set_title("Platform Status")
            fallback_row.set_subtitle("Component library not available - using basic widgets")

            status_icon = Gtk.Image.new_from_icon_name("emblem-default-symbolic")
            status_icon.set_icon_size(Gtk.IconSize.LARGE)
            fallback_row.add_prefix(status_icon)

            status_label = Gtk.Label(label="Ready")
            status_label.add_css_class("title-4")
            fallback_row.add_suffix(status_label)

            fallback_group.add(fallback_row)
            status_box.append(fallback_group)

        # Info section
        info_group = Adw.PreferencesGroup()
        info_group.set_title("Implementation Notes")

        info_row = Adw.ActionRow()
        info_row.set_title("Minimal Feature Set")
        info_row.set_subtitle("No API calls, no extra functionality - just a new tab with static content")

        info_group.add(info_row)
        status_box.append(info_group)

        # Create scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_child(status_box)

        return scrolled

    def refresh_status(self):
        """Refresh status information"""
        # Log refresh if logger available
        if hasattr(self.app, 'session_logger') and self.app.session_logger:
            self.app.session_logger.log_gui_event("STATUS_REFRESH", "Status view refreshed")

    def cleanup(self):
        """Clean up status components"""
        try:
            # Log cleanup
            if hasattr(self.app, 'session_logger') and self.app.session_logger:
                self.app.session_logger.log_gui_event("STATUS_CLEANUP", "Status components cleaned up")
                
        except Exception as e:
            if hasattr(self.app, 'session_logger') and self.app.session_logger:
                self.app.session_logger.log_gui_event("STATUS_CLEANUP_ERROR", str(e))
