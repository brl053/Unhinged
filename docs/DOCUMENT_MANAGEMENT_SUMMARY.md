# Document Management Component Specifications - Summary

## Quick Reference

This is a summary of the YAML component specifications needed for comprehensive GUI management of Documents and individual Document instances.

## Component Inventory

### Primitives (Atomic UI Elements)

| Component | Purpose | Key Properties |
|-----------|---------|-----------------|
| **document-list-item** | Individual document entry in list | title, type, created_at, modified_at, is_selected |
| **document-search** | Search/filter documents | search_text, search_fields, debounce_ms |
| **document-card** | Compact document preview | document, show_thumbnail, is_selected |
| **form-field** | Individual form input | value, label, type, error_message, required |

### Containers (Layout & Grouping)

| Component | Purpose | Contains |
|-----------|---------|----------|
| **document-header** | Title, metadata, actions | title, metadata, action buttons |
| **document-properties** | Editable properties display | property fields, validation errors |
| **document-actions-toolbar** | Bulk actions for selected docs | delete, export, share buttons |
| **document-footer** | Status, timestamps, save/cancel | status, timestamps, action buttons |
| **form-actions** | Submit/cancel buttons | submit button, cancel button |

### Complex (Stateful & Composed)

| Component | Purpose | Composition |
|-----------|---------|-------------|
| **document-list** | Browse/manage all documents | search, toolbar, list items, pagination |
| **document-detail** | View/edit single document | header, properties, content, footer |
| **document-form** | Create/edit document | form fields, validation, actions |
| **document-content** | Document-type-specific content | Varies by document type |

## Key Design Principles

### 1. Platform-Agnostic Specifications
- All components defined in YAML
- No platform-specific code in specs
- Generators create GTK4, Alpine Native, React, Flutter implementations

### 2. Semantic Design Tokens
- Use semantic names: `action.primary`, not `blue_500`
- All colors, spacing, typography from design system
- Enables theme switching and consistency

### 3. State Management via Events
- Components emit events with rich payloads
- Parent components listen and react
- Loose coupling between components
- Enables reusability across contexts

### 4. Accessibility First
- Keyboard navigation built-in
- ARIA labels and roles specified
- Focus indicators required
- WCAG AA compliance minimum

### 5. Single Responsibility
- Each component has one clear purpose
- Composable into larger systems
- Easy to test and maintain
- Easy to replace or upgrade

## Component Relationships

```
document-list
├── document-search (filter documents)
├── document-actions-toolbar (bulk operations)
└── document-list-item (individual entries)

document-detail
├── document-header (title, metadata, actions)
├── document-properties (editable fields)
├── document-content (document-specific)
└── document-footer (status, save/cancel)

document-form
├── form-field (individual inputs)
└── form-actions (submit/cancel)

document-card
├── document-thumbnail (preview)
└── document-metadata (quick info)
```

## State Transitions

### document-list States
```
empty → loading → populated
                ↓
            searching
                ↓
            error (optional)
```

### document-detail States
```
viewing ↔ editing → saving → saved
                        ↓
                      error (optional)
```

### document-form States
```
empty → populated → validating → submitting → success
                        ↓
                      error (optional)
```

## Events & Payloads

### document-list Events
```
document_selected
  → document_id: string

documents_selected
  → document_ids: array

document_opened
  → document_id: string

sort_changed
  → sort_by: string
  → sort_order: string

filter_changed
  → filter_text: string
```

### document-detail Events
```
edit_started
  → (no payload)

edit_cancelled
  → (no payload)

document_saved
  → document_id: string
  → saved_at: timestamp

property_changed
  → property_name: string
  → old_value: any
  → new_value: any
```

### document-form Events
```
field_changed
  → field_name: string
  → value: any

validation_error
  → field_name: string
  → error_message: string

form_submitted
  → document_id: string (for edit mode)
  → form_data: object
```

## Design Tokens Used

### Colors
- `action.primary`: Primary actions (edit, save)
- `action.secondary`: Secondary actions (cancel)
- `feedback.error`: Destructive actions (delete)
- `feedback.success`: Success states
- `surface.default`: Default backgrounds
- `surface.elevated`: Hover/selected states
- `text.primary`: Main content
- `text.secondary`: Metadata/timestamps
- `border.subtle`: Separators

### Spacing
- `sp.2`: 8px (padding within items)
- `sp.3`: 12px (padding within containers)
- `sp.4`: 16px (margin between items)
- `sp.6`: 24px (margin between sections)

### Typography
- `type.body`: 16px (main content)
- `type.caption`: 12px (metadata)
- `type.heading`: 20px (section titles)

## Keyboard Interactions

### document-list
- ↑/↓: Navigate items
- Space: Toggle selection
- Enter: Open document
- Ctrl+A: Select all
- Delete: Delete selected

### document-detail
- Tab: Navigate sections
- Ctrl+S: Save (edit mode)
- Escape: Cancel (edit mode)

### document-form
- Tab: Navigate fields
- Enter: Submit (when valid)
- Escape: Cancel

## Implementation Roadmap

### Phase 1: Primitives
- [ ] document-list-item
- [ ] document-search
- [ ] document-card
- [ ] form-field

### Phase 2: Containers
- [ ] document-header
- [ ] document-properties
- [ ] document-actions-toolbar
- [ ] document-footer
- [ ] form-actions

### Phase 3: Complex
- [ ] document-list
- [ ] document-detail
- [ ] document-form
- [ ] document-content

### Phase 4: Integration
- [ ] Wire components together
- [ ] Implement state management
- [ ] Add persistence layer
- [ ] End-to-end testing

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
├── DOCUMENT_MANAGEMENT_COMPONENT_SPECS.md (overview)
├── DOCUMENT_MANAGEMENT_YAML_EXAMPLES.md (examples)
├── DOCUMENT_MANAGEMENT_ARCHITECTURE.md (relationships)
└── DOCUMENT_MANAGEMENT_SUMMARY.md (this file)
```

## Next Steps

1. **Review Specifications**: Validate component definitions
2. **Create YAML Files**: Implement specifications in design system
3. **Validate Against Schema**: Ensure compliance with _schema.yaml
4. **Generate GTK4**: Run generators to create implementations
5. **Implement Components**: Build GTK4 widgets
6. **Wire UI**: Connect components in views
7. **Test**: Unit tests, integration tests, E2E tests

## Key Insights

✅ **Reusable**: Components work across multiple document types
✅ **Composable**: Build complex UIs from simple primitives
✅ **Testable**: Each component tested independently
✅ **Accessible**: Keyboard and screen reader support built-in
✅ **Maintainable**: Clear separation of concerns
✅ **Scalable**: Easy to add new features or document types
✅ **Platform-Independent**: Same specs for all platforms

## Related Documentation

- `libs/design_system/README.md` - Design system overview
- `libs/design_system/components/_schema.yaml` - Component schema
- `docs/DESIGN_SYSTEM_PATTERN.md` - Two-tier architecture
- `docs/WORKSPACE_TABS_IMPLEMENTATION.md` - Example implementation

