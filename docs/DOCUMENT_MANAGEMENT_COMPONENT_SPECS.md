# Document Management Component Specifications

## Overview

This document outlines the YAML component specifications needed to provide comprehensive GUI management of Documents and individual Document instances. These specifications follow the design system's two-tier architecture pattern.

## Component Hierarchy

```
Document Management System
├── document-list (complex)           # Browse/manage all documents
│   ├── document-list-item (primitive) # Individual list item
│   ├── document-search (primitive)    # Search/filter documents
│   └── document-actions-toolbar (container) # Bulk actions
│
├── document-detail (complex)         # View/edit single document
│   ├── document-header (container)    # Title, metadata, actions
│   ├── document-properties (container) # Editable properties
│   ├── document-content (complex)     # Document-type-specific content
│   └── document-footer (container)    # Status, timestamps
│
├── document-card (container)         # Compact document preview
│   ├── document-thumbnail (primitive) # Visual preview
│   └── document-metadata (primitive)  # Quick info display
│
├── form-input (primitive)            # Reusable input component
│   └── Supports: text, textarea, select, checkbox, hidden, voice
│
└── document-form (complex)           # Create/edit document
    ├── form-input (primitive)        # Individual form input
    ├── form-validation (system)      # Validation system
    └── form-actions (container)      # Submit/cancel buttons
```

## Detailed Specifications

### 1. document-list (COMPLEX)

**Purpose**: Browse, search, filter, and manage all documents of a given type

**Key Properties**:
- `documents`: array of document objects
- `selected_documents`: array of selected document IDs (multi-select)
- `sort_by`: enum (name, created, modified, type)
- `sort_order`: enum (ascending, descending)
- `filter_text`: string for search/filter
- `view_mode`: enum (list, grid, compact)
- `items_per_page`: number (pagination)
- `current_page`: number

**States**:
- `default`: Empty or populated list
- `loading`: Fetching documents
- `empty`: No documents match criteria
- `selected`: One or more items selected
- `searching`: Active search/filter
- `error`: Failed to load documents

**Events**:
- `document_selected`: Single document selected
- `documents_selected`: Multiple documents selected
- `document_opened`: Document double-clicked or opened
- `document_deleted`: Document(s) deleted
- `sort_changed`: Sort order changed
- `filter_changed`: Search/filter applied
- `page_changed`: Pagination changed

**Composition**: Can contain `document-list-item`, `document-search`, `document-actions-toolbar`

---

### 2. document-list-item (PRIMITIVE)

**Purpose**: Individual document entry in list view

**Key Properties**:
- `document_id`: string (unique identifier)
- `title`: string (document name)
- `description`: string (optional summary)
- `type`: string (document type)
- `created_at`: timestamp
- `modified_at`: timestamp
- `size`: number (bytes)
- `is_selected`: boolean
- `is_highlighted`: boolean

**States**:
- `default`: Normal appearance
- `hover`: Mouse over item
- `selected`: Item is selected
- `focused`: Keyboard focus
- `disabled`: Item cannot be interacted with

**Events**:
- `click`: Item clicked
- `double_click`: Item double-clicked (open)
- `context_menu`: Right-click menu requested
- `selection_changed`: Selection state changed

**Styling**: Uses semantic tokens for hover/selected states

---

### 3. document-detail (COMPLEX)

**Purpose**: View and edit a single document with full metadata

**Key Properties**:
- `document`: object (full document data)
- `document_id`: string
- `is_editing`: boolean
- `is_readonly`: boolean
- `unsaved_changes`: boolean
- `last_saved_at`: timestamp

**States**:
- `viewing`: Read-only view mode
- `editing`: Edit mode active
- `saving`: Saving changes
- `saved`: Changes saved successfully
- `error`: Error occurred
- `loading`: Loading document

**Events**:
- `edit_started`: User entered edit mode
- `edit_cancelled`: User cancelled editing
- `document_saved`: Changes saved
- `document_deleted`: Document deleted
- `property_changed`: Document property modified
- `save_error`: Error saving document

**Composition**: Contains `document-header`, `document-properties`, `document-content`, `document-footer`

---

### 4. document-header (CONTAINER)

**Purpose**: Display document title, metadata, and action buttons

**Key Properties**:
- `title`: string
- `document_type`: string
- `created_by`: string (optional)
- `created_at`: timestamp
- `modified_at`: timestamp
- `show_actions`: boolean

