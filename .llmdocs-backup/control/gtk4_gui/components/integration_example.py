"""
@llm-doc Integration Example for Existing Desktop App
@llm-version 1.0.0
@llm-date 2025-10-27

Shows how to integrate the component library into your existing
control/gtk4_gui/desktop_app.py with minimal changes.
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GLib
from pathlib import Path
import subprocess
import sys

# Import your new components
from components import (
    ActionButton, StatusLabel, ProgressIndicator,
    StatusCard, ServicePanel, LogViewer, SystemStatus
)


class EnhancedUnhingedDesktopApp(Adw.Application):
    """
    Enhanced version of your desktop app using the component library.
    
    This shows how to integrate components into your existing app
    with minimal changes to the overall structure.
    """
    
    def __init__(self):
        super().__init__(application_id='com.unhinged.platform.enhanced')
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.window = None
        
        # Component references
        self.start_button = None
        self.stop_button = None
        self.system_status = None
        self.log_viewer = None
        self.service_panels = {}
        
        # State
        self.running = False
        self.process = None
    
    def do_activate(self):
        """Application activation - create and show main window"""
        if not self.window:
            self.window = self.create_main_window()
            self._load_component_css()
        self.window.present()
    
    def _load_component_css(self):
        """Load component library CSS."""
        try:
            css_provider = Gtk.CssProvider()
            css_path = Path(__file__).parent / "components.css"
            
            if css_path.exists():
                css_provider.load_from_path(str(css_path))
                Gtk.StyleContext.add_provider_for_display(
                    self.window.get_display(),
                    css_provider,
                    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                )
                print("✅ Component CSS loaded")
        except Exception as e:
            print(f"❌ Failed to load component CSS: {e}")
    
    def create_main_window(self):
        """Create main application window with components."""
        window = Adw.ApplicationWindow(application=self)
        window.set_title("Unhinged - Enhanced with Components")
        window.set_default_size(900, 700)
        
        # Create toast overlay
        toast_overlay = Adw.ToastOverlay()
        
        # Create main content
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        main_box.set_margin_top(24)
        main_box.set_margin_bottom(24)
        main_box.set_margin_start(24)
        main_box.set_margin_end(24)
        
        # Add sections
        main_box.append(self.create_enhanced_welcome_section())
        main_box.append(self.create_enhanced_control_section())
        main_box.append(self.create_enhanced_status_section())
        main_box.append(self.create_enhanced_log_section())
        
        # Create scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_child(main_box)
        
        toast_overlay.set_child(scrolled)
        window.set_content(toast_overlay)
        
        return window
    
    def create_enhanced_welcome_section(self):
        """Enhanced welcome section with status card."""
        # Use StatusCard component instead of basic group
        welcome_card = StatusCard(
            title="Unhinged Graphics Platform",
            status="info",
            subtitle="Native graphics platform with dual-system architecture",
            description="Launch and manage the complete Unhinged experience with enhanced VM communication.",
            icon_name="applications-graphics"
        )
        
        return welcome_card.get_widget()
    
    def create_enhanced_control_section(self):
        """Enhanced control section with ActionButton components."""
        group = Adw.PreferencesGroup()
        group.set_title("Platform Control")
        group.set_description("Launch and manage the platform")
        
        control_row = Adw.ActionRow()
        control_row.set_title("Platform Launcher")
        control_row.set_subtitle("Enhanced controls with component library")
        
        # Button box
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        
        # Enhanced start button with ActionButton component
        self.start_button = ActionButton(
            label="Start Platform",
            style="primary",
            icon_name="media-playback-start-symbolic"
        )
        self.start_button.connect('clicked', self.on_start_clicked)
        button_box.append(self.start_button.get_widget())
        
        # Enhanced stop button
        self.stop_button = ActionButton(
            label="Stop",
            style="destructive",
            icon_name="process-stop-symbolic"
        )
        self.stop_button.set_sensitive(False)
        self.stop_button.connect('clicked', self.on_stop_clicked)
        button_box.append(self.stop_button.get_widget())
        
        # Status button
        status_button = ActionButton(
            label="Check Status",
            style="secondary",
            icon_name="view-refresh-symbolic"
        )
        status_button.connect('clicked', self.on_status_clicked)
        button_box.append(status_button.get_widget())
        
        control_row.add_suffix(button_box)
        group.add(control_row)
        
        return group
    
    def create_enhanced_status_section(self):
        """Enhanced status section with SystemStatus component."""
        group = Adw.PreferencesGroup()
        group.set_title("System Status")
        group.set_description("Real-time service monitoring")
        
        # Create SystemStatus component
        self.system_status = SystemStatus()
        group.add(self.system_status.get_widget())
        
        # Load initial status
        self.update_service_status()
        
        return group
    
    def create_enhanced_log_section(self):
        """Enhanced log section with LogViewer component."""
        group = Adw.PreferencesGroup()
        group.set_title("System Logs")
        group.set_description("Real-time log monitoring with filtering")
        
        # Create LogViewer component
        self.log_viewer = LogViewer()
        self.log_viewer.connect('export-requested', self.on_export_logs)
        self.log_viewer.connect('filter-changed', self.on_log_filter_changed)
        
        # Set reasonable height
        self.log_viewer.get_widget().set_size_request(-1, 300)
        
        group.add(self.log_viewer.get_widget())
        
        # Add some initial logs
        self.log_viewer.append_log("Application started", "INFO")
        self.log_viewer.append_log("Component library loaded", "INFO")
        
        return group
    
    def on_start_clicked(self, button):
        """Handle start button click with enhanced feedback."""
        if self.running:
            return
        
        # Set button to loading state
        self.start_button.set_loading(True)
        self.start_button.set_sensitive(False)
        
        # Log the action
        self.log_viewer.append_log("Starting platform...", "INFO")
        
        # Start the platform (simplified)
        GLib.timeout_add_seconds(2, self._simulate_start_complete)
    
    def _simulate_start_complete(self):
        """Simulate platform start completion."""
        self.running = True
        
        # Update button states
        self.start_button.set_loading(False)
        self.start_button.set_sensitive(False)
        self.stop_button.set_sensitive(True)
        
        # Log success
        self.log_viewer.append_log("Platform started successfully", "INFO")
        
        # Update status
        self.update_service_status()
        
        return False  # Don't repeat
    
    def on_stop_clicked(self, button):
        """Handle stop button click."""
        if not self.running:
            return
        
        self.running = False
        
        # Update button states
        self.start_button.set_sensitive(True)
        self.stop_button.set_sensitive(False)
        
        # Log the action
        self.log_viewer.append_log("Platform stopped", "INFO")
        
        # Update status
        self.update_service_status()
    
    def on_status_clicked(self, button):
        """Handle status check button click."""
        self.log_viewer.append_log("Checking service status...", "INFO")
        self.update_service_status()
    
    def update_service_status(self):
        """Update service status using components."""
        # Simulate getting service status (replace with actual service_launcher call)
        if self.running:
            services_data = {
                "LLM Service (Ollama)": {"running": True, "port": 1500, "health_method": "HTTP:1500"},
                "Text-to-Speech Service": {"running": True, "port": 1102, "health_method": "gRPC:9092"},
                "Vision AI Service": {"running": True, "port": 1103, "health_method": "gRPC:9093"},
                "Database": {"running": True, "port": 1200, "health_method": "container"},
            }
        else:
            services_data = {
                "LLM Service (Ollama)": {"running": False, "port": 1500, "health_method": "HTTP:1500"},
                "Text-to-Speech Service": {"running": False, "port": 1102, "health_method": "gRPC:9092"},
                "Vision AI Service": {"running": False, "port": 1103, "health_method": "gRPC:9093"},
                "Database": {"running": False, "port": 1200, "health_method": "container"},
            }
        
        # Update SystemStatus component
        self.system_status.update_services(services_data)
        
        # Log status update
        running_count = sum(1 for data in services_data.values() if data.get("running"))
        total_count = len(services_data)
        self.log_viewer.append_log(
            f"Status updated: {running_count}/{total_count} services running",
            "INFO"
        )
    
    def on_export_logs(self, log_viewer):
        """Handle log export request."""
        self.log_viewer.append_log("Log export requested", "INFO")
        # Implement actual export logic here
    
    def on_log_filter_changed(self, log_viewer, filter_text):
        """Handle log filter changes."""
        if filter_text:
            self.log_viewer.append_log(f"Filter applied: '{filter_text}'", "DEBUG")


def main():
    """Run the enhanced desktop application."""
    app = EnhancedUnhingedDesktopApp()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
