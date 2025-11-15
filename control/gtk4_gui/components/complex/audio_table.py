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

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")


from gi.repository import GLib, Gtk

from ..base import AdwComponentBase


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
        self.sort_column = "name"
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
        self.type_filter_dropdown.connect(
            "notify::selected", self._on_type_filter_changed
        )

        type_filter_box.append(type_label)
        type_filter_box.append(self.type_filter_dropdown)
        header_box.append(type_filter_box)

        # Master volume control
        volume_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        volume_label = Gtk.Label(label="Master:")
        volume_label.add_css_class("ds-text-caption")
        volume_box.append(volume_label)

        self.volume_master_scale = Gtk.Scale.new_with_range(
            Gtk.Orientation.HORIZONTAL, 0, 100, 5
        )
        self.volume_master_scale.set_value(50)  # Default volume
        self.volume_master_scale.set_size_request(120, -1)
        self.volume_master_scale.set_tooltip_text("Master volume control")
        self.volume_master_scale.connect(
            "value-changed", self._on_master_volume_changed
        )
        volume_box.append(self.volume_master_scale)

        master_volume_label = Gtk.Label(label="50%")
        master_volume_label.set_size_request(35, -1)
        master_volume_label.add_css_class("ds-text-caption")
        volume_box.append(master_volume_label)
        self.master_volume_label = master_volume_label

        header_box.append(volume_box)

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
        from ..tables import GenericTable, TableColumn

        # Define columns
        columns = [
            TableColumn("name", "Device Name", sortable=True, width=200),
            TableColumn("connection", "Connection", sortable=True, width=100),
            TableColumn("volume", "Volume", sortable=True, width=80),
            TableColumn("status", "Status", sortable=True, width=100),
            TableColumn("actions", "Actions", sortable=False, width=-1),
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
        from ..primitives import AudioDeviceRow

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
                d
                for d in filtered
                if (
                    search_lower in d.name.lower()
                    or search_lower in d.description.lower()
                )
            ]

        # Apply type filter
        if self.filter_type and self.filter_type != "All":
            filtered = [
                d for d in filtered if d.connection_type == self.filter_type.lower()
            ]

        return filtered

    def _sort_devices(self, devices):
        """Sort devices by the selected column."""
        if not devices:
            return devices

        sort_key_map = {
            "name": lambda d: d.name.lower(),
            "connection": lambda d: d.connection_type,
            "volume": lambda d: d.volume or 0,
            "status": lambda d: (d.is_default, d.is_active, not d.is_muted),
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
            self._auto_refresh_callback,
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
