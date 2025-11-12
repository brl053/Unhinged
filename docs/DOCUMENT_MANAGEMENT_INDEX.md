# Document Management Component Specifications - Complete Index

## Overview

This is a comprehensive guide to creating YAML component specifications for GUI management of Documents and individual Document instances using the Unhinged design system's two-tier architecture.

**Key Principle**: All specifications are platform-agnostic (YAML). Generators create platform-specific implementations (GTK4, Alpine Native, React, Flutter, etc.).

## Documentation Structure

### 1. **DOCUMENT_MANAGEMENT_SUMMARY.md** ⭐ START HERE
   - Quick reference of all components
   - Component inventory table
   - State transitions
   - Events and payloads
   - Design tokens used
   - Implementation roadmap

### 2. **DOCUMENT_MANAGEMENT_COMPONENT_SPECS.md**
   - Detailed specifications for each component
   - Component hierarchy
   - Properties, states, and events for each
   - Design token usage
   - Accessibility requirements
   - Implementation strategy (4 phases)

### 3. **DOCUMENT_MANAGEMENT_YAML_EXAMPLES.md**
   - Actual YAML code examples
   - `document-list-item.yaml` (complete example)
   - `document-list.yaml` (excerpt)
   - `document-detail.yaml` (excerpt)
   - Key patterns explained

### 4. **DOCUMENT_MANAGEMENT_ARCHITECTURE.md**
   - Component relationships and hierarchy
   - Data flow diagrams
   - State management pattern
   - Accessibility features
   - Design token integration
   - Implementation phases

### 5. **DOCUMENT_MANAGEMENT_VISUAL_GUIDE.md**
   - Component hierarchy tree
   - Visual layout examples
   - State diagrams
   - Event flow diagrams
   - Keyboard navigation
   - Focus indicators
   - Component sizing

### 6. **DOCUMENT_MANAGEMENT_INDEX.md** (this file)
   - Navigation guide
   - Quick lookup table
   - Related documentation

## Component Quick Lookup

### By Category

**Primitives** (Atomic UI Elements)
- `document-list-item` - Individual document entry
- `document-search` - Search/filter input
- `document-card` - Compact preview card
- `form-field` - Individual form input

**Containers** (Layout & Grouping)
- `document-header` - Title, metadata, actions
- `document-properties` - Editable properties
- `document-actions-toolbar` - Bulk actions
- `document-footer` - Status, timestamps
- `form-actions` - Submit/cancel buttons

**Complex** (Stateful & Composed)
- `document-list` - Browse all documents
- `document-detail` - View/edit single document
- `document-form` - Create/edit document
- `document-content` - Document-specific content

### By Use Case

**Viewing Documents**
- `document-list` → `document-list-item` → `document-detail`

**Searching Documents**
- `document-search` (filters `document-list`)

**Selecting Multiple Documents**
- `document-list-item` (with checkbox) → `document-actions-toolbar`

**Editing Document**
- `document-detail` → `document-properties` → Save/Cancel

**Creating Document**
- `document-form` → `form-field` → `form-actions`

**Previewing Document**
- `document-card` (in grid view)

## Key Concepts

### Two-Tier Architecture

```
Tier 1: Platform-Agnostic (YAML)
├─ Component specifications
├─ Design tokens
├─ Accessibility requirements
└─ Event definitions

        ↓ (Generators)

Tier 2: Platform-Specific (Generated Code)
├─ GTK4 (Python)
├─ Alpine Native (C)
├─ React (TypeScript)
└─ Flutter (Dart)
```

### State Management Pattern

```
Component Properties
    ↓
Component States (visual/behavioral)
    ↓
Component Events (emitted to parent)
    ↓
Parent Listens & Reacts
    ↓
Parent Updates Child Properties
```

### Design Token System

```
Semantic Names (YAML)
├─ action.primary
├─ feedback.error
├─ surface.default
├─ text.primary
└─ sp.2, sp.3, sp.4, sp.6

        ↓ (Generators)

Platform Values (Generated)
├─ GTK4: CSS variables
├─ React: theme.colors.action.primary
├─ Alpine: ACTION_PRIMARY_COLOR
└─ Flutter: Colors.actionPrimary
```

## Implementation Checklist

### Phase 1: Primitives (Week 1)
- [ ] Create `document-list-item.yaml`
- [ ] Create `document-search.yaml`
- [ ] Create `document-card.yaml`
- [ ] Create `form-field.yaml`
- [ ] Validate against `_schema.yaml`
- [ ] Generate GTK4 implementations
- [ ] Test each component

