"""
@llm-doc Overview and Hardware Section Handler
@llm-version 1.0.0
@llm-date 2025-11-15

System overview and hardware information section creation for system information view.
"""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gtk

# Try to import real components (optional)
try:
    from ..components import InfoCard
except ImportError:
    InfoCard = None


class OverviewSectionHandler:
    """Handles system overview and hardware section creation."""

    @staticmethod
    def create_system_overview_section(system_info):
        """Create system overview section with basic system information."""
        uptime_seconds = system_info.system.uptime_seconds
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        uptime_formatted = f"{uptime_hours}h {uptime_minutes}m"

        overview_data = {
            "os_name": f"{system_info.system.os_name} {system_info.system.os_version}",
            "kernel_version": system_info.system.kernel_version,
            "hostname": system_info.system.hostname,
            "uptime": uptime_formatted,
            "architecture": system_info.system.architecture,
        }

        if InfoCard:
            overview_card = InfoCard(title="System Overview", icon_name="computer-symbolic", data=overview_data)
            return overview_card.get_widget()
        else:
            # Fallback if InfoCard not available
            group = Adw.PreferencesGroup()
            group.set_title("System Overview")
            for key, value in overview_data.items():
                row = Adw.ActionRow()
                row.set_title(key.replace("_", " ").title())
                row.set_subtitle(str(value))
                group.add(row)
            return group

    @staticmethod
    def create_hardware_info_section(system_info):
        """Create hardware information section with detailed hardware data."""
        hardware_group = Adw.PreferencesGroup()
        hardware_group.set_title("Hardware Information")
        hardware_group.set_description("Detailed hardware specifications")

        cpu_row = Adw.ActionRow()
        cpu_row.set_title("Processor")
        cpu_row.set_subtitle(f"{system_info.hardware.cpu_model}")

        cpu_icon = Gtk.Image.new_from_icon_name("cpu-symbolic")
        cpu_row.add_prefix(cpu_icon)
        hardware_group.add(cpu_row)

        memory_row = Adw.ActionRow()
        memory_row.set_title("Memory")
        memory_row.set_subtitle(f"{system_info.hardware.memory_total_gb:.1f} GB ({system_info.hardware.memory_type})")

        memory_icon = Gtk.Image.new_from_icon_name("memory-symbolic")
        memory_row.add_prefix(memory_icon)
        hardware_group.add(memory_row)

        if hasattr(system_info.hardware, "storage_devices"):
            for device in system_info.hardware.storage_devices:
                storage_row = Adw.ActionRow()
                storage_row.set_title(f"Storage: {device.name}")
                storage_row.set_subtitle(f"{device.size_gb:.1f} GB {device.type}")

                storage_icon = Gtk.Image.new_from_icon_name("drive-harddisk-symbolic")
                storage_row.add_prefix(storage_icon)
                hardware_group.add(storage_row)

        if hasattr(system_info.hardware, "gpu_info") and system_info.hardware.gpu_info:
            gpu_row = Adw.ActionRow()
            gpu_row.set_title("Graphics")
            gpu_row.set_subtitle(system_info.hardware.gpu_info)

            gpu_icon = Gtk.Image.new_from_icon_name("video-display-symbolic")
            gpu_row.add_prefix(gpu_icon)
            hardware_group.add(gpu_row)

        return hardware_group

