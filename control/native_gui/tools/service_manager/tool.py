"""
🚀 Service Manager Tool

Placeholder implementation for service management.
Control service lifecycle and monitor status.
"""

import gi
gi.require_version('Gtk', '4.0')

from gi.repository import Gtk

from ...core.tool_manager import BaseTool


class ServiceManagerTool(BaseTool):
    """
    Service Manager tool plugin.
    
    Manages service lifecycle and monitoring.
    """
    
    def __init__(self):
        super().__init__()
        self.name = "Services"
        self.icon = "🚀"
        self.description = "Service Manager - Start, stop, restart, and monitor services"
        self.shortcut = "Ctrl+4"
    
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
        
        # Add sample services
        services = [
            ("Service Discovery", "running", "8500"),
            ("API Gateway", "running", "8080"),
            ("User Service", "stopped", "8001"),
            ("Auth Service", "running", "8002"),
            ("Database", "running", "5432"),
            ("Cache", "stopped", "6379")
        ]
        
        for name, status, port in services:
            service_row = self._create_service_row(name, status, port)
            services_box.append(service_row)
        
        services_frame.set_child(services_box)
        main_box.append(services_frame)
        
        print("✅ Service Manager widget created")
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
        print(f"🚀 Starting service: {service_name}")
        button.set_label("Starting...")
        button.set_sensitive(False)
        # TODO: Implement actual service start
    
    def _on_stop_service(self, button, service_name):
        """Handle stop service button"""
        print(f"🛑 Stopping service: {service_name}")
        button.set_label("Stopping...")
        button.set_sensitive(False)
        # TODO: Implement actual service stop
    
    def _on_restart_service(self, button, service_name):
        """Handle restart service button"""
        print(f"🔄 Restarting service: {service_name}")
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
    
    def _on_refresh_clicked(self, button):
        """Handle refresh button click"""
        print("🔄 Refreshing service status...")
    
    def _on_start_all_clicked(self, button):
        """Handle start all button click"""
        print("🚀 Starting all services...")
