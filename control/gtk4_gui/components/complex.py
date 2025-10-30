"""
@llm-doc Complex GTK4 Components
@llm-version 1.0.0
@llm-date 2025-10-28

Complex components that combine multiple elements for comprehensive interfaces:
- LogViewer: Advanced log viewer with filtering and search
- ServiceRow: Complete service status row with controls
- SystemStatus: Overall system status display
- PerformanceIndicator: System performance monitoring display
- ProcessTable: Complete process management interface
- BluetoothTable: Bluetooth device management with discovery
- AudioTable: Audio device management with volume control
"""

import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')


from gi.repository import Adw, GLib, GObject, Gtk

from .base import AdwComponentBase
from .containers import LogContainer, ServicePanel, StatusCard
from .primitives import ActionButton


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

    def append_log(self, message: str, level: str = "INFO", timestamp: str | None = None):
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
                 service_data: dict,
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

    def update_service_data(self, service_data: dict):
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

    def update_services(self, services_data: dict):
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


class ProcessTable(AdwComponentBase):
    """
    Live process monitoring table with aux/top command equivalence.

    Features:
    - Table header with sortable columns (PID, Name, CPU%, Memory%, User)
    - Search bar for process name/command filtering
    - User filter dropdown
    - Pagination with configurable limits
    - Process management actions with confirmations
    - Real-time update integration
    """

    def __init__(self, **kwargs):
        # Import required modules
        import sys
        from pathlib import Path
        sys.path.append(str(Path(__file__).parent))


        # Configuration
        self.current_processes = []
        self.process_limit = 50
        self.include_system_processes = True
        self.sort_column = 'cpu_percent'
        self.filter_text = ""
        self.filter_user = None

        # UI Components
        self.search_entry = None
        self.user_filter_dropdown = None
        self.process_table = None
        self.status_label = None
        self.refresh_button = None

        # Real-time updates
        self.auto_refresh = False
        self.refresh_interval = 2.0  # seconds
        self.refresh_timeout_id = None

        super().__init__("process-table", **kwargs)

    def _init_component(self, **kwargs):
        """Initialize the process table."""
        # Create main container
        self.widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)

        # Setup UI
        self._setup_ui()
        self._setup_table()
        self._load_initial_data()

        # Apply styling
        self.add_css_class("ds-process-table")

    def _setup_ui(self):
        """Setup the main UI structure."""
        # Create header with controls
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        header_box.set_margin_bottom(12)

        # Search entry
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Search processes...")
        self.search_entry.set_hexpand(True)
        self.search_entry.connect("search-changed", self._on_search_changed)
        header_box.append(self.search_entry)

        # User filter dropdown
        user_filter_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        user_label = Gtk.Label(label="User:")
        user_label.add_css_class("ds-text-caption")

        self.user_filter_dropdown = Gtk.DropDown()
        self.user_filter_dropdown.set_tooltip_text("Filter by user")
        self.user_filter_dropdown.connect("notify::selected", self._on_user_filter_changed)

        user_filter_box.append(user_label)
        user_filter_box.append(self.user_filter_dropdown)
        header_box.append(user_filter_box)

        # System processes toggle
        system_toggle = Gtk.ToggleButton()
        system_toggle.set_label("System")
        system_toggle.set_active(self.include_system_processes)
        system_toggle.set_tooltip_text("Include system processes")
        system_toggle.connect("toggled", self._on_system_toggle)
        header_box.append(system_toggle)

        # Refresh button
        self.refresh_button = Gtk.Button()
        self.refresh_button.set_icon_name("view-refresh-symbolic")
        self.refresh_button.set_tooltip_text("Refresh process list")
        self.refresh_button.connect("clicked", self._on_refresh_clicked)
        header_box.append(self.refresh_button)

        self.widget.append(header_box)

        # Status bar
        status_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        status_box.set_margin_bottom(6)

        self.status_label = Gtk.Label()
        self.status_label.set_halign(Gtk.Align.START)
        self.status_label.add_css_class("ds-text-caption")
        status_box.append(self.status_label)

        # Auto-refresh toggle
        auto_refresh_toggle = Gtk.ToggleButton()
        auto_refresh_toggle.set_label("Auto-refresh")
        auto_refresh_toggle.set_active(self.auto_refresh)
        auto_refresh_toggle.set_tooltip_text("Enable automatic refresh")
        auto_refresh_toggle.connect("toggled", self._on_auto_refresh_toggle)
        status_box.append(auto_refresh_toggle)

        self.widget.append(status_box)

    def _setup_table(self):
        """Setup the process table."""
        from .tables import GenericTable, TableColumn

        # Define columns
        columns = [
            TableColumn('pid', 'PID', sortable=True, width=80),
            TableColumn('name', 'Name', sortable=True, width=150),
            TableColumn('cpu_percent', 'CPU%', sortable=True, width=80),
            TableColumn('memory_percent', 'Memory%', sortable=True, width=80),
            TableColumn('user', 'User', sortable=True, width=100),
            TableColumn('status', 'Status', sortable=True, width=80),
            TableColumn('command', 'Command', sortable=False, width=-1)
        ]

        # Create table
        self.process_table = GenericTable(columns, self._create_process_row)
        self.process_table.set_vexpand(True)
        self.process_table.set_hexpand(True)

        # Set callbacks
        self.process_table.set_sort_changed_callback(self._on_sort_changed)
        self.process_table.set_selection_changed_callback(self._on_process_selected)

        self.widget.append(self.process_table)

    def _create_process_row(self, process_info):
        """Create a ProcessRow for the given process info."""
        from .primitives import ProcessRow
        process_row = ProcessRow(process_info)
        return process_row.get_widget()

    def _load_initial_data(self):
        """Load initial process data."""
        self._refresh_process_list()
        self._update_user_filter()

    def _refresh_process_list(self):
        """Refresh the process list."""
        try:
            # Import process monitor
            import sys
            from pathlib import Path
            sys.path.append(str(Path(__file__).parent.parent))
            from process_monitor import ProcessMonitor

            # Show loading state
            self.refresh_button.set_sensitive(False)
            self.status_label.set_text("Loading processes...")

            # Get processes
            monitor = ProcessMonitor()
            processes = monitor.get_process_list(self.include_system_processes)

            # Apply filters
            filtered_processes = self._apply_filters(processes)

            # Sort processes
            sorted_processes = self._sort_processes(filtered_processes)

            # Limit results
            limited_processes = sorted_processes[:self.process_limit]

            # Update table
            self.process_table.set_data(limited_processes)
            self.current_processes = limited_processes

            # Update status
            total_count = len(processes)
            filtered_count = len(filtered_processes)
            displayed_count = len(limited_processes)

            status_text = f"Showing {displayed_count} of {filtered_count} processes"
            if filtered_count != total_count:
                status_text += f" (filtered from {total_count})"

            self.status_label.set_text(status_text)

        except Exception as e:
            self.status_label.set_text(f"Error loading processes: {e}")
            import logging
            logging.getLogger(__name__).error(f"Failed to refresh process list: {e}")

        finally:
            self.refresh_button.set_sensitive(True)

    def _apply_filters(self, processes):
        """Apply search and user filters to process list."""
        filtered = processes

        # Apply search filter
        if self.filter_text:
            search_lower = self.filter_text.lower()
            filtered = [
                p for p in filtered
                if (search_lower in p.name.lower() or
                    search_lower in p.command.lower() or
                    search_lower in str(p.pid))
            ]

        # Apply user filter
        if self.filter_user and self.filter_user != "All":
            filtered = [p for p in filtered if p.user == self.filter_user]

        return filtered

    def _sort_processes(self, processes):
        """Sort processes by current sort column."""
        if not self.sort_column or not processes:
            return processes

        reverse = self.sort_column in ['cpu_percent', 'memory_percent', 'memory_mb']

        try:
            return sorted(
                processes,
                key=lambda p: getattr(p, self.sort_column, 0),
                reverse=reverse
            )
        except (AttributeError, TypeError):
            return processes

    def _update_user_filter(self):
        """Update user filter dropdown with available users."""
        if not self.current_processes:
            return

        # Get unique users
        users = sorted(set(p.user for p in self.current_processes))
        users.insert(0, "All")  # Add "All" option

        # Create string list model
        model = Gtk.StringList()
        for user in users:
            model.append(user)

        self.user_filter_dropdown.set_model(model)
        self.user_filter_dropdown.set_selected(0)  # Select "All"

    def _on_search_changed(self, entry):
        """Handle search text changes."""
        self.filter_text = entry.get_text()
        self._refresh_process_list()

    def _on_user_filter_changed(self, dropdown, param):
        """Handle user filter changes."""
        selected = dropdown.get_selected()
        model = dropdown.get_model()
        if model and selected < model.get_n_items():
            self.filter_user = model.get_string(selected)
            self._refresh_process_list()

    def _on_system_toggle(self, toggle):
        """Handle system processes toggle."""
        self.include_system_processes = toggle.get_active()
        self._refresh_process_list()

    def _on_refresh_clicked(self, button):
        """Handle refresh button click."""
        self._refresh_process_list()

    def _on_auto_refresh_toggle(self, toggle):
        """Handle auto-refresh toggle."""
        self.auto_refresh = toggle.get_active()

        if self.auto_refresh:
            self._start_auto_refresh()
        else:
            self._stop_auto_refresh()

    def _on_sort_changed(self, column_name, direction):
        """Handle sort changes."""
        self.sort_column = column_name
        # Direction is already handled by the table
        self._refresh_process_list()

    def _on_process_selected(self, process_info):
        """Handle process selection."""
        if process_info:
            print(f"Selected process: {process_info.name} (PID: {process_info.pid})")

    def _start_auto_refresh(self):
        """Start automatic refresh."""
        if self.refresh_timeout_id:
            GLib.source_remove(self.refresh_timeout_id)

        self.refresh_timeout_id = GLib.timeout_add(
            int(self.refresh_interval * 1000),  # Convert to milliseconds
            self._auto_refresh_callback
        )

    def _stop_auto_refresh(self):
        """Stop automatic refresh."""
        if self.refresh_timeout_id:
            GLib.source_remove(self.refresh_timeout_id)
            self.refresh_timeout_id = None

    def _auto_refresh_callback(self):
        """Callback for automatic refresh."""
        if self.auto_refresh:
            self._refresh_process_list()
            return True  # Continue
        return False  # Stop

    def set_process_limit(self, limit: int):
        """Set the maximum number of processes to display."""
        self.process_limit = limit
        self._refresh_process_list()

    def get_selected_process(self):
        """Get the currently selected process."""
        return self.process_table.get_selected_data()

    def cleanup(self):
        """Clean up resources."""
        self._stop_auto_refresh()
        super().cleanup()


