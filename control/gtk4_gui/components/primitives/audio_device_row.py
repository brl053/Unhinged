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

from typing import Any

from gi.repository import Gtk

from .hardware_info_row import HardwareInfoRow

logger = logging.getLogger(__name__)


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
            **kwargs,
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
            "unknown": "audio-card-symbolic",
        }

        return connection_type_icons.get(
            self.device_info.connection_type, "audio-card-symbolic"
        )

    def _create_device_details(self) -> dict[str, Any]:
        """Create detailed device information."""
        details = {
            "Card ID": f"hw:{self.device_info.card_id},{self.device_info.device_id}",
            "Connection": self.device_info.connection_type.title(),
            "Driver": self.device_info.driver,
            "Type": self.device_info.device_type.title(),
            "Default": "Yes" if self.device_info.is_default else "No",
            "Active": "Yes" if self.device_info.is_active else "No",
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
            self.volume_scale = Gtk.Scale.new_with_range(
                Gtk.Orientation.HORIZONTAL, 0, 100, 5
            )
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
        self.mute_button.set_icon_name(
            "audio-volume-muted-symbolic"
            if self.device_info.is_muted
            else "audio-volume-high-symbolic"
        )
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
        if hasattr(self, "widget"):
            self.widget.add_suffix(control_box)

    def _on_volume_changed(self, scale):
        """Handle volume scale changes."""
        new_volume = int(scale.get_value())

        # Update device info
        self.device_info.volume = new_volume

        # Update volume label
        if hasattr(self, "volume_label"):
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
        icon_name = (
            "audio-volume-muted-symbolic" if is_muted else "audio-volume-high-symbolic"
        )
        button.set_icon_name(icon_name)

        print(
            f"🔊 Mute toggled: {self.device_info.name} -> {'Muted' if is_muted else 'Unmuted'}"
        )
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
