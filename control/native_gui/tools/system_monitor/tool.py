
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
🏥 System Health Monitor Tool

Placeholder implementation for system monitoring.
Shows CPU, memory, disk usage, and service status.
"""

import gi
gi.require_version('Gtk', '4.0')

from gi.repository import Gtk, GLib
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    gui_logger.warn(" psutil not available - install with: pip install psutil")

import time

from ...core.tool_manager import BaseTool
from ...core.tool_config import ToolConfigFactory
from ...ui.widget_factory import WidgetFactory


class SystemMonitorTool(BaseTool):
    """
    System Health Monitor tool plugin.
    
    Displays real-time system metrics and service status.
    """
    
    def __init__(self):
        # Use ToolConfig for standardized initialization
        config = ToolConfigFactory.create_system_tool(
            name="Health",
            icon="🏥",
            description="System Health Monitor - CPU, memory, disk, and service status"
        )
        super().__init__(config)
        self.shortcut = "Ctrl+2"
        
        # Monitoring state
        self.monitoring = False
        self.update_timeout = None
    
    def create_widget(self):
        """Create the system monitor widget using WidgetFactory"""
        # Main container using WidgetFactory
        main_box = WidgetFactory.create_main_container(spacing=16)
        main_box.add_css_class("system-monitor")

        # Header using WidgetFactory
        header = WidgetFactory.create_header_box(
            title="🏥 System Health Monitor",
            subtitle="Real-time system performance metrics"
        )
        main_box.append(header)
        
        # Metrics grid
        metrics_grid = Gtk.Grid()
        metrics_grid.set_row_spacing(16)
        metrics_grid.set_column_spacing(16)
        metrics_grid.set_column_homogeneous(True)
        
        # CPU metric card
        self.cpu_card = self._create_metric_card("🔥 CPU Usage", "0%", "Processor utilization")
        metrics_grid.attach(self.cpu_card, 0, 0, 1, 1)
        
        # Memory metric card
        self.memory_card = self._create_metric_card("🧠 Memory", "0 GB", "RAM usage")
        metrics_grid.attach(self.memory_card, 1, 0, 1, 1)
        
        # Disk metric card
        self.disk_card = self._create_metric_card("💾 Disk", "0 GB", "Storage usage")
        metrics_grid.attach(self.disk_card, 2, 0, 1, 1)
        
        # Network metric card
        self.network_card = self._create_metric_card("🌐 Network", "0 KB/s", "Network activity")
        metrics_grid.attach(self.network_card, 3, 0, 1, 1)
        
        main_box.append(metrics_grid)
        
        # Services section
        services_label = Gtk.Label(label="🚀 Services Status")
        services_label.add_css_class("title")
        services_label.set_margin_top(16)
        main_box.append(services_label)
        
        # Services list
        self.services_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        main_box.append(self.services_box)
        
        # Add some placeholder services
        self._add_service_status("Service Discovery", "running", "Port 8500")
        self._add_service_status("API Gateway", "running", "Port 8080")
        self._add_service_status("Database", "running", "Port 5432")
        self._add_service_status("Cache", "stopped", "Port 6379")
        
        gui_logger.info(" System Monitor widget created", {"status": "success"})
        return main_box
    
    def _create_metric_card(self, title, value, description):
        """Create a metric display card"""
        card = Gtk.Frame()
        card.add_css_class("metric-card")
        
        card_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        card_box.set_margin_start(16)
        card_box.set_margin_end(16)
        card_box.set_margin_top(12)
        card_box.set_margin_bottom(12)
        
        # Title
        title_label = Gtk.Label(label=title)
        title_label.set_halign(Gtk.Align.START)
        card_box.append(title_label)
        
        # Value
        value_label = Gtk.Label(label=value)
        value_label.add_css_class("metric-value")
        value_label.set_halign(Gtk.Align.START)
        card_box.append(value_label)
        
        # Description
        desc_label = Gtk.Label(label=description)
        desc_label.add_css_class("metric-label")
        desc_label.set_halign(Gtk.Align.START)
        card_box.append(desc_label)
        
        card.set_child(card_box)
        
        # Store value label for updates
        card.value_label = value_label
        
        return card
    
    def _add_service_status(self, name, status, details):
        """Add a service status item"""
        service_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        service_box.add_css_class("service-card")
        service_box.set_margin_start(8)
        service_box.set_margin_end(8)
        service_box.set_margin_top(4)
        service_box.set_margin_bottom(4)
        
        # Status indicator
        status_label = Gtk.Label(label="●")
        if status == "running":
            status_label.add_css_class("service-status")
            status_label.add_css_class("running")
        elif status == "stopped":
            status_label.add_css_class("service-status")
            status_label.add_css_class("stopped")
        else:
            status_label.add_css_class("service-status")
            status_label.add_css_class("unknown")
        
        service_box.append(status_label)
        
        # Service name
        name_label = Gtk.Label(label=name)
        name_label.set_halign(Gtk.Align.START)
        name_label.set_hexpand(True)
        service_box.append(name_label)
        
        # Details
        details_label = Gtk.Label(label=details)
        details_label.add_css_class("metric-label")
        service_box.append(details_label)
        
        # Status text
        status_text_label = Gtk.Label(label=status.title())
        status_text_label.add_css_class("service-status")
        status_text_label.add_css_class(status)
        service_box.append(status_text_label)
        
        self.services_box.append(service_box)
    
    def on_activate(self):
        """Start monitoring when tool becomes active"""
        super().on_activate()
        self.start_monitoring()
    
    def on_deactivate(self):
        """Stop monitoring when tool becomes inactive"""
        super().on_deactivate()
        self.stop_monitoring()
    
    def start_monitoring(self):
        """Start real-time monitoring"""
        if not self.monitoring:
            self.monitoring = True
            self._update_metrics()
    
    def stop_monitoring(self):
        """Stop real-time monitoring"""
        if self.monitoring:
            self.monitoring = False
            if self.update_timeout:
                GLib.source_remove(self.update_timeout)
                self.update_timeout = None
    
    def _update_metrics(self):
        """Update system metrics"""
        if not self.monitoring:
            return False
        
        try:
            if PSUTIL_AVAILABLE:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=None)
                self.cpu_card.value_label.set_text(f"{cpu_percent:.1f}%")

                # Memory usage
                memory = psutil.virtual_memory()
                memory_gb = memory.used / (1024**3)
                self.memory_card.value_label.set_text(f"{memory_gb:.1f} GB")

                # Disk usage
                disk = psutil.disk_usage('/')
                disk_gb = disk.used / (1024**3)
                self.disk_card.value_label.set_text(f"{disk_gb:.1f} GB")

                # Network (placeholder)
                self.network_card.value_label.set_text("0 KB/s")
            else:
                # Placeholder values when psutil not available
                self.cpu_card.value_label.set_text("N/A")
                self.memory_card.value_label.set_text("N/A")
                self.disk_card.value_label.set_text("N/A")
                self.network_card.value_label.set_text("N/A")

        except Exception as e:
            gui_logger.error(f" Error updating metrics: {e}")
        
        # Schedule next update
        self.update_timeout = GLib.timeout_add_seconds(2, self._update_metrics)
        return False  # Don't repeat automatically
    
    def get_actions(self):
        """Get tool-specific header actions"""
        return [
            {
                'label': '🔄 Refresh',
                'callback': self._on_refresh_clicked,
                'css_class': 'secondary-button'
            }
        ]
    
    def _on_refresh_clicked(self, button):
        """Handle refresh button click"""
        self._update_metrics()
