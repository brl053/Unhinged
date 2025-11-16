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

import contextlib
import os
import sys
from pathlib import Path

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, GLib, Gtk

# Add virtual environment packages to path for gRPC support
# Calculate project root correctly (control/gtk4_gui/desktop_app.py -> project root)
project_root = Path(__file__).parent.parent.parent

# Use build/python/venv as single source of truth for all dependencies
# See: build/requirements-unified.txt and LLM_MASTER_PROMPT.md
venv_packages = project_root / "build" / "python" / "venv" / "lib" / "python3.12" / "site-packages"
protobuf_clients = project_root / "generated" / "python" / "clients"

if venv_packages.exists():
    sys.path.insert(0, str(venv_packages))
if protobuf_clients.exists():
    sys.path.insert(0, str(protobuf_clients))

# Import design system
from ..design_system import load_design_system_css

# Import new architecture components
try:
    try:
        from ..config import (
            log_configuration,
            validate_all_services,
        )
        from ..handlers.audio_handler import AudioHandler
    except ImportError:
        from config import (
            log_configuration,
            validate_all_services,
        )
        from handlers.audio_handler import AudioHandler
    ARCHITECTURE_AVAILABLE = True
except ImportError:
    ARCHITECTURE_AVAILABLE = False

# Import desktop app modules
from .handlers import RecordingControl, RecordingHandlers
from .tabs import TabContentFactory
from .ui import UIUtilities

# Import component library
try:
    sys.path.append(str(Path(__file__).parent))
    COMPONENTS_AVAILABLE = True
except ImportError:
    COMPONENTS_AVAILABLE = False

# Import system information collection
try:
    SYSTEM_INFO_AVAILABLE = True
except ImportError:
    SYSTEM_INFO_AVAILABLE = False

# Import session logging from event framework (optional)
SESSION_LOGGING_AVAILABLE = False
try:
    # Try multiple possible paths for the event framework
    # app.py is at: /project_root/control/gtk4_gui/desktop_app/app.py
    # So we need to go up 4 levels to get to project_root
    event_paths = [
        str(Path(__file__).parent.parent.parent.parent / "libs" / "event-framework" / "python" / "src"),
        str(Path(__file__).parent.parent.parent / "libs" / "event-framework" / "python" / "src"),
        str(
            Path(__file__).parent.parent.parent.parent
            / "build"
            / "python"
            / "venv"
            / "lib"
            / "python3.12"
            / "site-packages"
        ),
    ]

    for path in event_paths:
        if Path(path).exists():
            sys.path.append(path)
            break

    from events import GUIOutputCapture, create_gui_session_logger

    SESSION_LOGGING_AVAILABLE = True
except ImportError:
    # Session logging is optional - continue without it
    SESSION_LOGGING_AVAILABLE = False

