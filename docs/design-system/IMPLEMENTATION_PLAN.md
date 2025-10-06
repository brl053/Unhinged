# Design System Implementation Plan
## Migration Strategy from basicTheme to Scientific Design System

**Version**: 2.0.0  
**Date**: 2025-10-06  
**Scope**: Complete migration strategy with backward compatibility

---

## 1. Implementation Phases

### Phase 1: Foundation Layer (Week 1-2)
**Objective**: Establish core token architecture without breaking existing components

#### 1.1 Create New Design System Structure
```
frontend/src/design_system/
├── tokens/
│   ├── spatial.ts          # Decimal-based measurements
│   ├── colors.ts           # Scientific color architecture
│   ├── typography.ts       # Modular scale system
│   ├── motion.ts           # Animation tokens
│   └── index.ts            # Token exports
├── themes/
│   ├── light.ts            # Light theme composition
│   ├── dark.ts             # Dark theme composition
│   └── index.ts            # Theme exports
├── components/
│   ├── button.ts           # Button component tokens
│   ├── input.ts            # Input component tokens
│   └── index.ts            # Component token exports
├── utils/
│   ├── responsive.ts       # Responsive utilities
│   ├── platform.ts         # Platform detection
│   └── index.ts            # Utility exports
└── index.ts                # Main design system export
```

#### 1.2 Backward Compatibility Layer
```typescript
// frontend/src/design_system/legacy/compatibility.ts
import { UnhingedTheme } from '../themes';

// Map new tokens to old theme structure
export const createLegacyTheme = (theme: UnhingedTheme) => ({
  name: theme.meta.name,
  color: {
    palette: {
      white: theme.colors.primitive.achromatic.white,
    },
    text: {
      primary: theme.colors.semantic.context.text.primary,
      secondary: theme.colors.semantic.context.text.secondary,
    },
    background: {
      primary: theme.colors.semantic.context.background.primary,
      secondary: theme.colors.semantic.context.background.secondary,
      hovered: theme.colors.semantic.context.background.tertiary,
    },
    border: {
      primary: theme.colors.semantic.context.border.primary,
      secondary: theme.colors.semantic.context.border.secondary,
    },
  },
  fonts: {
    main: theme.typography.families.primary,
    heading: theme.typography.families.primary,
  },
});
```

### Phase 2: Token Implementation (Week 3-4)
**Objective**: Implement all design tokens with TypeScript safety

#### 2.1 Spatial Token Implementation
```typescript
// frontend/src/design_system/tokens/spatial.ts
export const spatial = {
  // Decimal-based measurements
  millipixel: 0.1,
  centipixel: 0.5,
  pixel: 1,
  decapixel: 10,
  hectopixel: 100,
  kilopixel: 1000,
  
  // Semantic spacing scale
  spacing: {
    none: 0,
    xs: 4,    // 0.4 * decapixel
    sm: 8,    // 0.8 * decapixel
    md: 16,   // 1.6 * decapixel
    lg: 24,   // 2.4 * decapixel
    xl: 32,   // 3.2 * decapixel
    xxl: 48,  // 4.8 * decapixel
  },
} as const;

// Type-safe spacing function
export const spacing = (value: keyof typeof spatial.spacing) => 
  `${spatial.spacing[value]}px`;
```

#### 2.2 Color Token Implementation
```typescript
// frontend/src/design_system/tokens/colors.ts
export const primitiveColors = {
  achromatic: {
    white: '#ffffff',
    gray100: '#f8f9fa',
    gray200: '#e9ecef',
    gray300: '#dee2e6',
    gray400: '#ced4da',
    gray500: '#adb5bd',
    gray600: '#6c757d',
    gray700: '#495057',
    gray800: '#343a40',
    gray900: '#212529',
    black: '#000000',
  },
  chromatic: {
    red: '#dc3545',
    orange: '#fd7e14',
    yellow: '#ffc107',
    green: '#28a745',
    cyan: '#17a2b8',
    blue: '#007bff',
    purple: '#6f42c1',
    magenta: '#e83e8c',
  },
} as const;

export const semanticColors = {
  intent: {
    primary: primitiveColors.chromatic.blue,
    secondary: primitiveColors.achromatic.gray600,
    success: primitiveColors.chromatic.green,
    warning: primitiveColors.chromatic.yellow,
    danger: primitiveColors.chromatic.red,
    info: primitiveColors.chromatic.cyan,
  },
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

### Phase 3: Component Migration (Week 5-8)
**Objective**: Migrate existing components to use new design tokens

#### 3.1 Component Token System
```typescript
// frontend/src/design_system/components/button.ts
import { spatial, semanticColors, typography } from '../tokens';

