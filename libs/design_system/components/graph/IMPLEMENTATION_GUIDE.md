# Graph Editor Implementation Guide

This guide outlines the step-by-step process for implementing the graph editor components in GTK4, with future portability to React and other platforms.

## Phase 1: Foundation (Week 1-2)

### Step 1.1: Generate GTK4 Components from Specs

**Objective**: Use the component generation system to create GTK4 Python code from YAML specs.

**Tasks**:
1. Run component generator on graph component specs
2. Generate GTK4 Python classes for each component
3. Verify generated code compiles and imports correctly
4. Create unit tests for generated components

**Expected Output**:
```
generated/design_system/gtk4/
├── graph_canvas.py
├── graph_node.py
├── graph_port.py
├── graph_edge.py
└── graph_toolbar.py
```

**Success Criteria**:
- All components import without errors
- Generated code follows GTK4 patterns
- Type hints are correct
- Docstrings match spec descriptions

### Step 1.2: Implement Canvas Rendering

**Objective**: Create a working canvas with pan/zoom support.

**Tasks**:
1. Create `GraphCanvasWidget` extending `Gtk.DrawingArea`
2. Implement Cairo rendering context
3. Implement pan gesture (drag to move viewport)
4. Implement zoom gesture (scroll wheel or pinch)
5. Implement grid rendering
6. Add viewport state management

**Key Classes**:
- `GraphCanvasWidget`: Main canvas widget
- `Viewport`: Manages pan/zoom state
- `CanvasRenderer`: Handles Cairo drawing

**Success Criteria**:
- Canvas renders without flickering
- Pan is smooth and responsive
- Zoom works with scroll wheel
- Grid aligns with zoom level
- Viewport state persists

### Step 1.3: Create Graph Workspace View

**Objective**: Integrate canvas into GTK4 UI as a new workspace.

**Tasks**:
1. Create `GraphWorkspaceView` class
2. Add "Graphs" tab to sidebar navigation
3. Implement workspace layout (toolbar + canvas)
4. Connect workspace to document store
5. Add basic toolbar with zoom controls

**File**: `control/gtk4_gui/views/graph_workspace_view.py`

**Success Criteria**:
- "Graphs" tab appears in sidebar
- Clicking tab shows graph workspace
- Toolbar is visible and functional
- Canvas fills available space
- Zoom controls work

## Phase 2: Core Editing (Week 3-4)

### Step 2.1: Render Nodes on Canvas

**Objective**: Display nodes as interactive rectangles on the canvas.

**Tasks**:
1. Implement node rendering in Cairo
2. Add node positioning based on `position` property
3. Implement node selection (click to select)
4. Add visual feedback for selected nodes
5. Implement node dragging
6. Add status indicator (color based on status)

**Key Methods**:
- `render_node(node, viewport)`: Draw single node
- `get_node_at_position(x, y)`: Hit detection
- `start_drag_node(node_id)`: Begin drag
- `move_node(node_id, position)`: Update position

**Success Criteria**:
- Nodes render at correct positions
- Nodes are selectable
- Selected nodes have visual highlight
- Nodes can be dragged
- Status colors display correctly

### Step 2.2: Render Edges Between Nodes

**Objective**: Display connections as lines between nodes.

**Tasks**:
1. Implement edge rendering in Cairo
2. Calculate port positions on nodes
3. Draw Bezier curves between ports
4. Add edge selection
5. Add status indicators (color, animation)
6. Implement edge deletion (click + delete key)

**Key Methods**:
- `render_edge(edge, nodes, viewport)`: Draw single edge
- `get_edge_at_position(x, y)`: Hit detection
- `calculate_port_position(node, port_name)`: Port location

**Success Criteria**:
- Edges render as smooth curves
- Edges connect to correct ports
- Edges are selectable
- Edge colors reflect status
- Edges can be deleted

### Step 2.3: Implement Edge Creation

**Objective**: Allow users to create connections by dragging between ports.

**Tasks**:
1. Implement port rendering on nodes
2. Detect drag from output port
3. Show preview line while dragging
4. Detect drop on input port
5. Validate connection (type checking)
6. Create edge on successful drop

**Key Methods**:
- `start_connection(source_port)`: Begin connection
- `update_connection_preview(target_position)`: Show preview
- `complete_connection(target_port)`: Create edge
- `validate_connection(source, target)`: Type checking

**Success Criteria**:
- Ports are visible on nodes
- Dragging from port shows preview line
- Dropping on valid port creates edge
- Invalid connections are rejected
- Connection events are emitted

## Phase 3: Integration (Week 5-6)

### Step 3.1: Document Store Integration

**Objective**: Save and load graphs from document store.

**Tasks**:
1. Implement graph serialization to protobuf
2. Implement graph deserialization from protobuf
3. Add "Save" button to toolbar
4. Add "Load" dialog
5. Implement auto-save
6. Add version management

**Key Methods**:
- `serialize_graph()`: Convert to protobuf
- `deserialize_graph(proto)`: Convert from protobuf
- `save_graph()`: Save to document store
- `load_graph(graph_id)`: Load from document store

