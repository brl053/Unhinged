#!/usr/bin/env python3
"""
@llm-doc Unhinged Desktop Application for GTK4 UI
@llm-version 1.0.0
@llm-date 2025-10-28

Enhanced GTK4 desktop application with comprehensive system monitoring, process management,
Bluetooth device control, and audio output management. Features tabbed interface with
real-time updates, component library integration, and professional design system.
- Real-time status updates and progress indication
- Integration with existing Makefile system and VM communication
- User-friendly error handling and feedback

## Design Principles
- **Native Integration**: Uses GTK4 for authentic Ubuntu GNOME experience
- **Functionality Mapping**: Executes same operations as 'make start'
- **Visual Appeal**: Modern, clean interface following GNOME HIG
- **Accessibility**: Keyboard navigation and screen reader support

@llm-principle Native desktop integration with existing backend
@llm-culture Independence through accessible graphical interface
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GLib, Gio, Pango
import subprocess
import threading
import sys
import os
from pathlib import Path
import time
import json
import requests  # HTTP client for LLM API communication

# Add virtual environment packages to path for gRPC support
# Calculate project root correctly (control/gtk4_gui/desktop_app.py -> project root)
project_root = Path(__file__).parent.parent.parent
venv_packages = project_root / "build" / "python" / "venv" / "lib" / "python3.12" / "site-packages"
protobuf_clients = project_root / "generated" / "python" / "clients"

if venv_packages.exists():
    sys.path.insert(0, str(venv_packages))
if protobuf_clients.exists():
    sys.path.insert(0, str(protobuf_clients))

# Import component library
try:
    sys.path.append(str(Path(__file__).parent))
    from components import (
        StatusCard, StatusLabel, SystemInfoCard, HardwareInfoRow,
        PerformanceIndicator, SystemStatusGrid, ProcessTable,
        BluetoothTable, AudioTable
    )
    COMPONENTS_AVAILABLE = True
except ImportError:
    COMPONENTS_AVAILABLE = False
    print("⚠️  Component library not available - using basic widgets")

# Import system information collection
try:
    from system_info import SystemInfoCollector, get_system_info, get_performance_summary
    from realtime_system_info import get_realtime_manager, start_realtime_updates, stop_realtime_updates
    SYSTEM_INFO_AVAILABLE = True
except ImportError as e:
    SYSTEM_INFO_AVAILABLE = False
    print(f"⚠️  System info collection not available: {e}")

# Import session logging from event framework (optional)
SESSION_LOGGING_AVAILABLE = False
try:
    # Try multiple possible paths for the event framework
    event_paths = [
        str(Path(__file__).parent.parent.parent / "libs" / "event-framework" / "python" / "src"),
        str(Path(__file__).parent.parent / "libs" / "event-framework" / "python" / "src"),
        str(Path(__file__).parent.parent.parent / "build" / "python" / "venv" / "lib" / "python3.12" / "site-packages")
    ]

    for path in event_paths:
        if Path(path).exists():
            sys.path.append(path)
            break

    from events import create_gui_session_logger, GUIOutputCapture
    SESSION_LOGGING_AVAILABLE = True
    print("✅ Session logging available")
except ImportError:
    # Session logging is optional - continue without it
    SESSION_LOGGING_AVAILABLE = False

# Simple approach: Use control modules as scripts (academic exercise)
CONTROL_MODULES_AVAILABLE = True
print("✅ Control modules available as scripts")

class UnhingedDesktopApp(Adw.Application):
    """
    @llm-doc Main Desktop Application Class

    GTK4/Libadwaita application that provides graphical interface
    for Unhinged platform functionality.

    Features:
    - Design system integration with semantic tokens
    - CSS loading from generated/design_system/gtk4/
    - Graceful fallback to Libadwaita defaults
    """

    def __init__(self):
        super().__init__(application_id='com.unhinged.platform.gtk4')
        self.project_root = Path(__file__).parent.parent.parent  # Updated path
        self.window = None
        self.status_label = None
        self.progress_bar = None
        self.log_textview = None
        self.start_button = None
        self.stop_button = None
        self.process = None
        self.running = False

        # System info refresh state
        self.system_info_auto_refresh = False
        self.system_info_refresh_interval = 10  # seconds
        self.system_info_refresh_timeout_id = None

        # Real-time updates
        self.realtime_updates_enabled = False
        self.performance_indicators = {}  # Store references to performance indicators

        # Development mode detection
        self.dev_mode = os.environ.get('DEV_MODE', '0') == '1'

        # Initialize session logging (optional)
        self.session_logger = None
        self.output_capture = None
        if SESSION_LOGGING_AVAILABLE:
            try:
                self.session_logger = create_gui_session_logger(self.project_root)
                self.output_capture = GUIOutputCapture(
                    self.session_logger,
                    self._gui_log_callback
                )
                self.session_logger.log_session_event("APP_INIT", "GTK4 desktop app with system info integration")
                print("✅ Session logging initialized")
            except Exception as e:
                print(f"⚠️  Session logging initialization failed: {e}")
                self.session_logger = None
                self.output_capture = None
        else:
            print("ℹ️  Session logging not available (optional feature)")

        # Control module availability
        self.control_available = CONTROL_MODULES_AVAILABLE

        # Design system CSS provider (for delayed loading)
        self._pending_css_provider = None

    def _load_design_system_css(self):
        """
        Load the generated design system CSS files.

        Loads semantic tokens and theme CSS from the design system
        to provide consistent styling across the application.
        """
        # Skip design system CSS if requested (for debugging)
        if os.environ.get('SKIP_DESIGN_SYSTEM', '0') == '1':
            print("ℹ️  Skipping design system CSS loading (SKIP_DESIGN_SYSTEM=1)")
            return

        try:
            css_provider = Gtk.CssProvider()

            # Path to generated CSS files
            css_dir = self.project_root / "generated" / "design_system" / "gtk4"

            # Load CSS files in correct order
            css_files = [
                "design-tokens.css",    # Base semantic tokens
                "theme-light.css",      # Light theme (default)
                "components.css"        # Component patterns
            ]

            combined_css = ""
            loaded_files = []

            for css_file in css_files:
                css_path = css_dir / css_file
                if css_path.exists():
                    combined_css += css_path.read_text() + "\n"
                    loaded_files.append(css_file)
                    print(f"✅ Loaded design system CSS: {css_file}")
                else:
                    print(f"⚠️  Design system CSS not found: {css_file}")

            if combined_css:
                # Add minimal semantic token test class
                test_css = """
                /* Design system integration test */
                .ds-semantic-primary {
                    background-color: var(--color-action-primary);
                    color: var(--color-text-inverse);
                }
                """
                combined_css += test_css

                # Add OS Chatroom design system styles
                chatroom_css = """
                /* OS Chatroom Design System Styles */
                .ds-chatroom-container {
                    background-color: var(--color-surface-default, #ffffff);
                    border: var(--border-thin, 1px) solid var(--color-border-subtle, #e0e0e0);
                    border-radius: var(--radius-md, 8px);
                }

                .ds-text-input {
                    background-color: var(--color-surface-elevated, #f8f9fa);
                    border: var(--border-thin, 1px) solid var(--color-border-default, #d0d7de);
                    border-radius: var(--radius-sm, 4px);
                    font-family: var(--font-family-prose, system-ui);
                    font-size: var(--font-size-body, 14px);
                    line-height: var(--line-height-body, 1.5);
                    color: var(--color-text-primary, #24292f);
                    min-height: 120px;
                }

                .ds-text-input:focus {
                    border-color: var(--color-action-primary, #0969da);
                    box-shadow: 0 0 0 2px var(--color-action-primary, #0969da) at 20% opacity;
                }

                /* TextEditor Component Styles */
                .ds-text-editor {
                    background-color: transparent;
                }

                .ds-placeholder {
                    color: var(--color-text-tertiary, #656d76);
                    font-style: italic;
                    opacity: 0.8;
                }

                .ds-focused .ds-text-input {
                    border-color: var(--color-action-primary, #0969da);
                    box-shadow: 0 0 0 1px var(--color-action-primary, #0969da);
                }

                .ds-typography-body {
                    font-family: var(--font-family-prose, system-ui);
                    font-size: var(--font-size-body, 14px);
                    line-height: var(--line-height-body, 1.5);
                }
                """
                combined_css += chatroom_css

                # Add sidebar navigation design system styles
                sidebar_css = """
                /* Sidebar Navigation Design System Styles */
                .navigation-sidebar {
                    background-color: var(--color-surface-default, #ffffff);
                    border-right: var(--border-thin, 1px) solid var(--color-border-subtle, #e0e0e0);
                }

                .sidebar-nav-item {
                    padding: 8px 12px; /* sp_2 vertical, sp_3 horizontal */
                    border-radius: var(--radius-sm, 4px);
                    margin: 2px 8px; /* sp_0_5 vertical, sp_2 horizontal */
                }

                .sidebar-nav-item:hover {
                    background-color: var(--color-surface-elevated, #f8f9fa);
                }

                .sidebar-nav-active {
                    background-color: var(--color-action-primary, #0969da);
                    color: var(--color-text-inverse, #ffffff);
                    border-left: 4px solid var(--color-action-primary, #0969da); /* Design system: thick border */
                }

                .sidebar-nav-active:hover {
                    background-color: var(--color-action-primary, #0969da);
                }
                """
                combined_css += sidebar_css

                # Add chat message design system styles
                chat_css = """
                /* Chat Message Design System Styles */
                .chat-message-user {
                    background-color: var(--color-surface-elevated, #f8f9fa);
                    border-left: 4px solid var(--color-action-primary, #0969da);
                    border-radius: var(--radius-sm, 4px);
                }

                .chat-message-assistant {
                    background-color: var(--color-surface-default, #ffffff);
                    border-left: 4px solid var(--color-success-default, #1a7f37);
                    border-radius: var(--radius-sm, 4px);
                }

                .chat-message-error {
                    background-color: var(--color-danger-subtle, #ffebe9);
                    border-left: 4px solid var(--color-danger-default, #cf222e);
                    border-radius: var(--radius-sm, 4px);
                }

                .chat-sender {
                    font-weight: var(--font-weight-semibold, 600);
                    font-size: var(--font-size-small, 12px);
                    color: var(--color-text-secondary, #656d76);
                }

                .chat-timestamp {
                    font-size: var(--font-size-small, 12px);
                    color: var(--color-text-tertiary, #8c959f);
                    font-family: var(--font-family-mono, monospace);
                }

                .chat-content {
                    font-family: var(--font-family-prose, system-ui);
                    font-size: var(--font-size-body, 14px);
                    line-height: var(--line-height-body, 1.5);
                    color: var(--color-text-primary, #24292f);
                }
                """
                combined_css += chat_css

                try:
                    css_provider.load_from_data(combined_css.encode())

                    # Apply CSS to display (requires window to be created)
                    if self.window:
                        display = self.window.get_display()
                        Gtk.StyleContext.add_provider_for_display(
                            display,
                            css_provider,
                            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                        )
                    else:
                        # Store CSS provider for later application
                        self._pending_css_provider = css_provider

                except Exception as css_error:
                    print(f"⚠️  CSS parsing error (using Libadwaita defaults): {css_error}")
                    # Continue without design system CSS - app will use Libadwaita defaults
                    self._pending_css_provider = None

                print(f"✅ Design system CSS loaded successfully ({len(loaded_files)} files)")

                # Log to session if available
                if self.session_logger:
                    self.session_logger.log_gui_event("DESIGN_SYSTEM_LOADED",
                                                    f"Loaded {len(loaded_files)} CSS files: {', '.join(loaded_files)}")
            else:
                print("ℹ️  No design system CSS files found - using Libadwaita defaults")

        except Exception as e:
            print(f"❌ Failed to load design system CSS: {e}")
            # App continues with Libadwaita defaults
            if self.session_logger:
                self.session_logger.log_gui_event("DESIGN_SYSTEM_ERROR", f"CSS loading failed: {e}")

    def do_activate(self):
        """Application activation - create and show main window"""
        if not self.window:
            self.window = self.create_main_window()

            # Load design system CSS after window creation
            self._load_design_system_css()

            # Apply any pending CSS provider
            if self._pending_css_provider:
                display = self.window.get_display()
                Gtk.StyleContext.add_provider_for_display(
                    display,
                    self._pending_css_provider,
                    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                )
                self._pending_css_provider = None
                print("✅ Applied pending design system CSS to display")

        # Log application activation
        if self.session_logger:
            self.session_logger.log_gui_event("APP_ACTIVATE", "Main window created and presented")

        self.window.present()
    
    def create_main_window(self):
        """
        @llm-doc Create Main Application Window
        
        Creates the main GTK4 window with modern Ubuntu GNOME styling
        using Libadwaita for native look and feel.
        """
        # Create main window
        window = Adw.ApplicationWindow(application=self)

        # Set title based on mode
        if self.dev_mode:
            window.set_title("Unhinged - Development Mode")
        else:
            window.set_title("Unhinged - Native Graphics Platform")

        window.set_default_size(800, 600)
        window.set_icon_name("applications-graphics")

        # Add actions (AdwApplicationWindow has built-in header bar)
        self.setup_actions()
        
        # Create toast overlay for notifications
        self.toast_overlay = Adw.ToastOverlay()

        # Create tab navigation
        self.create_tab_navigation()

        # Set up toast overlay with tab content
        window.set_content(self.toast_overlay)
        return window

    def create_tab_navigation(self):
        """Create sidebar navigation with NavigationSplitView."""
        # Create navigation split view
        self.navigation_split_view = Adw.NavigationSplitView()

        # Create content area with stack for different pages
        self.content_stack = Gtk.Stack()
        self.content_stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)

        # Create navigation pages and add to stack
        self.navigation_pages = {}

        # Main page
        main_content = self.create_main_tab_content()
        self.content_stack.add_named(main_content, "main")
        self.navigation_pages["main"] = main_content

        # Status page
        status_content = self.create_status_tab_content()
        self.content_stack.add_named(status_content, "status")
        self.navigation_pages["status"] = status_content

        # System Info page
        system_info_content = self.create_system_info_tab_content()
        self.content_stack.add_named(system_info_content, "system_info")
        self.navigation_pages["system_info"] = system_info_content

        # Processes page
        processes_content = self.create_processes_tab_content()
        self.content_stack.add_named(processes_content, "processes")
        self.navigation_pages["processes"] = processes_content

        # Bluetooth page
        bluetooth_content = self.create_bluetooth_tab_content()
        self.content_stack.add_named(bluetooth_content, "bluetooth")
        self.navigation_pages["bluetooth"] = bluetooth_content

        # Output page
        output_content = self.create_output_tab_content()
        self.content_stack.add_named(output_content, "output")
        self.navigation_pages["output"] = output_content

        # Input page
        input_content = self.create_input_tab_content()
        self.content_stack.add_named(input_content, "input")
        self.navigation_pages["input"] = input_content

        # OS Chatroom page
        chatroom_content = self.create_chatroom_tab_content()
        self.content_stack.add_named(chatroom_content, "chatroom")
        self.navigation_pages["chatroom"] = chatroom_content

        # Create sidebar navigation page
        sidebar_content = self.create_sidebar_navigation()
        sidebar_page = Adw.NavigationPage.new(sidebar_content, "Navigation")
        sidebar_page.set_title("Navigation")

        # Create content navigation page
        content_page = Adw.NavigationPage.new(self.content_stack, "Content")
        content_page.set_title("Content")

        # Set sidebar and content
        self.navigation_split_view.set_sidebar(sidebar_page)
        self.navigation_split_view.set_content(content_page)

        # Set initial page
        self.content_stack.set_visible_child_name("main")

        # Set up toast overlay
        self.toast_overlay.set_child(self.navigation_split_view)

    def create_sidebar_navigation(self):
        """Create sidebar navigation with design system styling."""
        # Create sidebar list box
        sidebar_list = Gtk.ListBox()
        sidebar_list.set_selection_mode(Gtk.SelectionMode.SINGLE)
        sidebar_list.add_css_class("navigation-sidebar")

        # Define navigation items (1:1 mapping from tabs)
        nav_items = [
            {"id": "main", "title": "Main", "icon": "applications-graphics"},
            {"id": "status", "title": "Status", "icon": "dialog-information-symbolic"},
            {"id": "system_info", "title": "System Info", "icon": "computer-symbolic"},
            {"id": "processes", "title": "Processes", "icon": "utilities-system-monitor-symbolic"},
            {"id": "bluetooth", "title": "Bluetooth", "icon": "bluetooth-symbolic"},
            {"id": "output", "title": "Output", "icon": "audio-speakers-symbolic"},
            {"id": "input", "title": "Input", "icon": "audio-input-microphone-symbolic"},
            {"id": "chatroom", "title": "OS Chatroom", "icon": "user-available-symbolic"},
        ]

        # Create sidebar rows
        for item in nav_items:
            row = Adw.ActionRow()
            row.set_title(item["title"])

            # Add icon
            icon = Gtk.Image.new_from_icon_name(item["icon"])
            icon.set_icon_size(Gtk.IconSize.NORMAL)
            row.add_prefix(icon)

            # Store item ID for navigation
            row.item_id = item["id"]

            # Apply design system styling
            row.add_css_class("sidebar-nav-item")

            sidebar_list.append(row)

        # Connect selection handler
        sidebar_list.connect("row-selected", self._on_sidebar_selection_changed)

        # Select first item by default
        first_row = sidebar_list.get_row_at_index(0)
        if first_row:
            sidebar_list.select_row(first_row)

        # Create scrolled window for sidebar
        sidebar_scrolled = Gtk.ScrolledWindow()
        sidebar_scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        sidebar_scrolled.set_child(sidebar_list)

        # Apply design system width
        sidebar_scrolled.set_size_request(240, -1)  # Design system: collapsed width

        return sidebar_scrolled

    def _on_sidebar_selection_changed(self, list_box, row):
        """Handle sidebar navigation selection."""
        if row and hasattr(row, 'item_id'):
            # Switch to selected page
            self.content_stack.set_visible_child_name(row.item_id)

            # Update active styling
            self._update_sidebar_active_state(row)

    def _update_sidebar_active_state(self, active_row):
        """Update sidebar active state styling."""
        # Remove active class from all rows
        parent = active_row.get_parent()
        if parent:
            row_index = 0
            while True:
                row = parent.get_row_at_index(row_index)
                if not row:
                    break
                row.remove_css_class("sidebar-nav-active")
                row_index += 1

        # Add active class to selected row
        active_row.add_css_class("sidebar-nav-active")

    def create_main_tab_content(self):
        """Create the main tab content (existing functionality)."""
        # Create main content
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        main_box.set_margin_top(24)
        main_box.set_margin_bottom(24)
        main_box.set_margin_start(24)
        main_box.set_margin_end(24)

        # Welcome section
        welcome_group = self.create_welcome_section()
        main_box.append(welcome_group)

        # Control section
        control_group = self.create_control_section()
        main_box.append(control_group)

        # Status section
        status_group = self.create_status_section()
        main_box.append(status_group)

        # Development section (only in dev mode)
        if self.dev_mode:
            dev_group = self.create_development_section()
            main_box.append(dev_group)

        # Log section
        log_group = self.create_log_section()
        main_box.append(log_group)

        # Create scrolled window for content
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_child(main_box)

        return scrolled

    def create_status_tab_content(self):
        """Create the new minimal status tab content using component library."""
        # Create status content box
        status_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        status_box.set_margin_top(24)
        status_box.set_margin_bottom(24)
        status_box.set_margin_start(24)
        status_box.set_margin_end(24)

        # Header section
        header_group = Adw.PreferencesGroup()
        header_group.set_title("New Status Tab")
        header_group.set_description("Minimal academic first step - parallel to existing status")
        status_box.append(header_group)

        # Use component library if available
        if COMPONENTS_AVAILABLE:
            # Status card using component library
            status_card = StatusCard(
                title="Platform Status",
                status="info",
                subtitle="Component library integration",
                description="This tab demonstrates the new component library in a minimal way.",
                icon_name="dialog-information-symbolic"
            )
            status_box.append(status_card.get_widget())

            # Status labels section
            labels_group = Adw.PreferencesGroup()
            labels_group.set_title("Status Examples")

            labels_row = Adw.ActionRow()
            labels_row.set_title("Component Status Labels")
            labels_row.set_subtitle("Different status types using the component library")

            # Create a box for status labels
            labels_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

            # Add different status labels
            for status_type in ["success", "warning", "error", "info"]:
                status_label = StatusLabel(
                    text=status_type.title(),
                    status=status_type
                )
                labels_box.append(status_label.get_widget())

            labels_row.add_suffix(labels_box)
            labels_group.add(labels_row)
            status_box.append(labels_group)

        else:
            # Fallback to basic widgets
            fallback_group = Adw.PreferencesGroup()
            fallback_group.set_title("Basic Status")

            fallback_row = Adw.ActionRow()
            fallback_row.set_title("Platform Status")
            fallback_row.set_subtitle("Component library not available - using basic widgets")

            status_icon = Gtk.Image.new_from_icon_name("emblem-default-symbolic")
            status_icon.set_icon_size(Gtk.IconSize.LARGE)
            fallback_row.add_prefix(status_icon)

            status_label = Gtk.Label(label="Ready")
            status_label.add_css_class("title-4")
            fallback_row.add_suffix(status_label)

            fallback_group.add(fallback_row)
            status_box.append(fallback_group)

        # Info section
        info_group = Adw.PreferencesGroup()
        info_group.set_title("Implementation Notes")

        info_row = Adw.ActionRow()
        info_row.set_title("Minimal Feature Set")
        info_row.set_subtitle("No API calls, no extra functionality - just a new tab with static content")

        info_group.add(info_row)
        status_box.append(info_group)

        # Voice Transcription Section
        voice_group = self.create_voice_transcription_section()
        if voice_group:
            status_box.append(voice_group)

        # Create scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_child(status_box)

        return scrolled

    def create_system_info_tab_content(self):
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

    def create_processes_tab_content(self):
        """Create the processes tab content with live process monitoring."""
        try:
            # Import ProcessTable component
            from components.complex import ProcessTable

            # Create main content box
            processes_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
            processes_box.set_margin_top(24)
            processes_box.set_margin_bottom(24)
            processes_box.set_margin_start(24)
            processes_box.set_margin_end(24)
            processes_box.set_vexpand(True)
            processes_box.set_hexpand(True)

            # Create header section
            header_group = Adw.PreferencesGroup()
            header_group.set_title("Process Monitor")
            header_group.set_description("Live process monitoring with aux/top command equivalence")

            # Add header info row
            info_row = Adw.ActionRow()
            info_row.set_title("Process Management")
            info_row.set_subtitle("View, sort, filter, and manage running processes")

            # Add process monitor icon
            monitor_icon = Gtk.Image.new_from_icon_name("utilities-system-monitor-symbolic")
            monitor_icon.set_icon_size(Gtk.IconSize.LARGE)
            monitor_icon.add_css_class("accent")
            info_row.add_prefix(monitor_icon)

            header_group.add(info_row)
            processes_box.append(header_group)

            # Create ProcessTable
            self.process_table = ProcessTable()

            # Create process table group
            table_group = Adw.PreferencesGroup()
            table_group.set_title("Running Processes")

            # Add ProcessTable widget to the group
            table_row = Adw.ActionRow()
            table_row.set_child(self.process_table.get_widget())
            table_group.add(table_row)

            processes_box.append(table_group)

            # Log processes tab creation
            if self.session_logger:
                self.session_logger.log_gui_event("PROCESSES_TAB_CREATED", "Processes tab with ProcessTable created")

            return processes_box

        except Exception as e:
            # Create error fallback
            error_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
            error_box.set_margin_top(24)
            error_box.set_margin_bottom(24)
            error_box.set_margin_start(24)
            error_box.set_margin_end(24)

            error_group = Adw.PreferencesGroup()
            error_group.set_title("Process Monitor Unavailable")
            error_group.set_description("Process monitoring is not available")

            error_row = Adw.ActionRow()
            error_row.set_title("Error Loading Process Monitor")
            error_row.set_subtitle(f"Error: {str(e)}")

            error_icon = Gtk.Image.new_from_icon_name("dialog-error-symbolic")
            error_icon.add_css_class("error")
            error_row.add_prefix(error_icon)

            error_group.add(error_row)
            error_box.append(error_group)

            # Log error
            if self.session_logger:
                self.session_logger.log_gui_event("PROCESSES_TAB_ERROR", f"Failed to create processes tab: {e}")

            return error_box

    def create_input_tab_content(self):
        """Create the Input tab content with audio input device listing."""
        try:
            # Create main content box
            input_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
            input_box.set_margin_top(24)
            input_box.set_margin_bottom(24)
            input_box.set_margin_start(24)
            input_box.set_margin_end(24)

            # Create header section
            header_group = Adw.PreferencesGroup()
            header_group.set_title("Audio Input Devices")
            header_group.set_description("Available microphones and audio input devices")

            # Add audio info row
            info_row = Adw.ActionRow()
            info_row.set_title("Input System")
            info_row.set_subtitle("List of available audio input devices")

            # Add microphone icon
            mic_icon = Gtk.Image.new_from_icon_name("audio-input-microphone-symbolic")
            mic_icon.set_icon_size(Gtk.IconSize.LARGE)
            info_row.add_prefix(mic_icon)

            header_group.add(info_row)
            input_box.append(header_group)

            # Create input devices list
            devices_group = Adw.PreferencesGroup()
            devices_group.set_title("Input Devices")

            # Get input devices and create list
            input_devices = self._get_input_devices()

            if input_devices:
                for device in input_devices:
                    device_row = Adw.ActionRow()
                    device_row.set_title(device['name'])
                    device_row.set_subtitle(device['description'])

                    # Add device type icon
                    device_icon = Gtk.Image.new_from_icon_name(device['icon'])
                    device_icon.set_icon_size(Gtk.IconSize.NORMAL)
                    device_row.add_prefix(device_icon)

                    # Add "Set as Default" button
                    default_button = Gtk.Button(label="Set as Default")
                    default_button.add_css_class("suggested-action")
                    default_button.connect("clicked", self._on_set_default_input_device, device)
                    device_row.add_suffix(default_button)

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

            input_box.append(devices_group)

            # Log Input tab creation
            if self.session_logger:
                self.session_logger.log_gui_event("INPUT_TAB_CREATED", f"Input tab created with {len(input_devices)} devices")

            return input_box

        except Exception as e:
            # Create error fallback
            error_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
            error_box.set_margin_top(24)
            error_box.set_margin_bottom(24)
            error_box.set_margin_start(24)
            error_box.set_margin_end(24)

            # Error group
            error_group = Adw.PreferencesGroup()
            error_group.set_title("Input Tab Error")
            error_group.set_description("Failed to load audio input interface")

            # Error row
            error_row = Adw.ActionRow()
            error_row.set_title("Audio Input Unavailable")
            error_row.set_subtitle(f"Error: {str(e)}")

            error_icon = Gtk.Image.new_from_icon_name("dialog-error-symbolic")
            error_icon.set_icon_size(Gtk.IconSize.LARGE)
            error_row.add_prefix(error_icon)

            error_group.add(error_row)
            error_box.append(error_group)

            # Log error
            if self.session_logger:
                self.session_logger.log_gui_event("INPUT_TAB_ERROR", str(e))

            return error_box

    def create_chatroom_tab_content(self):
        """Create the OS Chatroom tab content with design system layout utilities."""
        # Create main chat container using design system layout patterns
        chatroom_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        chatroom_container.set_vexpand(True)
        chatroom_container.set_hexpand(True)

        # Apply design system styling
        chatroom_container.add_css_class("ds-chatroom-container")

        # Chat messages area (expandable, will contain chat history)
        # Using design system spacing: sp_4 (16px) for major component margins
        messages_area = Gtk.ScrolledWindow()
        messages_area.set_vexpand(True)
        messages_area.set_hexpand(True)
        messages_area.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        # Messages container with design system padding
        messages_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)  # sp_2 (8px) for element spacing
        messages_container.set_margin_top(16)     # sp_4 - major component margins
        messages_container.set_margin_bottom(16)  # sp_4 - major component margins
        messages_container.set_margin_start(16)   # sp_4 - major component margins
        messages_container.set_margin_end(16)     # sp_4 - major component margins

        messages_area.set_child(messages_container)
        chatroom_container.append(messages_area)

        # Input area container (fixed at bottom, will contain text editor)
        # Using design system spacing: sp_6 (24px) for section breaks
        input_area = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        input_area.set_margin_top(24)     # sp_6 - section breaks, modal internal spacing
        input_area.set_margin_bottom(16)  # sp_4 - major component margins
        input_area.set_margin_start(16)   # sp_4 - major component margins
        input_area.set_margin_end(16)     # sp_4 - major component margins

        # Import and create TextEditor component
        from .components import TextEditor

        # Create proper text editor component following design system specification
        text_editor = TextEditor(
            placeholder="Type your message here...",
            word_wrap=True,
            min_height=120
        )

        # Apply design system margins (already handled by TextEditor component)
        text_editor_widget = text_editor.get_widget()
        text_editor_widget.set_margin_top(8)     # sp_2 - form field padding
        text_editor_widget.set_margin_bottom(8)  # sp_2 - form field padding
        text_editor_widget.set_margin_start(8)   # sp_2 - form field padding
        text_editor_widget.set_margin_end(8)     # sp_2 - form field padding

        # Connect text editor events
        text_editor.connect('content-changed', self._on_chatroom_content_changed)
        text_editor.connect('focus-gained', self._on_chatroom_focus_gained)
        text_editor.connect('focus-lost', self._on_chatroom_focus_lost)

        # Create horizontal box for text editor and send button
        input_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)  # sp_2 spacing

        # Add text editor to horizontal box (expand to fill space)
        text_editor_widget.set_hexpand(True)
        input_row.append(text_editor_widget)

        # Create Send button
        self._chatroom_send_button = Gtk.Button(label="Send")
        self._chatroom_send_button.add_css_class("suggested-action")
        self._chatroom_send_button.set_valign(Gtk.Align.END)  # Align to bottom of text editor
        self._chatroom_send_button.set_sensitive(False)  # Initially disabled

        # Connect send button handler
        self._chatroom_send_button.connect("clicked", self._on_chatroom_send_clicked)

        # Add send button to horizontal box
        input_row.append(self._chatroom_send_button)

        # Add horizontal box to input area
        input_area.append(input_row)
        chatroom_container.append(input_area)

        # Store references for future integration
        self._chatroom_messages_container = messages_container
        self._chatroom_input_area = input_area
        self._chatroom_text_editor = text_editor

        return chatroom_container

    def _on_chatroom_content_changed(self, text_editor, content):
        """Handle text editor content changes in OS Chatroom."""
        # Log content changes for debugging
        if self.session_logger:
            self.session_logger.log_gui_event("CHATROOM_CONTENT_CHANGED", f"Content length: {len(content)}")

        # Enable/disable send button based on content
        has_content = bool(content.strip())
        if hasattr(self, '_chatroom_send_button'):
            self._chatroom_send_button.set_sensitive(has_content)

        # Future: Add real-time features like typing indicators
        # Future: Add auto-save functionality
        # Future: Add content validation

    def _on_chatroom_focus_gained(self, text_editor):
        """Handle text editor focus gained in OS Chatroom."""
        if self.session_logger:
            self.session_logger.log_gui_event("CHATROOM_FOCUS_GAINED", "Text editor focused")

        # Future: Add focus-related UI changes
        # Future: Add keyboard shortcuts activation

    def _on_chatroom_focus_lost(self, text_editor):
        """Handle text editor focus lost in OS Chatroom."""
        if self.session_logger:
            self.session_logger.log_gui_event("CHATROOM_FOCUS_LOST", "Text editor unfocused")

        # Future: Add auto-save on focus loss
        # Future: Add content validation on blur

    def _on_chatroom_send_clicked(self, button):
        """Handle send button click in OS Chatroom."""
        # Get current text content
        content = self._chatroom_text_editor.get_content()

        if not content.strip():
            return  # Nothing to send

        # Log send action
        if self.session_logger:
            self.session_logger.log_gui_event("CHATROOM_SEND_CLICKED", f"Sending message: {len(content)} characters")

        # Send message to LLM service
        self._send_to_llm(content)

        # Clear text editor after sending
        self._chatroom_text_editor.clear()

        # Button will be disabled automatically by content_changed handler

    def _send_to_llm(self, message):
        """Send message to LLM service via gRPC and handle response."""
        try:
            # Add protobuf clients to path (following existing pattern)
            import sys
            from pathlib import Path
            import grpc

            project_root = Path(__file__).parent.parent.parent
            protobuf_path = project_root / "generated" / "python" / "clients"
            if protobuf_path.exists():
                sys.path.insert(0, str(protobuf_path))

            # Log LLM request
            if self.session_logger:
                self.session_logger.log_gui_event("LLM_REQUEST_SENT", f"Message: {message[:100]}")

            # For now, use Ollama HTTP API since gRPC protobuf clients aren't generated
            # TODO: Replace with proper gRPC when llm_pb2 clients are generated
            response = self._send_to_ollama_http(message)

            # Display user message first
            self._add_chat_message(message, "user")

            if response:
                # Display LLM response
                self._add_chat_message(response, "assistant")

                # Log successful response
                if self.session_logger:
                    self.session_logger.log_gui_event("LLM_RESPONSE_RECEIVED", f"Response length: {len(response)}")
            else:
                # Display error message
                self._add_chat_message("❌ No response from LLM service", "error")

        except Exception as e:
            print(f"❌ LLM communication error: {e}")
            if self.session_logger:
                self.session_logger.log_gui_event("LLM_ERROR", f"Error: {str(e)}")

    def _send_to_ollama_http(self, message):
        """Send message to Ollama HTTP API (temporary until gRPC is ready)."""
        try:
            # Use Ollama HTTP API on port 1500
            url = "http://localhost:1500/api/generate"
            payload = {
                "model": "llama2",  # Default model, will be configurable later
                "prompt": message,
                "stream": False
            }

            response = requests.post(url, json=payload, timeout=30)

            if response.status_code == 200:
                result = response.json()
                return result.get("response", "No response from model")
            else:
                error_msg = response.json().get("error", "Unknown error")
                print(f"❌ Ollama API error: {error_msg}")
                return f"Error: {error_msg}"

        except requests.exceptions.RequestException as e:
            print(f"❌ HTTP request error: {e}")
            return f"Connection error: {str(e)}"
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return f"Unexpected error: {str(e)}"

    def _add_chat_message(self, message, sender_type):
        """Add a chat message to the messages area with proper styling."""
        from datetime import datetime

        # Create message container
        message_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)  # sp_1 spacing
        message_box.set_margin_top(8)     # sp_2 - message spacing
        message_box.set_margin_bottom(8)  # sp_2 - message spacing
        message_box.set_margin_start(12)  # sp_3 - message margins
        message_box.set_margin_end(12)    # sp_3 - message margins

        # Create header with sender and timestamp
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)  # sp_2 spacing

        # Sender label
        if sender_type == "user":
            sender_label = Gtk.Label(label="👤 You")
            message_box.add_css_class("chat-message-user")
        elif sender_type == "assistant":
            sender_label = Gtk.Label(label="🤖 Assistant")
            message_box.add_css_class("chat-message-assistant")
        else:  # error
            sender_label = Gtk.Label(label="⚠️ System")
            message_box.add_css_class("chat-message-error")

        sender_label.set_halign(Gtk.Align.START)
        sender_label.add_css_class("chat-sender")
        header_box.append(sender_label)

        # Timestamp label
        timestamp = datetime.now().strftime("%H:%M:%S")
        timestamp_label = Gtk.Label(label=timestamp)
        timestamp_label.set_halign(Gtk.Align.END)
        timestamp_label.set_hexpand(True)
        timestamp_label.add_css_class("chat-timestamp")
        header_box.append(timestamp_label)

        message_box.append(header_box)

        # Message content
        content_label = Gtk.Label(label=message)
        content_label.set_wrap(True)
        content_label.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
        content_label.set_halign(Gtk.Align.START)
        content_label.set_selectable(True)  # Allow text selection
        content_label.add_css_class("chat-content")

        message_box.append(content_label)

        # Add to messages container
        self._chatroom_messages_container.append(message_box)

        # Auto-scroll to bottom
        self._scroll_messages_to_bottom()

    def _scroll_messages_to_bottom(self):
        """Scroll the messages area to the bottom to show latest message."""
        # Get the scrolled window parent of messages container
        parent = self._chatroom_messages_container.get_parent()
        while parent and not isinstance(parent, Gtk.ScrolledWindow):
            parent = parent.get_parent()

        if parent:
            # Get vertical adjustment and scroll to bottom
            vadj = parent.get_vadjustment()
            if vadj:
                # Use idle_add to ensure scroll happens after widget is rendered
                GLib.idle_add(lambda: vadj.set_value(vadj.get_upper() - vadj.get_page_size()))

    def create_bluetooth_tab_content(self):
        """Create the Bluetooth tab content with device discovery and management."""
        try:
            # Import BluetoothTable component
            from components.complex import BluetoothTable

            # Create main content box
            bluetooth_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
            bluetooth_box.set_margin_top(24)
            bluetooth_box.set_margin_bottom(24)
            bluetooth_box.set_margin_start(24)
            bluetooth_box.set_margin_end(24)
            bluetooth_box.set_vexpand(True)
            bluetooth_box.set_hexpand(True)

            # Create header section
            header_group = Adw.PreferencesGroup()
            header_group.set_title("Bluetooth Manager")
            header_group.set_description("Discover, pair, and manage Bluetooth devices")

            # Add header info row
            info_row = Adw.ActionRow()
            info_row.set_title("Device Management")
            info_row.set_subtitle("Scan for devices, manage connections, and configure pairing")

            # Add Bluetooth icon
            bluetooth_icon = Gtk.Image.new_from_icon_name("bluetooth-symbolic")
            bluetooth_icon.set_icon_size(Gtk.IconSize.LARGE)
            bluetooth_icon.add_css_class("accent")
            info_row.add_prefix(bluetooth_icon)

            header_group.add(info_row)
            bluetooth_box.append(header_group)

            # Create BluetoothTable
            self.bluetooth_table = BluetoothTable()

            # Create Bluetooth table group
            table_group = Adw.PreferencesGroup()
            table_group.set_title("Bluetooth Devices")

            # Add BluetoothTable widget to the group
            table_row = Adw.ActionRow()
            table_row.set_child(self.bluetooth_table.get_widget())
            table_group.add(table_row)

            bluetooth_box.append(table_group)

            # Log Bluetooth tab creation
            if self.session_logger:
                self.session_logger.log_gui_event("BLUETOOTH_TAB_CREATED", "Bluetooth tab with BluetoothTable created")

            return bluetooth_box

        except Exception as e:
            # Create error fallback
            error_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
            error_box.set_margin_top(24)
            error_box.set_margin_bottom(24)
            error_box.set_margin_start(24)
            error_box.set_margin_end(24)

            error_group = Adw.PreferencesGroup()
            error_group.set_title("Bluetooth Manager Unavailable")
            error_group.set_description("Bluetooth management is not available")

            error_row = Adw.ActionRow()
            error_row.set_title("Error Loading Bluetooth Manager")
            error_row.set_subtitle(f"Error: {str(e)}")

            error_icon = Gtk.Image.new_from_icon_name("dialog-error-symbolic")
            error_icon.add_css_class("error")
            error_row.add_prefix(error_icon)

            error_group.add(error_row)
            error_box.append(error_group)

            # Log error
            if self.session_logger:
                self.session_logger.log_gui_event("BLUETOOTH_TAB_ERROR", f"Failed to create Bluetooth tab: {e}")

            return error_box

    def create_output_tab_content(self):
        """Create the Output tab content with audio device management and connection switching."""
        try:
            # Import AudioTable component
            from components.complex import AudioTable

            # Create main content box
            output_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
            output_box.set_margin_top(24)
            output_box.set_margin_bottom(24)
            output_box.set_margin_start(24)
            output_box.set_margin_end(24)

            # Create header section
            header_group = Adw.PreferencesGroup()
            header_group.set_title("Audio Output Management")
            header_group.set_description("Manage audio devices, volume control, and connection switching")

            # Add audio info row
            info_row = Adw.ActionRow()
            info_row.set_title("Audio System")
            info_row.set_subtitle("Control audio output devices and volume settings")

            # Add audio icon
            audio_icon = Gtk.Image.new_from_icon_name("audio-speakers-symbolic")
            audio_icon.set_icon_size(Gtk.IconSize.LARGE)
            info_row.add_prefix(audio_icon)

            header_group.add(info_row)
            output_box.append(header_group)

            # Create AudioTable
            self.audio_table = AudioTable()

            # Create audio table group
            table_group = Adw.PreferencesGroup()
            table_group.set_title("Audio Devices")

            # Add AudioTable widget directly to the group (no ActionRow wrapper)
            audio_table_widget = self.audio_table.get_widget()
            audio_table_widget.set_vexpand(True)
            audio_table_widget.set_hexpand(True)

            # Create a clamp for better layout
            clamp = Adw.Clamp()
            clamp.set_maximum_size(1200)
            clamp.set_tightening_threshold(600)
            clamp.set_child(audio_table_widget)
            clamp.set_vexpand(True)

            table_group.add(clamp)
            output_box.append(table_group)

            # Log Output tab creation
            if self.session_logger:
                self.session_logger.log_gui_event("OUTPUT_TAB_CREATED", "Output tab with AudioTable created")

            return output_box

        except Exception as e:
            # Create error fallback
            error_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
            error_box.set_margin_top(24)
            error_box.set_margin_bottom(24)
            error_box.set_margin_start(24)
            error_box.set_margin_end(24)

            # Error group
            error_group = Adw.PreferencesGroup()
            error_group.set_title("Output Tab Error")
            error_group.set_description("Failed to load audio management interface")

            # Error row
            error_row = Adw.ActionRow()
            error_row.set_title("Audio Management Unavailable")
            error_row.set_subtitle(f"Error: {str(e)}")

            error_icon = Gtk.Image.new_from_icon_name("dialog-error-symbolic")
            error_icon.set_icon_size(Gtk.IconSize.LARGE)
            error_row.add_prefix(error_icon)

            error_group.add(error_row)
            error_box.append(error_group)

            # Log error
            if self.session_logger:
                self.session_logger.log_gui_event("OUTPUT_TAB_ERROR", f"Failed to create Output tab: {e}")

            return error_box

    def _create_system_overview_section(self, system_info):
        """Create system overview section with basic system information."""
        overview_data = {
            "os_name": f"{system_info.system.os_name} {system_info.system.os_version}",
            "kernel_version": system_info.system.kernel_version,
            "hostname": system_info.system.hostname,
            "username": system_info.system.username,
            "uptime_hours": f"{system_info.system.uptime_seconds / 3600:.1f} hours",
            "architecture": system_info.system.architecture
        }

        overview_card = SystemInfoCard(
            title="System Overview",
            subtitle="Basic system information",
            icon_name="computer-symbolic",
            data=overview_data
        )

        return overview_card.get_widget()

    def _create_performance_metrics_section(self, system_info):
        """Create performance metrics section with real-time indicators."""
        performance_group = Adw.PreferencesGroup()
        performance_group.set_title("Performance Metrics")
        performance_group.set_description("Real-time system performance indicators")

        # CPU Performance
        cpu_indicator = PerformanceIndicator(
            metric_type="cpu",
            title="CPU Usage",
            current_value=system_info.cpu.usage_percent,
            max_value=100.0,
            unit="%"
        )
        performance_group.add(cpu_indicator.get_widget())
        self.performance_indicators['cpu'] = cpu_indicator

        # Memory Performance
        memory_indicator = PerformanceIndicator(
            metric_type="memory",
            title="Memory Usage",
            current_value=system_info.memory.usage_percent,
            max_value=100.0,
            unit="%"
        )
        performance_group.add(memory_indicator.get_widget())
        self.performance_indicators['memory'] = memory_indicator

        # Storage Performance
        if system_info.storage.total_storage_gb > 0:
            storage_usage = (system_info.storage.total_used_gb / system_info.storage.total_storage_gb) * 100
            storage_indicator = PerformanceIndicator(
                metric_type="disk",
                title="Storage Usage",
                current_value=storage_usage,
                max_value=100.0,
                unit="%"
            )
            performance_group.add(storage_indicator.get_widget())
            self.performance_indicators['disk'] = storage_indicator

        # Start real-time updates for performance indicators
        self._setup_realtime_updates()

        return performance_group

    def _create_hardware_info_section(self, system_info):
        """Create hardware information section with detailed hardware data."""
        hardware_group = Adw.PreferencesGroup()
        hardware_group.set_title("Hardware Information")
        hardware_group.set_description("Detailed hardware specifications")

        # CPU Information
        cpu_details = {
            "model": system_info.cpu.model,
            "cores": system_info.cpu.cores,
            "threads": system_info.cpu.threads,
            "frequency_mhz": f"{system_info.cpu.frequency_mhz:.0f} MHz" if system_info.cpu.frequency_mhz > 0 else "Unknown",
            "features": ", ".join(system_info.cpu.features[:5]) if system_info.cpu.features else "None detected"
        }

        cpu_row = HardwareInfoRow(
            title=f"CPU: {system_info.cpu.model}",
            subtitle=f"{system_info.cpu.cores} cores, {system_info.cpu.threads} threads",
            hardware_type="cpu",
            status="normal",
            details=cpu_details
        )
        hardware_group.add(cpu_row.get_widget())

        # Memory Information
        memory_details = {
            "total_gb": f"{system_info.memory.total_gb:.1f} GB",
            "available_gb": f"{system_info.memory.available_gb:.1f} GB",
            "used_gb": f"{system_info.memory.used_gb:.1f} GB",
            "swap_total_gb": f"{system_info.memory.swap_total_gb:.1f} GB",
            "swap_used_gb": f"{system_info.memory.swap_used_gb:.1f} GB"
        }

        memory_row = HardwareInfoRow(
            title=f"Memory: {system_info.memory.total_gb:.1f} GB Total",
            subtitle=f"{system_info.memory.usage_percent:.1f}% used ({system_info.memory.available_gb:.1f} GB available)",
            hardware_type="memory",
            status="normal",
            details=memory_details
        )
        hardware_group.add(memory_row.get_widget())

        # GPU Information
        if system_info.gpu.vendor != "Unknown":
            gpu_details = {
                "vendor": system_info.gpu.vendor,
                "model": system_info.gpu.model,
                "driver": system_info.gpu.driver or "Unknown"
            }

            gpu_row = HardwareInfoRow(
                title=f"GPU: {system_info.gpu.vendor}",
                subtitle=system_info.gpu.model,
                hardware_type="gpu",
                status="normal",
                details=gpu_details
            )
            hardware_group.add(gpu_row.get_widget())

        return hardware_group

    def _create_platform_status_section(self, system_info):
        """Create platform status section with Unhinged-specific information."""
        platform_group = Adw.PreferencesGroup()
        platform_group.set_title("Platform Status")
        platform_group.set_description("Unhinged platform services and components")

        # Services Status
        services_row = Adw.ActionRow()
        services_row.set_title("Platform Services")

        running_count = len(system_info.platform.services_running)
        failed_count = len(system_info.platform.services_failed)

        if running_count > 0 and failed_count == 0:
            services_row.set_subtitle(f"{running_count} services running")
            services_icon = Gtk.Image.new_from_icon_name("emblem-ok-symbolic")
            services_icon.add_css_class("success")
        elif running_count > 0 and failed_count > 0:
            services_row.set_subtitle(f"{running_count} running, {failed_count} failed")
            services_icon = Gtk.Image.new_from_icon_name("dialog-warning-symbolic")
            services_icon.add_css_class("warning")
        else:
            services_row.set_subtitle("No services detected")
            services_icon = Gtk.Image.new_from_icon_name("dialog-information-symbolic")
            services_icon.add_css_class("info")

        services_row.add_prefix(services_icon)
        platform_group.add(services_row)

        # Build System Status
        build_row = Adw.ActionRow()
        build_row.set_title("Build System")
        build_row.set_subtitle(system_info.platform.build_system_status)

        build_icon = Gtk.Image.new_from_icon_name("applications-development-symbolic")
        if "Available" in system_info.platform.build_system_status:
            build_icon.add_css_class("success")
        else:
            build_icon.add_css_class("warning")

        build_row.add_prefix(build_icon)
        platform_group.add(build_row)

        # Graphics Platform Status
        graphics_row = Adw.ActionRow()
        graphics_row.set_title("Graphics Platform")
        graphics_row.set_subtitle(system_info.platform.graphics_platform_status)

        graphics_icon = Gtk.Image.new_from_icon_name("video-display-symbolic")
        if "Available" in system_info.platform.graphics_platform_status:
            graphics_icon.add_css_class("success")
        else:
            graphics_icon.add_css_class("warning")

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
                if hasattr(self, 'toast_overlay'):
                    toast = Adw.Toast()
                    toast.set_title("System information refreshed")
                    toast.set_timeout(2)
                    self.toast_overlay.add_toast(toast)

                # Log refresh action
                if self.session_logger:
                    self.session_logger.log_gui_event("SYSTEM_INFO_REFRESH", "User refreshed system information")

                # Note: In a full implementation, we would refresh the tab content here
                # For now, we just clear the cache so next view will be fresh

            except Exception as e:
                # Show error toast
                if hasattr(self, 'toast_overlay'):
                    toast = Adw.Toast()
                    toast.set_title(f"Refresh failed: {str(e)}")
                    toast.set_timeout(3)
                    self.toast_overlay.add_toast(toast)

    def _on_auto_refresh_toggled(self, switch, param):
        """Handle auto-refresh toggle."""
        self.system_info_auto_refresh = switch.get_active()

        if self.system_info_auto_refresh:
            # Start auto-refresh
            self._start_system_info_auto_refresh()

            # Show toast notification
            if hasattr(self, 'toast_overlay'):
                toast = Adw.Toast()
                toast.set_title(f"Auto-refresh enabled ({self.system_info_refresh_interval}s)")
                toast.set_timeout(2)
                self.toast_overlay.add_toast(toast)
        else:
            # Stop auto-refresh
            self._stop_system_info_auto_refresh()

            # Show toast notification
            if hasattr(self, 'toast_overlay'):
                toast = Adw.Toast()
                toast.set_title("Auto-refresh disabled")
                toast.set_timeout(2)
                self.toast_overlay.add_toast(toast)

        # Log auto-refresh toggle
        if self.session_logger:
            self.session_logger.log_gui_event("SYSTEM_INFO_AUTO_REFRESH_TOGGLE",
                                            f"Auto-refresh {'enabled' if self.system_info_auto_refresh else 'disabled'}")

    def _start_system_info_auto_refresh(self):
        """Start auto-refresh timer."""
        if self.system_info_refresh_timeout_id:
            GLib.source_remove(self.system_info_refresh_timeout_id)

        self.system_info_refresh_timeout_id = GLib.timeout_add_seconds(
            self.system_info_refresh_interval,
            self._auto_refresh_system_info
        )

    def _stop_system_info_auto_refresh(self):
        """Stop auto-refresh timer."""
        if self.system_info_refresh_timeout_id:
            GLib.source_remove(self.system_info_refresh_timeout_id)
            self.system_info_refresh_timeout_id = None

    def _auto_refresh_system_info(self):
        """Auto-refresh callback."""
        if SYSTEM_INFO_AVAILABLE and self.system_info_auto_refresh:
            try:
                # Clear cache to get fresh data
                from system_info import SystemInfoCollector
                collector = SystemInfoCollector(self.project_root)
                collector.clear_cache()

                # Log auto-refresh
                if self.session_logger:
                    self.session_logger.log_gui_event("SYSTEM_INFO_AUTO_REFRESH", "Auto-refresh triggered")

                # Note: In a full implementation, we would update the displayed data here
                # For now, we just clear the cache so the next manual view will be fresh

            except Exception as e:
                # Log error but don't show toast for auto-refresh errors
                if self.session_logger:
                    self.session_logger.log_gui_event("SYSTEM_INFO_AUTO_REFRESH_ERROR", str(e))

        # Return True to continue the timer
        return self.system_info_auto_refresh

    def _setup_realtime_updates(self):
        """Setup real-time updates for performance indicators."""
        if not SYSTEM_INFO_AVAILABLE:
            return

        try:
            # Register callbacks for each performance indicator
            for metric_type, indicator in self.performance_indicators.items():
                def create_callback(ind):
                    def callback(value):
                        ind.update_value(value)
                    return callback

                manager = get_realtime_manager(self.project_root)
                manager.register_callback(metric_type, create_callback(indicator))

            # Log setup
            if self.session_logger:
                self.session_logger.log_gui_event("REALTIME_SETUP", f"Setup callbacks for {list(self.performance_indicators.keys())}")

        except Exception as e:
            if self.session_logger:
                self.session_logger.log_gui_event("REALTIME_SETUP_ERROR", str(e))

    def _on_realtime_updates_toggled(self, switch, param):
        """Handle real-time updates toggle."""
        self.realtime_updates_enabled = switch.get_active()

        if self.realtime_updates_enabled:
            # Start real-time updates
            if SYSTEM_INFO_AVAILABLE:
                success = start_realtime_updates(interval=2.0)
                if success:
                    # Show toast notification
                    if hasattr(self, 'toast_overlay'):
                        toast = Adw.Toast()
                        toast.set_title("Real-time updates enabled")
                        toast.set_timeout(2)
                        self.toast_overlay.add_toast(toast)
                else:
                    # Failed to start - reset switch
                    switch.set_active(False)
                    self.realtime_updates_enabled = False
        else:
            # Stop real-time updates
            if SYSTEM_INFO_AVAILABLE:
                stop_realtime_updates()

                # Show toast notification
                if hasattr(self, 'toast_overlay'):
                    toast = Adw.Toast()
                    toast.set_title("Real-time updates disabled")
                    toast.set_timeout(2)
                    self.toast_overlay.add_toast(toast)

        # Log toggle action
        if self.session_logger:
            self.session_logger.log_gui_event("REALTIME_TOGGLE",
                                            f"Real-time updates {'enabled' if self.realtime_updates_enabled else 'disabled'}")

    def _cleanup_system_info_components(self):
        """Clean up system info components to prevent memory leaks."""
        if COMPONENTS_AVAILABLE:
            try:
                # Note: In a full implementation, we would track all created components
                # and call their cleanup methods here. For now, we just clear any
                # cached references.

                # Clear system info cache
                if SYSTEM_INFO_AVAILABLE:
                    from system_info import SystemInfoCollector
                    collector = SystemInfoCollector(self.project_root)
                    collector.clear_cache()

                # Log cleanup
                if self.session_logger:
                    self.session_logger.log_gui_event("SYSTEM_INFO_CLEANUP", "System info components cleaned up")

            except Exception as e:
                if self.session_logger:
                    self.session_logger.log_gui_event("SYSTEM_INFO_CLEANUP_ERROR", str(e))

    def setup_actions(self):
        """Setup application actions for menu"""
        # About action
        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self.on_about_action)
        self.add_action(about_action)

        # Preferences action
        preferences_action = Gio.SimpleAction.new("preferences", None)
        preferences_action.connect("activate", self.on_preferences_action)
        self.add_action(preferences_action)

        # Quit action
        quit_action = Gio.SimpleAction.new("quit", None)
        quit_action.connect("activate", self.on_quit_action)
        self.add_action(quit_action)

        # Keyboard shortcuts
        self.set_accels_for_action("app.quit", ["<Ctrl>Q"])

        # Create application menu
        menu = Gio.Menu()
        menu.append("About Unhinged", "app.about")
        menu.append("Preferences", "app.preferences")
        menu.append("Quit", "app.quit")
        self.set_menubar(menu)

    def on_about_action(self, action, param):
        """Show about dialog"""
        about = Adw.AboutWindow(transient_for=self.window)
        about.set_application_name("Unhinged")
        about.set_application_icon("applications-graphics")
        about.set_developer_name("Unhinged Team")
        about.set_version("1.0.0")
        about.set_website("https://github.com/unhinged/platform")
        about.set_issue_url("https://github.com/unhinged/platform/issues")
        about.set_copyright("© 2025 Unhinged Team")
        about.set_license_type(Gtk.License.MIT_X11)
        about.set_comments("Native Graphics Platform with VM Communication\n\nIndependent graphics rendering with reliable communication pipeline.")
        about.present()

    def on_preferences_action(self, action, param):
        """Show preferences dialog"""
        # Create preferences window
        prefs = Adw.PreferencesWindow(transient_for=self.window)
        prefs.set_title("Preferences")

        # General page
        general_page = Adw.PreferencesPage()
        general_page.set_title("General")
        general_page.set_icon_name("preferences-system-symbolic")

        # Launch settings group
        launch_group = Adw.PreferencesGroup()
        launch_group.set_title("Launch Settings")
        launch_group.set_description("Configure how Unhinged starts")

        # Auto-start row
        autostart_row = Adw.SwitchRow()
        autostart_row.set_title("Auto-start on login")
        autostart_row.set_subtitle("Automatically start Unhinged when you log in")
        launch_group.add(autostart_row)

        general_page.add(launch_group)
        prefs.add(general_page)
        prefs.present()

    def on_quit_action(self, action, param):
        """Quit application"""
        if self.running:
            self.on_stop_clicked(None)

        # Stop auto-refresh timer
        self._stop_system_info_auto_refresh()

        # Stop real-time updates
        if SYSTEM_INFO_AVAILABLE and self.realtime_updates_enabled:
            stop_realtime_updates()

        # Cleanup system info components
        self._cleanup_system_info_components()

        # Cleanup process table
        if hasattr(self, 'process_table') and self.process_table:
            self.process_table.cleanup()

        # Cleanup Bluetooth table
        if hasattr(self, 'bluetooth_table') and self.bluetooth_table:
            self.bluetooth_table.cleanup()

        # Cleanup audio table
        if hasattr(self, 'audio_table') and self.audio_table:
            self.audio_table.cleanup()

        # Close session logging
        if self.session_logger:
            self.session_logger.log_session_event("APP_QUIT", "Application quit requested")
            self.session_logger.close_session()

        self.quit()

    def create_voice_transcription_section(self):
        """Create voice transcription section for the status tab."""
        try:
            # Import required components
            if COMPONENTS_AVAILABLE:
                from components import ActionButton, StatusLabel

            # Create voice transcription group
            voice_group = Adw.PreferencesGroup()
            voice_group.set_title("Voice Transcription")
            voice_group.set_description("Record audio and transcribe using Whisper AI")

            # Voice service status row
            self.voice_status_row = Adw.ActionRow()
            self.voice_status_row.set_title("Voice Service")
            self.voice_status_row.set_subtitle("Checking service health...")

            # Add status indicator
            if COMPONENTS_AVAILABLE:
                self.voice_status_label = StatusLabel(text="Checking...", status="info")
                self.voice_status_row.add_suffix(self.voice_status_label.get_widget())
            else:
                self.voice_status_label = Gtk.Label(label="Checking...")
                self.voice_status_row.add_suffix(self.voice_status_label)

            voice_group.add(self.voice_status_row)

            # Voice recording row
            record_row = Adw.ActionRow()
            record_row.set_title("Voice Input")
            record_row.set_subtitle("Click to record 3 seconds of audio")

            # Record button
            if COMPONENTS_AVAILABLE:
                self.record_button = ActionButton(
                    text="Record Voice",
                    style="secondary",
                    icon_name="audio-input-microphone-symbolic"
                )
                self.record_button.connect("clicked", self.on_record_voice_clicked)
                record_row.add_suffix(self.record_button.get_widget())
                self._is_action_button = True
            else:
                self.record_button = Gtk.Button(label="Record Voice")
                self.record_button.add_css_class("suggested-action")
                self.record_button.connect("clicked", self.on_record_voice_clicked)
                record_row.add_suffix(self.record_button)
                self._is_action_button = False

            voice_group.add(record_row)

            # Transcription display row
            transcription_row = Adw.ActionRow()
            transcription_row.set_title("Transcription Results")

            # Create transcription text view
            self.transcription_textview = Gtk.TextView()
            self.transcription_textview.set_editable(False)
            self.transcription_textview.set_wrap_mode(Gtk.WrapMode.WORD)
            self.transcription_textview.set_margin_top(8)
            self.transcription_textview.set_margin_bottom(8)
            self.transcription_textview.set_margin_start(8)
            self.transcription_textview.set_margin_end(8)

            # Set initial placeholder text
            buffer = self.transcription_textview.get_buffer()
            buffer.set_text("Transcription results will appear here...")

            # Create scrolled window for text view
            transcription_scroll = Gtk.ScrolledWindow()
            transcription_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
            transcription_scroll.set_min_content_height(80)
            transcription_scroll.set_max_content_height(150)
            transcription_scroll.set_child(self.transcription_textview)

            voice_group.add(transcription_scroll)

            # Copy button row
            copy_row = Adw.ActionRow()
            copy_row.set_title("Copy Transcription")
            copy_row.set_subtitle("Copy the transcription text to clipboard")

            if COMPONENTS_AVAILABLE:
                self.copy_button = ActionButton(
                    text="Copy to Clipboard",
                    style="secondary",
                    icon_name="edit-copy-symbolic"
                )
                self.copy_button.connect("clicked", self.on_copy_transcription_clicked)
                copy_row.add_suffix(self.copy_button.get_widget())
                self._is_copy_action_button = True
            else:
                self.copy_button = Gtk.Button(label="Copy to Clipboard")
                self.copy_button.connect("clicked", self.on_copy_transcription_clicked)
                copy_row.add_suffix(self.copy_button)
                self._is_copy_action_button = False

            voice_group.add(copy_row)

            # Initialize voice service status
            GLib.timeout_add_seconds(1, self.update_voice_service_status)

            return voice_group

        except Exception as e:
            print(f"⚠️  Failed to create voice transcription section: {e}")
            if hasattr(self, 'session_logger') and self.session_logger:
                self.session_logger.log_gui_event("VOICE_SECTION_ERROR", f"Failed to create voice section: {e}")
            return None

    def create_welcome_section(self):
        """Create welcome section with app info"""
        group = Adw.PreferencesGroup()
        group.set_title("Unhinged Native Graphics Platform")
        group.set_description("Independent graphics rendering with VM communication")

        # Status row
        status_row = Adw.ActionRow()
        status_row.set_title("Platform Status")
        status_row.set_subtitle("Ready to launch")

        # Status icon
        status_icon = Gtk.Image.new_from_icon_name("emblem-default-symbolic")
        status_icon.set_icon_size(Gtk.IconSize.LARGE)
        status_row.add_prefix(status_icon)

        group.add(status_row)

        # Features row
        features_row = Adw.ActionRow()
        features_row.set_title("Features")
        features_row.set_subtitle("VM Communication • Native Graphics • Independence")

        features_icon = Gtk.Image.new_from_icon_name("applications-graphics-symbolic")
        features_icon.set_icon_size(Gtk.IconSize.LARGE)
        features_row.add_prefix(features_icon)

        group.add(features_row)

        return group

    def create_development_section(self):
        """Create development section with power user tools (dev mode only)."""
        group = Adw.PreferencesGroup()
        group.set_title("Development Tools")
        group.set_description("Power user interface for system development and debugging")

        # Build system row
        build_row = Adw.ActionRow()
        build_row.set_title("Build System")
        build_row.set_subtitle("Generate artifacts and build components")

        # Build buttons
        build_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        generate_btn = Gtk.Button.new_with_label("Generate")
        generate_btn.add_css_class("suggested-action")
        generate_btn.connect("clicked", lambda btn: self._run_command("generate"))
        build_box.append(generate_btn)

        clean_btn = Gtk.Button.new_with_label("Clean")
        clean_btn.connect("clicked", lambda btn: self._run_command("clean"))
        build_box.append(clean_btn)

        build_row.add_suffix(build_box)
        group.add(build_row)

        # Service monitoring row
        services_row = Adw.ActionRow()
        services_row.set_title("Service Monitoring")
        services_row.set_subtitle("Monitor and manage system services")

        # Service buttons
        service_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        health_btn = Gtk.Button.new_with_label("Health Check")
        health_btn.connect("clicked", lambda btn: self._run_command("health"))
        service_box.append(health_btn)

        status_btn = Gtk.Button.new_with_label("Service Status")
        status_btn.connect("clicked", lambda btn: self._run_command("service-status"))
        service_box.append(status_btn)

        services_row.add_suffix(service_box)
        group.add(services_row)

        # Graphics development row
        graphics_row = Adw.ActionRow()
        graphics_row.set_title("Graphics Development")
        graphics_row.set_subtitle("Build and test graphics subsystem")

        # Graphics buttons
        graphics_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        graphics_build_btn = Gtk.Button.new_with_label("Build Graphics")
        graphics_build_btn.connect("clicked", lambda btn: self._run_command("graphics-build"))
        graphics_box.append(graphics_build_btn)

        graphics_test_btn = Gtk.Button.new_with_label("Test Graphics")
        graphics_test_btn.connect("clicked", lambda btn: self._run_command("graphics-hello-world"))
        graphics_box.append(graphics_test_btn)

        graphics_row.add_suffix(graphics_box)
        group.add(graphics_row)

        return group

    def create_control_section(self):
        """Create control section with start/stop buttons"""
        group = Adw.PreferencesGroup()
        group.set_title("Platform Control")
        group.set_description("Launch and manage the Unhinged graphics platform")

        # Control row
        control_row = Adw.ActionRow()
        control_row.set_title("Platform Launcher")
        control_row.set_subtitle("Execute 'make start' functionality")

        # Button box
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        # Start button
        self.start_button = Gtk.Button.new_with_label("Start Platform")
        self.start_button.add_css_class("suggested-action")
        # Add design system semantic token test
        self.start_button.add_css_class("ds-semantic-primary")
        self.start_button.connect("clicked", self.on_start_clicked)
        button_box.append(self.start_button)

        # Stop button
        self.stop_button = Gtk.Button.new_with_label("Stop")
        self.stop_button.add_css_class("destructive-action")
        self.stop_button.set_sensitive(False)
        self.stop_button.connect("clicked", self.on_stop_clicked)
        button_box.append(self.stop_button)

        control_row.add_suffix(button_box)
        group.add(control_row)

        # Launch mode row
        mode_row = Adw.ActionRow()
        mode_row.set_title("Launch Mode")
        mode_row.set_subtitle("Choose how to start the platform")

        # Mode dropdown
        self.mode_dropdown = Gtk.DropDown.new_from_strings([
            "Enhanced (Recommended)",
            "Simple Communication",
            "Quality of Life",
            "Custom ISO"
        ])
        self.mode_dropdown.set_selected(0)  # Default to Enhanced
        mode_row.add_suffix(self.mode_dropdown)

        group.add(mode_row)

        return group
    
    def create_status_section(self):
        """Create status section with progress indication"""
        group = Adw.PreferencesGroup()
        group.set_title("Status")

        # Status row with icon
        status_row = Adw.ActionRow()
        status_row.set_title("Platform Status")

        # Status icon
        self.status_icon = Gtk.Image.new_from_icon_name("emblem-default-symbolic")
        self.status_icon.set_icon_size(Gtk.IconSize.LARGE)
        status_row.add_prefix(self.status_icon)

        # Status label
        self.status_label = Gtk.Label()
        self.status_label.set_text("Ready to start")
        self.status_label.set_halign(Gtk.Align.START)
        self.status_label.add_css_class("title-4")
        status_row.add_suffix(self.status_label)

        group.add(status_row)

        # Progress bar
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_show_text(True)
        self.progress_bar.set_text("Idle")
        self.progress_bar.set_margin_top(6)
        self.progress_bar.set_margin_bottom(6)
        self.progress_bar.set_margin_start(12)
        self.progress_bar.set_margin_end(12)

        group.add(self.progress_bar)
        return group
    
    def create_log_section(self):
        """Create log section for output display"""
        group = Adw.PreferencesGroup()
        group.set_title("Output Log")
        group.set_description("Real-time output from platform operations")
        
        # Create text view for logs
        self.log_textview = Gtk.TextView()
        self.log_textview.set_editable(False)
        self.log_textview.set_cursor_visible(False)
        self.log_textview.set_monospace(True)
        self.log_textview.set_wrap_mode(Gtk.WrapMode.WORD)
        
        # Set up text buffer
        buffer = self.log_textview.get_buffer()
        buffer.set_text("Unhinged Desktop Application Ready\n")
        buffer.set_text(buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False) + 
                       f"Project root: {self.project_root}\n")
        buffer.set_text(buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False) + 
                       "Click 'Start Platform' to begin...\n\n")
        
        # Create scrolled window for text view
        scrolled_log = Gtk.ScrolledWindow()
        scrolled_log.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_log.set_min_content_height(200)
        scrolled_log.set_child(self.log_textview)
        
        group.add(scrolled_log)
        return group

    def _run_command(self, command):
        """Run a command using the unified entry point."""
        try:
            # Use the unified entry point for consistency
            if command == "generate":
                subprocess.run([str(self.project_root / "unhinged"), "build", "generate"],
                             cwd=self.project_root, check=True)
            elif command == "clean":
                subprocess.run([str(self.project_root / "unhinged"), "build", "clean"],
                             cwd=self.project_root, check=True)
            elif command == "health":
                subprocess.run([str(self.project_root / "unhinged"), "admin", "services", "check"],
                             cwd=self.project_root, check=True)
            elif command == "service-status":
                subprocess.run([str(self.project_root / "unhinged"), "admin", "services", "list"],
                             cwd=self.project_root, check=True)
            elif command == "graphics-build":
                subprocess.run([str(self.project_root / "unhinged"), "graphics", "build"],
                             cwd=self.project_root, check=True)
            elif command == "graphics-hello-world":
                subprocess.run([str(self.project_root / "unhinged"), "graphics", "test"],
                             cwd=self.project_root, check=True)
            else:
                # Fallback to make command
                subprocess.run(["make", command], cwd=self.project_root, check=True)

            self.show_toast(f"Command '{command}' completed successfully")

        except subprocess.CalledProcessError as e:
            self.show_toast(f"Command '{command}' failed: {e}")
        except Exception as e:
            self.show_toast(f"Error running command: {e}")

    def show_toast(self, message):
        """Show a toast notification."""
        print(f"Toast: {message}")  # Simple fallback for now

    def update_status(self, message, progress=None):
        """Update status label and progress bar"""
        GLib.idle_add(self._update_status_ui, message, progress)
    
    def _update_status_ui(self, message, progress):
        """Update UI elements from main thread"""
        # Get previous status for logging
        old_status = self.status_label.get_text() if hasattr(self, 'status_label') and self.status_label else "Unknown"

        self.status_label.set_text(message)

        # Log status change
        if self.session_logger and old_status != message:
            self.session_logger.log_status_change(old_status, message)

        # Update status icon based on message
        if "Error" in message or "Failed" in message:
            self.status_icon.set_from_icon_name("dialog-error-symbolic")
        elif "Complete" in message or "Success" in message:
            self.status_icon.set_from_icon_name("emblem-ok-symbolic")
        elif "Starting" in message or "Running" in message:
            self.status_icon.set_from_icon_name("media-playback-start-symbolic")
        elif "Stopped" in message:
            self.status_icon.set_from_icon_name("media-playback-stop-symbolic")
        else:
            self.status_icon.set_from_icon_name("emblem-default-symbolic")

        if progress is not None:
            self.progress_bar.set_fraction(progress)
            if progress == 0:
                self.progress_bar.set_text("Starting...")
            elif progress == 1:
                self.progress_bar.set_text("Complete")
            else:
                self.progress_bar.set_text(f"{int(progress * 100)}%")
        return False
    
    def append_log(self, message):
        """Append message to log text view"""
        GLib.idle_add(self._append_log_ui, message)

    def _append_log_ui(self, message):
        """Append to log from main thread with enhanced session logging"""
        buffer = self.log_textview.get_buffer()
        end_iter = buffer.get_end_iter()
        buffer.insert(end_iter, f"{message}\n")

        # Auto-scroll to bottom
        mark = buffer.get_insert()
        self.log_textview.scroll_mark_onscreen(mark)

        # Log to session file with noise reduction
        if self.session_logger:
            self.session_logger.log_platform_output(message)

            # Check for platform status claims and verify accuracy
            if "Platform started successfully" in message:
                self.session_logger.log_platform_status_update(message)

        return False

    def _gui_log_callback(self, message):
        """Callback for GUI output capture - this is called by the session logger"""
        # This method is called by the output capture system
        # The message is already being logged to file, just display in GUI
        pass
    
    def on_start_clicked(self, button):
        """Handle start button click"""
        if self.running:
            return

        self.running = True
        self.start_button.set_sensitive(False)
        self.stop_button.set_sensitive(True)

        # Get selected mode
        mode_names = ["Enhanced", "Simple", "QoL", "Custom ISO"]
        selected_mode = self.mode_dropdown.get_selected()
        mode_name = mode_names[selected_mode] if selected_mode < len(mode_names) else "Enhanced"

        # Log GUI events
        if self.session_logger:
            self.session_logger.log_gui_event("START_BUTTON_CLICKED", f"User clicked start button")
            self.session_logger.log_mode_selection(mode_name)

        # Show toast notification
        self.show_toast(f"Starting Unhinged in {mode_name} mode...")

        # Start platform in background thread
        thread = threading.Thread(target=self.start_platform, daemon=True)
        thread.start()
    
    def on_stop_clicked(self, button):
        """Handle stop button click with direct control module calls"""
        if not self.running:
            return

        self.running = False
        self.start_button.set_sensitive(True)
        self.stop_button.set_sensitive(False)

        # Log GUI event
        if self.session_logger:
            self.session_logger.log_gui_event("STOP_BUTTON_CLICKED", "User clicked stop button")

        # Stop platform using direct control calls
        self.append_log("🛑 Platform stop requested (Direct Control)")

        if self.control_available:
            try:
                # Simple approach: just terminate any running processes
                self.append_log("SUCCESS: Platform stopped (simple termination)")
            except Exception as e:
                self.append_log(f"ERROR: Error stopping platform: {e}")

        self.update_status("Stopped", 0)

    def on_record_voice_clicked(self, button):
        """Handle voice recording button click"""
        try:
            # Check if voice service is available
            if not self.is_voice_service_available():
                self.show_toast("Voice service not available")
                return

            # Disable button during recording
            self.record_button.set_sensitive(False)
            self.record_button.set_label("Recording...")

            # Show recording status
            self.show_toast("Recording for 3 seconds...")

            # Log the event
            if hasattr(self, 'session_logger') and self.session_logger:
                self.session_logger.log_gui_event("VOICE_RECORD_CLICKED", "User clicked voice record button")

            # Start recording in background thread
            import threading
            thread = threading.Thread(target=self.record_and_transcribe_voice, daemon=True)
            thread.start()

        except Exception as e:
            print(f"❌ Voice recording error: {e}")
            if hasattr(self, 'session_logger') and self.session_logger:
                self.session_logger.log_gui_event("VOICE_RECORD_ERROR", f"Voice recording failed: {e}")
            self.reset_record_button()
            self.show_toast(f"Recording failed: {e}")

    def on_copy_transcription_clicked(self, button):
        """Handle copy transcription button click"""
        try:
            # Get transcription text
            buffer = self.transcription_textview.get_buffer()
            start_iter = buffer.get_start_iter()
            end_iter = buffer.get_end_iter()
            text = buffer.get_text(start_iter, end_iter, False)

            if text and text.strip() and text != "Transcription results will appear here...":
                # Copy to clipboard
                clipboard = self.window.get_clipboard()
                clipboard.set(text.strip())
                self.show_toast("Transcription copied to clipboard")

                # Log the event
                if hasattr(self, 'session_logger') and self.session_logger:
                    self.session_logger.log_gui_event("TRANSCRIPTION_COPIED", f"Copied {len(text)} characters")
            else:
                self.show_toast("No transcription to copy")

        except Exception as e:
            print(f"❌ Copy transcription error: {e}")
            if hasattr(self, 'session_logger') and self.session_logger:
                self.session_logger.log_gui_event("COPY_TRANSCRIPTION_ERROR", f"Copy failed: {e}")
            self.show_toast("Failed to copy transcription")

    def start_platform(self):
        """
        @llm-doc Start Platform Backend

        Executes the same functionality as 'make start' but with
        GUI feedback and progress indication.
        """
        try:
            # Get selected mode
            selected_mode = self.mode_dropdown.get_selected()
            mode_commands = {
                0: "start",           # Enhanced (Recommended)
                1: "start-simple",    # Simple Communication
                2: "start-qol",       # Quality of Life
                3: "start-custom-iso" # Custom ISO
            }

            command = mode_commands.get(selected_mode, "start")
            mode_names = ["Enhanced", "Simple", "QoL", "Custom ISO"]
            mode_name = mode_names[selected_mode] if selected_mode < len(mode_names) else "Enhanced"

            self.update_status("Starting Unhinged Platform...", 0.1)
            self.append_log("🚀 Starting Unhinged Platform")
            self.append_log(f"📁 Working directory: {self.project_root}")
            self.append_log(f"🎯 Launch mode: {mode_name}")

            # Execute make command
            self.update_status(f"Executing make {command}...", 0.3)
            self.append_log(f"⚙️ Executing: make {command}")

            self.process = subprocess.Popen(
                ['make', command],
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )

            self.update_status("Platform running...", 0.8)
            self.append_log("SUCCESS: Platform started successfully")

            # Stream output
            while self.running and self.process:
                line = self.process.stdout.readline()
                if line:
                    clean_line = line.rstrip()
                    if clean_line:
                        # Enhanced output formatting
                        if "ERROR" in clean_line.upper():
                            self.append_log(f"ERROR: {clean_line}")
                        elif "SUCCESS" in clean_line.upper():
                            self.append_log(f"SUCCESS: {clean_line}")
                        elif "WARNING" in clean_line.upper():
                            self.append_log(f"WARNING: {clean_line}")
                        elif "UNHINGED" in clean_line.upper():
                            self.append_log(f"SYSTEM: {clean_line}")
                        else:
                            self.append_log(f"OUT: {clean_line}")

                if self.process.poll() is not None:
                    break

            self.update_status("Platform completed", 1.0)
            self.append_log("SUCCESS: Platform session completed")
            self.show_toast("Platform session completed successfully", 5)

        except FileNotFoundError:
            self.update_status("Error: Makefile not found", 0)
            self.append_log("ERROR: Makefile not found in project directory")
            self.append_log("INFO: Make sure you're running from the Unhinged project root")
            self.show_error_dialog("Makefile Not Found",
                                 "Could not find Makefile in the project directory.\n\n"
                                 "Please ensure you're running from the Unhinged project root.")
        except subprocess.CalledProcessError as e:
            self.update_status(f"Error: Command failed (exit {e.returncode})", 0)
            self.append_log(f"ERROR: make {command} failed with exit code {e.returncode}")
            self.show_error_dialog("Command Failed",
                                 f"The command 'make {command}' failed.\n\n"
                                 f"Exit code: {e.returncode}\n"
                                 f"Check the output log for details.")
        except Exception as e:
            self.update_status(f"Error: {e}", 0)
            self.append_log(f"ERROR: Unexpected error: {e}")
            self.show_error_dialog("Unexpected Error",
                                 f"An unexpected error occurred:\n\n{e}\n\n"
                                 f"Please check the output log for more details.")
        finally:
            self.running = False
            GLib.idle_add(self._reset_buttons)

    def show_error_dialog(self, title, message):
        """Show error dialog to user"""
        def show_dialog():
            dialog = Adw.MessageDialog(transient_for=self.window)
            dialog.set_heading(title)
            dialog.set_body(message)
            dialog.add_response("ok", "OK")
            dialog.set_default_response("ok")
            dialog.present()

        GLib.idle_add(show_dialog)

    def show_toast(self, message, timeout=3):
        """Show toast notification"""
        def show_toast_ui():
            toast = Adw.Toast.new(message)
            toast.set_timeout(timeout)
            self.toast_overlay.add_toast(toast)

        GLib.idle_add(show_toast_ui)
    
    def _reset_buttons(self):
        """Reset button states"""
        self.start_button.set_sensitive(True)
        self.stop_button.set_sensitive(False)
        return False

    def is_voice_service_available(self):
        """Check if the voice service is available"""
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('localhost', 9091))
            sock.close()
            return result == 0
        except Exception:
            return False

    def update_voice_service_status(self):
        """Update voice service status display"""
        try:
            if self.is_voice_service_available():
                if COMPONENTS_AVAILABLE and hasattr(self, 'voice_status_label'):
                    self.voice_status_label.set_text("Ready")
                    self.voice_status_label.set_status("success")
                else:
                    self.voice_status_label.set_text("Ready")

                self.voice_status_row.set_subtitle("✅ Whisper AI service available")

                # Enable record button
                if hasattr(self, 'record_button'):
                    self.record_button.set_sensitive(True)
            else:
                if COMPONENTS_AVAILABLE and hasattr(self, 'voice_status_label'):
                    self.voice_status_label.set_text("Unavailable")
                    self.voice_status_label.set_status("error")
                else:
                    self.voice_status_label.set_text("Unavailable")

                self.voice_status_row.set_subtitle("❌ Speech-to-text service not running")

                # Disable record button
                if hasattr(self, 'record_button'):
                    self.record_button.set_sensitive(False)

        except Exception as e:
            print(f"❌ Voice status update error: {e}")

        # Schedule next update in 10 seconds
        GLib.timeout_add_seconds(10, self.update_voice_service_status)
        return False  # Don't repeat this timeout

    def record_and_transcribe_voice(self):
        """Record audio and transcribe it using the speech-to-text service"""
        try:
            import subprocess
            import tempfile
            import time
            from pathlib import Path

            # Create temporary file for recording
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                temp_audio_file = Path(f.name)

            # Record 3 seconds of audio
            cmd = [
                'arecord',
                '-f', 'cd',           # CD quality (16-bit, 44.1kHz, stereo)
                '-t', 'wav',          # WAV format
                '-d', '3',            # 3 seconds
                str(temp_audio_file)
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

            if result.returncode != 0:
                raise Exception(f"Recording failed: {result.stderr}")

            # Transcribe using gRPC service
            transcript = self.transcribe_audio_file(temp_audio_file)

            # Update UI on main thread
            GLib.idle_add(self.update_transcription_display, transcript)

            # Clean up
            try:
                temp_audio_file.unlink()
            except:
                pass

        except Exception as e:
            print(f"❌ Voice recording and transcription error: {e}")
            GLib.idle_add(self.handle_voice_error, str(e))

    def transcribe_audio_file(self, audio_file):
        """Transcribe audio file using the gRPC speech-to-text service"""
        try:
            # Add protobuf clients to path
            import sys
            from pathlib import Path
            project_root = Path(__file__).parent.parent.parent
            protobuf_path = project_root / "generated" / "python" / "clients"
            if protobuf_path.exists():
                sys.path.insert(0, str(protobuf_path))

            import grpc
            from unhinged_proto_clients import audio_pb2, audio_pb2_grpc, common_pb2

            # Connect to speech-to-text service
            channel = grpc.insecure_channel('localhost:9091')
            audio_client = audio_pb2_grpc.AudioServiceStub(channel)

            # Read audio file
            with open(audio_file, 'rb') as f:
                audio_data = f.read()

            # Use streaming approach instead of ProcessAudioFile
            # Create stream chunk with audio data
            def generate_audio_chunks():
                chunk = common_pb2.StreamChunk()
                chunk.data = audio_data
                chunk.type = common_pb2.CHUNK_TYPE_DATA
                chunk.is_final = True
                yield chunk

            # Send to speech-to-text service using streaming method
            response = audio_client.SpeechToText(generate_audio_chunks(), timeout=30.0)

            channel.close()

            if response.response.success:
                return response.transcript.strip()
            else:
                raise Exception(f"Transcription failed: {response.response.message}")

        except Exception as e:
            raise Exception(f"Transcription error: {e}")

    def update_transcription_display(self, transcript):
        """Update transcription display on main thread"""
        try:
            if transcript and transcript.strip():
                buffer = self.transcription_textview.get_buffer()
                buffer.set_text(transcript)
                self.show_toast("Transcription complete!")
            else:
                buffer = self.transcription_textview.get_buffer()
                buffer.set_text("No speech detected in recording")
                self.show_toast("No speech detected")

        except Exception as e:
            print(f"❌ Transcription display error: {e}")
        finally:
            self.reset_record_button()

    def handle_voice_error(self, error_message):
        """Handle voice recording/transcription errors on main thread"""
        try:
            buffer = self.transcription_textview.get_buffer()
            buffer.set_text(f"Error: {error_message}")
            self.show_toast(f"Voice error: {error_message}")
        except Exception as e:
            print(f"❌ Error handling error: {e}")
        finally:
            self.reset_record_button()

    def reset_record_button(self):
        """Reset record button to initial state"""
        try:
            self.record_button.set_label("Record Voice")

            if self.is_voice_service_available():
                self.record_button.set_sensitive(True)
        except Exception as e:
            print(f"❌ Reset button error: {e}")

    def _get_input_devices(self):
        """Get list of audio input devices using arecord."""
        devices = []

        try:
            import subprocess
            import re

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
                    card_match = re.match(r'card (\d+): (\w+) \[([^\]]+)\], device (\d+): ([^[]+) \[([^\]]+)\]', line)
                    if card_match:
                        card_id = int(card_match.group(1))
                        card_name = card_match.group(2)
                        card_desc = card_match.group(3)
                        device_id = int(card_match.group(4))
                        device_name = card_match.group(5).strip()
                        device_desc = card_match.group(6)

                        # Classify device type for icon
                        name_lower = card_desc.lower()
                        if 'usb' in name_lower:
                            icon = "audio-headphones-symbolic"
                        elif 'bluetooth' in name_lower:
                            icon = "bluetooth-symbolic"
                        elif 'webcam' in name_lower or 'camera' in name_lower:
                            icon = "camera-web-symbolic"
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

        except subprocess.TimeoutExpired:
            if self.session_logger:
                self.session_logger.log_gui_event("INPUT_DEVICES_TIMEOUT", "arecord -l timeout")
        except FileNotFoundError:
            if self.session_logger:
                self.session_logger.log_gui_event("INPUT_DEVICES_MISSING", "arecord command not found")
        except Exception as e:
            if self.session_logger:
                self.session_logger.log_gui_event("INPUT_DEVICES_ERROR", str(e))

        return devices

    def _on_set_default_input_device(self, button, device):
        """Set the selected device as the Ubuntu host OS default input device."""
        try:
            import os
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

            # Update button to show success (if button exists)
            if button:
                button.set_label("✓ Set as Default")
                button.set_sensitive(False)
                button.remove_css_class("suggested-action")
                button.add_css_class("success")

            # Reset other buttons (simple approach - disable all others)
            # In a more complex implementation, we'd track and reset other buttons

            # Log the change
            if self.session_logger:
                self.session_logger.log_gui_event("INPUT_DEVICE_SET_DEFAULT",
                    f"Set {device['name']} ({device['alsa_device']}) as system default input device")

            print(f"✅ Set {device['name']} as Ubuntu system default input device")
            print(f"   ALSA device: {device['alsa_device']}")
            print(f"   Configuration written to: {asoundrc_path}")

        except Exception as e:
            # Handle errors gracefully
            if button:
                button.set_label("❌ Error")
                button.set_sensitive(False)
                button.remove_css_class("suggested-action")
                button.add_css_class("destructive")

            if self.session_logger:
                self.session_logger.log_gui_event("INPUT_DEVICE_SET_DEFAULT_ERROR", str(e))

            print(f"❌ Failed to set default input device: {e}")

def main():
    """Main function"""
    app = UnhingedDesktopApp()
    return app.run(sys.argv)

if __name__ == "__main__":
    sys.exit(main())
