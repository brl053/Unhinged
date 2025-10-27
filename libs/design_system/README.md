# Unhinged Design System

A two-tier design system architecture providing semantic design tokens and platform-specific generation for consistent styling across the Unhinged platform.

## Architecture Overview

The design system follows a **two-tier architecture** based on industry best practices:

- **Tier 1 (Abstraction Layer)**: Platform-agnostic semantic design tokens serving as the single source of truth
- **Tier 2 (Platform Implementation)**: Generated platform-specific implementations from the abstraction layer

This approach follows our established polyglot pattern: abstraction → platform-specific generation (similar to protobuf → language clients).

## Designer Constraints

The system implements strict constraints to ensure consistency and maintainability:

### Color System (16 semantic roles)
- **Action Colors**: `primary`, `secondary`, `tertiary`, `disabled`
- **Feedback Colors**: `success`, `warning`, `error`, `info`  
- **Surface Colors**: `default`, `elevated`, `overlay`, `inverse`
- **Text Colors**: `primary`, `secondary`, `tertiary`, `inverse`, `disabled`
- **Border Colors**: `default`, `subtle`, `strong`
- **Interactive States**: `hover`, `active`, `focus`

### Typography System (5 type sizes, 3 weights, 2 families)
- **Type Scale**: `display`, `heading`, `body`, `caption`, `code`
- **Weights**: `regular` (400), `medium` (500), `bold` (700)
- **Families**: `prose` (Inter stack), `code` (JetBrains Mono stack)

### Spacing System (10 values, 4px base unit)
- **Scale**: `sp_0_5` (2px) through `sp_12` (48px)
- **Base Unit**: 4px atomic unit
- **Pattern**: Vertical-dominant margins, horizontal follows vertical

### Elevation System (4 shadow depths)
- **Shadows**: `1`, `2`, `3`, `4` (increasing depth)
- **Z-Index Layers**: `base`, `raised`, `floating`, `modal`, `notification`
- **Border Radius**: `none`, `sm`, `md`, `lg`

## Directory Structure

```
libs/design_system/
├── README.md                    # This file
├── tokens/                      # Tier 1: Semantic token definitions
│   ├── colors.yaml             # 16 semantic color roles + themes
│   ├── typography.yaml         # 5 type sizes, font families
│   ├── spacing.yaml            # 10 spacing values, 4px base
│   ├── elevation.yaml          # 4 shadow depths, z-index layers
│   ├── motion.yaml             # Interaction states system
│   └── components.yaml         # Component composition primitives
├── build/                       # Tier 2: Platform generators
│   ├── design_token_builder.py # Build system integration
│   ├── generators/
│   │   └── gtk4_generator.py   # GTK4 CSS generation
│   └── test_*.py               # Test scripts
└── generated/                   # Generated platform artifacts
    └── gtk4/                   # GTK4 CSS output
        ├── design-tokens.css   # Base semantic tokens
        ├── theme-light.css     # Light theme overrides
        ├── theme-dark.css      # Dark theme overrides
        └── components.css      # Component styles
```

## Usage

### Semantic Token Contract

Applications **must** use semantic tokens only, never hardcoded values:

```css
/* ✅ Correct - semantic token usage */
.button {
  background-color: var(--color-action-primary);
  padding: var(--spacing-sp-2) var(--spacing-sp-4);
  border-radius: var(--radius-md);
}

/* ❌ Incorrect - hardcoded values */
.button {
  background-color: #0066CC;
  padding: 8px 16px;
  border-radius: 8px;
}
```

### Build Integration

The design system integrates with the build orchestrator:

```bash
# Generate all design tokens
make design-tokens

# Generate GTK4-specific CSS
make design-tokens-gtk4

# Clean generated artifacts
make clean-design-tokens
```

### Build Targets

- `design-tokens`: Generate all platform artifacts
- `design-tokens-gtk4`: Generate GTK4 CSS specifically
- `design-system`: Alias for design-tokens
- `css-tokens`: Alias for GTK4 generation

## GTK4 Integration

The generated CSS files layer over Libadwaita base styling with selective overrides:

```css
/* Include in your GTK4 application */
@import url("generated/design_system/gtk4/design-tokens.css");
@import url("generated/design_system/gtk4/theme-light.css");
@import url("generated/design_system/gtk4/components.css");
```

### Theme Switching

```css
/* Apply dark theme */
body[data-theme="dark"] {
  /* Dark theme variables automatically applied */
}

/* Or use CSS class */
.theme-dark {
  /* Dark theme variables automatically applied */
}
```

## Development

### Adding New Tokens

1. **Edit semantic token files** in `tokens/` directory
2. **Follow designer constraints** (16 colors, 5 type sizes, etc.)
3. **Maintain WCAG contrast ratios** (4.5:1 minimum)
4. **Run validation**: `python3 libs/design_system/build/design_token_builder.py`
5. **Regenerate CSS**: Build system automatically detects changes

### Token Validation

The system validates tokens against designer constraints:

```python
# Automatic validation during build
builder = DesignTokenBuilder(context)
is_valid, errors = builder.validate_tokens()
```

### Extending to New Platforms

1. **Create new generator** in `build/generators/`
2. **Follow GTK4Generator pattern**
3. **Add platform support** to DesignTokenBuilder
4. **Update build targets** in build-config.yml

## Accessibility

All tokens maintain accessibility requirements:

- **Color Contrast**: 4.5:1 minimum for normal text, 3:1 for large text
- **Focus Indicators**: 3:1 contrast minimum, always visible
- **Motion Preferences**: Respects `prefers-reduced-motion`
- **Touch Targets**: 44px minimum for interactive elements

## Performance

- **Build-time generation**: Zero runtime cost for native applications
- **Intelligent caching**: Only regenerates when source tokens change
- **Dependency tracking**: Monitors token files and generator source
- **Parallel generation**: Supports concurrent platform generation

## Contributing

1. **Follow semantic naming**: Use intent-based tokens (`action.primary` not `blue.500`)
2. **Respect constraints**: Don't exceed designer limits (5 type sizes, 16 colors, etc.)
3. **Validate changes**: Run token validation before committing
4. **Update documentation**: Keep examples and usage patterns current
5. **Test integration**: Verify changes don't break existing components

## Migration Guide

### From Hardcoded Values

Replace hardcoded styling with semantic tokens:

```diff
- color: #0066CC;
+ color: var(--color-action-primary);

- font-size: 16px;
+ font-size: var(--font-size-body);

- margin: 8px;
+ margin: var(--spacing-sp-2);
```

### Theme Support

Update components to support theme switching:

```css
.component {
  /* Use semantic tokens - themes automatically applied */
  background-color: var(--color-surface-default);
  color: var(--color-text-primary);
  border: var(--border-thin) solid var(--color-border-default);
}
```

## Troubleshooting

### Build Issues

- **Token validation fails**: Check constraints in token YAML files
- **CSS not generated**: Verify build dependencies and file permissions
- **Cache issues**: Run clean target and rebuild

### Integration Issues

- **Styles not applied**: Check CSS import order and specificity
- **Theme switching broken**: Verify theme class/attribute application
- **Missing variables**: Ensure all tokens are defined in both light/dark themes

## References

- [Designer Specifications](../docs/design-system-specs.md)
- [Build System Integration](../../build/README.md)
- [GTK4 CSS Documentation](https://docs.gtk.org/gtk4/css-overview.html)
- [WCAG Accessibility Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
