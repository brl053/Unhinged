# Unhinged Design System Specifications
## Scientific Architecture for Cross-Platform UI Development

**Version**: 2.0.0  
**Date**: 2025-10-06  
**Scope**: Complete design system architecture for web/mobile/desktop/OS-level UI

---

## 1. Foundational Principles

### 1.1 Scientific Methodology
- **Etymology-Based Naming**: All tokens derive from English linguistic roots
- **Decimal Measurement System**: Base-10 scaling following metric principles
- **Systematic Categorization**: Hierarchical organization with clear relationships
- **Cross-Platform Abstraction**: Universal tokens that render across UI frameworks

### 1.2 Architectural Goals
- **Operating System Scalability**: From React components to OS-level interfaces
- **Maintainability**: Centralized token system with minimal coupling
- **Performance**: Optimized for runtime theme switching and responsive design
- **Accessibility**: WCAG 2.1 AA compliance by default

---

## 2. Decimal-Based Measurement System

### 2.1 Spatial Units (Etymology: Latin "spatium" = space)
```typescript
// Base unit: pixel (1px) - fundamental measurement
// Decimal scaling: 10^n progression
export const spatial = {
  // Micro scale (sub-pixel)
  millipixel: 0.1,    // 0.1px - hairline borders
  centipixel: 0.5,    // 0.5px - fine details
  
  // Base scale
  pixel: 1,           // 1px - fundamental unit
  decapixel: 10,      // 10px - small spacing
  hectopixel: 100,    // 100px - large spacing
  kilopixel: 1000,    // 1000px - layout dimensions
  
  // Semantic aliases
  hairline: 0.1,      // millipixel
  fine: 0.5,          // centipixel
  base: 1,            // pixel
  small: 10,          // decapixel
  medium: 100,        // hectopixel
  large: 1000,        // kilopixel
} as const;
```

### 2.2 Responsive Breakpoints (Etymology: "break" + "point")
```typescript
export const breakpoints = {
  // Mobile-first progression
  mobile: 0,          // 0px - base mobile
  tablet: 768,        // 768px - tablet portrait
  desktop: 1024,      // 1024px - desktop
  widescreen: 1440,   // 1440px - large desktop
  ultrawide: 1920,    // 1920px - ultra-wide displays
  
  // OS-level scaling
  systemSmall: 1366,  // Small system displays
  systemLarge: 2560,  // Large system displays
} as const;
```

---

## 3. Scientific Color Architecture

### 3.1 Primitive Color Palette (Etymology: "primus" = first)
```typescript
// Base chromatic values - scientifically derived
export const primitiveColors = {
  // Achromatic scale (grayscale)
  achromatic: {
    white: '#ffffff',     // Pure white (RGB: 255,255,255)
    gray100: '#f8f9fa',   // Near white
    gray200: '#e9ecef',   // Light gray
    gray300: '#dee2e6',   // Medium-light gray
    gray400: '#ced4da',   // Medium gray
    gray500: '#adb5bd',   // True middle gray
    gray600: '#6c757d',   // Medium-dark gray
    gray700: '#495057',   // Dark gray
    gray800: '#343a40',   // Very dark gray
    gray900: '#212529',   // Near black
    black: '#000000',     // Pure black (RGB: 0,0,0)
  },
  
  // Chromatic primaries (RGB color model)
  chromatic: {
    // Primary hues (60° intervals on color wheel)
    red: '#dc3545',       // 0° - Red primary
    orange: '#fd7e14',    // 30° - Red-orange
    yellow: '#ffc107',    // 60° - Yellow primary
    green: '#28a745',     // 120° - Green primary
    cyan: '#17a2b8',      // 180° - Cyan primary
    blue: '#007bff',      // 240° - Blue primary
    purple: '#6f42c1',    // 270° - Purple primary
    magenta: '#e83e8c',   // 300° - Magenta primary
  },
} as const;
```