**States**:
- `viewing`: Read-only header
- `editing`: Editable title
- `loading`: Metadata loading

**Events**:
- `title_changed`: Title edited
- `action_clicked`: Action button clicked (edit, delete, share, etc.)

---

### 5. document-properties (CONTAINER)

**Purpose**: Display and edit document metadata properties

**Key Properties**:
- `properties`: array of property objects
  - Each property has: name, value, type, editable, required
- `is_editing`: boolean
- `validation_errors`: object (property_name -> error_message)

**States**:
- `viewing`: Read-only display
- `editing`: Editable fields
- `validating`: Validation in progress
- `error`: Validation errors present

**Events**:
- `property_changed`: Property value modified
- `validation_error`: Validation failed
- `validation_success`: All properties valid

---

### 6. document-card (CONTAINER)

**Purpose**: Compact preview card for document (used in grids, dashboards)

**Key Properties**:
- `document`: object
- `show_thumbnail`: boolean
- `show_metadata`: boolean
- `is_selected`: boolean

**States**:
- `default`: Normal card
- `hover`: Mouse over
- `selected`: Card selected
- `loading`: Content loading

**Events**:
- `card_clicked`: Card clicked
- `card_selected`: Card selected (checkbox)
- `action_clicked`: Action button clicked

---

### 7. document-form (COMPLEX)

**Purpose**: Create new or edit existing document with validation

**Key Properties**:
- `mode`: enum (create, edit)
- `document`: object (for edit mode)
- `fields`: array of form field definitions
- `is_submitting`: boolean
- `submit_error`: string (optional)

**States**:
- `empty`: New document form
- `populated`: Form with data
- `validating`: Validation in progress
- `submitting`: Submitting form
- `success`: Form submitted successfully
- `error`: Submission error

**Events**:
- `field_changed`: Form field value changed
- `validation_error`: Field validation failed
- `form_submitted`: Form submitted
- `form_cancelled`: Form cancelled
- `submit_error`: Error submitting form

**Composition**: Contains `form-field` components, `form-validation` system, `form-actions`

---

### 8. form-input (PRIMITIVE)

**Purpose**: Reusable input component for all form types (text, textarea, select, checkbox, hidden, voice)

**Key Properties**:
- `type`: enum (text, textarea, select, checkbox, hidden, voice)
- `name`: string (field identifier)
- `label`: string (human-readable label)
- `value`: string or boolean
- `required`: boolean
- `placeholder`: string
- `help_text`: string
- `error_message`: string
- `disabled`: boolean
- `readonly`: boolean
- `min_length`: number (text/textarea/voice)
- `max_length`: number (text/textarea/voice)
- `rows`: number (textarea only)
- `options`: array of {label, value} (select only)
- `enable_voice`: boolean (text/textarea only, enables voice input button)
- `voice_language`: string (voice only, e.g., "en-US")
- `voice_mode`: enum (append, replace) - how transcription is added to existing text
- `show_visualizer`: boolean (voice type only, default: true) - show waveform visualizer during recording
- `visualizer_width`: number (voice type only, default: 250) - width of waveform display in pixels

**States**:
- `default`: Normal state
- `focused`: Input has focus
- `error`: Validation error
- `disabled`: Input disabled
- `readonly`: Input read-only
- `recording`: Voice recording in progress (voice type)
- `processing`: Voice transcription in progress (voice type)

**Events**:
- `value_changed`: Value changed
- `focus_in`: Input gained focus
- `focus_out`: Input lost focus
- `validation_error`: Validation failed
- `recording_started`: Voice recording started (voice type)
- `recording_stopped`: Voice recording stopped (voice type)
- `transcription_started`: Transcription processing started (voice type)
- `transcription_completed`: Transcription completed (voice type)
- `transcription_error`: Transcription failed (voice type)

**Methods**:
- `get_value()`: Return current value
- `set_value(value)`: Set value
- `validate()`: Validate against constraints
- `set_error(message)`: Set error state
- `clear_error()`: Clear error state
- `start_recording()`: Start voice recording (voice type)
- `stop_recording()`: Stop voice recording (voice type)
- `append_transcript(text)`: Append transcribed text to existing value (voice type)
- `set_transcript(text)`: Replace value with transcribed text (voice type)
- `get_recording_time()`: Get elapsed recording time in seconds (voice type)

**Composition** (voice type):
- Text input field (for displaying transcribed text)
- Waveform visualizer (horizontal, real-time amplitude display)
- Recording timer (MM:SS format)
- Voice button (microphone icon, toggles recording)

