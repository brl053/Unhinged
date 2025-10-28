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

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, Gio, GLib, GObject, Pango
from typing import Optional, Callable, Dict, Any
from .base import ComponentBase, AdwComponentBase


class ActionButton(AdwComponentBase):
    """
    Enhanced button component with design system integration.
    
    Features:
    - Semantic styling (primary, secondary, destructive)
    - Loading states with spinner
    - Icon support
    - Keyboard accessibility
    """
    
    __gsignals__ = {
        'clicked': (GObject.SignalFlags.RUN_FIRST, None, ()),
    }
    
    def __init__(self, 
                 label: str = "",
                 style: str = "primary",
                 icon_name: Optional[str] = None,
                 **kwargs):
        self.label = label
        self.style = style
        self.icon_name = icon_name
        self._loading = False
        self._spinner = None
        self._original_child = None
        
        super().__init__("action-button", **kwargs)
    
    def _init_component(self, **kwargs):
        """Initialize the button widget."""
        self.widget = Gtk.Button()
        
        # Set up button content
        self._setup_button_content()
        
        # Apply styling
        self._apply_button_style()
        
        # Connect signals
        self.widget.connect('clicked', self._on_clicked)
        
        # Set accessibility
        if self.label:
            self.widget.set_tooltip_text(self.label)

        # Add ARIA attributes
        self.widget.set_accessible_role(Gtk.AccessibleRole.BUTTON)
        if self.label:
            self.widget.update_property([Gtk.AccessibleProperty.LABEL], [self.label])
    
    def _setup_button_content(self):
        """Setup button content with optional icon."""
        if self.icon_name:
            # Button with icon and label
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            
            icon = Gtk.Image.new_from_icon_name(self.icon_name)
            box.append(icon)
            
            if self.label:
                label = Gtk.Label(label=self.label)
                box.append(label)
            
            self.widget.set_child(box)
            self._original_child = box
        else:
            # Text-only button
            self.widget.set_label(self.label)
            self._original_child = None
    
    def _apply_button_style(self):
        """Apply semantic styling based on button style."""
        style_classes = {
            "primary": "suggested-action",
            "secondary": "",
            "destructive": "destructive-action",
            "flat": "flat",
        }
        
        css_class = style_classes.get(self.style, "")
        if css_class:
            self.widget.add_css_class(css_class)
        
        # Add design system class
        self.add_css_class(f"ds-action-{self.style}")
    
    def _on_clicked(self, button):
        """Handle button click."""
        if not self._loading:
            self.emit('clicked')
            self.trigger_action('clicked')
    
    def set_loading(self, loading: bool):
        """Set loading state with spinner."""
        if self._loading == loading:
            return
            
        self._loading = loading
        
        if loading:
            # Show spinner
            self._spinner = Gtk.Spinner()
            self._spinner.set_spinning(True)
            self.widget.set_child(self._spinner)
            self.widget.set_sensitive(False)
        else:
            # Restore original content
            if self._original_child:
                self.widget.set_child(self._original_child)
            else:
                self.widget.set_label(self.label)
            self.widget.set_sensitive(True)
            self._spinner = None
    
    def set_label(self, label: str):
        """Update button label."""
        self.label = label
        if not self._loading:
            if self._original_child is None:
                self.widget.set_label(label)
            else:
                self._setup_button_content()


class StatusLabel(ComponentBase):
    """
    Label component with semantic status styling.
    
    Supports status types: success, warning, error, info, neutral
    """
    
    def __init__(self, 
                 text: str = "",
                 status: str = "neutral",
                 **kwargs):
        self.text = text
        self.status = status
        
        super().__init__("status-label", **kwargs)
    
    def _init_component(self, **kwargs):
        """Initialize the label widget."""
        self.widget = Gtk.Label(label=self.text)
        self.widget.set_wrap(True)
        self.widget.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
        
        # Apply status styling
        self._apply_status_style()
    
    def _apply_status_style(self):
        """Apply styling based on status type."""
        # Remove existing status classes
        for status_type in ["success", "warning", "error", "info", "neutral"]:
            self.widget.remove_css_class(f"status-{status_type}")
        
        # Add current status class
        self.widget.add_css_class(f"status-{self.status}")
        self.add_css_class(f"ds-status-{self.status}")
    
    def set_text(self, text: str):
        """Update label text."""
        self.text = text
        self.widget.set_label(text)
    
    def set_status(self, status: str):
        """Update status type."""
        self.status = status
        self._apply_status_style()


