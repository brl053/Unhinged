"""
@llm-doc CPU Details Section Handler
@llm-version 1.0.0
@llm-date 2025-11-15

CPU and motherboard section creation for system information view.
"""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gtk


class CPUSectionHandler:
    """Handles CPU and motherboard section creation."""

    @staticmethod
    def create_motherboard_section(system_info):
        """Create motherboard information section."""
        motherboard_group = Adw.PreferencesGroup()
        motherboard_group.set_title("Motherboard")
        motherboard_group.set_description("Motherboard and BIOS information")

        if system_info.motherboard:
            if "manufacturer" in system_info.motherboard:
                mfg_row = Adw.ActionRow()
                mfg_row.set_title("Manufacturer")
                mfg_row.set_subtitle(system_info.motherboard["manufacturer"])
                motherboard_group.add(mfg_row)

            if "model" in system_info.motherboard:
                model_row = Adw.ActionRow()
                model_row.set_title("Model")
                model_row.set_subtitle(system_info.motherboard["model"])
                motherboard_group.add(model_row)

            if "version" in system_info.motherboard:
                version_row = Adw.ActionRow()
                version_row.set_title("Version")
                version_row.set_subtitle(system_info.motherboard["version"])
                motherboard_group.add(version_row)

            if "serial" in system_info.motherboard:
                serial_row = Adw.ActionRow()
                serial_row.set_title("Serial Number")
                serial_row.set_subtitle(system_info.motherboard["serial"])
                motherboard_group.add(serial_row)
        else:
            empty_row = Adw.ActionRow()
            empty_row.set_title("No motherboard information available")
            motherboard_group.add(empty_row)

        return motherboard_group

    @staticmethod
    def create_cpu_details_section(system_info):
        """Create CPU details information section."""
        cpu_group = Adw.PreferencesGroup()
        cpu_group.set_title("Processor Details")
        cpu_group.set_description("CPU brand, model, and specifications")

        if system_info.cpu_details:
            if "brand" in system_info.cpu_details:
                brand_row = Adw.ActionRow()
                brand_row.set_title("Brand")
                brand_row.set_subtitle(system_info.cpu_details["brand"])
                cpu_group.add(brand_row)

            if "model_name" in system_info.cpu_details:
                model_row = Adw.ActionRow()
                model_row.set_title("Model")
                model_row.set_subtitle(system_info.cpu_details["model_name"])
                cpu_group.add(model_row)

            if "cache" in system_info.cpu_details:
                cache_row = Adw.ActionRow()
                cache_row.set_title("Cache")
                cache_row.set_subtitle(system_info.cpu_details["cache"])
                cpu_group.add(cache_row)

            if "stepping" in system_info.cpu_details:
                stepping_row = Adw.ActionRow()
                stepping_row.set_title("Stepping")
                stepping_row.set_subtitle(system_info.cpu_details["stepping"])
                cpu_group.add(stepping_row)

            if "family" in system_info.cpu_details:
                family_row = Adw.ActionRow()
                family_row.set_title("Family")
                family_row.set_subtitle(system_info.cpu_details["family"])
                cpu_group.add(family_row)

            if "model_number" in system_info.cpu_details:
                model_num_row = Adw.ActionRow()
                model_num_row.set_title("Model Number")
                model_num_row.set_subtitle(system_info.cpu_details["model_number"])
                cpu_group.add(model_num_row)
        else:
            empty_row = Adw.ActionRow()
            empty_row.set_title("No CPU details available")
            cpu_group.add(empty_row)

        return cpu_group

