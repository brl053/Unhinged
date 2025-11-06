# Unhinged Service Architecture Guide

## System Overview

The Unhinged platform is a multi-layered system for GPU-accelerated image generation with a GTK4 desktop interface. The architecture follows a clean separation of concerns with distinct layers for UI, services, backend processing, and infrastructure.

## Architecture Layers

### Layer 1: User Interface (GTK4)
**Location**: `control/gtk4_gui/`

Provides native GNOME desktop experience with:
- Main application window (`desktop_app.py`)
- Tabbed interface with multiple views
- Chatroom view with `/image` command support
- Real-time status updates and progress indication

**Key Entry Point**: `/image <prompt>` command in chatroom

### Layer 2: Service Abstraction (libs/services)
**Location**: `libs/services/`

Provides reusable service implementations:
- `ImageGenerationService`: GPU-accelerated image generation
- Lazy pipeline loading for memory efficiency
- Benchmark tracking and statistics
- Output management to `/build/tmp/generated_images/`

**Import Pattern**:
```python
from libs.services import ImageGenerationService
```

### Layer 3: Backend Services
**Location**: `services/`

Two implementation options:

**Option A: gRPC Service** (Recommended for production)
- Port: 9094
- Location: `services/image-generation/`
- Protocol: gRPC with streaming support
- Health checks: Implements `health.proto`
- Advantages: Language-agnostic, streaming, scalable

**Option B: REST API** (Alternative)
- Location: `services/image_gen_service.py`
- Framework: FastAPI
- Advantages: Simple HTTP, easy debugging

### Layer 4: ML Pipeline
**Location**: `build/modules/image_generation.py`

Core image generation logic:
- `SovereignImageGenerator`: Direct metal image generation
- Model: Stable Diffusion XL (production) or v1.5 (fast)
- Device: CUDA (GPU) or CPU fallback
- Optimization: float16 precision, attention slicing, xformers

### Layer 5: Infrastructure
**Location**: `libs/`

Supporting systems:
- **Event Framework** (`libs/event-framework/`): Centralized logging
- **Service Framework** (`libs/service-framework/`): Timeout configuration
- **Proto Definitions** (`proto/`): gRPC service contracts
- **Design System** (`libs/design_system/`): UI components

## Data Flow: /image Command

```
1. User types: /image a rubber duck in a bathtub
                    ↓
2. Chatroom View parses command
                    ↓
3. Spawns background thread
                    ↓
4. Imports ImageGenerationService from libs.services
                    ↓
5. Creates service instance
                    ↓
6. Calls generate_image(prompt, steps, guidance, height, width)
                    ↓
7. Service loads Stable Diffusion pipeline (lazy)
                    ↓
8. Generates image on GPU (RTX 5070 Ti)
                    ↓
9. Saves to /build/tmp/generated_images/
                    ↓
10. Returns result with metadata
                    ↓
11. UI displays image and stats
```

## Service Communication Patterns

### Pattern 1: Direct Python Import (Current)
**Used by**: GTK4 UI → Image Generation Service

```python
from libs.services import ImageGenerationService
service = ImageGenerationService()
result = service.generate_image(prompt="...")
```

**Pros**: Simple, no network overhead, fast
**Cons**: Tight coupling, requires same Python environment

### Pattern 2: gRPC (Recommended for Services)
**Used by**: Service-to-service communication

```python
import grpc
from unhinged_proto_clients import image_generation_pb2_grpc

channel = grpc.aio.secure_channel('localhost:9094', ...)
stub = image_generation_pb2_grpc.ImageGenerationServiceStub(channel)
response = stub.GenerateImage(request)
```

**Pros**: Language-agnostic, streaming, health checks
**Cons**: Network overhead, requires proto compilation

### Pattern 3: REST API (Alternative)
**Used by**: External clients, simple HTTP

```python
import requests
response = requests.post('http://localhost:8080/generate', json={
    'prompt': '...',
    'steps': 20
})
```

**Pros**: Simple HTTP, easy debugging
**Cons**: No streaming, less efficient

## Configuration & Deployment

### Development Mode
```bash
# Direct Python import (current)
python3 -m control.gtk4_gui.launch
```

### Production Mode (Future)
```bash
# Start gRPC service
python3 services/image-generation/main.py

# Start UI (connects via gRPC)
python3 -m control.gtk4_gui.launch
```

## Key Files Reference

| File | Purpose |
|------|---------|
| `control/gtk4_gui/desktop_app.py` | Main UI application |
| `control/gtk4_gui/views/chatroom_view.py` | Chat interface with `/image` command |
| `libs/services/__init__.py` | Service package initialization |
| `libs/services/image_generation_service.py` | Image generation service |
| `services/image-generation/main.py` | gRPC service launcher |
| `services/image-generation/grpc_server.py` | gRPC server implementation |
| `build/modules/image_generation.py` | Core ML pipeline |
| `proto/image_generation.proto` | gRPC service definition |

## Environment Setup

### Required Dependencies
```bash
# Core ML stack
pip install torch torchvision
pip install diffusers transformers
pip install safetensors pillow

# UI framework
pip install PyGObject Adwaita

# gRPC (optional)
pip install grpcio protobuf
```

### GPU Configuration
- **Device**: NVIDIA RTX 5070 Ti (16GB VRAM)
- **Driver**: 570.195.03-open
- **CUDA**: 12.8
- **PyTorch**: With CUDA support

## Troubleshooting

### Import Error: "No module named 'image_generation_service'"
**Solution**: Ensure `libs/services/__init__.py` exists and use proper import:
```python
from libs.services import ImageGenerationService
```

### GPU Not Detected
**Check**: `torch.cuda.is_available()` returns False
**Solution**: Verify NVIDIA drivers and CUDA installation

### Out of Memory
**Solution**: Reduce image size or use smaller model (v1.5 instead of XL)

### Slow Generation
**Solution**: Enable xformers optimization in config

## Future Enhancements

1. **Service Scaling**: Deploy multiple gRPC instances
2. **Model Selection**: UI for choosing different models
3. **Batch Processing**: Queue multiple generation requests
4. **Result Caching**: Cache generated images by prompt
5. **Remote Services**: Connect to remote image generation services

