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

# Import new architecture components
try:
    from .config import service_config, app_config, get_service_endpoint, validate_all_services, log_configuration
    from .service_connector import service_connector, service_registry
    from .audio_handler import AudioHandler, RecordingState
    from .exceptions import (
        UnhingedError, ServiceUnavailableError, AudioRecordingError,
        AudioTranscriptionError, get_user_friendly_message
    )
    ARCHITECTURE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ New architecture components not available: {e}")
    ARCHITECTURE_AVAILABLE = False

# Import component library
try:
    sys.path.append(str(Path(__file__).parent))
    from components import (
        StatusCard, StatusLabel, SystemInfoCard, HardwareInfoRow,
        PerformanceIndicator, SystemStatusGrid, ProcessTable,
        BluetoothTable, AudioTable, ChatBubble, LoadingDots, CopyButton
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

        # Loading indicators
        self.llm_loading_dots = None

        # Voice recording state
        self.recording_process = None
        self.recording_temp_file = None
        self.is_recording = False
        self.recording_start_time = None
        self.recording_timer_id = None

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

        # Initialize new architecture components
        self.audio_handler = None
        if ARCHITECTURE_AVAILABLE:
            try:
                # Initialize audio handler
                self.audio_handler = AudioHandler()
                self.audio_handler.set_callbacks(
                    state_callback=self._on_recording_state_changed,
                    result_callback=self._on_transcription_result,
                    error_callback=self._on_audio_error
                )

                # Log configuration for debugging
                if self.dev_mode:
                    log_configuration()

                # Validate service configuration
                if not validate_all_services():
                    print("⚠️ Some services are not properly configured")

                print("✅ New architecture components initialized")
            except Exception as e:
                print(f"⚠️ Failed to initialize new architecture: {e}")
                self.audio_handler = None
        else:
            print("ℹ️ Using legacy audio handling")

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

                # Add toast stack visual hierarchy styles
                toast_stack_css = """
                /* Toast Stack Visual Hierarchy */
                .toast-top-fade {
                    opacity: 0.5;
                    background: linear-gradient(135deg,
                        var(--color-surface-overlay, rgba(0,0,0,0.8)) 0%,
                        var(--color-surface-overlay, rgba(0,0,0,0.6)) 100%);
                    transition: opacity 0.3s ease-in-out;
                }

                .toast-second {
                    opacity: 0.8;
                    transform: translateY(4px);
                    transition: transform 0.2s ease-out, opacity 0.2s ease-out;
                }

                .toast-standard {
                    opacity: 1.0;
                    transform: translateY(8px);
                    transition: transform 0.2s ease-out;
                }

                /* Toast stack container improvements */
                toast {
                    margin-bottom: 2px;
                    box-shadow: var(--elevation-2, 0 2px 8px rgba(0,0,0,0.15));
                }

                toast.toast-top-fade {
                    z-index: 1003;
                }

                toast.toast-second {
                    z-index: 1002;
                }

                toast.toast-standard {
                    z-index: 1001;
                }
                """
                combined_css += toast_stack_css

                # Add recording indicator CSS
                recording_css = """
                /* Recording Indicator Styles */
                .recording-active {
                    background-color: var(--color-error, #dc3545) !important;
                    color: var(--color-text-inverse, #ffffff) !important;
                    animation: recording-pulse 1.5s infinite ease-in-out;
                }

                @keyframes recording-pulse {
                    0%, 100% {
                        opacity: 1;
                        transform: scale(1);
                    }
                    50% {
                        opacity: 0.8;
                        transform: scale(1.05);
                    }
                }

                .recording-timer {
                    font-family: var(--font-family-mono, monospace);
                    font-size: var(--font-size-sm, 12px);
                    font-weight: var(--font-weight-medium, 500);
                    color: var(--color-error, #dc3545);
                    background-color: var(--color-surface-container, #f8f9fa);
                    padding: var(--spacing-sp-1, 4px) var(--spacing-sp-2, 8px);
                    border-radius: var(--radius-sm, 4px);
                    border: var(--border-thin, 1px) solid var(--color-error, #dc3545);
                    margin-left: var(--spacing-sp-2, 8px);
                    animation: timer-blink 1s infinite ease-in-out;
                }

                @keyframes timer-blink {
                    0%, 50% { opacity: 1; }
                    51%, 100% { opacity: 0.7; }
                }

                /* Reduced motion preferences */
                @media (prefers-reduced-motion: reduce) {
                    .recording-active {
                        animation: none !important;
                        background-color: var(--color-error, #dc3545) !important;
                    }

                    .recording-timer {
                        animation: none !important;
                    }
                }
                """
                combined_css += recording_css

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

        # Toast stack management
        self.toast_stack = []
        self.max_toast_stack = 3

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
        """Create the status tab content using extracted StatusView."""
        try:
            from .views.status_view import StatusView

            self.status_view = StatusView(self)
            return self.status_view.create_content()

        except ImportError as e:
            print(f"⚠️ StatusView not available, using fallback: {e}")
            return self._create_status_fallback()
        except Exception as e:
            print(f"❌ Error creating status view: {e}")
            return self._create_status_fallback()

    def _create_status_fallback(self):
        """Fallback status implementation"""
        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        container.set_margin_top(16)
        container.set_margin_bottom(16)
        container.set_margin_start(16)
        container.set_margin_end(16)

        label = Gtk.Label(label="Status functionality temporarily unavailable")
        label.add_css_class("dim-label")
        container.append(label)

        return container

    def create_system_info_tab_content(self):
        """Create the system info tab content using extracted SystemInfoView."""
        try:
            from .views.system_view import SystemInfoView

            # Create system info view
            self.system_info_view = SystemInfoView(self)
            return self.system_info_view.create_content()

        except ImportError as e:
            print(f"⚠️ SystemInfoView not available, using fallback: {e}")
            return self._create_system_info_fallback()
        except Exception as e:
            print(f"❌ Error creating system info view: {e}")
            return self._create_system_info_fallback()

    def _create_system_info_fallback(self):
        """Fallback system info implementation"""
        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        container.set_margin_top(16)
        container.set_margin_bottom(16)
        container.set_margin_start(16)
        container.set_margin_end(16)

        label = Gtk.Label(label="System information functionality temporarily unavailable")
        label.add_css_class("dim-label")
        container.append(label)

        return container

    def create_processes_tab_content(self):
        """Create the processes tab content using extracted ProcessesView."""
        try:
            from .views.processes_view import ProcessesView

            # Create processes view
            self.processes_view = ProcessesView(self)
            return self.processes_view.create_content()

        except ImportError as e:
            print(f"⚠️ ProcessesView not available, using fallback: {e}")
            return self._create_processes_fallback()
        except Exception as e:
            print(f"❌ Error creating processes view: {e}")
            return self._create_processes_fallback()

    def _create_processes_fallback(self):
        """Fallback processes implementation"""
        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        container.set_margin_top(16)
        container.set_margin_bottom(16)
        container.set_margin_start(16)
        container.set_margin_end(16)

        label = Gtk.Label(label="Process monitoring functionality temporarily unavailable")
        label.add_css_class("dim-label")
        container.append(label)

        return container

    def create_input_tab_content(self):
        """Create the Input tab content using InputView."""
        try:
            from .views.input_view import InputView

            input_view = InputView()
            widget = input_view.render()

            if self.session_logger:
                self.session_logger.log_gui_event("INPUT_TAB_CREATED", "Input tab created")

            return widget

        except Exception as e:
            print(f"❌ Error creating input view: {e}")
            return self._create_input_fallback()

    def _create_input_fallback(self):
        """Fallback input implementation"""
        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        container.set_margin_top(16)
        container.set_margin_bottom(16)
        container.set_margin_start(16)
        container.set_margin_end(16)

        label = Gtk.Label(label="Input functionality temporarily unavailable")
        label.add_css_class("dim-label")
        container.append(label)

        return container

    def create_chatroom_tab_content(self):
        """Create the OS Chatroom tab content using extracted ChatroomView."""
        try:
            from .views.chatroom_view import ChatroomView

            # Create chatroom view
            self.chatroom_view = ChatroomView(self)
            return self.chatroom_view.create_content()

        except ImportError as e:
            print(f"⚠️ ChatroomView not available, using fallback: {e}")
            return self._create_chatroom_fallback()
        except Exception as e:
            print(f"❌ Error creating chatroom view: {e}")
            return self._create_chatroom_fallback()

    def _create_chatroom_fallback(self):
        """Fallback chatroom implementation"""
        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        container.set_margin_top(16)
        container.set_margin_bottom(16)
        container.set_margin_start(16)
        container.set_margin_end(16)

        label = Gtk.Label(label="Chatroom functionality temporarily unavailable")
        label.add_css_class("dim-label")
        container.append(label)

        return container





    def _start_toggle_recording(self):
        """Start toggle recording using AudioHandler"""
        try:
            if not hasattr(self, 'audio_handler'):
                self._init_audio_handler()

            self.audio_handler.start_recording()
            self.show_toast("Recording... (click to stop)")

            if self.session_logger:
                self.session_logger.log_gui_event("TOGGLE_RECORDING_START", "Started toggle recording")

        except Exception as e:
            print(f"❌ Start toggle recording error: {e}")
            self.show_toast(f"Recording failed: {e}")

    def _init_audio_handler(self):
        """Initialize the AudioHandler with callbacks"""
        try:
            from .handlers.audio_handler import AudioHandler, RecordingState

            self.audio_handler = AudioHandler()
            self.audio_handler.set_callbacks(
                state_callback=self._on_recording_state_changed,
                result_callback=self._on_transcription_result,
                error_callback=self._on_audio_error
            )

        except Exception as e:
            print(f"⚠️ Failed to initialize AudioHandler: {e}")
            self.audio_handler = None

    def _init_platform_handler(self):
        """Initialize the PlatformHandler with callbacks"""
        try:
            from .handlers.platform_handler import PlatformHandler

            self.platform_handler = PlatformHandler(self.project_root)
            self.platform_handler.set_callbacks(
                status_callback=self.update_status,
                log_callback=self.append_log,
                error_callback=self.show_error_dialog
            )

        except Exception as e:
            print(f"⚠️ Failed to initialize PlatformHandler: {e}")
            self.platform_handler = None



    def _stop_toggle_recording(self):
        """
        @llm-type service.audio
        @llm-does terminates recording process and initiates transcription workflow
        """
        import subprocess
        import time
        try:
            if not self.is_recording or not self.recording_process:
                return

            # Check if process is still running
            if self.recording_process.poll() is None:
                # Process is still running, send SIGINT to stop gracefully
                import signal
                self.recording_process.send_signal(signal.SIGINT)

                # Wait for graceful shutdown
                try:
                    self.recording_process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    # If graceful shutdown fails, force terminate
                    print("⚠️ Graceful recording stop timed out, force terminating")
                    self.recording_process.terminate()
                    self.recording_process.wait(timeout=2)

            self.is_recording = False

            # Stop recording timer and reset visual indicators
            self._stop_recording_timer()
            self._reset_chatroom_voice_button()

            # Critical fix: Wait for file system to flush the WAV file
            # This ensures the file is completely written before transcription
            time.sleep(0.5)  # Allow file system buffer to flush

            # Verify file exists and has content before proceeding
            if self.recording_temp_file and self.recording_temp_file.exists():
                file_size = self.recording_temp_file.stat().st_size
                print(f"🔍 Debug: WAV file size after recording: {file_size} bytes")

                # Wait a bit more if file is still being written (size is 0 or very small)
                retry_count = 0
                while file_size < 44 and retry_count < 10:  # WAV header is at least 44 bytes
                    time.sleep(0.1)
                    if self.recording_temp_file.exists():
                        file_size = self.recording_temp_file.stat().st_size
                        print(f"🔍 Debug: Retry {retry_count + 1}, WAV file size: {file_size} bytes")
                    retry_count += 1

            # Update UI
            self.show_toast("Processing voice...")

            # Log the event
            if self.session_logger:
                self.session_logger.log_gui_event("TOGGLE_RECORDING_STOP", "Stopped toggle recording")

            # Start transcription in background thread
            import threading
            thread = threading.Thread(target=self._transcribe_toggle_recording, daemon=True)
            thread.start()

        except subprocess.TimeoutExpired:
            # If graceful shutdown fails, force terminate
            print("⚠️ Graceful recording stop timed out, force terminating")
            self.recording_process.terminate()
            self.recording_process.wait(timeout=2)
            self.is_recording = False
            self._cleanup_recording()
        except Exception as e:
            print(f"❌ Stop toggle recording error: {e}")
            self._cleanup_recording()

    def _transcribe_toggle_recording(self):
        """Transcribe the toggle recording."""
        try:
            if not self.recording_temp_file or not self.recording_temp_file.exists():
                raise Exception("No recording file found")

            # Debug: Check file size and basic info
            file_size = self.recording_temp_file.stat().st_size
            print(f"🔍 Debug: WAV file size: {file_size} bytes")

            # Check if file is too small (WAV header is at least 44 bytes)
            if file_size < 44:
                raise Exception(f"WAV file too small ({file_size} bytes) - likely corrupted")

            # Additional validation: Check if file is a valid WAV file
            try:
                with open(self.recording_temp_file, 'rb') as f:
                    header = f.read(12)
                    if len(header) < 12 or header[:4] != b'RIFF' or header[8:12] != b'WAVE':
                        raise Exception("Invalid WAV file format - file may be corrupted")
                    print(f"✅ WAV file validation passed")
            except Exception as wav_error:
                raise Exception(f"WAV file validation failed: {wav_error}")

            # Transcribe using existing gRPC service
            transcript = self.transcribe_audio_file(self.recording_temp_file)

            # Update chatroom text editor on main thread
            GLib.idle_add(self._insert_chatroom_transcription, transcript)

        except Exception as e:
            print(f"❌ Toggle transcription error: {e}")
            GLib.idle_add(self._handle_chatroom_voice_error, str(e))
        finally:
            # Clean up
            self._cleanup_recording()

    def _update_chatroom_voice_button_for_recording(self):
        """
        @llm-type component.ui
        @llm-does applies recording visual state with CSS animations to voice button
        """
        try:
            if COMPONENTS_AVAILABLE:
                # For ActionButton, we can't directly change icon, but we can add CSS classes
                widget = self._chatroom_voice_button.get_widget()
                widget.add_css_class("recording-active")
                widget.set_tooltip_text("Recording... (click to stop)")
            else:
                # For regular Gtk.Button, change icon and tooltip
                self._chatroom_voice_button.set_icon_name("media-record")
                self._chatroom_voice_button.add_css_class("recording-active")
                self._chatroom_voice_button.set_tooltip_text("Recording... (click to stop)")
        except Exception as e:
            print(f"❌ Update chatroom voice button error: {e}")

    def _reset_chatroom_voice_button(self):
        """
        @llm-type component.ui
        @llm-does restores voice button to idle state removing recording animations
        """
        try:
            if COMPONENTS_AVAILABLE:
                widget = self._chatroom_voice_button.get_widget()
                widget.remove_css_class("recording-active")
                widget.set_tooltip_text("Click to start/stop recording")
            else:
                self._chatroom_voice_button.set_icon_name("audio-input-microphone-symbolic")
                self._chatroom_voice_button.remove_css_class("recording-active")
                self._chatroom_voice_button.set_tooltip_text("Click to start/stop recording")
        except Exception as e:
            print(f"❌ Reset chatroom voice button error: {e}")

    def _start_recording_timer(self):
        """
        @llm-type component.timer
        @llm-does creates and displays live MM:SS recording duration timer
        """
        try:
            # Create timer label if it doesn't exist
            if not hasattr(self, 'recording_timer_label'):
                self.recording_timer_label = Gtk.Label()
                self.recording_timer_label.set_text("00:00")
                self.recording_timer_label.add_css_class("recording-timer")
                self.recording_timer_label.set_visible(False)

                # Add timer to chatroom interface (next to voice button)
                if hasattr(self, '_chatroom_input_row'):
                    self._chatroom_input_row.append(self.recording_timer_label)

            # Show timer and start updating
            self.recording_timer_label.set_visible(True)
            self._update_recording_timer()

            # Schedule timer updates every second
            self.recording_timer_id = GLib.timeout_add_seconds(1, self._update_recording_timer)

        except Exception as e:
            print(f"❌ Start recording timer error: {e}")

    def _update_recording_timer(self):
        """
        @llm-type component.timer
        @llm-does updates timer display every second with current recording duration
        """
        try:
            if hasattr(self, 'recording_start_time') and self.is_recording:
                elapsed = time.time() - self.recording_start_time
                minutes = int(elapsed // 60)
                seconds = int(elapsed % 60)
                timer_text = f"{minutes:02d}:{seconds:02d}"

                if hasattr(self, 'recording_timer_label'):
                    self.recording_timer_label.set_text(timer_text)

                return True  # Continue timer
            else:
                return False  # Stop timer
        except Exception as e:
            print(f"❌ Update recording timer error: {e}")
            return False

    def _stop_recording_timer(self):
        """
        @llm-type component.timer
        @llm-does stops timer updates and hides recording duration display
        """
        try:
            # Stop timer updates
            if hasattr(self, 'recording_timer_id') and self.recording_timer_id:
                GLib.source_remove(self.recording_timer_id)
                self.recording_timer_id = None

            # Hide timer label
            if hasattr(self, 'recording_timer_label'):
                self.recording_timer_label.set_visible(False)

        except Exception as e:
            print(f"❌ Stop recording timer error: {e}")



    def _start_push_to_talk_recording(self):
        """Start push-to-talk recording (no duration limit)."""
        try:
            import subprocess
            import tempfile
            from pathlib import Path

            # Create temporary file for recording
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                self.recording_temp_file = Path(f.name)

            # Start unlimited recording with Whisper-optimal audio settings
            cmd = [
                'arecord',
                '-D', 'pipewire',     # Use PipeWire audio system
                '-f', 'S16_LE',       # 16-bit signed little-endian (optimal for Whisper)
                '-r', '16000',        # 16kHz sample rate (optimal for Whisper)
                '-c', '1',            # Mono (optimal for Whisper)
                '-t', 'wav',          # WAV format
                str(self.recording_temp_file)
            ]

            # Start recording process (non-blocking)
            self.recording_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            self.is_recording = True

            # Update UI
            self.show_toast("Recording... (release to stop)")

            # Log the event
            if self.session_logger:
                self.session_logger.log_gui_event("PUSH_TO_TALK_START", "Started push-to-talk recording")

        except Exception as e:
            print(f"❌ Start recording error: {e}")
            self.is_recording = False
            self.recording_process = None
            self.recording_temp_file = None
            raise e

    def _stop_push_to_talk_recording(self):
        """Stop push-to-talk recording and transcribe."""
        try:
            import time
            if not self.is_recording or not self.recording_process:
                return

            # Stop recording process
            self.recording_process.terminate()
            self.recording_process.wait(timeout=2)  # Wait for clean shutdown

            self.is_recording = False

            # Critical fix: Wait for file system to flush the WAV file
            time.sleep(0.5)  # Allow file system buffer to flush

            # Verify file exists and has content before proceeding
            if self.recording_temp_file and self.recording_temp_file.exists():
                file_size = self.recording_temp_file.stat().st_size
                print(f"🔍 Debug: Push-to-talk WAV file size: {file_size} bytes")

                # Wait a bit more if file is still being written
                retry_count = 0
                while file_size < 44 and retry_count < 10:  # WAV header is at least 44 bytes
                    time.sleep(0.1)
                    if self.recording_temp_file.exists():
                        file_size = self.recording_temp_file.stat().st_size
                        print(f"🔍 Debug: Push-to-talk retry {retry_count + 1}, WAV file size: {file_size} bytes")
                    retry_count += 1

            # Update UI
            self.show_toast("Processing voice...")

            # Log the event
            if self.session_logger:
                self.session_logger.log_gui_event("PUSH_TO_TALK_STOP", "Stopped push-to-talk recording")

            # Start transcription in background thread
            import threading
            thread = threading.Thread(target=self._transcribe_push_to_talk, daemon=True)
            thread.start()

        except Exception as e:
            print(f"❌ Stop recording error: {e}")
            self._cleanup_recording()

    def _transcribe_push_to_talk(self):
        """Transcribe the push-to-talk recording."""
        try:
            if not self.recording_temp_file or not self.recording_temp_file.exists():
                raise Exception("No recording file found")

            # Transcribe using existing gRPC service
            transcript = self.transcribe_audio_file(self.recording_temp_file)

            # Update chatroom text editor on main thread
            GLib.idle_add(self._insert_chatroom_transcription, transcript)

        except Exception as e:
            print(f"❌ Push-to-talk transcription error: {e}")
            GLib.idle_add(self._handle_chatroom_voice_error, str(e))
        finally:
            # Clean up
            self._cleanup_recording()

    def _cleanup_recording(self):
        """Clean up recording resources."""
        try:
            if self.recording_temp_file and self.recording_temp_file.exists():
                self.recording_temp_file.unlink()
        except:
            pass
        finally:
            # Stop timer and reset visual indicators
            self._stop_recording_timer()
            self._reset_chatroom_voice_button()

            # Clean up recording state
            self.recording_process = None
            self.recording_temp_file = None
            self.is_recording = False



    def _insert_chatroom_transcription(self, transcript):
        """Insert transcription into chatroom text editor."""
        try:
            if transcript and transcript.strip():
                # Get current content
                current_content = self._chatroom_text_editor.get_content()

                # Add transcription to current content (append with space if content exists)
                if current_content.strip():
                    new_content = current_content + " " + transcript.strip()
                else:
                    new_content = transcript.strip()

                # Set new content
                self._chatroom_text_editor.set_content(new_content)

                # Focus the text editor for user to continue editing
                self._chatroom_text_editor.focus()

                self.show_toast("Voice transcription added!")
            else:
                self.show_toast("No speech detected in recording")

        except Exception as e:
            print(f"❌ Chatroom transcription insert error: {e}")
        finally:
            self._reset_chatroom_voice_button()

    def _handle_chatroom_voice_error(self, error_message):
        """Handle voice recording/transcription errors in chatroom."""
        try:
            self.show_toast(f"Voice error: {error_message}")
        except Exception as e:
            print(f"❌ Error handling chatroom voice error: {e}")
        finally:
            self._reset_chatroom_voice_button()



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

            # Display user message first
            self._add_chat_message(message, "user")

            # Show loading dots while waiting for response
            self._show_llm_loading()

            # For now, use Ollama HTTP API since gRPC protobuf clients aren't generated
            # TODO: Replace with proper gRPC when llm_pb2 clients are generated
            response = self._send_to_ollama_http(message)

            # Hide loading dots
            self._hide_llm_loading()

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
        """Add a chat message to the messages area using ChatBubble component."""
        from datetime import datetime

        if not COMPONENTS_AVAILABLE:
            # Fallback to basic implementation if components not available
            self._add_chat_message_basic(message, sender_type)
            return

        # Determine sender name and alignment
        if sender_type == "user":
            sender = "You"
            alignment = "right"
            message_type = "default"
        elif sender_type == "assistant":
            sender = "Assistant"
            alignment = "left"
            message_type = "default"
        else:  # error
            sender = "System"
            alignment = "left"
            message_type = "error"

        # Create timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")

        # Create ChatBubble component
        chat_bubble = ChatBubble(
            message=message,
            sender=sender,
            timestamp=timestamp,
            alignment=alignment,
            message_type=message_type
        )

        # Connect to message click events for potential future features
        chat_bubble.connect('message-clicked', self._on_chat_message_clicked)

        # Add to messages container
        self._chatroom_messages_container.append(chat_bubble.get_widget())

        # Auto-scroll to bottom
        self._scroll_messages_to_bottom()

    def _add_chat_message_basic(self, message, sender_type):
        """Fallback basic chat message implementation."""
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

    def _on_chat_message_clicked(self, chat_bubble, message):
        """Handle chat message click events."""
        # Future feature: could show message details, copy, etc.
        print(f"Chat message clicked: {message[:50]}...")
        if self.session_logger:
            self.session_logger.log_gui_event("CHAT_MESSAGE_CLICKED", f"Message length: {len(message)}")

    def _show_llm_loading(self):
        """Show loading dots while waiting for LLM response."""
        if not COMPONENTS_AVAILABLE:
            return

        # Create loading dots if not exists
        if not self.llm_loading_dots:
            self.llm_loading_dots = LoadingDots(
                size="normal",
                speed="normal",
                color="primary"
            )

        # Add loading message with dots
        loading_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        loading_container.set_halign(Gtk.Align.CENTER)
        loading_container.set_margin_top(8)
        loading_container.set_margin_bottom(8)

        loading_label = Gtk.Label(label="Assistant is thinking")
        loading_label.add_css_class("chat-loading-label")
        loading_container.append(loading_label)
        loading_container.append(self.llm_loading_dots.get_widget())

        # Start animation
        self.llm_loading_dots.start_animation()

        # Add to messages container with special class for easy removal
        loading_container.add_css_class("llm-loading-indicator")
        self._chatroom_messages_container.append(loading_container)

        # Auto-scroll to bottom
        self._scroll_messages_to_bottom()

    def _hide_llm_loading(self):
        """Hide loading dots after LLM response."""
        if not COMPONENTS_AVAILABLE or not self.llm_loading_dots:
            return

        # Stop animation
        self.llm_loading_dots.stop_animation()

        # Find and remove loading indicator from messages container
        child = self._chatroom_messages_container.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            if child.has_css_class("llm-loading-indicator"):
                self._chatroom_messages_container.remove(child)
                break
            child = next_child

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
        """Create the Bluetooth tab content using extracted BluetoothView."""
        try:
            from .views.bluetooth_view import BluetoothView

            # Create bluetooth view
            self.bluetooth_view = BluetoothView(self)
            return self.bluetooth_view.create_content()

        except ImportError as e:
            print(f"⚠️ BluetoothView not available, using fallback: {e}")
            return self._create_bluetooth_fallback()
        except Exception as e:
            print(f"❌ Error creating bluetooth view: {e}")
            return self._create_bluetooth_fallback()

    def _create_bluetooth_fallback(self):
        """Fallback bluetooth implementation"""
        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        container.set_margin_top(16)
        container.set_margin_bottom(16)
        container.set_margin_start(16)
        container.set_margin_end(16)

        label = Gtk.Label(label="Bluetooth functionality temporarily unavailable")
        label.add_css_class("dim-label")
        container.append(label)

        return container

    def create_output_tab_content(self):
        """Create the Output tab content using extracted OutputView."""
        try:
            from .views.output_view import OutputView

            # Create output view
            self.output_view = OutputView(self)
            return self.output_view.create_content()

        except ImportError as e:
            print(f"⚠️ OutputView not available, using fallback: {e}")
            return self._create_output_fallback()
        except Exception as e:
            print(f"❌ Error creating output view: {e}")
            return self._create_output_fallback()

    def _create_output_fallback(self):
        """Fallback output implementation"""
        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        container.set_margin_top(16)
        container.set_margin_bottom(16)
        container.set_margin_start(16)
        container.set_margin_end(16)

        label = Gtk.Label(label="Audio output functionality temporarily unavailable")
        label.add_css_class("dim-label")
        container.append(label)

        return container

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
        self.set_accels_for_action("app.quit", ["<primary>q"])
        self.set_accels_for_action("app.preferences", ["<primary>comma"])

        # Create menu
        menu = Gio.Menu()
        menu.append("About Unhinged", "app.about")
        menu.append("Preferences", "app.preferences")
        menu.append("Quit", "app.quit")
        self.set_menubar(menu)
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

    def on_about_action(self, action, param):
        """Show about dialog"""
        about = Adw.AboutWindow(transient_for=self.window)
        about.set_application_name("Unhinged")
        about.set_application_icon("applications-graphics")
        about.set_developer_name("Unhinged Team")
        about.set_version("1.0.0")
        about.set_website("https://github.com/brl053/Unhinged")
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
        auto_start_row = Adw.ActionRow()
        auto_start_row.set_title("Auto-start Platform")
        auto_start_row.set_subtitle("Automatically start the platform when the application opens")

        auto_start_switch = Gtk.Switch()
        auto_start_switch.set_active(False)  # Default off
        auto_start_row.add_suffix(auto_start_switch)

        launch_group.add(auto_start_row)
        general_page.add(launch_group)
        prefs.add(general_page)

        prefs.present()

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

    def on_quit_action(self, action, param):
        """Quit application"""
        if self.running:
            self.on_stop_clicked(None)

        self.quit()

    def create_welcome_section(self):
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

        # Add loading dots for operations (initially hidden)
        if COMPONENTS_AVAILABLE:
            self.operation_loading_dots = LoadingDots(
                size="small",
                speed="normal",
                color="primary"
            )
            loading_row = Adw.ActionRow()
            loading_row.set_title("Processing")
            loading_row.add_suffix(self.operation_loading_dots.get_widget())
            loading_row.set_visible(False)  # Initially hidden
            self.operation_loading_row = loading_row
            group.add(loading_row)
        else:
            self.operation_loading_dots = None
            self.operation_loading_row = None
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
        """Handle start button click using PlatformHandler"""
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

        # Start platform using handler
        if hasattr(self, 'platform_handler') and self.platform_handler:
            import threading
            thread = threading.Thread(target=self.platform_handler.start_platform, daemon=True)
            thread.start()
        else:
            self.show_error_dialog("Platform Error", "Platform handler not available")

    def on_stop_clicked(self, button):
        """Handle stop button click using PlatformHandler"""
        if not self.running:
            return

        self.running = False
        self.start_button.set_sensitive(True)
        self.stop_button.set_sensitive(False)

        # Log GUI event
        if self.session_logger:
            self.session_logger.log_gui_event("STOP_BUTTON_CLICKED", "User clicked stop button")

        # Stop platform using handler
        if hasattr(self, 'platform_handler') and self.platform_handler:
            self.platform_handler.stop_platform()
        else:
            self.append_log("⚠️ Platform handler not available")
            self.update_status("Stopped", 0)

    def on_record_voice_clicked(self, button):
        """Handle voice recording button click"""
        try:
            # Log the event
            if hasattr(self, 'session_logger') and self.session_logger:
                self.session_logger.log_gui_event("VOICE_RECORD_CLICKED", "User clicked voice record button")

            # Use new AudioHandler if available
            if ARCHITECTURE_AVAILABLE and self.audio_handler:
                # Check if already busy
                if self.audio_handler.is_busy:
                    self.show_toast("Audio recording already in progress")
                    return

                # Start recording with new handler
                self.audio_handler.start_recording()
            else:
                # Fallback to legacy method
                # Check if voice service is available
                if not self.is_voice_service_available():
                    self.show_toast("Voice service not available")
                    return

                # Disable button during recording
                self.record_button.set_sensitive(False)
                self.record_button.set_label("Recording...")

                # Change icon to recording indicator
                if COMPONENTS_AVAILABLE and hasattr(self.record_button, 'set_icon_name'):
                    self.record_button.set_icon_name("media-record")

                # Show recording status
                self.show_toast("Recording for 10 seconds...")

                # Start recording in background thread
                import threading
                thread = threading.Thread(target=self.record_and_transcribe_voice, daemon=True)
                thread.start()

        except Exception as e:
            print(f"❌ Voice recording error: {e}")
            if hasattr(self, 'session_logger') and self.session_logger:
                self.session_logger.log_gui_event("VOICE_RECORD_ERROR", f"Voice recording failed: {e}")

            # Reset button state
            if hasattr(self, 'record_button'):
                self.record_button.set_sensitive(True)
                self.record_button.set_label("Record Voice")

            # Show user-friendly error
            if ARCHITECTURE_AVAILABLE:
                user_message = get_user_friendly_message(e)
                self.show_toast(user_message)
            else:
                self.show_toast(f"Recording failed: {e}")







    def _show_operation_loading(self, title="Processing"):
        """Show loading dots for long operations."""
        if self.operation_loading_dots and self.operation_loading_row:
            self.operation_loading_row.set_title(title)
            self.operation_loading_row.set_visible(True)
            self.operation_loading_dots.start_animation()

    def _hide_operation_loading(self):
        """Hide loading dots after operation completes."""
        if self.operation_loading_dots and self.operation_loading_row:
            self.operation_loading_dots.stop_animation()
            self.operation_loading_row.set_visible(False)













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
        """Show toast notification with visual stack management"""
        def show_toast_ui():
            # Create new toast
            toast = Adw.Toast.new(message)

            # Manage toast stack - remove oldest if at max capacity
            if len(self.toast_stack) >= self.max_toast_stack:
                # Remove oldest toast from stack
                oldest_toast = self.toast_stack.pop(0)
                # Note: Adwaita automatically manages toast removal, we just track them

            # Add to stack tracking
            self.toast_stack.append(toast)

            # Set timeout based on position in stack
            stack_position = len(self.toast_stack) - 1
            if stack_position == 0:  # Most recent (top)
                toast.set_timeout(1)  # 1s for top toast
            elif stack_position == 1:  # Second toast
                toast.set_timeout(2)  # 2s for second toast
            else:  # Third toast (standard)
                toast.set_timeout(timeout)  # Standard duration

            # Add toast to overlay
            self.toast_overlay.add_toast(toast)

            # Clean up stack tracking when toast is dismissed
            def on_toast_dismissed():
                if toast in self.toast_stack:
                    self.toast_stack.remove(toast)

            # Connect to toast dismissed signal if available
            try:
                toast.connect("dismissed", lambda t: on_toast_dismissed())
            except:
                # Fallback: use timeout to clean up stack
                GLib.timeout_add_seconds(max(timeout, 3), lambda: on_toast_dismissed() or False)

        GLib.idle_add(show_toast_ui)

    def _reset_buttons(self):
        """Reset button states"""
        self.start_button.set_sensitive(True)
        self.stop_button.set_sensitive(False)
        return False

    def is_voice_service_available(self):
        """Check if the voice service is available"""
        if ARCHITECTURE_AVAILABLE:
            # Use new service connector
            return service_connector.check_service_health('speech_to_text')
        else:
            # Fallback to old method
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex(('localhost', 1191))
                sock.close()
                return result == 0
            except Exception:
                return False



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

            # Record 10 seconds of audio with Whisper-optimal settings
            cmd = [
                'arecord',
                '-D', 'pipewire',     # Use PipeWire audio system
                '-f', 'S16_LE',       # 16-bit signed little-endian (optimal for Whisper)
                '-r', '16000',        # 16kHz sample rate (optimal for Whisper)
                '-c', '1',            # Mono (optimal for Whisper)
                '-t', 'wav',          # WAV format
                '-d', '10',           # 10 seconds
                str(temp_audio_file)
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)

            if result.returncode != 0:
                raise Exception(f"Recording failed: {result.stderr}")

            # Critical fix: Wait for file system to flush the WAV file
            time.sleep(0.5)  # Allow file system buffer to flush

            # Verify file exists and has content
            if temp_audio_file.exists():
                file_size = temp_audio_file.stat().st_size
                print(f"🔍 Debug: Status tab WAV file size: {file_size} bytes")

                # Check if file is too small (WAV header is at least 44 bytes)
                if file_size < 44:
                    raise Exception(f"WAV file too small ({file_size} bytes) - recording may have failed")
            else:
                raise Exception("Recording file not found after recording completed")

            # Transcribe using gRPC service
            transcript = self.transcribe_audio_file(temp_audio_file)

            # For OS chatroom, just add the transcript to the chat
            if transcript and transcript.strip():
                GLib.idle_add(self._add_voice_transcript_to_chat, transcript.strip())
            else:
                GLib.idle_add(self.show_toast, "No speech detected in recording")

            # Clean up
            try:
                temp_audio_file.unlink()
            except:
                pass

        except Exception as e:
            print(f"❌ Voice recording and transcription error: {e}")
            GLib.idle_add(self.show_toast, f"Voice recording failed: {e}")
        finally:
            # Reset button state
            GLib.idle_add(self._reset_voice_button_state)

    def _add_voice_transcript_to_chat(self, transcript):
        """Add voice transcript to the OS chatroom"""
        try:
            # Use the new ChatroomView if available
            if hasattr(self, 'chatroom_view') and self.chatroom_view:
                self.chatroom_view.add_voice_transcript(transcript)
            else:
                # Fallback for legacy implementation
                if hasattr(self, 'chat_input') and self.chat_input:
                    current_text = self.chat_input.get_text()
                    if current_text.strip():
                        # Append to existing text
                        self.chat_input.set_text(f"{current_text} {transcript}")
                    else:
                        # Set as new text
                        self.chat_input.set_text(transcript)

                    # Position cursor at end
                    self.chat_input.set_position(-1)

                    self.show_toast("Voice transcript added to chat")
                else:
                    self.show_toast(f"Transcript: {transcript}")

        except Exception as e:
            print(f"❌ Error adding transcript to chat: {e}")
            self.show_toast(f"Transcript: {transcript}")

    def _reset_voice_button_state(self):
        """Reset voice button to normal state"""
        try:
            if hasattr(self, 'record_button'):
                self.record_button.set_sensitive(True)
                self.record_button.set_label("Record Voice")

                # Reset icon back to microphone
                if COMPONENTS_AVAILABLE and hasattr(self.record_button, 'set_icon_name'):
                    self.record_button.set_icon_name("audio-input-microphone-symbolic")
        except Exception as e:
            print(f"❌ Error resetting voice button: {e}")

    def transcribe_audio_file(self, audio_file):
        """Transcribe audio file using the speech-to-text service"""
        if ARCHITECTURE_AVAILABLE:
            # Use new service connector
            try:
                return service_connector.transcribe_audio(Path(audio_file))
            except Exception as e:
                # Convert to user-friendly message
                user_message = get_user_friendly_message(e)
                raise Exception(user_message)
        else:
            # Fallback to old method
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

                # Connect to speech-to-text service with large message support
                MAX_MESSAGE_SIZE = 1024 * 1024 * 1024  # 1GB
                options = [
                    ('grpc.max_receive_message_length', MAX_MESSAGE_SIZE),
                    ('grpc.max_send_message_length', MAX_MESSAGE_SIZE),
                ]
                channel = grpc.insecure_channel('localhost:1191', options=options)
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







    def _on_recording_state_changed(self, state: 'RecordingState') -> None:
        """Handle recording state changes from AudioHandler"""
        try:
            if not ARCHITECTURE_AVAILABLE:
                return

            # Update UI based on recording state
            if state == RecordingState.RECORDING:
                self.show_toast("Recording audio...")
                if hasattr(self, 'record_button'):
                    self.record_button.set_sensitive(False)
                    self.record_button.set_label("Recording...")

            elif state == RecordingState.PROCESSING:
                self.show_toast("Processing audio...")
                if hasattr(self, 'record_button'):
                    self.record_button.set_label("Processing...")

            elif state == RecordingState.IDLE:
                if hasattr(self, 'record_button'):
                    self.record_button.set_sensitive(True)
                    self.record_button.set_label("Record Voice")

            elif state == RecordingState.ERROR:
                if hasattr(self, 'record_button'):
                    self.record_button.set_sensitive(True)
                    self.record_button.set_label("Record Voice")

        except Exception as e:
            print(f"❌ Error handling recording state change: {e}")

    def _on_transcription_result(self, transcript: str) -> None:
        """Handle transcription result from AudioHandler"""
        try:
            if transcript and transcript.strip():
                self._add_voice_transcript_to_chat(transcript.strip())
                self.show_toast("Voice transcription complete!")
            else:
                self.show_toast("No speech detected in recording")
        except Exception as e:
            print(f"❌ Error handling transcription result: {e}")

    def _on_audio_error(self, error: Exception) -> None:
        """Handle audio errors from AudioHandler"""
        try:
            if ARCHITECTURE_AVAILABLE:
                user_message = get_user_friendly_message(error)
            else:
                user_message = str(error)

            self.show_toast(f"Audio error: {user_message}")
            print(f"❌ Audio error: {error}")
        except Exception as e:
            print(f"❌ Error handling audio error: {e}")
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
