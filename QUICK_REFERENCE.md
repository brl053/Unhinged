# Unhinged Generate Command - Quick Reference

## Basic Commands

```bash
# Image generation
./unhinged generate image stable-diffusion "a beautiful landscape"
./unhinged generate image sdxl "portrait" --steps 40
./unhinged generate image flux "abstract art" --width 1024 --height 1024

# Video generation
./unhinged generate video stable-diffusion "sunset"
./unhinged generate video svd "dancing" --duration 60

# Help
./unhinged generate help
./unhinged generate image --help
./unhinged generate video --help
man ./man/man1/unhinged-generate.1
```

## Image Models

| Model | Speed | Quality | VRAM | Resolution |
|-------|-------|---------|------|------------|
| stable-diffusion | 10-15s | Good | 4GB | 512x512 |
| sdxl | 30-40s | Excellent | 8GB | 1024x1024 |
| flux | 20-30s | State-of-art | 24GB | 1024x1024 |

## Image Options

```
--steps NUM              Inference steps (default: 20)
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

## Common Examples

```bash
# Fast generation
./unhinged generate image stable-diffusion "landscape"

# High quality
./unhinged generate image sdxl "portrait" --steps 40 --guidance 7.5

# Custom resolution
./unhinged generate image stable-diffusion "art" --width 768 --height 768

# Reproducible
./unhinged generate image stable-diffusion "landscape" --seed 42

# JSON output
./unhinged generate image stable-diffusion "landscape" --format json

# Video
./unhinged generate video stable-diffusion "sunset"

# Long video
./unhinged generate video svd "dancing" --duration 60 --fps 30
```

## Output Location

```
/build/tmp/generated_images/
```

Filenames: `generated_YYYYMMDD_HHMMSS.png` or `.mp4`

## Integration with GTK4

```python
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

## Troubleshooting

| Problem | Solution |
|---------|----------|
| ModuleNotFoundError: torch | `pip install torch diffusers transformers` |
| CUDA out of memory | Use CPU: `CUDA_VISIBLE_DEVICES="" ./unhinged generate ...` |
| Slow generation | Use smaller model or resolution |
| Command not found | Make sure you're in project root |

## Files

| File | Purpose |
|------|---------|
| `control/generate_cli.py` | CLI implementation |
| `libs/services/image_generation_service.py` | Core generation |
| `man/man1/unhinged-generate.1` | Man page |
| `unhinged` | Main entry point |
| `GENERATE_COMMAND.md` | Full guide |
| `GTK4_INTEGRATION_GUIDE.md` | UI integration |

## Architecture

```
./unhinged generate [image|video] [model] [prompt] [options]
    ↓
control/generate_cli.py
    ↓
libs/services/ImageGenerationService
    ↓
Diffusers + PyTorch
    ↓
/build/tmp/generated_images/
```

## Key Features

✓ Headless - No UI dependencies
✓ Layerable - GTK4 UI calls these commands
✓ Reusable - Services are importable libraries
✓ Python homogenous - No microservices
✓ Simple - Start with Stable Diffusion, add models later
✓ Scriptable - JSON output for automation

## Next Steps

1. **Model Switching** - Add SDXL support
2. **YOLO Analysis** - Screenshot analysis
3. **Video Generation** - Frame interpolation
4. **GTK4 Integration** - Update OS Chatroom

See `IMPLEMENTATION_SUMMARY.md` for details.

