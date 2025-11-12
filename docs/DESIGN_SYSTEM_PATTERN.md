# Design System Pattern - Two-Tier Architecture

## Overview

The Unhinged design system implements a **two-tier architecture** that separates platform-agnostic specifications from platform-specific implementations. This pattern enables consistent UI across multiple platforms while allowing platform-specific optimizations.

## Architecture

### Tier 1: Abstraction Layer (Platform-Agnostic)

**Location**: `libs/design_system/`

Defines semantic specifications that are independent of any platform:

```
libs/design_system/
├── tokens/                          # Design tokens (colors, typography, spacing)
│   ├── colors.yaml                 # 16 semantic color roles
│   ├── typography.yaml             # 5 type sizes, 3 weights, 2 families
│   ├── spacing.yaml                # 10 spacing values (4px base unit)
│   ├── elevation.yaml              # 4 shadow depths, z-index layers
│   ├── motion.yaml                 # Interaction states
│   └── components.yaml             # Component composition primitives
└── components/                      # Component specifications
    ├── primitives/                 # Basic components (button, input, etc.)
    ├── containers/                 # Container components (window, tabs, etc.)
    ├── complex/                    # Complex components (graph, etc.)
    └── graph/                      # Graph-specific components
```

### Tier 2: Platform Implementation (Platform-Specific)

**Location**: `libs/design_system/build/generators/`

Generates platform-specific implementations from Tier 1 specifications:

```
libs/design_system/build/
├── generators/
│   ├── gtk4_generator.py           # GTK4 CSS + Python widget generation
│   ├── alpine_native_generator.py  # Alpine native C graphics (future)
│   ├── react_generator.py          # React/TypeScript (future)
│   └── flutter_generator.py        # Flutter/Dart (future)
└── design_token_builder.py         # Build orchestrator
```

## Component Specification Pattern

### YAML Structure

Each component is defined in YAML with these sections:

```yaml
component:
  id: "workspace-tabs"              # Unique identifier
  name: "Workspace Tabs"            # Display name
  category: "container"             # Category (primitive, container, complex)
  
  description: |                    # Semantic description
    Non-closeable workspace tabs...
  
  interface:                        # Platform-agnostic interface
    properties:                     # Component properties
      tabs:
        type: "array"
        description: "Array of tab definitions"
    
    states:                         # Component states
      default:
        description: "Initial state"
        visual_tokens: ["colors.surface.default"]
      
      tab_selected:
        description: "Tab is selected"
        visual_tokens: ["colors.action.primary"]
    
    events:                         # Component events
      tab_changed:
        description: "User switched tabs"
        payload:
          previous_tab_id: "string"
          new_tab_id: "string"
  
  styling:                          # Semantic styling
    default_state:
      background: "colors.surface.default"
      padding: "spacing.scale.sp_2"
    
    state_overrides:
      tab_selected:
        background: "colors.action.primary"
  
  accessibility:                    # WCAG compliance
    keyboard_support: true
    screen_reader_label: "required"
    keyboard_interactions:
      - key: "Left Arrow"
        action: "select_previous_tab"
  
  examples:                         # Usage examples
    - name: "Document workspace tabs"
      properties:
        tabs: [...]

metadata:
  version: "1.0.0"
  implementation_status:
    gtk4: "pending"
    alpine_native: "pending"
```

## Design Tokens

### Semantic Token System

Tokens are organized by semantic role, not by value:

```yaml
# ✅ CORRECT - Semantic naming
colors:
  action:
    primary: "#0066CC"
    secondary: "#6C757D"
    disabled: "#E9ECEF"
  
  surface:
    default: "#FFFFFF"
    elevated: "#F8F9FA"
    overlay: "#000000"

# ❌ WRONG - Value-based naming
colors:
  blue_500: "#0066CC"
  gray_600: "#6C757D"
  light_gray: "#F8F9FA"
```

### Token Categories