class ProgressIndicator(ComponentBase):
    """
    Progress indicator with semantic styling and optional text.
    
    Supports determinate and indeterminate progress.
    """
    
    def __init__(self, 
                 progress: float = 0.0,
                 text: Optional[str] = None,
                 show_percentage: bool = False,
                 **kwargs):
        self.progress = progress
        self.text = text
        self.show_percentage = show_percentage
        self._progress_bar = None
        self._label = None
        
        super().__init__("progress-indicator", **kwargs)
    
    def _init_component(self, **kwargs):
        """Initialize the progress indicator."""
        # Create container
        self.widget = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        
        # Create progress bar
        self._progress_bar = Gtk.ProgressBar()
        self._progress_bar.set_fraction(self.progress)
        self.widget.append(self._progress_bar)
        
        # Create optional label
        if self.text or self.show_percentage:
            self._label = Gtk.Label()
            self._label.add_css_class("caption")
            self.widget.append(self._label)
            self._update_label()
        
        # Apply styling
        self.add_css_class("ds-progress-indicator")
    
    def _update_label(self):
        """Update the progress label."""
        if not self._label:
            return
            
        label_text = ""
        if self.text:
            label_text = self.text
        
        if self.show_percentage:
            percentage = int(self.progress * 100)
            if label_text:
                label_text += f" ({percentage}%)"
            else:
                label_text = f"{percentage}%"
        
        self._label.set_label(label_text)
    
    def set_progress(self, progress: float):
        """Set progress value (0.0 to 1.0)."""
        self.progress = max(0.0, min(1.0, progress))
        self._progress_bar.set_fraction(self.progress)
        self._update_label()
    
    def set_text(self, text: Optional[str]):
        """Set progress text."""
        self.text = text
        self._update_label()
    
    def pulse(self):
        """Pulse the progress bar for indeterminate progress."""
        self._progress_bar.pulse()
    
    def set_indeterminate(self, indeterminate: bool):
        """Set indeterminate mode."""
        if indeterminate:
            self._progress_bar.set_fraction(0.0)
            self._progress_bar.pulse()
        else:
            self._progress_bar.set_fraction(self.progress)


