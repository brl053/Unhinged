
// ============================================================================
// Theme Compatibility Layer
// ============================================================================
//
// This file provides backward compatibility between the old basicTheme
// and the new scientific design system. It creates a compatibility theme
// that includes both structures.
//
// MIGRATION STATUS: Compatibility layer for gradual migration
// ============================================================================

import { lightTheme, createCompatibilityTheme } from './index';

// Legacy theme types for backward compatibility
enum ThemeName {
    BASIC = 'Basic Theme',
}

type LegacyTheme = {
    name: ThemeName;
    color : {
      palette: {
        white: string;
      }
      background: {
        primary: string;
        secondary: string;
        hovered: string;
      },
      border: {
        primary: string;
        secondary: string;
      }
      text: {
        primary: string;
        secondary: string;
      }
    };
    fonts: {
      main: string;
      heading: string;
    };
}

// Create compatibility theme that includes both old and new structures
const compatibilityTheme = createCompatibilityTheme(lightTheme);

// Export the compatibility theme as basicTheme for backward compatibility
export const basicTheme = compatibilityTheme;

// Also export the legacy Theme type for existing components
export type Theme = LegacyTheme;