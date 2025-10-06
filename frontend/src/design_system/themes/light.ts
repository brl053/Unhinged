// ============================================================================
// Light Theme - Default Theme Configuration
// ============================================================================
//
// @file light.ts
// @version 2.0.0
// @author Unhinged Design System Team
// @date 2025-10-06
// @description Light theme composition using scientific design tokens
//
// This theme serves as the default light mode configuration for the Unhinged
// design system, combining all token categories into a cohesive theme object.
// ============================================================================

import { spatial, breakpoints, containers, grid, zIndex } from '../tokens/spatial';
import { primitiveColors, semanticColors, alphaColors } from '../tokens/colors';
import { fontFamilies, fontWeights, fontScale, lineHeights, letterSpacing, semanticTypography } from '../tokens/typography';
import { duration, easing, animationPresets } from '../tokens/motion';

/**
 * Complete theme interface definition
 * Provides type safety and structure for all theme properties
 */
export interface UnhingedTheme {
  // Theme metadata
  meta: {
    name: string;
    version: string;
    mode: 'light' | 'dark' | 'auto';
    description: string;
  };
  
  // Spatial system
  spatial: {
    base: typeof spatial;
    breakpoints: typeof breakpoints;
    containers: typeof containers;
    grid: typeof grid;
    zIndex: typeof zIndex;
  };
  
  // Color system
  colors: {
    primitive: typeof primitiveColors;
    semantic: typeof semanticColors;
    alpha: typeof alphaColors;
  };
  
  // Typography system
  typography: {
    families: typeof fontFamilies;
    weights: typeof fontWeights;
    scale: typeof fontScale;
    lineHeights: typeof lineHeights;
    letterSpacing: typeof letterSpacing;
    semantic: typeof semanticTypography;
  };
  
  // Motion system
  motion: {
    duration: typeof duration;
    easing: typeof easing;
    presets: typeof animationPresets;
  };
  
  // Component-specific tokens (to be extended)
  components: {
    // Component tokens will be added here
    [key: string]: any;
  };
  
  // Platform-specific adaptations
  platform: {
    web: {
      boxShadow: {
        small: string;
        medium: string;
        large: string;
        xlarge: string;
      };
      borderRadius: {
        small: number;
        medium: number;
        large: number;
      };
    };
    mobile: {
      minTouchTarget: number;
      touchPadding: number;
    };
    desktop: {
      windowChrome: number;
      menuHeight: number;
    };
  };
}

/**
 * Light theme configuration
 * Default theme using light color scheme and standard proportions
 */
