# Graph Editor Specifications - Quick Reference

## File Structure

```
libs/design_system/components/graph/
├── graph-canvas.yaml                    # Infinite pan/zoom canvas
├── graph-node.yaml                      # Node container
├── graph-port.yaml                      # Input/output connection point
├── graph-edge.yaml                      # Connection line
├── graph-toolbar.yaml                   # Editing toolbar
├── README.md                            # Component overview
├── IMPLEMENTATION_GUIDE.md              # Step-by-step roadmap
├── GRAPH_SERVICE_MAPPING.md             # Protobuf integration
├── SPECIFICATION_VALIDATION_CHECKLIST.md # Validation checklist
└── QUICK_REFERENCE.md                   # This file
```

## Component Quick Reference

### graph-canvas
**Type**: Complex | **Purpose**: Infinite pan/zoom canvas for graph editing

**Key Properties**:
- `nodes`: Array of node objects
- `edges`: Array of edge objects
- `viewport`: {x, y, zoom}
- `grid_size`: Grid cell size
- `snap_to_grid`: Enable grid snapping

**Key Events**:
- `node_moved`: Node position changed
- `edge_created`: Connection created
- `viewport_changed`: Pan/zoom changed
- `node_selected`: Selection changed

**States**: idle, panning, selecting, connecting, dragging_node

---

### graph-node
**Type**: Complex | **Purpose**: Represents operation/service in graph

**Key Properties**:
- `id`: Unique identifier
- `type`: Node type (speech_to_text, llm_chat, etc.)
- `label`: Display name
- `position`: {x, y} canvas coordinates
- `data`: Node-specific configuration
- `status`: idle, running, completed, failed

**Key Events**:
- `clicked`: Node selected
- `double_clicked`: Open configuration
- `drag_started`/`drag_ended`: Node moved
- `port_hovered`: Mouse over port

**States**: idle, running, completed, failed, selected, hovered

---

### graph-port
**Type**: Primitive | **Purpose**: Input/output connection point

**Key Properties**:
- `id`: Unique port identifier
- `name`: Port name
- `direction`: input or output
- `data_type`: text, audio, image, any
- `connected`: Has active connection
- `required`: Connection required for execution

**Key Events**:
- `hover_enter`/`hover_exit`: Mouse over port
- `drag_start`/`drag_end`: Creating connection
- `connection_created`/`connection_removed`: Connection state

**States**: idle, hovering, connecting, connected, error

---

### graph-edge
**Type**: Primitive | **Purpose**: Connection line between nodes

**Key Properties**:
- `id`: Unique identifier
- `source`: Source node ID
- `target`: Target node ID
- `source_handle`: Source port name
- `target_handle`: Target port name
- `status`: valid, invalid, active
- `animated`: Animate data flow

**Key Events**:
- `clicked`: Edge selected
- `hover_enter`/`hover_exit`: Mouse over edge
- `deleted`: Edge removed

**States**: idle, hovered, selected, active, error

---

### graph-toolbar
**Type**: Container | **Purpose**: Toolbar for editing operations

**Key Properties**:
- `node_types`: Available node types
- `selected_count`: Number of selected items
- `can_undo`/`can_redo`: Undo/redo availability
- `zoom_level`: Current zoom
- `is_executing`: Graph execution state

**Key Events**:
- `node_type_selected`: User selected node type
- `zoom_changed`: Zoom level changed
- `undo_clicked`/`redo_clicked`: Edit operations
- `execute_clicked`: Start execution

**States**: idle, selecting_node, executing

---

## Data Model Quick Reference

### Node Object
```javascript
{
  id: "node-1",
  type: "speech_to_text",
  label: "Speech to Text",
  position: { x: 100, y: 100 },
  data: { model: "whisper-large-v3" },
  selected: false,
  status: "idle",
  error_message: ""
}
```

### Edge Object
```javascript
{
  id: "edge-1",
  source: "node-1",
  target: "node-2",
  source_handle: "transcript",
  target_handle: "text",
  selected: false,
  animated: false,
  status: "valid",
  error_message: ""
}
```

### Viewport Object
```javascript
{
  x: 0,      // Pan offset horizontal
  y: 0,      // Pan offset vertical
  zoom: 1.0  // Zoom level (0.1 to 4.0)
}
```

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1-2)
- Generate GTK4 components from specs
- Implement canvas rendering with Cairo
- Create graph workspace view

