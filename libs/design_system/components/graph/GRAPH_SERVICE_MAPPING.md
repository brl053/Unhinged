# Graph Editor Specifications - Graph Service Mapping

This document shows how the graph editor component specifications map to the existing Graph Service protobuf definitions.

## Overview

The graph editor specifications are designed to work seamlessly with the Graph Service (`proto/graph_service.proto`). The UI components represent the visual manifestation of the protobuf data structures.

## Data Structure Mapping

### Graph Service Message → Component Data

#### `Graph` (protobuf) → `graph-canvas` (component)

**Protobuf Definition**:
```protobuf
message Graph {
  string id = 1;
  repeated Node nodes = 2;
  repeated Edge edges = 3;
  GraphType type = 4;
  string name = 5;
  string description = 6;
  google.protobuf.Timestamp created_at = 7;
  google.protobuf.Timestamp updated_at = 8;
}
```

**Component Mapping**:
```yaml
graph-canvas:
  properties:
    nodes: []        # From Graph.nodes
    edges: []        # From Graph.edges
    viewport: {}     # UI-only (not in protobuf)
    grid_size: 20    # UI-only (not in protobuf)
```

**Metadata Mapping**:
- `Graph.id` → Used for document store persistence
- `Graph.name` → Displayed in workspace title
- `Graph.type` → Determines validation rules (DAG, CYCLIC, etc.)
- `Graph.created_at`, `updated_at` → Shown in document metadata

---

#### `Node` (protobuf) → `graph-node` (component)

**Protobuf Definition**:
```protobuf
message Node {
  string id = 1;
  string name = 2;
  NodeType type = 3;
  google.protobuf.Struct config = 4;
}
```

**Component Mapping**:
```yaml
graph-node:
  properties:
    id: "node-1"              # From Node.id
    type: "speech_to_text"    # From Node.type (enum value)
    label: "Speech to Text"   # From Node.name
    data: {}                  # From Node.config (JSON)
    position: {x, y}          # UI-only (not in protobuf)
    status: "idle"            # UI-only (execution state)
    selected: false           # UI-only (selection state)
```

**Type Mapping** (`NodeType` enum):
```
NodeType.SPEECH_TO_TEXT      → "speech_to_text"
NodeType.TEXT_TO_SPEECH      → "text_to_speech"
NodeType.LLM_CHAT            → "llm_chat"
NodeType.VISION_AI           → "vision_ai"
NodeType.CONTEXT_HYDRATION   → "context_hydration"
NodeType.DATA_TRANSFORM      → "data_transform"
NodeType.CUSTOM_SERVICE      → "custom_service"
```

**Configuration Example**:
```json
// Node.config (protobuf Struct)
{
  "model": "whisper-large-v3",
  "service_endpoint": "localhost:9091",
  "language": "en"
}

// Becomes graph-node.data
{
  "model": "whisper-large-v3",
  "service_endpoint": "localhost:9091",
  "language": "en"
}
```

---

#### `Edge` (protobuf) → `graph-edge` (component)

**Protobuf Definition**:
```protobuf
message Edge {
  string id = 1;
  string source_node_id = 2;
  string target_node_id = 3;
  string source_output = 4;
  string target_input = 5;
}
```

**Component Mapping**:
```yaml
graph-edge:
  properties:
    id: "edge-1"                    # From Edge.id
    source: "node-1"                # From Edge.source_node_id
    target: "node-2"                # From Edge.target_node_id
    source_handle: "transcript"     # From Edge.source_output
    target_handle: "text"           # From Edge.target_input
    status: "valid"                 # UI-only (validation state)
    selected: false                 # UI-only (selection state)
```

---

#### `ExecutionStatus` (protobuf) → `graph-node.status` (component)

**Protobuf Definition**:
```protobuf
enum ExecutionStatus {
  IDLE = 0;
  RUNNING = 1;
  COMPLETED = 2;
  FAILED = 3;
}
```

**Component Mapping**:
```yaml
graph-node:
  status:
    "idle"       # ExecutionStatus.IDLE
    "running"    # ExecutionStatus.RUNNING
    "completed"  # ExecutionStatus.COMPLETED
    "failed"     # ExecutionStatus.FAILED
```

---

#### `GraphType` (protobuf) → Validation Rules

**Protobuf Definition**:
```protobuf
enum GraphType {
  DAG = 0;
  CYCLIC = 1;
  CYCLIC_WITH_BREAKERS = 2;
  TREE = 3;
  UNRESTRICTED = 4;
}
```

**Component Validation**:
- `DAG`: No cycles allowed (topological sort required)
- `CYCLIC`: Cycles allowed
- `CYCLIC_WITH_BREAKERS`: Cycles allowed with breaker nodes
- `TREE`: Single root, no multiple parents
- `UNRESTRICTED`: Any structure allowed

**UI Implications**:
- Validation errors shown on edges
- Invalid connections rejected during creation
- Status indicator shows validation state

---

## Service Integration Points

### 1. Graph Execution

**Flow**:
```
User clicks "Execute" in toolbar
    ↓
graph-toolbar emits "execute_clicked" event
    ↓
GraphWorkspaceView calls graph_service.ExecuteGraph(graph_id)
    ↓
Service returns execution stream
    ↓
GraphWorkspaceView updates node status in real-time
    ↓
graph-node components update visual status
```

