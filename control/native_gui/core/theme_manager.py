"""
🎨 Theme Manager - Application-wide Styling

Manages themes, CSS, and visual styling for the entire application.
Provides consistent theming across all tools and components.
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('Gdk', '4.0')

from gi.repository import Gtk, Adw, Gdk
from pathlib import Path


class ThemeManager:
    """
    Manages application-wide theming and styling.
    
    Provides consistent dark theme with syntax highlighting
    and tool-specific styling capabilities.
    """
    
    def __init__(self):
        self.css_provider = None
        print("🎨 Theme manager initialized")
    
    def setup_theming(self):
        """Set up application-wide theming"""
        # Force dark theme
        Adw.StyleManager.get_default().set_color_scheme(Adw.ColorScheme.FORCE_DARK)
        
        # Load custom CSS
        self._load_application_css()
        
        print("✅ Application theming configured")
    
    def _load_application_css(self):
        """Load and apply custom CSS styles"""
        self.css_provider = Gtk.CssProvider()
        
        css_data = self._get_application_css()
        self.css_provider.load_from_data(css_data.encode())
        
        # Get default display
        display = Gdk.Display.get_default()
        if display:
            Gtk.StyleContext.add_provider_for_display(
                display,
                self.css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
    
    def _get_application_css(self) -> str:
        """Get the main application CSS"""
        return """
        /* ============================================================================ */
        /* UNHINGED CONTROL CENTER - NATIVE GTK THEME                                  */
        /* ============================================================================ */
        
        /* Main application window */
        .control-center-window {
            background-color: #0d1117;
            color: #c9d1d9;
        }
        
        /* Tool tabs */
        .tool-tabs {
            background-color: #161b22;
            border-bottom: 1px solid #30363d;
        }
        
        .tool-tab {
            padding: 12px 16px;
            border-radius: 6px 6px 0 0;
            margin-right: 2px;
            background-color: #21262d;
            color: #8b949e;
            border: 1px solid #30363d;
            border-bottom: none;
        }
        
        .tool-tab:hover {
            background-color: #30363d;
            color: #c9d1d9;
        }
        
        .tool-tab.active {
            background-color: #0d1117;
            color: #f0f6fc;
            border-color: #1f6feb;
        }
        
        /* Tool content area */
        .tool-content {
            background-color: #0d1117;
            padding: 16px;
        }
        
        /* API Development Tool */
        .api-dev-tool {
            background-color: #0d1117;
        }
        
        .proto-browser {
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 6px;
        }
        
        .request-builder {
            background-color: #0d1117;
            font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
        }
        
        .response-viewer {
            background-color: #0d1117;
            color: #c9d1d9;
        }
        
        /* System Monitor Tool */
        .system-monitor {
            background-color: #0d1117;
        }
        
        .metric-card {
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 16px;
            margin: 8px;
        }
        
        .metric-value {
            font-size: 24px;
            font-weight: bold;
            color: #56d364;
        }
        
        .metric-label {
            color: #8b949e;
            font-size: 12px;
        }
        
        /* Log Viewer Tool */
        .log-viewer {
            background-color: #0d1117;
            font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
        }
        
        .log-entry {
            padding: 4px 8px;
            border-bottom: 1px solid #21262d;
        }
        
        .log-entry.error {
            background-color: #490202;
            color: #f85149;
        }
        
        .log-entry.warning {
            background-color: #4d3800;
            color: #d29922;
        }
        
        .log-entry.info {
            background-color: #0c2d6b;
            color: #79c0ff;
        }
        
        /* Service Manager Tool */
        .service-manager {
            background-color: #0d1117;
        }
        
        .service-card {
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 12px;
            margin: 4px;
        }
        
        .service-status.running {
            color: #56d364;
        }
        
        .service-status.stopped {
            color: #f85149;
        }
        
        .service-status.unknown {
            color: #8b949e;
        }
        
        /* File Browser Tool */
        .file-browser {
            background-color: #0d1117;
        }
        
        .file-tree {
            background-color: #161b22;
            border: 1px solid #30363d;
        }
        
        .file-item {
            padding: 4px 8px;
        }
        
        .file-item:hover {
            background-color: #30363d;
        }
        
        .file-item:selected {
            background-color: #1f6feb;
        }
        
        /* Syntax highlighting */
        .syntax-json {
            color: #79c0ff;
        }
        
        .syntax-string {
            color: #a5d6ff;
        }
        
        .syntax-number {
            color: #79c0ff;
        }
        
        .syntax-keyword {
            color: #ff7b72;
            font-weight: bold;
        }
        
        .syntax-comment {
            color: #8b949e;
            font-style: italic;
        }
        
        /* Status indicators */
        .status-success {
            color: #56d364;
            font-weight: bold;
        }
        
        .status-error {
            color: #f85149;
            font-weight: bold;
        }
        
        .status-warning {
            color: #d29922;
            font-weight: bold;
        }
        
        .status-info {
            color: #79c0ff;
            font-weight: bold;
        }
        
        /* Buttons */
        .primary-button {
            background-color: #238636;
            color: #ffffff;
            border: 1px solid #2ea043;
            border-radius: 6px;
            padding: 8px 16px;
        }
        
        .primary-button:hover {
            background-color: #2ea043;
        }
        
        .secondary-button {
            background-color: #21262d;
            color: #c9d1d9;
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 8px 16px;
        }
        
        .secondary-button:hover {
            background-color: #30363d;
        }
        
        .danger-button {
            background-color: #da3633;
            color: #ffffff;
            border: 1px solid #f85149;
            border-radius: 6px;
            padding: 8px 16px;
        }
        
        .danger-button:hover {
            background-color: #f85149;
        }
        
        /* Text inputs */
        entry {
            background-color: #0d1117;
            color: #c9d1d9;
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 8px 12px;
        }
        
        entry:focus {
            border-color: #1f6feb;
            box-shadow: 0 0 0 3px rgba(31, 111, 235, 0.3);
        }
        
        /* Text views */
        textview {
            background-color: #0d1117;
            color: #c9d1d9;
        }
        
        textview text {
            background-color: #0d1117;
            color: #c9d1d9;
        }
        
        /* Scrollbars */
        scrollbar {
            background-color: #161b22;
        }
        
        scrollbar slider {
            background-color: #30363d;
            border-radius: 6px;
        }
        
        scrollbar slider:hover {
            background-color: #484f58;
        }
        
        /* Status bar */
        .status-bar {
            background-color: #161b22;
            border-top: 1px solid #30363d;
            padding: 8px 16px;
            color: #8b949e;
            font-size: 12px;
        }
        
        /* Tooltips */
        tooltip {
            background-color: #21262d;
            color: #c9d1d9;
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 8px;
        }
        """
    
    def add_tool_css(self, tool_name: str, css: str):
        """Add tool-specific CSS"""
        if not self.css_provider:
            return
        
        # Wrap tool CSS with tool-specific selector
        tool_css = f"""
        /* Tool-specific CSS: {tool_name} */
        .tool-{tool_name.lower().replace(' ', '-')} {{
            {css}
        }}
        """
        
        # Note: In a full implementation, you'd want to manage
        # multiple CSS providers or append to existing CSS
        print(f"🎨 Added CSS for tool: {tool_name}")
    
    def get_color(self, color_name: str) -> str:
        """Get a color value by name"""
        colors = {
            'background': '#0d1117',
            'surface': '#161b22',
            'primary': '#1f6feb',
            'success': '#56d364',
            'warning': '#d29922',
            'error': '#f85149',
            'text': '#c9d1d9',
            'text-muted': '#8b949e',
            'border': '#30363d'
        }
        
        return colors.get(color_name, '#c9d1d9')
    
    def apply_syntax_highlighting(self, text_buffer, language: str = 'json'):
        """Apply syntax highlighting to a text buffer"""
        # This is a placeholder for syntax highlighting
        # In a full implementation, you'd use a proper syntax highlighter
        print(f"🎨 Applied {language} syntax highlighting")
        
        # Basic JSON highlighting example
        if language == 'json':
            self._apply_json_highlighting(text_buffer)
    
    def _apply_json_highlighting(self, text_buffer):
        """Apply basic JSON syntax highlighting"""
        # Create text tags if they don't exist
        tag_table = text_buffer.get_tag_table()
        
        if not tag_table.lookup("json-string"):
            string_tag = text_buffer.create_tag("json-string")
            string_tag.set_property("foreground", "#a5d6ff")
            
            number_tag = text_buffer.create_tag("json-number")
            number_tag.set_property("foreground", "#79c0ff")
            
            keyword_tag = text_buffer.create_tag("json-keyword")
            keyword_tag.set_property("foreground", "#ff7b72")
            keyword_tag.set_property("weight", 700)  # Bold
