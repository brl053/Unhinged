"""
SystemInfoView - System Information tab extracted from desktop_app.py

This module contains all the system information functionality that was previously
embedded in the monolithic desktop_app.py file.
"""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, GLib, Gtk

# Import system info components
try:
    from ..system_info import get_system_info

    SYSTEM_INFO_AVAILABLE = True
except ImportError as e:
    SYSTEM_INFO_AVAILABLE = False
    print(f"⚠️ system_info import failed: {e}")

# Import realtime updates
try:
    from ..realtime_system_info import (
        start_realtime_updates,
        stop_realtime_updates,
    )

    REALTIME_AVAILABLE = True
except ImportError:
    REALTIME_AVAILABLE = False

    # Define dummy functions
    def start_realtime_updates(interval=2.0):
        return False

    def stop_realtime_updates():
        pass


# Define fallback component classes
class _FallbackInfoCard:
    def __init__(self, **kwargs):
        self.title = kwargs.get("title", "Info")
        self.data = kwargs.get("data", {})

    def get_widget(self):
        return Gtk.Label(label=self.title)


class _FallbackStatusIndicator:
    def __init__(self, **kwargs):
        pass

    def get_widget(self):
        return Gtk.Label(label="Status")


# Try to import real components (optional)
try:
    from ..components import InfoCard, StatusIndicator
except ImportError:
    InfoCard = _FallbackInfoCard
    StatusIndicator = _FallbackStatusIndicator

# Components are always available (we have fallbacks)
COMPONENTS_AVAILABLE = True