### Phase 2: Containers (Week 2)
- [ ] Create `document-header.yaml`
- [ ] Create `document-properties.yaml`
- [ ] Create `document-actions-toolbar.yaml`
- [ ] Create `document-footer.yaml`
- [ ] Create `form-actions.yaml`
- [ ] Validate against `_schema.yaml`
- [ ] Generate GTK4 implementations
- [ ] Test each component

### Phase 3: Complex (Week 3)
- [ ] Create `document-list.yaml`
- [ ] Create `document-detail.yaml`
- [ ] Create `document-form.yaml`
- [ ] Create `document-content.yaml`
- [ ] Validate against `_schema.yaml`
- [ ] Generate GTK4 implementations
- [ ] Test each component

### Phase 4: Integration (Week 4)
- [ ] Wire components in views
- [ ] Implement state management
- [ ] Add persistence layer
- [ ] End-to-end testing
- [ ] Accessibility testing
- [ ] Performance testing

## File Locations

### Specifications (to be created)
```
libs/design_system/components/
├── primitives/
│   ├── document-list-item.yaml
│   ├── document-search.yaml
│   ├── document-card.yaml
│   └── form-field.yaml
├── containers/
│   ├── document-header.yaml
│   ├── document-properties.yaml
│   ├── document-actions-toolbar.yaml
│   ├── document-footer.yaml
│   └── form-actions.yaml
└── complex/
    ├── document-list.yaml
    ├── document-detail.yaml
    ├── document-form.yaml
    └── document-content.yaml
```

### Documentation (created)
```
docs/
├── DOCUMENT_MANAGEMENT_INDEX.md (this file)
├── DOCUMENT_MANAGEMENT_SUMMARY.md (quick reference)
├── DOCUMENT_MANAGEMENT_COMPONENT_SPECS.md (detailed specs)
├── DOCUMENT_MANAGEMENT_YAML_EXAMPLES.md (code examples)
├── DOCUMENT_MANAGEMENT_ARCHITECTURE.md (relationships)
└── DOCUMENT_MANAGEMENT_VISUAL_GUIDE.md (visual layouts)
```

## Related Documentation

### Design System
- `libs/design_system/README.md` - Design system overview
- `libs/design_system/components/_schema.yaml` - Component schema
- `docs/DESIGN_SYSTEM_PATTERN.md` - Two-tier architecture

### Existing Components
- `libs/design_system/components/primitives/button.yaml`
- `libs/design_system/components/primitives/input.yaml`
- `libs/design_system/components/graph/graph-canvas.yaml`

### Implementation Examples
- `docs/WORKSPACE_TABS_IMPLEMENTATION.md` - Workspace tabs example
- `control/gtk4_gui/components/document_workspace_tabs.py` - GTK4 implementation

## Key Design Principles

✅ **Platform-Agnostic**: Specifications work for all platforms
✅ **Semantic Tokens**: Use meaningful names, not values
✅ **Event-Driven**: Components communicate via events
✅ **Accessible**: Keyboard and screen reader support built-in
✅ **Composable**: Build complex UIs from simple primitives
✅ **Testable**: Each component tested independently
✅ **Reusable**: Components work across multiple contexts
✅ **Maintainable**: Clear separation of concerns

## Quick Start

1. **Read**: Start with `DOCUMENT_MANAGEMENT_SUMMARY.md`
2. **Understand**: Review `DOCUMENT_MANAGEMENT_COMPONENT_SPECS.md`
3. **Visualize**: Check `DOCUMENT_MANAGEMENT_VISUAL_GUIDE.md`
4. **Learn**: Study `DOCUMENT_MANAGEMENT_YAML_EXAMPLES.md`
5. **Implement**: Follow `DOCUMENT_MANAGEMENT_ARCHITECTURE.md`

## Questions & Answers

**Q: Why YAML specifications?**
A: Platform-agnostic definitions enable automatic generation for GTK4, React, Flutter, etc.

**Q: How do components communicate?**
A: Via events with rich payloads. Parent components listen and react.

**Q: What about state management?**
A: Each component manages its own state. Parent coordinates between siblings.

**Q: How are design tokens used?**
A: All styling references semantic tokens (e.g., `action.primary`). Generators resolve to platform values.

**Q: What about accessibility?**
A: Built into specifications. Keyboard navigation, ARIA labels, focus indicators all defined.

**Q: Can I use these for other platforms?**
A: Yes! Same YAML specs generate GTK4, React, Flutter, Alpine Native, etc.

## Next Steps

1. Review the specifications in this documentation
2. Create YAML files in `libs/design_system/components/`
3. Validate against `_schema.yaml`
4. Generate GTK4 implementations
5. Implement components in `control/gtk4_gui/`
6. Wire components in views
7. Test end-to-end workflows

---

**Status**: ✅ Specifications documented (no implementation yet)
**Last Updated**: 2025-01-27
**Version**: 1.0.0

