# Image & Video Generation Implementation Roadmap

## Project Goals

### 1. Higher Fidelity Image Generation
**Current**: Stable Diffusion v1.5 (512x512, 20 steps)
**Target**: Comparable to DALL-E 3 / Midjourney quality

**Candidates**:
- **SDXL 1.0** (Stable Diffusion XL)
  - Pros: Better quality, 1024x1024 native, proven
  - Cons: ~8GB VRAM, slower (~30-40 seconds)
  - Status: Production-ready
  
- **Flux.1** (Black Forest Labs)
  - Pros: State-of-art quality, fast
  - Cons: ~24GB VRAM, newer/less tested
  - Status: Emerging
  
- **Kandinsky 3.0**
  - Pros: Good quality, efficient
  - Cons: Less community support
  - Status: Stable

**Recommendation**: Start with SDXL (proven, good balance)

### 2. YOLO-Based GUI Screenshot Analysis
**Purpose**: Analyze GTK4 GUI screenshots to understand layout/elements

**Implementation**:
```
Screenshot → YOLO Detection → Element Classification
    ↓
Detected: [buttons, text_fields, panels, icons]
    ↓
Generate images matching detected patterns
```

**Use Cases**:
- Generate UI mockups from screenshots
- Analyze existing GUI for design consistency
- Generate variations of detected elements
- Screenshot-to-image workflow

**YOLO Model Selection**:
- YOLOv8 (latest, best accuracy)
- YOLOv5 (proven, lighter)
- Custom fine-tuned model on GTK4 components

### 3. 30-Second Video Generation
**Target**: Establish video generation capability

**Approach** (simplest first):
1. **Frame Interpolation** (easiest)
   - Generate 2-3 keyframes
   - Interpolate between them
   - Combine into video
   - Tools: RIFE, DAIN

2. **Stable Video Diffusion** (medium)
   - Image-to-video pipeline
   - ~4-8 seconds per generation
   - Extend to 30s with looping/interpolation

3. **Full Video Diffusion** (hardest)
   - Text-to-video (Runway, Pika)
   - Requires significant VRAM
   - Slower generation

**Recommendation**: Start with Frame Interpolation + SVD

## Architecture Changes

### ImageGenerationService Enhancements
```python
class ImageGenerationService:
    # Current
    - generate_image(prompt, steps, guidance, height, width)
    
    # Enhanced
    - generate_image(..., model_id="sdxl")  # Model selection
    - generate_batch(prompts, model_id)     # Batch generation
    - generate_video(prompt, duration=30)   # Video generation
    - analyze_screenshot(image_path)        # YOLO analysis
```

### GeneratedArtifactWidget Extensions
```python
# Current: image only
artifact_type = "image"

# Enhanced
artifact_type in ["image", "video", "email", "code"]

# Video support
- Video player widget
- Duration/fps metadata
- Download button
```

### Proto Updates
```protobuf
// Add to image_generation.proto
service ImageGenerationService {
    // Existing
    rpc GenerateImage(GenerateImageRequest) returns (stream StreamChunk);
    
    // New
    rpc GenerateVideo(GenerateVideoRequest) returns (stream StreamChunk);
    rpc AnalyzeScreenshot(AnalyzeScreenshotRequest) returns (AnalysisResponse);
    rpc ListModels(ListModelsRequest) returns (ListModelsResponse);
}

message GenerateVideoRequest {
    string prompt = 1;
    int32 duration_seconds = 2;  // 30 for target
    int32 fps = 3;               // 24 or 30
    string model_id = 4;         // "svd" or "frame-interp"
}
```

## Implementation Phases

### Phase 1: Model Switching (Week 1)
- [ ] Add model_id parameter to generate_image()
- [ ] Implement SDXL pipeline loading
- [ ] Add quality presets (draft/standard/high)
- [ ] Update UI to show model selection
- [ ] Benchmark SDXL vs SD1.5

### Phase 2: YOLO Integration (Week 2)
- [ ] Integrate YOLOv8 for GUI analysis
- [ ] Create screenshot analysis endpoint
- [ ] Train/fine-tune on GTK4 components
- [ ] Add analysis results to chat
- [ ] Create screenshot-to-image workflow

### Phase 3: Video Generation (Week 3)
- [ ] Implement frame interpolation pipeline
- [ ] Add Stable Video Diffusion support
- [ ] Create video generation endpoint
- [ ] Extend GeneratedArtifactWidget for video
- [ ] Add video metadata (duration, fps, codec)

### Phase 4: Polish & Optimization (Week 4)
- [ ] Performance optimization
- [ ] Memory management improvements
- [ ] Error handling & recovery
- [ ] Documentation & examples
- [ ] User testing & feedback

## Dependencies to Add

```
# For SDXL
diffusers>=0.21.0  # Already have, update version
transformers>=4.30.0

# For YOLO
ultralytics>=8.0.0
opencv-python>=4.8.0

# For Video
imageio>=2.31.0
imageio-ffmpeg>=1.4.0
rife-ncnn-vulkan>=0.0.1  # For frame interpolation
```

## Testing Strategy

1. **Unit Tests**: Model loading, parameter validation
2. **Integration Tests**: End-to-end generation flows
3. **Performance Tests**: Generation time, memory usage
4. **Quality Tests**: Visual inspection, metrics
5. **UI Tests**: Widget rendering, error handling

## Success Metrics

- [ ] SDXL generates 1024x1024 images in <60 seconds
- [ ] YOLO detects GUI elements with >90% accuracy
- [ ] Video generation produces smooth 30-second clips
- [ ] All artifacts display correctly in chat
- [ ] No UI blocking during generation
- [ ] Memory usage stays <16GB on RTX 3080

