# Document Renderer - Quick Reference Guide

## Overview

`DocumentRenderer` is a reusable GTK4 component for rendering documents with consistent visual styling and metadata display.

## Basic Usage

### Simple Document Rendering

```python
from control.gtk4_gui.components import DocumentRenderer

# Create a document
document = {
    "id": "doc-123",
    "name": "My Graph",
    "description": "A sample graph document",
    "document_type": "graph",
    "created_at": "2025-11-12",
    "updated_at": "2025-11-12",
    "properties": {
        "nodes": 5,
        "edges": 8,
        "version": "1.0"
    }
}

# Render with default styling
renderer = DocumentRenderer(
    document=document,
    document_type="graph"
)

widget = renderer.render()
container.append(widget)
```

## Advanced Usage

### Custom Renderer

```python
def render_graph_document(doc):
    """Custom renderer for graph documents"""
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    
    # Custom graph visualization
    title = Gtk.Label(label=f"Graph: {doc['name']}")
    title.add_css_class("title-2")
    box.append(title)
    
    # Custom graph preview
    preview = create_graph_preview(doc)
    box.append(preview)
    
    return box

# Use custom renderer
renderer = DocumentRenderer(
    document=document,
    document_type="graph",
    custom_renderer=render_graph_document
)

widget = renderer.render()
```

### Updating Documents

```python
# Create renderer
renderer = DocumentRenderer(document=old_doc, document_type="graph")
widget = renderer.get_widget()

# Later, update the document
new_doc = {"id": "doc-123", "name": "Updated Graph", ...}
renderer.update_document(new_doc)
# Widget is automatically re-rendered
```

## Document Structure

Expected document dictionary format:

```python
{
    "id": str,                          # Unique document ID
    "name": str,                        # Document name
    "description": str,                 # Optional description
    "document_type": str,               # Type (graph, tool, user, etc.)
    "created_at": str,                  # Creation timestamp
    "updated_at": str,                  # Last update timestamp
    "properties": dict[str, Any],       # Custom properties
    # ... other fields as needed
}
```

## Rendering Layers

### Header Layer
- Document title
- Metadata: type, created date, updated date
- Description (if provided)

### Content Layer
- Document properties (key-value pairs)
- Hierarchical structure (if applicable)
- Custom content (via custom renderer)

### Footer Layer
- Document ID (selectable for copying)
- Additional metadata

## Styling

The renderer uses standard GTK4 CSS classes:

- `title-2` - Document title
- `title-3` - Section titles
- `dim-label` - Metadata and descriptions

## Integration Points

### In Registry Tab
```python
# Display list of documents
for doc in documents:
    renderer = DocumentRenderer(doc, "graph")
    list_box.append(renderer.render())
```

### In Editor Tab
```python
# Display selected document
renderer = DocumentRenderer(selected_doc, "graph")
editor_container.append(renderer.render())
```

### In Search Results
```python
# Display search results
for result in search_results:
    renderer = DocumentRenderer(result, result["type"])
    results_container.append(renderer.render())
```

## Custom Renderers by Type

### Graph Renderer
```python
def render_graph(doc):
    # Show graph preview, node count, edge count
    pass

renderer = DocumentRenderer(doc, "graph", custom_renderer=render_graph)
```

### Tool Renderer
```python
def render_tool(doc):
    # Show tool icon, parameters, usage
    pass

renderer = DocumentRenderer(doc, "tool", custom_renderer=render_tool)
```

### User Renderer
```python
def render_user(doc):
    # Show user avatar, role, permissions
    pass

renderer = DocumentRenderer(doc, "user", custom_renderer=render_user)
```

## API Reference

### Constructor
```python
DocumentRenderer(
    document: dict[str, Any],
    document_type: str = "document",
    custom_renderer: Optional[Callable] = None
)
```

### Methods

#### `render() -> Gtk.Widget`
Render the document and return the widget.

#### `get_widget() -> Gtk.Widget`
Get the rendered widget (renders if not already rendered).

#### `update_document(document: dict[str, Any]) -> Gtk.Widget`
Update the document and re-render.

#### `_render_default() -> Gtk.Widget`
Render with default layout (called by render() if no custom renderer).

#### `_render_header() -> Gtk.Widget`
Render header with title and metadata.

#### `_render_content() -> Gtk.Widget`
Render content area with properties.

#### `_render_footer() -> Gtk.Widget`
Render footer with document ID.

#### `_render_property(key: str, value: Any) -> Gtk.Widget`
Render a single property key-value pair.

## Best Practices

1. **Reuse Renderers**: Create renderer instances once and update them
2. **Custom Renderers**: Implement custom renderers for document-specific visualization
3. **Error Handling**: Handle missing properties gracefully (use defaults)
4. **Performance**: Cache rendered widgets when possible
5. **Consistency**: Use standard CSS classes for consistent styling

## Examples

See `/docs/DOCUMENT_WORKSPACE_REFINEMENT.md` for architecture overview.

See `/control/gtk4_gui/components/document_renderer.py` for implementation details.