# Simple approach: Use control modules as scripts (academic exercise)
CONTROL_MODULES_AVAILABLE = True


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
        super().__init__(application_id="com.unhinged.platform.gtk4")
        # app.py is at: /project_root/control/gtk4_gui/desktop_app/app.py
        # So we need to go up 4 levels to get to project_root
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.window = None
        # UI elements moved to StatusView
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
        self.dev_mode = os.environ.get("DEV_MODE", "0") == "1"

        # Initialize session logging (optional)
        self._init_session_logging()

        # Control module availability
        self.control_available = CONTROL_MODULES_AVAILABLE

        # Initialize new architecture components
        self._init_audio_handler_startup()

        # Design system CSS provider (for delayed loading)
        self._pending_css_provider = None

        # Initialize controllers
        self._init_controllers()

    def _init_session_logging(self):
        """Initialize session logging."""
        self.session_logger = None
        self.output_capture = None
        if SESSION_LOGGING_AVAILABLE:
            try:
                self.session_logger = create_gui_session_logger(self.project_root)
                self.output_capture = GUIOutputCapture(self.session_logger, self._gui_log_callback)
                self.session_logger.log_session_event("APP_INIT", "GTK4 desktop app with system info integration")
            except Exception:
                self.session_logger = None
                self.output_capture = None

    def _init_audio_handler_startup(self):
        """Initialize audio handler at startup."""
        self.audio_handler = None
        if ARCHITECTURE_AVAILABLE:
            try:
                self.audio_handler = AudioHandler()
                # Only set result_callback if FormInput is NOT available
                # FormInput handles transcription via event bus subscription
                # This prevents duplicate transcripts
                result_callback = None if COMPONENTS_AVAILABLE else self._on_transcription_result

                self.audio_handler.set_callbacks(
                    state_callback=self._on_recording_state_changed,
                    result_callback=result_callback,
                    error_callback=self._on_audio_error,
                )

                if self.dev_mode:
                    log_configuration()

                if not validate_all_services():
                    pass
            except Exception:
                self.audio_handler = None

    def _init_controllers(self):
        """Initialize all controllers"""
        try:
            try:
                from .controllers import (
                    ActionController,
                    ContentController,
                    UIController,
                )
            except ImportError:
                # Fallback for when running as script
                from controllers import (
                    ActionController,
                    ContentController,
                    UIController,
                )

            self.ui_controller = UIController(self)
            self.content_controller = ContentController(self)
            self.action_controller = ActionController(self)
        except Exception:
            self.ui_controller = None
            self.content_controller = None
            self.action_controller = None

    def _load_design_system_css(self):
        """Load design system CSS files"""
        if os.environ.get("SKIP_DESIGN_SYSTEM", "0") == "1":
            print("ℹ️ Skipping design system CSS loading")
            return

        with contextlib.suppress(Exception):
            # CSS loading is optional
            load_design_system_css(self)

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
                    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
                )
                self._pending_css_provider = None

        # Log application activation
        if self.session_logger:
            self.session_logger.log_gui_event("APP_ACTIVATE", "Main window created and presented")

        self.window.present()

    def create_main_window(self):
        """Create main application window using UIController"""
        if hasattr(self, "ui_controller") and self.ui_controller:
            # Set title based on mode
            if self.dev_mode:
                pass
            else:
                pass

            # Toast stack management
            self.toast_stack = []
            self.max_toast_stack = 3

            # Setup actions
            if hasattr(self, "action_controller") and self.action_controller:
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
        if hasattr(self, "ui_controller") and self.ui_controller:
            self.ui_controller.create_tab_navigation()
        else:
            # Fallback: create basic navigation
            self.content_stack = Gtk.Stack()
            self.toast_overlay.set_child(self.content_stack)

    # Main tab removed - functionality migrated to enhanced Status tab

    def create_status_tab_content(self):
        """Delegate to TabContentFactory."""
        return TabContentFactory.create_status_tab(self)

    def create_system_info_tab_content(self):
        """Delegate to TabContentFactory."""
        return TabContentFactory.create_system_info_tab(self)

    def create_processes_tab_content(self):
        """Delegate to TabContentFactory."""
        return TabContentFactory.create_processes_tab(self)

    def create_input_tab_content(self):
        """Delegate to TabContentFactory."""
        return TabContentFactory.create_input_tab(self)

    def create_chatroom_tab_content(self):
        """Delegate to TabContentFactory."""
        content = TabContentFactory.create_chatroom_tab(self)
        GLib.idle_add(self._auto_create_session)
        return content

    def _auto_create_session(self):
        """Automatically create a session on app launch (headless)"""
        try:
            if (
                hasattr(self, "chatroom_view")
                and self.chatroom_view
                and self.chatroom_view._session_status == "no_session"
            ):
                # Check if session already exists
                self.chatroom_view._create_new_session()
                if self.session_logger:
                    self.session_logger.log_gui_event(
                        "AUTO_SESSION_CREATED",
                        "Session automatically created on app launch (headless)",
                    )
        except Exception as e:
            print(f"⚠️ Auto-session creation failed: {e}")
            if self.session_logger:
                self.session_logger.log_gui_event(
                    "AUTO_SESSION_FAILED",
                    f"Auto-session creation failed: {e}",
                )
        return False  # Don't repeat

    def _start_toggle_recording(self):
        """Delegate to RecordingControl."""
        RecordingControl.start_recording(self)

    def _init_audio_handler(self):
        """Delegate to RecordingControl."""
        RecordingControl.init_audio_handler(self)

    def _init_platform_handler(self):
        """Initialize the PlatformHandler with callbacks"""
        try:
            from .handlers.platform_handler import PlatformHandler

            self.platform_handler = PlatformHandler(self.project_root)
            self.platform_handler.set_callbacks(
                status_callback=self.update_status,
                log_callback=self.append_log,
                error_callback=self.show_error_dialog,
            )

        except Exception as e:
            print(f"⚠️ Failed to initialize PlatformHandler: {e}")
            self.platform_handler = None

    def _on_recording_state_changed(self, state):
        """Delegate to RecordingHandlers."""
        RecordingHandlers.on_recording_state_changed(self, state)

    def _on_transcription_result(self, transcript):
        """Delegate to RecordingHandlers."""
        RecordingHandlers.on_transcription_result(self, transcript)

    def _on_audio_error(self, error_data):
        """Delegate to RecordingHandlers."""
        RecordingHandlers.on_audio_error(self, error_data)

    def _stop_toggle_recording(self):
        """Delegate to RecordingControl."""
        RecordingControl.stop_recording(self)

    def create_bluetooth_tab_content(self):
        """Delegate to TabContentFactory."""
        return TabContentFactory.create_bluetooth_tab(self)

    def create_output_tab_content(self):
        """Delegate to TabContentFactory."""
        return TabContentFactory.create_output_tab(self)

    def create_usb_tab_content(self):
        """Delegate to TabContentFactory."""
        return TabContentFactory.create_usb_tab(self)

    def create_graph_tab_content(self):
        """Delegate to TabContentFactory."""
        return TabContentFactory.create_graph_tab(self)

    def create_documents_tab_content(self):
        """Delegate to TabContentFactory."""
        return TabContentFactory.create_documents_tab(self)

    def create_gpu_drivers_tab_content(self):
        """Delegate to TabContentFactory."""
        return TabContentFactory.create_gpu_tab(self)

    def setup_actions(self):
        """Setup application actions using ActionController"""
        if hasattr(self, "action_controller") and self.action_controller:
            self.action_controller.setup_actions()
        else:
            print("⚠️ Action controller not available")

    def on_about_action(self, action, param):
        """Show about dialog using ActionController"""
        if hasattr(self, "action_controller") and self.action_controller:
            self.action_controller.on_about_action(action, param)

    def on_preferences_action(self, action, param):
        """Show preferences dialog using ActionController"""
        if hasattr(self, "action_controller") and self.action_controller:
            self.action_controller.on_preferences_action(action, param)

    def on_quit_action(self, action, param):
        """Quit application using ActionController"""
        if hasattr(self, "action_controller") and self.action_controller:
            self.action_controller.on_quit_action(action, param)
        else:
            self.quit()

    def update_status(self, message, progress=None):
        """Delegate to UIUtilities."""
        UIUtilities.update_status(self, message, progress)

    def append_log(self, message):
        """Delegate to UIUtilities."""
        UIUtilities.append_log(self, message)

    def _gui_log_callback(self, message):
        """Callback for GUI output capture - this is called by the session logger"""
        pass

    def on_start_clicked(self, button):
        """Handle start button click using ActionController"""
        if hasattr(self, "action_controller") and self.action_controller:
            self.action_controller.on_start_clicked(button)
        else:
            self.show_toast("Action controller not available")

    def on_stop_clicked(self, button):
        """Handle stop button click using ActionController"""
        if hasattr(self, "action_controller") and self.action_controller:
            self.action_controller.on_stop_clicked(button)
        else:
            self.show_toast("Action controller not available")

    def on_record_voice_clicked(self, button):
        """Handle voice recording button click using ActionController"""
        if hasattr(self, "action_controller") and self.action_controller:
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
        """Delegate to UIUtilities."""
        UIUtilities.show_error_dialog(self, title, message)

    def show_toast(self, message, timeout=3):
        """Delegate to UIUtilities."""
        UIUtilities.show_toast(self, message, timeout)

    def _reset_buttons(self):
        """Delegate to UIUtilities."""
        return UIUtilities.reset_buttons(self)

    def is_voice_service_available(self):
        """Check if voice service is available using AudioHandler"""
        # AudioHandler handles service availability
        return hasattr(self, "audio_handler") and bool(self.audio_handler)

    def _on_set_default_input_device(self, button, device):
        """Set default input device using ActionController"""
        if hasattr(self, "action_controller") and self.action_controller:
            self.action_controller.on_set_default_input_device(button, device)
        else:
            print("⚠️ Action controller not available")


def main():
    """Main function"""
    app = UnhingedDesktopApp()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