class BluetoothTable(AdwComponentBase):
    """
    Live Bluetooth device monitoring table with device discovery and management.

    Features:
    - Device discovery and scanning controls
    - Sortable columns (Name, Address, Type, Status, Signal)
    - Connection and pairing management
    - Device filtering and search
    - Real-time connection state updates
    """

    def __init__(self, **kwargs):
        # Import required modules
        import sys
        from pathlib import Path
        sys.path.append(str(Path(__file__).parent))


        # Configuration
        self.current_devices = []
        self.current_adapters = []
        self.include_unpaired = True
        self.sort_column = 'name'
        self.filter_text = ""
        self.filter_type = None

        # UI Components
        self.search_entry = None
        self.type_filter_dropdown = None
        self.bluetooth_table = None
        self.status_label = None
        self.discovery_button = None
        self.adapter_info_label = None

        # Discovery state
        self.discovery_active = False
        self.auto_refresh = True
        self.refresh_interval = 3.0  # seconds (slower than processes)
        self.refresh_timeout_id = None

        super().__init__("bluetooth-table", **kwargs)

    def _init_component(self, **kwargs):
        """Initialize the Bluetooth table."""
        # Create main container
        self.widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)

        # Setup UI
        self._setup_ui()
        self._setup_table()
        self._load_initial_data()

        # Apply styling
        self.add_css_class("ds-bluetooth-table")

    def _setup_ui(self):
        """Setup the main UI structure."""
        # Create header with controls
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        header_box.set_margin_bottom(12)

        # Search entry
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Search devices...")
        self.search_entry.set_hexpand(True)
        self.search_entry.connect("search-changed", self._on_search_changed)
        header_box.append(self.search_entry)

        # Device type filter dropdown
        type_filter_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        type_label = Gtk.Label(label="Type:")
        type_label.add_css_class("ds-text-caption")

        self.type_filter_dropdown = Gtk.DropDown()
        self.type_filter_dropdown.set_tooltip_text("Filter by device type")
        self.type_filter_dropdown.connect("notify::selected", self._on_type_filter_changed)

        type_filter_box.append(type_label)
        type_filter_box.append(self.type_filter_dropdown)
        header_box.append(type_filter_box)

        # Unpaired devices toggle
        unpaired_toggle = Gtk.ToggleButton()
        unpaired_toggle.set_label("Show All")
        unpaired_toggle.set_active(self.include_unpaired)
        unpaired_toggle.set_tooltip_text("Include unpaired devices")
        unpaired_toggle.connect("toggled", self._on_unpaired_toggle)
        header_box.append(unpaired_toggle)

        # Discovery button
        self.discovery_button = Gtk.Button()
        self.discovery_button.set_label("Start Discovery")
        self.discovery_button.set_icon_name("bluetooth-symbolic")
        self.discovery_button.set_tooltip_text("Start/stop device discovery")
        self.discovery_button.connect("clicked", self._on_discovery_clicked)
        header_box.append(self.discovery_button)

        self.widget.append(header_box)

        # Adapter info bar
        adapter_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        adapter_box.set_margin_bottom(6)

        self.adapter_info_label = Gtk.Label()
        self.adapter_info_label.set_halign(Gtk.Align.START)
        self.adapter_info_label.add_css_class("ds-text-caption")
        adapter_box.append(self.adapter_info_label)

        # Auto-refresh toggle
        auto_refresh_toggle = Gtk.ToggleButton()
        auto_refresh_toggle.set_label("Auto-refresh")
        auto_refresh_toggle.set_active(self.auto_refresh)
        auto_refresh_toggle.set_tooltip_text("Enable automatic refresh")
        auto_refresh_toggle.connect("toggled", self._on_auto_refresh_toggle)
        adapter_box.append(auto_refresh_toggle)

        self.widget.append(adapter_box)

        # Status bar
        status_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        status_box.set_margin_bottom(6)

        self.status_label = Gtk.Label()
        self.status_label.set_halign(Gtk.Align.START)
        self.status_label.add_css_class("ds-text-caption")
        status_box.append(self.status_label)

        self.widget.append(status_box)

    def _setup_table(self):
        """Setup the Bluetooth device table."""
        from .tables import GenericTable, TableColumn

        # Define columns
        columns = [
            TableColumn('name', 'Device Name', sortable=True, width=200),
            TableColumn('address', 'Address', sortable=True, width=150),
            TableColumn('device_type', 'Type', sortable=True, width=100),
            TableColumn('status', 'Status', sortable=True, width=100),
            TableColumn('rssi', 'Signal', sortable=True, width=80),
            TableColumn('actions', 'Actions', sortable=False, width=-1)
        ]

        # Create table
        self.bluetooth_table = GenericTable(columns, self._create_bluetooth_row)
        self.bluetooth_table.set_vexpand(True)
        self.bluetooth_table.set_hexpand(True)

        # Set callbacks
        self.bluetooth_table.set_sort_changed_callback(self._on_sort_changed)
        self.bluetooth_table.set_selection_changed_callback(self._on_device_selected)

        self.widget.append(self.bluetooth_table)

    def _create_bluetooth_row(self, device_info):
        """Create a BluetoothRow for the given device info."""
        from .primitives import BluetoothRow
        bluetooth_row = BluetoothRow(device_info)
        return bluetooth_row.get_widget()

    def _load_initial_data(self):
        """Load initial Bluetooth data."""
        self._refresh_device_list()
        self._update_adapter_info()
        self._update_type_filter()

    def _refresh_device_list(self):
        """Refresh the Bluetooth device list."""
        try:
            # Import Bluetooth monitor
            import sys
            from pathlib import Path
            sys.path.append(str(Path(__file__).parent.parent))
            from bluetooth_monitor import BluetoothMonitor

            # Show loading state
            self.discovery_button.set_sensitive(False)
            self.status_label.set_text("Scanning for devices...")

            # Get devices and adapters
            monitor = BluetoothMonitor()
            devices = monitor.get_devices(self.include_unpaired)
            adapters = monitor.get_adapters()

            # Apply filters
            filtered_devices = self._apply_filters(devices)

            # Sort devices
            sorted_devices = self._sort_devices(filtered_devices)

            # Update table
            self.bluetooth_table.set_data(sorted_devices)
            self.current_devices = sorted_devices
            self.current_adapters = adapters

            # Update status
            total_count = len(devices)
            filtered_count = len(filtered_devices)

            status_text = f"Found {filtered_count} device(s)"
            if filtered_count != total_count:
                status_text += f" (filtered from {total_count})"

            self.status_label.set_text(status_text)

        except Exception as e:
            self.status_label.set_text(f"Error scanning devices: {e}")
            import logging
            logging.getLogger(__name__).error(f"Failed to refresh device list: {e}")

        finally:
            self.discovery_button.set_sensitive(True)

    def _apply_filters(self, devices):
        """Apply search and type filters to device list."""
        filtered = devices

        # Apply search filter
        if self.filter_text:
            search_lower = self.filter_text.lower()
            filtered = [
                d for d in filtered
                if (search_lower in d.name.lower() or
                    search_lower in d.address.lower() or
                    search_lower in d.device_type.lower())
            ]

        # Apply type filter
        if self.filter_type and self.filter_type != "All":
            filtered = [d for d in filtered if d.device_type == self.filter_type.lower()]

        return filtered

    def _sort_devices(self, devices):
        """Sort devices by current sort column."""
        if not self.sort_column or not devices:
            return devices

        reverse = self.sort_column in ['rssi']  # Higher RSSI is better

        try:
            return sorted(
                devices,
                key=lambda d: getattr(d, self.sort_column, ""),
                reverse=reverse
            )
        except (AttributeError, TypeError):
            return devices

    def _update_adapter_info(self):
        """Update adapter information display."""
        if not self.current_adapters:
            self.adapter_info_label.set_text("No Bluetooth adapters found")
            return

        adapter = self.current_adapters[0]  # Use first adapter
        status_parts = []

        if adapter.powered:
            status_parts.append("Powered")
        if adapter.discoverable:
            status_parts.append("Discoverable")
        if adapter.discovering:
            status_parts.append("Discovering")

        status_text = f"Adapter: {adapter.name} ({adapter.address})"
        if status_parts:
            status_text += f" • {', '.join(status_parts)}"

        self.adapter_info_label.set_text(status_text)

    def _update_type_filter(self):
        """Update device type filter dropdown."""
        if not self.current_devices:
            return

        # Get unique device types
        types = sorted(set(d.device_type.title() for d in self.current_devices))
        types.insert(0, "All")  # Add "All" option

        # Create string list model
        model = Gtk.StringList()
        for device_type in types:
            model.append(device_type)

        self.type_filter_dropdown.set_model(model)
        self.type_filter_dropdown.set_selected(0)  # Select "All"

    def _on_search_changed(self, entry):
        """Handle search text changes."""
        self.filter_text = entry.get_text()
        self._refresh_device_list()

    def _on_type_filter_changed(self, dropdown, param):
        """Handle device type filter changes."""
        selected = dropdown.get_selected()
        model = dropdown.get_model()
        if model and selected < model.get_n_items():
            self.filter_type = model.get_string(selected)
            self._refresh_device_list()

    def _on_unpaired_toggle(self, toggle):
        """Handle unpaired devices toggle."""
        self.include_unpaired = toggle.get_active()
        self._refresh_device_list()

    def _on_discovery_clicked(self, button):
        """Handle discovery button click."""
        try:
            import sys
            from pathlib import Path
            sys.path.append(str(Path(__file__).parent.parent))
            from bluetooth_monitor import BluetoothMonitor

            monitor = BluetoothMonitor()

            if self.discovery_active:
                # Stop discovery
                success = monitor.stop_discovery()
                if success:
                    self.discovery_active = False
                    self.discovery_button.set_label("Start Discovery")
                    self.discovery_button.set_icon_name("bluetooth-symbolic")
                    self.status_label.set_text("Discovery stopped")
            else:
                # Start discovery
                success = monitor.start_discovery()
                if success:
                    self.discovery_active = True
                    self.discovery_button.set_label("Stop Discovery")
                    self.discovery_button.set_icon_name("process-stop-symbolic")
                    self.status_label.set_text("Discovering devices...")

                    # Refresh after starting discovery
                    GLib.timeout_add(2000, self._refresh_device_list)  # Refresh after 2 seconds

        except Exception as e:
            self.status_label.set_text(f"Discovery error: {e}")

    def _on_auto_refresh_toggle(self, toggle):
        """Handle auto-refresh toggle."""
        self.auto_refresh = toggle.get_active()

        if self.auto_refresh:
            self._start_auto_refresh()
        else:
            self._stop_auto_refresh()

    def _on_sort_changed(self, column_name, direction):
        """Handle sort changes."""
        self.sort_column = column_name
        self._refresh_device_list()

    def _on_device_selected(self, device_info):
        """Handle device selection."""
        if device_info:
            print(f"🔵 Selected device: {device_info.name} ({device_info.address})")

    def _start_auto_refresh(self):
        """Start automatic refresh."""
        if self.refresh_timeout_id:
            GLib.source_remove(self.refresh_timeout_id)

        self.refresh_timeout_id = GLib.timeout_add(
            int(self.refresh_interval * 1000),  # Convert to milliseconds
            self._auto_refresh_callback
        )

    def _stop_auto_refresh(self):
        """Stop automatic refresh."""
        if self.refresh_timeout_id:
            GLib.source_remove(self.refresh_timeout_id)
            self.refresh_timeout_id = None

    def _auto_refresh_callback(self):
        """Callback for automatic refresh."""
        if self.auto_refresh:
            self._refresh_device_list()
            return True  # Continue
        return False  # Stop

    def get_selected_device(self):
        """Get the currently selected device."""
        return self.bluetooth_table.get_selected_data()

    def cleanup(self):
        """Clean up resources."""
        self._stop_auto_refresh()

        # Stop discovery if active
        if self.discovery_active:
            try:
                import sys
                from pathlib import Path
                sys.path.append(str(Path(__file__).parent.parent))
                from bluetooth_monitor import BluetoothMonitor

                monitor = BluetoothMonitor()
                monitor.stop_discovery()
            except Exception:
                pass

        super().cleanup()


