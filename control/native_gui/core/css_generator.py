"""
@llm-type css-generator
@llm-legend Shared CSS Generator - Consolidated CSS generation for mobile UI framework
@llm-key Provides unified CSS generation logic to eliminate duplication across theme and build systems
@llm-map Central CSS generation component in Unhinged native GUI architecture
@llm-axiom CSS generation must be consistent and follow GTK4 theming conventions
@llm-contract Provides standardized CSS generation interface for themes and build system
@llm-token css_generator: Unified CSS generation system for mobile-responsive UI framework
"""

from typing import Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum


class CSSVariant(Enum):
    """CSS variant types for different styling approaches"""
    MOBILE_FIRST = "mobile_first"
    DESKTOP_FIRST = "desktop_first"
    COMPONENT_SPECIFIC = "component_specific"


@dataclass
class CSSConfig:
    """
    @llm-type configuration
    @llm-legend CSS generation configuration with responsive design parameters
    @llm-key Defines CSS generation parameters for consistent styling across viewports
    """
    # Typography
    base_font_size: int = 14
    mobile_font_scale: float = 1.1
    
    # Spacing
    base_spacing: int = 12
    mobile_spacing_scale: float = 0.8
    
    # Colors (GTK4 theme-aware)
    primary_color: str = "#007AFF"
    secondary_color: str = "#5856D6"
    success_color: str = "#34C759"
    warning_color: str = "#FF9500"
    error_color: str = "#FF3B30"
    
    # Responsive breakpoints
    mobile_breakpoint: int = 768
    tablet_breakpoint: int = 1024
    desktop_breakpoint: int = 1920
    
    # Touch optimization
    min_touch_target: int = 44
    touch_padding: int = 12
    border_radius: int = 8


