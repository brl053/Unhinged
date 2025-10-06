// ============================================================================
// Color Design Tokens - Scientific Color Architecture
// ============================================================================
//
// @file colors.ts
// @version 2.0.0
// @author Unhinged Design System Team
// @date 2025-10-06
// @description Scientific color system with primitive and semantic tokens
//
// Etymology: Latin "color" = appearance, hue
// Methodology: RGB color model with systematic semantic mapping
// ============================================================================

/**
 * Primitive color palette - foundational color values
 * These are the base colors from which all other colors derive
 * Organized by chromatic properties for systematic relationships
 */
export const primitiveColors = {
  /**
   * Achromatic colors (grayscale)
   * Etymology: Greek "a-" (without) + "chroma" (color)
   * Pure grayscale progression from white to black
   */
  achromatic: {
    white: '#ffffff',     // Pure white (RGB: 255,255,255)
    gray100: '#f8f9fa',   // Near white - subtle background
    gray200: '#e9ecef',   // Light gray - borders, dividers
    gray300: '#dee2e6',   // Medium-light gray - inactive states
    gray400: '#ced4da',   // Medium gray - placeholders
    gray500: '#adb5bd',   // True middle gray - secondary text
    gray600: '#6c757d',   // Medium-dark gray - body text
    gray700: '#495057',   // Dark gray - headings
    gray800: '#343a40',   // Very dark gray - emphasis
    gray900: '#212529',   // Near black - primary text
    black: '#000000',     // Pure black (RGB: 0,0,0)
  },
  
  /**
   * Chromatic colors (hues)
   * Etymology: Greek "chroma" = color
   * Primary and secondary hues based on color wheel theory
   */
  chromatic: {
    // Primary hues (RGB primaries and their complements)
    red: '#dc3545',       // 0° - Red primary, danger, error states
    orange: '#fd7e14',    // 30° - Red-orange, warning accent
    yellow: '#ffc107',    // 60° - Yellow primary, warning states
    green: '#28a745',     // 120° - Green primary, success states
    cyan: '#17a2b8',      // 180° - Cyan primary, info states
    blue: '#007bff',      // 240° - Blue primary, primary brand
    purple: '#6f42c1',    // 270° - Purple primary, secondary brand
    magenta: '#e83e8c',   // 300° - Magenta primary, accent color
  },
} as const;

/**
 * Semantic color tokens - meaning-based color assignments
 * Etymology: Greek "semantikos" = significant meaning
 * Colors assigned based on their intended use and meaning
 */
export const semanticColors = {
  /**
   * Intent colors - action and state-based meanings
   * Used for buttons, alerts, status indicators
   */
  intent: {
    primary: primitiveColors.chromatic.blue,      // Primary actions, brand
    secondary: primitiveColors.achromatic.gray600, // Secondary actions
    success: primitiveColors.chromatic.green,     // Success states, positive actions
    warning: primitiveColors.chromatic.yellow,    // Warning states, caution
    danger: primitiveColors.chromatic.red,        // Error states, destructive actions
    info: primitiveColors.chromatic.cyan,         // Informational states, neutral info
  },
  
  /**
   * Context colors - usage-based color assignments
   * Organized by UI context (background, text, borders)
   */
  context: {
    /**
     * Background colors for different surface levels
     * Follows elevation principles for depth perception
     */
    background: {
      primary: primitiveColors.achromatic.white,    // Main background, cards
      secondary: primitiveColors.achromatic.gray100, // Secondary surfaces
      tertiary: primitiveColors.achromatic.gray200,  // Tertiary surfaces, hover states
      inverse: primitiveColors.achromatic.gray900,   // Dark backgrounds, inverse themes
      overlay: 'rgba(0, 0, 0, 0.5)',               // Modal overlays, backdrops
    },
    
    /**
     * Text colors for different hierarchy levels
     * Ensures proper contrast ratios for accessibility
     */
    text: {
      primary: primitiveColors.achromatic.gray900,   // Primary text, headings
      secondary: primitiveColors.achromatic.gray700, // Secondary text, body
      tertiary: primitiveColors.achromatic.gray600,  // Tertiary text, captions
      inverse: primitiveColors.achromatic.white,     // Text on dark backgrounds
      disabled: primitiveColors.achromatic.gray400,  // Disabled text states
      placeholder: primitiveColors.achromatic.gray500, // Placeholder text
    },
    
    /**
     * Border colors for different interaction states
     * Provides visual separation and focus indication
     */
    border: {
      primary: primitiveColors.achromatic.gray300,   // Default borders
      secondary: primitiveColors.achromatic.gray200, // Subtle borders
      focus: primitiveColors.chromatic.blue,         // Focus indicators
      error: primitiveColors.chromatic.red,          // Error state borders
      success: primitiveColors.chromatic.green,      // Success state borders
      warning: primitiveColors.chromatic.yellow,     // Warning state borders
    },
  },
} as const;

/**
 * Alpha (transparency) variations for layering effects
 * Etymology: Greek "alpha" = first letter, representing opacity
 */
