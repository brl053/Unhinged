// ============================================================================
// Spatial Design Tokens - Decimal-Based Measurement System
// ============================================================================
//
// @file spatial.ts
// @version 2.0.0
// @author Unhinged Design System Team
// @date 2025-10-06
// @description Scientific decimal-based spatial measurement system
//
// Etymology: Latin "spatium" = space
// Methodology: Base-10 scaling following metric system principles
// ============================================================================

/**
 * Base spatial units following decimal progression
 * Foundation: 1px = fundamental measurement unit
 * Scaling: 10^n progression for systematic relationships
 */
export const spatial = {
  // Micro scale (sub-pixel precision)
  millipixel: 0.1,    // 0.1px - hairline borders, fine details
  centipixel: 0.5,    // 0.5px - sub-pixel rendering, retina displays
  
  // Base scale (fundamental units)
  pixel: 1,           // 1px - fundamental measurement unit
  decapixel: 10,      // 10px - small spacing, padding
  hectopixel: 100,    // 100px - large spacing, layout dimensions
  kilopixel: 1000,    // 1000px - container widths, major layout
  
  // Semantic spacing scale (derived from base units)
  spacing: {
    none: 0,          // 0px - no spacing
    xs: 4,            // 4px - 0.4 * decapixel - minimal spacing
    sm: 8,            // 8px - 0.8 * decapixel - small spacing
    md: 16,           // 16px - 1.6 * decapixel - medium spacing
    lg: 24,           // 24px - 2.4 * decapixel - large spacing
    xl: 32,           // 32px - 3.2 * decapixel - extra large spacing
    xxl: 48,          // 48px - 4.8 * decapixel - extra extra large spacing
    xxxl: 64,         // 64px - 6.4 * decapixel - maximum spacing
  },
  
  // Border radius scale (proportional to spacing)
  radius: {
    none: 0,          // 0px - sharp corners
    xs: 2,            // 2px - subtle rounding
    sm: 4,            // 4px - small rounding
    md: 8,            // 8px - medium rounding
    lg: 12,           // 12px - large rounding
    xl: 16,           // 16px - extra large rounding
    full: 9999,       // 9999px - fully rounded (pills, circles)
  },
  
  // Border width scale (sub-pixel to pixel precision)
  border: {
    none: 0,          // 0px - no border
    hairline: 0.5,    // 0.5px - hairline border
    thin: 1,          // 1px - standard border
    medium: 2,        // 2px - medium border
    thick: 4,         // 4px - thick border
    heavy: 8,         // 8px - heavy border
  },
} as const;

/**
 * Responsive breakpoints following mobile-first approach
 * Etymology: "break" + "point" = responsive breaking points
 */
export const breakpoints = {
  // Mobile-first progression
  mobile: 0,          // 0px - base mobile (320px+ implied)
  tablet: 768,        // 768px - tablet portrait
  desktop: 1024,      // 1024px - desktop/laptop
  widescreen: 1440,   // 1440px - large desktop
  ultrawide: 1920,    // 1920px - ultra-wide displays
  
  // OS-level scaling for desktop applications
  systemSmall: 1366,  // 1366px - small system displays
  systemLarge: 2560,  // 2560px - large system displays (4K)
} as const;

/**
 * Container max-widths for responsive design
 * Aligned with breakpoint system for consistent layouts
 */
export const containers = {
  mobile: '100%',           // Full width on mobile
  tablet: '768px',          // Match tablet breakpoint
  desktop: '1024px',        // Match desktop breakpoint
  widescreen: '1200px',     // Optimal reading width
  ultrawide: '1400px',      // Maximum content width
} as const;

/**
 * Grid system configuration
 * 12-column grid with flexible gutters
 */
export const grid = {
  columns: 12,              // Standard 12-column grid
  gutter: spatial.spacing.lg, // 24px gutter between columns
  margin: spatial.spacing.md, // 16px container margins
} as const;

/**
 * Z-index scale for layering management
 * Systematic approach to prevent z-index conflicts
 */
export const zIndex = {
  base: 0,                  // Base layer
  dropdown: 100,            // Dropdown menus
  sticky: 200,              // Sticky elements
  overlay: 300,             // Overlays, backdrops
  modal: 400,               // Modal dialogs
  popover: 500,             // Popovers, tooltips
  toast: 600,               // Toast notifications
  tooltip: 700,             // Tooltips (highest priority)
} as const;

/**
 * Type definitions for spatial tokens
 * Ensures type safety across the design system
 */
export type SpatialScale = keyof typeof spatial.spacing;
export type RadiusScale = keyof typeof spatial.radius;
export type BorderScale = keyof typeof spatial.border;
export type BreakpointScale = keyof typeof breakpoints;
export type ContainerScale = keyof typeof containers;
export type ZIndexScale = keyof typeof zIndex;

/**
 * Utility functions for spatial calculations
 */

/**
 * Convert spacing scale to pixel value
 * @param scale - Spacing scale key
 * @returns Pixel value as string
 */
export const spacing = (scale: SpatialScale): string => 
  `${spatial.spacing[scale]}px`;

/**
 * Convert radius scale to pixel value
 * @param scale - Radius scale key
 * @returns Pixel value as string
 */
export const radius = (scale: RadiusScale): string => 
  `${spatial.radius[scale]}px`;

/**
 * Convert border scale to pixel value
 * @param scale - Border scale key
 * @returns Pixel value as string
 */
export const border = (scale: BorderScale): string => 
  `${spatial.border[scale]}px`;

/**
 * Generate responsive media query
 * @param breakpoint - Breakpoint scale key
 * @returns CSS media query string
 */
export const mediaQuery = (breakpoint: BreakpointScale): string => 
  `@media (min-width: ${breakpoints[breakpoint]}px)`;

/**
 * Calculate proportional spacing
 * @param multiplier - Multiplication factor
 * @param base - Base spacing scale (default: 'md')
 * @returns Calculated pixel value as string
 */
export const proportionalSpacing = (
  multiplier: number, 
  base: SpatialScale = 'md'
): string => 
  `${spatial.spacing[base] * multiplier}px`;

/**
 * Generate CSS custom properties for spatial tokens
 * Enables runtime theme switching and CSS variable usage
 */
export const spatialCSSProperties = {
  // Spacing scale
  '--spacing-none': spacing('none'),
  '--spacing-xs': spacing('xs'),
  '--spacing-sm': spacing('sm'),
  '--spacing-md': spacing('md'),
  '--spacing-lg': spacing('lg'),
  '--spacing-xl': spacing('xl'),
  '--spacing-xxl': spacing('xxl'),
  '--spacing-xxxl': spacing('xxxl'),
  
  // Radius scale
  '--radius-none': radius('none'),
  '--radius-xs': radius('xs'),
  '--radius-sm': radius('sm'),
  '--radius-md': radius('md'),
  '--radius-lg': radius('lg'),
  '--radius-xl': radius('xl'),
  '--radius-full': radius('full'),
  
  // Border scale
  '--border-none': border('none'),
  '--border-hairline': border('hairline'),
  '--border-thin': border('thin'),
  '--border-medium': border('medium'),
  '--border-thick': border('thick'),
  '--border-heavy': border('heavy'),
} as const;
