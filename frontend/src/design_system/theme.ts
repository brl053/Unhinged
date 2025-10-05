
/**
 * @fileoverview Unhinged Platform Theme System
 * @purpose Centralized theme configuration for consistent styling across the platform
 * @editable true - LLM should update this file when adding new theme properties or colors
 * @deprecated false
 *
 * @remarks
 * This file defines the complete theme system for the Unhinged Platform.
 * When adding new components, ensure all color/spacing/typography references
 * use these theme properties instead of hardcoded values.
 *
 * @example
 * ```typescript
 * // Good - uses theme
 * color: ${({ theme }) => theme.color.primary.main};
 *
 * // Bad - hardcoded
 * color: '#58a6ff';
 * ```
 */

/**
 * Available theme names for the platform
 * @public
 */
enum ThemeName {
    /** Default dark theme for the Unhinged Platform */
    UNHINGED_DARK = 'Unhinged Dark',
    /** Light theme variant */
    UNHINGED_LIGHT = 'Unhinged Light',
    /** Legacy basic theme - deprecated */
    BASIC = 'Basic Theme',
}

/**
 * Font size scale following 8px grid system
 * @public
 */
export const FontSizes = {
    /** 12px - Small text, captions */
    xs: '0.75rem',
    /** 14px - Body text, labels */
    sm: '0.875rem',
    /** 16px - Default body text */
    md: '1rem',
    /** 18px - Large body text */
    lg: '1.125rem',
    /** 24px - Headings */
    xl: '1.5rem',
    /** 32px - Large headings */
    '2xl': '2rem',
    /** 40px - Display headings */
    '3xl': '2.5rem',
} as const;

/**
 * Border radius scale for consistent rounded corners
 * @public
 */
export const BorderRadius = {
    /** 2px - Minimal rounding */
    xs: '2px',
    /** 4px - Small elements */
    sm: '4px',
    /** 8px - Standard elements */
    md: '8px',
    /** 12px - Cards, containers */
    lg: '12px',
    /** 16px - Large containers */
    xl: '16px',
    /** 50% - Circular elements */
    full: '50%',
} as const;

/**
 * Spacing scale following 8px grid system
 * @public
 */
export const Spacing = {
    /** 4px */
    xs: '0.25rem',
    /** 8px */
    sm: '0.5rem',
    /** 16px */
    md: '1rem',
    /** 24px */
    lg: '1.5rem',
    /** 32px */
    xl: '2rem',
    /** 48px */
    '2xl': '3rem',
    /** 64px */
    '3xl': '4rem',
} as const;

/**
 * Complete theme configuration interface
 * @public
 */
export interface Theme {
    /** Theme identifier */
    name: ThemeName;

    /** Color system */
    color: {
        /** Primary brand colors */
        primary: {
            /** Main brand color - use for primary actions */
            main: string;
            /** Darker variant for hover states */
            dark: string;
            /** Lighter variant for backgrounds */
            light: string;
            /** Text color on primary backgrounds */
            contrastText: string;
        };

        /** Secondary accent colors */
        secondary: {
            main: string;
            dark: string;
            light: string;
            contrastText: string;
        };

        /** Error/danger colors */
        error: {
            main: string;
            dark: string;
            light: string;
            contrastText: string;
        };

        /** Warning colors */
        warning: {
            main: string;
            dark: string;
            light: string;
            contrastText: string;
        };

        /** Success colors */
        success: {
            main: string;
            dark: string;
            light: string;
            contrastText: string;
        };

        /** Text colors */
        text: {
            /** Primary text color */
            primary: string;
            /** Secondary text color */
            secondary: string;
            /** Tertiary text color */
            tertiary: string;
            /** Disabled text color */
            disabled: string;
        };

        /** Background colors */
        background: {
            /** Main background */
            primary: string;
            /** Secondary background (cards, panels) */
            secondary: string;
            /** Tertiary background (hover states) */
            tertiary: string;
            /** Hovered state background */
            hovered: string;
        };

        /** Border colors */
        border: {
            /** Primary border color */
            primary: string;
            /** Secondary border color */
            secondary: string;
            /** Focus border color */
            focus: string;
        };

        /** Common palette colors */
        palette: {
            white: string;
            black: string;
            transparent: string;
        };
    };

    /** Typography system */
    typography: {
        /** Font families */
        fontFamily: {
            /** Main UI font */
            main: string;
            /** Heading font */
            heading: string;
            /** Monospace font for code */
            mono: string;
        };

        /** Font sizes */
        fontSize: typeof FontSizes;

        /** Font weights */
        fontWeight: {
            light: number;
            normal: number;
            medium: number;
            semibold: number;
            bold: number;
        };

        /** Line heights */
        lineHeight: {
            tight: number;
            normal: number;
            relaxed: number;
        };
    };

