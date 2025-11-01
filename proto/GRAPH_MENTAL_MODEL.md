# Graph Service Mental Model - Key Changes

## 🧠 Mental Model Shift: Graph > DAG

### Before: DAG-Centric
- DAG was the core concept
- Forced acyclic constraint from the start
- Limited to directed acyclic graphs only

### After: Graph-Centric  
- **Graph** is the core concept
- **DAG is just a validation type** (`GraphType.DAG`)
- Supports multiple graph types with different validation rules

## 🏗️ New Architecture

### Graph Types (Validation Rules)
```protobuf
enum GraphType {
  DAG = 1;                    // Directed Acyclic Graph - no cycles
  CYCLIC = 2;                 // Allows cycles  
  CYCLIC_WITH_BREAKERS = 3;   // Cycles with loop breakers (max 5 iterations)
  TREE = 4;                   // Tree structure - single root
  UNRESTRICTED = 5;           // No validation - just ensure nothing's broken
}
```

### Clean IDs (No Redundant Prefixes)
```protobuf
// Before: dag_id, node_id, edge_id
// After: id, id, id (scope is clear from context)

message Graph {
  string id = 1;              // UUID - scope is obvious
  // ...
}

message Node {
  string id = 1;              // UUID - scope is obvious  
  // ...
}
```

## 🛠️ Tool Generation Ready

The proto will be **scraped to generate LLM tools** for each node type:

```protobuf
enum NodeType {
  SPEECH_TO_TEXT = 1;         // → Tool: "speech_to_text_node"
  TEXT_TO_SPEECH = 2;         // → Tool: "text_to_speech_node"  
  LLM_CHAT = 3;              // → Tool: "llm_chat_node"
  CONTEXT_HYDRATION = 7;     // → Tool: "context_hydration_node"
  // ...
}
```

Each tool will help LLMs create nodes of that type with proper configuration.

## 📄 Document-Based Storage

Graphs are stored as **documents** with:
- **Metadata**: Created by, timestamps, version, etc.
- **Body**: The actual graph structure (nodes, edges, config)

```protobuf
message Graph {
  string id = 1;
  string name = 2;
  string description = 3;
  GraphType graph_type = 4;                         // Determines validation
  repeated Node nodes = 5;                          // Document body
  repeated Edge edges = 6;                          // Document body  
  unhinged.common.v1.ResourceMetadata metadata = 7; // Document metadata
}
```

## 🔄 gRPC Streaming Support

**Yes, gRPC supports streaming!** It's a core feature:

```protobuf
// Server streaming - one request, multiple responses
rpc StreamExecution(StreamExecutionRequest) returns (stream ExecutionEvent);
```

This enables **real-time execution monitoring** without polling:
- Client sends one request with `execution_id`
- Server streams back execution events as they happen
- Client receives real-time updates: node started, completed, failed, etc.

## 🎯 Use Cases Enabled

### 1. Voice Pipeline (DAG)
```
Voice → STT → LLM → TTS → Audio
```
- `GraphType.DAG` - no cycles allowed
- Linear pipeline execution

### 2. Context-Enhanced Pipeline (DAG)  
```
Voice → STT → Context Hydration → LLM → TTS → Audio
                    ↑
              Vector DB Lookup
```

### 3. Feedback Loop (CYCLIC_WITH_BREAKERS)
```
Input → Process → Evaluate → Improve
           ↑         ↓
           ←---------←
        (max 5 iterations)
```

### 4. Complex Workflow (UNRESTRICTED)
```
Multiple inputs, parallel processing, conditional branches
No validation - just ensure nothing's broken
```

## 🚀 Benefits

1. **Flexibility**: Not locked into DAG-only thinking
2. **Extensibility**: Easy to add new graph types and validation rules
3. **Tool Generation**: Proto scraping creates LLM tools automatically  
4. **Document Storage**: Clean metadata + body separation
5. **Real-time Monitoring**: gRPC streaming for live execution updates
6. **Clean APIs**: No redundant prefixes, clear scope from context

## 🎯 Next Steps

1. Update service implementation to use Graph instead of DAG
2. Implement graph type validation logic
3. Add tool generation from proto scraping
4. Test with voice pipeline and cyclic workflows

This mental model shift opens up much more flexibility while keeping the implementation clean and focused.