### Phase 2: Core Editing (Week 3-4)
- Render nodes on canvas
- Render edges between nodes
- Implement edge creation

### Phase 3: Integration (Week 5-6)
- Document store integration (save/load)
- Graph service integration (execution)
- Node palette

### Phase 4: Polish (Week 7-8)
- Undo/redo
- Multi-select and copy/paste
- Auto-layout
- Minimap

---

## Integration Points

### Graph Service (`proto/graph_service.proto`)
- Node types → NodeType enum
- Graph structure → Graph protobuf message
- Execution status → ExecutionStatus enum
- Graph types → GraphType enum (DAG, CYCLIC, etc.)

### Document Store (`proto/document_store.proto`)
- Graphs stored as documents
- Automatic versioning
- Tag-based version management

### Design System (`libs/design_system/`)
- Components use design tokens
- Generated code follows patterns
- Accessibility built-in

---

## Node Types

```
speech_to_text      → Convert audio to text
text_to_speech      → Convert text to audio
llm_chat            → LLM chat service
vision_ai           → Vision/image processing
context_hydration   → Context enrichment
data_transform      → Data transformation
custom_service      → Custom service
```

---

## Keyboard Shortcuts

### Canvas
- **Delete**: Delete selected nodes/edges
- **Ctrl+Z**: Undo
- **Ctrl+Y**: Redo
- **Ctrl+A**: Select all
- **Escape**: Deselect all
- **Arrow Keys**: Move selected nodes
- **Ctrl+C**: Copy
- **Ctrl+V**: Paste
- **Ctrl+D**: Duplicate

### Toolbar
- **Ctrl+S**: Save
- **Ctrl+Enter**: Execute

---

## Validation Rules

### Connection Validation
1. Cannot connect output to output
2. Cannot connect input to input
3. Data types must be compatible
4. Cannot create cycles (if GraphType is DAG)
5. Cannot exceed max connections per port

### Graph Validation
- **DAG**: No cycles allowed
- **CYCLIC**: Cycles allowed
- **CYCLIC_WITH_BREAKERS**: Cycles with breaker nodes
- **TREE**: Single root, no multiple parents
- **UNRESTRICTED**: Any structure allowed

---

## Performance Targets

- **Nodes**: Support 100+ nodes on canvas
- **Pan/Zoom**: Smooth and responsive
- **Rendering**: 60 FPS target
- **Execution**: Real-time status updates

**Note**: If performance issues arise with 100+ nodes, implement viewport culling.

---

## Accessibility

### Keyboard Support
- Full keyboard navigation
- Tab through nodes
- Arrow keys to move
- Enter to open config
- Delete to remove

### Screen Reader Support
- Describe graph structure
- Announce node types and status
- Describe connections

### Visual Accessibility
- High contrast mode support
- Adjustable node size
- Clear status indicators

---

## Platform Portability

### Current
- **GTK4**: Desktop Linux/Windows

### Future
- **React**: Web interface
- **Mobile**: React Native or Flutter

Same YAML specifications work for all platforms.

---

## Documentation Files

| File | Purpose |
|------|---------|
| README.md | Component overview and hierarchy |
| IMPLEMENTATION_GUIDE.md | Step-by-step implementation roadmap |
| GRAPH_SERVICE_MAPPING.md | Protobuf integration details |
| SPECIFICATION_VALIDATION_CHECKLIST.md | Validation checklist |
| QUICK_REFERENCE.md | This quick reference |

---

## Getting Started

1. **Review** the README.md for component overview
2. **Study** the IMPLEMENTATION_GUIDE.md for roadmap
3. **Check** GRAPH_SERVICE_MAPPING.md for integration
4. **Validate** using SPECIFICATION_VALIDATION_CHECKLIST.md
5. **Reference** QUICK_REFERENCE.md during implementation

---

## Questions?

Refer to the appropriate documentation:
- **"What components exist?"** → README.md
- **"How do I implement this?"** → IMPLEMENTATION_GUIDE.md
- **"How does this integrate with Graph Service?"** → GRAPH_SERVICE_MAPPING.md
- **"Is this complete?"** → SPECIFICATION_VALIDATION_CHECKLIST.md
- **"Quick lookup?"** → QUICK_REFERENCE.md (this file)