class HardwareInfoRow(AdwComponentBase):
    """
    Specialized row component for displaying hardware details.

    Features:
    - Hardware-specific icons and styling
    - Status indicators for hardware health
    - Expandable details for complex hardware info
    - Semantic color coding
    """

    def __init__(self,
                 title: str = "",
                 subtitle: str = "",
                 hardware_type: str = "generic",
                 status: str = "normal",
                 details: Optional[Dict[str, Any]] = None,
                 icon_name: Optional[str] = None,
                 **kwargs):
        self.title = title
        self.subtitle = subtitle
        self.hardware_type = hardware_type
        self.status = status
        self.details = details or {}
        self.icon_name = icon_name or self._get_default_icon()

        super().__init__("hardware-info-row", **kwargs)

    def _init_component(self, **kwargs):
        """Initialize the hardware info row widget."""
        self.widget = Adw.ActionRow()
        self.widget.set_title(self.title)
        if self.subtitle:
            self.widget.set_subtitle(self.subtitle)

        # Add hardware icon
        self._setup_icon()

        # Add status indicator
        self._setup_status_indicator()

        # Add details if available
        if self.details:
            self._setup_details_button()

        # Apply styling
        self.add_css_class("ds-hardware-info-row")
        self._apply_hardware_styling()

        # Apply status-based styling
        if self.status in ["good", "normal"]:
            self.add_css_class("status-success")
        elif self.status == "warning":
            self.add_css_class("status-warning")
        elif self.status in ["error", "critical"]:
            self.add_css_class("status-error")
        else:
            self.add_css_class("status-info")

        # Add accessibility attributes
        self.widget.set_accessible_role(Gtk.AccessibleRole.LIST_ITEM)
        self.widget.update_property([Gtk.AccessibleProperty.LABEL], [f"{self.hardware_type}: {self.title}"])
        if self.subtitle:
            self.widget.update_property([Gtk.AccessibleProperty.DESCRIPTION], [self.subtitle])

    def _get_default_icon(self) -> str:
        """Get default icon based on hardware type."""
        icon_map = {
            "cpu": "cpu-symbolic",
            "memory": "memory-symbolic",
            "storage": "drive-harddisk-symbolic",
            "gpu": "video-display-symbolic",
            "network": "network-wired-symbolic",
            "motherboard": "computer-symbolic",
            "generic": "emblem-system-symbolic"
        }
        return icon_map.get(self.hardware_type, "emblem-system-symbolic")

    def _setup_icon(self):
        """Setup hardware icon."""
        icon = Gtk.Image.new_from_icon_name(self.icon_name)
        icon.set_icon_size(Gtk.IconSize.LARGE)
        icon.add_css_class(f"hardware-{self.hardware_type}")
        self.widget.add_prefix(icon)

    def _setup_status_indicator(self):
        """Setup status indicator."""
        status_icon = Gtk.Image()
        status_icon.set_icon_size(Gtk.IconSize.NORMAL)

        # Set icon and styling based on status
        if self.status == "good" or self.status == "normal":
            status_icon.set_from_icon_name("emblem-ok-symbolic")
            status_icon.add_css_class("success")
        elif self.status == "warning":
            status_icon.set_from_icon_name("dialog-warning-symbolic")
            status_icon.add_css_class("warning")
        elif self.status == "error" or self.status == "critical":
            status_icon.set_from_icon_name("dialog-error-symbolic")
            status_icon.add_css_class("error")
        else:
            status_icon.set_from_icon_name("dialog-information-symbolic")
            status_icon.add_css_class("info")

        self.widget.add_suffix(status_icon)

    def _setup_details_button(self):
        """Setup details expansion button."""
        details_button = Gtk.Button()
        details_button.set_icon_name("view-more-symbolic")
        details_button.add_css_class("flat")
        details_button.set_tooltip_text("Show details")
        self.connect_signal(details_button, "clicked", self._on_details_clicked)

        self.widget.add_suffix(details_button)

    def _apply_hardware_styling(self):
        """Apply hardware-specific styling."""
        self.add_css_class(f"hardware-{self.hardware_type}")
        self.add_css_class(f"status-{self.status}")

    def _on_details_clicked(self, button):
        """Handle details button click."""
        # Create details dialog or popover
        dialog = Adw.MessageDialog()
        dialog.set_heading(f"{self.title} Details")

        # Format details as text
        details_text = ""
        for key, value in self.details.items():
            formatted_key = key.replace('_', ' ').title()
            details_text += f"{formatted_key}: {value}\n"

        dialog.set_body(details_text)
        dialog.add_response("close", "Close")
        dialog.set_default_response("close")

        # Show dialog
        if hasattr(self.widget, 'get_root'):
            root = self.widget.get_root()
            if root:
                dialog.set_transient_for(root)

        dialog.present()

    def update_status(self, new_status: str):
        """Update hardware status."""
        self.status = new_status
        self._apply_hardware_styling()
        # Re-setup status indicator
        # Note: In a full implementation, we'd update the existing indicator

    def update_details(self, new_details: Dict[str, Any]):
        """Update hardware details."""
        self.details = new_details


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
        self.pid = getattr(process_data, 'pid', 0)
        self.name = getattr(process_data, 'name', 'Unknown')
        self.cpu_percent = getattr(process_data, 'cpu_percent', 0.0)
        self.memory_percent = getattr(process_data, 'memory_percent', 0.0)
        self.user = getattr(process_data, 'user', 'unknown')
        self.status = getattr(process_data, 'status', 'unknown')
        self.command = getattr(process_data, 'command', '')

        # Create title and subtitle
        title = f"{self.name} (PID: {self.pid})"
        subtitle = f"User: {self.user} | CPU: {self.cpu_percent:.1f}% | Memory: {self.memory_percent:.1f}%"

        # Initialize with process-specific settings
        super().__init__(
            title=title,
            subtitle=subtitle,
            hardware_type="process",
            status=self._map_process_status(),
            **kwargs
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
            'running': 'normal',
            'sleeping': 'normal',
            'disk-sleep': 'normal',
            'stopped': 'warning',
            'tracing-stop': 'warning',
            'zombie': 'error',
            'dead': 'error',
            'wake-kill': 'error',
            'waking': 'info'
        }
        return status_map.get(self.status.lower(), 'info')

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
        pid = int(parameter.get_string())

        dialog = Adw.MessageDialog()
        dialog.set_heading(f"Process Details - {self.name}")

        details_text = f"""PID: {self.pid}
Name: {self.name}
User: {self.user}
Status: {self.status}
CPU Usage: {self.cpu_percent:.1f}%
Memory Usage: {self.memory_percent:.1f}%
Command: {self.command[:100]}{'...' if len(self.command) > 100 else ''}"""

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
        pid = int(parameter.get_string())

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
        pid = int(parameter.get_string())

        dialog = Adw.MessageDialog()
        dialog.set_heading("Force Kill Process")
        dialog.set_body(f"Are you sure you want to force kill '{self.name}' (PID: {self.pid})?\n\nThis may cause data loss!")

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
        self.cpu_percent = getattr(new_data, 'cpu_percent', 0.0)
        self.memory_percent = getattr(new_data, 'memory_percent', 0.0)
        self.status = getattr(new_data, 'status', 'unknown')

        # Update UI
        self._update_indicators()

        # Highlight if changed significantly
        if (abs(self.cpu_percent - old_cpu) > 1.0 or
            abs(self.memory_percent - old_memory) > 1.0):
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
            self._remove_highlight
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


