# Unhinged Generate Command

Headless image and video generation for the Unhinged platform. Designed to be layered with GTK4 UI later.

## Quick Start

### Image Generation
```bash
# Basic usage
./unhinged generate image stable-diffusion "a beautiful landscape"

# With options
./unhinged generate image sdxl "portrait" --steps 40 --guidance 7.5

# Custom resolution
./unhinged generate image stable-diffusion "abstract art" --width 768 --height 768

# With seed for reproducibility
./unhinged generate image stable-diffusion "landscape" --seed 42

# JSON output for scripting
./unhinged generate image stable-diffusion "landscape" --format json
```

### Video Generation
```bash
# Basic usage
./unhinged generate video stable-diffusion "sunset over ocean"

# Custom duration and fps
./unhinged generate video svd "dancing figure" --duration 60 --fps 30
```

## Architecture

### Headless-First Design
- **No UI dependencies** - Pure Python CLI
- **Layerable** - GTK4 UI calls these commands
- **Scriptable** - JSON output for automation
- **Reusable** - `/libs/services/ImageGenerationService` is the core

### Command Structure
```
./unhinged generate [image|video] [model] [prompt] [options]
                    ↓
                    control/generate_cli.py
                    ↓
                    libs/services/ImageGenerationService
                    ↓
                    Diffusers (PyTorch)
```

## Image Models

| Model | Speed | Quality | VRAM | Resolution |
|-------|-------|---------|------|------------|
| stable-diffusion | 10-15s | Good | 4GB | 512x512 |
| sdxl | 30-40s | Excellent | 8GB | 1024x1024 |
| flux | 20-30s | State-of-art | 24GB | 1024x1024 |

## Image Options

```
--steps NUM              Number of inference steps (default: 20)
--guidance FLOAT        Guidance scale (default: 7.5)
--height PIXELS         Image height (default: 512)
--width PIXELS          Image width (default: 512)
--seed SEED             Random seed (optional)
--format {json,text}    Output format (default: text)
```

## Video Models

| Model | Approach | Speed | Quality |
|-------|----------|-------|---------|
| stable-diffusion | Frame interpolation | ~30s | Good |
| frame-interp | RIFE interpolation | ~30s | Good |
| svd | Stable Video Diffusion | ~60s | Excellent |

## Video Options

```
--duration SECONDS      Video duration (default: 30)
--fps FPS              Frames per second (default: 24)
--format {json,text}   Output format (default: text)
```

## Output

Generated files are saved to:
```
/build/tmp/generated_images/
```

Filenames follow the pattern:
```
generated_YYYYMMDD_HHMMSS.png
generated_YYYYMMDD_HHMMSS.mp4
```

## Integration with GTK4 UI

The OS Chatroom view can call these commands directly:

```python
# In chatroom_view.py
import subprocess
import json

result = subprocess.run([
    "./unhinged", "generate", "image", "stable-diffusion",
    "a beautiful landscape",
    "--format", "json"
], capture_output=True, text=True)

data = json.loads(result.stdout)
image_path = data["image_path"]
```

## Man Page

View the full man page:
```bash
man ./man/man1/unhinged-generate.1
```

Or:
```bash
./unhinged generate help
```

## Examples

### Generate and save with metadata
```bash
./unhinged generate image stable-diffusion "sunset" --format json > result.json
cat result.json | jq '.image_path'
```

### Batch generation
```bash
for prompt in "landscape" "portrait" "abstract"; do
  ./unhinged generate image stable-diffusion "$prompt"
done
```

### High-quality generation
```bash
./unhinged generate image sdxl "professional portrait" \
  --steps 40 \
  --guidance 7.5 \
  --width 1024 \
  --height 1024
```

### Reproducible generation
```bash
# Generate same image twice
./unhinged generate image stable-diffusion "landscape" --seed 12345
./unhinged generate image stable-diffusion "landscape" --seed 12345
```

## Implementation Details

### Files
- `control/generate_cli.py` - CLI implementation
- `libs/services/image_generation_service.py` - Core generation logic
- `man/man1/unhinged-generate.1` - Man page
- `unhinged` - Main entry point (updated)

### Design Principles
1. **Headless first** - No UI dependencies
2. **Python homogenous** - Pure Python, no microservices
3. **Layerable** - GTK4 UI calls these commands
4. **Reusable** - Services are importable libraries
5. **Simple** - Start with Stable Diffusion, add models later

## Future Enhancements

### Phase 1: Model Switching
- [ ] Add model_id parameter to ImageGenerationService
- [ ] Implement SDXL pipeline loading
- [ ] Add quality presets (draft/standard/high/ultra)

### Phase 2: YOLO Integration
- [ ] Add `/analyze` command for screenshot analysis
- [ ] Integrate YOLOv8 for GUI element detection
- [ ] Screenshot-to-image workflow

### Phase 3: Video Generation
- [ ] Implement frame interpolation pipeline
- [ ] Add Stable Video Diffusion support
- [ ] Video metadata (duration, fps, codec)

## Troubleshooting

### "ModuleNotFoundError: No module named 'torch'"
Install dependencies:
```bash
pip install torch diffusers transformers
```

### "CUDA out of memory"
Use CPU instead:
```bash
CUDA_VISIBLE_DEVICES="" ./unhinged generate image stable-diffusion "prompt"
```

Or reduce resolution:
```bash
./unhinged generate image stable-diffusion "prompt" --width 256 --height 256
```

### "No GPU detected"
The system will automatically fall back to CPU. Generation will be slower.

## Performance Targets

- Image generation: <20s (SD1.5), <60s (SDXL)
- Video generation: <2 minutes (30 seconds)
- Memory: <16GB on RTX 3080
- No UI blocking during generation

