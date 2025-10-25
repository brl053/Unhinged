
# Initialize GUI event logger
gui_logger = create_gui_logger("unhinged-theme-manager", "1.0.0")

"""
@llm-type theme-system
@llm-legend Enhanced Theme Manager - Unified theming system with mobile-responsive CSS support
@llm-key Manages GTK4 themes, mobile-responsive styles, and dynamic theme switching
@llm-map Central theming component in Unhinged native GUI architecture
@llm-axiom Themes must maintain consistency across desktop and mobile viewports
@llm-contract Provides standardized theming interface with mobile-first responsive design
@llm-token theme_manager: Enhanced theming system with mobile-responsive CSS integration
"""
"""
🎨 Theme Manager - Application-wide Styling

Manages themes, CSS, and visual styling for the entire application.
Provides consistent theming across all tools and components.
"""

import gi
from unhinged_events import create_gui_logger
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('Gdk', '4.0')

from gi.repository import Gtk, Adw, Gdk, Gdk
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from dataclasses import dataclass

# Import shared CSS generator
from .css_generator import CSSGenerator, CSSConfig


class ThemeVariant(Enum):
    """
    @llm-type enum
    @llm-legend Theme variant types for different use cases
    @llm-key Defines available theme variants with specific characteristics
    """
    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"          # Follow system preference
    HIGH_CONTRAST = "high_contrast"
    MOBILE_OPTIMIZED = "mobile_optimized"


@dataclass
class ThemeConfig:
    """
    @llm-type configuration
    @llm-legend Theme configuration with mobile-responsive properties
    @llm-key Defines theme parameters for consistent styling across viewports
    """
    variant: ThemeVariant = ThemeVariant.DARK  # Default to dark theme
    mobile_optimized: bool = True
    touch_friendly: bool = True
    high_contrast: bool = False
    custom_css_enabled: bool = True
    animation_enabled: bool = True

    # Color scheme
    primary_color: str = "#007AFF"
    secondary_color: str = "#5856D6"
    success_color: str = "#34C759"
    warning_color: str = "#FF9500"
    error_color: str = "#FF3B30"

    # Typography
    base_font_size: int = 14
    mobile_font_scale: float = 1.1

    # Spacing
    base_spacing: int = 12
    mobile_spacing_scale: float = 0.8