1. **Colors** (16 semantic roles)
   - Action: primary, secondary, tertiary, disabled
   - Feedback: success, warning, error, info
   - Surface: default, elevated, overlay, inverse
   - Text: primary, secondary, tertiary, inverse, disabled
   - Border: default, subtle, strong
   - Interactive: hover, active, focus

2. **Typography** (5 sizes, 3 weights, 2 families)
   - Sizes: display, heading, body, caption, code
   - Weights: regular (400), medium (500), bold (700)
   - Families: prose (Inter), code (JetBrains Mono)

3. **Spacing** (10 values, 4px base unit)
   - Scale: sp_0_5 (2px) through sp_12 (48px)
   - Pattern: Vertical-dominant, horizontal follows

4. **Elevation** (4 shadow depths)
   - Shadows: 1, 2, 3, 4 (increasing depth)
   - Z-Index: base, raised, floating, modal, notification
   - Border Radius: none, sm, md, lg

## Generation Pipeline

### Build Process

```bash
# 1. Validate specifications
make validate-components

# 2. Generate platform artifacts
make components-gtk4              # Generate GTK4 CSS + Python
make components-alpine            # Generate Alpine native C
make components-react             # Generate React/TypeScript

# 3. Output location
generated/design_system/
├── gtk4/
│   ├── design-tokens.css
│   ├── theme-light.css
│   ├── theme-dark.css
│   └── components.css
├── alpine/
│   └── components.c
└── react/
    └── components.tsx
```

### Generator Pattern

Each generator implements the same interface:

```python
class PlatformGenerator:
    def generate(self, component_spec: dict) -> GeneratedArtifact:
        """Generate platform-specific implementation"""
        # 1. Validate specification
        # 2. Resolve design tokens
        # 3. Generate platform code
        # 4. Apply platform-specific optimizations
        return artifact
```

## Usage Pattern

### For Developers

1. **Define component in YAML**
   ```bash
   vim libs/design_system/components/containers/tabs.yaml
   ```

2. **Validate specification**
   ```bash
   make validate-components
   ```

3. **Generate platform implementations**
   ```bash
   make components-gtk4
   ```

4. **Use generated component**
   ```python
   from generated.design_system.gtk4.workspace_tabs import WorkspaceTabs
   ```

### For Designers

1. **Update design tokens**
   ```bash
   vim libs/design_system/tokens/colors.yaml
   ```

2. **Regenerate all platforms**
   ```bash
   make design-tokens
   ```

3. **Verify consistency**
   - All platforms use same tokens
   - Theme switching works correctly
   - Accessibility maintained

## Benefits

### 1. Consistency
- Single source of truth for component definitions
- All platforms implement same interface
- Design tokens ensure visual consistency

### 2. Scalability
- Add new platforms without changing existing code
- Reuse specifications across platforms
- Centralized token management

### 3. Maintainability
- Changes in one place propagate to all platforms
- Clear separation of concerns
- Easier to debug and test

### 4. Accessibility
- WCAG compliance built into specifications
- Keyboard navigation defined once
- Screen reader support standardized

### 5. Performance
- Build-time generation (zero runtime cost)
- Intelligent caching
- Parallel generation support

## Current Status

### Implemented
✅ Design token system (colors, typography, spacing, elevation)
✅ Component specification schema
✅ GTK4 generator (CSS + Python widgets)
✅ Build system integration
✅ Validation framework

### In Progress
🔄 Component library expansion
🔄 Alpine native generator
🔄 React/TypeScript generator

### Future
📋 Component composition validation
📋 Cross-platform compatibility checking
📋 Visual component preview
📋 Hot reloading for development

## References

- **Design System README**: `libs/design_system/README.md`
- **Implementation Summary**: `libs/design_system/IMPLEMENTATION_SUMMARY.md`
- **Component Generation**: `libs/design_system/COMPONENT_GENERATION.md`
- **Build System**: `build/README.md`

