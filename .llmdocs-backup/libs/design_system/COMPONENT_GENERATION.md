# 📦 Component Generation System

**Platform-agnostic component generation with semantic design tokens**

## Overview

The Component Generation System extends the Unhinged Design System with **specification-first, platform-equal** component generation. Components are defined once in YAML and generated for multiple platforms, ensuring consistency across GTK4 desktop applications, Alpine+Unhinged native implementations, and future platforms.

## Architecture

```
libs/design_system/
├── components/               # Platform-agnostic component specifications
│   ├── _schema.yaml         # Component meta-schema validation
│   ├── primitives/          # Basic UI elements (button, input, etc.)
│   ├── containers/          # Layout components (modal, card, etc.)
│   ├── complex/             # Composite components (text-editor, etc.)
│   └── system/              # System-level components
├── build/                   # Generation and validation tools
│   ├── component_generator.py       # Component orchestrator
│   ├── component_validator.py       # Specification validation
│   ├── component_build_module.py    # Build system integration
│   └── generators/                  # Platform-specific generators
│       ├── _abstract_generator.py   # Generator interface
│       └── gtk4/                    # GTK4 Python generator
└── generated/               # Generated artifacts (do not edit)
    └── design_system/
        └── gtk4/            # GTK4-specific outputs
```

## Component Specification Format

Components are defined in YAML with LlmDocs annotations:

```yaml
# @llm-type component-specification
# @llm-legend Platform-agnostic component specification
# @llm-key Core component definition with semantic behavior
# @llm-map Part of design system component hierarchy
# @llm-axiom Component specifications must be platform-agnostic
# @llm-contract Defines interface, states, events, and styling
# @llm-token component-name: Description of component purpose

component:
  id: "component-name"           # kebab-case identifier
  name: "Component Name"         # Human-readable name
  category: "primitive"          # primitive|container|complex|system
  
  description: |
    Detailed description of component purpose and usage.
    
  interface:
    properties:                  # Component properties
      property_name:
        type: "string"           # string|boolean|number|enum
        required: true           # Optional, defaults to false
        default: "value"         # Default value
        description: "Purpose"   # Property description
    
    states:                      # Component states
      default:
        description: "Initial state"
        visual_tokens: ["colors.action.primary"]
        triggers: ["component_mount"]
      
    events:                      # Component events
      event_name:
        description: "Event description"
        payload:
          field: "type"          # Event payload structure
  
  styling:                       # Visual styling with tokens
    default_state:
      background: "colors.surface.default"
      color: "colors.text.primary"
      padding_vertical: "spacing.scale.sp_2"
      padding_horizontal: "spacing.scale.sp_4"
  
  accessibility:                 # Accessibility requirements
    keyboard_support: true
    screen_reader_label: "required"
    focus_indicator: "required"
    contrast_requirement: "WCAG_AA"
```

## Usage

### Validate Components

```bash
# Validate all component specifications
make validate-components

# Validate specific component
python3 libs/design_system/build/component_validator.py \
  --components-dir libs/design_system/components/primitives
```

### Generate Components

```bash
# Generate components for all platforms
make components

# Generate GTK4 components specifically
make components-gtk4

# Clean generated artifacts
make clean-components
```

### Direct Python Usage

```python
from component_validator import ComponentSpecificationValidator
from component_generator import ComponentGeneratorOrchestrator

# Validate component
validator = ComponentSpecificationValidator(schema_path, tokens_dir)
result = validator.validate_specification(component_path)

# Generate component
orchestrator = ComponentGeneratorOrchestrator(project_root)
orchestrator.register_generator("GTK4", GTK4ComponentGenerator)
summary = orchestrator.generate_all_components(["GTK4"])
```

## GTK4 Generator

The GTK4 generator produces Python GTK4 widgets with:

- **GObject Properties**: Type-safe property definitions
- **Signal Handling**: Event emission and handling
- **CSS Integration**: Design token CSS classes
- **Accessibility**: GNOME HIG compliance
- **LlmDocs**: Full AI comprehension annotations

### Generated Widget Structure

```python
class ComponentName(Gtk.Widget):
    """Generated GTK4 widget with LlmDocs annotations"""
    
    __gtype_name__ = 'ComponentName'
    
    # GObject properties from specification
    property_name = GObject.Property(type=str, default="")
    
    # Signals from specification events
    __gsignals__ = {
        'event-name': (GObject.SignalFlags.RUN_FIRST, None, (object,))
    }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_css_class("ds-component")
        self.add_css_class("ds-component-name")
```

## Validation System

Comprehensive validation ensures specification quality:

- **Schema Validation**: Components must conform to meta-schema
- **Token Validation**: All token references must exist in design tokens
- **Accessibility Validation**: Required a11y fields must be present
- **ID Validation**: Component IDs must be unique and kebab-case
- **State Validation**: State definitions must be consistent

## Build System Integration

The component generation integrates with the Unhinged build system:

- **ComponentBuildModule**: Implements `BuildModule` interface
- **Dependency Tracking**: Automatic cache invalidation
- **Parallel Generation**: Multi-platform generation support
- **Error Reporting**: Comprehensive validation feedback

## Token Integration

Components reference design tokens by full path:

```yaml
# ✅ Correct token references
styling:
  default_state:
    background: "colors.action.primary"
    color: "colors.text.inverse"
    padding_vertical: "spacing.scale.sp_2"
    font_family: "typography.families.prose"

# ❌ Incorrect - hardcoded values
styling:
  default_state:
    background: "#0066CC"
    color: "white"
    padding: "8px"
```

## Platform Equality

The system treats all platforms as equal consumers:

- **No Primary Platform**: GTK4 is not favored over future platforms
- **Specification-First**: Implementation follows specification
- **Generator Interface**: Consistent interface for all platforms
- **Equal Validation**: Same validation rules for all platforms

## Examples

### Simple Button Component

See `libs/design_system/components/primitives/simple-button.yaml` for a complete, validated example.

### Generated GTK4 Widget

```python
# Generated from simple-button.yaml
class SimpleButton(Gtk.Widget):
    __gtype_name__ = 'SimpleButton'
    
    label = GObject.Property(type=str, default='')
    disabled = GObject.Property(type=bool, default=False)
    
    __gsignals__ = {
        'click': (GObject.SignalFlags.RUN_FIRST, None, (object,))
    }
```

## Development Workflow

1. **Define Component**: Create YAML specification with LlmDocs
2. **Validate**: Run `make validate-components`
3. **Generate**: Run `make components-gtk4`
4. **Test**: Import and use generated component
5. **Iterate**: Update specification and regenerate

## Adding New Platforms

1. Create generator in `build/generators/platform_name/`
2. Implement `ComponentGenerator` interface
3. Register in `component_generator.py`
4. Add build targets to Makefile
5. Update documentation

## Best Practices

- Use semantic design tokens exclusively
- Include comprehensive accessibility support
- Add detailed LlmDocs annotations
- Validate before committing
- Test generated components
- Follow platform-agnostic principles

## Troubleshooting

### Validation Errors

- Check token references against `libs/design_system/tokens/`
- Ensure component ID is kebab-case
- Verify required fields are present
- Check state definitions for consistency

### Generation Failures

- Validate component specifications first
- Check generator registration
- Verify design token loading
- Review error messages for specific issues