class ThemeManager:
    """
    @llm-type manager-class
    @llm-legend Enhanced theme manager with mobile-responsive capabilities
    @llm-key Manages GTK4 themes, CSS loading, and responsive design adaptation
    @llm-map Central theming system for Unhinged native GUI with mobile support
    @llm-axiom Themes must provide consistent experience across all viewport sizes
    @llm-contract Provides unified theming interface with mobile-first responsive design
    @llm-token ThemeManager: Enhanced theming system with mobile-responsive CSS support

    Enhanced theme manager for the Unhinged Control Center.
    Provides unified theming with mobile-responsive CSS support.
    """

    def __init__(self, config: Optional[ThemeConfig] = None):
        self.config = config or ThemeConfig()

        # Theme state
        self.current_variant = self.config.variant
        self.is_mobile_mode = False
        self.css_provider = None  # Keep for backward compatibility
        self.mobile_css_provider = None

        # Theme paths
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.theme_dir = self.project_root / "control" / "native_gui" / "themes"
        self.generated_css_dir = self.project_root / "generated" / "static_html"

        # CSS providers
        self.css_providers: Dict[str, Gtk.CssProvider] = {}

        # Initialize shared CSS generator
        css_config = CSSConfig(
            base_font_size=self.config.base_font_size,
            mobile_font_scale=self.config.mobile_font_scale,
            base_spacing=self.config.base_spacing,
            mobile_spacing_scale=self.config.mobile_spacing_scale,
            primary_color=self.config.primary_color,
            secondary_color=self.config.secondary_color,
            success_color=self.config.success_color,
            warning_color=self.config.warning_color,
            error_color=self.config.error_color
        )
        self.css_generator = CSSGenerator(css_config)

        # Callbacks
        self.on_theme_changed: Optional[Callable[[ThemeVariant], None]] = None
        self.on_mobile_mode_changed: Optional[Callable[[bool], None]] = None

    
    def setup_theming(self):
        """
        @llm-type method
        @llm-legend Set up enhanced application-wide theming with mobile support
        @llm-key Initializes theme system with responsive CSS and mobile optimization
        """
        # Initialize enhanced theme system
        self._initialize_theme_system()

        # Apply current theme variant
        self._apply_theme_variant(self.current_variant)

        # Load custom CSS (backward compatibility)
        self._load_application_css()

        # Load mobile-responsive CSS
        self._load_mobile_css()

        gui_logger.info(" Enhanced application theming configured", {"status": "success"})

    def _load_mobile_css(self):
        """
        @llm-type method
        @llm-legend Load mobile-responsive CSS using shared generator
        @llm-key Applies mobile-optimized CSS for responsive design
        """
        try:
            # Generate mobile CSS using shared generator
            mobile_css = self.css_generator.generate_mobile_css()

            # Create mobile CSS provider if not exists
            if 'mobile' not in self.css_providers:
                self.css_providers['mobile'] = Gtk.CssProvider()

            # Load mobile CSS
            self.css_providers['mobile'].load_from_data(mobile_css.encode())

            # Apply to display
            display = Gdk.Display.get_default()
            if display:
                Gtk.StyleContext.add_provider_for_display(
                    display,
                    self.css_providers['mobile'],
                    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION + 1
                )

            gui_logger.info(" Mobile-responsive CSS loaded", {"event_type": "theming"})

        except Exception as e:
            gui_logger.error(f" Failed to load mobile CSS: {e}")

    def _initialize_theme_system(self):
        """
        @llm-type method
        @llm-legend Initialize the enhanced theme system with CSS providers
        @llm-key Sets up GTK4 CSS providers and loads base themes
        """
        try:
            # Create theme directories if they don't exist
            self.theme_dir.mkdir(parents=True, exist_ok=True)

            # Initialize CSS providers
            self._setup_css_providers()

            # Load base theme
            self._load_base_theme()

            gui_logger.info(" Enhanced theme system initialized", {"event_type": "theming"})

        except Exception as e:
            gui_logger.error(f" Failed to initialize enhanced theme system: {e}")

    def _setup_css_providers(self):
        """
        @llm-type method
        @llm-legend Set up GTK4 CSS providers for theme management
        @llm-key Creates and configures CSS providers for different theme components
        """
        # Base theme provider
        self.css_providers['base'] = Gtk.CssProvider()

        # Mobile-responsive provider
        self.css_providers['mobile'] = Gtk.CssProvider()

        # Custom theme provider
        self.css_providers['custom'] = Gtk.CssProvider()

        # High contrast provider
        self.css_providers['high_contrast'] = Gtk.CssProvider()

        gui_logger.info(" CSS providers initialized", {"event_type": "theming"})

    def _apply_theme_variant(self, variant: ThemeVariant):
        """
        @llm-type method
        @llm-legend Apply specific theme variant to the application
        @llm-key Configures theme variant-specific styling and behavior
        """
        try:
            self.current_variant = variant

            # Apply variant-specific CSS
            if variant == ThemeVariant.HIGH_CONTRAST:
                self._apply_high_contrast_css()

            # Update theme configuration
            self.config.variant = variant

            # Trigger theme changed callback
            if self.on_theme_changed:
                self.on_theme_changed(variant)


        except Exception as e:
            gui_logger.error(f" Failed to apply theme variant {variant.value}: {e}")

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

    def _generate_base_css(self) -> str:
        """
        @llm-type method
        @llm-legend Generate base CSS with Unhinged design system using shared generator
        @llm-key Creates foundational CSS with consistent design tokens via CSSGenerator
        """
        # Use shared CSS generator for mobile CSS
        mobile_css = self.css_generator.generate_mobile_css()
        component_css = self.css_generator.generate_component_css()

        # Add theme-specific CSS variables
        theme_vars = f"""
/* Enhanced Unhinged Control Center Base Theme */
/* @llm-type generated-css */
/* @llm-legend Base theme CSS with Unhinged design system and mobile support */
/* @llm-key Foundational styling for consistent UI appearance across viewports */

:root {{
    --primary-color: {self.config.primary_color};
    --secondary-color: {self.config.secondary_color};
    --success-color: {self.config.success_color};
    --warning-color: {self.config.warning_color};
    --error-color: {self.config.error_color};

    --base-font-size: {self.config.base_font_size}px;
    --base-spacing: {self.config.base_spacing}px;

    --border-radius: 8px;
    --shadow-light: 0 2px 8px alpha(@theme_fg_color, 0.1);
    --shadow-medium: 0 4px 16px alpha(@theme_fg_color, 0.15);
    --shadow-heavy: 0 8px 32px alpha(@theme_fg_color, 0.2);
}}
"""

        return f"{theme_vars}\n{mobile_css}\n{component_css}"

    def _generate_mobile_css(self) -> str:
        """
        @llm-type method
        @llm-legend Generate mobile-specific CSS overrides using shared generator
        @llm-key Provides mobile-optimized styling via CSSGenerator
        """
        # Use shared CSS generator for responsive CSS
        responsive_css = self.css_generator.generate_responsive_css()
        navigation_css = self.css_generator.generate_navigation_css()

        return f"{responsive_css}\n{navigation_css}"

    def _apply_high_contrast_css(self):
        """
        @llm-type method
        @llm-legend Apply high contrast CSS overrides using shared generator
        @llm-key Provides accessibility-focused high contrast styling via CSSGenerator
        """
        # Use shared CSS generator for high contrast CSS
        high_contrast_css = self.css_generator.generate_high_contrast_css()

        try:
            if 'high_contrast' not in self.css_providers:
                self.css_providers['high_contrast'] = Gtk.CssProvider()

            self.css_providers['high_contrast'].load_from_data(high_contrast_css.encode())

            display = Gdk.Display.get_default()
            if display:
                Gtk.StyleContext.add_provider_for_display(
                    display,
                    self.css_providers['high_contrast'],
                    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION + 2
                )

            gui_logger.info(" High contrast CSS applied", {"event_type": "theming"})

        except Exception as e:
            gui_logger.error(f" Failed to apply high contrast CSS: {e}")

    def set_mobile_mode(self, enabled: bool):
        """
        @llm-type method
        @llm-legend Enable or disable mobile mode
        @llm-key Toggles mobile-optimized styling and behavior
        """
        if self.is_mobile_mode != enabled:
            self.is_mobile_mode = enabled

            # Trigger callback
            if self.on_mobile_mode_changed:
                self.on_mobile_mode_changed(enabled)


    def get_theme_info(self) -> Dict[str, Any]:
        """
        @llm-type method
        @llm-legend Get current theme information
        @llm-key Returns comprehensive theme state and configuration
        """
        return {
            'variant': self.current_variant.value,
            'mobile_mode': self.is_mobile_mode,
            'config': {
                'mobile_optimized': self.config.mobile_optimized,
                'touch_friendly': self.config.touch_friendly,
                'high_contrast': self.config.high_contrast,
                'animation_enabled': self.config.animation_enabled,
                'primary_color': self.config.primary_color,
                'base_font_size': self.config.base_font_size,
                'base_spacing': self.config.base_spacing
            },
            'css_providers': list(self.css_providers.keys()) if hasattr(self, 'css_providers') else [],
            'theme_dir': str(self.theme_dir) if hasattr(self, 'theme_dir') else '',
            'generated_css_dir': str(self.generated_css_dir) if hasattr(self, 'generated_css_dir') else ''
        }
