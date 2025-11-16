"""
@llm-doc Performance and Platform Section Handler
@llm-version 1.0.0
@llm-date 2025-11-15

Performance metrics and platform status section creation for system information view.
"""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gtk

# Try to import real components (optional)
try:
    from ..components import StatusIndicator
    COMPONENTS_AVAILABLE = True
except ImportError:
    COMPONENTS_AVAILABLE = False


class PlatformSectionHandler:
    """Handles performance metrics and platform status section creation."""

    @staticmethod
    def create_performance_metrics_section(system_info):
        """Create performance metrics section with real-time indicators."""
        performance_group = Adw.PreferencesGroup()
        performance_group.set_title("Performance Metrics")
        performance_group.set_description("Real-time system performance indicators")

        cpu_row = Adw.ActionRow()
        cpu_row.set_title("CPU Usage")
        cpu_row.set_subtitle(
            f"{system_info.performance.cpu_count} cores, {system_info.performance.cpu_freq_current:.1f} MHz"
        )

        if COMPONENTS_AVAILABLE:
            cpu_indicator = StatusIndicator(
                value=system_info.performance.cpu_percent,
                max_value=100,
                unit="%",
                status="success"
                if system_info.performance.cpu_percent < 70
                else "warning"
                if system_info.performance.cpu_percent < 90
                else "error",
            )
            cpu_row.add_suffix(cpu_indicator.get_widget())

        performance_group.add(cpu_row)

        memory_row = Adw.ActionRow()
        memory_row.set_title("Memory Usage")
        memory_row.set_subtitle(f"{system_info.performance.memory_total_gb:.1f} GB total")

        if COMPONENTS_AVAILABLE:
            memory_indicator = StatusIndicator(
                value=system_info.performance.memory_percent,
                max_value=100,
                unit="%",
                status="success"
                if system_info.performance.memory_percent < 70
                else "warning"
                if system_info.performance.memory_percent < 90
                else "error",
            )
            memory_row.add_suffix(memory_indicator.get_widget())

        performance_group.add(memory_row)

        disk_row = Adw.ActionRow()
        disk_row.set_title("Disk Usage")
        disk_row.set_subtitle(f"{system_info.performance.disk_total_gb:.1f} GB total")

        if COMPONENTS_AVAILABLE:
            disk_indicator = StatusIndicator(
                value=system_info.performance.disk_percent,
                max_value=100,
                unit="%",
                status="success"
                if system_info.performance.disk_percent < 70
                else "warning"
                if system_info.performance.disk_percent < 90
                else "error",
            )
            disk_row.add_suffix(disk_indicator.get_widget())

        performance_group.add(disk_row)

        return performance_group

    @staticmethod
    def create_platform_status_section(system_info, project_root):
        """Create platform status section with Unhinged-specific information."""
        platform_group = Adw.PreferencesGroup()
        platform_group.set_title("Platform Status")
        platform_group.set_description("Unhinged platform services and components")

        python_row = Adw.ActionRow()
        python_row.set_title("Python Environment")
        python_row.set_subtitle(f"Python {system_info.platform.python_version}")

        python_icon = Gtk.Image.new_from_icon_name("applications-development-symbolic")
        python_row.add_prefix(python_icon)
        platform_group.add(python_row)

        project_row = Adw.ActionRow()
        project_row.set_title("Project Root")
        project_row.set_subtitle(str(project_root))

        project_icon = Gtk.Image.new_from_icon_name("folder-symbolic")
        project_row.add_prefix(project_icon)
        platform_group.add(project_row)

        gtk_row = Adw.ActionRow()
        gtk_row.set_title("GTK Version")
        gtk_row.set_subtitle(f"GTK {Gtk.get_major_version()}.{Gtk.get_minor_version()}.{Gtk.get_micro_version()}")

        gtk_icon = Gtk.Image.new_from_icon_name("applications-graphics-symbolic")
        gtk_row.add_prefix(gtk_icon)
        platform_group.add(gtk_row)

        if hasattr(system_info.platform, "desktop_environment"):
            desktop_row = Adw.ActionRow()
            desktop_row.set_title("Desktop Environment")
            desktop_row.set_subtitle(system_info.platform.desktop_environment)

            desktop_icon = Gtk.Image.new_from_icon_name("desktop-symbolic")
            desktop_row.add_prefix(desktop_icon)
            platform_group.add(desktop_row)

        if hasattr(system_info.platform, "display_info"):
            display_row = Adw.ActionRow()
            display_row.set_title("Display")
            display_row.set_subtitle(system_info.platform.display_info)

            graphics_icon = Gtk.Image.new_from_icon_name("video-display-symbolic")
            display_row.add_prefix(graphics_icon)
            platform_group.add(display_row)

        return platform_group

