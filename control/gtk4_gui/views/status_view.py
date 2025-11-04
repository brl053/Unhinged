"""
StatusView - Enhanced Status tab with platform controls and monitoring

Migrated from main tab:
- Platform control (Start/Stop buttons)
- Platform status display (icon, label, progress bar)
- Log viewing functionality
"""

import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Adw, Gtk

# Import component library
try:
    from ..components import LogViewer, StatusCard, StatusLabel
    COMPONENTS_AVAILABLE = True
except ImportError:
    COMPONENTS_AVAILABLE = False

# Import platform handler
try:
    from ..handlers.platform_handler import PlatformHandler
    PLATFORM_HANDLER_AVAILABLE = True
except ImportError:
    PLATFORM_HANDLER_AVAILABLE = False


class StatusView:
    """Enhanced Status tab with platform controls and monitoring"""

    def __init__(self, parent_app):
        """Initialize with reference to parent app"""
        self.app = parent_app

        # Platform control references (migrated from main tab)
        self.start_button = None
        self.stop_button = None
        self.status_icon = None
        self.status_label = None
        self.progress_bar = None
        self.log_viewer = None

        # Session management references
        self.session_id_label = None

        # Initialize platform handler
        self.platform_handler = None
        if PLATFORM_HANDLER_AVAILABLE:
            try:
                self.platform_handler = PlatformHandler(parent_app.project_root)
                self.platform_handler.set_callbacks(
                    status_callback=self._update_platform_status,
                    log_callback=self._append_platform_log,
                    error_callback=self._show_platform_error
                )
            except Exception as e:
                print(f"⚠️ Failed to initialize platform handler: {e}")

    def create_content(self):
        """Create enhanced status tab with platform controls and monitoring."""
        # Create status content box
        status_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        status_box.set_margin_top(24)
        status_box.set_margin_bottom(24)
        status_box.set_margin_start(24)
        status_box.set_margin_end(24)

        # Add session management section
        session_section = self._create_session_management_section()
        status_box.append(session_section)

        # Add platform control section
        platform_control = self._create_platform_control_section()
        status_box.append(platform_control)

        # Add platform status section
        platform_status = self._create_platform_status_section()
        status_box.append(platform_status)

        # Add platform logs section
        platform_logs = self._create_platform_logs_section()
        status_box.append(platform_logs)

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

    def _create_platform_control_section(self):
        """Create platform control section with Start/Stop buttons"""
        group = Adw.PreferencesGroup()
        group.set_title("Platform Control")
        group.set_description("Launch and manage the Unhinged platform")

        # Control row
        control_row = Adw.ActionRow()
        control_row.set_title("Platform Launcher")
        control_row.set_subtitle("Start or stop the platform backend")

        # Button box
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        # Start button (migrated from main tab)
        self.start_button = Gtk.Button.new_with_label("Start Platform")
        self.start_button.add_css_class("suggested-action")
        self.start_button.connect("clicked", self._on_start_clicked)
        button_box.append(self.start_button)

        # Stop button (migrated from main tab)
        self.stop_button = Gtk.Button.new_with_label("Stop")
        self.stop_button.add_css_class("destructive-action")
        self.stop_button.set_sensitive(False)
        self.stop_button.connect("clicked", self._on_stop_clicked)
        button_box.append(self.stop_button)

        control_row.add_suffix(button_box)
        group.add(control_row)

        return group

    def _create_platform_status_section(self):
        """Create platform status section with icon, label, and progress bar"""
        group = Adw.PreferencesGroup()
        group.set_title("Platform Status")

        # Status row with icon (migrated from main tab)
        status_row = Adw.ActionRow()
        status_row.set_title("Current Status")

        # Status icon (migrated from main tab)
        self.status_icon = Gtk.Image.new_from_icon_name("emblem-default-symbolic")
        self.status_icon.set_icon_size(Gtk.IconSize.LARGE)
        status_row.add_prefix(self.status_icon)

        # Status label (migrated from main tab)
        self.status_label = Gtk.Label()
        self.status_label.set_text("Ready to start")
        self.status_label.set_halign(Gtk.Align.START)
        self.status_label.add_css_class("title-4")
        status_row.add_suffix(self.status_label)

        group.add(status_row)

        # Progress bar (migrated from main tab)
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_show_text(True)
        self.progress_bar.set_text("Idle")
        self.progress_bar.set_margin_top(6)
        self.progress_bar.set_margin_bottom(6)
        self.progress_bar.set_margin_start(12)
        self.progress_bar.set_margin_end(12)

        group.add(self.progress_bar)

        return group

    def _create_platform_logs_section(self):
        """Create platform logs section with LogViewer component"""
        group = Adw.PreferencesGroup()
        group.set_title("Platform Logs")
        group.set_description("Real-time output from platform operations")

        if COMPONENTS_AVAILABLE:
            # Use sophisticated LogViewer component
            self.log_viewer = LogViewer()
            group.add(self.log_viewer.get_widget())
        else:
            # Fallback to basic TextView (like main tab had)
            self.log_textview = Gtk.TextView()
            self.log_textview.set_editable(False)
            self.log_textview.set_cursor_visible(False)
            self.log_textview.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
            self.log_textview.add_css_class("monospace")
            self.log_textview.set_size_request(-1, 200)

            # Create scrolled window for log
            scrolled_log = Gtk.ScrolledWindow()
            scrolled_log.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            scrolled_log.set_size_request(-1, 200)
            scrolled_log.set_child(self.log_textview)

            group.add(scrolled_log)

        return group

    def _on_start_clicked(self, button):
        """Handle start button click (migrated from ActionController)"""
        if hasattr(self.app, 'running') and self.app.running:
            return

        # Update button states
        self.start_button.set_sensitive(False)
        self.stop_button.set_sensitive(True)

        # Log GUI event
        if hasattr(self.app, 'session_logger') and self.app.session_logger:
            self.app.session_logger.log_gui_event("START_BUTTON_CLICKED", "User clicked start button from Status tab")

        # Show toast notification
        if hasattr(self.app, 'show_toast'):
            self.app.show_toast("Starting Unhinged platform...")

        # Start platform using handler
        if self.platform_handler:
            import threading
            thread = threading.Thread(target=self.platform_handler.start_platform, daemon=True)
            thread.start()
        else:
            self._show_platform_error("Platform Error", "Platform handler not available")

    def _on_stop_clicked(self, button):
        """Handle stop button click (migrated from ActionController)"""
        if hasattr(self.app, 'running') and not self.app.running:
            return

        # Update button states
        self.start_button.set_sensitive(True)
        self.stop_button.set_sensitive(False)

        # Log GUI event
        if hasattr(self.app, 'session_logger') and self.app.session_logger:
            self.app.session_logger.log_gui_event("STOP_BUTTON_CLICKED", "User clicked stop button from Status tab")

        # Stop platform using handler
        if self.platform_handler:
            self.platform_handler.stop_platform()
        else:
            self._append_platform_log("⚠️ Platform handler not available")
            self._update_platform_status("Stopped", 0)

    def _update_platform_status(self, message, progress=None):
        """Update platform status display (migrated from desktop_app.py)"""
        from gi.repository import GLib

        def update_ui():
            if self.status_label:
                self.status_label.set_text(message)

            # Update status icon based on message
            if self.status_icon:
                if "Error" in message or "Failed" in message:
                    self.status_icon.set_from_icon_name("dialog-error-symbolic")
                elif "Complete" in message or "Success" in message or "running" in message.lower():
                    self.status_icon.set_from_icon_name("emblem-ok-symbolic")
                elif "Starting" in message or "Running" in message:
                    self.status_icon.set_from_icon_name("media-playback-start-symbolic")
                elif "Stopped" in message:
                    self.status_icon.set_from_icon_name("media-playback-stop-symbolic")
                else:
                    self.status_icon.set_from_icon_name("emblem-default-symbolic")

            if progress is not None and self.progress_bar:
                self.progress_bar.set_fraction(progress)
                if progress == 0:
                    self.progress_bar.set_text("Starting...")
                elif progress == 1:
                    self.progress_bar.set_text("Complete")
                else:
                    self.progress_bar.set_text(f"{int(progress * 100)}%")
            return False

        GLib.idle_add(update_ui)

    def _append_platform_log(self, message):
        """Append message to platform log (migrated from desktop_app.py)"""
        from gi.repository import GLib

        def update_log():
            if self.log_viewer:
                # Use sophisticated LogViewer
                self.log_viewer.append_log(message)
            elif hasattr(self, 'log_textview'):
                # Fallback to basic TextView
                buffer = self.log_textview.get_buffer()
                end_iter = buffer.get_end_iter()
                buffer.insert(end_iter, f"{message}\n")

                # Auto-scroll to bottom
                mark = buffer.get_insert()
                self.log_textview.scroll_mark_onscreen(mark)
            return False

        GLib.idle_add(update_log)

    def _show_platform_error(self, title, message):
        """Show platform error dialog"""
        if hasattr(self.app, 'show_error_dialog'):
            self.app.show_error_dialog(title, message)
        else:
            print(f"❌ {title}: {message}")

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

    def refresh_status(self):
        """Refresh status information"""
        # Log refresh if logger available
        if hasattr(self.app, 'session_logger') and self.app.session_logger:
            self.app.session_logger.log_gui_event("STATUS_REFRESH", "Status view refreshed")

    def cleanup(self):
        """Clean up status components and platform handler"""
        try:
            # Clean up platform handler
            if self.platform_handler:
                self.platform_handler.cleanup()

            # Log cleanup
            if hasattr(self.app, 'session_logger') and self.app.session_logger:
                self.app.session_logger.log_gui_event("STATUS_CLEANUP", "Enhanced status components cleaned up")

        except Exception as e:
            if hasattr(self.app, 'session_logger') and self.app.session_logger:
                self.app.session_logger.log_gui_event("STATUS_CLEANUP_ERROR", str(e))
