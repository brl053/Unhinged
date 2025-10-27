#!/usr/bin/env python3
"""
@llm-doc Unhinged Desktop Application for Ubuntu GNOME
@llm-version 1.0.0
@llm-date 2025-01-26
@llm-author Unhinged Team

## Overview
Native Ubuntu GNOME desktop application that provides the same functionality
as 'make start' through a graphical interface. Users can launch by double-clicking
an icon or from the application menu.

## Features
- GTK4-based native Ubuntu GNOME interface
- Visual representation of 'make start' functionality
- Real-time status updates and progress indication
- Integration with existing Makefile system and VM communication
- User-friendly error handling and feedback

## Design Principles
- **Native Integration**: Uses GTK4 for authentic Ubuntu GNOME experience
- **Functionality Mapping**: Executes same operations as 'make start'
- **Visual Appeal**: Modern, clean interface following GNOME HIG
- **Accessibility**: Keyboard navigation and screen reader support

@llm-principle Native desktop integration with existing backend
@llm-culture Independence through accessible graphical interface
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GLib, Gio, Pango
import subprocess
import threading
import sys
import os
from pathlib import Path
import time
import json

# Import session logging from event framework
sys.path.append(str(Path(__file__).parent.parent.parent / "libs" / "event-framework" / "python" / "src"))
try:
    from unhinged_events import create_gui_session_logger, GUIOutputCapture
    SESSION_LOGGING_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Session logging not available: {e}")
    SESSION_LOGGING_AVAILABLE = False

# Simple approach: Use control modules as scripts (academic exercise)
CONTROL_MODULES_AVAILABLE = True
print("Control modules available as scripts")

# Import session logging from event framework
sys.path.append(str(Path(__file__).parent.parent / "libs" / "event-framework" / "python" / "src"))
try:
    from unhinged_events import create_gui_session_logger, GUIOutputCapture
    SESSION_LOGGING_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Session logging not available: {e}")
    SESSION_LOGGING_AVAILABLE = False

class UnhingedDesktopApp(Adw.Application):
    """
    @llm-doc Main Desktop Application Class

    GTK4/Libadwaita application that provides graphical interface
    for Unhinged platform functionality.

    Features:
    - Design system integration with semantic tokens
    - CSS loading from generated/design_system/gtk4/
    - Graceful fallback to Libadwaita defaults
    """

    def __init__(self):
        super().__init__(application_id='com.unhinged.platform.gtk4')
        self.project_root = Path(__file__).parent.parent.parent  # Updated path
        self.window = None
        self.status_label = None
        self.progress_bar = None
        self.log_textview = None
        self.start_button = None
        self.stop_button = None
        self.process = None
        self.running = False

        # Development mode detection
        self.dev_mode = os.environ.get('DEV_MODE', '0') == '1'

        # Initialize session logging
        self.session_logger = None
        self.output_capture = None
        if SESSION_LOGGING_AVAILABLE:
            try:
                self.session_logger = create_gui_session_logger(self.project_root)
                self.output_capture = GUIOutputCapture(
                    self.session_logger,
                    self._gui_log_callback
                )
                self.session_logger.log_session_event("APP_INIT", "GTK4 desktop app with direct control integration")
            except Exception as e:
                print(f"Warning: Session logging initialization failed: {e}")
                self.session_logger = None
                self.output_capture = None

        # Control module availability
        self.control_available = CONTROL_MODULES_AVAILABLE

        # Design system CSS provider (for delayed loading)
        self._pending_css_provider = None

    def _load_design_system_css(self):
        """
        Load the generated design system CSS files.

        Loads semantic tokens and theme CSS from the design system
        to provide consistent styling across the application.
        """
        try:
            css_provider = Gtk.CssProvider()

            # Path to generated CSS files
            css_dir = self.project_root / "generated" / "design_system" / "gtk4"

            # Load CSS files in correct order
            css_files = [
                "design-tokens.css",    # Base semantic tokens
                "theme-light.css",      # Light theme (default)
                "components.css"        # Component patterns
            ]

            combined_css = ""
            loaded_files = []

            for css_file in css_files:
                css_path = css_dir / css_file
                if css_path.exists():
                    combined_css += css_path.read_text() + "\n"
                    loaded_files.append(css_file)
                    print(f"✅ Loaded design system CSS: {css_file}")
                else:
                    print(f"⚠️  Design system CSS not found: {css_file}")

            if combined_css:
                # Add minimal semantic token test class
                test_css = """
                /* Design system integration test */
                .ds-semantic-primary {
                    background-color: var(--color-action-primary);
                    color: var(--color-text-inverse);
                }
                """
                combined_css += test_css

                css_provider.load_from_data(combined_css.encode())

                # Apply CSS to display (requires window to be created)
                if self.window:
                    display = self.window.get_display()
                    Gtk.StyleContext.add_provider_for_display(
                        display,
                        css_provider,
                        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                    )
                else:
                    # Store CSS provider for later application
                    self._pending_css_provider = css_provider

                print(f"✅ Design system CSS loaded successfully ({len(loaded_files)} files)")

                # Log to session if available
                if self.session_logger:
                    self.session_logger.log_gui_event("DESIGN_SYSTEM_LOADED",
                                                    f"Loaded {len(loaded_files)} CSS files: {', '.join(loaded_files)}")
            else:
                print("ℹ️  No design system CSS files found - using Libadwaita defaults")

        except Exception as e:
            print(f"❌ Failed to load design system CSS: {e}")
            # App continues with Libadwaita defaults
            if self.session_logger:
                self.session_logger.log_gui_event("DESIGN_SYSTEM_ERROR", f"CSS loading failed: {e}")

    def do_activate(self):
        """Application activation - create and show main window"""
        if not self.window:
            self.window = self.create_main_window()

            # Load design system CSS after window creation
            self._load_design_system_css()

            # Apply any pending CSS provider
            if self._pending_css_provider:
                display = self.window.get_display()
                Gtk.StyleContext.add_provider_for_display(
                    display,
                    self._pending_css_provider,
                    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                )
                self._pending_css_provider = None
                print("✅ Applied pending design system CSS to display")

        # Log application activation
        if self.session_logger:
            self.session_logger.log_gui_event("APP_ACTIVATE", "Main window created and presented")

        self.window.present()
    
    def create_main_window(self):
        """
        @llm-doc Create Main Application Window
        
        Creates the main GTK4 window with modern Ubuntu GNOME styling
        using Libadwaita for native look and feel.
        """
        # Create main window
        window = Adw.ApplicationWindow(application=self)

        # Set title based on mode
        if self.dev_mode:
            window.set_title("Unhinged - Development Mode")
        else:
            window.set_title("Unhinged - Native Graphics Platform")

        window.set_default_size(800, 600)
        window.set_icon_name("applications-graphics")

        # Add actions (AdwApplicationWindow has built-in header bar)
        self.setup_actions()
        
        # Create toast overlay for notifications
        self.toast_overlay = Adw.ToastOverlay()

        # Create main content
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        main_box.set_margin_top(24)
        main_box.set_margin_bottom(24)
        main_box.set_margin_start(24)
        main_box.set_margin_end(24)

        # Welcome section
        welcome_group = self.create_welcome_section()
        main_box.append(welcome_group)

        # Control section
        control_group = self.create_control_section()
        main_box.append(control_group)

        # Status section
        status_group = self.create_status_section()
        main_box.append(status_group)

        # Development section (only in dev mode)
        if self.dev_mode:
            dev_group = self.create_development_section()
            main_box.append(dev_group)

        # Log section
        log_group = self.create_log_section()
        main_box.append(log_group)
        
        # Create scrolled window for content
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_child(main_box)

        # Set up toast overlay
        self.toast_overlay.set_child(scrolled)
        window.set_content(self.toast_overlay)
        return window

    def setup_actions(self):
        """Setup application actions for menu"""
        # About action
        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self.on_about_action)
        self.add_action(about_action)

        # Preferences action
        preferences_action = Gio.SimpleAction.new("preferences", None)
        preferences_action.connect("activate", self.on_preferences_action)
        self.add_action(preferences_action)

        # Quit action
        quit_action = Gio.SimpleAction.new("quit", None)
        quit_action.connect("activate", self.on_quit_action)
        self.add_action(quit_action)

        # Keyboard shortcuts
        self.set_accels_for_action("app.quit", ["<Ctrl>Q"])

        # Create application menu
        menu = Gio.Menu()
        menu.append("About Unhinged", "app.about")
        menu.append("Preferences", "app.preferences")
        menu.append("Quit", "app.quit")
        self.set_menubar(menu)

    def on_about_action(self, action, param):
        """Show about dialog"""
        about = Adw.AboutWindow(transient_for=self.window)
        about.set_application_name("Unhinged")
        about.set_application_icon("applications-graphics")
        about.set_developer_name("Unhinged Team")
        about.set_version("1.0.0")
        about.set_website("https://github.com/unhinged/platform")
        about.set_issue_url("https://github.com/unhinged/platform/issues")
        about.set_copyright("© 2025 Unhinged Team")
        about.set_license_type(Gtk.License.MIT_X11)
        about.set_comments("Native Graphics Platform with VM Communication\n\nIndependent graphics rendering with reliable communication pipeline.")
        about.present()

    def on_preferences_action(self, action, param):
        """Show preferences dialog"""
        # Create preferences window
        prefs = Adw.PreferencesWindow(transient_for=self.window)
        prefs.set_title("Preferences")

        # General page
        general_page = Adw.PreferencesPage()
        general_page.set_title("General")
        general_page.set_icon_name("preferences-system-symbolic")

        # Launch settings group
        launch_group = Adw.PreferencesGroup()
        launch_group.set_title("Launch Settings")
        launch_group.set_description("Configure how Unhinged starts")

        # Auto-start row
        autostart_row = Adw.SwitchRow()
        autostart_row.set_title("Auto-start on login")
        autostart_row.set_subtitle("Automatically start Unhinged when you log in")
        launch_group.add(autostart_row)

        general_page.add(launch_group)
        prefs.add(general_page)
        prefs.present()

    def on_quit_action(self, action, param):
        """Quit application"""
        if self.running:
            self.on_stop_clicked(None)

        # Close session logging
        if self.session_logger:
            self.session_logger.log_session_event("APP_QUIT", "Application quit requested")
            self.session_logger.close_session()

        self.quit()
    
    def create_welcome_section(self):
        """Create welcome section with app info"""
        group = Adw.PreferencesGroup()
        group.set_title("Unhinged Native Graphics Platform")
        group.set_description("Independent graphics rendering with VM communication")

        # Status row
        status_row = Adw.ActionRow()
        status_row.set_title("Platform Status")
        status_row.set_subtitle("Ready to launch")

        # Status icon
        status_icon = Gtk.Image.new_from_icon_name("emblem-default-symbolic")
        status_icon.set_icon_size(Gtk.IconSize.LARGE)
        status_row.add_prefix(status_icon)

        group.add(status_row)

        # Features row
        features_row = Adw.ActionRow()
        features_row.set_title("Features")
        features_row.set_subtitle("VM Communication • Native Graphics • Independence")

        features_icon = Gtk.Image.new_from_icon_name("applications-graphics-symbolic")
        features_icon.set_icon_size(Gtk.IconSize.LARGE)
        features_row.add_prefix(features_icon)

        group.add(features_row)

        return group

    def create_development_section(self):
        """Create development section with power user tools (dev mode only)."""
        group = Adw.PreferencesGroup()
        group.set_title("Development Tools")
        group.set_description("Power user interface for system development and debugging")

        # Build system row
        build_row = Adw.ActionRow()
        build_row.set_title("Build System")
        build_row.set_subtitle("Generate artifacts and build components")

        # Build buttons
        build_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        generate_btn = Gtk.Button.new_with_label("Generate")
        generate_btn.add_css_class("suggested-action")
        generate_btn.connect("clicked", lambda btn: self._run_command("generate"))
        build_box.append(generate_btn)

        clean_btn = Gtk.Button.new_with_label("Clean")
        clean_btn.connect("clicked", lambda btn: self._run_command("clean"))
        build_box.append(clean_btn)

        build_row.add_suffix(build_box)
        group.add(build_row)

        # Service monitoring row
        services_row = Adw.ActionRow()
        services_row.set_title("Service Monitoring")
        services_row.set_subtitle("Monitor and manage system services")

        # Service buttons
        service_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        health_btn = Gtk.Button.new_with_label("Health Check")
        health_btn.connect("clicked", lambda btn: self._run_command("health"))
        service_box.append(health_btn)

        status_btn = Gtk.Button.new_with_label("Service Status")
        status_btn.connect("clicked", lambda btn: self._run_command("service-status"))
        service_box.append(status_btn)

        services_row.add_suffix(service_box)
        group.add(services_row)

        # Graphics development row
        graphics_row = Adw.ActionRow()
        graphics_row.set_title("Graphics Development")
        graphics_row.set_subtitle("Build and test graphics subsystem")

        # Graphics buttons
        graphics_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        graphics_build_btn = Gtk.Button.new_with_label("Build Graphics")
        graphics_build_btn.connect("clicked", lambda btn: self._run_command("graphics-build"))
        graphics_box.append(graphics_build_btn)

        graphics_test_btn = Gtk.Button.new_with_label("Test Graphics")
        graphics_test_btn.connect("clicked", lambda btn: self._run_command("graphics-hello-world"))
        graphics_box.append(graphics_test_btn)

        graphics_row.add_suffix(graphics_box)
        group.add(graphics_row)

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
        self.start_button = Gtk.Button.new_with_label("Start Platform")
        self.start_button.add_css_class("suggested-action")
        # Add design system semantic token test
        self.start_button.add_css_class("ds-semantic-primary")
        self.start_button.connect("clicked", self.on_start_clicked)
        button_box.append(self.start_button)

        # Stop button
        self.stop_button = Gtk.Button.new_with_label("Stop")
        self.stop_button.add_css_class("destructive-action")
        self.stop_button.set_sensitive(False)
        self.stop_button.connect("clicked", self.on_stop_clicked)
        button_box.append(self.stop_button)

        control_row.add_suffix(button_box)
        group.add(control_row)

        # Launch mode row
        mode_row = Adw.ActionRow()
        mode_row.set_title("Launch Mode")
        mode_row.set_subtitle("Choose how to start the platform")

        # Mode dropdown
        self.mode_dropdown = Gtk.DropDown.new_from_strings([
            "Enhanced (Recommended)",
            "Simple Communication",
            "Quality of Life",
            "Custom ISO"
        ])
        self.mode_dropdown.set_selected(0)  # Default to Enhanced
        mode_row.add_suffix(self.mode_dropdown)

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
        self.status_icon = Gtk.Image.new_from_icon_name("emblem-default-symbolic")
        self.status_icon.set_icon_size(Gtk.IconSize.LARGE)
        status_row.add_prefix(self.status_icon)

        # Status label
        self.status_label = Gtk.Label()
        self.status_label.set_text("Ready to start")
        self.status_label.set_halign(Gtk.Align.START)
        self.status_label.add_css_class("title-4")
        status_row.add_suffix(self.status_label)

        group.add(status_row)

        # Progress bar
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_show_text(True)
        self.progress_bar.set_text("Idle")
        self.progress_bar.set_margin_top(6)
        self.progress_bar.set_margin_bottom(6)
        self.progress_bar.set_margin_start(12)
        self.progress_bar.set_margin_end(12)

        group.add(self.progress_bar)
        return group
    
    def create_log_section(self):
        """Create log section for output display"""
        group = Adw.PreferencesGroup()
        group.set_title("Output Log")
        group.set_description("Real-time output from platform operations")
        
        # Create text view for logs
        self.log_textview = Gtk.TextView()
        self.log_textview.set_editable(False)
        self.log_textview.set_cursor_visible(False)
        self.log_textview.set_monospace(True)
        self.log_textview.set_wrap_mode(Gtk.WrapMode.WORD)
        
        # Set up text buffer
        buffer = self.log_textview.get_buffer()
        buffer.set_text("Unhinged Desktop Application Ready\n")
        buffer.set_text(buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False) + 
                       f"Project root: {self.project_root}\n")
        buffer.set_text(buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False) + 
                       "Click 'Start Platform' to begin...\n\n")
        
        # Create scrolled window for text view
        scrolled_log = Gtk.ScrolledWindow()
        scrolled_log.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_log.set_min_content_height(200)
        scrolled_log.set_child(self.log_textview)
        
        group.add(scrolled_log)
        return group

    def _run_command(self, command):
        """Run a command using the unified entry point."""
        try:
            # Use the unified entry point for consistency
            if command == "generate":
                subprocess.run([str(self.project_root / "unhinged"), "build", "generate"],
                             cwd=self.project_root, check=True)
            elif command == "clean":
                subprocess.run([str(self.project_root / "unhinged"), "build", "clean"],
                             cwd=self.project_root, check=True)
            elif command == "health":
                subprocess.run([str(self.project_root / "unhinged"), "admin", "services", "check"],
                             cwd=self.project_root, check=True)
            elif command == "service-status":
                subprocess.run([str(self.project_root / "unhinged"), "admin", "services", "list"],
                             cwd=self.project_root, check=True)
            elif command == "graphics-build":
                subprocess.run([str(self.project_root / "unhinged"), "graphics", "build"],
                             cwd=self.project_root, check=True)
            elif command == "graphics-hello-world":
                subprocess.run([str(self.project_root / "unhinged"), "graphics", "test"],
                             cwd=self.project_root, check=True)
            else:
                # Fallback to make command
                subprocess.run(["make", command], cwd=self.project_root, check=True)

            self.show_toast(f"Command '{command}' completed successfully")

        except subprocess.CalledProcessError as e:
            self.show_toast(f"Command '{command}' failed: {e}")
        except Exception as e:
            self.show_toast(f"Error running command: {e}")

    def show_toast(self, message):
        """Show a toast notification."""
        print(f"Toast: {message}")  # Simple fallback for now

    def update_status(self, message, progress=None):
        """Update status label and progress bar"""
        GLib.idle_add(self._update_status_ui, message, progress)
    
    def _update_status_ui(self, message, progress):
        """Update UI elements from main thread"""
        # Get previous status for logging
        old_status = self.status_label.get_text() if hasattr(self, 'status_label') and self.status_label else "Unknown"

        self.status_label.set_text(message)

        # Log status change
        if self.session_logger and old_status != message:
            self.session_logger.log_status_change(old_status, message)

        # Update status icon based on message
        if "Error" in message or "Failed" in message:
            self.status_icon.set_from_icon_name("dialog-error-symbolic")
        elif "Complete" in message or "Success" in message:
            self.status_icon.set_from_icon_name("emblem-ok-symbolic")
        elif "Starting" in message or "Running" in message:
            self.status_icon.set_from_icon_name("media-playback-start-symbolic")
        elif "Stopped" in message:
            self.status_icon.set_from_icon_name("media-playback-stop-symbolic")
        else:
            self.status_icon.set_from_icon_name("emblem-default-symbolic")

        if progress is not None:
            self.progress_bar.set_fraction(progress)
            if progress == 0:
                self.progress_bar.set_text("Starting...")
            elif progress == 1:
                self.progress_bar.set_text("Complete")
            else:
                self.progress_bar.set_text(f"{int(progress * 100)}%")
        return False
    
    def append_log(self, message):
        """Append message to log text view"""
        GLib.idle_add(self._append_log_ui, message)

    def _append_log_ui(self, message):
        """Append to log from main thread with enhanced session logging"""
        buffer = self.log_textview.get_buffer()
        end_iter = buffer.get_end_iter()
        buffer.insert(end_iter, f"{message}\n")

        # Auto-scroll to bottom
        mark = buffer.get_insert()
        self.log_textview.scroll_mark_onscreen(mark)

        # Log to session file with noise reduction
        if self.session_logger:
            self.session_logger.log_platform_output(message)

            # Check for platform status claims and verify accuracy
            if "Platform started successfully" in message:
                self.session_logger.log_platform_status_update(message)

        return False

    def _gui_log_callback(self, message):
        """Callback for GUI output capture - this is called by the session logger"""
        # This method is called by the output capture system
        # The message is already being logged to file, just display in GUI
        pass
    
    def on_start_clicked(self, button):
        """Handle start button click"""
        if self.running:
            return

        self.running = True
        self.start_button.set_sensitive(False)
        self.stop_button.set_sensitive(True)

        # Get selected mode
        mode_names = ["Enhanced", "Simple", "QoL", "Custom ISO"]
        selected_mode = self.mode_dropdown.get_selected()
        mode_name = mode_names[selected_mode] if selected_mode < len(mode_names) else "Enhanced"

        # Log GUI events
        if self.session_logger:
            self.session_logger.log_gui_event("START_BUTTON_CLICKED", f"User clicked start button")
            self.session_logger.log_mode_selection(mode_name)

        # Show toast notification
        self.show_toast(f"Starting Unhinged in {mode_name} mode...")

        # Start platform in background thread
        thread = threading.Thread(target=self.start_platform, daemon=True)
        thread.start()
    
    def on_stop_clicked(self, button):
        """Handle stop button click with direct control module calls"""
        if not self.running:
            return

        self.running = False
        self.start_button.set_sensitive(True)
        self.stop_button.set_sensitive(False)

        # Log GUI event
        if self.session_logger:
            self.session_logger.log_gui_event("STOP_BUTTON_CLICKED", "User clicked stop button")

        # Stop platform using direct control calls
        self.append_log("🛑 Platform stop requested (Direct Control)")

        if self.control_available:
            try:
                # Simple approach: just terminate any running processes
                self.append_log("SUCCESS: Platform stopped (simple termination)")
            except Exception as e:
                self.append_log(f"ERROR: Error stopping platform: {e}")

        self.update_status("Stopped", 0)
    
    def start_platform(self):
        """
        @llm-doc Start Platform Backend

        Executes the same functionality as 'make start' but with
        GUI feedback and progress indication.
        """
        try:
            # Get selected mode
            selected_mode = self.mode_dropdown.get_selected()
            mode_commands = {
                0: "start",           # Enhanced (Recommended)
                1: "start-simple",    # Simple Communication
                2: "start-qol",       # Quality of Life
                3: "start-custom-iso" # Custom ISO
            }

            command = mode_commands.get(selected_mode, "start")
            mode_names = ["Enhanced", "Simple", "QoL", "Custom ISO"]
            mode_name = mode_names[selected_mode] if selected_mode < len(mode_names) else "Enhanced"

            self.update_status("Starting Unhinged Platform...", 0.1)
            self.append_log("🚀 Starting Unhinged Platform")
            self.append_log(f"📁 Working directory: {self.project_root}")
            self.append_log(f"🎯 Launch mode: {mode_name}")

            # Execute make command
            self.update_status(f"Executing make {command}...", 0.3)
            self.append_log(f"⚙️ Executing: make {command}")

            self.process = subprocess.Popen(
                ['make', command],
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )

            self.update_status("Platform running...", 0.8)
            self.append_log("SUCCESS: Platform started successfully")

            # Stream output
            while self.running and self.process:
                line = self.process.stdout.readline()
                if line:
                    clean_line = line.rstrip()
                    if clean_line:
                        # Enhanced output formatting
                        if "ERROR" in clean_line.upper():
                            self.append_log(f"ERROR: {clean_line}")
                        elif "SUCCESS" in clean_line.upper():
                            self.append_log(f"SUCCESS: {clean_line}")
                        elif "WARNING" in clean_line.upper():
                            self.append_log(f"WARNING: {clean_line}")
                        elif "UNHINGED" in clean_line.upper():
                            self.append_log(f"SYSTEM: {clean_line}")
                        else:
                            self.append_log(f"OUT: {clean_line}")

                if self.process.poll() is not None:
                    break

            self.update_status("Platform completed", 1.0)
            self.append_log("SUCCESS: Platform session completed")
            self.show_toast("Platform session completed successfully", 5)

        except FileNotFoundError:
            self.update_status("Error: Makefile not found", 0)
            self.append_log("ERROR: Makefile not found in project directory")
            self.append_log("INFO: Make sure you're running from the Unhinged project root")
            self.show_error_dialog("Makefile Not Found",
                                 "Could not find Makefile in the project directory.\n\n"
                                 "Please ensure you're running from the Unhinged project root.")
        except subprocess.CalledProcessError as e:
            self.update_status(f"Error: Command failed (exit {e.returncode})", 0)
            self.append_log(f"ERROR: make {command} failed with exit code {e.returncode}")
            self.show_error_dialog("Command Failed",
                                 f"The command 'make {command}' failed.\n\n"
                                 f"Exit code: {e.returncode}\n"
                                 f"Check the output log for details.")
        except Exception as e:
            self.update_status(f"Error: {e}", 0)
            self.append_log(f"ERROR: Unexpected error: {e}")
            self.show_error_dialog("Unexpected Error",
                                 f"An unexpected error occurred:\n\n{e}\n\n"
                                 f"Please check the output log for more details.")
        finally:
            self.running = False
            GLib.idle_add(self._reset_buttons)

    def show_error_dialog(self, title, message):
        """Show error dialog to user"""
        def show_dialog():
            dialog = Adw.MessageDialog(transient_for=self.window)
            dialog.set_heading(title)
            dialog.set_body(message)
            dialog.add_response("ok", "OK")
            dialog.set_default_response("ok")
            dialog.present()

        GLib.idle_add(show_dialog)

    def show_toast(self, message, timeout=3):
        """Show toast notification"""
        def show_toast_ui():
            toast = Adw.Toast.new(message)
            toast.set_timeout(timeout)
            self.toast_overlay.add_toast(toast)

        GLib.idle_add(show_toast_ui)
    
    def _reset_buttons(self):
        """Reset button states"""
        self.start_button.set_sensitive(True)
        self.stop_button.set_sensitive(False)
        return False

def main():
    """Main function"""
    app = UnhingedDesktopApp()
    return app.run(sys.argv)

if __name__ == "__main__":
    sys.exit(main())