export const buttonTokens = {
  size: {
    small: {
      padding: `${spatial.spacing.xs}px ${spatial.spacing.sm}px`,
      fontSize: typography.scale.small,
      minHeight: spatial.decapixel * 3.2, // 32px
    },
    medium: {
      padding: `${spatial.spacing.sm}px ${spatial.spacing.md}px`,
      fontSize: typography.scale.base,
      minHeight: spatial.decapixel * 4.0, // 40px
    },
    large: {
      padding: `${spatial.spacing.md}px ${spatial.spacing.lg}px`,
      fontSize: typography.scale.medium,
      minHeight: spatial.decapixel * 4.8, // 48px
    },
  },
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
} as const;
```

#### 3.2 Styled Component Migration Pattern
```typescript
// Before: Hard-coded values
const OldButton = styled.button`
  padding: 12px 24px;
  background: #007bff;
  color: white;
  border: 1px solid #007bff;
  border-radius: 6px;
`;

// After: Token-based styling
const NewButton = styled.button<{ size: 'small' | 'medium' | 'large'; intent: 'primary' | 'secondary' }>`
  ${({ theme, size, intent }) => {
    const sizeTokens = theme.components.button.size[size];
    const intentTokens = theme.components.button.intent[intent];
    
    return `
      padding: ${sizeTokens.padding};
      font-size: ${sizeTokens.fontSize}rem;
      min-height: ${sizeTokens.minHeight}px;
      background: ${intentTokens.background};
      color: ${intentTokens.color};
      border: 1px solid ${intentTokens.border};
      border-radius: ${theme.spatial.spacing.xs}px;
      transition: all ${theme.motion.duration.swift}ms ${theme.motion.easing.transition};
    `;
  }}
`;
```

---

## 2. Migration Strategy

### 2.1 Gradual Migration Approach
1. **Dual Theme Support**: Run old and new themes simultaneously
2. **Component-by-Component**: Migrate one component at a time
3. **Feature Flag System**: Toggle between old/new styling per component
4. **Automated Testing**: Ensure visual regression testing

### 2.2 Breaking Change Management
```typescript
// Migration utility for smooth transition
export const migrateComponent = (
  oldProps: OldThemeProps,
  newTheme: UnhingedTheme
): NewThemeProps => {
  return {
    // Map old color props to new semantic tokens
    primaryColor: newTheme.colors.semantic.intent.primary,
    backgroundColor: newTheme.colors.semantic.context.background.primary,
    // Map old spacing to new spatial system
    padding: newTheme.spatial.spacing.md,
    margin: newTheme.spatial.spacing.sm,
  };
};
```

---

## 3. Implementation Timeline

### Week 1-2: Foundation
- [ ] Create new design system file structure
- [ ] Implement core token files (spatial, colors, typography)
- [ ] Create backward compatibility layer
- [ ] Set up TypeScript interfaces

### Week 3-4: Token System
- [ ] Complete all design token implementations
- [ ] Create theme composition functions
- [ ] Implement responsive utilities
- [ ] Add platform detection utilities

### Week 5-6: Component Tokens
- [ ] Define component-specific token systems
- [ ] Create component token interfaces
- [ ] Implement button, input, and layout tokens
- [ ] Add motion and animation tokens

### Week 7-8: Migration & Testing
- [ ] Migrate existing components to new system
- [ ] Implement visual regression testing
- [ ] Create migration documentation
- [ ] Performance optimization and bundle analysis

---

## 4. Practical Implementation Examples

### 4.1 New Theme Provider Setup
```typescript
// frontend/src/App.tsx - Updated theme provider
import React from 'react';
import { ThemeProvider } from 'styled-components';
import { createTheme } from './design_system';
import { createLegacyTheme } from './design_system/legacy/compatibility';

const App: React.FC = ({ children }) => {
  const newTheme = createTheme();
  const legacyTheme = createLegacyTheme(newTheme);

  return (
    <ThemeProvider theme={{ ...newTheme, legacy: legacyTheme }}>
      {children}
    </ThemeProvider>
  );
};
```

### 4.2 Component Migration Example
```typescript
// Before: PromptSurgeryPanel with hard-coded values
const OldSurgeryPanel = styled.div`
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border: 2px solid #007bff;
  border-radius: 12px;
  padding: 20px;
  margin: 16px 0;
`;

