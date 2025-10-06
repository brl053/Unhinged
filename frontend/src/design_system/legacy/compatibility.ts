// ============================================================================
// Legacy Theme Compatibility Layer
// ============================================================================
//
// @file compatibility.ts
// @version 2.0.0
// @author Unhinged Design System Team
// @date 2025-10-06
// @description Backward compatibility layer for existing basicTheme usage
//
// This module provides a compatibility layer that maps the new scientific
// design system tokens to the old basicTheme structure, ensuring existing
// components continue to work during the migration period.
// ============================================================================

import { UnhingedTheme } from '../themes/light';

/**
 * Legacy theme interface - matches the original basicTheme structure
 * This interface represents the old theme format that existing components expect
 */
export interface LegacyTheme {
  name: string;
  color: {
    palette: {
      white: string;
    };
    text: {
      primary: string;
      secondary: string;
    };
    background: {
      primary: string;
      secondary: string;
      hovered: string;
    };
    border: {
      primary: string;
      secondary: string;
    };
  };
  fonts: {
    main: string;
    heading: string;
  };
}

/**
 * Extended legacy theme interface for components expecting additional properties
 * Some components (like ErrorBoundary) expect different color property names
 */
export interface ExtendedLegacyTheme extends LegacyTheme {
  colors?: {
    // Bootstrap-style color names used in some components
    surface?: string;
    danger?: string;
    primary?: string;
    primaryDark?: string;
    text?: string;
    background?: string;
    border?: string;
    muted?: string;
    hover?: string;
  };
}

/**
 * Create legacy theme from new design system theme
 * Maps new scientific tokens to old theme structure
 * 
 * @param theme - New UnhingedTheme object
 * @returns Legacy theme object compatible with existing components
 */
export const createLegacyTheme = (theme: UnhingedTheme): ExtendedLegacyTheme => ({
  // Basic legacy structure
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
    heading: theme.typography.families.secondary,
  },
  
  // Extended properties for components expecting Bootstrap-style names
  colors: {
    surface: theme.colors.semantic.context.background.secondary,
    danger: theme.colors.semantic.intent.danger,
    primary: theme.colors.semantic.intent.primary,
    primaryDark: theme.colors.primitive.chromatic.blue, // Darker variant
    text: theme.colors.semantic.context.text.primary,
    background: theme.colors.semantic.context.background.primary,
    border: theme.colors.semantic.context.border.primary,
    muted: theme.colors.semantic.context.text.tertiary,
    hover: theme.colors.semantic.context.background.tertiary,
  },
});

/**
 * Migration utilities for component updates
 * Helps developers migrate from old theme properties to new ones
 */
export const migrationUtils = {
  /**
   * Map old color property paths to new ones
   * Provides guidance for updating component styles
   */
  colorMigrationMap: {
    // Old path -> New path
    'theme.color.palette.white': 'theme.colors.primitive.achromatic.white',
    'theme.color.text.primary': 'theme.colors.semantic.context.text.primary',
    'theme.color.text.secondary': 'theme.colors.semantic.context.text.secondary',
    'theme.color.background.primary': 'theme.colors.semantic.context.background.primary',
    'theme.color.background.secondary': 'theme.colors.semantic.context.background.secondary',
    'theme.color.background.hovered': 'theme.colors.semantic.context.background.tertiary',
    'theme.color.border.primary': 'theme.colors.semantic.context.border.primary',
    'theme.color.border.secondary': 'theme.colors.semantic.context.border.secondary',
    'theme.fonts.main': 'theme.typography.families.primary',
    'theme.fonts.heading': 'theme.typography.families.secondary',
  },
  
  /**
   * Generate migration warnings for deprecated usage
   * @param oldPath - Old theme property path
   * @returns Warning message with migration guidance
   */
  generateMigrationWarning: (oldPath: string): string => {
    const newPath = migrationUtils.colorMigrationMap[oldPath as keyof typeof migrationUtils.colorMigrationMap];
    if (newPath) {
      return `⚠️  Deprecated theme path "${oldPath}" should be updated to "${newPath}"`;
    }
    return `⚠️  Unknown deprecated theme path "${oldPath}"`;
  },
  
  /**
   * Validate component for legacy theme usage
   * Scans component code for old theme property usage
   * @param componentCode - Component source code as string
   * @returns Array of migration warnings
   */
  scanForLegacyUsage: (componentCode: string): string[] => {
    const warnings: string[] = [];
    const legacyPatterns = Object.keys(migrationUtils.colorMigrationMap);
    
    legacyPatterns.forEach(pattern => {
      if (componentCode.includes(pattern)) {
        warnings.push(migrationUtils.generateMigrationWarning(pattern));
      }
    });
    
    return warnings;
  },
};

/**
 * Theme provider compatibility wrapper
 * Provides both new and legacy theme objects to components
 */
export interface CompatibilityThemeProviderProps {
  theme: UnhingedTheme;
  children: React.ReactNode;
}

/**
 * Enhanced theme object that includes both new and legacy structures
 * Allows gradual migration of components
 */
export interface CompatibilityTheme extends UnhingedTheme {
  legacy: ExtendedLegacyTheme;
  // Add extended colors directly to theme for ErrorBoundary compatibility
  colors: UnhingedTheme['colors'] & {
    // Bootstrap-style color names used in some components
    surface?: string;
    danger?: string;
    primary?: string;
    primaryDark?: string;
    text?: string;
    background?: string;
    border?: string;
    muted?: string;
    hover?: string;
  };
}

