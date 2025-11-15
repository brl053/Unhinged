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

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

import os
import sys
from pathlib import Path

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
from .design_system import load_design_system_css

# Import new architecture components
try:
    # Try relative imports first
    try:
        from .config import (
            log_configuration,
            validate_all_services,
        )
        from .handlers.audio_handler import AudioHandler
    except ImportError:
        # Fallback to absolute imports for script execution
        from config import (
            log_configuration,
            validate_all_services,
        )
        from handlers.audio_handler import AudioHandler
    ARCHITECTURE_AVAILABLE = True
except ImportError:
    ARCHITECTURE_AVAILABLE = False

# Import component library
try:
    sys.path.append(str(Path(__file__).parent))
    # Components are imported dynamically when needed
    COMPONENTS_AVAILABLE = True
except ImportError:
    COMPONENTS_AVAILABLE = False

# Import system information collection
try:
    # System info modules are imported dynamically when needed
    SYSTEM_INFO_AVAILABLE = True
except ImportError:
    SYSTEM_INFO_AVAILABLE = False

# Import session logging from event framework (optional)
SESSION_LOGGING_AVAILABLE = False
try:
    # Try multiple possible paths for the event framework
    event_paths = [
        str(Path(__file__).parent.parent.parent / "libs" / "event-framework" / "python" / "src"),
        str(Path(__file__).parent.parent / "libs" / "event-framework" / "python" / "src"),
        str(Path(__file__).parent.parent.parent / "build" / "python" / "venv" / "lib" / "python3.12" / "site-packages"),
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
        self.project_root = Path(__file__).parent.parent.parent  # Updated path
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
                    error_callback=self._on_audio_error,
                )

                # Log configuration for debugging
                if self.dev_mode:
                    log_configuration()

                # Validate service configuration
                if not validate_all_services():
                    pass  # Services not properly configured, continue anyway
            except Exception:
                self.audio_handler = None

        # Design system CSS provider (for delayed loading)
        self._pending_css_provider = None

        # Initialize controllers
        self._init_controllers()

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

        try:
            load_design_system_css(self)
        except Exception:
            pass  # CSS loading is optional

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
        """Create the status tab content using extracted StatusView."""
        try:
            from .views.status_view import StatusView

            self.status_view = StatusView(self)
            content = self.status_view.create_content()
            return content
        except Exception as e:
            print(f"❌ CRITICAL: Status creation failed: {e}")
            import traceback

            traceback.print_exc()
            raise

    def create_system_info_tab_content(self):
        """Create the system info tab content using extracted SystemInfoView"""
        try:
            from .views.system_view import SystemInfoView

            self.system_info_view = SystemInfoView(self)
            content = self.system_info_view.create_content()
            return content
        except Exception as e:
            print(f"❌ CRITICAL: System Info creation failed: {e}")
            import traceback

            traceback.print_exc()
            raise

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

    def _create_fallback(self, title: str):
        """Create a generic fallback widget for unavailable features"""
        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        container.set_margin_top(16)
        container.set_margin_bottom(16)
        container.set_margin_start(16)
        container.set_margin_end(16)

        label = Gtk.Label(label=f"{title} functionality temporarily unavailable")
        label.add_css_class("dim-label")
        container.append(label)

        return container

    def _create_processes_fallback(self):
        """Fallback processes implementation"""
        return self._create_fallback("Process monitoring")

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
        return self._create_fallback("Input")

    def create_chatroom_tab_content(self):
        """Create the OS Chatroom tab content using extracted ChatroomView"""
        try:
            from .views.chatroom_view import ChatroomView

            self.chatroom_view = ChatroomView(self)
            content = self.chatroom_view.create_content()

            # Automatically create a session on app launch (headless)
            # Schedule session creation after UI is ready
            GLib.idle_add(self._auto_create_session)

            return content
        except Exception as e:
            print(f"❌ CRITICAL: OS Chatroom creation failed: {e}")
            import traceback

            traceback.print_exc()
            raise

    def _auto_create_session(self):
        """Automatically create a session on app launch (headless)"""
        try:
            if hasattr(self, "chatroom_view") and self.chatroom_view:
                # Check if session already exists
                if self.chatroom_view._session_status == "no_session":
                    self.chatroom_view._create_new_session()
                    if self.session_logger:
                        self.session_logger.log_gui_event(
                            "AUTO_SESSION_CREATED",
                            "Session automatically created on app launch (headless)",
                        )
        except Exception:
            pass  # Auto-session creation failed, continue
        return False  # Don't repeat

    def _start_toggle_recording(self):
        """Start toggle recording using AudioHandler"""
        try:
            if not hasattr(self, "audio_handler"):
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
            from .handlers.audio_handler import AudioHandler

            self.audio_handler = AudioHandler()
            self.audio_handler.set_callbacks(
                state_callback=self._on_recording_state_changed,
                result_callback=self._on_transcription_result,
                error_callback=self._on_audio_error,
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
                error_callback=self.show_error_dialog,
            )

        except Exception as e:
            print(f"⚠️ Failed to initialize PlatformHandler: {e}")
            self.platform_handler = None

    def _on_recording_state_changed(self, state):
        """Handle recording state changes from AudioHandler"""
        try:
            if hasattr(self, "session_logger") and self.session_logger:
                self.session_logger.log_gui_event("RECORDING_STATE_CHANGED", f"Recording state: {state}")

            # Update UI based on state - minimal feedback
            if state.name == "RECORDING" or state.name == "PROCESSING":
                pass  # Visual feedback handled by button state
            elif state.name == "IDLE":
                pass  # Will be handled by result or error callback

        except Exception as e:
            print(f"❌ Recording state change error: {e}")

    def _on_transcription_result(self, transcript):
        """Handle transcription results from AudioHandler"""
        try:
            if transcript:
                # Route to chatroom if it's active
                if hasattr(self, "chatroom_view") and self.chatroom_view:
                    self.chatroom_view.add_voice_transcript(transcript)
                    # No toast needed - user can see transcript was added
                else:
                    # Fallback: show in toast
                    self.show_toast(f"Transcript: {transcript}")

                # Log successful transcription
                if hasattr(self, "session_logger") and self.session_logger:
                    self.session_logger.log_gui_event("TRANSCRIPTION_SUCCESS", f"Transcript: {transcript}")
            else:
                self.show_toast("No transcription received")

        except Exception as e:
            print(f"❌ Transcription result error: {e}")
            self.show_toast(f"Transcription error: {e}")

    def _on_audio_error(self, error_data):
        """Handle audio errors from AudioHandler

        Receives error_data dict with full diagnostic information:
        - error: string representation
        - type: exception class name
        - message: detailed message
        - device: audio device that failed
        - details: dict with stderr output and other context
        """
        try:
            # Handle both old string format and new dict format for backward compatibility
            if isinstance(error_data, dict):
                error_msg = error_data.get("error", "Unknown error")
                device = error_data.get("device", "unknown")
                details = error_data.get("details", {})
                stderr_output = details.get("arecord_stderr", "")

                # Build comprehensive error message
                if stderr_output:
                    # Include stderr for device/format errors
                    full_msg = f"Audio error on {device}: {error_msg}\n\nDetails: {stderr_output}"
                else:
                    full_msg = f"Audio error on {device}: {error_msg}"
            else:
                # Fallback for old string format
                full_msg = f"Audio error: {str(error_data)}"

            # Show user-friendly toast (truncated)
            toast_msg = full_msg.split("\n")[0][:100]  # First line, max 100 chars
            self.show_toast(toast_msg)

            # Log full diagnostic information to session
            if hasattr(self, "session_logger") and self.session_logger:
                self.session_logger.log_gui_event("AUDIO_ERROR", full_msg)

        except Exception as e:
            print(f"❌ Audio error handler error: {e}")

    def _stop_toggle_recording(self):
        """Stop toggle recording using AudioHandler"""
        try:
            if hasattr(self, "audio_handler") and self.audio_handler:
                self.audio_handler.stop_recording()
                self.show_toast("Processing recording...")

                if self.session_logger:
                    self.session_logger.log_gui_event("TOGGLE_RECORDING_STOP", "Stopped toggle recording")
            else:
                print("⚠️ AudioHandler not available")

        except Exception as e:
            print(f"❌ Stop toggle recording error: {e}")
            self.show_toast(f"Stop recording failed: {e}")

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
        return self._create_fallback("Bluetooth")

    def create_output_tab_content(self):
        """Create the Output tab content using extracted OutputView"""
        try:
            from .views.output_view import OutputView

            self.output_view = OutputView(self)
            return self.output_view.create_content()
        except Exception as e:
            print(f"❌ Error creating output view: {e}")
            return self._create_fallback("Audio output")

    def _create_output_fallback(self):
        """Fallback output implementation"""
        return self._create_fallback("Audio output")

    def create_usb_tab_content(self):
        """Create the USB tab content using extracted USBView"""
        try:
            from .views.usb_view import USBView

            self.usb_view = USBView(self)
            return self.usb_view.create_content()
        except Exception as e:
            print(f"❌ Error creating USB view: {e}")
            import traceback

            traceback.print_exc()
            return self._create_fallback("USB Devices")

    def create_graph_tab_content(self):
        """Create the Graph Editor tab content using GraphWorkspaceView"""
        try:
            from .views.graph_workspace_view import GraphWorkspaceView

            self.graph_workspace_view = GraphWorkspaceView(self)
            content = self.graph_workspace_view.create_content()

            # Load sample graph for demonstration
            self.graph_workspace_view.load_sample_graph()

            return content
        except Exception as e:
            print(f"❌ Error creating graph editor view: {e}")
            import traceback

            traceback.print_exc()
            return self._create_fallback("Graph Editor")

    def create_documents_tab_content(self):
        """Create the Documents tab content using DocumentWorkspaceView"""
        try:
            from .views.document_workspace_view import DocumentWorkspaceView

            self.document_workspace_view = DocumentWorkspaceView(self, document_type="document")
            return self.document_workspace_view.create_content()
        except Exception as e:
            print(f"❌ Error creating documents view: {e}")
            import traceback

            traceback.print_exc()
            return self._create_fallback("Documents")

    def create_gpu_drivers_tab_content(self):
        """Create the GPU tab content using GPUView"""
        try:
            from .views.gpu_view import GPUView

            self.gpu_view = GPUView(self)
            return self.gpu_view.create_content()
        except Exception as e:
            print(f"❌ Error creating GPU view: {e}")
            import traceback

            traceback.print_exc()
            return self._create_fallback("GPU")

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
        """Update status label and progress bar"""
        GLib.idle_add(self._update_status_ui, message, progress)

    def _update_status_ui(self, message, progress):
        """Update UI elements from main thread (now delegates to StatusView)"""
        # Delegate to StatusView if available
        if hasattr(self, "status_view") and self.status_view:
            self.status_view._update_platform_status(message, progress)

        # Log status change
        if self.session_logger:
            self.session_logger.log_status_change("Previous", message)

        return False

    def append_log(self, message):
        """Append message to log (now delegates to StatusView)"""
        GLib.idle_add(self._append_log_ui, message)

    def _append_log_ui(self, message):
        """Append to log from main thread (now delegates to StatusView)"""
        # Delegate to StatusView if available
        if hasattr(self, "status_view") and self.status_view:
            self.status_view._append_platform_log(message)

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
                self.toast_stack.pop(0)
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
        """Reset button states (now handled by StatusView)"""
        # Button state management now handled by StatusView
        if hasattr(self, "status_view") and self.status_view:
            if hasattr(self.status_view, "start_button") and self.status_view.start_button:
                self.status_view.start_button.set_sensitive(True)
            if hasattr(self.status_view, "stop_button") and self.status_view.stop_button:
                self.status_view.stop_button.set_sensitive(False)
        return False

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
