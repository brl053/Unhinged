"""
@llm-doc System Information View Orchestrator
@llm-version 1.0.0
@llm-date 2025-11-15

System Information tab view orchestrator that delegates to specialized section handlers.
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

    def start_realtime_updates(interval=2.0):
        return False

    def stop_realtime_updates():
        pass


# Import section handlers
from .system_view_cpu import CPUSectionHandler
from .system_view_storage import StorageSectionHandler
from .system_view_memory import MemorySectionHandler
from .system_view_motherboard import OverviewSectionHandler
from .system_view_platform import PlatformSectionHandler

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
        """Delegate to OverviewSectionHandler."""
        return OverviewSectionHandler.create_system_overview_section(system_info)

    def _create_performance_metrics_section(self, system_info):
        """Delegate to PlatformSectionHandler."""
        self._setup_realtime_updates()
        return PlatformSectionHandler.create_performance_metrics_section(system_info)

    def _create_hardware_info_section(self, system_info):
        """Delegate to OverviewSectionHandler."""
        return OverviewSectionHandler.create_hardware_info_section(system_info)

    def _create_motherboard_section(self, system_info):
        """Delegate to CPUSectionHandler."""
        return CPUSectionHandler.create_motherboard_section(system_info)

    def _create_cpu_details_section(self, system_info):
        """Delegate to CPUSectionHandler."""
        return CPUSectionHandler.create_cpu_details_section(system_info)

    def _create_gpu_details_section(self, system_info):
        """Delegate to StorageSectionHandler."""
        return StorageSectionHandler.create_gpu_details_section(system_info)

    def _create_storage_section(self, system_info):
        """Delegate to StorageSectionHandler."""
        return StorageSectionHandler.create_storage_section(system_info)

    def _create_memory_section(self, system_info):
        """Delegate to MemorySectionHandler."""
        return MemorySectionHandler.create_memory_section(system_info)

    def _create_network_section(self, system_info):
        """Delegate to MemorySectionHandler."""
        return MemorySectionHandler.create_network_section(system_info)

    def _create_platform_status_section(self, system_info):
        """Delegate to PlatformSectionHandler."""
        return PlatformSectionHandler.create_platform_status_section(system_info, self.project_root)

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
                    self.app.session_logger.log_gui_event("SYSTEM_INFO_REFRESH", "User refreshed system information")

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
                    self.app.show_toast(f"Auto-refresh enabled ({self.system_info_refresh_interval}s interval)")

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
                self.app.session_logger.log_gui_event("SYSTEM_INFO_AUTO_REFRESH_DISABLED", "Auto-refresh disabled")

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
                    self.app.session_logger.log_gui_event("SYSTEM_INFO_AUTO_REFRESH", "Auto-refresh triggered")

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
                if not success and hasattr(self.app, "session_logger") and self.app.session_logger:
                    # Failed to start real-time updates
                    self.app.session_logger.log_gui_event("REALTIME_SETUP_FAILED", "Failed to start real-time updates")

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
                    self.app.session_logger.log_gui_event("SYSTEM_INFO_CLEANUP", "System info components cleaned up")

            except Exception as e:
                if hasattr(self.app, "session_logger") and self.app.session_logger:
                    self.app.session_logger.log_gui_event("SYSTEM_INFO_CLEANUP_ERROR", str(e))
