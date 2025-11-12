# Document Management Architecture

## System Overview

The document management system is built from composable, reusable components following the design system's two-tier architecture. Each component is platform-agnostic (YAML specification) and can be generated for any platform (GTK4, Alpine Native, React, Flutter, etc.).

## Component Relationships

```
┌─────────────────────────────────────────────────────────────┐
│                    Document Management                      │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              document-list (complex)                 │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │ document-search (primitive)                    │  │  │
│  │  │ - Search text input                            │  │  │
│  │  │ - Emits: search_changed, search_submitted      │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │ document-actions-toolbar (container)           │  │  │
│  │  │ - Bulk actions (delete, export, share)         │  │  │
│  │  │ - Visible when items selected                  │  │  │
│  │  │ - Emits: action_clicked, action_completed      │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │ [document-list-item] (primitive) x N           │  │  │
│  │  │ - Title, type, timestamps, size               │  │  │
│  │  │ - Selection checkbox                           │  │  │
│  │  │ - Emits: clicked, double_clicked, selected     │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │ pagination-controls (primitive)                │  │  │
│  │  │ - Page navigation                              │  │  │
│  │  │ - Emits: page_changed                          │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │            document-detail (complex)                │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │ document-header (container)                    │  │  │
│  │  │ - Title (editable in edit mode)                │  │  │
│  │  │ - Metadata (created, modified, type)           │  │  │
│  │  │ - Action buttons (edit, delete, share)         │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │ document-properties (container)                │  │  │
│  │  │ - Key-value properties                         │  │  │
│  │  │ - Editable in edit mode                        │  │  │
│  │  │ - Validation errors displayed                  │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │ document-content (complex)                     │  │  │
│  │  │ - Document-type-specific content               │  │  │
│  │  │ - Graph, text, image, etc.                     │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │ document-footer (container)                    │  │  │
│  │  │ - Status, last saved, file size                │  │  │
│  │  │ - Save/Cancel buttons in edit mode             │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │             document-form (complex)                 │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │ [form-field] (primitive) x N                   │  │  │
│  │  │ - Input, select, textarea, etc.                │  │  │
│  │  │ - Validation errors displayed                  │  │  │
│  │  │ - Emits: field_changed, validation_error       │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │ form-actions (container)                       │  │  │
│  │  │ - Submit button (enabled when valid)           │  │  │
│  │  │ - Cancel button                                │  │  │
│  │  │ - Loading state during submission              │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │             document-card (container)               │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │ document-thumbnail (primitive)                 │  │  │
│  │  │ - Visual preview of document                   │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │ document-metadata (primitive)                  │  │  │
│  │  │ - Quick info (title, type, modified)           │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### Viewing Documents (List → Detail)

```
1. User opens Documents tab
   ↓
2. document-list loads all documents
   ↓
3. document-list-item components render for each document
   ↓
4. User clicks document-list-item
   ↓
5. document-list emits: document_opened event
   ↓
6. Parent view receives event, loads document
   ↓
7. document-detail displays full document
```

### Editing Document

```
1. User clicks "Edit" button in document-header
   ↓
2. document-detail state: is_editing = true
   ↓
3. document-properties fields become editable
   ↓
4. User modifies properties
   ↓
5. document-properties emits: property_changed events
   ↓
6. document-detail tracks: unsaved_changes = true
   ↓
7. User clicks "Save"
   ↓
8. document-detail validates all properties
   ↓
9. If valid: saves to backend, emits: document_saved
   ↓
10. If invalid: shows validation errors in document-properties
```

### Creating Document

```
1. User clicks "New Document" button
   ↓
2. document-form displays with empty fields
   ↓
3. User fills form fields
   ↓
4. form-field components emit: field_changed events
   ↓
5. form validates in real-time
   ↓
6. Submit button enabled when all required fields valid
   ↓
7. User clicks "Submit"
   ↓
8. form-actions shows loading state
   ↓
9. Backend creates document
   ↓
10. If success: emits: form_submitted, navigates to document-detail
    If error: shows error message, keeps form open
```

## State Management Pattern

Each component manages its own state via properties and emits events:

```
Component State:
  - Properties: Configuration and data
  - States: Visual/behavioral modes
  - Events: Notifications to parent

Parent Responsibility:
  - Listen to child events
  - Update child properties
  - Coordinate between siblings
  - Persist state to backend
```

### Example: document-list

```
Properties:
  - documents: [...]
  - selected_documents: [...]
  - sort_by: "modified"
  - filter_text: ""

States:
  - loading, empty, populated, searching, error

Events Emitted:
  - document_selected
  - documents_selected
  - document_opened
  - sort_changed
  - filter_changed

Parent Listens To:
  - document_selected → highlight item
  - document_opened → navigate to detail view
  - sort_changed → re-fetch with new sort
  - filter_changed → re-fetch with filter
```

## Accessibility Features

### Keyboard Navigation

**document-list**:
- Arrow Up/Down: Navigate between items
- Space: Toggle selection
- Enter: Open selected document
- Ctrl+A: Select all
- Delete: Delete selected

**document-detail**:
- Tab: Navigate between sections
- Ctrl+S: Save (in edit mode)
- Escape: Cancel edit (in edit mode)

**document-form**:
- Tab: Navigate between fields
- Enter: Submit (when valid)
- Escape: Cancel

### Screen Reader Support

- All components have proper ARIA labels
- Form fields have associated labels
- Error messages linked via aria-describedby
- List items have aria-selected state
- Buttons have aria-label for icon-only buttons

### Focus Management

- Focus indicators visible on all interactive elements
- Focus trapped in modals
- Focus restored after modal closes
- Logical tab order maintained

## Design Token Integration

All components use semantic design tokens:

```yaml
Colors:
  action.primary: Primary actions (edit, save)
  action.secondary: Secondary actions (cancel)
  feedback.error: Destructive actions (delete)
  feedback.success: Success states (saved)
  surface.default: Card backgrounds
  surface.elevated: Hover states
  text.primary: Main content
  text.secondary: Metadata

Spacing:
  sp.2: Padding within items (8px)
  sp.3: Padding within containers (12px)
  sp.4: Margin between items (16px)
  sp.6: Margin between sections (24px)

Typography:
  type.body: Main content (16px)
  type.caption: Metadata (12px)
  type.heading: Section titles (20px)
```

## Implementation Phases

### Phase 1: Primitives (Week 1)
- document-list-item
- document-search
- document-card

### Phase 2: Containers (Week 2)
- document-header
- document-properties
- document-actions-toolbar

### Phase 3: Complex (Week 3)
- document-list
- document-detail
- document-form

### Phase 4: Integration (Week 4)
- Wire components together
- Implement state management
- Add persistence layer
- Test end-to-end workflows

## Benefits of This Architecture

✅ **Reusability**: Components used across multiple views
✅ **Testability**: Each component tested independently
✅ **Maintainability**: Clear separation of concerns
✅ **Scalability**: Easy to add new document types
✅ **Accessibility**: Built-in from the start
✅ **Platform Independence**: Same specs for all platforms