/**
 * Create compatibility theme with both new and legacy structures
 * @param theme - New UnhingedTheme object
 * @returns Enhanced theme with legacy compatibility
 */
export const createCompatibilityTheme = (theme: UnhingedTheme): CompatibilityTheme => ({
  ...theme,
  legacy: createLegacyTheme(theme),
  // Extend colors with Bootstrap-style properties for ErrorBoundary compatibility
  colors: {
    ...theme.colors,
    // Bootstrap-style color names used in some components
    surface: theme.colors.semantic.context.background.secondary,
    danger: theme.colors.semantic.intent.danger,
    primary: theme.colors.semantic.intent.primary,
    primaryDark: theme.colors.primitive.chromatic.blue, // Darker variant
    text: theme.colors.semantic.context.text.primary,
    background: theme.colors.semantic.context.background.primary,
    border: theme.colors.semantic.context.border.primary,
    muted: theme.colors.semantic.context.text.tertiary,
    hover: theme.colors.semantic.context.background.tertiary,
  },
});

/**
 * Styled-components theme type augmentation
 * Extends the DefaultTheme interface to include legacy properties
 */
declare module 'styled-components' {
  export interface DefaultTheme extends CompatibilityTheme {}
}

/**
 * Migration checklist for component updates
 * Provides a systematic approach to migrating components
 */
export const migrationChecklist = {
  steps: [
    {
      id: 'audit',
      title: 'Audit Component',
      description: 'Scan component for legacy theme usage',
      action: 'Use migrationUtils.scanForLegacyUsage()',
    },
    {
      id: 'update-imports',
      title: 'Update Imports',
      description: 'Import new design system tokens',
      action: 'Import from @unhinged/design-system',
    },
    {
      id: 'replace-properties',
      title: 'Replace Theme Properties',
      description: 'Update theme property paths',
      action: 'Use colorMigrationMap for guidance',
    },
    {
      id: 'add-semantic-tokens',
      title: 'Add Semantic Tokens',
      description: 'Replace hard-coded values with semantic tokens',
      action: 'Use spacing(), fontSize(), etc. utilities',
    },
    {
      id: 'test-compatibility',
      title: 'Test Compatibility',
      description: 'Ensure component works with new theme',
      action: 'Run visual regression tests',
    },
    {
      id: 'remove-legacy',
      title: 'Remove Legacy Dependencies',
      description: 'Remove references to legacy theme properties',
      action: 'Clean up compatibility layer usage',
    },
  ],
  
  /**
   * Generate migration report for a component
   * @param componentName - Name of the component
   * @param componentCode - Component source code
   * @returns Migration report object
   */
  generateReport: (componentName: string, componentCode: string) => {
    const warnings = migrationUtils.scanForLegacyUsage(componentCode);
    const completedSteps = migrationChecklist.steps.filter(step => {
      // Simple heuristics to determine completion
      switch (step.id) {
        case 'audit':
          return warnings.length > 0; // Audit completed if warnings found
        case 'update-imports':
          return componentCode.includes('@unhinged/design-system');
        case 'replace-properties':
          return warnings.length === 0; // No legacy usage found
        default:
          return false; // Manual verification required
      }
    });
    
    return {
      componentName,
      totalSteps: migrationChecklist.steps.length,
      completedSteps: completedSteps.length,
      progress: Math.round((completedSteps.length / migrationChecklist.steps.length) * 100),
      warnings,
      nextSteps: migrationChecklist.steps.filter(step => 
        !completedSteps.some(completed => completed.id === step.id)
      ),
    };
  },
};

/**
 * Development helpers for migration process
 */
export const migrationDevUtils = {
  /**
   * Log migration status to console
   * @param report - Migration report from generateReport()
   */
  logMigrationStatus: (report: ReturnType<typeof migrationChecklist.generateReport>) => {
    console.group(`🔄 Migration Status: ${report.componentName}`);
    console.log(`Progress: ${report.progress}% (${report.completedSteps}/${report.totalSteps})`);
    
    if (report.warnings.length > 0) {
      console.warn('Warnings:', report.warnings);
    }
    
    if (report.nextSteps.length > 0) {
      console.log('Next steps:', report.nextSteps.map(step => step.title));
    }
    
    console.groupEnd();
  },
  
  /**
   * Generate migration documentation
   * @param reports - Array of migration reports
   * @returns Markdown documentation string
   */
  generateMigrationDocs: (reports: ReturnType<typeof migrationChecklist.generateReport>[]): string => {
    const totalComponents = reports.length;
    const fullyMigrated = reports.filter(r => r.progress === 100).length;
    const averageProgress = Math.round(
      reports.reduce((sum, r) => sum + r.progress, 0) / totalComponents
    );
    
    return `
# Migration Progress Report

**Overall Progress:** ${averageProgress}%  
**Components:** ${fullyMigrated}/${totalComponents} fully migrated

## Component Status

${reports.map(report => `
### ${report.componentName}
- **Progress:** ${report.progress}%
- **Warnings:** ${report.warnings.length}
- **Next Steps:** ${report.nextSteps.length}
`).join('')}

## Migration Checklist

${migrationChecklist.steps.map((step, index) => `
${index + 1}. **${step.title}**  
   ${step.description}  
   *Action:* ${step.action}
`).join('')}
    `.trim();
  },
};

/**
 * Export all compatibility utilities
 */
export default {
  createLegacyTheme,
  createCompatibilityTheme,
  migrationUtils,
  migrationChecklist,
  migrationDevUtils,
};
