# DAG Service - AI Workflow Orchestration

## Overview

The DAG Service provides minimal, focused workflow orchestration for voice-first AI pipelines. It executes Directed Acyclic Graphs (DAGs) that coordinate calls to existing AI services like speech-to-text, LLM processing, and text-to-speech.

## Architecture

### Core Components

- **`main.py`**: Service launcher and entry point
- **`grpc_server.py`**: gRPC service implementation
- **`dag_executor.py`**: Core DAG execution engine
- **`node_executors.py`**: Node-specific execution logic
- **`test_dag_service.py`**: Test suite for validation

### Service Integration

The DAG service orchestrates existing services:
- **AudioService** (port 9091/9092): Speech-to-text and text-to-speech
- **ChatService** (port 9095): LLM chat and completion
- **ContextService** (port 9094): Prompt enhancement
- **Custom Services**: HTTP/gRPC endpoints

## Supported Node Types

### AI Services
- `SPEECH_TO_TEXT`: Convert audio to text
- `TEXT_TO_SPEECH`: Convert text to audio
- `LLM_CHAT`: LLM conversation processing
- `LLM_COMPLETION`: LLM text completion
- `VISION_AI`: Image analysis (future)
- `IMAGE_GENERATION`: Image creation (future)

### Data Operations
- `DATA_TRANSFORM`: JSON data transformation
- `CONDITIONAL`: Conditional branching (future)

### Integration
- `HTTP_REQUEST`: HTTP API calls (future)
- `CUSTOM_SERVICE`: Generic gRPC service calls

## Usage

### 1. Start the Service

```bash
# Using centralized Python runner
build/python/run.py services/dag-service/main.py

# Or directly (after proto generation)
cd services/dag-service && python main.py
```

### 2. Generate Proto Clients

```bash
# Generate all proto clients including DAG service
make generate

# Or generate specific clients
make generate-clients
```

### 3. Create a Voice Pipeline DAG

```python
import grpc
from unhinged_proto_clients import dag_service_pb2, dag_service_pb2_grpc

# Connect to DAG service
channel = grpc.insecure_channel('localhost:9096')
stub = dag_service_pb2_grpc.DAGServiceStub(channel)

# Create DAG definition
dag = dag_service_pb2.DAG()
dag.name = "Voice Pipeline"
dag.description = "Voice input to voice output"

# Add STT node
stt_node = dag.nodes.add()
stt_node.node_id = "stt1"
stt_node.type = dag_service_pb2.SPEECH_TO_TEXT
stt_node.config.update({"model": "whisper", "service_endpoint": "localhost:9091"})

# Add LLM node
llm_node = dag.nodes.add()
llm_node.node_id = "llm1"
llm_node.type = dag_service_pb2.LLM_CHAT
llm_node.config.update({"model": "llama3", "service_endpoint": "localhost:9095"})

# Add TTS node
tts_node = dag.nodes.add()
tts_node.node_id = "tts1"
tts_node.type = dag_service_pb2.TEXT_TO_SPEECH
tts_node.config.update({"voice": "nova", "service_endpoint": "localhost:9092"})

# Connect nodes with edges
edge1 = dag.edges.add()
edge1.source_node_id = "stt1"
edge1.target_node_id = "llm1"

edge2 = dag.edges.add()
edge2.source_node_id = "llm1"
edge2.target_node_id = "tts1"

# Create DAG
request = dag_service_pb2.CreateDAGRequest(dag=dag)
response = stub.CreateDAG(request)
dag_id = response.dag_id
```

### 4. Execute the DAG

```python
# Execute DAG
exec_request = dag_service_pb2.ExecuteDAGRequest()
exec_request.dag_id = dag_id
exec_request.input_data.update({"audio_file": "input.wav"})

exec_response = stub.ExecuteDAG(exec_request)
execution_id = exec_response.execution_id

# Stream execution events
stream_request = dag_service_pb2.StreamExecutionRequest(execution_id=execution_id)
for event in stub.StreamExecution(stream_request):
    print(f"Event: {event.event_type} - Node: {event.node_id}")
```

## Testing

### Run Unit Tests

```bash
# Run DAG service tests
build/python/run.py services/dag-service/test_dag_service.py
```

### Test Voice Pipeline

The test suite includes:
- DAG creation and validation
- Node execution simulation
- Event streaming
- Error handling

## Configuration

### Environment Variables

- `REDIS_HOST`: Redis host for session storage (default: localhost)
- `DAG_SERVICE_PORT`: Service port (default: 9096)

### Node Configuration

Each node type accepts specific configuration in the `config` field:

```json
{
  "SPEECH_TO_TEXT": {
    "model": "whisper-large-v3",
    "language": "auto",
    "service_endpoint": "localhost:9091"
  },
  "LLM_CHAT": {
    "model": "llama3.1:8b",
    "temperature": 0.7,
    "service_endpoint": "localhost:9095"
  },
  "TEXT_TO_SPEECH": {
    "voice": "nova",
    "speed": 1.0,
    "service_endpoint": "localhost:9092"
  }
}
```

## Integration with Frontend

The DAG service is designed to work with the GTK4 Graph Editor component:

1. **Graph Editor** creates DAG definitions visually
2. **DAG Service** executes workflows and streams progress
3. **Real-time Updates** via gRPC streaming show execution status

## Service Health

The service provides standard health checks:

```bash
# Check service health
grpcurl -plaintext localhost:9096 unhinged.dag.v1.DAGService/HealthCheck
```

## Monitoring

The service emits structured events for:
- DAG creation/deletion
- Execution start/completion
- Node execution progress
- Error conditions

Events are logged using the centralized event system and can be monitored via the dashboard.

## Next Steps

1. **Enhanced Node Types**: Add vision AI and image generation nodes
2. **Conditional Logic**: Implement branching and loops
3. **Data Flow**: Improve edge-based data passing
4. **Persistence**: Add DAG and execution persistence
5. **Scheduling**: Add cron-based DAG triggers
6. **UI Integration**: Connect with GTK4 Graph Editor
