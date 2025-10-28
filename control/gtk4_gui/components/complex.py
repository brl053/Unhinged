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

from gi.repository import Gtk, Adw, GLib, GLib, GObject
from typing import Dict, List, Optional, Callable
from base import ComponentBase, AdwComponentBase
from primitives import ActionButton, StatusLabel, ProgressIndicator
from containers import StatusCard, ServicePanel, LogContainer, SystemInfoCard


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


class PerformanceIndicator(AdwComponentBase):
    """
    Real-time performance metrics display component.

    Features:
    - CPU, memory, and disk usage indicators
    - Progress bars with semantic color coding
    - Real-time updates with smooth animations
    - Configurable thresholds for warning/error states
    """

    def __init__(self,
                 metric_type: str = "cpu",
                 title: str = "",
                 current_value: float = 0.0,
                 max_value: float = 100.0,
                 unit: str = "%",
                 warning_threshold: float = 75.0,
                 error_threshold: float = 90.0,
                 **kwargs):
        self.metric_type = metric_type
        self.title = title or self._get_default_title()
        self.current_value = current_value
        self.max_value = max_value
        self.unit = unit
        self.warning_threshold = warning_threshold
        self.error_threshold = error_threshold

        self._progress_bar = None
        self._value_label = None
        self._status_icon = None
        self._main_row = None
        self._update_timeout_id = None
        self._auto_update = False
        self._update_interval = 2.0  # seconds

        super().__init__("performance-indicator", **kwargs)

    def _init_component(self, **kwargs):
        """Initialize the performance indicator."""
        # Create preferences group for structure
        self.widget = Adw.PreferencesGroup()
        self.widget.set_title(self.title)

        # Create main row
        self._main_row = Adw.ActionRow()
        self._main_row.set_title(self.title)

        # Add metric icon
        self._setup_metric_icon(self._main_row)

        # Add progress bar
        self._setup_progress_bar(self._main_row)

        # Add value label
        self._setup_value_label(self._main_row)

        # Add status indicator
        self._setup_status_indicator(self._main_row)

        self.widget.add(self._main_row)

        # Apply styling
        self.add_css_class("ds-performance-indicator")
        self.add_css_class(f"metric-{self.metric_type}")

        # Apply initial status styling
        percentage = (self.current_value / self.max_value) * 100 if self.max_value > 0 else 0
        if percentage >= self.error_threshold:
            self.add_css_class("status-error")
        elif percentage >= self.warning_threshold:
            self.add_css_class("status-warning")
        else:
            self.add_css_class("status-success")

        # Add accessibility attributes
        self.widget.set_accessible_role(Gtk.AccessibleRole.GROUP)
        self.widget.update_property([Gtk.AccessibleProperty.LABEL], [f"Performance Metric: {self.title}"])

        # Update display
        self._update_display()

    def _get_default_title(self) -> str:
        """Get default title based on metric type."""
        titles = {
            "cpu": "CPU Usage",
            "memory": "Memory Usage",
            "disk": "Disk Usage",
            "network": "Network Usage",
            "temperature": "Temperature",
            "generic": "Performance"
        }
        return titles.get(self.metric_type, "Performance")

    def _setup_metric_icon(self, row: Adw.ActionRow):
        """Setup metric type icon."""
        icon_map = {
            "cpu": "cpu-symbolic",
            "memory": "memory-symbolic",
            "disk": "drive-harddisk-symbolic",
            "network": "network-wired-symbolic",
            "temperature": "temperature-symbolic",
            "generic": "utilities-system-monitor-symbolic"
        }

        icon_name = icon_map.get(self.metric_type, "utilities-system-monitor-symbolic")
        icon = Gtk.Image.new_from_icon_name(icon_name)
        icon.set_icon_size(Gtk.IconSize.LARGE)
        icon.add_css_class(f"metric-{self.metric_type}")
        row.add_prefix(icon)

    def _setup_progress_bar(self, row: Adw.ActionRow):
        """Setup progress bar for metric display."""
        self._progress_bar = Gtk.ProgressBar()
        self._progress_bar.set_size_request(150, -1)
        self._progress_bar.set_show_text(False)  # We'll use separate label

        # Create container for progress bar
        progress_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        progress_box.append(self._progress_bar)

        row.add_suffix(progress_box)

    def _setup_value_label(self, row: Adw.ActionRow):
        """Setup value display label."""
        self._value_label = Gtk.Label()
        self._value_label.add_css_class("title-4")
        self._value_label.add_css_class("numeric")
        self._value_label.set_size_request(80, -1)
        self._value_label.set_xalign(1.0)  # Right align

        row.add_suffix(self._value_label)

    def _setup_status_indicator(self, row: Adw.ActionRow):
        """Setup status indicator icon."""
        self._status_icon = Gtk.Image()
        self._status_icon.set_icon_size(Gtk.IconSize.NORMAL)
        row.add_suffix(self._status_icon)

    def _update_display(self):
        """Update the display with current values."""
        # Calculate percentage
        percentage = (self.current_value / self.max_value) * 100 if self.max_value > 0 else 0

        # Update progress bar
        self._progress_bar.set_fraction(min(percentage / 100, 1.0))

        # Update value label
        if self.unit == "%":
            self._value_label.set_text(f"{percentage:.1f}%")
        else:
            self._value_label.set_text(f"{self.current_value:.1f} {self.unit}")

        # Update status and styling
        self._update_status_styling(percentage)

    def _update_status_styling(self, percentage: float):
        """Update status styling based on thresholds."""
        # Remove existing status classes
        for status in ["normal", "warning", "error"]:
            self._progress_bar.remove_css_class(status)
            self._status_icon.remove_css_class(status)

        # Determine status
        if percentage >= self.error_threshold:
            status = "error"
            icon_name = "dialog-error-symbolic"
        elif percentage >= self.warning_threshold:
            status = "warning"
            icon_name = "dialog-warning-symbolic"
        else:
            status = "normal"
            icon_name = "emblem-ok-symbolic"

        # Apply status styling
        self._progress_bar.add_css_class(status)
        self._status_icon.add_css_class(status)
        self._status_icon.set_from_icon_name(icon_name)

        # Update subtitle with status
        if self._main_row:
            if status == "error":
                self._main_row.set_subtitle("Critical usage level")
            elif status == "warning":
                self._main_row.set_subtitle("High usage level")
            else:
                self._main_row.set_subtitle("Normal usage level")

    def update_value(self, new_value: float):
        """Update the current value and refresh display."""
        self.current_value = new_value
        self._update_display()

    def set_thresholds(self, warning: float, error: float):
        """Update warning and error thresholds."""
        self.warning_threshold = warning
        self.error_threshold = error
        self._update_display()

    def get_status(self) -> str:
        """Get current status based on thresholds."""
        percentage = (self.current_value / self.max_value) * 100 if self.max_value > 0 else 0

        if percentage >= self.error_threshold:
            return "error"
        elif percentage >= self.warning_threshold:
            return "warning"
        else:
            return "normal"

    def start_auto_update(self, update_callback=None, interval: float = 2.0):
        """Start automatic updates with a callback function."""
        self._update_interval = interval
        self._auto_update = True
        self._update_callback = update_callback

        if self._update_timeout_id:
            GLib.source_remove(self._update_timeout_id)

        self._update_timeout_id = GLib.timeout_add(
            int(self._update_interval * 1000),  # Convert to milliseconds
            self._auto_update_callback
        )

    def stop_auto_update(self):
        """Stop automatic updates."""
        self._auto_update = False
        if self._update_timeout_id:
            GLib.source_remove(self._update_timeout_id)
            self._update_timeout_id = None

    def _auto_update_callback(self):
        """Callback for automatic updates."""
        if not self._auto_update:
            return False

        try:
            if hasattr(self, '_update_callback') and self._update_callback:
                new_value = self._update_callback(self.metric_type)
                if new_value is not None:
                    self.update_value(new_value)
        except Exception as e:
            # Log error but continue updating
            print(f"Auto-update error for {self.metric_type}: {e}")

        return self._auto_update  # Continue if still auto-updating

    def cleanup(self):
        """Clean up resources."""
        self.stop_auto_update()
        super().cleanup()
