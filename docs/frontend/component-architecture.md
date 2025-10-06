# Frontend Component Architecture
## Recursive Component Structure with Design System Integration

**Date**: 2025-10-06  
**Version**: 1.0.0  
**Purpose**: Define standardized component structure for design system integration

---

## **Component Structure Philosophy**

### **Recursive File Organization**

Each component is a **self-contained folder** that mirrors the file structure recursively as needed. Not all files need to be present, but when they exist, they follow this pattern:

```
ComponentName/
├── index.ts              # Main export (required)
├── ComponentName.tsx     # Component implementation (required)
├── styles.ts            # Styled-components with design tokens
├── types.ts             # TypeScript interfaces and types
├── utils.ts             # Component-specific utilities
├── hooks.ts             # Component-specific custom hooks
├── constants.ts         # Component-specific constants
├── stories.ts           # Storybook stories
├── test.tsx             # Component tests
├── README.md            # Component documentation
└── SubComponent/        # Nested components (recursive structure)
    ├── index.ts
    ├── SubComponent.tsx
    ├── styles.ts
    └── types.ts
```

### **Design System Integration Requirements**

Every component **MUST** integrate with our scientific design system:

```typescript
// styles.ts - REQUIRED pattern
import styled from 'styled-components';
import { UnhingedTheme } from '../../design_system';

export const ComponentContainer = styled.div<ComponentProps>`
  // Use design tokens, not hard-coded values
  padding: ${({ theme }) => theme.spatial.spacing.md}px;
  color: ${({ theme }) => theme.colors.semantic.context.text.primary};
  font-size: ${({ theme }) => theme.typography.scale.base}rem;
  
  // Use motion tokens for transitions
  transition: ${({ theme }) => 
    `all ${theme.motion.duration.moderate}ms ${theme.motion.easing.transition}`
  };
  
  // Responsive using breakpoints
  ${({ theme }) => theme.spatial.breakpoints.tablet} {
    padding: ${({ theme }) => theme.spatial.spacing.lg}px;
  }
`;
```

---

## **File Specifications**

### **index.ts (Required)**

**Purpose**: Single export point for the component and its types

```typescript
// index.ts
export { ComponentName } from './ComponentName';
export type { ComponentNameProps, ComponentNameVariant } from './types';

// Re-export sub-components if needed
export { SubComponent } from './SubComponent';
```

### **ComponentName.tsx (Required)**

**Purpose**: Main component implementation with design system integration

```typescript
// ComponentName.tsx
import React from 'react';
import { ComponentNameProps } from './types';
import { ComponentContainer, ComponentTitle } from './styles';
import { useComponentLogic } from './hooks';
import { formatComponentData } from './utils';

export const ComponentName: React.FC<ComponentNameProps> = ({
  title,
  variant = 'primary',
  children,
  ...props
}) => {
  const { state, handlers } = useComponentLogic(props);
  const formattedTitle = formatComponentData(title);

  return (
    <ComponentContainer variant={variant} {...props}>
      <ComponentTitle>{formattedTitle}</ComponentTitle>
      {children}
    </ComponentContainer>
  );
};
```

### **styles.ts (Design System Integration)**

**Purpose**: Styled-components using design tokens exclusively

```typescript
// styles.ts
import styled from 'styled-components';
import { UnhingedTheme } from '../../design_system';
import { ComponentNameProps } from './types';

export const ComponentContainer = styled.div<ComponentNameProps>`
  // Spatial tokens
  padding: ${({ theme }) => theme.spatial.spacing.md}px;
  margin: ${({ theme }) => theme.spatial.spacing.sm}px 0;
  border-radius: ${({ theme }) => theme.spatial.radius.md}px;
  
  // Color tokens based on variant
  background: ${({ theme, variant }) => {
    switch (variant) {
      case 'primary': return theme.colors.semantic.intent.primary;
      case 'secondary': return theme.colors.semantic.intent.secondary;
      default: return theme.colors.semantic.context.background.primary;
    }
  }};
  
  // Typography tokens
  font-family: ${({ theme }) => theme.typography.families.primary};
  font-size: ${({ theme }) => theme.typography.scale.base}rem;
  line-height: ${({ theme }) => theme.typography.lineHeights.base};
  
  // Motion tokens
  transition: ${({ theme }) => 
    `all ${theme.motion.duration.moderate}ms ${theme.motion.easing.transition}`
  };
  
  // Responsive breakpoints
  @media (min-width: ${({ theme }) => theme.spatial.breakpoints.tablet}px) {
    padding: ${({ theme }) => theme.spatial.spacing.lg}px;
  }
  
  // Feature level adaptations
  ${({ theme }) => theme.platform.web.boxShadow && `
    box-shadow: ${theme.platform.web.boxShadow.small};
  `}
`;

export const ComponentTitle = styled.h3`
  margin: 0 0 ${({ theme }) => theme.spatial.spacing.sm}px 0;
  color: ${({ theme }) => theme.colors.semantic.context.text.primary};
  font-size: ${({ theme }) => theme.typography.semantic.heading.h3.fontSize}rem;
  font-weight: ${({ theme }) => theme.typography.semantic.heading.h3.fontWeight};
  line-height: ${({ theme }) => theme.typography.semantic.heading.h3.lineHeight};
