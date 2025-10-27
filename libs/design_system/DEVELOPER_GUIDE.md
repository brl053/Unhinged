# Design System Developer Guide

Quick reference for developers working with the Unhinged design system.

## Quick Start

### 1. Using Semantic Tokens in GTK4

```css
/* Include generated CSS in your GTK4 application */
@import url("generated/design_system/gtk4/design-tokens.css");
@import url("generated/design_system/gtk4/theme-light.css");
@import url("generated/design_system/gtk4/components.css");

/* Use semantic tokens in your styles */
.my-button {
  background-color: var(--color-action-primary);
  color: var(--color-text-inverse);
  padding: var(--spacing-sp-2) var(--spacing-sp-4);
  border-radius: var(--radius-md);
  font-size: var(--font-size-body);
  font-weight: var(--font-weight-medium);
}
```

### 2. Building Design Tokens

```bash
# Generate all design tokens
make design-tokens

# Generate GTK4 CSS specifically  
make design-tokens-gtk4

# Clean and rebuild
make clean-design-tokens && make design-tokens
```

### 3. Theme Switching

```css
/* Light theme (default) */
body {
  /* Uses light theme variables automatically */
}

/* Dark theme */
body[data-theme="dark"] {
  /* Dark theme variables automatically applied */
}

/* Or use CSS classes */
.theme-light { /* light theme */ }
.theme-dark { /* dark theme */ }
```

## Token Reference

### Colors (16 semantic roles)

```css
/* Action Colors - User interactions */
var(--color-action-primary)     /* #0066CC - Main buttons, links */
var(--color-action-secondary)   /* #666666 - Secondary actions */
var(--color-action-tertiary)    /* #999999 - Minimal actions */
var(--color-action-disabled)    /* #CCCCCC - Disabled state */

/* Feedback Colors - System communication */
var(--color-feedback-success)   /* #217A3C - Success states */
var(--color-feedback-warning)   /* #C17A00 - Warning states */
var(--color-feedback-error)     /* #C21E1E - Error states */
var(--color-feedback-info)      /* #0066CC - Info states */

/* Surface Colors - Backgrounds */
var(--color-surface-default)    /* #FFFFFF - Main background */
var(--color-surface-elevated)   /* #F5F5F5 - Cards, modals */
var(--color-surface-overlay)    /* #FFFFFF - Tooltips, dropdowns */
var(--color-surface-inverse)    /* #1A1A1A - Dark backgrounds */

/* Text Colors - Content */
var(--color-text-primary)       /* #1A1A1A - Main text */
var(--color-text-secondary)     /* #666666 - Supporting text */
var(--color-text-tertiary)      /* #999999 - Helper text */
var(--color-text-inverse)       /* #FFFFFF - Text on dark */
var(--color-text-disabled)      /* #CCCCCC - Disabled text */

/* Border Colors - Visual separation */
var(--color-border-default)     /* #D9D9D9 - Standard borders */
var(--color-border-subtle)      /* #F0F0F0 - Soft separation */
var(--color-border-strong)      /* #999999 - Emphasized borders */

/* Interactive States - Overlays (8% opacity) */
var(--color-interactive-hover)  /* #000000 - Hover overlay */
var(--color-interactive-active) /* #000000 - Active overlay */
var(--color-interactive-focus)  /* #0066CC - Focus ring */
```

### Typography (5 type sizes)

```css
/* Type Scale */
var(--font-size-display)        /* 2.25rem - Page titles, hero text */
var(--font-size-heading)        /* 1.5rem - Section headers */
var(--font-size-body)           /* 1rem - Default text */
var(--font-size-caption)        /* 0.875rem - Small text */
var(--font-size-code)           /* 0.875rem - Monospace text */

/* Font Families (2 maximum) */
var(--font-family-prose)        /* Inter stack - UI text */
var(--font-family-code)         /* JetBrains Mono stack - Code */

/* Font Weights (3 weights) */
var(--font-weight-regular)      /* 400 - Normal text */
var(--font-weight-medium)       /* 500 - Emphasized text */
var(--font-weight-bold)         /* 700 - Strong emphasis */

/* Line Heights */
var(--line-height-display)      /* 1.2 - Tight for large text */
var(--line-height-heading)      /* 1.2 - Tight for headers */
var(--line-height-body)         /* 1.5 - Normal for body */
var(--line-height-caption)      /* 1.6 - Loose for small text */
var(--line-height-code)         /* 1.5 - Code readability */
```

### Spacing (10 values, 4px base)

