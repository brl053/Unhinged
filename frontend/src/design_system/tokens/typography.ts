// ============================================================================
// Typography Design Tokens - Modular Scale System
// ============================================================================
//
// @file typography.ts
// @version 2.0.0
// @author Unhinged Design System Team
// @date 2025-10-06
// @description Scientific typography system with modular scale and semantic hierarchy
//
// Etymology: Greek "typos" (impression) + "graphein" (to write)
// Methodology: Modular scale with semantic naming and responsive behavior
// ============================================================================

/**
 * Font family stacks with systematic fallbacks
 * Etymology: Latin "familia" = household, group
 * Organized by purpose and rendering characteristics
 */
export const fontFamilies = {
  /**
   * Primary font family for body text and UI
   * Optimized for readability and cross-platform consistency
   */
  primary: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", "Helvetica Neue", Arial, sans-serif',
  
  /**
   * Secondary font family for headings and emphasis
   * Provides visual hierarchy and brand personality
   */
  secondary: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", "Helvetica Neue", Arial, sans-serif',
  
  /**
   * Monospace font family for code and technical content
   * Ensures consistent character width for alignment
   */
  monospace: '"SF Mono", Monaco, "Cascadia Code", "Roboto Mono", Consolas, "Courier New", monospace',
  
  /**
   * System font family for OS-level integration
   * Uses native system fonts for optimal performance
   */
  system: 'system-ui, -apple-system, BlinkMacSystemFont, sans-serif',
} as const;

/**
 * Font weight scale following OpenType standard
 * Etymology: "weight" = visual heaviness of letterforms
 * Numeric values align with CSS font-weight property
 */
export const fontWeights = {
  thin: 100,        // Thin weight - decorative use only
  extralight: 200,  // Extra light - large display text
  light: 300,       // Light - subtle emphasis
  regular: 400,     // Regular - body text default
  medium: 500,      // Medium - UI elements, buttons
  semibold: 600,    // Semibold - subheadings, emphasis
  bold: 700,        // Bold - headings, strong emphasis
  extrabold: 800,   // Extra bold - display headings
  black: 900,       // Black - maximum emphasis
} as const;

/**
 * Modular scale for font sizes
 * Etymology: Latin "modulus" = small measure
 * Based on Major Third ratio (1.250) for harmonious proportions
 */
export const fontScale = {
  // Base scale using Major Third ratio (1.250)
  micro: 0.64,      // 10.24px at 16px base - fine print, captions
  small: 0.8,       // 12.8px at 16px base - small text, labels
  base: 1,          // 16px base - body text default
  medium: 1.25,     // 20px at 16px base - large body text
  large: 1.563,     // 25px at 16px base - subheadings
  xlarge: 1.953,    // 31.25px at 16px base - headings
  xxlarge: 2.441,   // 39.06px at 16px base - large headings
  xxxlarge: 3.052,  // 48.83px at 16px base - display headings
  
  // Responsive scaling factors
  mobileScale: 0.875,  // 87.5% of base scale on mobile
  desktopScale: 1,     // 100% of base scale on desktop
  largeScale: 1.125,   // 112.5% of base scale on large screens
} as const;

/**
 * Line height scale for optimal readability
 * Etymology: "line" + "height" = vertical spacing between lines
 * Values optimized for different text purposes
 */
export const lineHeights = {
  none: 1,          // 1.0 - no additional line spacing
  tight: 1.2,       // 1.2 - headings, compact text
  snug: 1.375,      // 1.375 - UI text, buttons
  base: 1.5,        // 1.5 - body text, optimal readability
  relaxed: 1.625,   // 1.625 - long-form reading
  loose: 2,         // 2.0 - maximum spacing, accessibility
} as const;

/**
 * Letter spacing scale for fine typography control
 * Etymology: "letter" + "spacing" = horizontal space between characters
 * Values in em units for proportional scaling
 */