`;
```

### **types.ts (TypeScript Definitions)**

**Purpose**: Component-specific type definitions with design system integration

```typescript
// types.ts
import { ReactNode } from 'react';
import { UnhingedTheme } from '../../design_system';

export interface ComponentNameProps {
  // Required props
  title: string;
  
  // Optional props with design system variants
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger';
  size?: 'small' | 'medium' | 'large';
  density?: 'compact' | 'comfortable' | 'spacious';
  
  // Standard React props
  children?: ReactNode;
  className?: string;
  
  // Event handlers
  onClick?: () => void;
  onHover?: () => void;
}

export type ComponentNameVariant = ComponentNameProps['variant'];
export type ComponentNameSize = ComponentNameProps['size'];
export type ComponentNameDensity = ComponentNameProps['density'];

// Theme-aware styled component props
export interface StyledComponentProps extends ComponentNameProps {
  theme: UnhingedTheme;
}
```

### **utils.ts (Component Utilities)**

**Purpose**: Component-specific utility functions

```typescript
// utils.ts
import { UnhingedTheme } from '../../design_system';
import { ComponentNameProps } from './types';

export const formatComponentData = (data: string): string => {
  return data.trim().toLowerCase();
};

export const getVariantStyles = (
  variant: ComponentNameProps['variant'],
  theme: UnhingedTheme
) => {
  switch (variant) {
    case 'primary':
      return {
        background: theme.colors.semantic.intent.primary,
        color: theme.colors.semantic.context.text.inverse,
      };
    case 'secondary':
      return {
        background: theme.colors.semantic.intent.secondary,
        color: theme.colors.semantic.context.text.primary,
      };
    default:
      return {
        background: theme.colors.semantic.context.background.primary,
        color: theme.colors.semantic.context.text.primary,
      };
  }
};

export const calculateResponsiveSpacing = (
  size: ComponentNameProps['size'],
  theme: UnhingedTheme
): string => {
  switch (size) {
    case 'small': return `${theme.spatial.spacing.sm}px`;
    case 'large': return `${theme.spatial.spacing.lg}px`;
    default: return `${theme.spatial.spacing.md}px`;
  }
};
```

### **hooks.ts (Custom Hooks)**

**Purpose**: Component-specific React hooks

```typescript
// hooks.ts
import { useState, useEffect, useCallback } from 'react';
import { ComponentNameProps } from './types';

export const useComponentLogic = (props: ComponentNameProps) => {
  const [state, setState] = useState({
    isActive: false,
    isLoading: false,
  });

  const handleClick = useCallback(() => {
    setState(prev => ({ ...prev, isActive: !prev.isActive }));
    props.onClick?.();
  }, [props.onClick]);

  const handleHover = useCallback(() => {
    props.onHover?.();
  }, [props.onHover]);

  useEffect(() => {
    // Component-specific side effects
  }, []);

  return {
    state,
    handlers: {
      onClick: handleClick,
      onHover: handleHover,
    },
  };
};
```

### **constants.ts (Component Constants)**

**Purpose**: Component-specific constants and configuration

```typescript
// constants.ts
export const COMPONENT_VARIANTS = {
  PRIMARY: 'primary',
  SECONDARY: 'secondary',
  SUCCESS: 'success',
  WARNING: 'warning',
  DANGER: 'danger',
} as const;

export const COMPONENT_SIZES = {
  SMALL: 'small',
  MEDIUM: 'medium',
  LARGE: 'large',
} as const;

export const COMPONENT_DENSITY = {
  COMPACT: 'compact',
  COMFORTABLE: 'comfortable',
  SPACIOUS: 'spacious',
} as const;

export const DEFAULT_PROPS = {
  variant: COMPONENT_VARIANTS.PRIMARY,
  size: COMPONENT_SIZES.MEDIUM,
  density: COMPONENT_DENSITY.COMFORTABLE,
} as const;
```

---

## **Component Categories**

### **Atomic Components** (`/components/atoms/`)
- Button, Input, Label, Icon, Avatar
- Single responsibility, no sub-components
- Direct design token usage

### **Molecular Components** (`/components/molecules/`)
- SearchBox, NavigationItem, Card, Modal
- Composed of atoms
- May have simple sub-components

### **Organism Components** (`/components/organisms/`)
- Header, Sidebar, ChatInterface, PromptSurgeryPanel
- Complex compositions
- Multiple levels of sub-components

### **Template Components** (`/components/templates/`)
- PageLayout, ChatLayout, DashboardLayout
- Page-level compositions
- Orchestrate organisms

---

## **Migration Strategy**

### **Phase 1: Standardize Structure**
1. Convert existing components to folder structure
2. Separate concerns into appropriate files
3. Add missing TypeScript types

### **Phase 2: Design System Integration**
1. Replace hard-coded values with design tokens
2. Implement responsive breakpoints
3. Add motion and animation tokens

### **Phase 3: Component Enhancement**
1. Add comprehensive testing
2. Create Storybook stories
3. Document component APIs

---

**Next**: DAG Roadmap for Component Migration and Design System Integration
