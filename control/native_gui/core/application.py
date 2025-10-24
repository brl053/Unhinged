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
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('Gdk', '4.0')

from gi.repository import Gtk, Adw, GLib, Gio, Gdk
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

        print("🎛️ Unhinged Control Center initialized")

    def do_command_line(self, command_line):
        """Handle command line arguments and ensure single instance"""
        print("🎯 Command line received - checking for existing instance...")

        # If we already have a window, just present it
        if self.main_window:
            print("🔄 Existing instance found - presenting window...")
            self.main_window.present()
            return 0

        # Otherwise activate normally
        self.activate()
        return 0

    def do_activate(self):
        """Application activation - create and show main window"""
        print("🎯 Application activating...")

        if not self.main_window:
            print("🏗️ Creating mobile-first control center window...")
            from ..main_window import MobileControlCenterWindow

            self.main_window = MobileControlCenterWindow(
                application=self,
                project_root=self.project_root,
                tool_manager=self.tool_manager
            )

            # Show AI launch indicator if launched by AI
            if self.launched_by_ai:
                print("🤖 Adding AI launch indicator...")
                GLib.timeout_add(500, self._show_ai_launch_indicator)

        print("🖼️ Presenting control center...")
        self.main_window.present()
        print("✅ Unhinged Control Center ready!")

    def _show_ai_launch_indicator(self):
        """Show AI launch indicator in the GUI"""
        if self.main_window and hasattr(self.main_window, '_add_ai_launch_indicator'):
            self.main_window._add_ai_launch_indicator()
        return False  # Don't repeat

    def do_startup(self):
        """Application startup - set up global resources"""
        print("🔧 Application startup...")
        Adw.Application.do_startup(self)
        
        print("🎨 Setting up theming...")
        self.theme_manager.setup_theming()
        
        print("🔧 Registering tools...")
        self._register_tools()
        
        print("⌨️ Setting up shortcuts...")
        self._setup_shortcuts()
        
        print("✅ Application startup complete")
    
    def _register_tools(self):
        """Register all available tools"""
        # Import and register tools
        try:
            from ..tools.api_dev.tool import APIDevTool
            self.tool_manager.register_tool(APIDevTool())
            print("✅ Registered API Development Tool")
        except ImportError as e:
            print(f"⚠️ Failed to load API Dev Tool: {e}")

        try:
            from ..tools.system_monitor.tool import SystemMonitorTool
            self.tool_manager.register_tool(SystemMonitorTool())
            print("✅ Registered System Monitor Tool")
        except ImportError as e:
            print(f"⚠️ Failed to load System Monitor Tool: {e}")

        try:
            from ..tools.log_viewer.tool import LogViewerTool
            self.tool_manager.register_tool(LogViewerTool())
            print("✅ Registered Log Viewer Tool")
        except ImportError as e:
            print(f"⚠️ Failed to load Log Viewer Tool: {e}")

        try:
            from ..tools.service_manager.tool import ServiceManagerTool
            self.tool_manager.register_tool(ServiceManagerTool())
            print("✅ Registered Service Manager Tool")
        except ImportError as e:
            print(f"⚠️ Failed to load Service Manager Tool: {e}")

        try:
            from ..tools.file_browser.tool import FileBrowserTool
            self.tool_manager.register_tool(FileBrowserTool())
            print("✅ Registered File Browser Tool")
        except ImportError as e:
            print(f"⚠️ Failed to load File Browser Tool: {e}")

        try:
            from ..tools.chat.tool import ChatTool
            self.tool_manager.register_tool(ChatTool())
            print("✅ Registered Chat Tool")
        except ImportError as e:
            print(f"⚠️ Failed to load Chat Tool: {e}")

        print(f"🔧 Total tools registered: {len(self.tool_manager.get_tools())}")
    
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
    print("🚀 Starting Unhinged Control Center...")
    print("💡 CULTURE: We are independent. We render natively. We depend on nothing.")
    print("🎛️ Multi-tool native application - maximum independence achieved.")

    # Check if launched by AI assistant
    if launched_by_ai:
        print("🤖 LAUNCHED BY AI ASSISTANT - You should see the mobile-first GUI window!")

    app = UnhingedApplication(launched_by_ai=launched_by_ai)
    print("📱 Created control center instance")

    print("🎬 Running application...")

    # Filter out our custom arguments that GTK doesn't understand
    filtered_argv = [arg for arg in sys.argv if not arg.startswith('--launched-by-ai')]

    exit_code = app.run(filtered_argv)
    print(f"🏁 Control center exited with code: {exit_code}")
    return exit_code
