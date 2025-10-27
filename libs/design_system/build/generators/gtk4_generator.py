#!/usr/bin/env python3

"""
GTK4 CSS Generator for Design System
Generates CSS custom properties from semantic design tokens for GTK4 applications.

This generator:
- Converts semantic tokens to CSS custom properties
- Layers over Libadwaita base styling (selective overrides)
- Generates theme-aware CSS files for light/dark variants
- Respects GTK4 conventions and CSS capabilities
- Maintains semantic naming in CSS variable names

Author: Unhinged Team
Version: 1.0.0
Date: 2025-10-27
"""

import logging
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional


class GTK4CSSGenerator:
    """
    Generates GTK4-compatible CSS from semantic design tokens.
    
    Follows designer specifications:
    - Semantic tokens as CSS custom properties
    - Light/dark theme variants
    - Selective overrides over Libadwaita base
    - WCAG contrast validation preserved
    """
    
    def __init__(self, tokens_dir: Path, output_dir: Path):
        self.tokens_dir = tokens_dir
        self.output_dir = output_dir
        self.tokens: Dict[str, Any] = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
    def load_tokens(self) -> None:
        """Load all semantic token files"""
        token_files = [
            'colors.yaml',
            'typography.yaml',
            'spacing.yaml',
            'elevation.yaml',
            'motion.yaml',
            'components.yaml'
        ]

        for token_file in token_files:
            token_path = self.tokens_dir / token_file
            if token_path.exists():
                try:
                    with open(token_path, 'r', encoding='utf-8') as f:
                        token_name = token_file.replace('.yaml', '')
                        self.tokens[token_name] = yaml.safe_load(f)
                        self.logger.debug(f"Loaded tokens from {token_file}")
                except Exception as e:
                    self.logger.error(f"Failed to load {token_file}: {e}")
                    raise
            else:
                self.logger.warning(f"Token file not found: {token_path}")
    
    def generate_css(self) -> Dict[str, str]:
        """Generate CSS files for GTK4"""
        css_files = {}

        # Performance: Generate files in order of dependency
        # Base tokens first (most fundamental)
        self.logger.debug("Generating base CSS with semantic tokens")
        css_files['design-tokens.css'] = self._generate_base_css()

        # Theme variants (depend on base tokens)
        self.logger.debug("Generating theme-specific CSS files")
        css_files['theme-light.css'] = self._generate_theme_css('light')
        css_files['theme-dark.css'] = self._generate_theme_css('dark')

        # Component styles (depend on tokens and themes)
        self.logger.debug("Generating component CSS with semantic token usage")
        css_files['components.css'] = self._generate_component_css()

        self.logger.info(f"Generated {len(css_files)} CSS files for GTK4")
        return css_files
    
    def _generate_base_css(self) -> str:
        """Generate base CSS with semantic token definitions"""
        css_lines = [
            "/* Generated Design Tokens for GTK4 */",
            "/* DO NOT EDIT - Generated from libs/design_system/tokens/ */",
            "/* Semantic tokens as CSS custom properties */",
            "",
            ":root {",
            "  /* === SEMANTIC COLOR TOKENS === */"
        ]
        
        # Colors - semantic structure
        if 'colors' in self.tokens:
            colors = self.tokens['colors']['colors']
            css_lines.extend(self._generate_color_properties(colors))
            css_lines.append("")
        
        # Typography - 5 type sizes
        if 'typography' in self.tokens:
            css_lines.append("  /* === TYPOGRAPHY TOKENS === */")
            css_lines.extend(self._generate_typography_properties())
            css_lines.append("")
        
        # Spacing - 10 spacing values
        if 'spacing' in self.tokens:
            css_lines.append("  /* === SPACING TOKENS === */")
            css_lines.extend(self._generate_spacing_properties())
            css_lines.append("")
        
        # Elevation - 4 shadow depths
        if 'elevation' in self.tokens:
            css_lines.append("  /* === ELEVATION TOKENS === */")
            css_lines.extend(self._generate_elevation_properties())
            css_lines.append("")
        
        css_lines.append("}")
        
        return "\n".join(css_lines)
    
    def _generate_color_properties(self, colors: Dict[str, Any]) -> List[str]:
        """Generate CSS custom properties for semantic colors"""
        properties = []
        
        for category, color_group in colors.items():
            if isinstance(color_group, dict):
                properties.append(f"  /* {category.title()} Colors */")
                for color_name, color_value in color_group.items():
                    if isinstance(color_value, str):
                        # Direct color value
                        properties.append(f"  --color-{category}-{color_name}: {color_value};")
                    elif isinstance(color_value, dict):
                        # Nested color structure (like action.primary.hover)
                        for sub_name, sub_value in color_value.items():
                            if isinstance(sub_value, str):
                                properties.append(f"  --color-{category}-{color_name}-{sub_name}: {sub_value};")
        
        return properties
    
    def _generate_typography_properties(self) -> List[str]:
        """Generate CSS custom properties for typography tokens"""
        properties = []
        
        typography = self.tokens['typography']['typography']
        
        # Font families
        if 'families' in typography:
            properties.append("  /* Font Families */")
            for family_name, family_stack in typography['families'].items():
                if isinstance(family_stack, list):
                    family_value = ', '.join(f'"{font}"' if ' ' in font else font for font in family_stack)
                    properties.append(f"  --font-family-{family_name}: {family_value};")
        
        # Type scale (5 sizes)
        if 'scale' in typography:
            properties.append("  /* Type Scale (5 sizes) */")
            for size_name, size_props in typography['scale'].items():
                if isinstance(size_props, dict):
                    # Font size
                    if 'size' in size_props:
                        properties.append(f"  --font-size-{size_name}: {size_props['size']};")
                    # Line height
                    if 'line_height' in size_props:
                        line_height = typography.get('line_heights', {}).get(size_props['line_height'], size_props['line_height'])
                        properties.append(f"  --line-height-{size_name}: {line_height};")
                    # Font weight
                    if 'weight' in size_props:
                        weight = typography.get('weights', {}).get(size_props['weight'], size_props['weight'])
                        properties.append(f"  --font-weight-{size_name}: {weight};")
                    # Letter spacing
                    if 'letter_spacing' in size_props:
                        spacing = typography.get('letter_spacing', {}).get(size_props['letter_spacing'], size_props['letter_spacing'])
                        properties.append(f"  --letter-spacing-{size_name}: {spacing};")
        
        return properties
    
    def _generate_spacing_properties(self) -> List[str]:
        """Generate CSS custom properties for spacing tokens"""
        properties = []
        
        spacing = self.tokens['spacing']['spacing']
        
        if 'scale' in spacing:
            properties.append("  /* Spacing Scale (10 values, 4px base unit) */")
            for space_name, space_value in spacing['scale'].items():
                # Convert sp_1_5 to sp-1-5 for CSS
                css_name = space_name.replace('_', '-')
                properties.append(f"  --spacing-{css_name}: {space_value};")
        
        return properties
    
    def _generate_elevation_properties(self) -> List[str]:
        """Generate CSS custom properties for elevation tokens"""
        properties = []
        
        elevation = self.tokens['elevation']['elevation']
        
        # Shadows (4 depths)
        if 'shadows' in elevation:
            properties.append("  /* Elevation Shadows (4 depths) */")
            for shadow_level, shadow_props in elevation['shadows'].items():
                if isinstance(shadow_props, dict):
                    # Construct CSS box-shadow from blur, offset, color
                    blur = shadow_props.get('blur', '0px')
                    offset = shadow_props.get('offset', '0px')
                    color = shadow_props.get('color', 'rgba(0,0,0,0.1)')
                    box_shadow = f"0 {offset} {blur} {color}"
                    properties.append(f"  --elevation-{shadow_level}: {box_shadow};")
        
        # Z-index layers
        if 'layers' in elevation:
            properties.append("  /* Z-Index Layers */")
            for layer_name, layer_value in elevation['layers'].items():
                properties.append(f"  --z-index-{layer_name}: {layer_value};")
        
        # Border radius (4 values)
        if 'radius' in elevation:
            properties.append("  /* Border Radius (4 values) */")
            for radius_name, radius_value in elevation['radius'].items():
                properties.append(f"  --radius-{radius_name}: {radius_value};")
        
        # Border width (3 values)
        if 'border' in elevation:
            properties.append("  /* Border Width (3 values) */")
            for border_name, border_value in elevation['border'].items():
                properties.append(f"  --border-{border_name}: {border_value};")
        
        return properties
    
    def _generate_theme_css(self, theme_name: str) -> str:
        """Generate theme-specific CSS overrides"""
        css_lines = [
            f"/* {theme_name.title()} Theme for GTK4 */",
            f"/* Semantic token overrides for {theme_name} theme */",
            "/* Layers over Libadwaita base styling */",
            "",
            f"/* Apply {theme_name} theme */",
            f"[data-theme='{theme_name}'], .theme-{theme_name} {{",
        ]
        
        # Theme-specific color overrides
        if 'colors' in self.tokens and 'themes' in self.tokens['colors']:
            theme_colors = self.tokens['colors']['themes'].get(theme_name, {})
            if theme_colors:
                css_lines.append(f"  /* {theme_name.title()} Theme Colors */")
                for category, color_group in theme_colors.items():
                    if isinstance(color_group, dict):
                        for color_name, color_value in color_group.items():
                            if isinstance(color_value, str):
                                css_lines.append(f"  --color-{category}-{color_name}: {color_value};")
        
        css_lines.append("}")
        
        return "\n".join(css_lines)
    
    def _generate_component_css(self) -> str:
        """Generate component CSS using semantic tokens"""
        css_lines = [
            "/* Component Styles Using Semantic Tokens */",
            "/* GTK4-compatible component patterns */",
            "/* Selective overrides over Libadwaita base */",
            "",
        ]
        
        if 'components' in self.tokens:
            components = self.tokens['components']['components']
            
            # Button component
            if 'button' in components:
                css_lines.extend(self._generate_button_css(components['button']))
                css_lines.append("")
            
            # Form field component
            if 'form_field' in components:
                css_lines.extend(self._generate_form_field_css(components['form_field']))
                css_lines.append("")
            
            # Card component
            if 'card' in components:
                css_lines.extend(self._generate_card_css(components['card']))
                css_lines.append("")
        
        return "\n".join(css_lines)
    
    def _generate_button_css(self, button_config: Dict[str, Any]) -> List[str]:
        """Generate button CSS using semantic tokens"""
        css = [
            "/* Button Component - Semantic Token Usage */",
            "button, .btn {",
            f"  padding: var(--spacing-{button_config['padding']['vertical'].replace('sp_', 'sp-')}) var(--spacing-{button_config['padding']['horizontal'].replace('sp_', 'sp-')});",
            f"  border-radius: var(--{button_config['border_radius'].replace('_', '-')});",
            "  font-family: var(--font-family-prose);",
            "  font-size: var(--font-size-body);",
            "  font-weight: var(--font-weight-body);",
            "  background-color: var(--color-action-primary);",
            "  color: var(--color-text-inverse);",
            "  border: var(--border-thin) solid var(--color-action-primary);",
            f"  min-height: {button_config.get('minimum_height', '44px')};",
            "  cursor: pointer;",
            "  transition: all 150ms ease;",
            "}",
            "",
            "button:hover, .btn:hover {",
            "  box-shadow: var(--elevation-1);",
            "}",
            "",
            "button:active, .btn:active {",
            "  transform: translateY(1px);",
            "}",
            "",
            "button:disabled, .btn:disabled {",
            "  background-color: var(--color-action-disabled);",
            "  color: var(--color-text-disabled);",
            "  cursor: not-allowed;",
            "  opacity: 0.5;",
            "}"
        ]
        return css
    
    def _generate_form_field_css(self, field_config: Dict[str, Any]) -> List[str]:
        """Generate form field CSS using semantic tokens"""
        css = [
            "/* Form Field Component - Semantic Token Usage */",
            "input, textarea, select {",
            f"  padding: var(--spacing-{field_config['padding']['vertical'].replace('sp_', 'sp-')}) var(--spacing-{field_config['padding']['horizontal'].replace('sp_', 'sp-')});",
            f"  border-radius: var(--{field_config['border_radius'].replace('_', '-')});",
            "  border: var(--border-thin) solid var(--color-border-default);",
            "  font-family: var(--font-family-prose);",
            "  font-size: var(--font-size-body);",
            "  background-color: var(--color-surface-default);",
            "  color: var(--color-text-primary);",
            "}",
            "",
            "input:focus, textarea:focus, select:focus {",
            "  border-width: var(--border-medium);",
            "  outline: none;",
            "}",
            "",
            "input::placeholder, textarea::placeholder {",
            "  color: var(--color-text-tertiary);",
            "}"
        ]
        return css
    
    def _generate_card_css(self, card_config: Dict[str, Any]) -> List[str]:
        """Generate card CSS using semantic tokens"""
        css = [
            "/* Card Component - Semantic Token Usage */",
            ".card {",
            f"  padding: var(--spacing-{card_config['padding'].replace('sp_', 'sp-')});",
            f"  border-radius: var(--{card_config['border_radius'].replace('_', '-')});",
            "  background-color: var(--color-surface-elevated);",
            "  border: var(--border-thin) solid var(--color-border-subtle);",
            f"  box-shadow: var(--{card_config['shadow'].replace('.', '-')});",
            "}",
            "",
            ".card:hover {",
            "  box-shadow: var(--elevation-3);",
            "}"
        ]
        return css
