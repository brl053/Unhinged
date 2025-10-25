
# Initialize GUI event logger
gui_logger = create_gui_logger("unhinged-application", "1.0.0")

"""
@llm-type control-system
@llm-legend application.py - system control component
@llm-key Core functionality for application
@llm-map Part of the Unhinged system architecture
@llm-axiom Maintains system independence and architectural compliance
@llm-contract Provides standardized interface for system integration
@llm-token application: system control component
"""
"""
🎛️ Main Application Class

Core application framework for the Unhinged Control Center.
Manages tools, theming, and global application state.
"""

import gi
from unhinged_events import create_gui_logger
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('Gdk', '4.0')

from gi.repository import Gtk, Adw, GLib, Gio
import sys
from pathlib import Path

from .tool_manager import ToolManager
from .theme_manager import ThemeManager


class UnhingedApplication(Adw.Application):
    """
    Main Unhinged Control Center application.

    Manages multiple tools in a tabbed interface:
    - 🔧 API Development Tool
    - 🏥 System Health Monitor
    - 📋 Log Viewer
    - 🚀 Service Manager
    - 📁 File Browser
    - 💬 Chat Tool
    - ⚙️ Settings
    """
    
    def __init__(self, launched_by_ai=False):
        super().__init__(
            application_id="com.unhinged.controlcenter",
            flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE
        )

        # Project root for file operations
        self.project_root = Path(__file__).parent.parent.parent.parent

        # Core managers
        self.tool_manager = ToolManager(self.project_root)
        self.theme_manager = ThemeManager()

        # Main window reference
        self.main_window = None
        self.launched_by_ai = launched_by_ai


    def do_command_line(self, command_line):
        """Handle command line arguments and ensure single instance"""
        gui_logger.info(" Command line received - checking for existing instance...", {"event_type": "activation"})

        # If we already have a window, just present it
        if self.main_window:
            self.main_window.present()
            return 0

        # Otherwise activate normally
        self.activate()
        return 0

    def do_activate(self):
        """Application activation - create and show main window"""
        gui_logger.info(" Application activating...", {"event_type": "activation"})

        if not self.main_window:
            gui_logger.info(" Creating mobile-first control center window...", {"event_type": "initialization"})
            from ..main_window import MobileControlCenterWindow

            self.main_window = MobileControlCenterWindow(
                application=self,
                project_root=self.project_root,
                tool_manager=self.tool_manager
            )

            # Show AI launch indicator if launched by AI
            if self.launched_by_ai:
                GLib.timeout_add(500, self._show_ai_launch_indicator)

        gui_logger.info(" Presenting control center...", {"event_type": "ui_display"})
        self.main_window.present()
        gui_logger.info(" Unhinged Control Center ready!", {"status": "success"})

    def _show_ai_launch_indicator(self):
        """Show AI launch indicator in the GUI"""
        if self.main_window and hasattr(self.main_window, '_add_ai_launch_indicator'):
            self.main_window._add_ai_launch_indicator()
        return False  # Don't repeat

    def do_startup(self):
        """Application startup - set up global resources"""
        gui_logger.debug(" Application startup...", {"event_type": "configuration"})
        Adw.Application.do_startup(self)
        
        gui_logger.info(" Setting up theming...", {"event_type": "theming"})
        self.theme_manager.setup_theming()
        
        gui_logger.debug(" Registering tools...", {"event_type": "configuration"})
        self._register_tools()
        
        self._setup_shortcuts()
        
        gui_logger.info(" Application startup complete", {"status": "success"})
    
    def _register_tools(self):
        """Register all available tools"""
        # Import and register tools
        try:
            from ..tools.api_dev.tool import APIDevTool
            self.tool_manager.register_tool(APIDevTool())
            gui_logger.info(" Registered API Development Tool", {"status": "success"})
        except ImportError as e:
            gui_logger.warn(f" Failed to load API Dev Tool: {e}")

        try:
            from ..tools.system_monitor.tool import SystemMonitorTool
            self.tool_manager.register_tool(SystemMonitorTool())
            gui_logger.info(" Registered System Monitor Tool", {"status": "success"})
        except ImportError as e:
            gui_logger.warn(f" Failed to load System Monitor Tool: {e}")

        try:
            from ..tools.log_viewer.tool import LogViewerTool
            self.tool_manager.register_tool(LogViewerTool())
            gui_logger.info(" Registered Log Viewer Tool", {"status": "success"})
        except ImportError as e:
            gui_logger.warn(f" Failed to load Log Viewer Tool: {e}")

        try:
            from ..tools.service_manager.tool import ServiceManagerTool
            self.tool_manager.register_tool(ServiceManagerTool())
            gui_logger.info(" Registered Service Manager Tool", {"status": "success"})
        except ImportError as e:
            gui_logger.warn(f" Failed to load Service Manager Tool: {e}")

        try:
            from ..tools.file_browser.tool import FileBrowserTool
            self.tool_manager.register_tool(FileBrowserTool())
            gui_logger.info(" Registered File Browser Tool", {"status": "success"})
        except ImportError as e:
            gui_logger.warn(f" Failed to load File Browser Tool: {e}")

        try:
            from ..tools.chat.tool import ChatTool
            self.tool_manager.register_tool(ChatTool())
            gui_logger.info(" Registered Chat Tool", {"status": "success"})
        except ImportError as e:
            gui_logger.warn(f" Failed to load Chat Tool: {e}")

    
    def _setup_shortcuts(self):
        """Set up application keyboard shortcuts"""
        # Ctrl+Q to quit
        quit_action = Gio.SimpleAction.new("quit", None)
        quit_action.connect("activate", lambda *args: self.quit())
        self.add_action(quit_action)
        self.set_accels_for_action("app.quit", ["<Ctrl>q"])
        
        # Ctrl+1-9 for tool switching
        for i in range(1, 10):
            action_name = f"switch-tool-{i}"
            action = Gio.SimpleAction.new(action_name, None)
            action.connect("activate", self._on_switch_tool, i-1)
            self.add_action(action)
            self.set_accels_for_action(f"app.{action_name}", [f"<Ctrl>{i}"])
        
        # F11 for fullscreen
        fullscreen_action = Gio.SimpleAction.new("toggle-fullscreen", None)
        fullscreen_action.connect("activate", self._on_toggle_fullscreen)
        self.add_action(fullscreen_action)
        self.set_accels_for_action("app.toggle-fullscreen", ["F11"])
        
        # Ctrl+Shift+I for inspector (debug)
        inspector_action = Gio.SimpleAction.new("toggle-inspector", None)
        inspector_action.connect("activate", self._on_toggle_inspector)
        self.add_action(inspector_action)
        self.set_accels_for_action("app.toggle-inspector", ["<Ctrl><Shift>i"])
    
    def _on_switch_tool(self, action, param, tool_index):
        """Handle tool switching shortcut"""
        if self.main_window:
            self.main_window.switch_to_tool(tool_index)
    
    def _on_toggle_fullscreen(self, action, param):
        """Handle fullscreen toggle"""
        if self.main_window:
            if self.main_window.is_fullscreen():
                self.main_window.unfullscreen()
            else:
                self.main_window.fullscreen()
    
    def _on_toggle_inspector(self, action, param):
        """Handle GTK inspector toggle"""
        Gtk.Window.set_interactive_debugging(True)
    
    def get_tool_manager(self):
        """Get the tool manager instance"""
        return self.tool_manager
    
    def get_theme_manager(self):
        """Get the theme manager instance"""
        return self.theme_manager


def run_control_center(launched_by_ai=False):
    """
    Entry point for the Unhinged Control Center.

    Replaces the single-purpose API tool with a multi-tool application.
    """
    gui_logger.info(" Starting Unhinged Control Center...", {"event_type": "startup"})

    # Check if launched by AI assistant
    if launched_by_ai:
        pass

    app = UnhingedApplication(launched_by_ai=launched_by_ai)


    # Filter out our custom arguments that GTK doesn't understand
    filtered_argv = [arg for arg in sys.argv if not arg.startswith('--launched-by-ai')]

    exit_code = app.run(filtered_argv)
    return exit_code
