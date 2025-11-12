# Document Management YAML Examples

This document shows example YAML specifications for document management components.

## 1. document-list-item.yaml

```yaml
# @llm-type component.spec
# @llm-does Individual document entry in list view with selection and actions
# @llm-key Atomic unit of document list - represents single document

component:
  id: "document-list-item"
  name: "Document List Item"
  category: "primitive"
  
  description: |
    Individual document entry in a list view. Displays document metadata
    (title, type, timestamps, size) with selection checkbox and context menu.
    Supports hover, selection, and keyboard focus states.

  interface:
    properties:
      document_id:
        type: "string"
        required: true
        description: "Unique document identifier"
      
      title:
        type: "string"
        required: true
        description: "Document display name"
      
      document_type:
        type: "string"
        required: true
        description: "Type of document (e.g., 'graph', 'text', 'image')"
      
      created_at:
        type: "string"
        required: true
        description: "ISO 8601 timestamp of creation"
      
      modified_at:
        type: "string"
        required: true
        description: "ISO 8601 timestamp of last modification"
      
      size_bytes:
        type: "number"
        required: false
        description: "Document size in bytes"
      
      is_selected:
        type: "boolean"
        default: false
        description: "Whether item is currently selected"
      
      is_highlighted:
        type: "boolean"
        default: false
        description: "Whether item is highlighted (keyboard focus)"

    states:
      default:
        description: "Normal appearance"
        visual_tokens: ["surface.default", "text.primary", "border.subtle"]
      
      hover:
        description: "Mouse over item"
        visual_tokens: ["surface.elevated", "interactive.hover"]
        triggers: ["mouse_enter"]
      
      selected:
        description: "Item is selected"
        visual_tokens: ["surface.elevated", "action.primary", "border.medium"]
        triggers: ["selection_changed"]
      
      focused:
        description: "Keyboard focus"
        visual_tokens: ["interactive.focus"]
        triggers: ["keyboard_focus"]

    events:
      clicked:
        description: "Item clicked"
        payload:
          document_id: "string"
          shift_key: "boolean"
          ctrl_key: "boolean"
      
      double_clicked:
        description: "Item double-clicked (open)"
        payload:
          document_id: "string"
      
      context_menu_requested:
        description: "Right-click context menu requested"
        payload:
          document_id: "string"
          x: "number"
          y: "number"
      
      selection_changed:
        description: "Selection state changed"
        payload:
          document_id: "string"
          is_selected: "boolean"

  styling:
    default_state:
      background: "surface.default"
      padding_vertical: "sp.2"
      padding_horizontal: "sp.3"
      border_bottom: ["border.thin", "border.subtle"]
      min_height: "48px"
      display: "flex"
      align_items: "center"
      gap: "sp.3"
    
    state_overrides:
      hover:
        background: "surface.elevated"
      
      selected:
        background: "action.primary"
        background_opacity: 0.1
        border_left: ["border.thick", "action.primary"]
      
      focused:
        outline: ["border.medium", "interactive.focus"]
        outline_offset: "-2px"

  composition:
    is_leaf: false
    can_contain: ["primitive"]
    layout_type: "box"
    
    child_elements:
      - id: "checkbox"
        type: "primitive"
        description: "Selection checkbox"
      
      - id: "title"
        type: "text"
        description: "Document title"
      
      - id: "metadata"
        type: "text"
        description: "Type, created, modified timestamps"
      
      - id: "size"
        type: "text"
        description: "Document size"

  accessibility:
    keyboard_support: true
    screen_reader_label: "required"
    focus_indicator: "required"
    contrast_requirement: "WCAG_AA"
    
    keyboard_interactions:
      - key: "Space"
        action: "toggle_selection"
      - key: "Enter"
        action: "open_document"
      - key: "Delete"
        action: "delete_document"
      - key: "Shift+Space"
        action: "extend_selection"
    
    aria_attributes:
      - "role: listitem"
      - "aria-selected: true/false"
      - "aria-label: document title and type"

metadata:
  version: "1.0.0"
  implementation_status:
    gtk4: "pending"
    alpine_native: "pending"
```

---

## 2. document-list.yaml (excerpt)

