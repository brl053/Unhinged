"""
Input View - Audio input device management interface.

Simple React component-like view for managing audio input devices.
Uses basic device detection without complex hooks for now.
"""

import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
import re
import subprocess

from gi.repository import Adw, Gtk


class InputView:
    """Input devices view (like a React functional component)."""

    def __init__(self):
        # Simple initialization without complex hooks for now
        self.devices = self._get_input_devices()
        self.current_device = self._get_current_default_device()
        self.container = None
        self.devices_group = None

    def render(self) -> Gtk.Widget:
        """Render the input view (like React's render method)."""
        self.container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.container.set_margin_top(24)
        self.container.set_margin_bottom(24)
        self.container.set_margin_start(24)
        self.container.set_margin_end(24)

        # Header section
        header = self._render_header()
        self.container.append(header)

        # Current status section
        if self.current_device:
            status = self._render_current_status()
            self.container.append(status)

        # Device list section
        devices = self._render_device_list()
        self.devices_group = devices
        self.container.append(devices)

        return self.container

    def _render_header(self) -> Gtk.Widget:
        """Render header section."""
        header_group = Adw.PreferencesGroup()
        header_group.set_title("Audio Input Devices")
        header_group.set_description("Available microphones and audio input devices")

        # Header row with refresh button
        info_row = Adw.ActionRow()
        info_row.set_title("Input System")
        info_row.set_subtitle("List of available audio input devices")

        # Microphone icon
        mic_icon = Gtk.Image.new_from_icon_name("audio-input-microphone-symbolic")
        mic_icon.set_icon_size(Gtk.IconSize.LARGE)
        info_row.add_prefix(mic_icon)

        # Refresh button
        refresh_button = Gtk.Button(label="Refresh")
        refresh_button.add_css_class("flat")
        refresh_button.connect("clicked", self._on_refresh_clicked)
        info_row.add_suffix(refresh_button)

        header_group.add(info_row)
        return header_group

    def _render_current_status(self) -> Gtk.Widget:
        """Render current device status section."""
        status_group = Adw.PreferencesGroup()
        status_group.set_title("Current Status")

        if self.current_device:
            status_row = Adw.ActionRow()
            status_row.set_title("Active Input Device")
            status_row.set_subtitle(f"{self.current_device.get('name', 'Unknown Device')}")

            # Active icon
            active_icon = Gtk.Image.new_from_icon_name("emblem-ok-symbolic")
            active_icon.set_icon_size(Gtk.IconSize.NORMAL)
            active_icon.add_css_class("success")
            status_row.add_prefix(active_icon)

            status_group.add(status_row)

        return status_group



    def _render_device_list(self) -> Gtk.Widget:
        """Render the list of audio devices."""
        devices_group = Adw.PreferencesGroup()
        devices_group.set_title("Input Devices")

        if self.devices:
            for device in self.devices:
                device_row = self._create_device_row(device)
                devices_group.add(device_row)
        else:
            # No devices found
            no_devices_row = Adw.ActionRow()
            no_devices_row.set_title("No Input Devices Found")
            no_devices_row.set_subtitle("No audio input devices detected")

            warning_icon = Gtk.Image.new_from_icon_name("dialog-warning-symbolic")
            warning_icon.set_icon_size(Gtk.IconSize.NORMAL)
            no_devices_row.add_prefix(warning_icon)

            devices_group.add(no_devices_row)

        return devices_group

    def _create_device_row(self, device) -> Adw.ActionRow:
        """Create a row for an audio device."""
        device_row = Adw.ActionRow()
        device_row.set_title(device['name'])

        # Check if this device is currently active
        is_active = self._is_device_active(device)

        if is_active:
            device_row.set_subtitle(f"{device['description']} • Currently Active")
            # Add checkmark icon
            check_icon = Gtk.Image.new_from_icon_name("emblem-ok-symbolic")
            check_icon.set_icon_size(Gtk.IconSize.NORMAL)
            check_icon.add_css_class("success")
            device_row.add_suffix(check_icon)
        else:
            device_row.set_subtitle(device['description'])
            # Add "Set as Default" button
            default_button = Gtk.Button(label="Set as Default")
            default_button.add_css_class("suggested-action")
            default_button.connect("clicked", self._on_set_default_clicked, device)
            device_row.add_suffix(default_button)

        # Add device icon
        device_icon = Gtk.Image.new_from_icon_name(device['icon'])
        device_icon.set_icon_size(Gtk.IconSize.NORMAL)
        device_row.add_prefix(device_icon)

        return device_row

    def _get_input_devices(self):
        """Get list of audio input devices using arecord."""
        devices = []

        try:
            # Use arecord -l to list input devices
            result = subprocess.run(
                ['arecord', '-l'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    line = line.strip()

                    # Parse card line: "card 1: LIGHTSPEED [PRO X 2 LIGHTSPEED], device 0: USB Audio [USB Audio]"
                    card_match = re.match(
                        r'card (\d+): (\w+) \[([^\]]+)\], device (\d+): ([^[]+) \[([^\]]+)\]',
                        line
                    )

                    if card_match:
                        card_id = int(card_match.group(1))
                        card_name = card_match.group(2)
                        card_desc = card_match.group(3)
                        device_id = int(card_match.group(4))
                        device_name = card_match.group(5).strip()
                        device_desc = card_match.group(6)

                        # Determine device icon
                        if "camera" in card_desc.lower() or "webcam" in card_desc.lower():
                            icon = "camera-web-symbolic"
                        elif "headset" in card_desc.lower() or "lightspeed" in card_desc.lower():
                            icon = "audio-headphones-symbolic"
                        else:
                            icon = "audio-input-microphone-symbolic"

                        device = {
                            'name': card_desc,
                            'description': f"Card {card_id}, Device {device_id} - {device_desc}",
                            'card_id': card_id,
                            'device_id': device_id,
                            'alsa_device': f"hw:{card_id},{device_id}",
                            'icon': icon
                        }

                        devices.append(device)

        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            # Return empty list on any error
            pass

        return devices

    def _get_current_default_device(self):
        """Get the current default input device from the system."""
        try:
            # Try to get default source from wpctl (PipeWire)
            result = subprocess.run(
                ['wpctl', 'status'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                # Parse wpctl output to find default source
                lines = result.stdout.split('\n')
                in_sources_section = False

                for line in lines:
                    if 'Sources:' in line:
                        in_sources_section = True
                        continue
                    elif in_sources_section and ('├─' in line or '└─' in line):
                        # Check if this line has an asterisk (default device)
                        if '*' in line:
                            match = re.search(r'(\d+)\.\s+([^[]+)', line)
                            if match:
                                device_id = match.group(1).strip()
                                device_name = match.group(2).strip()
                                return {
                                    'id': device_id,
                                    'name': device_name,
                                    'source': 'wpctl'
                                }
                    elif in_sources_section and ('Sinks:' in line or line.strip() == ''):
                        # End of sources section
                        break

        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            pass

        return None

    def _is_device_active(self, device):
        """Check if a device is currently active."""
        if not self.current_device:
            return False

        # Match by name (for PipeWire devices)
        if device['name'] in self.current_device.get('name', ''):
            return True

        return False

    def _on_refresh_clicked(self, button):
        """Handle refresh button click."""
        self.devices = self._get_input_devices()
        self.current_device = self._get_current_default_device()
        print("🔄 Audio devices refreshed")

        # Re-render the device list
        if self.devices_group and self.container:
            self._refresh_device_list_ui()

    def _refresh_device_list_ui(self):
        """Refresh the device list UI without recreating the entire view."""
        if not self.devices_group:
            return

        # Remove all children from the devices group
        while True:
            child = self.devices_group.get_first_child()
            if child is None:
                break
            self.devices_group.remove(child)

        # Re-add devices
        if self.devices:
            for device in self.devices:
                device_row = self._create_device_row(device)
                self.devices_group.add(device_row)
        else:
            # No devices found
            no_devices_row = Adw.ActionRow()
            no_devices_row.set_title("No Input Devices Found")
            no_devices_row.set_subtitle("No audio input devices detected")

            warning_icon = Gtk.Image.new_from_icon_name("dialog-warning-symbolic")
            warning_icon.set_icon_size(Gtk.IconSize.NORMAL)
            no_devices_row.add_prefix(warning_icon)

            self.devices_group.add(no_devices_row)

    def _on_set_default_clicked(self, button, device):
        """Handle set default button click."""
        try:
            from pathlib import Path

            # Create ALSA configuration for default input device
            asoundrc_content = f"""# ALSA configuration - Default input device set by Unhinged
# Device: {device['name']} ({device['alsa_device']})

pcm.!default {{
    type plug
    slave {{
        pcm "hw:{device['card_id']},{device['device_id']}"
    }}
}}

ctl.!default {{
    type hw
    card {device['card_id']}
}}
"""

            # Write to ~/.asoundrc
            asoundrc_path = Path.home() / ".asoundrc"
            with open(asoundrc_path, 'w') as f:
                f.write(asoundrc_content)

            button.set_label("✓ Set as Default")
            button.set_sensitive(False)
            button.remove_css_class("suggested-action")
            button.add_css_class("success")
            print(f"✅ Set {device['name']} as default input device")

        except Exception as e:
            button.set_label("❌ Error")
            button.set_sensitive(False)
            button.remove_css_class("suggested-action")
            button.add_css_class("destructive")
            print(f"❌ Failed to set {device['name']} as default: {e}")