export const lightTheme: UnhingedTheme = {
  // Theme metadata
  meta: {
    name: 'Unhinged Light Theme',
    version: '2.0.0',
    mode: 'light',
    description: 'Default light theme with scientific design token architecture',
  },
  
  // Spatial system - decimal-based measurements
  spatial: {
    base: spatial,
    breakpoints,
    containers,
    grid,
    zIndex,
  },
  
  // Color system - light mode colors
  colors: {
    primitive: primitiveColors,
    semantic: semanticColors,
    alpha: alphaColors,
  },
  
  // Typography system - modular scale
  typography: {
    families: fontFamilies,
    weights: fontWeights,
    scale: fontScale,
    lineHeights,
    letterSpacing,
    semantic: semanticTypography,
  },
  
  // Motion system - animation and transitions
  motion: {
    duration,
    easing,
    presets: animationPresets,
  },
  
  // Component tokens (extensible)
  components: {
    // Button component tokens
    button: {
      size: {
        small: {
          padding: `${spatial.spacing.xs}px ${spatial.spacing.sm}px`,
          fontSize: fontScale.small,
          minHeight: spatial.decapixel * 3.2, // 32px
          borderRadius: spatial.radius.sm,
        },
        medium: {
          padding: `${spatial.spacing.sm}px ${spatial.spacing.md}px`,
          fontSize: fontScale.base,
          minHeight: spatial.decapixel * 4.0, // 40px
          borderRadius: spatial.radius.md,
        },
        large: {
          padding: `${spatial.spacing.md}px ${spatial.spacing.lg}px`,
          fontSize: fontScale.medium,
          minHeight: spatial.decapixel * 4.8, // 48px
          borderRadius: spatial.radius.lg,
        },
      },
      intent: {
        primary: {
          background: semanticColors.intent.primary,
          color: semanticColors.context.text.inverse,
          border: semanticColors.intent.primary,
          hover: {
            background: primitiveColors.chromatic.blue, // Darker blue
            border: primitiveColors.chromatic.blue,
          },
        },
        secondary: {
          background: 'transparent',
          color: semanticColors.intent.primary,
          border: semanticColors.intent.primary,
          hover: {
            background: alphaColors.primary.alpha10,
            border: semanticColors.intent.primary,
          },
        },
        success: {
          background: semanticColors.intent.success,
          color: semanticColors.context.text.inverse,
          border: semanticColors.intent.success,
          hover: {
            background: primitiveColors.chromatic.green,
            border: primitiveColors.chromatic.green,
          },
        },
        warning: {
          background: semanticColors.intent.warning,
          color: semanticColors.context.text.primary,
          border: semanticColors.intent.warning,
          hover: {
            background: primitiveColors.chromatic.yellow,
            border: primitiveColors.chromatic.yellow,
          },
        },
        danger: {
          background: semanticColors.intent.danger,
          color: semanticColors.context.text.inverse,
          border: semanticColors.intent.danger,
          hover: {
            background: primitiveColors.chromatic.red,
            border: primitiveColors.chromatic.red,
          },
        },
      },
    },
    
    // Input component tokens
    input: {
      size: {
        small: {
          padding: `${spatial.spacing.xs}px ${spatial.spacing.sm}px`,
          fontSize: fontScale.small,
          minHeight: spatial.decapixel * 3.2, // 32px
          borderRadius: spatial.radius.sm,
        },
        medium: {
          padding: `${spatial.spacing.sm}px ${spatial.spacing.md}px`,
          fontSize: fontScale.base,
          minHeight: spatial.decapixel * 4.0, // 40px
          borderRadius: spatial.radius.md,
        },
        large: {
          padding: `${spatial.spacing.md}px ${spatial.spacing.lg}px`,
          fontSize: fontScale.medium,
          minHeight: spatial.decapixel * 4.8, // 48px
          borderRadius: spatial.radius.lg,
        },
      },
      state: {
        default: {
          background: semanticColors.context.background.primary,
          color: semanticColors.context.text.primary,
          border: semanticColors.context.border.primary,
          placeholder: semanticColors.context.text.placeholder,
        },
        focus: {
          background: semanticColors.context.background.primary,
          color: semanticColors.context.text.primary,
          border: semanticColors.context.border.focus,
          boxShadow: `0 0 0 3px ${alphaColors.primary.alpha20}`,
        },
        error: {
          background: semanticColors.context.background.primary,
          color: semanticColors.context.text.primary,
          border: semanticColors.context.border.error,
          boxShadow: `0 0 0 3px ${alphaColors.danger.alpha20}`,
        },
        disabled: {
          background: semanticColors.context.background.tertiary,
          color: semanticColors.context.text.disabled,
          border: semanticColors.context.border.secondary,
        },
      },
    },
    
    // Card component tokens
    card: {
      elevation: {
        flat: {
          background: semanticColors.context.background.primary,
          border: semanticColors.context.border.primary,
          boxShadow: 'none',
        },
        raised: {
          background: semanticColors.context.background.primary,
          border: semanticColors.context.border.secondary,
          boxShadow: `0 ${spatial.pixel}px ${spatial.decapixel * 0.3}px rgba(0,0,0,0.1)`,
        },
        floating: {
          background: semanticColors.context.background.primary,
          border: 'none',
          boxShadow: `0 ${spatial.decapixel * 0.4}px ${spatial.decapixel * 0.8}px rgba(0,0,0,0.15)`,
        },
      },
      padding: {
        small: spatial.spacing.md,
        medium: spatial.spacing.lg,
        large: spatial.spacing.xl,
      },
      borderRadius: {
        small: spatial.radius.sm,
        medium: spatial.radius.md,
        large: spatial.radius.lg,
      },
    },
  },
  
  // Platform-specific adaptations
  platform: {
    web: {
      boxShadow: {
        small: `0 ${spatial.pixel}px ${spatial.decapixel * 0.3}px rgba(0,0,0,0.1)`,
        medium: `0 ${spatial.decapixel * 0.4}px ${spatial.decapixel * 0.8}px rgba(0,0,0,0.15)`,
        large: `0 ${spatial.decapixel * 0.8}px ${spatial.decapixel * 2.5}px rgba(0,0,0,0.2)`,
        xlarge: `0 ${spatial.decapixel * 1.6}px ${spatial.decapixel * 6.4}px rgba(0,0,0,0.25)`,
      },
      borderRadius: {
        small: spatial.radius.sm,
        medium: spatial.radius.md,
        large: spatial.radius.lg,
      },
    },
    mobile: {
      minTouchTarget: spatial.decapixel * 4.4, // 44px minimum touch target
      touchPadding: spatial.decapixel * 1.6,   // 16px touch padding
    },
    desktop: {
      windowChrome: spatial.decapixel * 3.2,   // 32px title bar height
      menuHeight: spatial.decapixel * 2.8,     // 28px menu item height
    },
  },
};

/**
 * Default export for easy importing
 */
export default lightTheme;