class BluetoothRow(HardwareInfoRow):
    """
    Individual Bluetooth device display extending hardware row pattern.

    Features:
    - Device data display (name, address, type, connection status)
    - Connection/pairing action controls
    - Device type icons and status indicators
    - Real-time connection state updates
    """

    def __init__(self, device_info, **kwargs):
        # Import required modules
        import sys
        from pathlib import Path
        sys.path.append(str(Path(__file__).parent.parent))

        self.device_info = device_info
        self.action_menu = None
        self.connection_button = None
        self.status_icon = None

        # Determine hardware type and status from device info
        hardware_type = "bluetooth"
        status = self._determine_status()

        # Create title and subtitle
        title = device_info.name or device_info.alias or "Unknown Device"
        subtitle = f"{device_info.address} • {device_info.device_type.title()}"

        # Add connection status to subtitle
        if device_info.connected:
            subtitle += " • Connected"
        elif device_info.paired:
            subtitle += " • Paired"
        else:
            subtitle += " • Discovered"

        super().__init__(
            title=title,
            subtitle=subtitle,
            hardware_type=hardware_type,
            status=status,
            details=self._create_device_details(),
            icon_name=self._get_device_icon(),
            **kwargs
        )

    def _determine_status(self) -> str:
        """Determine device status for styling."""
        if self.device_info.blocked:
            return "error"
        elif self.device_info.connected:
            return "success"
        elif self.device_info.paired:
            return "warning"
        else:
            return "normal"

    def _get_device_icon(self) -> str:
        """Get appropriate icon for device type."""
        device_type_icons = {
            "computer": "computer-symbolic",
            "phone": "phone-symbolic",
            "audio": "audio-headphones-symbolic",
            "peripheral": "input-mouse-symbolic",
            "imaging": "camera-photo-symbolic",
            "wearable": "preferences-system-symbolic",
            "toy": "applications-games-symbolic",
            "health": "applications-science-symbolic",
            "unknown": "bluetooth-symbolic"
        }

        return device_type_icons.get(self.device_info.device_type, "bluetooth-symbolic")

    def _create_device_details(self) -> Dict[str, Any]:
        """Create detailed device information."""
        details = {
            "Address": self.device_info.address,
            "Type": self.device_info.device_type.title(),
            "Paired": "Yes" if self.device_info.paired else "No",
            "Connected": "Yes" if self.device_info.connected else "No",
            "Trusted": "Yes" if self.device_info.trusted else "No",
            "Blocked": "Yes" if self.device_info.blocked else "No"
        }

        if self.device_info.rssi is not None:
            details["Signal Strength"] = f"{self.device_info.rssi} dBm"

        if self.device_info.uuids:
            details["Services"] = f"{len(self.device_info.uuids)} available"

        return details

    def _init_component(self, **kwargs):
        """Initialize the Bluetooth device row."""
        # Call parent initialization
        super()._init_component(**kwargs)

        # Add Bluetooth-specific action controls
        self._add_bluetooth_actions()

        # Apply Bluetooth-specific styling
        self.add_css_class("ds-bluetooth-row")

        # Add connection status styling
        if self.device_info.connected:
            self.add_css_class("bluetooth-connected")
        elif self.device_info.paired:
            self.add_css_class("bluetooth-paired")
        else:
            self.add_css_class("bluetooth-discovered")

    def _add_bluetooth_actions(self):
        """Add Bluetooth-specific action controls."""
        # Create action button box
        action_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        # Connection/Pairing button
        if self.device_info.connected:
            self.connection_button = Gtk.Button()
            self.connection_button.set_label("Disconnect")
            self.connection_button.set_icon_name("network-wireless-disconnected-symbolic")
            self.connection_button.add_css_class("destructive-action")
            self.connection_button.connect("clicked", self._on_disconnect_clicked)
        elif self.device_info.paired:
            self.connection_button = Gtk.Button()
            self.connection_button.set_label("Connect")
            self.connection_button.set_icon_name("network-wireless-symbolic")
            self.connection_button.add_css_class("suggested-action")
            self.connection_button.connect("clicked", self._on_connect_clicked)
        else:
            self.connection_button = Gtk.Button()
            self.connection_button.set_label("Pair")
            self.connection_button.set_icon_name("bluetooth-symbolic")
            self.connection_button.add_css_class("suggested-action")
            self.connection_button.connect("clicked", self._on_pair_clicked)

        action_box.append(self.connection_button)

        # Action menu button
        self.action_menu = Gtk.MenuButton()
        self.action_menu.set_icon_name("view-more-symbolic")
        self.action_menu.set_tooltip_text("Device actions")

        # Create action menu
        menu_model = Gio.Menu()

        if self.device_info.paired:
            if not self.device_info.trusted:
                menu_model.append("Trust Device", "bluetooth.trust")
            else:
                menu_model.append("Untrust Device", "bluetooth.untrust")

            menu_model.append("Remove Device", "bluetooth.remove")

        if not self.device_info.blocked:
            menu_model.append("Block Device", "bluetooth.block")
        else:
            menu_model.append("Unblock Device", "bluetooth.unblock")

        menu_model.append("Device Info", "bluetooth.info")

        self.action_menu.set_menu_model(menu_model)
        action_box.append(self.action_menu)

        # Add action box to the row
        if hasattr(self, '_main_row'):
            self._main_row.add_suffix(action_box)

    def _on_connect_clicked(self, button):
        """Handle connect button click."""
        print(f"🔵 Connecting to {self.device_info.name} ({self.device_info.address})")
        # TODO: Implement actual connection logic

    def _on_disconnect_clicked(self, button):
        """Handle disconnect button click."""
        print(f"🔵 Disconnecting from {self.device_info.name} ({self.device_info.address})")
        # TODO: Implement actual disconnection logic

    def _on_pair_clicked(self, button):
        """Handle pair button click."""
        print(f"🔵 Pairing with {self.device_info.name} ({self.device_info.address})")
        # TODO: Implement actual pairing logic

    def update_device_data(self, new_device_info):
        """Update device data and refresh display."""
        old_connected = self.device_info.connected
        old_paired = self.device_info.paired

        self.device_info = new_device_info

        # Update title and subtitle
        title = new_device_info.name or new_device_info.alias or "Unknown Device"
        subtitle = f"{new_device_info.address} • {new_device_info.device_type.title()}"

        if new_device_info.connected:
            subtitle += " • Connected"
        elif new_device_info.paired:
            subtitle += " • Paired"
        else:
            subtitle += " • Discovered"

        # Update the row content
        if hasattr(self, '_main_row'):
            self._main_row.set_title(title)
            self._main_row.set_subtitle(subtitle)

        # Update styling if connection status changed
        if old_connected != new_device_info.connected or old_paired != new_device_info.paired:
            # Remove old status classes
            self.remove_css_class("bluetooth-connected")
            self.remove_css_class("bluetooth-paired")
            self.remove_css_class("bluetooth-discovered")

            # Add new status class
            if new_device_info.connected:
                self.add_css_class("bluetooth-connected")
            elif new_device_info.paired:
                self.add_css_class("bluetooth-paired")
            else:
                self.add_css_class("bluetooth-discovered")

            # Update connection button
            self._update_connection_button()

    def _update_connection_button(self):
        """Update connection button based on current state."""
        if not self.connection_button:
            return

        if self.device_info.connected:
            self.connection_button.set_label("Disconnect")
            self.connection_button.set_icon_name("network-wireless-disconnected-symbolic")
            self.connection_button.remove_css_class("suggested-action")
            self.connection_button.add_css_class("destructive-action")
        elif self.device_info.paired:
            self.connection_button.set_label("Connect")
            self.connection_button.set_icon_name("network-wireless-symbolic")
            self.connection_button.remove_css_class("destructive-action")
            self.connection_button.add_css_class("suggested-action")
        else:
            self.connection_button.set_label("Pair")
            self.connection_button.set_icon_name("bluetooth-symbolic")
            self.connection_button.remove_css_class("destructive-action")
            self.connection_button.add_css_class("suggested-action")


