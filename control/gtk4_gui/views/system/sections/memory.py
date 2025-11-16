"""
@llm-doc Memory and Network Section Handler
@llm-version 1.0.0
@llm-date 2025-11-15

Memory and network section creation for system information view.
"""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gtk


class MemorySectionHandler:
    """Handles memory and network section creation."""

    @staticmethod
    def create_memory_section(system_info):
        """Create memory information section."""
        memory_group = Adw.PreferencesGroup()
        memory_group.set_title("Memory")
        memory_group.set_description("RAM and swap information")

        if system_info.memory:
            total_row = Adw.ActionRow()
            total_row.set_title("Total RAM")
            total_row.set_subtitle(f"{system_info.memory.total_gb:.1f} GB")
            memory_group.add(total_row)

            used_row = Adw.ActionRow()
            used_row.set_title("Used")
            used_row.set_subtitle(f"{system_info.memory.used_gb:.1f} GB ({system_info.memory.usage_percent:.0f}%)")
            memory_group.add(used_row)

            available_row = Adw.ActionRow()
            available_row.set_title("Available")
            available_row.set_subtitle(f"{system_info.memory.available_gb:.1f} GB")
            memory_group.add(available_row)

            if system_info.memory.swap_total_gb > 0:
                swap_row = Adw.ActionRow()
                swap_row.set_title("Swap")
                swap_row.set_subtitle(
                    f"{system_info.memory.swap_total_gb:.1f} GB "
                    f"({system_info.memory.swap_used_gb:.1f} GB used, {system_info.memory.swap_percent:.0f}%)"
                )
                memory_group.add(swap_row)
        else:
            empty_row = Adw.ActionRow()
            empty_row.set_title("No memory information available")
            memory_group.add(empty_row)

        return memory_group

    @staticmethod
    def create_network_section(system_info):
        """Create network information section."""
        network_group = Adw.PreferencesGroup()
        network_group.set_title("Network")
        network_group.set_description("Network interfaces and connectivity")

        if system_info.network:
            hostname_row = Adw.ActionRow()
            hostname_row.set_title("Hostname")
            hostname_row.set_subtitle(system_info.network.hostname)
            network_group.add(hostname_row)

            active_interfaces = [
                iface for iface in system_info.network.interfaces if iface.status == "Up" and iface.ip_address
            ]

            if active_interfaces:
                for iface in active_interfaces:
                    iface_row = Adw.ActionRow()
                    iface_row.set_title(iface.name)
                    iface_row.set_subtitle(iface.ip_address)
                    network_group.add(iface_row)
            else:
                empty_row = Adw.ActionRow()
                empty_row.set_title("No active network interfaces")
                network_group.add(empty_row)
        else:
            empty_row = Adw.ActionRow()
            empty_row.set_title("No network information available")
            network_group.add(empty_row)

        return network_group

