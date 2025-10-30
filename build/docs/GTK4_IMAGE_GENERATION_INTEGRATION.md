# GTK4 GUI Image Generation Integration Plan

## Overview

This document outlines the integration plan for adding sovereign image generation capabilities to the existing GTK4 GUI system. The integration follows the established architecture patterns and provides a seamless user experience.

## 🎯 Integration Goals

1. **Seamless Integration** - Add image generation without disrupting existing functionality
2. **Consistent UX** - Follow established GTK4 GUI patterns and design system
3. **Service Architecture** - Integrate with the image generation service via REST API
4. **Real-time Feedback** - Provide progress updates and generation status
5. **Image Management** - Display, save, and manage generated images

## 🏗️ Architecture Integration

### Service Layer Integration

```
┌─────────────────────────────────────────────────────────────┐
│                    GTK4 GUI Application                     │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │   Audio Views   │  │  System Views   │  │ Image Gen   │  │
│  │                 │  │                 │  │    View     │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                Service Connector Layer                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │ Audio Services  │  │ System Services │  │ Image Gen   │  │
│  │   (gRPC)        │  │   (Various)     │  │ (gRPC)      │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                    gRPC Network Layer                       │
└─────────────────────────────────────────────────────────────┘
         │                        │                    │
         ▼                        ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ Speech Services │  │ System Services │  │ Image Gen gRPC  │
│   (gRPC:9091)   │  │   (Various)     │  │   (gRPC:9094)   │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

### Component Integration

The image generation components integrate with the existing component system:

```python
# In control/gtk4_gui/components/__init__.py
from .image_generation import ImageGenerationPanel, ImageGenerationView

# In control/gtk4_gui/views/__init__.py  
from .image_generation_view import ImageGenerationView
```

## 📦 New Components Added

### 1. ImageGenerationPanel
- **Location**: `control/gtk4_gui/components/image_generation.py`
- **Purpose**: Main UI for image generation parameters and controls
- **Features**:
  - Prompt and negative prompt input
  - Dimension controls (width/height)
  - Generation parameters (steps, guidance scale, seed)
  - Real-time generation progress
  - Results display with thumbnails

### 2. ImageGenerationView
- **Location**: `control/gtk4_gui/views/image_generation_view.py`
- **Purpose**: Scrollable container for the image generation panel
- **Integration**: Follows existing view pattern

### 3. ImageGenerationService
- **Location**: `control/gtk4_gui/services/image_generation_service.py`
- **Purpose**: Service connector for image generation API
- **Features**:
  - REST API communication
  - Async request handling
  - Error handling and retry logic

## 🔧 Implementation Steps

### Phase 1: Core Integration (Completed)
- ✅ Created `ImageGenerationPanel` component
- ✅ Created `ImageGenerationView` wrapper
- ✅ Implemented basic UI with all generation parameters
- ✅ Added progress indication and status updates

### Phase 2: Service Integration (Next)
1. **Create Service Connector**
   ```python
   # control/gtk4_gui/services/image_generation_service.py
   class ImageGenerationService:
       def __init__(self, base_url="http://localhost:8080"):
           self.base_url = base_url
       
       async def generate_image(self, request: ImageGenerationRequest):
           # REST API call to image generation service
   ```

2. **Update Service Configuration**
   ```python
   # control/gtk4_gui/config.py
   IMAGE_GENERATION_SERVICE_URL = os.getenv('IMAGE_GEN_URL', 'http://localhost:8080')
   ```

3. **Add to Main Application**
   ```python
   # control/gtk4_gui/desktop_app.py
   from .views.image_generation_view import ImageGenerationView
   
   # Add tab/page for image generation
   self.image_gen_view = ImageGenerationView()
   self.notebook.append_page(self.image_gen_view, Gtk.Label(label="Image Generation"))
   ```

### Phase 3: Advanced Features
1. **Image Display and Management**
   - Thumbnail generation
   - Full-size image viewer
   - Save/export functionality
   - Generation history

2. **Batch Generation**
   - Multiple prompt support
   - Queue management
   - Progress tracking for multiple images

3. **Model Management**
   - Model selection dropdown
   - Model status indicators
   - Model download progress

## 🎨 UI/UX Design

### Design System Integration
- Uses existing Adwaita components (`Adw.PreferencesGroup`, `Adw.ActionRow`)
- Follows established spacing and margin patterns
- Integrates with design system tokens from `generated/design_system/`

### User Flow
1. **Input Phase**: User enters prompt and adjusts parameters
2. **Generation Phase**: Progress indication with status updates
3. **Results Phase**: Display generated images with action buttons
4. **Management Phase**: Save, open, or regenerate images

### Accessibility
- Proper ARIA labels for all controls
- Keyboard navigation support
- Screen reader compatibility
- High contrast support

## 🔌 Service Communication

### gRPC Streaming Integration
```python
# Example gRPC call with streaming progress
from libs.python.grpc.client_factory import create_image_generation_client
from unhinged_proto_clients import image_generation_pb2