export const letterSpacing = {
  tighter: '-0.05em',  // -0.05em - tight spacing for large text
  tight: '-0.025em',   // -0.025em - slightly tight spacing
  normal: '0',         // 0 - default spacing
  wide: '0.025em',     // 0.025em - slightly wide spacing
  wider: '0.05em',     // 0.05em - wide spacing for small text
  widest: '0.1em',     // 0.1em - maximum spacing for emphasis
} as const;

/**
 * Semantic typography tokens
 * Etymology: Greek "semantikos" = significant meaning
 * Typography styles organized by content hierarchy and purpose
 */
export const semanticTypography = {
  /**
   * Display typography for hero sections and major headings
   * Large, impactful text for maximum visual hierarchy
   */
  display: {
    hero: {
      fontSize: fontScale.xxxlarge,
      fontWeight: fontWeights.bold,
      lineHeight: lineHeights.tight,
      letterSpacing: letterSpacing.tighter,
      fontFamily: fontFamilies.primary,
    },
    large: {
      fontSize: fontScale.xxlarge,
      fontWeight: fontWeights.bold,
      lineHeight: lineHeights.tight,
      letterSpacing: letterSpacing.tight,
      fontFamily: fontFamilies.primary,
    },
    medium: {
      fontSize: fontScale.xlarge,
      fontWeight: fontWeights.semibold,
      lineHeight: lineHeights.snug,
      letterSpacing: letterSpacing.normal,
      fontFamily: fontFamilies.primary,
    },
  },
  
  /**
   * Heading typography for content hierarchy
   * Structured heading levels following HTML semantics
   */
  heading: {
    h1: {
      fontSize: fontScale.xlarge,
      fontWeight: fontWeights.bold,
      lineHeight: lineHeights.tight,
      letterSpacing: letterSpacing.normal,
      fontFamily: fontFamilies.primary,
    },
    h2: {
      fontSize: fontScale.large,
      fontWeight: fontWeights.semibold,
      lineHeight: lineHeights.snug,
      letterSpacing: letterSpacing.normal,
      fontFamily: fontFamilies.primary,
    },
    h3: {
      fontSize: fontScale.medium,
      fontWeight: fontWeights.semibold,
      lineHeight: lineHeights.snug,
      letterSpacing: letterSpacing.normal,
      fontFamily: fontFamilies.primary,
    },
    h4: {
      fontSize: fontScale.base,
      fontWeight: fontWeights.semibold,
      lineHeight: lineHeights.base,
      letterSpacing: letterSpacing.normal,
      fontFamily: fontFamilies.primary,
    },
    h5: {
      fontSize: fontScale.small,
      fontWeight: fontWeights.semibold,
      lineHeight: lineHeights.base,
      letterSpacing: letterSpacing.wide,
      fontFamily: fontFamilies.primary,
    },
    h6: {
      fontSize: fontScale.micro,
      fontWeight: fontWeights.bold,
      lineHeight: lineHeights.base,
      letterSpacing: letterSpacing.wider,
      fontFamily: fontFamilies.primary,
    },
  },
  
  /**
   * Body typography for content and UI text
   * Optimized for readability and user interface elements
   */
  body: {
    large: {
      fontSize: fontScale.medium,
      fontWeight: fontWeights.regular,
      lineHeight: lineHeights.relaxed,
      letterSpacing: letterSpacing.normal,
      fontFamily: fontFamilies.primary,
    },
    base: {
      fontSize: fontScale.base,
      fontWeight: fontWeights.regular,
      lineHeight: lineHeights.base,
      letterSpacing: letterSpacing.normal,
      fontFamily: fontFamilies.primary,
    },
    small: {
      fontSize: fontScale.small,
      fontWeight: fontWeights.regular,
      lineHeight: lineHeights.base,
      letterSpacing: letterSpacing.normal,
      fontFamily: fontFamilies.primary,
    },
  },
  
  /**
   * UI typography for interface elements
   * Compact, functional text for buttons, labels, and controls
   */
  ui: {
    button: {
      fontSize: fontScale.base,
      fontWeight: fontWeights.medium,
      lineHeight: lineHeights.none,
      letterSpacing: letterSpacing.normal,
      fontFamily: fontFamilies.primary,
    },
    label: {
      fontSize: fontScale.small,
      fontWeight: fontWeights.medium,
      lineHeight: lineHeights.snug,
      letterSpacing: letterSpacing.wide,
      fontFamily: fontFamilies.primary,
    },
    caption: {
      fontSize: fontScale.micro,
      fontWeight: fontWeights.regular,
      lineHeight: lineHeights.base,
      letterSpacing: letterSpacing.normal,
      fontFamily: fontFamilies.primary,
    },
  },
  
  /**
   * Code typography for technical content
   * Monospace fonts with optimized spacing for code readability
   */
  code: {
    inline: {
      fontSize: fontScale.small,
      fontWeight: fontWeights.regular,
      lineHeight: lineHeights.base,
      letterSpacing: letterSpacing.normal,
      fontFamily: fontFamilies.monospace,
    },
    block: {
      fontSize: fontScale.small,
      fontWeight: fontWeights.regular,
      lineHeight: lineHeights.relaxed,
      letterSpacing: letterSpacing.normal,
      fontFamily: fontFamilies.monospace,
    },
  },
} as const;

