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

        # Initialize controllers
        self._init_controllers()

    def _init_controllers(self):
        """Initialize all controllers"""
        try:
            from .controllers import UIController, ContentController, ActionController

            self.ui_controller = UIController(self)
            self.content_controller = ContentController(self)
            self.action_controller = ActionController(self)

            print("✅ Controllers initialized")
        except Exception as e:
            print(f"⚠️ Failed to initialize controllers: {e}")
            self.ui_controller = None
            self.content_controller = None
            self.action_controller = None

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
        """Create main application window using UIController"""
        if hasattr(self, 'ui_controller') and self.ui_controller:
            # Set title based on mode
            if self.dev_mode:
                title = "Unhinged - Development Mode"
            else:
                title = "Unhinged - Native Graphics Platform"

            # Toast stack management
            self.toast_stack = []
            self.max_toast_stack = 3

            # Setup actions
            if hasattr(self, 'action_controller') and self.action_controller:
                self.action_controller.setup_actions()

            return self.ui_controller.create_main_window()
        else:
            # Fallback implementation
            window = Adw.ApplicationWindow(application=self)
            window.set_title("Unhinged Platform")
            window.set_default_size(800, 600)
            return window

    def create_tab_navigation(self):
        """Create sidebar navigation using UIController"""
        if hasattr(self, 'ui_controller') and self.ui_controller:
            self.ui_controller.create_tab_navigation()
        else:
            # Fallback: create basic navigation
            self.content_stack = Gtk.Stack()
            self.toast_overlay.set_child(self.content_stack)



    def create_main_tab_content(self):
        """Create main tab content using ContentController"""
        if hasattr(self, 'content_controller') and self.content_controller:
            return self.content_controller.create_main_tab_content()
        else:
            # Fallback implementation
            container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
            label = Gtk.Label(label="Main content not available")
            container.append(label)
            return container

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
        """Handle start button click using ActionController"""
        if hasattr(self, 'action_controller') and self.action_controller:
            self.action_controller.on_start_clicked(button)
        else:
            self.show_toast("Action controller not available")

    def on_stop_clicked(self, button):
        """Handle stop button click using ActionController"""
        if hasattr(self, 'action_controller') and self.action_controller:
            self.action_controller.on_stop_clicked(button)
        else:
            self.show_toast("Action controller not available")

    def on_record_voice_clicked(self, button):
        """Handle voice recording button click using ActionController"""
        if hasattr(self, 'action_controller') and self.action_controller:
            self.action_controller.on_record_voice_clicked(button)
        else:
            self.show_toast("Action controller not available")







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
