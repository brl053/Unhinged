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


from gi.repository import GObject, Gtk

from ..base import AdwComponentBase
from ..containers import LogContainer
from ..primitives import ActionButton


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
        "filter-changed": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        "export-requested": (GObject.SignalFlags.RUN_FIRST, None, ()),
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

        # Create log container with error handling
        try:
            self._log_container = LogContainer()
            if hasattr(self._log_container, "get_widget"):
                self.widget.append(self._log_container.get_widget())
            elif hasattr(self._log_container, "widget"):
                self.widget.append(self._log_container.widget)
            else:
                print("⚠️ LogContainer missing widget accessor")
        except Exception as e:
            print(f"❌ Failed to create LogContainer: {e}")
            # Create fallback text view
            fallback_view = Gtk.TextView()
            fallback_view.set_editable(False)
            scrolled = Gtk.ScrolledWindow()
            scrolled.set_child(fallback_view)
            self.widget.append(scrolled)
            self._log_container = None

        # Apply styling
        self.add_css_class("ds-log-viewer")

    def _create_toolbar(self) -> Gtk.Widget:
        """Create the log viewer toolbar."""
        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        toolbar.add_css_class("toolbar")

        # Search entry
        self._search_entry = Gtk.SearchEntry()
        self._search_entry.set_placeholder_text("Search logs...")
        self._search_entry.connect("search-changed", self._on_search_changed)
        toolbar.append(self._search_entry)

        # Filter dropdown
        filter_model = Gtk.StringList()
        for level in self._log_levels:
            filter_model.append(level)

        self._filter_dropdown = Gtk.DropDown(model=filter_model)
        self._filter_dropdown.set_selected(0)  # ALL
        self._filter_dropdown.connect("notify::selected", self._on_filter_changed)
        toolbar.append(self._filter_dropdown)

        # Auto-scroll toggle
        self._auto_scroll_toggle = Gtk.ToggleButton()
        self._auto_scroll_toggle.set_icon_name("view-continuous-symbolic")
        self._auto_scroll_toggle.set_tooltip_text("Auto-scroll to bottom")
        self._auto_scroll_toggle.set_active(True)
        self._auto_scroll_toggle.connect("toggled", self._on_auto_scroll_toggled)
        toolbar.append(self._auto_scroll_toggle)

        # Export button
        self._export_button = ActionButton(label="Export", style="flat", icon_name="document-save-symbolic")
        self._export_button.connect("clicked", self._on_export_clicked)
        toolbar.append(self._export_button.get_widget())

        return toolbar

    def _on_search_changed(self, entry):
        """Handle search text changes."""
        search_text = entry.get_text()
        self._current_filter = search_text
        self.emit("filter-changed", search_text)

    def _on_filter_changed(self, dropdown, param):
        """Handle log level filter changes."""
        selected = dropdown.get_selected()
        self._log_levels[selected]
        # Implement log level filtering logic here
        pass

    def _on_auto_scroll_toggled(self, toggle):
        """Handle auto-scroll toggle."""
        auto_scroll = toggle.get_active()
        self._log_container.auto_scroll = auto_scroll

    def _on_export_clicked(self, button):
        """Handle export button click."""
        self.emit("export-requested")

    def append_log(self, message: str, level: str = "INFO", timestamp: str | None = None):
        """Add a log message."""
        # Format log message
        formatted_message = f"[{timestamp}] {level}: {message}" if timestamp else f"{level}: {message}"

        # Add to log container - with error handling
        try:
            if self._log_container and hasattr(self._log_container, "append_text"):
                self._log_container.append_text(formatted_message)
            else:
                print(f"⚠️ LogContainer not properly initialized: {self._log_container}")
                print(f"   Log message: {formatted_message}")
        except Exception as e:
            print(f"❌ Error appending to log container: {e}")
            print(f"   Log message: {formatted_message}")

    def clear_logs(self):
        """Clear all log messages."""
        self._log_container.clear()

    def get_log_text(self) -> str:
        """Get all log text."""
        return self._log_container.get_text()
