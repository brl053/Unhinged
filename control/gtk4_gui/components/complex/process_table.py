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

from ..base import AdwComponentBase
from ..containers import LogContainer, ServicePanel, StatusCard
from ..primitives import ActionButton




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
        from ..tables import GenericTable, TableColumn

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
        from ..primitives import ProcessRow
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
