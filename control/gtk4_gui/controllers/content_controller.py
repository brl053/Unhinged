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
import subprocess


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
        """Create welcome section with app info"""
        group = Adw.PreferencesGroup()
        group.set_title("Unhinged Native Graphics Platform")
        group.set_description("Independent graphics rendering with VM communication")
        
        # Version row
        version_row = Adw.ActionRow()
        version_row.set_title("Version")
        version_row.set_subtitle("1.0.0 Development")
        
        version_icon = Gtk.Image.new_from_icon_name("applications-graphics-symbolic")
        version_icon.add_css_class("accent")
        version_row.add_prefix(version_icon)
        
        group.add(version_row)
        
        # Features row
        features_row = Adw.ActionRow()
        features_row.set_title("Features")
        features_row.set_subtitle("Voice-first interface • Native graphics • AI integration")
        
        features_icon = Gtk.Image.new_from_icon_name("starred-symbolic")
        features_icon.add_css_class("success")
        features_row.add_prefix(features_icon)
        
        group.add(features_row)
        
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
        
        # Launch mode row
        mode_row = Adw.ActionRow()
        mode_row.set_title("Launch Mode")
        mode_row.set_subtitle("Choose how to start the platform")
        
        # Mode dropdown
        self.app.mode_dropdown = Gtk.DropDown.new_from_strings([
            "Enhanced (Recommended)",
            "Simple Communication", 
            "Quality of Life",
            "Custom ISO"
        ])
        self.app.mode_dropdown.set_selected(0)  # Default to Enhanced
        mode_row.add_suffix(self.app.mode_dropdown)
        
        group.add(mode_row)
        
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
        """Create development section with power user tools"""
        group = Adw.PreferencesGroup()
        group.set_title("Development Tools")
        group.set_description("Power user interface for system development and debugging")
        
        # Voice recording row
        voice_row = Adw.ActionRow()
        voice_row.set_title("Voice Recording")
        voice_row.set_subtitle("Test voice-to-text functionality")
        
        # Voice button
        voice_button = Gtk.Button.new_with_label("Record Voice")
        voice_button.add_css_class("pill")
        voice_button.connect("clicked", self.app.on_record_voice_clicked)
        voice_row.add_suffix(voice_button)
        
        group.add(voice_row)
        
        # Build commands row
        build_row = Adw.ActionRow()
        build_row.set_title("Build Commands")
        build_row.set_subtitle("Execute build system operations")
        
        # Build button box
        build_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        
        # Generate button
        generate_button = Gtk.Button.new_with_label("Generate")
        generate_button.add_css_class("pill")
        generate_button.connect("clicked", lambda b: self._run_command("generate"))
        build_box.append(generate_button)
        
        # Build button
        build_button = Gtk.Button.new_with_label("Build")
        build_button.add_css_class("pill")
        build_button.connect("clicked", lambda b: self._run_command("build"))
        build_box.append(build_button)
        
        build_row.add_suffix(build_box)
        group.add(build_row)
        
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
        
    def _run_command(self, command):
        """Run a command using the unified entry point"""
        try:
            # Use the unified entry point for consistency
            if command == "generate":
                subprocess.run([str(self.project_root / "unhinged"), "build", "generate"],
                             cwd=self.project_root, check=True)
                self.app.append_log("SUCCESS: Generate command completed")
            elif command == "build":
                subprocess.run([str(self.project_root / "unhinged"), "build"],
                             cwd=self.project_root, check=True)
                self.app.append_log("SUCCESS: Build command completed")
                
        except subprocess.CalledProcessError as e:
            self.app.append_log(f"ERROR: Command '{command}' failed with exit code {e.returncode}")
        except FileNotFoundError:
            self.app.append_log(f"ERROR: Command '{command}' not found")
        except Exception as e:
            self.app.append_log(f"ERROR: Unexpected error running '{command}': {e}")