class CSSGenerator:
    """
    @llm-type generator-class
    @llm-legend Unified CSS generator for mobile-responsive UI framework
    @llm-key Consolidates CSS generation logic from theme manager and mobile UI builder
    @llm-map Central CSS generation system for Unhinged native GUI with mobile support
    @llm-axiom CSS generation must be consistent and eliminate duplication
    @llm-contract Provides unified CSS generation interface for all styling needs
    @llm-token CSSGenerator: Consolidated CSS generation system for mobile-first responsive design
    
    Unified CSS generator that consolidates duplicate CSS generation logic
    from both theme_manager.py and mobile_ui_builder.py.
    """
    
    def __init__(self, config: Optional[CSSConfig] = None):
        self.config = config or CSSConfig()
    
    def generate_mobile_css(self) -> str:
        """
        @llm-type method
        @llm-legend Generate mobile-first base CSS
        @llm-key Creates mobile-optimized CSS with touch-friendly controls
        """
        mobile_font_size = int(self.config.base_font_size * self.config.mobile_font_scale)
        mobile_spacing = int(self.config.base_spacing * self.config.mobile_spacing_scale)
        
        return f"""
/* Mobile-first base styles */
/* @llm-type generated-css */
/* @llm-legend Mobile-optimized CSS with touch-friendly controls */
/* @llm-key Base mobile styling for responsive UI framework */

.mobile-optimized {{
    padding: {mobile_spacing}px;
    margin: {mobile_spacing // 2}px;
}}

.viewport-mobile {{
    font-size: {mobile_font_size}px;
    padding: {mobile_spacing}px;
}}

.touch-button {{
    min-height: {self.config.min_touch_target}px;
    min-width: {self.config.min_touch_target}px;
    padding: {self.config.touch_padding}px;
    border-radius: {self.config.border_radius}px;
    transition: all 150ms ease;
}}

.touch-button:hover {{
    background-color: alpha(@theme_fg_color, 0.1);
}}

.touch-button.pressed {{
    background-color: alpha(@theme_fg_color, 0.2);
    transform: scale(0.95);
}}

.touch-button:active {{
    transform: scale(0.95);
    background-color: alpha(@theme_fg_color, 0.1);
}}

.card {{
    background-color: @theme_base_color;
    border-radius: calc({self.config.border_radius}px * 1.5);
    box-shadow: 0 2px 8px alpha(@theme_fg_color, 0.1);
    margin: {mobile_spacing}px;
    padding: {self.config.base_spacing}px;
    transition: all 200ms ease;
}}

.card:hover {{
    box-shadow: 0 4px 16px alpha(@theme_fg_color, 0.15);
    transform: translateY(-2px);
}}

.card-title {{
    font-weight: bold;
    font-size: 1.2em;
    margin-bottom: 4px;
}}

.card-subtitle {{
    opacity: 0.7;
    font-size: 0.9em;
    margin-bottom: {self.config.base_spacing}px;
}}
"""
    
    def generate_responsive_css(self) -> str:
        """
        @llm-type method
        @llm-legend Generate responsive breakpoint CSS
        @llm-key Creates responsive media queries for mobile-first design
        """
        return f"""
/* Responsive breakpoints */
/* @llm-type responsive-css */
/* @llm-legend Responsive media queries for mobile-first design */
/* @llm-key Breakpoint-based styling for different viewport sizes */

@media (max-width: {self.config.mobile_breakpoint}px) {{
    .desktop-only {{ opacity: 0; }}
    .mobile-hidden {{ opacity: 0; }}
    
    .mobile-only {{
        opacity: 1;
        pointer-events: auto;
    }}
    
    .responsive-grid {{
        grid-template-columns: 1fr;
        gap: {int(self.config.base_spacing * self.config.mobile_spacing_scale)}px;
    }}
    
    .responsive-spacing {{
        padding: {int(self.config.base_spacing * self.config.mobile_spacing_scale)}px;
        margin: {int(self.config.base_spacing * self.config.mobile_spacing_scale // 2)}px;
    }}
}}

@media (min-width: {self.config.mobile_breakpoint}px) and (max-width: {self.config.tablet_breakpoint}px) {{
    .mobile-only {{ opacity: 0; }}
    .desktop-only {{ opacity: 0; }}
    
    .tablet-only {{
        opacity: 1;
        pointer-events: auto;
    }}
    
    .responsive-grid {{
        grid-template-columns: repeat(2, 1fr);
        gap: {self.config.base_spacing}px;
    }}
    
    .responsive-spacing {{
        padding: {self.config.base_spacing}px;
        margin: {self.config.base_spacing // 2}px;
    }}
}}

@media (min-width: {self.config.tablet_breakpoint}px) {{
    .mobile-only {{ opacity: 0; }}
    .tablet-only {{ opacity: 0; }}
    
    .desktop-only {{
        opacity: 1;
        pointer-events: auto;
    }}
    
    .responsive-grid {{
        grid-template-columns: repeat(3, 1fr);
        gap: {self.config.base_spacing + 4}px;
    }}
    
    .responsive-spacing {{
        padding: {self.config.base_spacing + 4}px;
        margin: {self.config.base_spacing}px;
    }}
}}
"""
    
    def generate_component_css(self) -> str:
        """
        @llm-type method
        @llm-legend Generate component-specific CSS
        @llm-key Creates styling for UI components with consistent design tokens
        """
        return f"""
/* Component-specific styles */
/* @llm-type component-css */
/* @llm-legend Component styling with consistent design tokens */
/* @llm-key Standardized component appearance and behavior */

.status-indicator {{
    padding: {self.config.base_spacing // 2}px {self.config.base_spacing}px;
    border-radius: {self.config.border_radius // 2}px;
    font-size: {self.config.base_font_size}px;
}}

.status-indicator.status-success {{
    background-color: alpha({self.config.success_color}, 0.1);
    color: {self.config.success_color};
}}

.status-indicator.status-warning {{
    background-color: alpha({self.config.warning_color}, 0.1);
    color: {self.config.warning_color};
}}

.status-indicator.status-error {{
    background-color: alpha({self.config.error_color}, 0.1);
    color: {self.config.error_color};
}}

.metric-value {{
    font-size: 2em;
    font-weight: bold;
    line-height: 1;
}}

.trend-positive {{
    color: {self.config.success_color};
}}

.trend-negative {{
    color: {self.config.error_color};
}}

.loading-spinner {{
    padding: {self.config.base_spacing * 2}px;
}}

.empty-state {{
    padding: {self.config.base_spacing * 2}px;
}}

.empty-state-icon {{
    opacity: 0.6;
}}

.empty-state-title {{
    font-weight: bold;
    font-size: 1.2em;
}}

.empty-state-subtitle {{
    opacity: 0.7;
}}
"""

    def generate_high_contrast_css(self) -> str:
        """
        @llm-type method
        @llm-legend Generate high contrast accessibility CSS
        @llm-key Creates accessibility-focused high contrast styling
        """
        return f"""
/* High contrast theme overrides */
/* @llm-type accessibility-css */
/* @llm-legend High contrast styling for accessibility */
/* @llm-key Enhanced contrast for better visibility */

:root {{
    --primary-color: #0066CC;
    --success-color: #008800;
    --warning-color: #CC6600;
    --error-color: #CC0000;
}}

button {{
    border: 2px solid @theme_fg_color;
}}

.card {{
    border: 1px solid @theme_fg_color;
}}

.status-indicator {{
    border: 1px solid currentColor;
}}

.touch-button {{
    border: 2px solid @theme_fg_color;
    font-weight: bold;
}}
"""

    def generate_navigation_css(self) -> str:
        """
        @llm-type method
        @llm-legend Generate navigation-specific CSS
        @llm-key Creates mobile-friendly navigation styling
        """
        return f"""
/* Navigation styles */
/* @llm-type navigation-css */
/* @llm-legend Mobile-friendly navigation styling */
/* @llm-key Touch-optimized navigation components */

.bottom-tab-bar {{
    border-top: 1px solid alpha(@theme_fg_color, 0.1);
    background-color: @theme_base_color;
    padding: {self.config.base_spacing // 2}px;
}}

.side-tab-bar {{
    border-right: 1px solid alpha(@theme_fg_color, 0.1);
    background-color: @theme_base_color;
    padding: {self.config.base_spacing}px;
}}

.nav-item {{
    min-height: {self.config.min_touch_target}px;
    padding: {self.config.touch_padding}px;
    border-radius: {self.config.border_radius}px;
    transition: all 150ms ease;
}}

.nav-item:hover {{
    background-color: alpha(@theme_fg_color, 0.1);
}}

.nav-item.active {{
    background-color: alpha({self.config.primary_color}, 0.2);
    color: {self.config.primary_color};
}}

.sidebar {{
    border-right: 1px solid alpha(@theme_fg_color, 0.1);
    background-color: @theme_base_color;
    padding: {self.config.base_spacing}px;
}}
"""

    def generate_complete_css(self, include_high_contrast: bool = False) -> str:
        """
        @llm-type method
        @llm-legend Generate complete CSS combining all components
        @llm-key Creates unified CSS output with all styling components
        """
        css_parts = [
            "/* Mobile UI Framework CSS - Generated by CSSGenerator */",
            "/* @llm-type complete-css */",
            "/* @llm-legend Complete mobile-first responsive CSS */",
            "/* @llm-key Unified CSS for mobile-responsive UI framework */",
            "",
            self.generate_mobile_css(),
            "",
            self.generate_responsive_css(),
            "",
            self.generate_component_css(),
            "",
            self.generate_navigation_css()
        ]

        if include_high_contrast:
            css_parts.extend([
                "",
                self.generate_high_contrast_css()
            ])

        return "\n".join(css_parts)