class AudioTable(AdwComponentBase):
    """
    Audio device management table with volume control and connection switching.

    Features:
    - Audio device enumeration and display
    - Volume control and mute management
    - Default device selection and switching
    - Bluetooth audio connection pulling
    - Device filtering and search capabilities
    """

    def __init__(self, **kwargs):
        # Import required modules
        import sys
        from pathlib import Path
        sys.path.append(str(Path(__file__).parent))


        # Configuration
        self.current_devices = []
        self.sort_column = 'name'
        self.filter_text = ""
        self.filter_type = None

        # UI Components
        self.search_entry = None
        self.type_filter_dropdown = None
        self.audio_table = None
        self.status_label = None
        self.device_count_label = None
        self.refresh_button = None
        self.volume_master_scale = None
        self.bluetooth_connect_button = None

        # Auto-refresh
        self.auto_refresh = True
        self.refresh_interval = 2.0  # seconds
        self.refresh_timeout_id = None

        super().__init__("audio-table", **kwargs)

    def _init_component(self, **kwargs):
        """Initialize the audio table component."""
        # Create main container
        self.widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.widget.set_vexpand(True)
        self.widget.set_hexpand(True)

        # Setup UI
        self._setup_ui()
        self._setup_table()
        self._load_initial_data()

        # Apply styling
        self.add_css_class("ds-audio-table")

    def _setup_ui(self):
        """Setup the main UI structure."""
        # Create header with controls
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        header_box.set_margin_bottom(12)

        # Search entry
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Search audio devices...")
        self.search_entry.set_hexpand(True)
        self.search_entry.connect("search-changed", self._on_search_changed)
        header_box.append(self.search_entry)

        # Connection type filter dropdown
        type_filter_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        type_label = Gtk.Label(label="Type:")
        type_label.add_css_class("ds-text-caption")

        self.type_filter_dropdown = Gtk.DropDown()
        self.type_filter_dropdown.set_tooltip_text("Filter by connection type")
        self.type_filter_dropdown.connect("notify::selected", self._on_type_filter_changed)

        type_filter_box.append(type_label)
        type_filter_box.append(self.type_filter_dropdown)
        header_box.append(type_filter_box)

        # Master volume control
        volume_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        volume_label = Gtk.Label(label="Master:")
        volume_label.add_css_class("ds-text-caption")
        volume_box.append(volume_label)

        self.volume_master_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 5)
        self.volume_master_scale.set_value(50)  # Default volume
        self.volume_master_scale.set_size_request(120, -1)
        self.volume_master_scale.set_tooltip_text("Master volume control")
        self.volume_master_scale.connect("value-changed", self._on_master_volume_changed)
        volume_box.append(self.volume_master_scale)

        master_volume_label = Gtk.Label(label="50%")
        master_volume_label.set_size_request(35, -1)
        master_volume_label.add_css_class("ds-text-caption")
        volume_box.append(master_volume_label)
        self.master_volume_label = master_volume_label

        header_box.append(volume_box)

        # Bluetooth connection button
        self.bluetooth_connect_button = Gtk.Button()
        self.bluetooth_connect_button.set_label("Pull from Phone")
        self.bluetooth_connect_button.set_icon_name("bluetooth-symbolic")
        self.bluetooth_connect_button.set_tooltip_text("Connect Bluetooth audio device from phone")
        self.bluetooth_connect_button.add_css_class("suggested-action")
        self.bluetooth_connect_button.connect("clicked", self._on_bluetooth_connect_clicked)
        header_box.append(self.bluetooth_connect_button)

        # Refresh button
        self.refresh_button = Gtk.Button()
        self.refresh_button.set_icon_name("view-refresh-symbolic")
        self.refresh_button.set_tooltip_text("Refresh audio devices")
        self.refresh_button.connect("clicked", self._on_refresh_clicked)
        header_box.append(self.refresh_button)

        self.widget.append(header_box)

        # Status bar
        status_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        status_box.set_margin_bottom(6)

        self.device_count_label = Gtk.Label()
        self.device_count_label.add_css_class("ds-text-caption")
        status_box.append(self.device_count_label)

        self.status_label = Gtk.Label(label="Ready")
        self.status_label.set_halign(Gtk.Align.START)
        self.status_label.add_css_class("ds-text-caption")
        status_box.append(self.status_label)

        # Auto-refresh toggle
        auto_refresh_toggle = Gtk.ToggleButton()
        auto_refresh_toggle.set_label("Auto-refresh")
        auto_refresh_toggle.set_active(self.auto_refresh)
        auto_refresh_toggle.set_tooltip_text("Enable automatic refresh")
        auto_refresh_toggle.connect("toggled", self._on_auto_refresh_toggle)
        status_box.append(auto_refresh_toggle)

        self.widget.append(status_box)

    def _setup_table(self):
        """Setup the audio device table."""
        from .tables import GenericTable, TableColumn

        # Define columns
        columns = [
            TableColumn('name', 'Device Name', sortable=True, width=200),
            TableColumn('connection', 'Connection', sortable=True, width=100),
            TableColumn('volume', 'Volume', sortable=True, width=80),
            TableColumn('status', 'Status', sortable=True, width=100),
            TableColumn('actions', 'Actions', sortable=False, width=-1)
        ]

        # Create table
        self.audio_table = GenericTable(columns, self._create_audio_row)
        self.audio_table.set_vexpand(True)
        self.audio_table.set_hexpand(True)

        # Set callbacks
        self.audio_table.set_sort_changed_callback(self._on_sort_changed)
        self.audio_table.set_selection_changed_callback(self._on_device_selected)

        # Create scrolled window for the table
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_vexpand(True)
        scrolled_window.set_hexpand(True)
        scrolled_window.set_min_content_height(300)  # Minimum height
        scrolled_window.set_child(self.audio_table)

        self.widget.append(scrolled_window)

    def _create_audio_row(self, device_info):
        """Create an AudioDeviceRow for the given device info."""
        from .primitives import AudioDeviceRow
        audio_row = AudioDeviceRow(device_info)
        return audio_row.get_widget()

    def _load_initial_data(self):
        """Load initial audio data."""
        self._refresh_device_list()
        self._update_type_filter()

        # Start auto-refresh if enabled
        if self.auto_refresh:
            self._start_auto_refresh()

    def _refresh_device_list(self):
        """Refresh the audio device list."""
        try:
            # Import audio monitor from handlers
            try:
                from ..handlers.audio_monitor import AudioLevelMonitor as AudioMonitor
            except ImportError:
                # Fallback for direct execution
                import sys
                from pathlib import Path
                sys.path.append(str(Path(__file__).parent.parent / "handlers"))
                from audio_monitor import AudioLevelMonitor as AudioMonitor

            # Show loading state
            self.refresh_button.set_sensitive(False)
            self.status_label.set_text("Loading audio devices...")

            # Get audio devices
            monitor = AudioMonitor()
            devices = monitor.get_playback_devices()

            # Apply filters
            filtered_devices = self._apply_filters(devices)

            # Sort devices
            sorted_devices = self._sort_devices(filtered_devices)

            # Update table
            self.audio_table.set_data(sorted_devices)
            self.current_devices = sorted_devices

            # Update status and controls
            self._update_status()
            self._update_master_volume()

        except Exception as e:
            self.status_label.set_text(f"Error loading devices: {e}")
            import logging
            logging.getLogger(__name__).error(f"Failed to refresh audio devices: {e}")

        finally:
            self.refresh_button.set_sensitive(True)

    def _apply_filters(self, devices):
        """Apply search and type filters to device list."""
        filtered = devices

        # Apply text filter
        if self.filter_text:
            search_lower = self.filter_text.lower()
            filtered = [
                d for d in filtered
                if (search_lower in d.name.lower() or
                    search_lower in d.description.lower())
            ]

        # Apply type filter
        if self.filter_type and self.filter_type != "All":
            filtered = [d for d in filtered if d.connection_type == self.filter_type.lower()]

        return filtered

    def _sort_devices(self, devices):
        """Sort devices by the selected column."""
        if not devices:
            return devices

        sort_key_map = {
            'name': lambda d: d.name.lower(),
            'connection': lambda d: d.connection_type,
            'volume': lambda d: d.volume or 0,
            'status': lambda d: (d.is_default, d.is_active, not d.is_muted)
        }

        sort_key = sort_key_map.get(self.sort_column, lambda d: d.name.lower())

        try:
            return sorted(devices, key=sort_key, reverse=False)
        except Exception as e:
            print(f"❌ Sort failed: {e}")
            return devices

    def _update_status(self):
        """Update status labels and controls."""
        device_count = len(self.current_devices)

        # Update device count
        self.device_count_label.set_text(f"{device_count} device(s)")

        # Update status
        if device_count == 0:
            self.status_label.set_text("No audio devices found")
        else:
            default_devices = [d for d in self.current_devices if d.is_default]
            if default_devices:
                self.status_label.set_text(f"Default: {default_devices[0].name}")
            else:
                self.status_label.set_text("No default device set")

    def _update_master_volume(self):
        """Update master volume control from current devices."""
        if self.current_devices and self.current_devices[0].volume is not None:
            volume = self.current_devices[0].volume
            self.volume_master_scale.set_value(volume)
            self.master_volume_label.set_text(f"{volume}%")

    def _update_type_filter(self):
        """Update connection type filter dropdown."""
        if not self.current_devices:
            return

        # Get unique connection types
        types = sorted(set(d.connection_type.title() for d in self.current_devices))
        types.insert(0, "All")  # Add "All" option

        # Create string list model
        model = Gtk.StringList()
        for conn_type in types:
            model.append(conn_type)

        self.type_filter_dropdown.set_model(model)
        self.type_filter_dropdown.set_selected(0)  # Select "All"

    def _on_search_changed(self, entry):
        """Handle search text changes."""
        self.filter_text = entry.get_text()
        self._refresh_device_list()

    def _on_type_filter_changed(self, dropdown, param):
        """Handle connection type filter changes."""
        selected = dropdown.get_selected()
        model = dropdown.get_model()
        if model and selected < model.get_n_items():
            self.filter_type = model.get_string(selected)
            self._refresh_device_list()

    def _on_master_volume_changed(self, scale):
        """Handle master volume scale changes."""
        new_volume = int(scale.get_value())

        # Update master volume label
        self.master_volume_label.set_text(f"{new_volume}%")

        # Update tooltip
        scale.set_tooltip_text(f"Master volume: {new_volume}%")

        print(f"🔊 Master volume changed: {new_volume}%")
        # TODO: Implement actual master volume control via AudioMonitor

    def _on_bluetooth_connect_clicked(self, button):
        """Handle Bluetooth connect button click."""
        print("🔊 Attempting to pull Bluetooth audio from phone...")

        # Disable button temporarily
        button.set_sensitive(False)
        button.set_label("Connecting...")

        try:
            # TODO: Implement Bluetooth audio connection pulling
            # This would:
            # 1. Scan for Bluetooth devices
            # 2. Find audio devices (like PRO X 2)
            # 3. Connect them to this computer
            # 4. Set as default audio device

            # For now, show a placeholder message
            self.status_label.set_text("Bluetooth connection not yet implemented")

            # Simulate connection attempt
            import time
            time.sleep(1)

        except Exception as e:
            self.status_label.set_text(f"Bluetooth connection failed: {e}")
        finally:
            button.set_sensitive(True)
            button.set_label("Pull from Phone")

    def _on_refresh_clicked(self, button):
        """Handle refresh button click."""
        self._refresh_device_list()

    def _on_auto_refresh_toggle(self, toggle):
        """Handle auto-refresh toggle."""
        self.auto_refresh = toggle.get_active()

        if self.auto_refresh:
            self._start_auto_refresh()
        else:
            self._stop_auto_refresh()

    def _on_sort_changed(self, column_name, direction):
        """Handle sort changes."""
        self.sort_column = column_name
        self._refresh_device_list()

    def _on_device_selected(self, device_info):
        """Handle device selection."""
        if device_info:
            print(f"🔊 Selected audio device: {device_info.name}")

    def _start_auto_refresh(self):
        """Start automatic refresh."""
        if self.refresh_timeout_id:
            GLib.source_remove(self.refresh_timeout_id)

        self.refresh_timeout_id = GLib.timeout_add(
            int(self.refresh_interval * 1000),  # Convert to milliseconds
            self._auto_refresh_callback
        )

    def _stop_auto_refresh(self):
        """Stop automatic refresh."""
        if self.refresh_timeout_id:
            GLib.source_remove(self.refresh_timeout_id)
            self.refresh_timeout_id = None

    def _auto_refresh_callback(self):
        """Callback for automatic refresh."""
        if self.auto_refresh:
            self._refresh_device_list()
            return True  # Continue
        return False  # Stop

    def get_device_count(self) -> int:
        """Get current device count."""
        return len(self.current_devices)

    def get_default_device(self):
        """Get the current default audio device."""
        for device in self.current_devices:
            if device.is_default:
                return device
        return None

    def cleanup(self):
        """Clean up resources."""
        self._stop_auto_refresh()
        self.current_devices.clear()
        super().cleanup()
