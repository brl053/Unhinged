"""
StatusView - Status tab showing active chat session ID

Simple status display for the active chat session.
"""

import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Adw, Gtk


class StatusView:
    """Status tab showing active chat session ID"""

    def __init__(self, parent_app):
        """Initialize with reference to parent app"""
        self.app = parent_app
        self.session_id_label = None

    def create_content(self):
        """Create status tab showing only the active chat session ID."""
        # Create status content box
        status_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        status_box.set_margin_top(24)
        status_box.set_margin_bottom(24)
        status_box.set_margin_start(24)
        status_box.set_margin_end(24)

        # Add session management section (only section now)
        session_section = self._create_session_management_section()
        status_box.append(session_section)

        # Create scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_child(status_box)

        return scrolled

    def _create_session_management_section(self):
        """Create session management section displaying active session ID"""
        group = Adw.PreferencesGroup()
        group.set_title("Chat Session")
        group.set_description("Active session from OS Chatroom")

        # Session ID row
        session_row = Adw.ActionRow()
        session_row.set_title("Session ID")

        # Session ID label (displays active session ID from chatroom)
        self.session_id_label = Gtk.Label()
        self.session_id_label.set_text("No active session")
        self.session_id_label.set_halign(Gtk.Align.END)
        self.session_id_label.add_css_class("monospace")
        self.session_id_label.add_css_class("caption")
        session_row.add_suffix(self.session_id_label)

        group.add(session_row)

        return group


    def update_session_id(self, session_id):
        """Update the displayed session ID from chatroom"""
        from gi.repository import GLib

        def update_ui():
            if self.session_id_label:
                if session_id:
                    self.session_id_label.set_text(session_id)
                else:
                    self.session_id_label.set_text("No active session")
            return False

        GLib.idle_add(update_ui)