```css
/* Spacing Scale (4px base unit) */
var(--spacing-sp-0-5)           /* 2px - Micro spacing */
var(--spacing-sp-1)             /* 4px - Minimal spacing */
var(--spacing-sp-1-5)           /* 6px - Button padding */
var(--spacing-sp-2)             /* 8px - Standard spacing */
var(--spacing-sp-3)             /* 12px - Section spacing */
var(--spacing-sp-4)             /* 16px - Component spacing */
var(--spacing-sp-5)             /* 20px - Layout spacing */
var(--spacing-sp-6)             /* 24px - Section breaks */
var(--spacing-sp-8)             /* 32px - Major spacing */
var(--spacing-sp-12)            /* 48px - Page margins */
```

### Elevation (4 shadow depths)

```css
/* Shadows */
var(--elevation-1)              /* Subtle lift, hover states */
var(--elevation-2)              /* Cards, floating buttons */
var(--elevation-3)              /* Popovers, tooltips */
var(--elevation-4)              /* Large modals, drawers */

/* Z-Index Layers */
var(--z-index-base)             /* 0 - Document flow */
var(--z-index-raised)           /* 10 - Cards above background */
var(--z-index-floating)         /* 100 - Dropdowns, tooltips */
var(--z-index-modal)            /* 1000 - Modal dialogs */
var(--z-index-notification)     /* 2000 - Toast notifications */

/* Border Radius */
var(--radius-none)              /* 0px - Sharp edges */
var(--radius-sm)                /* 4px - Form elements */
var(--radius-md)                /* 8px - Standard components */
var(--radius-lg)                /* 16px - Large containers */

/* Border Width */
var(--border-thin)              /* 1px - Default borders */
var(--border-medium)            /* 2px - Active states */
var(--border-thick)             /* 4px - Emphasis */
```

## Component Patterns

### Button

```css
.button {
  /* Required properties */
  padding: var(--spacing-sp-2) var(--spacing-sp-4);
  border-radius: var(--radius-md);
  font-family: var(--font-family-prose);
  font-size: var(--font-size-body);
  font-weight: var(--font-weight-medium);
  min-height: 44px; /* Touch target */
  
  /* Primary button */
  background-color: var(--color-action-primary);
  color: var(--color-text-inverse);
  border: var(--border-thin) solid var(--color-action-primary);
}

.button:hover {
  box-shadow: var(--elevation-1);
}

.button:disabled {
  background-color: var(--color-action-disabled);
  color: var(--color-text-disabled);
  opacity: 0.5;
}
```

### Form Field

```css
.form-field {
  padding: var(--spacing-sp-2) var(--spacing-sp-3);
  border-radius: var(--radius-sm);
  border: var(--border-thin) solid var(--color-border-default);
  font-family: var(--font-family-prose);
  font-size: var(--font-size-body);
  background-color: var(--color-surface-default);
  color: var(--color-text-primary);
}

.form-field:focus {
  border-width: var(--border-medium);
  outline: none;
}

.form-field::placeholder {
  color: var(--color-text-tertiary);
}
```

### Card

```css
.card {
  padding: var(--spacing-sp-4);
  border-radius: var(--radius-md);
  background-color: var(--color-surface-elevated);
  border: var(--border-thin) solid var(--color-border-subtle);
  box-shadow: var(--elevation-2);
}

.card:hover {
  box-shadow: var(--elevation-3);
}
```

## Best Practices

### ✅ Do

- Use semantic tokens exclusively
- Follow component composition patterns
- Respect designer constraints (5 type sizes, 16 colors, etc.)
- Test with both light and dark themes
- Maintain 4.5:1 contrast ratios
- Use vertical-dominant margin patterns

### ❌ Don't

- Use hardcoded color values (`#0066CC`)
- Use arbitrary font sizes (`17px`)
- Use random spacing values (`13px`)
- Create more than 2 font families
- Exceed 5 type sizes in the scale
- Use more than 16 semantic color roles

## Troubleshooting

### CSS Variables Not Working

```css
/* Check import order */
@import url("design-tokens.css");     /* Base tokens first */
@import url("theme-light.css");       /* Theme second */
@import url("components.css");        /* Components last */
```

### Theme Switching Issues

```javascript
// Apply theme programmatically
document.body.setAttribute('data-theme', 'dark');

// Or use CSS class
document.body.className = 'theme-dark';
```

### Build Issues

```bash
# Check token validation
python3 libs/design_system/build/design_token_builder.py

# Force rebuild
make clean-design-tokens && make design-tokens

# Check build logs
make design-tokens 2>&1 | grep -i error
```

## Contributing

1. **Edit tokens** in `libs/design_system/tokens/`
2. **Follow constraints** (16 colors, 5 type sizes, etc.)
3. **Validate changes** with build system
4. **Test integration** with existing components
5. **Update documentation** if adding new patterns

## Support

- **Documentation**: `libs/design_system/README.md`
- **Build System**: `build/README.md`
- **Token Validation**: Run DesignTokenBuilder directly
- **CSS Generation**: Check `generated/design_system/gtk4/`
