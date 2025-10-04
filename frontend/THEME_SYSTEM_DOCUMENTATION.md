/**
 * @fileoverview Unhinged Platform Theme System Documentation
 * @purpose Complete documentation of the enhanced theme system and component architecture
 * @editable true - LLM should update this documentation when theme system changes
 * @deprecated false
 * 
 * @remarks
 * This documentation serves as the single source of truth for the theme system.
 * All future LLM interactions should reference this file to understand the current
 * theme structure and avoid hardcoding values.
 */

# Unhinged Platform Theme System Documentation

## 🎯 **Purpose**
This document records the complete theme system architecture for the Unhinged Platform, ensuring consistent styling and preventing future hardcoding issues.

## 🚨 **Critical Rules for LLMs**

### **ALWAYS USE THEME TOKENS**
```typescript
// ✅ CORRECT - Use theme tokens
color: ${({ theme }) => theme.color.primary.main};
font-size: ${({ theme }) => theme.typography.fontSize.md};
border-radius: ${({ theme }) => theme.borderRadius.md};

// ❌ WRONG - Hardcoded values
color: '#58a6ff';
font-size: '1rem';
border-radius: '8px';
```

### **ALWAYS USE TRANSIENT PROPS**
```typescript
// ✅ CORRECT - Transient props (prefixed with $)
const StyledDiv = styled.div<{ $isActive: boolean }>`
  color: ${({ $isActive, theme }) => $isActive ? theme.color.primary.main : theme.color.text.primary};
`;

// Usage
<StyledDiv $isActive={true} />

// ❌ WRONG - Regular props passed to DOM
const StyledDiv = styled.div<{ isActive: boolean }>`
  color: ${({ isActive, theme }) => isActive ? theme.color.primary.main : theme.color.text.primary};
`;
```

### **ALWAYS ADD TSDOC HEADERS**
```typescript
/**
 * @fileoverview Brief description of the file's purpose
 * @purpose Detailed explanation of what this file does
 * @editable true/false - Whether LLM should modify this file
 * @deprecated false - Whether this file is deprecated
 * 
 * @remarks
 * Additional context, instructions, or warnings for future LLM interactions
 */
```

## 🎨 **Theme Structure**

### **Color System**
```typescript
theme.color = {
  // Primary brand colors
  primary: {
    main: '#58a6ff',      // Main brand color
    dark: '#4493e6',      // Hover states
    light: '#79b8ff',     // Light backgrounds
    contrastText: '#ffffff' // Text on primary backgrounds
  },
  
  // Secondary accent colors
  secondary: {
    main: '#b392f0',
    dark: '#9a7dd8',
    light: '#c8a7f5',
    contrastText: '#ffffff'
  },
  
  // Semantic colors
  error: { main, dark, light, contrastText },
  warning: { main, dark, light, contrastText },
  success: { main, dark, light, contrastText },
  
  // Text colors
  text: {
    primary: '#e1e4e8',    // Main text
    secondary: '#8b949e',  // Secondary text
    tertiary: '#6a737d',   // Muted text
    disabled: '#484f58'    // Disabled text
  },
  
  // Background colors
  background: {
    primary: '#0d1117',    // Main background
    secondary: '#161b22',  // Cards, panels
    tertiary: '#21262d',   // Elevated surfaces
    hovered: '#30363d'     // Hover states
  },
  
  // Border colors
  border: {
    primary: '#30363d',    // Default borders
    secondary: '#21262d',  // Subtle borders
    focus: '#58a6ff'       // Focus indicators
  }
}
```

### **Typography System**
```typescript
theme.typography = {
  fontFamily: {
    main: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    heading: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    mono: '"JetBrains Mono", "Fira Code", Consolas, monospace'
  },
  
  fontSize: {
    xs: '0.75rem',   // 12px
    sm: '0.875rem',  // 14px
    md: '1rem',      // 16px
    lg: '1.125rem',  // 18px
    xl: '1.5rem',    // 24px
    '2xl': '2rem',   // 32px
    '3xl': '2.5rem'  // 40px
  },
  
  fontWeight: {
    light: 300,
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700
  },
  
  lineHeight: {
    tight: 1.2,
    normal: 1.5,
    relaxed: 1.8
  }
}
```

### **Spacing System**
```typescript
theme.spacing = {
  xs: '0.25rem',   // 4px
  sm: '0.5rem',    // 8px
  md: '1rem',      // 16px
  lg: '1.5rem',    // 24px
  xl: '2rem',      // 32px
  '2xl': '3rem',   // 48px
  '3xl': '4rem'    // 64px
}
```

### **Border Radius System**
```typescript
theme.borderRadius = {
  xs: '2px',
  sm: '4px',
  md: '8px',
  lg: '12px',
  xl: '16px',
  full: '50%'
}
```