    /** Spacing system */
    spacing: typeof Spacing;

    /** Border radius system */
    borderRadius: typeof BorderRadius;

    /** Shadow system */
    shadows: {
        sm: string;
        md: string;
        lg: string;
        xl: string;
    };

    /** Z-index scale */
    zIndex: {
        dropdown: number;
        modal: number;
        tooltip: number;
        overlay: number;
    };
}

/**
 * Unhinged Dark Theme - Primary theme for the platform
 * @public
 */
export const unhingedDarkTheme: Theme = {
    name: ThemeName.UNHINGED_DARK,

    color: {
        primary: {
            main: '#58a6ff',
            dark: '#4493e6',
            light: '#79b8ff',
            contrastText: '#ffffff',
        },

        secondary: {
            main: '#b392f0',
            dark: '#9a7dd8',
            light: '#c8a7f5',
            contrastText: '#ffffff',
        },

        error: {
            main: '#f85149',
            dark: '#da3633',
            light: '#ff6b6b',
            contrastText: '#ffffff',
        },

        warning: {
            main: '#d29922',
            dark: '#b8860b',
            light: '#f0c040',
            contrastText: '#000000',
        },

        success: {
            main: '#3fb950',
            dark: '#2ea043',
            light: '#56d364',
            contrastText: '#ffffff',
        },

        text: {
            primary: '#e1e4e8',
            secondary: '#8b949e',
            tertiary: '#6a737d',
            disabled: '#484f58',
        },

        background: {
            primary: '#0d1117',
            secondary: '#161b22',
            tertiary: '#21262d',
            hovered: '#30363d',
        },

        border: {
            primary: '#30363d',
            secondary: '#21262d',
            focus: '#58a6ff',
        },

        palette: {
            white: '#ffffff',
            black: '#000000',
            transparent: 'transparent',
        },
    },

    typography: {
        fontFamily: {
            main: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
            heading: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
            mono: '"JetBrains Mono", "Fira Code", Consolas, monospace',
        },

        fontSize: FontSizes,

        fontWeight: {
            light: 300,
            normal: 400,
            medium: 500,
            semibold: 600,
            bold: 700,
        },

        lineHeight: {
            tight: 1.2,
            normal: 1.5,
            relaxed: 1.8,
        },
    },

    spacing: Spacing,
    borderRadius: BorderRadius,

    shadows: {
        sm: '0 1px 3px rgba(0, 0, 0, 0.12)',
        md: '0 4px 12px rgba(0, 0, 0, 0.15)',
        lg: '0 8px 24px rgba(0, 0, 0, 0.18)',
        xl: '0 16px 48px rgba(0, 0, 0, 0.24)',
    },

    zIndex: {
        dropdown: 1000,
        modal: 1050,
        tooltip: 1100,
        overlay: 1200,
    },
};

/**
 * Unhinged Light Theme - Light variant for accessibility
 * @public
 */
export const unhingedLightTheme: Theme = {
    name: ThemeName.UNHINGED_LIGHT,

    color: {
        primary: {
            main: '#0969da',
            dark: '#0550ae',
            light: '#218bff',
            contrastText: '#ffffff',
        },

        secondary: {
            main: '#8250df',
            dark: '#6f42c1',
            light: '#a475f9',
            contrastText: '#ffffff',
        },

        error: {
            main: '#d1242f',
            dark: '#a40e26',
            light: '#ff6b6b',
            contrastText: '#ffffff',
        },

        warning: {
            main: '#bf8700',
            dark: '#9a6700',
            light: '#d4a72c',
            contrastText: '#000000',
        },

        success: {
            main: '#1a7f37',
            dark: '#116329',
            light: '#2da44e',
            contrastText: '#ffffff',
        },

        text: {
            primary: '#24292f',
            secondary: '#656d76',
            tertiary: '#8c959f',
            disabled: '#d0d7de',
        },

        background: {
            primary: '#ffffff',
            secondary: '#f6f8fa',
            tertiary: '#eaeef2',
            hovered: '#ddd8e0',
        },

        border: {
            primary: '#d0d7de',
            secondary: '#eaeef2',
            focus: '#0969da',
        },

        palette: {
            white: '#ffffff',
            black: '#000000',
            transparent: 'transparent',
        },
    },

    typography: {
        fontFamily: {
            main: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
            heading: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
            mono: '"JetBrains Mono", "Fira Code", Consolas, monospace',
        },

        fontSize: FontSizes,

        fontWeight: {
            light: 300,
            normal: 400,
            medium: 500,
            semibold: 600,
            bold: 700,
        },

        lineHeight: {
            tight: 1.2,
            normal: 1.5,
            relaxed: 1.8,
        },
    },

    spacing: Spacing,
    borderRadius: BorderRadius,

    shadows: {
        sm: '0 1px 3px rgba(0, 0, 0, 0.08)',
        md: '0 4px 12px rgba(0, 0, 0, 0.10)',
        lg: '0 8px 24px rgba(0, 0, 0, 0.12)',
        xl: '0 16px 48px rgba(0, 0, 0, 0.16)',
    },

    zIndex: {
        dropdown: 1000,
        modal: 1050,
        tooltip: 1100,
        overlay: 1200,
    },
};