// After: Using design tokens
const NewSurgeryPanel = styled.div`
  background: linear-gradient(135deg,
    ${({ theme }) => theme.colors.semantic.context.background.primary} 0%,
    ${({ theme }) => theme.colors.semantic.context.background.secondary} 100%
  );
  border: ${({ theme }) => theme.spatial.centipixel * 4}px solid
    ${({ theme }) => theme.colors.semantic.intent.primary};
  border-radius: ${({ theme }) => theme.spatial.spacing.sm}px;
  padding: ${({ theme }) => theme.spatial.spacing.lg}px;
  margin: ${({ theme }) => theme.spatial.spacing.md}px 0;
  transition: all ${({ theme }) => theme.motion.duration.moderate}ms
    ${({ theme }) => theme.motion.easing.transition};
`;
```

### 4.3 Responsive Design Implementation
```typescript
// Responsive utility function
export const responsive = (theme: UnhingedTheme) => ({
  mobile: `@media (min-width: ${theme.responsive.breakpoints.mobile}px)`,
  tablet: `@media (min-width: ${theme.responsive.breakpoints.tablet}px)`,
  desktop: `@media (min-width: ${theme.responsive.breakpoints.desktop}px)`,
});

// Usage in styled components
const ResponsiveContainer = styled.div`
  padding: ${({ theme }) => theme.spatial.spacing.sm}px;

  ${({ theme }) => responsive(theme).tablet} {
    padding: ${theme.spatial.spacing.md}px;
  }

  ${({ theme }) => responsive(theme).desktop} {
    padding: ${theme.spatial.spacing.lg}px;
  }
`;
```

---

## 5. Testing & Validation Strategy

### 5.1 Visual Regression Testing
```typescript
// tests/design-system/visual-regression.test.ts
import { render } from '@testing-library/react';
import { ThemeProvider } from 'styled-components';
import { createTheme } from '../src/design_system';

describe('Design System Visual Regression', () => {
  const theme = createTheme();

  it('should render button variants consistently', () => {
    const { container } = render(
      <ThemeProvider theme={theme}>
        <Button size="small" intent="primary">Small Primary</Button>
        <Button size="medium" intent="secondary">Medium Secondary</Button>
        <Button size="large" intent="primary">Large Primary</Button>
      </ThemeProvider>
    );

    expect(container).toMatchSnapshot();
  });
});
```

### 5.2 Token Validation Tests
```typescript
// tests/design-system/tokens.test.ts
import { spatial, semanticColors, typography } from '../src/design_system/tokens';

describe('Design System Tokens', () => {
  it('should maintain decimal-based spatial relationships', () => {
    expect(spatial.decapixel).toBe(spatial.pixel * 10);
    expect(spatial.hectopixel).toBe(spatial.pixel * 100);
    expect(spatial.kilopixel).toBe(spatial.pixel * 1000);
  });

  it('should provide accessible color contrasts', () => {
    // Test WCAG AA compliance
    const contrast = calculateContrast(
      semanticColors.context.text.primary,
      semanticColors.context.background.primary
    );
    expect(contrast).toBeGreaterThan(4.5); // WCAG AA standard
  });
});
```

---

## 6. Performance Optimization

### 6.1 Bundle Size Optimization
```typescript
// Tree-shakable token imports
import { spatial } from '@unhinged/design-system/tokens/spatial';
import { semanticColors } from '@unhinged/design-system/tokens/colors';

// Instead of importing entire design system
// import { designSystem } from '@unhinged/design-system'; // ❌ Large bundle
```

### 6.2 Runtime Performance
```typescript
// CSS Custom Properties for theme switching
export const generateCSSCustomProperties = (theme: UnhingedTheme) => {
  return {
    '--color-primary': theme.colors.semantic.intent.primary,
    '--color-background': theme.colors.semantic.context.background.primary,
    '--spacing-sm': `${theme.spatial.spacing.sm}px`,
    '--spacing-md': `${theme.spatial.spacing.md}px`,
  };
};

// Usage in styled components for better performance
const OptimizedComponent = styled.div`
  background: var(--color-background);
  padding: var(--spacing-md);
  color: var(--color-primary);
`;
```

---

## 7. Documentation & Developer Experience

### 7.1 Storybook Integration
```typescript
// .storybook/preview.ts
import { ThemeProvider } from 'styled-components';
import { createTheme } from '../src/design_system';

export const decorators = [
  (Story) => {
    const theme = createTheme();
    return (
      <ThemeProvider theme={theme}>
        <Story />
      </ThemeProvider>
    );
  },
];
```

### 7.2 TypeScript IntelliSense
```typescript
// Enhanced developer experience with autocomplete
declare module 'styled-components' {
  export interface DefaultTheme extends UnhingedTheme {}
}

// Now all styled components have full TypeScript support
const TypeSafeComponent = styled.div`
  /* Full autocomplete for theme properties */
  color: ${({ theme }) => theme.colors.semantic.intent.primary};
  padding: ${({ theme }) => theme.spatial.spacing.md}px;
`;
```

---

**Implementation Status**: Ready for execution with comprehensive migration strategy and backward compatibility.
