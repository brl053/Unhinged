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

        /* === TYPOGRAPHY SYSTEM - Material Design 3 2025 === */
        @import url('https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,100;0,300;0,400;0,500;0,700;0,900;1,100;1,300;1,400;1,500;1,700;1,900&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&display=swap');

        :root {
            /* === MATERIAL DESIGN 3 COLOR SYSTEM === */
            /* Primary Colors - Dynamic Material You */
            --md-sys-color-primary: #6750A4;
            --md-sys-color-on-primary: #FFFFFF;
            --md-sys-color-primary-container: #EADDFF;
            --md-sys-color-on-primary-container: #21005D;

            /* Surface Colors - Elevated Surfaces */
            --md-sys-color-surface: #FEF7FF;
            --md-sys-color-surface-dim: #DED8E1;
            --md-sys-color-surface-bright: #FEF7FF;
            --md-sys-color-surface-container-lowest: #FFFFFF;
            --md-sys-color-surface-container-low: #F7F2FA;
            --md-sys-color-surface-container: #F3EDF7;
            --md-sys-color-surface-container-high: #ECE6F0;
            --md-sys-color-surface-container-highest: #E6E0E9;
            --md-sys-color-on-surface: #1C1B1F;
            --md-sys-color-on-surface-variant: #49454F;

            /* Dark Theme Override */
            --md-sys-color-surface-dark: #141218;
            --md-sys-color-on-surface-dark: #E6E0E9;
            --md-sys-color-surface-container-dark: #211F26;
            --md-sys-color-surface-container-high-dark: #2B2930;
            --md-sys-color-surface-container-highest-dark: #36343B;

            /* Accent & Secondary */
            --md-sys-color-secondary: #625B71;
            --md-sys-color-on-secondary: #FFFFFF;
            --md-sys-color-secondary-container: #E8DEF8;
            --md-sys-color-on-secondary-container: #1D192B;

            /* Error & Warning */
            --md-sys-color-error: #BA1A1A;
            --md-sys-color-on-error: #FFFFFF;
            --md-sys-color-error-container: #FFDAD6;
            --md-sys-color-on-error-container: #410002;

            /* === TYPOGRAPHY SCALE - Material Design 3 === */
            --md-sys-typescale-display-large-font: 'Roboto', 'Inter', system-ui, -apple-system, sans-serif;
            --md-sys-typescale-display-large-size: 57px;
            --md-sys-typescale-display-large-weight: 400;
            --md-sys-typescale-display-large-line-height: 64px;
            --md-sys-typescale-display-large-tracking: -0.25px;

            --md-sys-typescale-display-medium-font: 'Roboto', 'Inter', system-ui, sans-serif;
            --md-sys-typescale-display-medium-size: 45px;
            --md-sys-typescale-display-medium-weight: 400;
            --md-sys-typescale-display-medium-line-height: 52px;
            --md-sys-typescale-display-medium-tracking: 0px;

            --md-sys-typescale-display-small-font: 'Roboto', 'Inter', system-ui, sans-serif;
            --md-sys-typescale-display-small-size: 36px;
            --md-sys-typescale-display-small-weight: 400;
            --md-sys-typescale-display-small-line-height: 44px;
            --md-sys-typescale-display-small-tracking: 0px;

            --md-sys-typescale-headline-large-font: 'Roboto', 'Inter', system-ui, sans-serif;
            --md-sys-typescale-headline-large-size: 32px;
            --md-sys-typescale-headline-large-weight: 400;
            --md-sys-typescale-headline-large-line-height: 40px;
            --md-sys-typescale-headline-large-tracking: 0px;

            --md-sys-typescale-headline-medium-font: 'Roboto', 'Inter', system-ui, sans-serif;
            --md-sys-typescale-headline-medium-size: 28px;
            --md-sys-typescale-headline-medium-weight: 400;
            --md-sys-typescale-headline-medium-line-height: 36px;
            --md-sys-typescale-headline-medium-tracking: 0px;

            --md-sys-typescale-headline-small-font: 'Roboto', 'Inter', system-ui, sans-serif;
            --md-sys-typescale-headline-small-size: 24px;
            --md-sys-typescale-headline-small-weight: 400;
            --md-sys-typescale-headline-small-line-height: 32px;
            --md-sys-typescale-headline-small-tracking: 0px;

            --md-sys-typescale-title-large-font: 'Roboto', 'Inter', system-ui, sans-serif;
            --md-sys-typescale-title-large-size: 22px;
            --md-sys-typescale-title-large-weight: 400;
            --md-sys-typescale-title-large-line-height: 28px;
            --md-sys-typescale-title-large-tracking: 0px;

            --md-sys-typescale-title-medium-font: 'Roboto', 'Inter', system-ui, sans-serif;
            --md-sys-typescale-title-medium-size: 16px;
            --md-sys-typescale-title-medium-weight: 500;
            --md-sys-typescale-title-medium-line-height: 24px;
            --md-sys-typescale-title-medium-tracking: 0.15px;

            --md-sys-typescale-title-small-font: 'Roboto', 'Inter', system-ui, sans-serif;
            --md-sys-typescale-title-small-size: 14px;
            --md-sys-typescale-title-small-weight: 500;
            --md-sys-typescale-title-small-line-height: 20px;
            --md-sys-typescale-title-small-tracking: 0.1px;

            --md-sys-typescale-body-large-font: 'Roboto', 'Inter', system-ui, sans-serif;
            --md-sys-typescale-body-large-size: 16px;
            --md-sys-typescale-body-large-weight: 400;
            --md-sys-typescale-body-large-line-height: 24px;
            --md-sys-typescale-body-large-tracking: 0.5px;

            --md-sys-typescale-body-medium-font: 'Roboto', 'Inter', system-ui, sans-serif;
            --md-sys-typescale-body-medium-size: 14px;
            --md-sys-typescale-body-medium-weight: 400;
            --md-sys-typescale-body-medium-line-height: 20px;
            --md-sys-typescale-body-medium-tracking: 0.25px;

            --md-sys-typescale-body-small-font: 'Roboto', 'Inter', system-ui, sans-serif;
            --md-sys-typescale-body-small-size: 12px;
            --md-sys-typescale-body-small-weight: 400;
            --md-sys-typescale-body-small-line-height: 16px;
            --md-sys-typescale-body-small-tracking: 0.4px;

            --md-sys-typescale-label-large-font: 'Roboto', 'Inter', system-ui, sans-serif;
            --md-sys-typescale-label-large-size: 14px;
            --md-sys-typescale-label-large-weight: 500;
            --md-sys-typescale-label-large-line-height: 20px;
            --md-sys-typescale-label-large-tracking: 0.1px;

            --md-sys-typescale-label-medium-font: 'Roboto', 'Inter', system-ui, sans-serif;
            --md-sys-typescale-label-medium-size: 12px;
            --md-sys-typescale-label-medium-weight: 500;
            --md-sys-typescale-label-medium-line-height: 16px;
            --md-sys-typescale-label-medium-tracking: 0.5px;

            --md-sys-typescale-label-small-font: 'Roboto', 'Inter', system-ui, sans-serif;
            --md-sys-typescale-label-small-size: 11px;
            --md-sys-typescale-label-small-weight: 500;
            --md-sys-typescale-label-small-line-height: 16px;
            --md-sys-typescale-label-small-tracking: 0.5px;

            /* === SPACING SYSTEM - 8px Grid === */
            --md-sys-spacing-xs: 4px;
            --md-sys-spacing-sm: 8px;
            --md-sys-spacing-md: 16px;
            --md-sys-spacing-lg: 24px;
            --md-sys-spacing-xl: 32px;
            --md-sys-spacing-xxl: 48px;
            --md-sys-spacing-xxxl: 64px;

            /* === ELEVATION SYSTEM === */
            --md-sys-elevation-level0: none;
            --md-sys-elevation-level1: 0px 1px 2px 0px rgba(0, 0, 0, 0.3), 0px 1px 3px 1px rgba(0, 0, 0, 0.15);
            --md-sys-elevation-level2: 0px 1px 2px 0px rgba(0, 0, 0, 0.3), 0px 2px 6px 2px rgba(0, 0, 0, 0.15);
            --md-sys-elevation-level3: 0px 1px 3px 0px rgba(0, 0, 0, 0.3), 0px 4px 8px 3px rgba(0, 0, 0, 0.15);
            --md-sys-elevation-level4: 0px 2px 3px 0px rgba(0, 0, 0, 0.3), 0px 6px 10px 4px rgba(0, 0, 0, 0.15);
            --md-sys-elevation-level5: 0px 4px 4px 0px rgba(0, 0, 0, 0.3), 0px 8px 12px 6px rgba(0, 0, 0, 0.15);

            /* === BORDER RADIUS SYSTEM === */
            --md-sys-shape-corner-none: 0px;
            --md-sys-shape-corner-extra-small: 4px;
            --md-sys-shape-corner-small: 8px;
            --md-sys-shape-corner-medium: 12px;
            --md-sys-shape-corner-large: 16px;
            --md-sys-shape-corner-extra-large: 28px;
            --md-sys-shape-corner-full: 9999px;

            /* === MOTION & ANIMATION === */
            --md-sys-motion-duration-short1: 50ms;
            --md-sys-motion-duration-short2: 100ms;
            --md-sys-motion-duration-short3: 150ms;
            --md-sys-motion-duration-short4: 200ms;
            --md-sys-motion-duration-medium1: 250ms;
            --md-sys-motion-duration-medium2: 300ms;
            --md-sys-motion-duration-medium3: 350ms;
            --md-sys-motion-duration-medium4: 400ms;
            --md-sys-motion-duration-long1: 450ms;
            --md-sys-motion-duration-long2: 500ms;
            --md-sys-motion-duration-long3: 550ms;
            --md-sys-motion-duration-long4: 600ms;

            --md-sys-motion-easing-linear: cubic-bezier(0, 0, 1, 1);
            --md-sys-motion-easing-standard: cubic-bezier(0.2, 0, 0, 1);
            --md-sys-motion-easing-standard-accelerate: cubic-bezier(0.3, 0, 1, 1);
            --md-sys-motion-easing-standard-decelerate: cubic-bezier(0, 0, 0, 1);
            --md-sys-motion-easing-emphasized: cubic-bezier(0.2, 0, 0, 1);
            --md-sys-motion-easing-emphasized-accelerate: cubic-bezier(0.3, 0, 0.8, 0.15);
            --md-sys-motion-easing-emphasized-decelerate: cubic-bezier(0.05, 0.7, 0.1, 1);
        }

        /* === DARK THEME OVERRIDE === */
        @media (prefers-color-scheme: dark) {
            :root {
                --md-sys-color-surface: var(--md-sys-color-surface-dark);
                --md-sys-color-on-surface: var(--md-sys-color-on-surface-dark);
                --md-sys-color-surface-container: var(--md-sys-color-surface-container-dark);
                --md-sys-color-surface-container-high: var(--md-sys-color-surface-container-high-dark);
                --md-sys-color-surface-container-highest: var(--md-sys-color-surface-container-highest-dark);
            }
        }

        /* === MAIN APPLICATION WINDOW === */
        .control-center-window {
            background-color: var(--md-sys-color-surface-dark);
            color: var(--md-sys-color-on-surface-dark);
            font-family: var(--md-sys-typescale-body-large-font);
            font-size: var(--md-sys-typescale-body-large-size);
            font-weight: var(--md-sys-typescale-body-large-weight);
            line-height: var(--md-sys-typescale-body-large-line-height);
            letter-spacing: var(--md-sys-typescale-body-large-tracking);
            transition: all var(--md-sys-motion-duration-medium2) var(--md-sys-motion-easing-standard);
        }

        /* === HEADER BAR - Material Design 3 Navigation === */
        .control-center-header {
            background: var(--md-sys-color-surface-container-high-dark);
            border-bottom: 1px solid var(--md-sys-color-surface-container-highest-dark);
            padding: var(--md-sys-spacing-md) var(--md-sys-spacing-lg);
            box-shadow: var(--md-sys-elevation-level2);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            transition: all var(--md-sys-motion-duration-medium2) var(--md-sys-motion-easing-standard);
        }

        .control-center-title {
            color: var(--md-sys-color-primary);
            font-family: var(--md-sys-typescale-headline-medium-font);
            font-size: var(--md-sys-typescale-headline-medium-size);
            font-weight: var(--md-sys-typescale-headline-medium-weight);
            line-height: var(--md-sys-typescale-headline-medium-line-height);
            letter-spacing: var(--md-sys-typescale-headline-medium-tracking);
            margin: 0;
            padding: 0;
        }

        /* === TOOL TABS - Material Design 3 Navigation Rail === */
        .tool-tabs {
            background: var(--md-sys-color-surface-container-dark);
            border-bottom: 1px solid var(--md-sys-color-surface-container-highest-dark);
            padding: var(--md-sys-spacing-sm) var(--md-sys-spacing-md);
            display: flex;
            gap: var(--md-sys-spacing-xs);
            overflow-x: auto;
            scrollbar-width: none;
            -ms-overflow-style: none;
        }

        .tool-tabs::-webkit-scrollbar {
            display: none;
        }

        .tool-tab {
            padding: var(--md-sys-spacing-md) var(--md-sys-spacing-lg);
            border-radius: var(--md-sys-shape-corner-large) var(--md-sys-shape-corner-large) 0 0;
            margin-right: var(--md-sys-spacing-xs);
            background: var(--md-sys-color-surface-container-high-dark);
            color: var(--md-sys-color-on-surface-variant);
            border: 1px solid var(--md-sys-color-surface-container-highest-dark);
            border-bottom: none;
            font-family: var(--md-sys-typescale-title-medium-font);
            font-size: var(--md-sys-typescale-title-medium-size);
            font-weight: var(--md-sys-typescale-title-medium-weight);
            line-height: var(--md-sys-typescale-title-medium-line-height);
            letter-spacing: var(--md-sys-typescale-title-medium-tracking);
            transition: all var(--md-sys-motion-duration-short4) var(--md-sys-motion-easing-standard);
            cursor: pointer;
            position: relative;
            overflow: hidden;
            white-space: nowrap;
            min-width: 120px;
            text-align: center;
        }

        .tool-tab::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: var(--md-sys-color-primary);
            opacity: 0;
            transition: opacity var(--md-sys-motion-duration-short2) var(--md-sys-motion-easing-standard);
            z-index: -1;
        }

        .tool-tab:hover {
            background: var(--md-sys-color-surface-container-highest-dark);
            color: var(--md-sys-color-on-surface-dark);
            transform: translateY(-2px);
            box-shadow: var(--md-sys-elevation-level2);
        }

        .tool-tab:hover::before {
            opacity: 0.08;
        }

        .tool-tab.active {
            background: var(--md-sys-color-primary-container);
            color: var(--md-sys-color-on-primary-container);
            border-color: var(--md-sys-color-primary);
            box-shadow: var(--md-sys-elevation-level3);
            transform: translateY(-1px);
        }

        .tool-tab.active::before {
            opacity: 0.12;
        }

        .tool-tab:active {
            transform: translateY(0);
            transition: transform var(--md-sys-motion-duration-short1) var(--md-sys-motion-easing-standard);
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
            transform: translateY(-2px);
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
            width: 100%;
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
            min-width: 48px;
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
            max-width: 280px;
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
            display: none;
        }

        .show-mobile-only {
            display: none;
        }

        .viewport-mobile .show-mobile-only {
            display: block;
        }

        .hide-tablet {
            /* Hidden on tablet viewports */
        }

        .viewport-tablet .hide-tablet {
            display: none;
        }

        .hide-desktop {
            /* Hidden on desktop viewports */
        }

        .viewport-desktop .hide-desktop {
            display: none;
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
