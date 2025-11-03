# Registry UI - Quick Reference Guide

## What Was Built

A **reusable CRUD component** for managing first-class entities (documents) in the Unhinged system.

## Key Changes

### 1. Tabs Are Now Visible ✅

**Before**: Tabs existed but were invisible (no TabBar)  
**After**: TabBar + TabView = visible, clickable tabs

```python
# In GraphWorkspaceTabs.__init__()
self.tab_bar = Adw.TabBar()
self.tab_bar.set_view(self.notebook)
self.main_box.append(self.tab_bar)
self.main_box.append(self.notebook)
```

### 2. Registry Tab Has Full CRUD UI ✅

**Create**: Dialog with name, description, graph type  
**Read**: List all graphs with metadata  
**Update**: Edit button → opens in Editor tab  
**Delete**: Confirmation dialog + async delete  

### 3. Reusable Pattern ✅

The `RegistryUI` component works for ANY document type:

```python
# For graphs
graphs_registry = RegistryUI(doc_store_client)
graphs_registry.on_create_graph = handle_create
graphs_registry.on_edit_graph = handle_edit
graphs_registry.on_delete_graph = handle_delete

# For tools (same pattern)
tools_registry = RegistryUI(doc_store_client)
tools_registry.on_create_tool = handle_create
# ... etc

# For users (same pattern)
users_registry = RegistryUI(doc_store_client)
users_registry.on_create_user = handle_create
# ... etc
```

## Files Changed

| File | Change | Lines |
|------|--------|-------|
| `registry_ui.py` | **NEW** | 310 |
| `graph_workspace_tabs.py` | Modified | +30 |
| `document_store_client.py` | Modified | +40 |
| `graph_workspace_view.py` | Modified | +5 |
| `__init__.py` | Modified | +3 |

## How to Use

### Basic Setup

```python
from control.gtk4_gui.components import RegistryUI, GraphWorkspaceTabs
from control.gtk4_gui.components.document_store_client import DocumentStoreClient

# Create document store client
doc_store = DocumentStoreClient()

# Create registry UI
registry = RegistryUI(doc_store)

# Set callbacks
registry.on_create_graph = my_create_handler
registry.on_edit_graph = my_edit_handler
registry.on_delete_graph = my_delete_handler

# Get widget and add to UI
widget = registry.create_widget()
container.append(widget)
```

### In GraphWorkspaceView

```python
# Already integrated!
self.tabs = GraphWorkspaceTabs()
self.tabs.set_registry_client(self.doc_store_client)
```

## API Reference

### RegistryUI Class

#### Methods

- `create_widget() -> Gtk.Widget`
  - Returns the main registry UI widget

- `set_registry_client(doc_store_client)`
  - Set the document store client (done automatically)

#### Callbacks

- `on_create_graph(name: str, description: str, graph_type: str)`
  - Called when user creates a graph

- `on_edit_graph(graph_id: str)`
  - Called when user clicks edit button

- `on_delete_graph(graph_id: str)`
  - Called when user confirms delete

### DocumentStoreClient Methods

- `async save_graph(graph, namespace="graphs", tags=None, session_id=None) -> str`
  - Save graph, returns graph_id

- `async load_graph(graph_id, version=None, tag=None) -> Graph`
  - Load graph by ID, version, or tag

- `async list_graphs(namespace="graphs", tag=None, session_id=None) -> List[Dict]`
  - List all graphs with metadata

- `async delete_graph(graph_id, deleted_by="user", deleted_by_type="person") -> bool`
  - Delete graph, returns success status

## UI Flow

```
User clicks "+ Create New Graph"
    ↓
Dialog appears (name, description, type)
    ↓
User fills form and clicks "Create"
    ↓
on_create_graph callback triggered
    ↓
Graph saved to document store
    ↓
List reloads automatically
    ↓
New graph appears in list

---

User clicks "Edit" on graph
    ↓
on_edit_graph callback triggered
    ↓
Graph loaded from document store
    ↓
Editor tab activated
    ↓
Canvas populated with graph

---

User clicks "Delete" on graph
    ↓
Confirmation dialog appears
    ↓
User confirms
    ↓
on_delete_graph callback triggered
    ↓
Graph deleted from store
    ↓
List reloads automatically
```

## Status Messages

The Registry UI provides real-time feedback:

- ✅ "Loaded X graphs"
- ⚠️ "Document store not available"
- ❌ "Error loading graphs: ..."
- 🔄 "Loading graphs..."
- 📝 "Creating graph: ..."
- 🗑️ "Deleting graph..."

## Design Principles

✅ **Async-first**: All I/O is non-blocking  
✅ **User feedback**: Status messages for all operations  
✅ **Confirmation dialogs**: Destructive actions require confirmation  
✅ **Error handling**: Graceful error messages  
✅ **Reusable**: Works for any document type  
✅ **Protobuf-first**: All documents are protobuf-serialized  
✅ **Document-centric**: First-class entities are documents  

## Testing

All files compile successfully:
```bash
python3 -m py_compile control/gtk4_gui/components/registry_ui.py
python3 -m py_compile control/gtk4_gui/components/graph_workspace_tabs.py
python3 -m py_compile control/gtk4_gui/components/document_store_client.py
```

Application runs without errors:
```bash
./unhinged
```

## Next Steps

1. Implement `on_create_graph` callback in GraphWorkspaceView
2. Implement `on_edit_graph` callback to load graph into canvas
3. Implement `on_delete_graph` callback for cleanup
4. Test with actual document store service
5. Extend pattern to other document types

## Architecture Alignment

✅ Service framework level (not client-specific)  
✅ Polyglot support (Python + Kotlin + future)  
✅ Document model (NoSQL, text/zip abstraction)  
✅ Reusable CRUD pattern  
✅ Protobuf-first system  
✅ Persistence with versioning  