```yaml
component:
  id: "document-list"
  name: "Document List"
  category: "complex"
  
  description: |
    Browse, search, filter, and manage all documents. Supports multiple
    view modes (list, grid, compact), sorting, filtering, pagination,
    and multi-select operations.

  interface:
    properties:
      documents:
        type: "array"
        required: true
        description: "Array of document objects"
      
      selected_documents:
        type: "array"
        default: []
        description: "Array of selected document IDs"
      
      sort_by:
        type: "enum"
        values: ["name", "created", "modified", "type", "size"]
        default: "modified"
        description: "Sort field"
      
      sort_order:
        type: "enum"
        values: ["ascending", "descending"]
        default: "descending"
        description: "Sort direction"
      
      filter_text:
        type: "string"
        default: ""
        description: "Search/filter text"
      
      view_mode:
        type: "enum"
        values: ["list", "grid", "compact"]
        default: "list"
        description: "Display mode"
      
      items_per_page:
        type: "number"
        default: 20
        min: 5
        max: 100
        description: "Pagination size"
      
      current_page:
        type: "number"
        default: 1
        description: "Current page number"

    states:
      empty:
        description: "No documents"
        visual_tokens: ["surface.default"]
      
      loading:
        description: "Fetching documents"
        visual_tokens: ["surface.default"]
      
      populated:
        description: "Documents loaded"
        visual_tokens: ["surface.default"]
      
      searching:
        description: "Active search/filter"
        visual_tokens: ["surface.elevated"]
      
      error:
        description: "Failed to load"
        visual_tokens: ["feedback.error"]

    events:
      document_selected:
        description: "Single document selected"
        payload:
          document_id: "string"
      
      documents_selected:
        description: "Multiple documents selected"
        payload:
          document_ids: "array"
      
      document_opened:
        description: "Document opened"
        payload:
          document_id: "string"
      
      sort_changed:
        description: "Sort order changed"
        payload:
          sort_by: "string"
          sort_order: "string"
      
      filter_changed:
        description: "Filter applied"
        payload:
          filter_text: "string"

  composition:
    is_leaf: false
    can_contain: ["document-search", "document-list-item", "document-actions-toolbar"]
    layout_type: "box"
    
    layout_structure:
      - section: "toolbar"
        contains: ["document-search", "document-actions-toolbar"]
      
      - section: "content"
        contains: ["document-list-item"]
      
      - section: "pagination"
        contains: ["pagination-controls"]
```

---

## 3. document-detail.yaml (excerpt)

```yaml
component:
  id: "document-detail"
  name: "Document Detail"
  category: "complex"
  
  description: |
    View and edit a single document with full metadata, properties,
    and content. Supports read-only and edit modes with unsaved
    changes tracking.

  interface:
    properties:
      document:
        type: "object"
        required: true
        description: "Full document data"
      
      document_id:
        type: "string"
        required: true
        description: "Document identifier"
      
      is_editing:
        type: "boolean"
        default: false
        description: "Edit mode active"
      
      is_readonly:
        type: "boolean"
        default: false
        description: "Read-only mode"
      
      unsaved_changes:
        type: "boolean"
        default: false
        description: "Has unsaved changes"

    states:
      viewing:
        description: "Read-only view"
        visual_tokens: ["surface.default"]
      
      editing:
        description: "Edit mode"
        visual_tokens: ["surface.elevated"]
      
      saving:
        description: "Saving changes"
        visual_tokens: ["surface.elevated"]
      
      saved:
        description: "Changes saved"
        visual_tokens: ["feedback.success"]
      
      error:
        description: "Error occurred"
        visual_tokens: ["feedback.error"]

    events:
      edit_started:
        description: "User entered edit mode"
        payload: {}
      
      edit_cancelled:
        description: "User cancelled editing"
        payload: {}
      
      document_saved:
        description: "Changes saved"
        payload:
          document_id: "string"
          saved_at: "string"
      
      property_changed:
        description: "Property modified"
        payload:
          property_name: "string"
          old_value: "any"
          new_value: "any"

  composition:
    is_leaf: false
    can_contain: ["document-header", "document-properties", "document-content", "document-footer"]
    layout_type: "box"
```

---

## Key Patterns

### 1. Semantic Naming
- Use **semantic names** not value-based names
- `action.primary` not `blue_500`
- `feedback.error` not `red_600`

### 2. State Management
- Define all possible states
- Specify visual tokens for each state
- Document state transitions

### 3. Events
- Emit events with rich payloads
- Include context (IDs, values, flags)
- Enable parent components to react

### 4. Composition
- Specify what children can contain
- Define layout structure
- Enable recursive composition

### 5. Accessibility
- Keyboard support required
- ARIA attributes specified
- Focus indicators defined

