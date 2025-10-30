"""
SystemInfoView - System Information tab extracted from desktop_app.py

This module contains all the system information functionality that was previously
embedded in the monolithic desktop_app.py file.
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GLib, Gio

# Import system info components
try:
    from system_info import get_system_info, start_realtime_updates, stop_realtime_updates
    SYSTEM_INFO_AVAILABLE = True
except ImportError:
    SYSTEM_INFO_AVAILABLE = False

# Import component library
try:
    from ..components import InfoCard, StatusIndicator, ActionRow
    COMPONENTS_AVAILABLE = True
except ImportError:
    COMPONENTS_AVAILABLE = False


class SystemInfoView:
    """Handles the System Information tab functionality"""
    
    def __init__(self, parent_app):
        """Initialize with reference to parent app"""
        self.app = parent_app
        self.project_root = parent_app.project_root
        
        # System info settings
        self.system_info_auto_refresh = getattr(parent_app, 'system_info_auto_refresh', False)
        self.system_info_refresh_interval = getattr(parent_app, 'system_info_refresh_interval', 30)
        self.realtime_updates_enabled = getattr(parent_app, 'realtime_updates_enabled', False)
        
        # Timer references
        self._auto_refresh_timer_id = None
        
    def create_content(self):
        """Create the system info tab content with comprehensive system information."""
        # Create main content box
        system_info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        system_info_box.set_margin_top(24)
        system_info_box.set_margin_bottom(24)
        system_info_box.set_margin_start(24)
        system_info_box.set_margin_end(24)
        system_info_box.set_vexpand(True)
        system_info_box.set_hexpand(True)

        # Header section
        header_group = Adw.PreferencesGroup()
        header_group.set_title("System Information")
        header_group.set_description("Comprehensive system hardware and performance information")
        system_info_box.append(header_group)

        if SYSTEM_INFO_AVAILABLE and COMPONENTS_AVAILABLE:
            # Collect system information
            try:
                system_info = get_system_info(self.project_root, use_cache=True)

                # Create system overview section
                overview_section = self._create_system_overview_section(system_info)
                system_info_box.append(overview_section)

                # Create performance metrics section
                performance_section = self._create_performance_metrics_section(system_info)
                system_info_box.append(performance_section)

                # Create hardware information section
                hardware_section = self._create_hardware_info_section(system_info)
                system_info_box.append(hardware_section)

                # Create platform status section
                platform_section = self._create_platform_status_section(system_info)
                system_info_box.append(platform_section)

                # Add refresh button
                refresh_section = self._create_refresh_section()
                system_info_box.append(refresh_section)

            except Exception as e:
                # Error handling
                error_group = Adw.PreferencesGroup()
                error_group.set_title("Error")

                error_row = Adw.ActionRow()
                error_row.set_title("Failed to collect system information")
                error_row.set_subtitle(str(e))

                error_icon = Gtk.Image.new_from_icon_name("dialog-error-symbolic")
                error_icon.add_css_class("error")
                error_row.add_prefix(error_icon)

                error_group.add(error_row)
                system_info_box.append(error_group)
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
            system_info_box.append(fallback_group)

        # Create scrolled window with proper sizing
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)
        scrolled.set_hexpand(True)
        scrolled.set_min_content_height(400)
        scrolled.set_child(system_info_box)

        return scrolled

    def _create_system_overview_section(self, system_info):
        """Create system overview section with basic system information."""
        overview_data = {
            "os_name": f"{system_info.system.os_name} {system_info.system.os_version}",
            "kernel_version": system_info.system.kernel_version,
            "hostname": system_info.system.hostname,
            "uptime": system_info.system.uptime_formatted,
            "architecture": system_info.system.architecture
        }

        overview_card = InfoCard(
            title="System Overview",
            icon_name="computer-symbolic",
            data=overview_data
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
        cpu_row.set_subtitle(f"{system_info.performance.cpu_count} cores, {system_info.performance.cpu_freq_current:.1f} MHz")

        if COMPONENTS_AVAILABLE:
            cpu_indicator = StatusIndicator(
                value=system_info.performance.cpu_percent,
                max_value=100,
                unit="%",
                status="success" if system_info.performance.cpu_percent < 70 else "warning" if system_info.performance.cpu_percent < 90 else "error"
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
                status="success" if system_info.performance.memory_percent < 70 else "warning" if system_info.performance.memory_percent < 90 else "error"
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
                status="success" if system_info.performance.disk_percent < 70 else "warning" if system_info.performance.disk_percent < 90 else "error"
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

        if COMPONENTS_AVAILABLE:
            cpu_details = ActionRow(
                title="CPU Details",
                subtitle=f"Cores: {system_info.hardware.cpu_cores}, Threads: {system_info.hardware.cpu_threads}",
                icon_name="cpu-symbolic"
            )
            hardware_group.add(cpu_details.get_widget())
        else:
            hardware_group.add(cpu_row)

        # Memory Information
        memory_row = Adw.ActionRow()
        memory_row.set_title("Memory")
        memory_row.set_subtitle(f"{system_info.hardware.memory_total_gb:.1f} GB ({system_info.hardware.memory_type})")

        memory_icon = Gtk.Image.new_from_icon_name("memory-symbolic")
        memory_row.add_prefix(memory_icon)
        hardware_group.add(memory_row)

        # Storage Information
        if hasattr(system_info.hardware, 'storage_devices'):
            for device in system_info.hardware.storage_devices:
                storage_row = Adw.ActionRow()
                storage_row.set_title(f"Storage: {device.name}")
                storage_row.set_subtitle(f"{device.size_gb:.1f} GB {device.type}")

                storage_icon = Gtk.Image.new_from_icon_name("drive-harddisk-symbolic")
                storage_row.add_prefix(storage_icon)
                hardware_group.add(storage_row)

        # GPU Information
        if hasattr(system_info.hardware, 'gpu_info') and system_info.hardware.gpu_info:
            gpu_row = Adw.ActionRow()
            gpu_row.set_title("Graphics")
            gpu_row.set_subtitle(system_info.hardware.gpu_info)

            gpu_icon = Gtk.Image.new_from_icon_name("video-display-symbolic")
            gpu_row.add_prefix(gpu_icon)

            if COMPONENTS_AVAILABLE:
                gpu_details = ActionRow(
                    title="GPU Details",
                    subtitle=system_info.hardware.gpu_info,
                    icon_name="video-display-symbolic"
                )
                hardware_group.add(gpu_details.get_widget())
            else:
                hardware_group.add(gpu_row)

        return hardware_group

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
        gtk_row.set_subtitle(f"GTK {Gtk.get_major_version()}.{Gtk.get_minor_version()}.{Gtk.get_micro_version()}")

        gtk_icon = Gtk.Image.new_from_icon_name("applications-graphics-symbolic")
        gtk_row.add_prefix(gtk_icon)
        platform_group.add(gtk_row)

        # Desktop Environment
        if hasattr(system_info.platform, 'desktop_environment'):
            desktop_row = Adw.ActionRow()
            desktop_row.set_title("Desktop Environment")
            desktop_row.set_subtitle(system_info.platform.desktop_environment)

            desktop_icon = Gtk.Image.new_from_icon_name("desktop-symbolic")
            desktop_row.add_prefix(desktop_icon)
            platform_group.add(desktop_row)

        # Display Information
        if hasattr(system_info.platform, 'display_info'):
            display_row = Adw.ActionRow()
            display_row.set_title("Display")
            display_row.set_subtitle(system_info.platform.display_info)

            graphics_icon = Gtk.Image.new_from_icon_name("video-display-symbolic")
            graphics_row.add_prefix(graphics_icon)
            platform_group.add(graphics_row)

        return platform_group

    def _create_refresh_section(self):
        """Create refresh controls section."""
        refresh_group = Adw.PreferencesGroup()
        refresh_group.set_title("Controls")

        # Manual refresh row
        refresh_row = Adw.ActionRow()
        refresh_row.set_title("Refresh System Information")
        refresh_row.set_subtitle("Update all system information and metrics")

        refresh_button = Gtk.Button()
        refresh_button.set_icon_name("view-refresh-symbolic")
        refresh_button.add_css_class("suggested-action")
        refresh_button.set_tooltip_text("Refresh system information")
        refresh_button.connect("clicked", self._on_refresh_system_info)

        refresh_row.add_suffix(refresh_button)
        refresh_group.add(refresh_row)

        # Auto-refresh row
        auto_refresh_row = Adw.ActionRow()
        auto_refresh_row.set_title("Auto-Refresh")
        auto_refresh_row.set_subtitle(f"Automatically refresh every {self.system_info_refresh_interval} seconds")

        auto_refresh_switch = Gtk.Switch()
        auto_refresh_switch.set_active(self.system_info_auto_refresh)
        auto_refresh_switch.connect("notify::active", self._on_auto_refresh_toggled)

        auto_refresh_row.add_suffix(auto_refresh_switch)
        refresh_group.add(auto_refresh_row)

        # Real-time updates row
        realtime_row = Adw.ActionRow()
        realtime_row.set_title("Real-time Performance Updates")
        realtime_row.set_subtitle("Live updating of CPU, memory, and disk usage (2s interval)")

        realtime_switch = Gtk.Switch()
        realtime_switch.set_active(self.realtime_updates_enabled)
        realtime_switch.connect("notify::active", self._on_realtime_updates_toggled)

        realtime_row.add_suffix(realtime_switch)
        refresh_group.add(realtime_row)

        return refresh_group

    def _on_refresh_system_info(self, button):
        """Handle refresh button click."""
        if SYSTEM_INFO_AVAILABLE:
            try:
                # Clear cache and collect fresh data
                from system_info import SystemInfoCollector
                collector = SystemInfoCollector(self.project_root)
                collector.clear_cache()

                # Show toast notification
                if hasattr(self.app, 'show_toast'):
                    self.app.show_toast("System information refreshed")

                # Log refresh action
                if hasattr(self.app, 'session_logger') and self.app.session_logger:
                    self.app.session_logger.log_gui_event("SYSTEM_INFO_REFRESH", "User refreshed system information")

                # Note: In a full implementation, we would refresh the tab content here
                # For now, the user needs to switch tabs to see updated information

            except Exception as e:
                # Show error toast
                if hasattr(self.app, 'show_toast'):
                    self.app.show_toast(f"Refresh failed: {str(e)}")

    def _on_auto_refresh_toggled(self, switch, param):
        """Handle auto-refresh toggle."""
        self.system_info_auto_refresh = switch.get_active()

        if self.system_info_auto_refresh:
            # Start auto-refresh
            if SYSTEM_INFO_AVAILABLE:
                self._auto_refresh_timer_id = GLib.timeout_add_seconds(
                    self.system_info_refresh_interval,
                    self._auto_refresh_callback
                )

                # Show toast notification
                if hasattr(self.app, 'show_toast'):
                    self.app.show_toast(f"Auto-refresh enabled ({self.system_info_refresh_interval}s interval)")

                # Log toggle action
                if hasattr(self.app, 'session_logger') and self.app.session_logger:
                    self.app.session_logger.log_gui_event("SYSTEM_INFO_AUTO_REFRESH_ENABLED",
                                                        f"Auto-refresh enabled with {self.system_info_refresh_interval}s interval")
        else:
            # Stop auto-refresh
            if self._auto_refresh_timer_id:
                GLib.source_remove(self._auto_refresh_timer_id)
                self._auto_refresh_timer_id = None

            # Show toast notification
            if hasattr(self.app, 'show_toast'):
                self.app.show_toast("Auto-refresh disabled")

            # Log toggle action
            if hasattr(self.app, 'session_logger') and self.app.session_logger:
                self.app.session_logger.log_gui_event("SYSTEM_INFO_AUTO_REFRESH_DISABLED", "Auto-refresh disabled")

    def _auto_refresh_callback(self):
        """Auto-refresh callback function."""
        if not self.system_info_auto_refresh:
            return False  # Stop the timer

        try:
            if SYSTEM_INFO_AVAILABLE:
                # Clear cache and collect fresh data
                from system_info import SystemInfoCollector
                collector = SystemInfoCollector(self.project_root)
                collector.clear_cache()

                # Log auto-refresh
                if hasattr(self.app, 'session_logger') and self.app.session_logger:
                    self.app.session_logger.log_gui_event("SYSTEM_INFO_AUTO_REFRESH", "Auto-refresh triggered")

        except Exception as e:
            # Log error but continue auto-refresh
            if hasattr(self.app, 'session_logger') and self.app.session_logger:
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
                    if hasattr(self.app, 'session_logger') and self.app.session_logger:
                        self.app.session_logger.log_gui_event("REALTIME_SETUP_FAILED", "Failed to start real-time updates")

        except Exception as e:
            if hasattr(self.app, 'session_logger') and self.app.session_logger:
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
                    if hasattr(self.app, 'show_toast'):
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
                if hasattr(self.app, 'show_toast'):
                    self.app.show_toast("Real-time updates disabled")

        # Log toggle action
        if hasattr(self.app, 'session_logger') and self.app.session_logger:
            self.app.session_logger.log_gui_event("REALTIME_TOGGLE",
                                                f"Real-time updates {'enabled' if self.realtime_updates_enabled else 'disabled'}")

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
                    from system_info import SystemInfoCollector
                    collector = SystemInfoCollector(self.project_root)
                    collector.clear_cache()

                # Log cleanup
                if hasattr(self.app, 'session_logger') and self.app.session_logger:
                    self.app.session_logger.log_gui_event("SYSTEM_INFO_CLEANUP", "System info components cleaned up")

            except Exception as e:
                if hasattr(self.app, 'session_logger') and self.app.session_logger:
                    self.app.session_logger.log_gui_event("SYSTEM_INFO_CLEANUP_ERROR", str(e))