**Protobuf Service Method**:
```protobuf
rpc ExecuteGraph(ExecuteGraphRequest) returns (stream ExecutionEvent);
```

**Component Updates**:
- `graph-node.status` changes from "idle" → "running" → "completed"/"failed"
- `graph-edge.animated` set to true during data flow
- `graph-edge.status` shows "active" during execution

### 2. Graph Persistence

**Flow**:
```
User clicks "Save" in toolbar
    ↓
graph-toolbar emits "save_clicked" event
    ↓
GraphWorkspaceView serializes graph to protobuf
    ↓
Document store saves Graph message
    ↓
Workspace shows save confirmation
```

**Protobuf Service Method**:
```protobuf
rpc PutDocument(PutDocumentRequest) returns (Document);
```

**Serialization**:
```python
# From component state to protobuf
graph_proto = Graph(
    id=graph_id,
    nodes=[
        Node(
            id=node.id,
            name=node.label,
            type=NodeType[node.type.upper()],
            config=json_to_struct(node.data)
        )
        for node in canvas.nodes
    ],
    edges=[
        Edge(
            id=edge.id,
            source_node_id=edge.source,
            target_node_id=edge.target,
            source_output=edge.source_handle,
            target_input=edge.target_handle
        )
        for edge in canvas.edges
    ],
    type=GraphType[graph_type.upper()],
    name=graph_name
)

# Save to document store
document_store.put_document(graph_proto)
```

### 3. Graph Loading

**Flow**:
```
User opens graph from document store
    ↓
GraphWorkspaceView loads Graph protobuf
    ↓
Deserialize to component state
    ↓
graph-canvas renders nodes and edges
```

**Deserialization**:
```python
# From protobuf to component state
canvas_state = {
    "nodes": [
        {
            "id": node.id,
            "label": node.name,
            "type": NodeType(node.type).name.lower(),
            "data": struct_to_json(node.config),
            "position": {"x": 100, "y": 100},  # Default position
            "status": "idle"
        }
        for node in graph_proto.nodes
    ],
    "edges": [
        {
            "id": edge.id,
            "source": edge.source_node_id,
            "target": edge.target_node_id,
            "source_handle": edge.source_output,
            "target_handle": edge.target_input,
            "status": "valid"
        }
        for edge in graph_proto.edges
    ]
}
```

### 4. Node Type Discovery

**Flow**:
```
GraphWorkspaceView initializes
    ↓
Calls graph_service.ListNodeTypes()
    ↓
Populates graph-toolbar with available types
    ↓
User can drag types to canvas
```

**Protobuf Service Method**:
```protobuf
rpc ListNodeTypes(Empty) returns (ListNodeTypesResponse);
```

**Toolbar Population**:
```python
node_types = graph_service.list_node_types()
toolbar.node_types = [
    {
        "id": node_type.id,
        "label": node_type.name,
        "icon": node_type.icon_name,
        "description": node_type.description
    }
    for node_type in node_types
]
```

---

## Validation Rules

### Connection Validation

**Rules**:
1. Cannot connect output port to output port
2. Cannot connect input port to input port
3. Data types must be compatible
4. Cannot create cycles (if GraphType is DAG)
5. Cannot exceed maximum connections per port

**Implementation**:
```python
def validate_connection(source_port, target_port, graph_type):
    # Check direction
    if source_port.direction != "output":
        return False, "Source must be output port"
    if target_port.direction != "input":
        return False, "Target must be input port"
    
    # Check data type compatibility
    if not is_compatible(source_port.data_type, target_port.data_type):
        return False, "Data type mismatch"
    
    # Check for cycles (if DAG)
    if graph_type == GraphType.DAG:
        if would_create_cycle(source_port.node, target_port.node):
            return False, "Would create cycle in DAG"
    
    return True, ""
```

**Component Feedback**:
- Invalid connections rejected during drag
- `graph-edge.status` set to "invalid" with error message
- Visual feedback (red color, error tooltip)

---

## Position Persistence

**Note**: Node positions are NOT stored in the protobuf Graph message. They are UI-only state.

**Persistence Strategy**:
1. Store positions in document metadata (optional)
2. Or recalculate on load using auto-layout
3. Or use default positions and let user arrange

**Recommendation**: Store positions in document metadata for better UX:
```json
{
  "metadata": {
    "node_positions": {
      "node-1": {"x": 100, "y": 100},
      "node-2": {"x": 300, "y": 100}
    }
  }
}
```

---

## Summary

The graph editor components are designed to be a thin UI layer over the Graph Service protobuf definitions:

- **graph-canvas** ↔ **Graph** message
- **graph-node** ↔ **Node** message
- **graph-edge** ↔ **Edge** message
- **graph-port** ↔ Port names in Edge message
- **graph-toolbar** ↔ Service RPC methods

This mapping ensures:
- ✅ Tight integration with existing service
- ✅ Consistent data model across platforms
- ✅ Easy serialization/deserialization
- ✅ Clear separation of concerns (UI vs. logic)