client = create_image_generation_client("localhost:9094")

request = image_generation_pb2.GenerateImageRequest()
request.prompt = "a rubber duck in a bathtub"
request.negative_prompt = "blurry, low quality"
request.width = 1024
request.height = 1024
request.num_inference_steps = 25
request.guidance_scale = 7.5

# Stream with real-time progress updates
for chunk in client.GenerateImage(request):
    if chunk.type == common_pb2.CHUNK_TYPE_PROGRESS:
        progress = dict(chunk.structured)
        print(f"Progress: {progress['progress_percent']:.1f}% - {progress['status_message']}")
    elif chunk.type == common_pb2.CHUNK_TYPE_DATA and chunk.is_final:
        result = dict(chunk.structured)
        print(f"Generated {result['image_count']} images in {result['generation_time']:.1f}s")
```

### Error Handling
- Network connectivity issues
- Service unavailable scenarios
- Generation failures
- Invalid parameter validation

## 🚀 Deployment Integration

### Docker Compose Integration
```yaml
# Add to existing docker-compose.yml
services:
  gtk4-gui:
    environment:
      - IMAGE_GEN_URL=http://image-generation:8080
    depends_on:
      - image-generation
  
  image-generation:
    # From build/ci/docker-compose.image-gen.yml
```

### Service Discovery
- Automatic detection of image generation service
- Fallback to disabled state if service unavailable
- Health check integration

## 📊 Performance Considerations

### Memory Management
- Thumbnail caching with size limits
- Image cleanup after display
- Progress bar updates without blocking UI

### Network Optimization
- Async API calls to prevent UI blocking
- Request queuing for multiple generations
- Timeout handling for long generations

## 🧪 Testing Strategy

### Unit Tests
- Component rendering tests
- Service communication tests
- Error handling tests

### Integration Tests
- Full generation workflow
- Service connectivity
- UI state management

### Manual Testing
- Generation with various parameters
- Error scenarios
- Performance with large images

## 📝 Configuration

### Environment Variables
```bash
# Image generation service
IMAGE_GEN_URL=http://localhost:8080
IMAGE_GEN_TIMEOUT=300
IMAGE_GEN_MAX_CONCURRENT=2

# UI settings
IMAGE_GEN_THUMBNAIL_SIZE=256
IMAGE_GEN_PREVIEW_SIZE=512
IMAGE_GEN_AUTO_SAVE=true
```

### User Preferences
- Default generation parameters
- Output directory preferences
- Model selection preferences

## 🎯 Success Metrics

1. **Functionality**: All generation parameters work correctly
2. **Performance**: UI remains responsive during generation
3. **Reliability**: Proper error handling and recovery
4. **Usability**: Intuitive interface following GTK4 patterns
5. **Integration**: Seamless fit with existing application

## 🔄 Future Enhancements

1. **Advanced Features**
   - Inpainting and outpainting
   - Style transfer
   - Image-to-image generation

2. **Workflow Integration**
   - Integration with other services
   - Batch processing workflows
   - Automated generation triggers

3. **Model Management**
   - Model switching
   - Custom model loading
   - Model performance monitoring

This integration plan provides a comprehensive roadmap for adding sovereign image generation capabilities to the GTK4 GUI while maintaining the existing architecture and user experience standards.