/**
 * Type definitions for typography tokens
 * Ensures type safety across the design system
 */
export type FontFamilyScale = keyof typeof fontFamilies;
export type FontWeightScale = keyof typeof fontWeights;
export type FontSizeScale = keyof typeof fontScale;
export type LineHeightScale = keyof typeof lineHeights;
export type LetterSpacingScale = keyof typeof letterSpacing;
export type SemanticTypographyScale = keyof typeof semanticTypography;

/**
 * Utility functions for typography calculations
 */

/**
 * Convert font scale to rem value
 * @param scale - Font scale key
 * @returns Font size in rem units
 */
export const fontSize = (scale: FontSizeScale): string => 
  `${fontScale[scale]}rem`;

/**
 * Generate responsive font size with clamp()
 * @param minScale - Minimum font scale
 * @param maxScale - Maximum font scale
 * @param preferredScale - Preferred font scale
 * @returns CSS clamp() function
 */
export const responsiveFontSize = (
  minScale: FontSizeScale,
  maxScale: FontSizeScale,
  preferredScale: FontSizeScale = 'base'
): string => 
  `clamp(${fontSize(minScale)}, ${fontSize(preferredScale)}, ${fontSize(maxScale)})`;

/**
 * Generate CSS custom properties for typography tokens
 * Enables runtime theme switching and CSS variable usage
 */
export const typographyCSSProperties = {
  // Font families
  '--font-primary': fontFamilies.primary,
  '--font-secondary': fontFamilies.secondary,
  '--font-monospace': fontFamilies.monospace,
  '--font-system': fontFamilies.system,
  
  // Font weights
  '--font-weight-regular': fontWeights.regular.toString(),
  '--font-weight-medium': fontWeights.medium.toString(),
  '--font-weight-semibold': fontWeights.semibold.toString(),
  '--font-weight-bold': fontWeights.bold.toString(),
  
  // Font sizes
  '--font-size-micro': fontSize('micro'),
  '--font-size-small': fontSize('small'),
  '--font-size-base': fontSize('base'),
  '--font-size-medium': fontSize('medium'),
  '--font-size-large': fontSize('large'),
  '--font-size-xlarge': fontSize('xlarge'),
  '--font-size-xxlarge': fontSize('xxlarge'),
  '--font-size-xxxlarge': fontSize('xxxlarge'),
  
  // Line heights
  '--line-height-tight': lineHeights.tight.toString(),
  '--line-height-snug': lineHeights.snug.toString(),
  '--line-height-base': lineHeights.base.toString(),
  '--line-height-relaxed': lineHeights.relaxed.toString(),
} as const;
