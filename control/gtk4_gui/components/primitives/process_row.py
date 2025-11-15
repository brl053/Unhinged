"""
@llm-doc Primitive GTK4 Components
@llm-version 1.0.0
@llm-date 2025-10-28

Basic building block components with design system integration:
- ActionButton: Enhanced button with semantic styling
- StatusLabel: Label with status styling (success, warning, error)
- ProgressIndicator: Progress bar with semantic styling
- HardwareInfoRow: Hardware information display row
- ProcessRow: Process information display with controls
- BluetoothRow: Bluetooth device display with connection controls
- AudioDeviceRow: Audio device display with volume controls
"""

import logging

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("Gdk", "4.0")


from gi.repository import Adw, Gio, GLib, Gtk

from .hardware_info_row import HardwareInfoRow

logger = logging.getLogger(__name__)


class ProcessRow(HardwareInfoRow):
    """
    Individual process display extending hardware row pattern.

    Features:
    - Process data display (PID, name, CPU%, memory%, user)
    - Action menu integration (kill, priority, details)
    - Status indicators and real-time updates
    - Update highlighting for changed processes
    """

    def __init__(self, process_data, **kwargs):
        # Extract process information
        self.process_data = process_data
        self.pid = getattr(process_data, "pid", 0)
        self.name = getattr(process_data, "name", "Unknown")
        self.cpu_percent = getattr(process_data, "cpu_percent", 0.0)
        self.memory_percent = getattr(process_data, "memory_percent", 0.0)
        self.user = getattr(process_data, "user", "unknown")
        self.status = getattr(process_data, "status", "unknown")
        self.command = getattr(process_data, "command", "")

        # Create title and subtitle
        title = f"{self.name} (PID: {self.pid})"
        subtitle = (
            f"User: {self.user} | CPU: {self.cpu_percent:.1f}% | Memory: {self.memory_percent:.1f}%"
        )

        # Initialize with process-specific settings
        super().__init__(
            title=title,
            subtitle=subtitle,
            hardware_type="process",
            status=self._map_process_status(),
            **kwargs,
        )

        # Setup process-specific features
        self._setup_process_indicators()
        self._setup_process_actions()

        # Apply process-specific styling
        self.add_css_class("ds-process-row")

        # Store for update highlighting
        self._last_cpu = self.cpu_percent
        self._last_memory = self.memory_percent
        self._update_highlight_timeout = None

    def _map_process_status(self) -> str:
        """Map process status to component status."""
        status_map = {
            "running": "normal",
            "sleeping": "normal",
            "disk-sleep": "normal",
            "stopped": "warning",
            "tracing-stop": "warning",
            "zombie": "error",
            "dead": "error",
            "wake-kill": "error",
            "waking": "info",
        }
        return status_map.get(self.status.lower(), "info")

    def _setup_process_indicators(self):
        """Setup CPU and memory usage indicators."""
        # CPU indicator
        cpu_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        cpu_label = Gtk.Label(label="CPU:")
        cpu_label.add_css_class("ds-text-caption")
        cpu_value = Gtk.Label(label=f"{self.cpu_percent:.1f}%")
        cpu_value.add_css_class("ds-text-caption")

        # Color code CPU usage
        if self.cpu_percent > 80:
            cpu_value.add_css_class("error")
        elif self.cpu_percent > 50:
            cpu_value.add_css_class("warning")
        else:
            cpu_value.add_css_class("success")

        cpu_box.append(cpu_label)
        cpu_box.append(cpu_value)

        # Memory indicator
        mem_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        mem_label = Gtk.Label(label="Mem:")
        mem_label.add_css_class("ds-text-caption")
        mem_value = Gtk.Label(label=f"{self.memory_percent:.1f}%")
        mem_value.add_css_class("ds-text-caption")

        # Color code memory usage
        if self.memory_percent > 80:
            mem_value.add_css_class("error")
        elif self.memory_percent > 50:
            mem_value.add_css_class("warning")
        else:
            mem_value.add_css_class("success")

        mem_box.append(mem_label)
        mem_box.append(mem_value)

        # Add indicators to row
        indicators_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        indicators_box.append(cpu_box)
        indicators_box.append(mem_box)

        self.widget.add_suffix(indicators_box)

        # Store references for updates
        self._cpu_value_label = cpu_value
        self._mem_value_label = mem_value

    def _setup_process_actions(self):
        """Setup process management action menu."""
        # Create action menu button
        menu_button = Gtk.MenuButton()
        menu_button.set_icon_name("view-more-symbolic")
        menu_button.add_css_class("flat")
        menu_button.set_tooltip_text("Process actions")

        # Create menu model
        menu = Gio.Menu()

        # Add menu items
        menu.append("Show Details", f"process.details::{self.pid}")
        menu.append("Change Priority", f"process.priority::{self.pid}")

        # Add separator and dangerous actions
        menu.append_section(None, self._create_danger_section())

        menu_button.set_menu_model(menu)
        self.widget.add_suffix(menu_button)

        # Setup action group
        self._setup_action_group()

    def _create_danger_section(self) -> Gio.Menu:
        """Create dangerous actions section."""
        danger_section = Gio.Menu()
        danger_section.append("Terminate Process", f"process.kill::{self.pid}")
        danger_section.append("Force Kill", f"process.force_kill::{self.pid}")
        return danger_section

    def _setup_action_group(self):
        """Setup action group for process actions."""
        action_group = Gio.SimpleActionGroup()

        # Details action
        details_action = Gio.SimpleAction.new("details", GLib.VariantType.new("s"))
        details_action.connect("activate", self._on_show_details)
        action_group.add_action(details_action)

        # Priority action
        priority_action = Gio.SimpleAction.new("priority", GLib.VariantType.new("s"))
        priority_action.connect("activate", self._on_change_priority)
        action_group.add_action(priority_action)

        # Kill action
        kill_action = Gio.SimpleAction.new("kill", GLib.VariantType.new("s"))
        kill_action.connect("activate", self._on_kill_process)
        action_group.add_action(kill_action)

        # Force kill action
        force_kill_action = Gio.SimpleAction.new("force_kill", GLib.VariantType.new("s"))
        force_kill_action.connect("activate", self._on_force_kill_process)
        action_group.add_action(force_kill_action)

        # Insert action group
        self.widget.insert_action_group("process", action_group)

    def _on_show_details(self, action, parameter):
        """Show process details dialog."""
        int(parameter.get_string())

        dialog = Adw.MessageDialog()
        dialog.set_heading(f"Process Details - {self.name}")

        details_text = f"""PID: {self.pid}
Name: {self.name}
User: {self.user}
Status: {self.status}
CPU Usage: {self.cpu_percent:.1f}%
Memory Usage: {self.memory_percent:.1f}%
Command: {self.command[:100]}{"..." if len(self.command) > 100 else ""}"""

        dialog.set_body(details_text)
        dialog.add_response("close", "Close")
        dialog.set_default_response("close")

        # Get parent window
        parent = self.widget.get_root()
        if parent:
            dialog.set_transient_for(parent)

        dialog.present()

    def _on_change_priority(self, action, parameter):
        """Show priority change dialog."""
        # TODO: Implement priority change dialog
        print(f"Change priority for PID {self.pid}")

    def _on_kill_process(self, action, parameter):
        """Show kill process confirmation."""
        int(parameter.get_string())

        dialog = Adw.MessageDialog()
        dialog.set_heading("Terminate Process")
        dialog.set_body(f"Are you sure you want to terminate '{self.name}' (PID: {self.pid})?")

        dialog.add_response("cancel", "Cancel")
        dialog.add_response("terminate", "Terminate")
        dialog.set_response_appearance("terminate", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.set_default_response("cancel")

        dialog.connect("response", self._on_kill_confirmed)

        # Get parent window
        parent = self.widget.get_root()
        if parent:
            dialog.set_transient_for(parent)

        dialog.present()

    def _on_force_kill_process(self, action, parameter):
        """Show force kill confirmation."""
        int(parameter.get_string())

        dialog = Adw.MessageDialog()
        dialog.set_heading("Force Kill Process")
        dialog.set_body(
            f"Are you sure you want to force kill '{self.name}' (PID: {self.pid})?\n\nThis may cause data loss!"
        )

        dialog.add_response("cancel", "Cancel")
        dialog.add_response("force_kill", "Force Kill")
        dialog.set_response_appearance("force_kill", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.set_default_response("cancel")

        dialog.connect("response", self._on_force_kill_confirmed)

        # Get parent window
        parent = self.widget.get_root()
        if parent:
            dialog.set_transient_for(parent)

        dialog.present()

    def _on_kill_confirmed(self, dialog, response):
        """Handle kill confirmation response."""
        if response == "terminate":
            # TODO: Implement actual process termination
            print(f"Terminating process {self.pid}")
        dialog.close()

    def _on_force_kill_confirmed(self, dialog, response):
        """Handle force kill confirmation response."""
        if response == "force_kill":
            # TODO: Implement actual force kill
            print(f"Force killing process {self.pid}")
        dialog.close()

    def update_process_data(self, new_data):
        """Update process data and highlight changes."""
        old_cpu = self.cpu_percent
        old_memory = self.memory_percent

        # Update data
        self.process_data = new_data
        self.cpu_percent = getattr(new_data, "cpu_percent", 0.0)
        self.memory_percent = getattr(new_data, "memory_percent", 0.0)
        self.status = getattr(new_data, "status", "unknown")

        # Update UI
        self._update_indicators()

        # Highlight if changed significantly
        if abs(self.cpu_percent - old_cpu) > 1.0 or abs(self.memory_percent - old_memory) > 1.0:
            self._highlight_update()

    def _update_indicators(self):
        """Update CPU and memory indicators."""
        # Update CPU
        self._cpu_value_label.set_text(f"{self.cpu_percent:.1f}%")
        self._cpu_value_label.remove_css_class("success")
        self._cpu_value_label.remove_css_class("warning")
        self._cpu_value_label.remove_css_class("error")

        if self.cpu_percent > 80:
            self._cpu_value_label.add_css_class("error")
        elif self.cpu_percent > 50:
            self._cpu_value_label.add_css_class("warning")
        else:
            self._cpu_value_label.add_css_class("success")

        # Update Memory
        self._mem_value_label.set_text(f"{self.memory_percent:.1f}%")
        self._mem_value_label.remove_css_class("success")
        self._mem_value_label.remove_css_class("warning")
        self._mem_value_label.remove_css_class("error")

        if self.memory_percent > 80:
            self._mem_value_label.add_css_class("error")
        elif self.memory_percent > 50:
            self._mem_value_label.add_css_class("warning")
        else:
            self._mem_value_label.add_css_class("success")

    def _highlight_update(self):
        """Briefly highlight the row to show it was updated."""
        # Remove existing highlight
        self.widget.remove_css_class("ds-process-row-updated")

        # Add highlight
        self.widget.add_css_class("ds-process-row-updated")

        # Remove highlight after delay
        if self._update_highlight_timeout:
            GLib.source_remove(self._update_highlight_timeout)

        self._update_highlight_timeout = GLib.timeout_add(
            500,  # 500ms
            self._remove_highlight,
        )

    def _remove_highlight(self):
        """Remove update highlight."""
        self.widget.remove_css_class("ds-process-row-updated")
        self._update_highlight_timeout = None
        return False  # Don't repeat

    def cleanup(self):
        """Clean up resources."""
        if self._update_highlight_timeout:
            GLib.source_remove(self._update_highlight_timeout)
        super().cleanup()
