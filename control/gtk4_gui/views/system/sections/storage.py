"""
@llm-doc Storage and GPU Section Handler
@llm-version 1.0.0
@llm-date 2025-11-15

Storage devices and GPU section creation for system information view.
"""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw


class StorageSectionHandler:
    """Handles storage and GPU section creation."""

    @staticmethod
    def create_gpu_details_section(system_info):
        """Create GPU details information section."""
        gpu_group = Adw.PreferencesGroup()
        gpu_group.set_title("Graphics")
        gpu_group.set_description("GPU and graphics information")

        if system_info.gpu and system_info.gpu.vendor != "Unknown":
            vendor_row = Adw.ActionRow()
            vendor_row.set_title("Vendor")
            vendor_row.set_subtitle(system_info.gpu.vendor)
            gpu_group.add(vendor_row)

            if system_info.gpu.model:
                model_row = Adw.ActionRow()
                model_row.set_title("Model")
                model_row.set_subtitle(system_info.gpu.model)
                gpu_group.add(model_row)

            if system_info.gpu.driver:
                driver_row = Adw.ActionRow()
                driver_row.set_title("Driver")
                driver_row.set_subtitle(system_info.gpu.driver)
                gpu_group.add(driver_row)

            if system_info.gpu.memory_mb:
                memory_row = Adw.ActionRow()
                memory_row.set_title("Memory")
                memory_row.set_subtitle(f"{system_info.gpu.memory_mb} MB")
                gpu_group.add(memory_row)
        else:
            empty_row = Adw.ActionRow()
            empty_row.set_title("No GPU information available")
            gpu_group.add(empty_row)

        return gpu_group

    @staticmethod
    def create_storage_section(system_info):
        """Create storage/USB devices information section."""
        storage_group = Adw.PreferencesGroup()
        storage_group.set_title("Storage Devices")
        storage_group.set_description("Disks and USB devices")

        if system_info.storage and system_info.storage.devices:
            summary_row = Adw.ActionRow()
            summary_row.set_title("Total Storage")
            summary_row.set_subtitle(
                f"{system_info.storage.total_storage_gb:.1f} GB ({system_info.storage.total_used_gb:.1f} GB used)"
            )
            storage_group.add(summary_row)

            for device in system_info.storage.devices:
                if "loop" in device.device.lower():
                    continue

                device_row = Adw.ActionRow()
                device_row.set_title(device.device)
                device_row.set_subtitle(
                    f"{device.total_gb:.1f} GB ({device.filesystem}) - {device.usage_percent:.0f}% used"
                )
                storage_group.add(device_row)
        else:
            empty_row = Adw.ActionRow()
            empty_row.set_title("No storage information available")
            storage_group.add(empty_row)

        return storage_group