**Success Criteria**:
- Graphs can be saved
- Graphs can be loaded
- Saved graphs match original
- Version history works
- Auto-save doesn't block UI

### Step 3.2: Graph Service Integration

**Objective**: Execute graphs and visualize execution.

**Tasks**:
1. Connect to graph service gRPC endpoint
2. Implement graph execution
3. Stream execution events
4. Update node status during execution
5. Animate edges during data flow
6. Display execution results

**Key Methods**:
- `execute_graph()`: Start execution
- `stream_execution_events()`: Listen for updates
- `update_node_status(node_id, status)`: Update UI
- `animate_edge(edge_id)`: Show data flow

**Success Criteria**:
- Graphs execute via service
- Node status updates in real-time
- Edges animate during execution
- Execution results display
- Errors are shown clearly

### Step 3.3: Node Palette

**Objective**: Allow users to add nodes to the graph.

**Tasks**:
1. Populate toolbar with available node types
2. Implement drag-from-palette to canvas
3. Create new node on drop
4. Show node configuration dialog
5. Add node type icons
6. Add node type descriptions

**Key Methods**:
- `get_available_node_types()`: From graph service
- `create_node_from_palette(type, position)`: Add node
- `show_node_config_dialog(node)`: Configure node

**Success Criteria**:
- Node palette shows all types
- Dragging from palette creates node
- New nodes appear on canvas
- Configuration dialog works
- Node icons display correctly

## Phase 4: Polish (Week 7-8)

### Step 4.1: Undo/Redo

**Objective**: Implement undo/redo for all editing operations.

**Tasks**:
1. Create command pattern for operations
2. Implement undo/redo stack
3. Add undo/redo buttons to toolbar
4. Implement keyboard shortcuts (Ctrl+Z, Ctrl+Y)
5. Limit stack size

**Success Criteria**:
- All operations are undoable
- Undo/redo buttons work
- Keyboard shortcuts work
- Stack size is reasonable

### Step 4.2: Multi-Select and Copy/Paste

**Objective**: Support selecting multiple nodes and copying/pasting.

**Tasks**:
1. Implement multi-select (Ctrl+click)
2. Implement marquee selection
3. Implement copy (Ctrl+C)
4. Implement paste (Ctrl+V)
5. Implement duplicate (Ctrl+D)
6. Preserve connections when copying

**Success Criteria**:
- Multiple nodes can be selected
- Marquee selection works
- Copy/paste works
- Connections are preserved
- Duplicates are offset

### Step 4.3: Auto-Layout

**Objective**: Automatically arrange nodes for better visualization.

**Tasks**:
1. Implement hierarchical layout algorithm
2. Add "Auto-Layout" button to toolbar
3. Animate nodes to new positions
4. Preserve user-arranged nodes option

**Success Criteria**:
- Auto-layout produces readable graphs
- Animation is smooth
- User can disable auto-layout

### Step 4.4: Minimap

**Objective**: Add minimap for navigation in large graphs.

**Tasks**:
1. Create minimap widget
2. Show graph overview
3. Show viewport rectangle
4. Allow clicking to navigate
5. Add toggle button to toolbar

**Success Criteria**:
- Minimap shows graph overview
- Viewport rectangle is visible
- Clicking minimap navigates
- Toggle works

## Testing Strategy

### Unit Tests
- Test component generation
- Test canvas rendering
- Test node/edge operations
- Test document store integration

### Integration Tests
- Test graph service integration
- Test execution visualization
- Test save/load cycle

### UI Tests
- Test keyboard shortcuts
- Test mouse interactions
- Test touch gestures (if applicable)

### Performance Tests
- Test with 100+ nodes
- Measure pan/zoom responsiveness
- Measure rendering performance

## Performance Considerations

### Viewport Culling
For graphs with 100+ nodes, implement viewport culling:
- Only render nodes/edges visible in viewport
- Update culling on pan/zoom
- Measure impact on performance

### Rendering Optimization
- Use double buffering
- Cache node/edge geometry
- Batch Cairo operations
- Profile with GTK4 profiler

### Memory Management
- Limit undo/redo stack size
- Clean up event listeners
- Manage gRPC connections

## Accessibility

### Keyboard Navigation
- Tab through nodes
- Arrow keys to move selected nodes
- Enter to open configuration
- Delete to remove

### Screen Reader Support
- Describe graph structure
- Announce node types and status
- Describe connections

### Visual Accessibility
- High contrast mode support
- Adjustable node size
- Clear status indicators

## Future Enhancements

1. **React Implementation**: Use same specs to generate React components
2. **Mobile Support**: Touch-optimized interface
3. **Collaborative Editing**: Real-time multi-user editing
4. **Advanced Layouts**: Force-directed, circular, etc.
5. **Node Search**: Find nodes by type or name
6. **Graph Templates**: Pre-built graph patterns
7. **Debugging**: Step through execution
8. **Analytics**: Execution statistics and profiling

