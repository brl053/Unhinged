
import logging; gui_logger = logging.getLogger(__name__)

"""
@llm-type control-system
@llm-legend tool.py - system control component
@llm-key Core functionality for tool
@llm-map Part of the Unhinged system architecture
@llm-axiom Maintains system independence and architectural compliance
@llm-contract Provides standardized interface for system integration
@llm-token tool: system control component
"""
"""
🚀 Service Manager Tool

Real-time service management with gRPC health.proto integration.
Control service lifecycle and monitor status via gRPC health endpoints.
"""

import gi
gi.require_version('Gtk', '4.0')

from gi.repository import Gtk, GLib
import threading
import time

from ...core.tool_manager import BaseTool
from ...health_client import HealthClient


class ServiceManagerTool(BaseTool):
    """
    Service Manager tool plugin.
    
    Manages service lifecycle and monitoring.
    """
    
    def __init__(self):
        super().__init__()
        self.name = "Services"
        self.icon = "🚀"
        self.description = "Service Manager - Real-time gRPC health monitoring and control"
        self.shortcut = "Ctrl+4"

        # Initialize health client
        self.health_client = HealthClient()
        self.service_rows = {}  # Track service UI rows
        self.refresh_thread = None
        self.should_refresh = False
    
    def create_widget(self):
        """Create the service manager widget"""
        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        main_box.set_margin_start(16)
        main_box.set_margin_end(16)
        main_box.set_margin_top(16)
        main_box.set_margin_bottom(16)
        
        # Title
        title_label = Gtk.Label(label="🚀 Service Manager")
        title_label.add_css_class("title")
        main_box.append(title_label)
        
        # Services list
        services_frame = Gtk.Frame()
        services_frame.set_label("Services")
        
        services_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        services_box.set_margin_start(16)
        services_box.set_margin_end(16)
        services_box.set_margin_top(12)
        services_box.set_margin_bottom(12)
        
        # Add real services from health client
        self.services_box = services_box  # Store reference for updates
        self._populate_services()

        # Start background refresh
        self._start_refresh_thread()
        
        services_frame.set_child(services_box)
        main_box.append(services_frame)
        
        gui_logger.info(" Service Manager widget created", {"status": "success"})
        return main_box
    
    def _create_service_row(self, name, status, port):
        """Create a service control row"""
        row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        row_box.set_margin_top(4)
        row_box.set_margin_bottom(4)
        
        # Service name
        name_label = Gtk.Label(label=name)
        name_label.set_halign(Gtk.Align.START)
        name_label.set_hexpand(True)
        row_box.append(name_label)
        
        # Port
        port_label = Gtk.Label(label=f":{port}")
        port_label.add_css_class("metric-label")
        row_box.append(port_label)
        
        # Status
        status_label = Gtk.Label(label=status.title())
        if status == "running":
            status_label.add_css_class("status-success")
        else:
            status_label.add_css_class("status-error")
        row_box.append(status_label)
        
        # Control buttons
        if status == "running":
            stop_button = Gtk.Button(label="Stop")
            stop_button.add_css_class("danger-button")
            stop_button.connect("clicked", self._on_stop_service, name)
            row_box.append(stop_button)
            
            restart_button = Gtk.Button(label="Restart")
            restart_button.add_css_class("secondary-button")
            restart_button.connect("clicked", self._on_restart_service, name)
            row_box.append(restart_button)
        else:
            start_button = Gtk.Button(label="Start")
            start_button.add_css_class("primary-button")
            start_button.connect("clicked", self._on_start_service, name)
            row_box.append(start_button)
        
        return row_box
    
    def _on_start_service(self, button, service_name):
        """Handle start service button"""
        button.set_label("Starting...")
        button.set_sensitive(False)
        # TODO: Implement actual service start
    
    def _on_stop_service(self, button, service_name):
        """Handle stop service button"""
        button.set_label("Stopping...")
        button.set_sensitive(False)
        # TODO: Implement actual service stop
    
    def _on_restart_service(self, button, service_name):
        """Handle restart service button"""
        button.set_label("Restarting...")
        button.set_sensitive(False)
        # TODO: Implement actual service restart
    
    def get_actions(self):
        """Get tool-specific header actions"""
        return [
            {
                'label': '🔄 Refresh',
                'callback': self._on_refresh_clicked,
                'css_class': 'secondary-button'
            },
            {
                'label': '🚀 Start All',
                'callback': self._on_start_all_clicked,
                'css_class': 'primary-button'
            }
        ]
    
    def _populate_services(self):
        """Populate services from health client"""
        for service_name in self.health_client.get_service_list():
            service_row = self._create_service_row(service_name, "checking", "unknown")
            self.services_box.append(service_row)
            self.service_rows[service_name] = service_row

    def _start_refresh_thread(self):
        """Start background thread for service health monitoring"""
        self.should_refresh = True
        self.refresh_thread = threading.Thread(target=self._refresh_loop, daemon=True)
        self.refresh_thread.start()

    def _refresh_loop(self):
        """Background loop to refresh service status"""
        while self.should_refresh:
            try:
                # Check all services
                results = self.health_client.check_all_services()

                # Update UI on main thread
                GLib.idle_add(self._update_service_status, results)

                # Wait before next refresh
                time.sleep(5)  # Refresh every 5 seconds
            except Exception as e:
                time.sleep(10)  # Wait longer on error

    def _update_service_status(self, results):
        """Update service status in UI (called on main thread)"""
        for service_name, result in results.items():
            if service_name in self.service_rows:
                row = self.service_rows[service_name]
                is_healthy = result["healthy"]
                data = result["data"]

                # Update status based on health check
                if is_healthy:
                    status = data.get("status", "healthy")
                    port = self.health_client.services[service_name]["port"]
                    response_time = data.get("response_time_ms", 0)
                    self._update_service_row(row, service_name, status, str(port), response_time)
                else:
                    error = data.get("error", "unknown error")
                    self._update_service_row(row, service_name, "unhealthy", "error", 0, error)

        return False  # Don't repeat this idle callback

    def _update_service_row(self, row, name, status, port, response_time=0, error=None):
        """Update a service row with new status"""
        # This is a simplified update - in a real implementation,
        # you'd need to access the specific labels and buttons in the row
        # For now, just print the update
        if error:
            pass
        else:

            pass
    def _on_refresh_clicked(self, button):
        """Handle refresh button click"""
        # Force immediate refresh
        threading.Thread(target=self._force_refresh, daemon=True).start()

    def _force_refresh(self):
        """Force immediate service status refresh"""
        try:
            results = self.health_client.check_all_services()
            GLib.idle_add(self._update_service_status, results)
        except Exception as e:

            pass
    def _on_start_all_clicked(self, button):
        """Handle start all button click"""
        gui_logger.info(" Starting all services...", {"event_type": "startup"})
        # In a real implementation, this would start Docker containers
        # or systemd services for each service
