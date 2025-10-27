"""
@llm-doc Complex GTK4 Components
@llm-version 1.0.0
@llm-date 2025-10-27

Complex components that combine multiple elements:
- LogViewer: Advanced log viewer with filtering and search
- ServiceRow: Complete service status row with controls
- SystemStatus: Overall system status display
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GLib, GObject
from typing import Dict, List, Optional, Callable
from base import ComponentBase, AdwComponentBase
from primitives import ActionButton, StatusLabel, ProgressIndicator
from containers import StatusCard, ServicePanel, LogContainer


class LogViewer(AdwComponentBase):
    """
    Advanced log viewer with filtering, search, and export capabilities.
    
    Features:
    - Real-time log streaming
    - Text filtering and search
    - Log level filtering
    - Export functionality
    - Auto-scroll toggle
    """
    
    __gsignals__ = {
        'filter-changed': (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        'export-requested': (GObject.SignalFlags.RUN_FIRST, None, ()),
    }
    
    def __init__(self, **kwargs):
        self._log_container = None
        self._search_entry = None
        self._filter_dropdown = None
        self._auto_scroll_toggle = None
        self._export_button = None
        self._current_filter = ""
        self._log_levels = ["ALL", "DEBUG", "INFO", "WARNING", "ERROR"]
        
        super().__init__("log-viewer", **kwargs)
    
    def _init_component(self, **kwargs):
        """Initialize the log viewer."""
        # Create main container
        self.widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        
        # Create toolbar
        toolbar = self._create_toolbar()
        self.widget.append(toolbar)
        
        # Create log container
        self._log_container = LogContainer()
        self.widget.append(self._log_container.get_widget())
        
        # Apply styling
        self.add_css_class("ds-log-viewer")
    
    def _create_toolbar(self) -> Gtk.Widget:
        """Create the log viewer toolbar."""
        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        toolbar.add_css_class("toolbar")
        
        # Search entry
        self._search_entry = Gtk.SearchEntry()
        self._search_entry.set_placeholder_text("Search logs...")
        self._search_entry.connect('search-changed', self._on_search_changed)
        toolbar.append(self._search_entry)
        
        # Filter dropdown
        filter_model = Gtk.StringList()
        for level in self._log_levels:
            filter_model.append(level)
        
        self._filter_dropdown = Gtk.DropDown(model=filter_model)
        self._filter_dropdown.set_selected(0)  # ALL
        self._filter_dropdown.connect('notify::selected', self._on_filter_changed)
        toolbar.append(self._filter_dropdown)
        
        # Auto-scroll toggle
        self._auto_scroll_toggle = Gtk.ToggleButton()
        self._auto_scroll_toggle.set_icon_name("view-continuous-symbolic")
        self._auto_scroll_toggle.set_tooltip_text("Auto-scroll to bottom")
        self._auto_scroll_toggle.set_active(True)
        self._auto_scroll_toggle.connect('toggled', self._on_auto_scroll_toggled)
        toolbar.append(self._auto_scroll_toggle)
        
        # Export button
        self._export_button = ActionButton(
            label="Export",
            style="flat",
            icon_name="document-save-symbolic"
        )
        self._export_button.connect('clicked', self._on_export_clicked)
        toolbar.append(self._export_button.get_widget())
        
        return toolbar
    
    def _on_search_changed(self, entry):
        """Handle search text changes."""
        search_text = entry.get_text()
        self._current_filter = search_text
        self.emit('filter-changed', search_text)
    
    def _on_filter_changed(self, dropdown, param):
        """Handle log level filter changes."""
        selected = dropdown.get_selected()
        level = self._log_levels[selected]
        # Implement log level filtering logic here
        pass
    
    def _on_auto_scroll_toggled(self, toggle):
        """Handle auto-scroll toggle."""
        auto_scroll = toggle.get_active()
        self._log_container.auto_scroll = auto_scroll
    
    def _on_export_clicked(self, button):
        """Handle export button click."""
        self.emit('export-requested')
    
    def append_log(self, message: str, level: str = "INFO", timestamp: Optional[str] = None):
        """Add a log message."""
        # Format log message
        if timestamp:
            formatted_message = f"[{timestamp}] {level}: {message}"
        else:
            formatted_message = f"{level}: {message}"
        
        # Add to log container
        self._log_container.append_text(formatted_message)
    
    def clear_logs(self):
        """Clear all log messages."""
        self._log_container.clear()
    
    def get_log_text(self) -> str:
        """Get all log text."""
        return self._log_container.get_text()


class ServiceRow(AdwComponentBase):
    """
    Complete service status row with controls and status display.
    
    Features:
    - Service name and status
    - Health indicator with method
    - Start/stop/restart controls
    - Expandable details
    """
    
    __gsignals__ = {
        'action-requested': (GObject.SignalFlags.RUN_FIRST, None, (str, str)),
    }
    
    def __init__(self,
                 service_name: str,
                 service_data: Dict,
                 **kwargs):
        self.service_name = service_name
        self.service_data = service_data
        self._service_panel = None
        self._action_buttons = {}
        
        super().__init__("service-row", **kwargs)
    
    def _init_component(self, **kwargs):
        """Initialize the service row."""
        # Create service panel
        self._service_panel = ServicePanel(
            service_name=self.service_name,
            service_status="running" if self.service_data.get("running") else "stopped",
            port=self.service_data.get("port"),
            health_method=self.service_data.get("health_method", "unknown")
        )
        
        # Add action buttons
        self._create_action_buttons()
        
        # Set main widget
        self.widget = self._service_panel.get_widget()
        
        # Apply styling
        self.add_css_class("ds-service-row")
    
    def _create_action_buttons(self):
        """Create action buttons for the service."""
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        
        # Start/Stop button
        if self.service_data.get("running"):
            stop_button = ActionButton(
                label="Stop",
                style="destructive",
                icon_name="process-stop-symbolic"
            )
            stop_button.connect('clicked', lambda b: self._on_action_clicked("stop"))
            self._action_buttons["stop"] = stop_button
            button_box.append(stop_button.get_widget())
        else:
            start_button = ActionButton(
                label="Start",
                style="primary",
                icon_name="media-playback-start-symbolic"
            )
            start_button.connect('clicked', lambda b: self._on_action_clicked("start"))
            self._action_buttons["start"] = start_button
            button_box.append(start_button.get_widget())
        
        # Restart button
        restart_button = ActionButton(
            label="Restart",
            style="secondary",
            icon_name="view-refresh-symbolic"
        )
        restart_button.connect('clicked', lambda b: self._on_action_clicked("restart"))
        self._action_buttons["restart"] = restart_button
        button_box.append(restart_button.get_widget())
        
        # Add button box to service panel
        self._service_panel.add_action_button(button_box)
    
    def _on_action_clicked(self, action: str):
        """Handle action button clicks."""
        self.emit('action-requested', self.service_name, action)
    
    def update_service_data(self, service_data: Dict):
        """Update service data and refresh display."""
        self.service_data = service_data
        
        # Update status
        status = "running" if service_data.get("running") else "stopped"
        self._service_panel.set_service_status(status)
        
        # Recreate action buttons if status changed
        # This is a simplified approach - in production you'd update buttons more efficiently
        self._create_action_buttons()


class SystemStatus(AdwComponentBase):
    """
    Overall system status display with service overview.
    
    Features:
    - Overall health indicator
    - Service count summary
    - Quick actions
    - Status breakdown
    """
    
    def __init__(self, **kwargs):
        self._services_data = {}
        self._status_card = None
        self._services_summary = None
        self._quick_actions = None
        
        super().__init__("system-status", **kwargs)
    
    def _init_component(self, **kwargs):
        """Initialize the system status display."""
        # Create main container
        self.widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        
        # Create status card
        self._status_card = StatusCard(
            title="System Status",
            status="neutral",
            subtitle="Checking services...",
            icon_name="computer-symbolic"
        )
        self.widget.append(self._status_card.get_widget())
        
        # Create services summary
        self._services_summary = Adw.PreferencesGroup()
        self._services_summary.set_title("Services Overview")
        self.widget.append(self._services_summary)
        
        # Apply styling
        self.add_css_class("ds-system-status")
    
    def update_services(self, services_data: Dict):
        """Update system status with services data."""
        self._services_data = services_data
        
        # Calculate overall status
        total_services = len(services_data)
        running_services = sum(1 for data in services_data.values() if data.get("running"))
        
        # Update status card
        if running_services == total_services:
            status = "success"
            subtitle = f"All {total_services} services running"
        elif running_services == 0:
            status = "error"
            subtitle = "No services running"
        else:
            status = "warning"
            subtitle = f"{running_services}/{total_services} services running"
        
        self._status_card.set_status(status)
        self._status_card.set_subtitle(subtitle)
        
        # Update services summary
        self._update_services_summary()
    
    def _update_services_summary(self):
        """Update the services summary display."""
        # Clear existing summary
        child = self._services_summary.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self._services_summary.remove(child)
            child = next_child
        
        # Group services by status
        running = []
        stopped = []
        
        for name, data in self._services_data.items():
            if data.get("running"):
                running.append(name)
            else:
                stopped.append(name)
        
        # Add running services
        if running:
            running_row = Adw.ActionRow()
            running_row.set_title("Running Services")
            running_row.set_subtitle(", ".join(running))
            
            running_icon = Gtk.Image.new_from_icon_name("emblem-ok-symbolic")
            running_icon.add_css_class("success")
            running_row.add_prefix(running_icon)
            
            self._services_summary.add(running_row)
        
        # Add stopped services
        if stopped:
            stopped_row = Adw.ActionRow()
            stopped_row.set_title("Stopped Services")
            stopped_row.set_subtitle(", ".join(stopped))
            
            stopped_icon = Gtk.Image.new_from_icon_name("process-stop-symbolic")
            stopped_icon.add_css_class("error")
            stopped_row.add_prefix(stopped_icon)
            
            self._services_summary.add(stopped_row)
