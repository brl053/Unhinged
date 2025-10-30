"""
Content Controller - Handles all tab content creation

Extracted from desktop_app.py to achieve 75% reduction target.
Manages main content, welcome sections, development tools, and logs.
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GLib, Pango
from pathlib import Path


class ContentController:
    """Controller for tab content creation and management"""
    
    def __init__(self, app):
        """Initialize content controller with app reference"""
        self.app = app
        self.project_root = app.project_root
        
    def create_main_tab_content(self):
        """Create the main tab content (existing functionality)"""
        # Create main content
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        main_box.set_margin_top(24)
        main_box.set_margin_bottom(24)
        main_box.set_margin_start(24)
        main_box.set_margin_end(24)
        
        # Add sections
        main_box.append(self.create_welcome_section())
        main_box.append(self.create_control_section())
        main_box.append(self.create_status_section())
        main_box.append(self.create_development_section())
        main_box.append(self.create_log_section())
        
        # Create scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_child(main_box)
        
        return scrolled
        
    def create_welcome_section(self):
        """Create deprecation notice for main tab"""
        group = Adw.PreferencesGroup()
        group.set_title("Main Tab Deprecation Notice")
        group.set_description("This tab is being phased out - functionality moved to Status tab")

        # Deprecation notice row
        notice_row = Adw.ActionRow()
        notice_row.set_title("Functionality Moved")
        notice_row.set_subtitle("Platform controls and status moved to Status tab")

        notice_icon = Gtk.Image.new_from_icon_name("dialog-warning-symbolic")
        notice_icon.add_css_class("warning")
        notice_row.add_prefix(notice_icon)

        group.add(notice_row)

        return group
        
    def create_control_section(self):
        """Create control section with start/stop buttons"""
        group = Adw.PreferencesGroup()
        group.set_title("Platform Control")
        group.set_description("Launch and manage the Unhinged graphics platform")
        
        # Control row
        control_row = Adw.ActionRow()
        control_row.set_title("Platform Launcher")
        control_row.set_subtitle("Execute 'make start' functionality")
        
        # Button box
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        
        # Start button
        self.app.start_button = Gtk.Button.new_with_label("Start Platform")
        self.app.start_button.add_css_class("suggested-action")
        self.app.start_button.connect("clicked", self.app.on_start_clicked)
        button_box.append(self.app.start_button)
        
        # Stop button
        self.app.stop_button = Gtk.Button.new_with_label("Stop")
        self.app.stop_button.add_css_class("destructive-action")
        self.app.stop_button.set_sensitive(False)
        self.app.stop_button.connect("clicked", self.app.on_stop_clicked)
        button_box.append(self.app.stop_button)
        
        control_row.add_suffix(button_box)
        group.add(control_row)

        return group
        
    def create_status_section(self):
        """Create status section with progress indication"""
        group = Adw.PreferencesGroup()
        group.set_title("Status")
        
        # Status row with icon
        status_row = Adw.ActionRow()
        status_row.set_title("Platform Status")
        
        # Status icon
        self.app.status_icon = Gtk.Image.new_from_icon_name("emblem-default-symbolic")
        self.app.status_icon.set_icon_size(Gtk.IconSize.LARGE)
        status_row.add_prefix(self.app.status_icon)
        
        # Status label
        self.app.status_label = Gtk.Label()
        self.app.status_label.set_text("Ready to start")
        self.app.status_label.set_halign(Gtk.Align.START)
        self.app.status_label.add_css_class("title-4")
        status_row.add_suffix(self.app.status_label)
        
        group.add(status_row)
        
        # Progress bar
        self.app.progress_bar = Gtk.ProgressBar()
        self.app.progress_bar.set_show_text(True)
        self.app.progress_bar.set_text("Idle")
        self.app.progress_bar.set_margin_top(6)
        self.app.progress_bar.set_margin_bottom(6)
        self.app.progress_bar.set_margin_start(12)
        self.app.progress_bar.set_margin_end(12)
        
        group.add(self.app.progress_bar)
        
        return group
        
    def create_development_section(self):
        """Create minimal development section (most functionality moved to appropriate tabs)"""
        group = Adw.PreferencesGroup()
        group.set_title("Development Notes")
        group.set_description("Development tools have been moved to appropriate tabs")

        # Info row about moved functionality
        info_row = Adw.ActionRow()
        info_row.set_title("Voice Recording")
        info_row.set_subtitle("Available in OS Chatroom tab with full interface")

        # Add info icon
        info_icon = Gtk.Image.new_from_icon_name("dialog-information-symbolic")
        info_icon.add_css_class("accent")
        info_row.add_prefix(info_icon)

        group.add(info_row)

        return group
        
    def create_log_section(self):
        """Create log section for output display"""
        group = Adw.PreferencesGroup()
        group.set_title("Output Log")
        group.set_description("Real-time output from platform operations")
        
        # Create text view for log output
        self.app.log_textview = Gtk.TextView()
        self.app.log_textview.set_editable(False)
        self.app.log_textview.set_cursor_visible(False)
        self.app.log_textview.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.app.log_textview.add_css_class("monospace")
        self.app.log_textview.set_size_request(-1, 200)
        
        # Create scrolled window for log
        scrolled_log = Gtk.ScrolledWindow()
        scrolled_log.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_log.set_size_request(-1, 200)
        scrolled_log.set_child(self.app.log_textview)
        
        group.add(scrolled_log)
        return group
