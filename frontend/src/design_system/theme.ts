
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

import { lightTheme } from './themes/light';
import { createCompatibilityTheme } from './legacy/compatibility';

// Legacy theme types for backward compatibility
const ThemeName = {
    BASIC: 'Basic Theme' as const,
} as const;

type ThemeName = typeof ThemeName[keyof typeof ThemeName];

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
let compatibilityTheme;
try {
  compatibilityTheme = createCompatibilityTheme(lightTheme);
  console.log('✅ Compatibility theme created successfully');
} catch (error) {
  console.error('❌ Failed to create compatibility theme:', error);
  // Fallback to a minimal theme structure with all required properties
  compatibilityTheme = {
    ...lightTheme,
    legacy: {
      name: 'Basic Theme' as const,
      color: {
        palette: { white: '#ffffff' },
        background: { primary: '#ffffff', secondary: '#f8f9fa', hovered: '#e9ecef' },
        border: { primary: '#dee2e6', secondary: '#e9ecef' },
        text: { primary: '#212529', secondary: '#6c757d' }
      },
      fonts: { main: 'system-ui', heading: 'system-ui' }
    },
    color: {
      palette: { white: '#ffffff' },
      background: { primary: '#ffffff', secondary: '#f8f9fa', hovered: '#e9ecef' },
      border: { primary: '#dee2e6', secondary: '#e9ecef' },
      text: { primary: '#212529', secondary: '#6c757d' }
    },
    fonts: { main: 'system-ui', heading: 'system-ui' },
    background: '#ffffff',
    colors: {
      ...lightTheme.colors,
      surface: '#f8f9fa',
      danger: '#dc3545',
      primary: '#007bff',
      primaryDark: '#0056b3',
      text: '#212529',
      background: '#ffffff',
      border: '#dee2e6',
      muted: '#6c757d',
      hover: '#e9ecef'
    }
  };
}

// Export the compatibility theme as basicTheme for backward compatibility
export const basicTheme = compatibilityTheme;

// Also export the legacy Theme type for existing components
export type Theme = LegacyTheme;