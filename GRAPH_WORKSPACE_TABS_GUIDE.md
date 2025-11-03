# Graph Workspace Tabs Component Guide

## Overview

The `GraphWorkspaceTabs` component provides a modern tabbed interface for the graph workspace using Libadwaita's `Adw.TabView`. It organizes the graph editing experience into three main sections: Registry, Editor, and Metrics.

## Component Structure

### Three Main Tabs

1. **Registry Tab** (`registry`)
   - Browse available node types
   - Manage saved graphs
   - Node library and templates
   - Icon: `document-properties-symbolic`

2. **Editor Tab** (`editor`)
   - Visual graph editing canvas
   - Node and edge manipulation
   - Toolbar with zoom and grid controls
   - Icon: `document-edit-symbolic`

3. **Metrics Tab** (`metrics`)
   - Execution performance metrics
   - Statistics and monitoring
   - Real-time execution data
   - Icon: `chart-line-symbolic`

## Usage

### Basic Initialization

```python
from control.gtk4_gui.components import GraphWorkspaceTabs

# Create tabs
tabs = GraphWorkspaceTabs()

# Get the widget to add to your UI
widget = tabs.get_widget()
```

### Setting Tab Content

```python
# Replace editor tab with canvas
canvas = GraphCanvasWidget()
tabs.set_editor_content(canvas)

# Replace registry tab with custom widget
registry_widget = create_registry_widget()
tabs.set_registry_content(registry_widget)

# Replace metrics tab with custom widget
metrics_widget = create_metrics_widget()
tabs.set_metrics_content(metrics_widget)
```

### Tab Navigation

```python
# Get current tab
current = tabs.get_current_tab()  # Returns: "registry", "editor", or "metrics"

# Switch to specific tab
tabs.set_current_tab("metrics")
```

### Tab Change Callbacks

```python
# Set callback for tab changes
def on_tab_changed(tab_name):
    print(f"Switched to {tab_name} tab")

tabs.on_tab_changed = on_tab_changed
```

### Updating Metrics

```python
# Update metrics display
metrics_data = {
    "total_executions": 42,
    "successful": 40,
    "failed": 2,
    "average_duration": 1250  # milliseconds
}

tabs.update_metrics(metrics_data)
```

## Integration with GraphWorkspaceView

The `GraphWorkspaceView` automatically creates and manages the tabs:

```python
class GraphWorkspaceView:
    def create_content(self):
        # Create tabbed workspace
        self.tabs = GraphWorkspaceTabs()
        self.tabs.on_tab_changed = self._on_tab_changed
        
        # Create canvas for editor tab
        self.canvas = GraphCanvasWidget()
        
        # Set canvas as editor tab content
        self.tabs.set_editor_content(self.canvas)
        
        # Add tabs to main box
        main_box.append(self.tabs.get_widget())
```

## API Reference

### GraphWorkspaceTabs Class

#### Methods

- `get_widget() -> Gtk.Widget`
  - Returns the main notebook widget

- `set_editor_content(widget: Gtk.Widget)`
  - Replace the editor tab content

- `set_registry_content(widget: Gtk.Widget)`
  - Replace the registry tab content

- `set_metrics_content(widget: Gtk.Widget)`
  - Replace the metrics tab content

- `get_current_tab() -> str`
  - Get the currently selected tab name

- `set_current_tab(tab_name: str)`
  - Set the current tab by name

- `update_metrics(metrics: Dict[str, Any])`
  - Update metrics display

#### Properties

- `notebook: Adw.TabView`
  - The underlying tab view widget

- `on_tab_changed: Optional[Callable[[str], None]]`
  - Callback function for tab change events

- `registry_page`, `editor_page`, `metrics_page`
  - Tab page objects for advanced customization

## Styling

The component uses Libadwaita CSS classes for consistent styling:

- `title-2` - Tab titles
- `dim-label` - Descriptive text
- `card` - Metric rows
- `monospace` - Metric values

## Future Enhancements

1. **Tab Persistence**
   - Remember last selected tab
   - Save tab state to preferences

2. **Keyboard Shortcuts**
   - Ctrl+1 for Registry
   - Ctrl+2 for Editor
   - Ctrl+3 for Metrics

3. **Tab Customization**
   - Custom tab icons
   - Tab reordering
   - Tab closing

4. **Advanced Metrics**
   - Performance charts
   - Real-time graphs
   - Export metrics data

## File Locations

- Component: `control/gtk4_gui/components/graph_workspace_tabs.py`
- Integration: `control/gtk4_gui/views/graph_workspace_view.py`
- Exports: `control/gtk4_gui/components/__init__.py`

## Dependencies

- `gi.repository.Gtk` - GTK4 bindings
- `gi.repository.Adw` - Libadwaita bindings
- Python 3.8+

## Notes

- The component uses Adw.TabView for modern GNOME integration
- Tab content can be dynamically replaced at runtime
- Tab changes trigger callbacks for custom handling
- Metrics display is extensible for custom data