export const alphaColors = {
  /**
   * Generate alpha variations of semantic colors
   * Useful for hover states, overlays, and subtle backgrounds
   */
  primary: {
    alpha10: 'rgba(0, 123, 255, 0.1)',   // 10% opacity
    alpha20: 'rgba(0, 123, 255, 0.2)',   // 20% opacity
    alpha30: 'rgba(0, 123, 255, 0.3)',   // 30% opacity
    alpha50: 'rgba(0, 123, 255, 0.5)',   // 50% opacity
  },
  
  success: {
    alpha10: 'rgba(40, 167, 69, 0.1)',   // 10% opacity
    alpha20: 'rgba(40, 167, 69, 0.2)',   // 20% opacity
    alpha30: 'rgba(40, 167, 69, 0.3)',   // 30% opacity
    alpha50: 'rgba(40, 167, 69, 0.5)',   // 50% opacity
  },
  
  warning: {
    alpha10: 'rgba(255, 193, 7, 0.1)',   // 10% opacity
    alpha20: 'rgba(255, 193, 7, 0.2)',   // 20% opacity
    alpha30: 'rgba(255, 193, 7, 0.3)',   // 30% opacity
    alpha50: 'rgba(255, 193, 7, 0.5)',   // 50% opacity
  },
  
  danger: {
    alpha10: 'rgba(220, 53, 69, 0.1)',   // 10% opacity
    alpha20: 'rgba(220, 53, 69, 0.2)',   // 20% opacity
    alpha30: 'rgba(220, 53, 69, 0.3)',   // 30% opacity
    alpha50: 'rgba(220, 53, 69, 0.5)',   // 50% opacity
  },
} as const;

/**
 * Dark theme color variations
 * Inverted color relationships for dark mode support
 */
export const darkColors = {
  context: {
    background: {
      primary: primitiveColors.achromatic.gray900,   // Dark primary background
      secondary: primitiveColors.achromatic.gray800, // Dark secondary background
      tertiary: primitiveColors.achromatic.gray700,  // Dark tertiary background
      inverse: primitiveColors.achromatic.white,     // Light backgrounds in dark theme
      overlay: 'rgba(255, 255, 255, 0.1)',         // Light overlays in dark theme
    },
    
    text: {
      primary: primitiveColors.achromatic.white,     // Light text on dark
      secondary: primitiveColors.achromatic.gray300, // Secondary light text
      tertiary: primitiveColors.achromatic.gray400,  // Tertiary light text
      inverse: primitiveColors.achromatic.gray900,   // Dark text on light surfaces
      disabled: primitiveColors.achromatic.gray600,  // Disabled text in dark theme
      placeholder: primitiveColors.achromatic.gray500, // Placeholder in dark theme
    },
    
    border: {
      primary: primitiveColors.achromatic.gray600,   // Dark theme borders
      secondary: primitiveColors.achromatic.gray700, // Subtle dark borders
      focus: primitiveColors.chromatic.blue,         // Focus remains consistent
      error: primitiveColors.chromatic.red,          // Error remains consistent
      success: primitiveColors.chromatic.green,      // Success remains consistent
      warning: primitiveColors.chromatic.yellow,     // Warning remains consistent
    },
  },
} as const;

/**
 * Type definitions for color tokens
 * Ensures type safety across the design system
 */
export type PrimitiveColorScale = keyof typeof primitiveColors.achromatic | keyof typeof primitiveColors.chromatic;
export type IntentColorScale = keyof typeof semanticColors.intent;
export type ContextColorScale = keyof typeof semanticColors.context;
export type AlphaColorScale = keyof typeof alphaColors;

/**
 * Utility functions for color manipulation
 */

/**
 * Generate CSS custom properties for color tokens
 * Enables runtime theme switching and CSS variable usage
 */
export const colorCSSProperties = {
  // Primitive colors
  '--color-white': primitiveColors.achromatic.white,
  '--color-black': primitiveColors.achromatic.black,
  '--color-gray-100': primitiveColors.achromatic.gray100,
  '--color-gray-200': primitiveColors.achromatic.gray200,
  '--color-gray-300': primitiveColors.achromatic.gray300,
  '--color-gray-400': primitiveColors.achromatic.gray400,
  '--color-gray-500': primitiveColors.achromatic.gray500,
  '--color-gray-600': primitiveColors.achromatic.gray600,
  '--color-gray-700': primitiveColors.achromatic.gray700,
  '--color-gray-800': primitiveColors.achromatic.gray800,
  '--color-gray-900': primitiveColors.achromatic.gray900,
  
  // Intent colors
  '--color-primary': semanticColors.intent.primary,
  '--color-secondary': semanticColors.intent.secondary,
  '--color-success': semanticColors.intent.success,
  '--color-warning': semanticColors.intent.warning,
  '--color-danger': semanticColors.intent.danger,
  '--color-info': semanticColors.intent.info,
  
  // Context colors
  '--color-bg-primary': semanticColors.context.background.primary,
  '--color-bg-secondary': semanticColors.context.background.secondary,
  '--color-bg-tertiary': semanticColors.context.background.tertiary,
  '--color-text-primary': semanticColors.context.text.primary,
  '--color-text-secondary': semanticColors.context.text.secondary,
  '--color-text-tertiary': semanticColors.context.text.tertiary,
  '--color-border-primary': semanticColors.context.border.primary,
  '--color-border-secondary': semanticColors.context.border.secondary,
} as const;