## 🛠 **Available Themes**

### **1. Unhinged Dark (Default)**
- **Name**: `unhingedDarkTheme`
- **Usage**: Primary dark theme for the platform
- **Colors**: GitHub-inspired dark palette

### **2. Unhinged Light**
- **Name**: `unhingedLightTheme`
- **Usage**: Light theme for accessibility
- **Colors**: GitHub-inspired light palette

### **3. Basic Theme (Deprecated)**
- **Name**: `basicTheme`
- **Usage**: Legacy theme - use `unhingedDarkTheme` instead
- **Status**: Kept for backward compatibility

## 📦 **Component Examples**

### **TextEditor Component**
```typescript
// ✅ Proper theme usage
export const EditorContainer = styled.div<EditorContainerProps>`
  border: 1px solid ${({ theme, $hasError }) => 
    $hasError ? theme.color.error.main : theme.color.border.primary};
  border-radius: ${({ theme }) => theme.borderRadius.md};
  background: ${({ theme }) => theme.color.background.primary};
`;
```

### **Button Component**
```typescript
// ✅ Proper theme usage
export const Button = styled.button`
  padding: ${({ theme }) => theme.spacing.sm} ${({ theme }) => theme.spacing.lg};
  background: ${({ theme }) => theme.color.primary.main};
  color: ${({ theme }) => theme.color.primary.contrastText};
  border-radius: ${({ theme }) => theme.borderRadius.md};
  font-size: ${({ theme }) => theme.typography.fontSize.sm};
  font-weight: ${({ theme }) => theme.typography.fontWeight.medium};
  
  &:hover {
    background: ${({ theme }) => theme.color.primary.dark};
  }
`;
```

## 🔧 **Theme Utilities**

### **Theme Selection**
```typescript
import { themeUtils, ThemeName } from './design_system/theme';

// Get specific theme
const darkTheme = themeUtils.getTheme(ThemeName.UNHINGED_DARK);

// Get all themes
const allThemes = themeUtils.getAllThemes();

// Check if theme is dark
const isDark = themeUtils.isDarkTheme(darkTheme);
```

## 🚨 **Common Mistakes to Avoid**

### **1. Hardcoded Values**
```typescript
// ❌ WRONG
color: '#58a6ff';
font-size: '1rem';
padding: '16px';

// ✅ CORRECT
color: ${({ theme }) => theme.color.primary.main};
font-size: ${({ theme }) => theme.typography.fontSize.md};
padding: ${({ theme }) => theme.spacing.md};
```

### **2. Non-Transient Props**
```typescript
// ❌ WRONG - Causes React warnings
const StyledDiv = styled.div<{ isActive: boolean }>`
  color: ${({ isActive }) => isActive ? 'blue' : 'gray'};
`;

// ✅ CORRECT - Uses transient props
const StyledDiv = styled.div<{ $isActive: boolean }>`
  color: ${({ $isActive, theme }) => 
    $isActive ? theme.color.primary.main : theme.color.text.secondary};
`;
```

### **3. Missing TSDoc Headers**
```typescript
// ❌ WRONG - No documentation
import { styled } from 'styled-components';

// ✅ CORRECT - Proper documentation
/**
 * @fileoverview Component styles for XYZ
 * @purpose Styled components for the XYZ feature
 * @editable true
 * @deprecated false
 */
import { styled } from 'styled-components';
```

## 📝 **Maintenance Notes**

### **When Adding New Components**
1. Always use theme tokens instead of hardcoded values
2. Add proper TSDoc headers to all files
3. Use transient props for styled-components
4. Follow the established naming conventions
5. Update this documentation if adding new theme properties

### **When Modifying Themes**
1. Update all theme objects consistently
2. Test with both dark and light themes
3. Ensure accessibility standards are met
4. Update this documentation with changes

### **LLM Instructions**
- **ALWAYS** reference this documentation before making theme-related changes
- **NEVER** hardcode color, spacing, or typography values
- **ALWAYS** use the established theme structure
- **ALWAYS** add TSDoc headers to new files
- **ALWAYS** use transient props in styled-components

## 🎉 **Current Status**

### **✅ Completed**
- Enhanced theme system with comprehensive tokens
- Fixed all hardcoded values in ComponentShowcase
- Fixed all hardcoded values in TextEditor component
- Added proper TSDoc documentation
- Fixed styled-components prop warnings
- Fixed React key warnings in SideNav

### **🔄 Active**
- Theme system is fully functional
- All components use proper theme tokens
- Development server running successfully
- No TypeScript errors
- No React warnings

This documentation ensures that future LLM interactions will maintain consistency and avoid the issues we just fixed. Remember: **ALWAYS USE THEME TOKENS, NEVER HARDCODE VALUES!**