---

### 9. document-search (PRIMITIVE)

**Purpose**: Search and filter documents

**Key Properties**:
- `search_text`: string
- `search_fields`: array (which fields to search)
- `placeholder`: string
- `debounce_ms`: number (search delay)

**States**:
- `default`: Empty search
- `searching`: Search in progress
- `results`: Results displayed
- `no_results`: No matches found

**Events**:
- `search_changed`: Search text changed
- `search_submitted`: User pressed Enter
- `search_cleared`: Search cleared

---

### 10. document-actions-toolbar (CONTAINER)

**Purpose**: Toolbar with bulk actions for selected documents

**Key Properties**:
- `selected_count`: number
- `available_actions`: array (delete, export, share, etc.)
- `is_loading`: boolean

**States**:
- `empty`: No documents selected
- `single_selected`: One document selected
- `multiple_selected`: Multiple documents selected
- `loading`: Action in progress

**Events**:
- `action_clicked`: Action button clicked
- `action_completed`: Action completed
- `action_error`: Action failed

---

## Design Token Usage

All components use semantic design tokens:

**Colors**:
- `action.primary`: Primary action buttons
- `feedback.error`: Delete/destructive actions
- `feedback.success`: Save/success states
- `surface.default`: Card backgrounds
- `text.primary`: Main text
- `text.secondary`: Metadata/timestamps
- `border.subtle`: List item separators

**Spacing**:
- `sp.2`: Padding within items
- `sp.3`: Padding within containers
- `sp.4`: Margin between items
- `sp.6`: Margin between sections

**Typography**:
- `type.body`: Main content
- `type.caption`: Metadata/timestamps
- `type.heading`: Section titles

---

## Accessibility Requirements

All components must support:
- **Keyboard Navigation**: Tab, Shift+Tab, Arrow keys, Enter, Escape
- **Screen Readers**: Proper ARIA labels and roles
- **Focus Indicators**: Visible focus states
- **Contrast**: WCAG AA minimum (4.5:1 for text)

---

## Implementation Strategy

### Phase 1: Primitives
1. `document-list-item`
2. `document-search`
3. `document-card`

### Phase 2: Containers
1. `document-header`
2. `document-properties`
3. `document-actions-toolbar`

### Phase 3: Complex Components
1. `document-list`
2. `document-detail`
3. `document-form`

### Phase 4: Integration
- Wire components together
- Implement state management
- Add persistence layer

---

## Voice Input Example

### Dedicated Voice Input (type: voice)
```yaml
form-input:
  type: voice
  name: message
  label: "Voice Message"
  voice_language: "en-US"
  voice_mode: replace
  show_visualizer: true
  visualizer_width: 250
  placeholder: "Click microphone to record"
```

**Layout**:
```
┌─────────────────────────────────────────────┐
│ Voice Message                               │
├─────────────────────────────────────────────┤
│ 00:15  ▁▂▃▄▅▆▇█▆▅▄▃▂▁  [🎤]               │
│                                             │
│ [Transcribed text appears here]             │
└─────────────────────────────────────────────┘
```

### Voice-Enabled Text/Textarea
```yaml
document-form:
  fields:
    - type: form-input
      name: title
      label: "Document Title"
      type: text
      enable_voice: true
      voice_mode: replace
      placeholder: "Speak or type title"

    - type: form-input
      name: description
      label: "Description"
      type: textarea
      enable_voice: true
      voice_mode: append
      show_visualizer: true
      visualizer_width: 300
      placeholder: "Speak or type description"
      rows: 4
```

**Voice Flow**:
1. User clicks voice button on input
2. Input emits `recording_started` event
3. Waveform visualizer shows real-time amplitude
4. Recording timer displays elapsed time (MM:SS)
5. User stops recording (manual or auto-detect silence)
6. Input emits `recording_stopped` event
7. TranscriptionService transcribes audio via gRPC
8. Input emits `transcription_started` event
9. On success: `transcription_completed` + `value_changed` events
10. On error: `transcription_error` event
11. Transcript appended (append mode) or replaces (replace mode) existing text
12. Waveform visualizer hides, timer resets

---

## Notes

- All specifications are **platform-agnostic** (YAML)
- Generators will create GTK4, Alpine Native, React implementations
- Components follow **single responsibility principle**
- State management via callbacks (loose coupling)
- Full accessibility compliance built-in
- Voice input integrates with existing AudioHandler and TranscriptionService

