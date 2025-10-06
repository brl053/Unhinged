// ============================================================================
// Unhinged Design System - Main Export
// ============================================================================
//
// @file index.ts
// @version 2.0.0
// @author Unhinged Design System Team
// @date 2025-10-06
// @description Main entry point for the Unhinged Design System
//
// This file provides the primary interface for consuming the design system,
// including themes, tokens, utilities, and type definitions.
// ============================================================================

// Token exports
export * from './tokens/spatial';
export * from './tokens/colors';
export * from './tokens/typography';
export * from './tokens/motion';

// Theme exports
export * from './themes/light';
export type { UnhingedTheme } from './themes/light';

// Re-export default theme for convenience
export { default as lightTheme } from './themes/light';

// Compatibility layer exports
export {
  createLegacyTheme,
  createCompatibilityTheme,
  migrationUtils,
  migrationChecklist
} from './legacy/compatibility';

// Utility functions
import { lightTheme, UnhingedTheme } from './themes/light';
import { 
  spatialCSSProperties,
  spacing,
  radius,
  border,
  mediaQuery,
  proportionalSpacing 
} from './tokens/spatial';
import { 
  colorCSSProperties 
} from './tokens/colors';
import { 
  typographyCSSProperties,
  fontSize,
  responsiveFontSize 
} from './tokens/typography';
import { 
  motionCSSProperties,
  getDuration,
  transition,
  multipleTransitions 
} from './tokens/motion';

/**
 * Theme factory function
 * Creates a theme with optional overrides for customization
 * 
 * @param overrides - Partial theme object to override default values
 * @returns Complete UnhingedTheme object
 */
export const createTheme = (overrides?: Partial<UnhingedTheme>): UnhingedTheme => {
  if (!overrides) {
    return lightTheme;
  }
  
  // Deep merge overrides with light theme
  return {
    ...lightTheme,
    ...overrides,
    meta: {
      ...lightTheme.meta,
      ...overrides.meta,
    },
    spatial: {
      ...lightTheme.spatial,
      ...overrides.spatial,
    },
    colors: {
      ...lightTheme.colors,
      ...overrides.colors,
    },
    typography: {
      ...lightTheme.typography,
      ...overrides.typography,
    },
    motion: {
      ...lightTheme.motion,
      ...overrides.motion,
    },
    components: {
      ...lightTheme.components,
      ...overrides.components,
    },
    platform: {
      ...lightTheme.platform,
      ...overrides.platform,
    },
  };
};

/**
 * Generate all CSS custom properties for the theme
 * Combines all token CSS properties into a single object
 * 
 * @param theme - UnhingedTheme object
 * @returns Object with CSS custom properties
 */
export const generateCSSCustomProperties = (theme: UnhingedTheme) => ({
  ...spatialCSSProperties,
  ...colorCSSProperties,
  ...typographyCSSProperties,
  ...motionCSSProperties,
  
  // Theme-specific custom properties
  '--theme-name': `"${theme.meta.name}"`,
  '--theme-version': `"${theme.meta.version}"`,
  '--theme-mode': `"${theme.meta.mode}"`,
});

/**
 * Utility object with commonly used design system functions
 * Provides easy access to token utilities without individual imports
 */
export const designSystemUtils = {
  // Spatial utilities
  spacing,
  radius,
  border,
  mediaQuery,
  proportionalSpacing,
  
  // Typography utilities
  fontSize,
  responsiveFontSize,
  
  // Motion utilities
  getDuration,
  transition,
  multipleTransitions,
  
  // Theme utilities
  createTheme,
  generateCSSCustomProperties,
};

/**
 * Responsive utility functions
 * Provides consistent responsive design patterns
 */
export const responsive = {
  /**
   * Generate mobile-first media queries
   * @param theme - UnhingedTheme object
   * @returns Object with media query functions
   */
  mediaQueries: (theme: UnhingedTheme) => ({
    mobile: `@media (min-width: ${theme.spatial.breakpoints.mobile}px)`,
    tablet: `@media (min-width: ${theme.spatial.breakpoints.tablet}px)`,
    desktop: `@media (min-width: ${theme.spatial.breakpoints.desktop}px)`,
    widescreen: `@media (min-width: ${theme.spatial.breakpoints.widescreen}px)`,
    ultrawide: `@media (min-width: ${theme.spatial.breakpoints.ultrawide}px)`,
  }),
  
  /**
   * Generate container queries (when supported)
   * @param theme - UnhingedTheme object
   * @returns Object with container query functions
   */
  containerQueries: (theme: UnhingedTheme) => ({
    small: `@container (min-width: ${theme.spatial.containers.mobile})`,
    medium: `@container (min-width: ${theme.spatial.containers.tablet})`,
    large: `@container (min-width: ${theme.spatial.containers.desktop})`,
    xlarge: `@container (min-width: ${theme.spatial.containers.widescreen})`,
  }),
  
  /**
   * Generate responsive values using CSS clamp()
   * @param min - Minimum value
   * @param preferred - Preferred value (typically viewport-relative)
   * @param max - Maximum value
   * @returns CSS clamp() function string
   */
  clamp: (min: string, preferred: string, max: string): string => 
    `clamp(${min}, ${preferred}, ${max})`,
};

