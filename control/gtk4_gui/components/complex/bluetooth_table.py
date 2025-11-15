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
        from ..tables import GenericTable, TableColumn

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
        from ..primitives import BluetoothRow
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