### 3.2 Semantic Color Tokens (Etymology: "semanticus" = meaningful)
```typescript
export const semanticColors = {
  // Intent-based colors
  intent: {
    primary: primitiveColors.chromatic.blue,
    secondary: primitiveColors.achromatic.gray600,
    success: primitiveColors.chromatic.green,
    warning: primitiveColors.chromatic.yellow,
    danger: primitiveColors.chromatic.red,
    info: primitiveColors.chromatic.cyan,
  },
  
  // Context-based colors
  context: {
    background: {
      primary: primitiveColors.achromatic.white,
      secondary: primitiveColors.achromatic.gray100,
      tertiary: primitiveColors.achromatic.gray200,
      inverse: primitiveColors.achromatic.gray900,
    },
    text: {
      primary: primitiveColors.achromatic.gray900,
      secondary: primitiveColors.achromatic.gray700,
      tertiary: primitiveColors.achromatic.gray600,
      inverse: primitiveColors.achromatic.white,
      disabled: primitiveColors.achromatic.gray400,
    },
    border: {
      primary: primitiveColors.achromatic.gray300,
      secondary: primitiveColors.achromatic.gray200,
      focus: primitiveColors.chromatic.blue,
      error: primitiveColors.chromatic.red,
    },
  },
} as const;
```

---

## 4. Typography Architecture

### 4.1 Font System (Etymology: "typographia" = writing impression)
```typescript
export const typography = {
  // Font families with fallback stacks
  families: {
    primary: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    secondary: '"Roboto Mono", "SF Mono", Monaco, "Cascadia Code", monospace',
    system: 'system-ui, -apple-system, BlinkMacSystemFont, sans-serif',
  },
  
  // Modular scale (1.250 - Major Third)
  scale: {
    micro: 0.64,        // 10.24px at 16px base
    small: 0.8,         // 12.8px at 16px base
    base: 1,            // 16px base
    medium: 1.25,       // 20px at 16px base
    large: 1.563,       // 25px at 16px base
    xlarge: 1.953,      // 31.25px at 16px base
    xxlarge: 2.441,     // 39.06px at 16px base
    xxxlarge: 3.052,    // 48.83px at 16px base
  },
  
  // Semantic font sizes
  semantic: {
    caption: 'micro',
    body: 'base',
    subtitle: 'medium',
    title: 'large',
    heading: 'xlarge',
    display: 'xxlarge',
    hero: 'xxxlarge',
  },
} as const;
```

### 4.2 Line Height System (Etymology: "linea" = line)
```typescript
export const lineHeight = {
  // Proportional to font size
  tight: 1.2,         // Headings, tight spacing
  base: 1.5,          // Body text, optimal readability
  loose: 1.8,         // Relaxed reading, accessibility
  
  // Semantic aliases
  heading: 'tight',
  body: 'base',
  caption: 'loose',
} as const;
```

---

## 5. Component Token Architecture

### 5.1 Component Variants (Etymology: "varians" = changing)
```typescript
export const componentTokens = {
  // Button component tokens
  button: {
    // Size variants
    size: {
      small: {
        padding: `${spatial.decapixel * 0.5}px ${spatial.decapixel}px`,
        fontSize: typography.scale.small,
        borderRadius: spatial.decapixel * 0.4,
      },
      medium: {
        padding: `${spatial.decapixel * 0.75}px ${spatial.decapixel * 1.5}px`,
        fontSize: typography.scale.base,
        borderRadius: spatial.decapixel * 0.6,
      },
      large: {
        padding: `${spatial.decapixel}px ${spatial.decapixel * 2}px`,
        fontSize: typography.scale.medium,
        borderRadius: spatial.decapixel * 0.8,
      },
    },
    
    // Intent variants
    intent: {
      primary: {
        background: semanticColors.intent.primary,
        color: semanticColors.context.text.inverse,
        border: semanticColors.intent.primary,
      },
      secondary: {
        background: 'transparent',
        color: semanticColors.intent.primary,
        border: semanticColors.intent.primary,
      },
    },
  },
} as const;
```

---

## 6. Animation & Motion System

### 6.1 Duration Scale (Etymology: "durare" = to last)
```typescript
export const duration = {
  // Decimal progression in milliseconds
  instant: 0,         // 0ms - immediate
  swift: 100,         // 100ms - quick feedback
  moderate: 250,      // 250ms - standard transitions
  deliberate: 500,    // 500ms - emphasized changes
  extended: 1000,     // 1000ms - dramatic effects
  
  // Semantic aliases
  hover: 'swift',
  focus: 'moderate',
  modal: 'deliberate',
} as const;
```