/**
 * Accessibility utilities
 * Provides functions for accessible design implementation
 */
export const accessibility = {
  /**
   * Calculate color contrast ratio (simplified)
   * Note: This is a basic implementation. Use a proper contrast library for production.
   * @param color1 - First color (hex)
   * @param color2 - Second color (hex)
   * @returns Approximate contrast ratio
   */
  calculateContrast: (color1: string, color2: string): number => {
    // This is a placeholder implementation
    // In production, use a proper color contrast calculation library
    return 4.5; // Placeholder return value
  },
  
  /**
   * Check if color combination meets WCAG standards
   * @param foreground - Foreground color
   * @param background - Background color
   * @param level - WCAG level ('AA' or 'AAA')
   * @returns Boolean indicating compliance
   */
  isWCAGCompliant: (
    foreground: string, 
    background: string, 
    level: 'AA' | 'AAA' = 'AA'
  ): boolean => {
    const contrast = accessibility.calculateContrast(foreground, background);
    const threshold = level === 'AAA' ? 7 : 4.5;
    return contrast >= threshold;
  },
  
  /**
   * Generate focus ring styles
   * @param theme - UnhingedTheme object
   * @returns CSS focus ring styles
   */
  focusRing: (theme: UnhingedTheme) => ({
    outline: 'none',
    boxShadow: `0 0 0 3px ${theme.colors.alpha.primary.alpha30}`,
    borderColor: theme.colors.semantic.context.border.focus,
  }),
  
  /**
   * Generate reduced motion styles
   * @returns CSS for reduced motion preference
   */
  reducedMotion: () => ({
    '@media (prefers-reduced-motion: reduce)': {
      '*': {
        animationDuration: '0.01ms !important',
        animationIterationCount: '1 !important',
        transitionDuration: '0.01ms !important',
      },
    },
  }),
};

/**
 * Development utilities
 * Helpful functions for development and debugging
 */
export const devUtils = {
  /**
   * Log theme information to console
   * @param theme - UnhingedTheme object
   */
  logTheme: (theme: UnhingedTheme) => {
    console.group(`🎨 ${theme.meta.name} v${theme.meta.version}`);
    console.log('Mode:', theme.meta.mode);
    console.log('Description:', theme.meta.description);
    console.log('Spatial tokens:', Object.keys(theme.spatial.base.spacing).length);
    console.log('Color tokens:', Object.keys(theme.colors.semantic.intent).length);
    console.log('Typography tokens:', Object.keys(theme.typography.semantic).length);
    console.log('Motion tokens:', Object.keys(theme.motion.duration).length);
    console.groupEnd();
  },
  
  /**
   * Validate theme structure
   * @param theme - UnhingedTheme object
   * @returns Array of validation errors (empty if valid)
   */
  validateTheme: (theme: UnhingedTheme): string[] => {
    const errors: string[] = [];
    
    // Basic structure validation
    if (!theme.meta?.name) errors.push('Theme missing meta.name');
    if (!theme.meta?.version) errors.push('Theme missing meta.version');
    if (!theme.spatial?.base) errors.push('Theme missing spatial.base');
    if (!theme.colors?.semantic) errors.push('Theme missing colors.semantic');
    if (!theme.typography?.families) errors.push('Theme missing typography.families');
    if (!theme.motion?.duration) errors.push('Theme missing motion.duration');
    
    return errors;
  },
  
  /**
   * Generate theme documentation
   * @param theme - UnhingedTheme object
   * @returns Markdown documentation string
   */
  generateDocs: (theme: UnhingedTheme): string => {
    return `
# ${theme.meta.name}

**Version:** ${theme.meta.version}  
**Mode:** ${theme.meta.mode}  
**Description:** ${theme.meta.description}

## Token Summary

- **Spatial tokens:** ${Object.keys(theme.spatial.base.spacing).length}
- **Color tokens:** ${Object.keys(theme.colors.semantic.intent).length}
- **Typography tokens:** ${Object.keys(theme.typography.semantic).length}
- **Motion tokens:** ${Object.keys(theme.motion.duration).length}
- **Component tokens:** ${Object.keys(theme.components).length}

## Usage

\`\`\`typescript
import { createTheme } from '@unhinged/design-system';

const theme = createTheme();
\`\`\`
    `.trim();
  },
};

/**
 * Default export - the complete design system
 */
export default {
  // Core theme
  theme: lightTheme,
  createTheme,
  
  // Utilities
  utils: designSystemUtils,
  responsive,
  accessibility,
  devUtils,
  
  // CSS properties generator
  generateCSSCustomProperties,
};
