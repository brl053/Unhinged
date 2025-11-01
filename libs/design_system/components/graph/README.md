# Graph Editor Component Specifications

This directory contains platform-agnostic component specifications for a visual graph editor. These specifications define the interface, behavior, and styling for all graph editing components.

## Component Hierarchy

```
graph-canvas (complex)
├── graph-node (complex)
│   └── graph-port (primitive)
├── graph-edge (primitive)
└── graph-toolbar (container)
    ├── action-button (primitive)
    ├── icon-button (primitive)
    ├── dropdown (complex)
    └── slider (primitive)
```

## Components

### `graph-canvas.yaml`
**The foundation of the graph editor.**

Infinite pan/zoom canvas for rendering and editing node-based graphs. Manages:
- Viewport state (pan, zoom)
- Node and edge rendering
- User interactions (drag, zoom, select)
- Event coordination

**Key Properties:**
- `nodes`: Array of node objects
- `edges`: Array of edge objects
- `viewport`: Current pan/zoom state
- `grid_size`: Grid cell size for snapping
- `snap_to_grid`: Enable/disable grid snapping

**Key Events:**
- `node_moved`: Node position changed
- `edge_created`: New connection created
- `viewport_changed`: Pan or zoom changed
- `node_selected`: Selection changed

### `graph-node.yaml`
**Represents a single operation in the graph.**

Generic container for nodes representing services, operations, or data transformations. Each node:
- Has a unique ID and type
- Displays label, icon, and status
- Contains input/output ports
- Can be dragged to reposition
- Shows execution status (idle, running, completed, failed)

**Key Properties:**
- `id`: Unique identifier
- `type`: Node type (speech_to_text, llm_chat, etc.)
- `label`: Display name
- `position`: Canvas coordinates
- `data`: Node-specific configuration
- `status`: Execution status

**Key Events:**
- `clicked`: Node selected
- `double_clicked`: Open configuration
- `drag_started`/`drag_ended`: Node repositioned
- `port_hovered`: Mouse over port

### `graph-port.yaml`
**Input/output connection point on a node.**

Defines where edges can connect to nodes. Ports:
- Have direction (input or output)
- Have data type (text, audio, image, etc.)
- Can be single or multiple connections
- Show connection status

**Key Properties:**
- `id`: Unique port identifier
- `name`: Port name
- `direction`: input or output
- `data_type`: Type of data flowing through
- `connected`: Whether port has active connection
- `required`: Whether connection is required

**Key Events:**
- `hover_enter`/`hover_exit`: Mouse over port
- `drag_start`/`drag_end`: Creating connection
- `connection_created`/`connection_removed`: Connection state changed

### `graph-edge.yaml`
**Connection line between two nodes.**

Represents data flow or dependencies. Edges:
- Connect output ports to input ports
- Show connection status (valid, invalid, active)
- Can be animated during execution
- Support labels for port names

**Key Properties:**
- `id`: Unique identifier
- `source`: Source node ID
- `target`: Target node ID
- `source_handle`: Source port name
- `target_handle`: Target port name
- `status`: Connection status
- `animated`: Animate data flow

**Key Events:**
- `clicked`: Edge selected
- `hover_enter`/`hover_exit`: Mouse over edge
- `deleted`: Edge removed

### `graph-toolbar.yaml`
**Toolbar for graph editing operations.**

Provides access to:
- Node palette (available node types)
- Canvas controls (zoom, fit, reset)
- Edit controls (undo, redo, delete)
- Graph controls (save, execute, validate)
- View options (grid, minimap)

**Key Properties:**
- `node_types`: Available node types to add
- `selected_count`: Number of selected items
- `can_undo`/`can_redo`: Undo/redo availability
- `zoom_level`: Current zoom
- `is_executing`: Graph execution state

**Key Events:**
- `node_type_selected`: User selected node type
- `zoom_changed`: Zoom level changed
- `undo_clicked`/`redo_clicked`: Edit operations
- `execute_clicked`: Start graph execution

## Data Model

### Node Object
```javascript
{
  id: "node-1",                    // UUID
  type: "speech_to_text",          // NodeType enum value
  label: "Speech to Text",         // Display name
  position: { x: 100, y: 100 },   // Canvas coordinates
  data: {                          // Type-specific config
    model: "whisper-large-v3",
    service_endpoint: "localhost:9091"
  },
  selected: false,
  status: "idle",                  // idle|running|completed|failed
  error_message: ""
}
```

### Edge Object
```javascript
{
  id: "edge-1",
  source: "node-1",
  target: "node-2",
  source_handle: "transcript",     // Port name (optional)
  target_handle: "text",           // Port name (optional)
  selected: false,
  animated: false,
  status: "valid",                 // valid|invalid|active
  error_message: ""
}
```

### Viewport Object
```javascript
{
  x: 0,        // Pan offset horizontal
  y: 0,        // Pan offset vertical
  zoom: 1.0    // Zoom level (0.1 to 4.0)
}
```

## Integration with Graph Service

These components are designed to work with the Graph Service (`proto/graph_service.proto`):

- **Node types** map to `NodeType` enum
- **Graph structure** matches `Graph` protobuf message
- **Execution status** reflects `ExecutionStatus` from service
- **Validation** uses graph type rules (DAG, CYCLIC, TREE, etc.)

## Implementation Roadmap

### Phase 1: Foundation (Week 1-2)
- [ ] Generate GTK4 components from specs
- [ ] Implement canvas rendering with Cairo
- [ ] Implement pan/zoom gestures
- [ ] Create graph workspace view

### Phase 2: Core Editing (Week 3-4)
- [ ] Render nodes on canvas
- [ ] Render edges between nodes
- [ ] Implement node dragging
- [ ] Implement edge creation

### Phase 3: Integration (Week 5-6)
- [ ] Document store integration
- [ ] Graph service integration
- [ ] Real-time execution visualization
- [ ] Node palette

### Phase 4: Polish (Week 7-8)
- [ ] Undo/redo
- [ ] Copy/paste
- [ ] Multi-select
- [ ] Auto-layout
- [ ] Minimap

## Platform Portability

These specifications are designed to be platform-agnostic. Implementation targets:

1. **GTK4** (current) - Desktop Linux/Windows
2. **React** (future) - Web interface
3. **Mobile** (future) - React Native or Flutter

The same YAML specifications should generate working implementations for each platform.

## Design Principles

1. **Specification-First**: YAML specs are the source of truth
2. **Platform-Agnostic**: Specs describe *what*, not *how*
3. **Composable**: Components build on each other
4. **Accessible**: Full keyboard and screen reader support
5. **Extensible**: Easy to add new node types and features

## References

- **Graph Service**: `proto/graph_service.proto`
- **Mental Model**: `proto/GRAPH_MENTAL_MODEL.md`
- **Component System**: `libs/design_system/COMPONENT_GENERATION.md`
- **Design Tokens**: `libs/design_system/tokens/`