### 6.2 Easing Functions (Etymology: "ease" = comfort)
```typescript
export const easing = {
  // CSS cubic-bezier functions
  linear: 'linear',
  easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
  easeOut: 'cubic-bezier(0, 0, 0.2, 1)',
  easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
  
  // Semantic aliases
  entrance: 'easeOut',
  exit: 'easeIn',
  transition: 'easeInOut',
} as const;
```

---

## 7. Cross-Platform Abstractions

### 7.1 Platform-Specific Adaptations
```typescript
// Platform detection and adaptation
export const platformTokens = {
  web: {
    // CSS-specific tokens
    boxShadow: {
      small: `0 ${spatial.pixel}px ${spatial.decapixel * 0.3}px rgba(0,0,0,0.1)`,
      medium: `0 ${spatial.decapixel * 0.4}px ${spatial.decapixel * 0.8}px rgba(0,0,0,0.15)`,
      large: `0 ${spatial.decapixel * 0.8}px ${spatial.decapixel * 2.5}px rgba(0,0,0,0.2)`,
    },
    borderRadius: {
      small: spatial.decapixel * 0.4,
      medium: spatial.decapixel * 0.8,
      large: spatial.decapixel * 1.2,
    },
  },

  mobile: {
    // Touch-optimized tokens
    minTouchTarget: spatial.decapixel * 4.4, // 44px minimum
    touchPadding: spatial.decapixel * 1.6,   // 16px touch padding
  },

  desktop: {
    // Desktop-specific tokens
    windowChrome: spatial.decapixel * 3.2,   // 32px title bar
    menuHeight: spatial.decapixel * 2.8,     // 28px menu items
  },
} as const;
```

### 7.2 Responsive Design Tokens
```typescript
export const responsiveTokens = {
  // Container max-widths
  container: {
    mobile: '100%',
    tablet: '768px',
    desktop: '1024px',
    widescreen: '1200px',
  },

  // Grid system
  grid: {
    columns: 12,
    gutter: spatial.decapixel * 2, // 20px
    margin: spatial.decapixel * 1.6, // 16px
  },
} as const;
```

---

## 8. Theme Architecture

### 8.1 Complete Theme Interface
```typescript
export interface UnhingedTheme {
  // Core systems
  spatial: typeof spatial;
  colors: {
    primitive: typeof primitiveColors;
    semantic: typeof semanticColors;
  };
  typography: typeof typography;

  // Component tokens
  components: typeof componentTokens;

  // Motion system
  motion: {
    duration: typeof duration;
    easing: typeof easing;
  };

  // Platform adaptations
  platform: typeof platformTokens;
  responsive: typeof responsiveTokens;

  // Theme metadata
  meta: {
    name: string;
    version: string;
    mode: 'light' | 'dark' | 'auto';
  };
}
```

### 8.2 Theme Composition Strategy
```typescript
// Composable theme factory
export const createTheme = (overrides?: Partial<UnhingedTheme>): UnhingedTheme => ({
  spatial,
  colors: {
    primitive: primitiveColors,
    semantic: semanticColors,
  },
  typography,
  components: componentTokens,
  motion: {
    duration,
    easing,
  },
  platform: platformTokens,
  responsive: responsiveTokens,
  meta: {
    name: 'Unhinged Design System',
    version: '2.0.0',
    mode: 'light',
  },
  ...overrides,
});
```

---

## 9. Implementation Requirements

### 9.1 Technical Stack Integration
- **React**: styled-components with theme provider
- **TypeScript**: Complete type safety for all tokens
- **CSS Custom Properties**: Runtime theme switching capability
- **PostCSS**: Build-time optimizations and vendor prefixes

### 9.2 Performance Considerations
- **Tree Shaking**: Modular token imports
- **CSS-in-JS Optimization**: Static extraction where possible
- **Runtime Efficiency**: Minimal theme switching overhead
- **Bundle Size**: Optimized token delivery

### 9.3 Accessibility Compliance
- **WCAG 2.1 AA**: All color combinations meet contrast requirements
- **Focus Management**: Consistent focus indicators across components
- **Screen Reader Support**: Semantic HTML with proper ARIA attributes
- **Motion Preferences**: Respect `prefers-reduced-motion` settings

---

**Next Phase**: Implementation Plan & Migration Strategy
