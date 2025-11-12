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

    def resolve_token(self, token_path: str, context: str = "light") -> str:
        """
        Resolve a design token to its actual value for GTK4 CSS.

        Args:
            token_path: Dot-separated path like "colors.action.primary" or "spacing.scale.sp_2"
            context: Theme context ("light" or "dark")

        Returns:
            Actual CSS value (e.g., "#0066CC", "8px")
        """
        parts = token_path.split('.')
        category = parts[0]  # 'colors', 'spacing', 'elevation'

        # Handle theme-aware color tokens
        if category == 'colors':
            # Try theme-aware resolution first: tokens['colors']['themes'][context][...]
            try:
                value = self.tokens['colors']['themes'][context]
                for part in parts[1:]:
                    value = value[part]
                return str(value)
            except (KeyError, TypeError):
                # Fall back to base color value: tokens['colors']['colors'][...]
                try:
                    value = self.tokens['colors']['colors']
                    for part in parts[1:]:
                        value = value[part]
                    return str(value)
                except (KeyError, TypeError) as e:
                    self.logger.error(f"Failed to resolve color token {token_path}: {e}")
                    raise

        # For non-color tokens (spacing, elevation, etc.)
        # The YAML structure has an extra nesting level: tokens[category][category][...]
        try:
            value = self.tokens[category][category]
            for part in parts[1:]:
                value = value[part]
            return str(value)
        except (KeyError, TypeError) as e:
            self.logger.error(f"Failed to resolve token {token_path}: {e}")
            raise
        
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

        # NOTE: We do NOT generate design-tokens.css or theme-*.css files because GTK4 does not support CSS custom properties.
        # All tokens are resolved at generation time in component CSS files.
        # These files would only contain CSS variables which GTK4 rejects.
        # Theme switching can be implemented via Python code or by regenerating CSS for different themes.

        # Component styles (depend on tokens and themes) - generate for light theme
        self.logger.debug("Generating component CSS with resolved semantic tokens")
        css_files['components.css'] = self._generate_component_css('light')

        self.logger.info(f"Generated {len(css_files)} CSS files for GTK4 with resolved tokens")
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

        # Shadows (4 depths) - GTK4 compatible format
        if 'shadows' in elevation:
            properties.append("  /* Elevation Shadows (GTK4 compatible) */")
            for shadow_level, shadow_props in elevation['shadows'].items():
                if isinstance(shadow_props, dict):
                    # Convert to GTK4-compatible shadow format
                    gtk4_shadow = self._convert_shadow_to_gtk4_format(shadow_props)
                    properties.append(f"  --elevation-{shadow_level}: {gtk4_shadow};")
        
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

    def _convert_shadow_to_gtk4_format(self, shadow_props: Dict) -> str:
        """Convert shadow properties to GTK4-compatible format."""
        # GTK4 has limited box-shadow support, use simple format
        offset = shadow_props.get('offset', '2px').replace('px', '')
        blur = shadow_props.get('blur', '4px').replace('px', '')

        # Convert rgba to alpha() function for GTK4
        color = shadow_props.get('color', 'rgba(0,0,0,0.1)')
        if 'rgba' in color:
            # Extract alpha value and convert to GTK4 alpha() format
            try:
                # Parse rgba(r, g, b, a) format
                rgba_parts = color.replace('rgba(', '').replace(')', '').split(',')
                if len(rgba_parts) == 4:
                    alpha = float(rgba_parts[3].strip())
                    return f"0 {offset}px {blur}px alpha(black, {alpha})"
            except:
                pass

        # Fallback to simple shadow
        return f"0 {offset}px {blur}px alpha(black, 0.1)"
    
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
    
    def _generate_component_css(self, context: str = "light") -> str:
        """Generate component CSS using resolved semantic tokens"""
        css_lines = [
            "/* Component Styles Using Resolved Semantic Tokens */",
            "/* GTK4-compatible component patterns */",
            "/* Selective overrides over Libadwaita base */",
            "",
        ]

        if 'components' in self.tokens:
            components = self.tokens['components']['components']

            # Button component
            if 'button' in components:
                css_lines.extend(self._generate_button_css(components['button'], context))
                css_lines.append("")

            # Form field component
            if 'form_field' in components:
                css_lines.extend(self._generate_form_field_css(components['form_field'], context))
                css_lines.append("")

            # Card component
            if 'card' in components:
                css_lines.extend(self._generate_card_css(components['card'], context))
                css_lines.append("")

        return "\n".join(css_lines)
    
    def _generate_button_css(self, button_config: Dict[str, Any], context: str = "light") -> List[str]:
        """Generate button CSS using resolved semantic tokens"""
        # Resolve tokens to actual values
        vertical_padding = self.resolve_token(f"spacing.scale.{button_config['padding']['vertical']}", context)
        horizontal_padding = self.resolve_token(f"spacing.scale.{button_config['padding']['horizontal']}", context)
        # Strip 'radius_' prefix from border_radius shorthand
        radius_key = button_config['border_radius'].replace('radius_', '')
        border_radius = self.resolve_token(f"elevation.radius.{radius_key}", context)
        action_primary = self.resolve_token("colors.action.primary", context)
        text_inverse = self.resolve_token("colors.text.inverse", context)
        action_disabled = self.resolve_token("colors.action.disabled", context)
        text_disabled = self.resolve_token("colors.text.disabled", context)

        css = [
            "/* Button Component - Resolved Semantic Tokens */",
            "button, .btn {",
            f"  padding: {vertical_padding} {horizontal_padding};",
            f"  border-radius: {border_radius};",
            "  font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;",
            "  font-size: 1rem;",
            "  font-weight: 500;",
            f"  background-color: {action_primary};",
            f"  color: {text_inverse};",
            f"  border: 1px solid {action_primary};",
            f"  min-height: {button_config.get('minimum_height', '44px')};",
            "  transition: all 150ms ease;",
            "}",
            "",
            "button:hover, .btn:hover {",
            "  opacity: 0.9;",
            "}",
            "",
            "button:active, .btn:active {",
            "  opacity: 0.8;",
            "}",
            "",
            "button:disabled, .btn:disabled {",
            f"  background-color: {action_disabled};",
            f"  color: {text_disabled};",
            "  opacity: 0.5;",
            "}"
        ]
        return css
    
    def _generate_form_field_css(self, field_config: Dict[str, Any], context: str = "light") -> List[str]:
        """Generate form field CSS using resolved semantic tokens"""
        # Resolve tokens to actual values
        vertical_padding = self.resolve_token(f"spacing.scale.{field_config['padding']['vertical']}", context)
        horizontal_padding = self.resolve_token(f"spacing.scale.{field_config['padding']['horizontal']}", context)
        # Strip 'radius_' prefix from border_radius shorthand
        radius_key = field_config['border_radius'].replace('radius_', '')
        border_radius = self.resolve_token(f"elevation.radius.{radius_key}", context)
        border_default = self.resolve_token("colors.border.default", context)
        surface_default = self.resolve_token("colors.surface.default", context)
        text_primary = self.resolve_token("colors.text.primary", context)
        text_tertiary = self.resolve_token("colors.text.tertiary", context)

        css = [
            "/* Form Field Component - Resolved Semantic Tokens */",
            "input, textarea, select {",
            f"  padding: {vertical_padding} {horizontal_padding};",
            f"  border-radius: {border_radius};",
            f"  border: 1px solid {border_default};",
            "  font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;",
            "  font-size: 1rem;",
            f"  background-color: {surface_default};",
            f"  color: {text_primary};",
            "}",
            "",
            "input:focus, textarea:focus, select:focus {",
            "  border-width: 2px;",
            "  outline: none;",
            "}"
        ]
        return css
    
    def _generate_card_css(self, card_config: Dict[str, Any], context: str = "light") -> List[str]:
        """Generate card CSS using resolved semantic tokens"""
        # Resolve tokens to actual values
        padding = self.resolve_token(f"spacing.scale.{card_config['padding']}", context)
        # Strip 'radius_' prefix from border_radius shorthand
        radius_key = card_config['border_radius'].replace('radius_', '')
        border_radius = self.resolve_token(f"elevation.radius.{radius_key}", context)
        surface_elevated = self.resolve_token("colors.surface.elevated", context)
        border_subtle = self.resolve_token("colors.border.subtle", context)

        css = [
            "/* Card Component - Resolved Semantic Tokens */",
            ".card {",
            f"  padding: {padding};",
            f"  border-radius: {border_radius};",
            f"  background-color: {surface_elevated};",
            f"  border: 1px solid {border_subtle};",
            "}",
            "",
            ".card:hover {",
            "  opacity: 0.95;",
            "}"
        ]
        return css