class AudioDeviceRow(HardwareInfoRow):
    """
    Individual audio device display extending hardware row pattern.

    Features:
    - Audio device data display (name, type, connection, volume)
    - Volume control slider and mute toggle
    - Default device selection and connection switching
    - Device type icons and status indicators
    """

    def __init__(self, device_info, **kwargs):
        # Import required modules
        import sys
        from pathlib import Path
        sys.path.append(str(Path(__file__).parent.parent))

        self.device_info = device_info
        self.volume_scale = None
        self.mute_button = None
        self.default_button = None
        self.connect_button = None

        # Determine hardware type and status from device info
        hardware_type = "audio"
        status = self._determine_status()

        # Create title and subtitle
        title = device_info.display_name
        subtitle = f"{device_info.description} • {device_info.connection_type.title()}"

        # Add volume and status to subtitle
        if device_info.volume is not None:
            volume_text = "Muted" if device_info.is_muted else f"{device_info.volume}%"
            subtitle += f" • {volume_text}"

        if device_info.is_default:
            subtitle += " • Default"

        super().__init__(
            title=title,
            subtitle=subtitle,
            hardware_type=hardware_type,
            status=status,
            details=self._create_device_details(),
            icon_name=self._get_device_icon(),
            **kwargs
        )

    def _determine_status(self) -> str:
        """Determine device status for styling."""
        if self.device_info.is_default:
            return "success"
        elif self.device_info.is_active:
            return "warning"
        elif self.device_info.is_muted:
            return "error"
        else:
            return "normal"

    def _get_device_icon(self) -> str:
        """Get appropriate icon for device type."""
        connection_type_icons = {
            "usb": "audio-headphones-symbolic",
            "hdmi": "video-display-symbolic",
            "bluetooth": "bluetooth-symbolic",
            "internal": "audio-speakers-symbolic",
            "unknown": "audio-card-symbolic"
        }

        return connection_type_icons.get(self.device_info.connection_type, "audio-card-symbolic")

    def _create_device_details(self) -> Dict[str, Any]:
        """Create detailed device information."""
        details = {
            "Card ID": f"hw:{self.device_info.card_id},{self.device_info.device_id}",
            "Connection": self.device_info.connection_type.title(),
            "Driver": self.device_info.driver,
            "Type": self.device_info.device_type.title(),
            "Default": "Yes" if self.device_info.is_default else "No",
            "Active": "Yes" if self.device_info.is_active else "No"
        }

        if self.device_info.volume is not None:
            details["Volume"] = f"{self.device_info.volume}%"
            details["Muted"] = "Yes" if self.device_info.is_muted else "No"

        if self.device_info.subdevices > 1:
            details["Subdevices"] = str(self.device_info.subdevices)

        return details

    def _init_component(self, **kwargs):
        """Initialize the audio device row."""
        # Call parent initialization
        super()._init_component(**kwargs)

        # Add audio-specific controls
        self._add_audio_controls()

        # Apply audio-specific styling
        self.add_css_class("ds-audio-row")

        # Add connection status styling
        if self.device_info.is_default:
            self.add_css_class("audio-default")
        elif self.device_info.is_active:
            self.add_css_class("audio-active")
        elif self.device_info.is_muted:
            self.add_css_class("audio-muted")

    def _add_audio_controls(self):
        """Add audio-specific control widgets."""
        # Create control box
        control_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        # Volume control
        if self.device_info.volume is not None:
            volume_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)

            # Volume icon
            volume_icon = Gtk.Image.new_from_icon_name("audio-volume-medium-symbolic")
            volume_icon.set_icon_size(Gtk.IconSize.NORMAL)
            volume_box.append(volume_icon)

            # Volume scale
            self.volume_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 5)
            self.volume_scale.set_value(self.device_info.volume)
            self.volume_scale.set_size_request(100, -1)
            self.volume_scale.set_tooltip_text(f"Volume: {self.device_info.volume}%")
            self.volume_scale.connect("value-changed", self._on_volume_changed)
            volume_box.append(self.volume_scale)

            # Volume percentage label
            volume_label = Gtk.Label(label=f"{self.device_info.volume}%")
            volume_label.set_size_request(35, -1)
            volume_label.add_css_class("ds-text-caption")
            volume_box.append(volume_label)
            self.volume_label = volume_label

            control_box.append(volume_box)

        # Mute button
        self.mute_button = Gtk.ToggleButton()
        self.mute_button.set_icon_name("audio-volume-muted-symbolic" if self.device_info.is_muted else "audio-volume-high-symbolic")
        self.mute_button.set_active(self.device_info.is_muted)
        self.mute_button.set_tooltip_text("Toggle mute")
        self.mute_button.connect("toggled", self._on_mute_toggled)
        control_box.append(self.mute_button)

        # Default device button
        if not self.device_info.is_default:
            self.default_button = Gtk.Button()
            self.default_button.set_label("Set Default")
            self.default_button.set_icon_name("emblem-default-symbolic")
            self.default_button.set_tooltip_text("Set as default audio device")
            self.default_button.add_css_class("suggested-action")
            self.default_button.connect("clicked", self._on_set_default_clicked)
            control_box.append(self.default_button)

        # Connect/Bluetooth button for Bluetooth devices
        if self.device_info.connection_type == "bluetooth":
            self.connect_button = Gtk.Button()
            self.connect_button.set_label("Connect")
            self.connect_button.set_icon_name("bluetooth-symbolic")
            self.connect_button.set_tooltip_text("Connect Bluetooth audio device")
            self.connect_button.add_css_class("suggested-action")
            self.connect_button.connect("clicked", self._on_connect_clicked)
            control_box.append(self.connect_button)

        # Add control box to the row
        if hasattr(self, 'widget'):
            self.widget.add_suffix(control_box)

    def _on_volume_changed(self, scale):
        """Handle volume scale changes."""
        new_volume = int(scale.get_value())

        # Update device info
        self.device_info.volume = new_volume

        # Update volume label
        if hasattr(self, 'volume_label'):
            self.volume_label.set_text(f"{new_volume}%")

        # Update tooltip
        scale.set_tooltip_text(f"Volume: {new_volume}%")

        print(f"🔊 Volume changed: {self.device_info.name} -> {new_volume}%")
        # TODO: Implement actual volume control via AudioMonitor

    def _on_mute_toggled(self, button):
        """Handle mute button toggle."""
        is_muted = button.get_active()

        # Update device info
        self.device_info.is_muted = is_muted

        # Update button icon
        icon_name = "audio-volume-muted-symbolic" if is_muted else "audio-volume-high-symbolic"
        button.set_icon_name(icon_name)

        print(f"🔊 Mute toggled: {self.device_info.name} -> {'Muted' if is_muted else 'Unmuted'}")
        # TODO: Implement actual mute control via AudioMonitor

    def _on_set_default_clicked(self, button):
        """Handle set default button click."""
        print(f"🔊 Setting default device: {self.device_info.name}")
        # TODO: Implement actual default device setting via AudioMonitor

        # Update UI state
        self.device_info.is_default = True
        button.set_visible(False)

        # Update styling
        self.remove_css_class("audio-active")
        self.remove_css_class("audio-muted")
        self.add_css_class("audio-default")

    def _on_connect_clicked(self, button):
        """Handle Bluetooth connect button click."""
        print(f"🔊 Connecting Bluetooth audio: {self.device_info.name}")
        # TODO: Implement Bluetooth audio connection
