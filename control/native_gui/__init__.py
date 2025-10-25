
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent / "libs" / "event-framework" / "python" / "src"))

try:
    from unhinged_events import create_gui_logger
    # Initialize GUI event logger
    gui_logger = create_gui_logger("unhinged---init--", "1.0.0")
except ImportError:
    # Fallback to basic logging if event framework not available
    import logging
    gui_logger = logging.getLogger("unhinged---init--")

"""
@llm-type control-system
@llm-legend __init__.py - system control component
@llm-key Core functionality for __init__
@llm-map Part of the Unhinged system architecture
@llm-axiom Maintains system independence and architectural compliance
@llm-contract Provides standardized interface for system integration
@llm-token __init__: system control component
"""
"""
🔧 Native GTK GUI - Pure Python + GTK4 Implementation

No WebKit bullshit. No JavaScript. No HTML/CSS.
Pure native desktop application using GTK4 widgets.

Architecture:
- GTK4 for native widgets and rendering
- Cairo for custom graphics when needed
- Pango for rich text formatting
- Direct Python method calls (no HTTP bridge)
- Native system integration

Independence Culture: Maximum independence with zero web dependencies.
"""

import gi
from unhinged_events import create_gui_logger
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('Gdk', '4.0')

from gi.repository import Gtk, Adw, Gio
import sys
from pathlib import Path

from .core.application import run_control_center

# Legacy application class - replaced by core.application.UnhingedApplication
class UnhingedNativeApp(Adw.Application):
    """
    Main native GTK application class.
    
    Uses Adwaita for modern GNOME styling and GTK4 for widgets.
    No web technologies involved - pure native desktop app.
    """
    
    def __init__(self):
        super().__init__(
            application_id="ai.unhinged.native-gui",
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS
        )
        
        # Project root for file operations
        self.project_root = Path(__file__).parent.parent.parent
        
        # Main window reference
        self.main_window = None
    
    def do_activate(self):
        """Application activation - create and show main window"""
        gui_logger.info(" Application activating...", {"event_type": "activation"})

        if not self.main_window:
            gui_logger.info(" Creating main window...", {"event_type": "initialization"})
            self.main_window = MainWindow(
                application=self,
                project_root=self.project_root
            )

        gui_logger.info(" Presenting main window...", {"event_type": "ui_display"})
        self.main_window.present()
        gui_logger.info(" Main window should be visible now!", {"status": "success"})
    
    def do_startup(self):
        """Application startup - set up global resources"""
        gui_logger.debug(" Application startup...", {"event_type": "configuration"})
        Adw.Application.do_startup(self)

        gui_logger.info(" Setting up theming...", {"event_type": "theming"})
        # Set up application-wide CSS theming
        self._setup_theming()

        # Set up keyboard shortcuts
        self._setup_shortcuts()

        gui_logger.info(" Application startup complete", {"status": "success"})
    
    def _setup_theming(self):
        """Apply dark theme and custom styling"""
        # Force dark theme
        Adw.StyleManager.get_default().set_color_scheme(Adw.ColorScheme.FORCE_DARK)
        
        # Load custom CSS
        css_provider = Gtk.CssProvider()
        css_data = """
        .api-dev-window {
            background-color: #1e1e1e;
            color: #ffffff;
        }
        
        .proto-browser {
            background-color: #252526;
            border: 1px solid #3c3c3c;
        }
        
        .request-builder {
            background-color: #1e1e1e;
            font-family: 'JetBrains Mono', 'Consolas', monospace;
        }
        
        .response-viewer {
            background-color: #0d1117;
            color: #c9d1d9;
        }
        
        .syntax-json {
            color: #79c0ff;
        }
        
        .syntax-string {
            color: #a5d6ff;
        }
        
        .syntax-number {
            color: #79c0ff;
        }
        
        .status-success {
            color: #56d364;
            font-weight: bold;
        }
        
        .status-error {
            color: #f85149;
            font-weight: bold;
        }
        
        .proto-file-item {
            padding: 8px;
            border-radius: 4px;
        }
        
        .proto-file-item:hover {
            background-color: #30363d;
        }
        
        .proto-file-item:selected {
            background-color: #1f6feb;
        }
        """
        
        css_provider.load_from_data(css_data.encode())

        # Get default display
        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(
                display,
                css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
    
    def _setup_shortcuts(self):
        """Set up application keyboard shortcuts"""
        # Ctrl+Q to quit
        quit_action = Gio.SimpleAction.new("quit", None)
        quit_action.connect("activate", lambda *args: self.quit())
        self.add_action(quit_action)
        self.set_accels_for_action("app.quit", ["<Ctrl>q"])
        
        # Ctrl+N for new request
        new_action = Gio.SimpleAction.new("new-request", None)
        new_action.connect("activate", self._on_new_request)
        self.add_action(new_action)
        self.set_accels_for_action("app.new-request", ["<Ctrl>n"])
        
        # F5 to send request
        send_action = Gio.SimpleAction.new("send-request", None)
        send_action.connect("activate", self._on_send_request)
        self.add_action(send_action)
        self.set_accels_for_action("app.send-request", ["F5"])
    
    def _on_new_request(self, action, param):
        """Handle new request shortcut"""
        if self.main_window:
            self.main_window.new_request()
    
    def _on_send_request(self, action, param):
        """Handle send request shortcut"""
        if self.main_window:
            self.main_window.send_request()


def run_native_gui(launched_by_ai=False):
    """
    Entry point for native GTK GUI application.

    Now launches the full Control Center instead of just API tool.
    """
    return run_control_center(launched_by_ai=launched_by_ai)


if __name__ == "__main__":
    run_native_gui()
