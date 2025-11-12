# Workspace Tabs Implementation

## Overview

Workspace tabs provide a non-closeable, non-organizable tab interface for displaying multiple persistent views of the same document. Each tab (Registry, Editor, Metrics) represents a unique visual representation with its own feature set.

## Architecture

### Design System Integration

The workspace tabs component is defined in the design system as a platform-agnostic specification:

**File**: `libs/design_system/components/containers/tabs.yaml`

This YAML specification defines:
- **Properties**: tabs array, selected_tab, closeable (always false), organizable (always false)
- **States**: default, tab_selected, tab_unselected
- **Events**: tab_changed with payload (previous_tab_id, new_tab_id, timestamp)
- **Styling**: Uses semantic design tokens exclusively
- **Accessibility**: Full WCAG AA compliance with keyboard navigation

### Implementation Pattern

The design system follows a **two-tier architecture**:

1. **Tier 1 (Abstraction)**: Platform-agnostic YAML specifications in `libs/design_system/components/`
2. **Tier 2 (Implementation)**: Platform-specific implementations generated from specifications

This ensures consistency across all platforms (GTK4, Alpine Native, etc.) while allowing platform-specific optimizations.

## GTK4 Implementation

### File Structure

```
control/gtk4_gui/components/
├── document_workspace_tabs.py    # Generic workspace tabs component
└── graph_workspace_tabs.py       # Graph-specific workspace tabs
```

### Key Implementation Details

**Non-Closeable Tabs**:
```python
# Prevent tab closing by handling the close-page signal
self.notebook.connect('close-page', self._on_close_page_requested)

def _on_close_page_requested(self, notebook, page):
    """Prevent tab closing - workspace tabs are non-closeable"""
    return True  # Return True to prevent the close
```

**Inner Padding for Visual Taste**:
```python
self.tab_bar = Adw.TabBar()
self.tab_bar.set_margin_top(8)
self.tab_bar.set_margin_bottom(8)
self.tab_bar.set_margin_start(8)
self.tab_bar.set_margin_end(8)
```

**Tab Structure**:
- Uses `Adw.TabView` for the tab container
- Uses `Adw.TabBar` for the tab bar display
- Each tab is a `TabPage` with title and icon
- Tabs are arranged horizontally in a top bar

### API

```python
class DocumentWorkspaceTabs:
    def __init__(self, document_type: str, doc_store_client=None)
    
    # Callbacks for content
    on_registry_content: Callable[[], Gtk.Widget]
    on_editor_content: Callable[[], Gtk.Widget]
    on_metrics_content: Callable[[], Gtk.Widget]
    on_workspace_changed: Callable[[str], None]
    
    # Methods
    get_widget() -> Gtk.Widget
    set_registry_content(callback)
    set_editor_content(callback)
    set_metrics_content(callback)
```

## Usage Example

```python
# Create workspace tabs
tabs = DocumentWorkspaceTabs(document_type="graph")

# Set content callbacks
tabs.set_registry_content(lambda: create_registry_widget())
tabs.set_editor_content(lambda: create_editor_widget())
tabs.set_metrics_content(lambda: create_metrics_widget())

# Handle tab changes
tabs.on_workspace_changed = lambda tab_name: print(f"Switched to {tab_name}")

# Add to UI
main_box.append(tabs.get_widget())
```

## Design Principles

### Surgical Precision

The implementation uses exactly what's needed:
- Simple top bar with N-length array of tabs
- Non-closeable (no X buttons)
- Non-organizable (fixed order)
- Inner padding (8px margins) for visual taste
- Crude, straightforward interface

### Reusability

The component is document-type agnostic:
- Works with any document type (graphs, tools, users, etc.)
- Content provided via callbacks
- No hardcoded assumptions about document structure

### Accessibility

Full WCAG AA compliance:
- Keyboard navigation (arrow keys, Home, End)
- Screen reader support (role=tablist, role=tab)
- Focus indicators
- Proper ARIA attributes

## Testing

### Compilation
```bash
python3 -m py_compile control/gtk4_gui/components/document_workspace_tabs.py
```

### Runtime
```bash
./unhinged
# Navigate to Documents tab in sidebar
# Verify tabs appear (Registry, Editor, Metrics)
# Verify tabs are non-closeable
# Verify tab switching works
```

## Future Enhancements

### Design System Generation

Once the component generator is fully implemented, GTK4 components can be automatically generated from the YAML specification:

```bash
make components-gtk4
# Generates: generated/design_system/gtk4/workspace-tabs.py
```

### Platform Support

The same YAML specification can be used to generate implementations for:
- Alpine Native C graphics
- React/TypeScript
- Flutter/Dart
- Other platforms

## References

- Design System: `libs/design_system/README.md`
- Component Specification: `libs/design_system/components/containers/tabs.yaml`
- GTK4 Documentation: https://docs.gtk.org/gtk4/
- Libadwaita Documentation: https://gnome.pages.gitlab.gnome.org/libadwaita/