/**
 * Legacy basic theme - kept for backward compatibility
 * @deprecated Use unhingedDarkTheme instead
 * @public
 */
export const basicTheme: Theme = {
    name: ThemeName.BASIC,

    color: {
        primary: {
            main: '#8550a6',
            dark: '#562b70',
            light: '#a875c4',
            contrastText: '#ffffff',
        },

        secondary: {
            main: '#562b70',
            dark: '#301442',
            light: '#8550a6',
            contrastText: '#ffffff',
        },

        error: {
            main: '#dc3545',
            dark: '#c82333',
            light: '#f5c6cb',
            contrastText: '#ffffff',
        },

        warning: {
            main: '#ffc107',
            dark: '#e0a800',
            light: '#fff3cd',
            contrastText: '#000000',
        },

        success: {
            main: '#28a745',
            dark: '#1e7e34',
            light: '#d4edda',
            contrastText: '#ffffff',
        },

        text: {
            primary: '#ffffff',
            secondary: '#000000',
            tertiary: '#6c757d',
            disabled: '#adb5bd',
        },

        background: {
            primary: '#562b70',
            secondary: '#8550a6',
            tertiary: '#a875c4',
            hovered: '#f0f0f0',
        },

        border: {
            primary: '#301442',
            secondary: '#ffffff',
            focus: '#8550a6',
        },

        palette: {
            white: '#ffffff',
            black: '#000000',
            transparent: 'transparent',
        },
    },

    typography: {
        fontFamily: {
            main: 'Arial, sans-serif',
            heading: 'Roboto, sans-serif',
            mono: 'Consolas, monospace',
        },

        fontSize: FontSizes,

        fontWeight: {
            light: 300,
            normal: 400,
            medium: 500,
            semibold: 600,
            bold: 700,
        },

        lineHeight: {
            tight: 1.2,
            normal: 1.5,
            relaxed: 1.8,
        },
    },

    spacing: Spacing,
    borderRadius: BorderRadius,

    shadows: {
        sm: '0 1px 3px rgba(0, 0, 0, 0.12)',
        md: '0 4px 12px rgba(0, 0, 0, 0.15)',
        lg: '0 8px 24px rgba(0, 0, 0, 0.18)',
        xl: '0 16px 48px rgba(0, 0, 0, 0.24)',
    },

    zIndex: {
        dropdown: 1000,
        modal: 1050,
        tooltip: 1100,
        overlay: 1200,
    },
};

/**
 * Default theme for the platform
 * @public
 */
export const defaultTheme = unhingedDarkTheme;

/**
 * Theme utility functions
 * @public
 */
export const themeUtils = {
    /**
     * Get theme by name
     * @param name - Theme name to retrieve
     * @returns Theme object
     */
    getTheme: (name: ThemeName): Theme => {
        switch (name) {
            case ThemeName.UNHINGED_DARK:
                return unhingedDarkTheme;
            case ThemeName.UNHINGED_LIGHT:
                return unhingedLightTheme;
            case ThemeName.BASIC:
                return basicTheme;
            default:
                return defaultTheme;
        }
    },

    /**
     * Get all available themes
     * @returns Array of all theme objects
     */
    getAllThemes: (): Theme[] => [
        unhingedDarkTheme,
        unhingedLightTheme,
        basicTheme,
    ],

    /**
     * Check if theme is dark
     * @param theme - Theme to check
     * @returns True if theme is dark
     */
    isDarkTheme: (theme: Theme): boolean => {
        return theme.name === ThemeName.UNHINGED_DARK || theme.name === ThemeName.BASIC;
    },
};