class SystemInfoView:
    """Handles the System Information tab functionality"""

    def __init__(self, parent_app):
        """Initialize with reference to parent app"""
        self.app = parent_app
        self.project_root = parent_app.project_root

        # System info settings
        self.system_info_auto_refresh = getattr(parent_app, "system_info_auto_refresh", False)
        self.system_info_refresh_interval = getattr(parent_app, "system_info_refresh_interval", 30)
        self.realtime_updates_enabled = getattr(parent_app, "realtime_updates_enabled", False)

        # Timer references
        self._auto_refresh_timer_id = None

        # Content references for refresh
        self.system_info_box = None
        self.scrolled_window = None

    def create_content(self):
        """Create the system info tab content with comprehensive system information."""
        # Create main content box
        self.system_info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.system_info_box.set_margin_top(24)
        self.system_info_box.set_margin_bottom(24)
        self.system_info_box.set_margin_start(24)
        self.system_info_box.set_margin_end(24)
        self.system_info_box.set_vexpand(True)
        self.system_info_box.set_hexpand(True)

        # Header section with refresh button
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        header_box.set_margin_bottom(12)

        # Title
        title_label = Gtk.Label(label="System Information")
        title_label.add_css_class("title-2")
        title_label.set_halign(Gtk.Align.START)
        header_box.append(title_label)

        # Refresh button (right-aligned)
        refresh_button = Gtk.Button()
        refresh_button.set_icon_name("view-refresh-symbolic")
        refresh_button.set_tooltip_text("Refresh system information")
        refresh_button.connect("clicked", self._on_refresh_system_info)
        header_box.append(refresh_button)

        self.system_info_box.append(header_box)

        if SYSTEM_INFO_AVAILABLE and COMPONENTS_AVAILABLE:
            # Collect system information
            try:
                system_info = get_system_info(self.project_root, use_cache=True)

                # Create motherboard information section (PRIORITY)
                motherboard_section = self._create_motherboard_section(system_info)
                self.system_info_box.append(motherboard_section)

                # Create CPU details section
                cpu_details_section = self._create_cpu_details_section(system_info)
                self.system_info_box.append(cpu_details_section)

                # Create GPU details section
                gpu_details_section = self._create_gpu_details_section(system_info)
                self.system_info_box.append(gpu_details_section)

                # Create storage section
                storage_section = self._create_storage_section(system_info)
                self.system_info_box.append(storage_section)

                # Create memory section
                memory_section = self._create_memory_section(system_info)
                self.system_info_box.append(memory_section)

                # Create network section
                network_section = self._create_network_section(system_info)
                self.system_info_box.append(network_section)

                # Try to create other sections (may fail if attributes missing)
                try:
                    overview_section = self._create_system_overview_section(system_info)
                    self.system_info_box.append(overview_section)
                except Exception as e:
                    print(f"⚠️ Skipping overview section: {e}")

                try:
                    performance_section = self._create_performance_metrics_section(system_info)
                    self.system_info_box.append(performance_section)
                except Exception as e:
                    print(f"⚠️ Skipping performance section: {e}")

                try:
                    hardware_section = self._create_hardware_info_section(system_info)
                    self.system_info_box.append(hardware_section)
                except Exception as e:
                    print(f"⚠️ Skipping hardware section: {e}")

                try:
                    platform_section = self._create_platform_status_section(system_info)
                    self.system_info_box.append(platform_section)
                except Exception as e:
                    print(f"⚠️ Skipping platform section: {e}")

            except Exception as e:
                # Error handling
                import traceback

                print(f"❌ Error creating system info sections: {e}")
                traceback.print_exc()

                error_group = Adw.PreferencesGroup()
                error_group.set_title("Error")

                error_row = Adw.ActionRow()
                error_row.set_title("Failed to collect system information")
                error_row.set_subtitle(str(e))

                error_icon = Gtk.Image.new_from_icon_name("dialog-error-symbolic")
                error_icon.add_css_class("error")
                error_row.add_prefix(error_icon)

                error_group.add(error_row)
                self.system_info_box.append(error_group)
        else:
            # Fallback when system info or components not available
            fallback_group = Adw.PreferencesGroup()
            fallback_group.set_title("System Information Unavailable")

            fallback_row = Adw.ActionRow()
            if not SYSTEM_INFO_AVAILABLE:
                fallback_row.set_title("System information collection not available")
                fallback_row.set_subtitle("Missing system_info module or dependencies")
            elif not COMPONENTS_AVAILABLE:
                fallback_row.set_title("Component library not available")
                fallback_row.set_subtitle("Missing component library for display")

            fallback_icon = Gtk.Image.new_from_icon_name("dialog-warning-symbolic")
            fallback_icon.add_css_class("warning")
            fallback_row.add_prefix(fallback_icon)

            fallback_group.add(fallback_row)
            self.system_info_box.append(fallback_group)

        # Create scrolled window with proper sizing
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scrolled_window.set_vexpand(True)
        self.scrolled_window.set_hexpand(True)
        self.scrolled_window.set_min_content_height(400)
        self.scrolled_window.set_child(self.system_info_box)

        return self.scrolled_window

    def _create_system_overview_section(self, system_info):
        """Create system overview section with basic system information."""
        # Format uptime
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

        overview_card = InfoCard(
            title="System Overview", icon_name="computer-symbolic", data=overview_data
        )

        return overview_card.get_widget()

    def _create_performance_metrics_section(self, system_info):
        """Create performance metrics section with real-time indicators."""
        performance_group = Adw.PreferencesGroup()
        performance_group.set_title("Performance Metrics")
        performance_group.set_description("Real-time system performance indicators")

        # CPU Usage
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

        # Memory Usage
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

        # Disk Usage
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

        # Start real-time updates for performance indicators
        self._setup_realtime_updates()

        return performance_group

    def _create_hardware_info_section(self, system_info):
        """Create hardware information section with detailed hardware data."""
        hardware_group = Adw.PreferencesGroup()
        hardware_group.set_title("Hardware Information")
        hardware_group.set_description("Detailed hardware specifications")

        # CPU Information
        cpu_row = Adw.ActionRow()
        cpu_row.set_title("Processor")
        cpu_row.set_subtitle(f"{system_info.hardware.cpu_model}")

        cpu_icon = Gtk.Image.new_from_icon_name("cpu-symbolic")
        cpu_row.add_prefix(cpu_icon)
        hardware_group.add(cpu_row)

        # Memory Information
        memory_row = Adw.ActionRow()
        memory_row.set_title("Memory")
        memory_row.set_subtitle(
            f"{system_info.hardware.memory_total_gb:.1f} GB ({system_info.hardware.memory_type})"
        )

        memory_icon = Gtk.Image.new_from_icon_name("memory-symbolic")
        memory_row.add_prefix(memory_icon)
        hardware_group.add(memory_row)

        # Storage Information
        if hasattr(system_info.hardware, "storage_devices"):
            for device in system_info.hardware.storage_devices:
                storage_row = Adw.ActionRow()
                storage_row.set_title(f"Storage: {device.name}")
                storage_row.set_subtitle(f"{device.size_gb:.1f} GB {device.type}")

                storage_icon = Gtk.Image.new_from_icon_name("drive-harddisk-symbolic")
                storage_row.add_prefix(storage_icon)
                hardware_group.add(storage_row)

        # GPU Information
        if hasattr(system_info.hardware, "gpu_info") and system_info.hardware.gpu_info:
            gpu_row = Adw.ActionRow()
            gpu_row.set_title("Graphics")
            gpu_row.set_subtitle(system_info.hardware.gpu_info)

            gpu_icon = Gtk.Image.new_from_icon_name("video-display-symbolic")
            gpu_row.add_prefix(gpu_icon)
            hardware_group.add(gpu_row)

        return hardware_group

    def _create_motherboard_section(self, system_info):
        """Create motherboard information section."""
        motherboard_group = Adw.PreferencesGroup()
        motherboard_group.set_title("Motherboard")
        motherboard_group.set_description("Motherboard and BIOS information")

        if system_info.motherboard:
            # Manufacturer
            if "manufacturer" in system_info.motherboard:
                mfg_row = Adw.ActionRow()
                mfg_row.set_title("Manufacturer")
                mfg_row.set_subtitle(system_info.motherboard["manufacturer"])
                motherboard_group.add(mfg_row)

            # Model
            if "model" in system_info.motherboard:
                model_row = Adw.ActionRow()
                model_row.set_title("Model")
                model_row.set_subtitle(system_info.motherboard["model"])
                motherboard_group.add(model_row)

            # Version
            if "version" in system_info.motherboard:
                version_row = Adw.ActionRow()
                version_row.set_title("Version")
                version_row.set_subtitle(system_info.motherboard["version"])
                motherboard_group.add(version_row)

            # Serial Number
            if "serial" in system_info.motherboard:
                serial_row = Adw.ActionRow()
                serial_row.set_title("Serial Number")
                serial_row.set_subtitle(system_info.motherboard["serial"])
                motherboard_group.add(serial_row)
        else:
            # No motherboard info available
            empty_row = Adw.ActionRow()
            empty_row.set_title("No motherboard information available")
            motherboard_group.add(empty_row)

        return motherboard_group

    def _create_cpu_details_section(self, system_info):
        """Create CPU details information section."""
        cpu_group = Adw.PreferencesGroup()
        cpu_group.set_title("Processor Details")
        cpu_group.set_description("CPU brand, model, and specifications")

        if system_info.cpu_details:
            # Brand
            if "brand" in system_info.cpu_details:
                brand_row = Adw.ActionRow()
                brand_row.set_title("Brand")
                brand_row.set_subtitle(system_info.cpu_details["brand"])
                cpu_group.add(brand_row)

            # Model Name
            if "model_name" in system_info.cpu_details:
                model_row = Adw.ActionRow()
                model_row.set_title("Model")
                model_row.set_subtitle(system_info.cpu_details["model_name"])
                cpu_group.add(model_row)

            # Cache
            if "cache" in system_info.cpu_details:
                cache_row = Adw.ActionRow()
                cache_row.set_title("Cache")
                cache_row.set_subtitle(system_info.cpu_details["cache"])
                cpu_group.add(cache_row)

            # Stepping
            if "stepping" in system_info.cpu_details:
                stepping_row = Adw.ActionRow()
                stepping_row.set_title("Stepping")
                stepping_row.set_subtitle(system_info.cpu_details["stepping"])
                cpu_group.add(stepping_row)

            # Family
            if "family" in system_info.cpu_details:
                family_row = Adw.ActionRow()
                family_row.set_title("Family")
                family_row.set_subtitle(system_info.cpu_details["family"])
                cpu_group.add(family_row)

            # Model Number
            if "model_number" in system_info.cpu_details:
                model_num_row = Adw.ActionRow()
                model_num_row.set_title("Model Number")
                model_num_row.set_subtitle(system_info.cpu_details["model_number"])
                cpu_group.add(model_num_row)
        else:
            # No CPU details available
            empty_row = Adw.ActionRow()
            empty_row.set_title("No CPU details available")
            cpu_group.add(empty_row)

        return cpu_group

    def _create_gpu_details_section(self, system_info):
        """Create GPU details information section."""
        gpu_group = Adw.PreferencesGroup()
        gpu_group.set_title("Graphics")
        gpu_group.set_description("GPU and graphics information")

        if system_info.gpu and system_info.gpu.vendor != "Unknown":
            # Vendor
            vendor_row = Adw.ActionRow()
            vendor_row.set_title("Vendor")
            vendor_row.set_subtitle(system_info.gpu.vendor)
            gpu_group.add(vendor_row)

            # Model
            if system_info.gpu.model:
                model_row = Adw.ActionRow()
                model_row.set_title("Model")
                model_row.set_subtitle(system_info.gpu.model)
                gpu_group.add(model_row)

            # Driver
            if system_info.gpu.driver:
                driver_row = Adw.ActionRow()
                driver_row.set_title("Driver")
                driver_row.set_subtitle(system_info.gpu.driver)
                gpu_group.add(driver_row)

            # Memory
            if system_info.gpu.memory_mb:
                memory_row = Adw.ActionRow()
                memory_row.set_title("Memory")
                memory_row.set_subtitle(f"{system_info.gpu.memory_mb} MB")
                gpu_group.add(memory_row)
        else:
            # No GPU info available
            empty_row = Adw.ActionRow()
            empty_row.set_title("No GPU information available")
            gpu_group.add(empty_row)

        return gpu_group

    def _create_storage_section(self, system_info):
        """Create storage/USB devices information section."""
        storage_group = Adw.PreferencesGroup()
        storage_group.set_title("Storage Devices")
        storage_group.set_description("Disks and USB devices")

        if system_info.storage and system_info.storage.devices:
            # Show summary first
            summary_row = Adw.ActionRow()
            summary_row.set_title("Total Storage")
            summary_row.set_subtitle(
                f"{system_info.storage.total_storage_gb:.1f} GB ({system_info.storage.total_used_gb:.1f} GB used)"
            )
            storage_group.add(summary_row)

            # Show each device (filter out loop devices for cleaner display)
            for device in system_info.storage.devices:
                # Skip loop devices (squashfs) for cleaner display
                if "loop" in device.device.lower():
                    continue

                device_row = Adw.ActionRow()
                device_row.set_title(device.device)
                device_row.set_subtitle(
                    f"{device.total_gb:.1f} GB ({device.filesystem}) - {device.usage_percent:.0f}% used"
                )
                storage_group.add(device_row)
        else:
            # No storage info available
            empty_row = Adw.ActionRow()
            empty_row.set_title("No storage information available")
            storage_group.add(empty_row)

        return storage_group

    def _create_memory_section(self, system_info):
        """Create memory information section."""
        memory_group = Adw.PreferencesGroup()
        memory_group.set_title("Memory")
        memory_group.set_description("RAM and swap information")

        if system_info.memory:
            # Total RAM
            total_row = Adw.ActionRow()
            total_row.set_title("Total RAM")
            total_row.set_subtitle(f"{system_info.memory.total_gb:.1f} GB")
            memory_group.add(total_row)

            # Used RAM
            used_row = Adw.ActionRow()
            used_row.set_title("Used")
            used_row.set_subtitle(
                f"{system_info.memory.used_gb:.1f} GB ({system_info.memory.usage_percent:.0f}%)"
            )
            memory_group.add(used_row)

            # Available RAM
            available_row = Adw.ActionRow()
            available_row.set_title("Available")
            available_row.set_subtitle(f"{system_info.memory.available_gb:.1f} GB")
            memory_group.add(available_row)

            # Swap
            if system_info.memory.swap_total_gb > 0:
                swap_row = Adw.ActionRow()
                swap_row.set_title("Swap")
                swap_row.set_subtitle(
                    f"{system_info.memory.swap_total_gb:.1f} GB ({system_info.memory.swap_used_gb:.1f} GB used, {system_info.memory.swap_percent:.0f}%)"
                )
                memory_group.add(swap_row)
        else:
            # No memory info available
            empty_row = Adw.ActionRow()
            empty_row.set_title("No memory information available")
            memory_group.add(empty_row)

        return memory_group

    def _create_network_section(self, system_info):
        """Create network information section."""
        network_group = Adw.PreferencesGroup()
        network_group.set_title("Network")
        network_group.set_description("Network interfaces and connectivity")

        if system_info.network:
            # Hostname
            hostname_row = Adw.ActionRow()
            hostname_row.set_title("Hostname")
            hostname_row.set_subtitle(system_info.network.hostname)
            network_group.add(hostname_row)

            # Network interfaces (show only active ones with IP addresses)
            active_interfaces = [
                iface
                for iface in system_info.network.interfaces
                if iface.status == "Up" and iface.ip_address
            ]

            if active_interfaces:
                for iface in active_interfaces:
                    iface_row = Adw.ActionRow()
                    iface_row.set_title(iface.name)
                    iface_row.set_subtitle(iface.ip_address)
                    network_group.add(iface_row)
            else:
                # No active interfaces
                empty_row = Adw.ActionRow()
                empty_row.set_title("No active network interfaces")
                network_group.add(empty_row)
        else:
            # No network info available
            empty_row = Adw.ActionRow()
            empty_row.set_title("No network information available")
            network_group.add(empty_row)

        return network_group

    def _create_platform_status_section(self, system_info):
        """Create platform status section with Unhinged-specific information."""
        platform_group = Adw.PreferencesGroup()
        platform_group.set_title("Platform Status")
        platform_group.set_description("Unhinged platform services and components")

        # Python Environment
        python_row = Adw.ActionRow()
        python_row.set_title("Python Environment")
        python_row.set_subtitle(f"Python {system_info.platform.python_version}")

        python_icon = Gtk.Image.new_from_icon_name("applications-development-symbolic")
        python_row.add_prefix(python_icon)
        platform_group.add(python_row)

        # Project Root
        project_row = Adw.ActionRow()
        project_row.set_title("Project Root")
        project_row.set_subtitle(str(self.project_root))

        project_icon = Gtk.Image.new_from_icon_name("folder-symbolic")
        project_row.add_prefix(project_icon)
        platform_group.add(project_row)

        # GTK Version
        gtk_row = Adw.ActionRow()
        gtk_row.set_title("GTK Version")
        gtk_row.set_subtitle(
            f"GTK {Gtk.get_major_version()}.{Gtk.get_minor_version()}.{Gtk.get_micro_version()}"
        )

        gtk_icon = Gtk.Image.new_from_icon_name("applications-graphics-symbolic")
        gtk_row.add_prefix(gtk_icon)
        platform_group.add(gtk_row)

        # Desktop Environment
        if hasattr(system_info.platform, "desktop_environment"):
            desktop_row = Adw.ActionRow()
            desktop_row.set_title("Desktop Environment")
            desktop_row.set_subtitle(system_info.platform.desktop_environment)

            desktop_icon = Gtk.Image.new_from_icon_name("desktop-symbolic")
            desktop_row.add_prefix(desktop_icon)
            platform_group.add(desktop_row)

        # Display Information
        if hasattr(system_info.platform, "display_info"):
            display_row = Adw.ActionRow()
            display_row.set_title("Display")
            display_row.set_subtitle(system_info.platform.display_info)

            graphics_icon = Gtk.Image.new_from_icon_name("video-display-symbolic")
            display_row.add_prefix(graphics_icon)
            platform_group.add(display_row)

        return platform_group

    def _on_refresh_system_info(self, button):
        """Handle refresh button click."""
        if SYSTEM_INFO_AVAILABLE:
            try:
                # Clear cache and collect fresh data
                from ..system_info import SystemInfoCollector

                collector = SystemInfoCollector(self.project_root)
                collector.clear_cache()

                # Refresh the UI by clearing and rebuilding content
                if self.system_info_box:
                    # Remove all children from the box
                    while True:
                        child = self.system_info_box.get_first_child()
                        if child is None:
                            break
                        self.system_info_box.remove(child)

                    # Rebuild content with fresh data
                    system_info = get_system_info(self.project_root, use_cache=False)

                    # Header section with refresh button
                    header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
                    header_box.set_margin_bottom(12)

                    title_label = Gtk.Label(label="System Information")
                    title_label.add_css_class("title-2")
                    title_label.set_halign(Gtk.Align.START)
                    header_box.append(title_label)

                    refresh_button = Gtk.Button()
                    refresh_button.set_icon_name("view-refresh-symbolic")
                    refresh_button.set_tooltip_text("Refresh system information")
                    refresh_button.connect("clicked", self._on_refresh_system_info)
                    header_box.append(refresh_button)

                    self.system_info_box.append(header_box)

                    # Add all sections
                    try:
                        motherboard_section = self._create_motherboard_section(system_info)
                        self.system_info_box.append(motherboard_section)
                    except Exception as e:
                        print(f"⚠️ Skipping motherboard section: {e}")

                    try:
                        cpu_details_section = self._create_cpu_details_section(system_info)
                        self.system_info_box.append(cpu_details_section)
                    except Exception as e:
                        print(f"⚠️ Skipping CPU details section: {e}")

                    try:
                        gpu_details_section = self._create_gpu_details_section(system_info)
                        self.system_info_box.append(gpu_details_section)
                    except Exception as e:
                        print(f"⚠️ Skipping GPU details section: {e}")

                    try:
                        storage_section = self._create_storage_section(system_info)
                        self.system_info_box.append(storage_section)
                    except Exception as e:
                        print(f"⚠️ Skipping storage section: {e}")

                    try:
                        memory_section = self._create_memory_section(system_info)
                        self.system_info_box.append(memory_section)
                    except Exception as e:
                        print(f"⚠️ Skipping memory section: {e}")

                    try:
                        network_section = self._create_network_section(system_info)
                        self.system_info_box.append(network_section)
                    except Exception as e:
                        print(f"⚠️ Skipping network section: {e}")

                    try:
                        overview_section = self._create_system_overview_section(system_info)
                        self.system_info_box.append(overview_section)
                    except Exception as e:
                        print(f"⚠️ Skipping overview section: {e}")

                    try:
                        performance_section = self._create_performance_metrics_section(system_info)
                        self.system_info_box.append(performance_section)
                    except Exception as e:
                        print(f"⚠️ Skipping performance section: {e}")

                    try:
                        hardware_section = self._create_hardware_info_section(system_info)
                        self.system_info_box.append(hardware_section)
                    except Exception as e:
                        print(f"⚠️ Skipping hardware section: {e}")

                    try:
                        platform_section = self._create_platform_status_section(system_info)
                        self.system_info_box.append(platform_section)
                    except Exception as e:
                        print(f"⚠️ Skipping platform section: {e}")

                # Show toast notification
                if hasattr(self.app, "show_toast"):
                    self.app.show_toast("System information refreshed")

                # Log refresh action
                if hasattr(self.app, "session_logger") and self.app.session_logger:
                    self.app.session_logger.log_gui_event(
                        "SYSTEM_INFO_REFRESH", "User refreshed system information"
                    )

            except Exception as e:
                # Show error toast
                if hasattr(self.app, "show_toast"):
                    self.app.show_toast(f"Refresh failed: {str(e)}")

    def _on_auto_refresh_toggled(self, switch, param):
        """Handle auto-refresh toggle."""
        self.system_info_auto_refresh = switch.get_active()

        if self.system_info_auto_refresh:
            # Start auto-refresh
            if SYSTEM_INFO_AVAILABLE:
                self._auto_refresh_timer_id = GLib.timeout_add_seconds(
                    self.system_info_refresh_interval, self._auto_refresh_callback
                )

                # Show toast notification
                if hasattr(self.app, "show_toast"):
                    self.app.show_toast(
                        f"Auto-refresh enabled ({self.system_info_refresh_interval}s interval)"
                    )

                # Log toggle action
                if hasattr(self.app, "session_logger") and self.app.session_logger:
                    self.app.session_logger.log_gui_event(
                        "SYSTEM_INFO_AUTO_REFRESH_ENABLED",
                        f"Auto-refresh enabled with {self.system_info_refresh_interval}s interval",
                    )
        else:
            # Stop auto-refresh
            if self._auto_refresh_timer_id:
                GLib.source_remove(self._auto_refresh_timer_id)
                self._auto_refresh_timer_id = None

            # Show toast notification
            if hasattr(self.app, "show_toast"):
                self.app.show_toast("Auto-refresh disabled")

            # Log toggle action
            if hasattr(self.app, "session_logger") and self.app.session_logger:
                self.app.session_logger.log_gui_event(
                    "SYSTEM_INFO_AUTO_REFRESH_DISABLED", "Auto-refresh disabled"
                )

    def _auto_refresh_callback(self):
        """Auto-refresh callback function."""
        if not self.system_info_auto_refresh:
            return False  # Stop the timer

        try:
            if SYSTEM_INFO_AVAILABLE:
                # Clear cache and collect fresh data
                from ..system_info import SystemInfoCollector

                collector = SystemInfoCollector(self.project_root)
                collector.clear_cache()

                # Log auto-refresh
                if hasattr(self.app, "session_logger") and self.app.session_logger:
                    self.app.session_logger.log_gui_event(
                        "SYSTEM_INFO_AUTO_REFRESH", "Auto-refresh triggered"
                    )

        except Exception as e:
            # Log error but continue auto-refresh
            if hasattr(self.app, "session_logger") and self.app.session_logger:
                self.app.session_logger.log_gui_event("SYSTEM_INFO_AUTO_REFRESH_ERROR", str(e))

        # Return True to continue the timer
        return self.system_info_auto_refresh

    def _setup_realtime_updates(self):
        """Setup real-time updates for performance indicators."""
        if not SYSTEM_INFO_AVAILABLE:
            return

        try:
            if self.realtime_updates_enabled:
                # Start real-time updates
                success = start_realtime_updates(interval=2.0)
                if not success:
                    # Failed to start real-time updates
                    if hasattr(self.app, "session_logger") and self.app.session_logger:
                        self.app.session_logger.log_gui_event(
                            "REALTIME_SETUP_FAILED", "Failed to start real-time updates"
                        )

        except Exception as e:
            if hasattr(self.app, "session_logger") and self.app.session_logger:
                self.app.session_logger.log_gui_event("REALTIME_SETUP_ERROR", str(e))

    def _on_realtime_updates_toggled(self, switch, param):
        """Handle real-time updates toggle."""
        self.realtime_updates_enabled = switch.get_active()

        if self.realtime_updates_enabled:
            # Start real-time updates
            if SYSTEM_INFO_AVAILABLE:
                success = start_realtime_updates(interval=2.0)
                if success:
                    # Show toast notification
                    if hasattr(self.app, "show_toast"):
                        self.app.show_toast("Real-time updates enabled")
                else:
                    # Failed to start - reset switch
                    switch.set_active(False)
                    self.realtime_updates_enabled = False
        else:
            # Stop real-time updates
            if SYSTEM_INFO_AVAILABLE:
                stop_realtime_updates()

                # Show toast notification
                if hasattr(self.app, "show_toast"):
                    self.app.show_toast("Real-time updates disabled")

        # Log toggle action
        if hasattr(self.app, "session_logger") and self.app.session_logger:
            self.app.session_logger.log_gui_event(
                "REALTIME_TOGGLE",
                f"Real-time updates {'enabled' if self.realtime_updates_enabled else 'disabled'}",
            )

    def cleanup(self):
        """Clean up system info components to prevent memory leaks."""
        # Stop auto-refresh timer
        if self._auto_refresh_timer_id:
            GLib.source_remove(self._auto_refresh_timer_id)
            self._auto_refresh_timer_id = None

        # Stop real-time updates
        if SYSTEM_INFO_AVAILABLE and self.realtime_updates_enabled:
            stop_realtime_updates()

        if COMPONENTS_AVAILABLE:
            try:
                # Clear system info cache
                if SYSTEM_INFO_AVAILABLE:
                    from ..system_info import SystemInfoCollector

                    collector = SystemInfoCollector(self.project_root)
                    collector.clear_cache()

                # Log cleanup
                if hasattr(self.app, "session_logger") and self.app.session_logger:
                    self.app.session_logger.log_gui_event(
                        "SYSTEM_INFO_CLEANUP", "System info components cleaned up"
                    )

            except Exception as e:
                if hasattr(self.app, "session_logger") and self.app.session_logger:
                    self.app.session_logger.log_gui_event("SYSTEM_INFO_CLEANUP_ERROR", str(e))
