"""
@llm-type control-system
@llm-legend theme_manager.py - system control component
@llm-key Core functionality for theme_manager
@llm-map Part of the Unhinged system architecture
@llm-axiom Maintains system independence and architectural compliance
@llm-contract Provides standardized interface for system integration
@llm-token theme_manager: system control component
"""
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
        """Get the main application CSS - 2025 Pixel 10XL Material Design 3 Standards"""
        return """
        /* ============================================================================ */
        /* UNHINGED CONTROL CENTER - 2025 PIXEL 10XL MATERIAL DESIGN 3 THEME          */
        /* Modern UI/UX Standards with Dynamic Color System & Advanced Typography      */
        /* ============================================================================ */

        /* === GTK-COMPATIBLE THEME - NO @IMPORT OR CSS VARIABLES === */
        /* Material Design 3 inspired colors hardcoded for GTK compatibility */

        /* === MAIN APPLICATION WINDOW === */
        .control-center-window {
            background-color: #141218;
            color: #E6E0E9;
            font-family: system-ui, sans-serif;
            font-size: 16px;
            font-weight: 400;
            line-height: 24px;
        }

        /* === HEADER BAR - Material Design 3 Navigation === */
        .control-center-header {
            background: #2B2930;
            border-bottom: 1px solid #36343B;
            padding: 16px 24px;
            box-shadow: 0px 1px 2px 0px rgba(0, 0, 0, 0.3), 0px 2px 6px 2px rgba(0, 0, 0, 0.15);
        }

        .control-center-title {
            color: #6750A4;
            font-family: system-ui, sans-serif;
            font-size: 28px;
            font-weight: 400;
            line-height: 36px;
            margin: 0;
            padding: 0;
        }

        /* === TOOL TABS - Material Design 3 Navigation Rail === */
        .tool-tabs {
            background: #211F26;
            border-bottom: 1px solid #36343B;
            padding: 8px 16px;
            /* GTK: Use orientation instead of display: flex */
            
            /* GTK: Use spacing instead of gap */

            /* GTK: Remove webkit-specific properties */
        }

        .tool-tab {
            padding: 16px 24px;
            border-radius: 16px 16px 0 0;
            margin-right: 4px;
            background: #2B2930;
            color: #49454F;
            border: 1px solid #36343B;
            border-bottom: none;
            font-family: #E6E0E9;
            font-size: #E6E0E9;
            font-weight: #E6E0E9;
            line-height: #E6E0E9;
            letter-
            transition: all #E6E0E9 #E6E0E9;

            /* GTK: Use padding instead of min-width for minimum size */
            padding-left: 60px;
            padding-right: 60px;
            
        }

        .tool-tab::before {
            content: '';
            
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: #6750A4;
            opacity: 0;
            transition: opacity #E6E0E9 #E6E0E9;
            
        }

        .tool-tab:hover {
            background: #36343B;
            color: #E6E0E9;
            
            box-shadow: 0px 1px 2px 0px rgba(0, 0, 0, 0.3), 0px 2px 6px 2px rgba(0, 0, 0, 0.15);
        }

        .tool-tab:hover::before {
            opacity: 0.08;
        }

        .tool-tab.active {
            background: #E6E0E9;
            color: #E6E0E9;
            border-color: #6750A4;
            box-shadow: 0px 1px 3px 0px rgba(0, 0, 0, 0.3), 0px 4px 8px 3px rgba(0, 0, 0, 0.15);
            
        }

        .tool-tab.active::before {
            opacity: 0.12;
        }

        .tool-tab:active {
            
            transition: transform #E6E0E9 #E6E0E9;
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

        /* ============================================================================ */
        /* MOBILE-FIRST RESPONSIVE DESIGN SYSTEM                                       */
        /* ============================================================================ */

        /* === VIEWPORT-SPECIFIC STYLES === */
        .viewport-mobile {
            /* Mobile-specific overrides */
        }

        .viewport-tablet {
            /* Tablet-specific overrides */
        }

        .viewport-desktop {
            /* Desktop-specific overrides */
        }

        /* === RESPONSIVE BREAKPOINTS === */
        .breakpoint-xs {
            /* Extra small: ≤480px */
        }

        .breakpoint-sm {
            /* Small: ≤768px */
        }

        .breakpoint-md {
            /* Medium: ≤1024px */
        }

        .breakpoint-lg {
            /* Large: ≤1440px */
        }

        .breakpoint-xl {
            /* Extra large: >1440px */
        }

        /* === MOBILE-FIRST WINDOW === */
        .mobile-first-window {
            background: #141218;
            color: #E6E0E9;
        }

        /* === MOBILE NAVIGATION BAR === */
        .mobile-nav-bar {
            background: #211F26;
            border-top: 1px solid #36343B;
            padding: 8px 0;
        }

        .nav-item {
            padding: 8px 4px;
            border-radius: 12px;
            margin: 0 4px;
            transition: all 200ms ease;
        }

        .nav-item:hover {
            background: rgba(103, 80, 164, 0.08);
        }

        .nav-item.active {
            background: rgba(103, 80, 164, 0.12);
        }

        .nav-icon {
            font-size: 24px;
            color: #E6E0E9;
        }

        .nav-item.active .nav-icon {
            color: #6750A4;
        }

        .nav-label {
            font-size: 10px;
            color: #CAC4D0;
            font-weight: 500;
        }

        .nav-item.active .nav-label {
            color: #6750A4;
            font-weight: 600;
        }

        /* === RESPONSIVE CONTAINER === */
        .responsive-container {
            background: #141218;
        }

        .mobile-main {
            padding: 16px;
        }

        .tablet-layout {
            padding: 16px;
        }

        .tablet-sidebar {
            background: #1D1B20;
            border-radius: 16px;
            padding: 16px;
        }

        .tablet-main {
            background: #141218;
        }

        .desktop-layout {
            padding: 24px;
        }

        .desktop-sidebar {
            background: #1D1B20;
            border-radius: 20px;
            padding: 24px;
        }

        .desktop-main {
            background: #141218;
        }

        /* === MOBILE HEADER === */
        .mobile-header {
            background: #211F26;
            border-bottom: 1px solid #36343B;
            min-height: 56px;
        }

        .mobile-title {
            font-size: 18px;
            font-weight: 600;
            color: #6750A4;
        }

        /* === MOBILE TOOL CARDS === */
        .mobile-tool-card {
            background: #1D1B20;
            border-radius: 16px;
            margin: 8px 0;
            border: 1px solid #36343B;
            transition: all 200ms ease;
        }

        .mobile-tool-card:hover {
            background: #211F26;
            border-color: #6750A4;
            
        }

        .tool-icon {
            font-size: 32px;
            color: #6750A4;
        }

        .tool-title {
            font-size: 16px;
            font-weight: 600;
            color: #E6E0E9;
        }

        .tool-description {
            font-size: 14px;
            color: #CAC4D0;
            opacity: 0.8;
        }

        .tool-arrow {
            font-size: 24px;
            color: #6750A4;
            font-weight: bold;
        }

        /* === MOBILE CONTENT AREA === */
        .mobile-content {
            background: #141218;
            border-radius: 16px 16px 0 0;
            min-height: 400px;
        }

        /* === MOBILE CHAT INTERFACE === */
        .mobile-chat-interface {
            padding: 16px;
            background: #141218;
        }

        .mobile-chat-input {
            background: #1D1B20;
            border: 2px solid #36343B;
            border-radius: 24px;
            padding: 12px 16px;
            font-size: 16px;
            color: #E6E0E9;
            /* GTK: Use hexpand instead of width: 100% */
            
            min-height: 48px;
        }

        .mobile-chat-input:focus {
            border-color: #6750A4;
            background: #211F26;
        }

        .mobile-chat-send-button {
            background: #6750A4;
            color: #FFFFFF;
            border-radius: 24px;
            padding: 12px 16px;
            margin-left: 8px;
            /* GTK: Use padding for minimum size instead of min-width */
            padding: 18px;
            min-height: 48px;
        }

        .mobile-chat-send-button:hover {
            background: #7C4DFF;
        }

        /* === MOBILE CHAT MESSAGES === */
        .chat-message {
            margin: 4px 0;
        }

        .message-bubble {
            background: #1D1B20;
            border-radius: 18px;
            padding: 12px 16px;
            /* GTK: Remove max-width, use natural text wrapping */
        }

        .user-message .message-bubble {
            background: #6750A4;
            border-bottom-right-radius: 4px;
        }

        .assistant-message .message-bubble {
            background: #2B2930;
            border-bottom-left-radius: 4px;
        }

        .message-text {
            color: #E6E0E9;
            font-size: 16px;
            line-height: 1.4;
        }

        .user-message .message-text {
            color: #FFFFFF;
        }

        .message-timestamp {
            font-size: 12px;
            color: #CAC4D0;
            opacity: 0.7;
            margin-top: 4px;
        }

        .typing-indicator {
            opacity: 0.7;
        }

        .typing-dots {
            color: #CAC4D0;
            font-size: 14px;
            font-style: italic;
        }

        /* === MOBILE CHAT HEADER === */
        .mobile-chat-header {
            border-bottom: 1px solid #36343B;
            padding-bottom: 8px;
        }

        .chat-header-title {
            font-size: 20px;
            font-weight: 600;
            color: #E6E0E9;
        }

        .chat-status {
            font-size: 14px;
            color: #56D364;
        }

        /* === CHAT INPUT FRAME === */
        .chat-input-frame {
            border: 2px solid #36343B;
            border-radius: 24px;
            background: #1D1B20;
        }

        .chat-input-frame:focus-within {
            border-color: #6750A4;
            background: #211F26;
        }

        /* === CHAT MESSAGES SCROLL === */
        .chat-messages-scroll {
            background: transparent;
        }

        .chat-messages {
            padding: 8px 0;
        }

        /* === RESPONSIVE UTILITIES === */
        .hide-mobile {
            /* Hidden on mobile viewports */
        }

        .viewport-mobile .hide-mobile {
            /* GTK: Use opacity instead of display: none */
            opacity: 0;
            
        }

        .show-mobile-only {
            /* GTK: Use opacity instead of display: none */
            opacity: 0;
            
        }

        .viewport-mobile .show-mobile-only {
            /* GTK: Use opacity instead of display: block */
            opacity: 1;
            
        }

        .hide-tablet {
            /* Hidden on tablet viewports */
        }

        .viewport-tablet .hide-tablet {
            /* GTK: Use opacity instead of display: none */
            opacity: 0;
            
        }

        .hide-desktop {
            /* Hidden on desktop viewports */
        }

        .viewport-desktop .hide-desktop {
            /* GTK: Use opacity instead of display: none */
            opacity: 0;
            
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
