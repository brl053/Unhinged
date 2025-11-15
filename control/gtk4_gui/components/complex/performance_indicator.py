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


from gi.repository import Adw, GLib, Gtk

from ..base import AdwComponentBase


class PerformanceIndicator(AdwComponentBase):
    """
    Real-time performance metrics display component.

    Features:
    - CPU, memory, and disk usage indicators
    - Progress bars with semantic color coding
    - Real-time updates with smooth animations
    - Configurable thresholds for warning/error states
    """

    def __init__(
        self,
        metric_type: str = "cpu",
        title: str = "",
        current_value: float = 0.0,
        max_value: float = 100.0,
        unit: str = "%",
        warning_threshold: float = 75.0,
        error_threshold: float = 90.0,
        **kwargs,
    ):
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
        self.widget.update_property(
            [Gtk.AccessibleProperty.LABEL], [f"Performance Metric: {self.title}"]
        )

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
            "generic": "Performance",
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
            "generic": "utilities-system-monitor-symbolic",
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
            self._auto_update_callback,
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
            if hasattr(self, "_update_callback") and self._update_callback:
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
