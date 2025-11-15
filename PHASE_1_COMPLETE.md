# Phase 1: Model Switching - COMPLETE ✅

## What Was Implemented

### 1. Multi-Model Support
- ✅ Stable Diffusion v1.5 (512x512, fast)
- ✅ SDXL (1024x1024, high quality)
- ✅ Model selection via CLI parameter

### 2. Quality Presets
- ✅ **draft**: 15 steps, 7.0 guidance, 50% resolution
- ✅ **standard**: 20 steps, 7.5 guidance, 100% resolution (default)
- ✅ **high**: 30 steps, 8.0 guidance, 100% resolution
- ✅ **ultra**: 50 steps, 8.5 guidance, 100% resolution

### 3. Parameter Overrides
- ✅ `--steps` - Override inference steps
- ✅ `--guidance` - Override guidance scale
- ✅ `--height` - Override image height
- ✅ `--width` - Override image width
- ✅ `--seed` - Set random seed for reproducibility

## Files Modified

1. **libs/services/image_generation_service.py**
   - Added MODELS dict with model configurations
   - Added QUALITY_PRESETS dict
   - Updated __init__ to accept model parameter
   - Updated _load_pipeline() for multi-model support
   - Updated generate_image() to use quality presets

2. **control/generate_cli.py**
   - Updated generate_image() method
   - Added quality parameter
   - Updated argument parser

3. **unhinged** (bash script)
   - Updated help text with quality presets
   - Updated examples

## Output Directory

All generated images are saved to:
```
/build/tmp/generated/
```

## Test Commands

### Test 1: Basic Stable Diffusion (Standard Quality)
```bash
./unhinged generate image stable-diffusion "a serene mountain landscape at sunset"
```

### Test 2: SDXL with Standard Quality
```bash
./unhinged generate image sdxl "a professional portrait of a person"
```

### Test 3: High Quality SDXL
```bash
./unhinged generate image sdxl "a detailed fantasy landscape" --quality high
```

### Test 4: Ultra Quality SDXL (Slow but Best)
```bash
./unhinged generate image sdxl "a beautiful abstract artwork" --quality ultra
```

### Test 5: Draft Quality (Fast)
```bash
./unhinged generate image stable-diffusion "a quick sketch" --quality draft
```

### Test 6: Custom Resolution
```bash
./unhinged generate image sdxl "a portrait" --quality high --width 768 --height 768
```

### Test 7: Reproducible Generation (Same Seed)
```bash
./unhinged generate image stable-diffusion "a landscape" --seed 42
./unhinged generate image stable-diffusion "a landscape" --seed 42
```

### Test 8: JSON Output for Scripting
```bash
./unhinged generate image stable-diffusion "a landscape" --format json
```

### Test 9: Override Steps and Guidance
```bash
./unhinged generate image sdxl "a portrait" --quality high --steps 40 --guidance 8.5
```

### Test 10: Benchmark Comparison
```bash
# Fast generation
./unhinged generate image stable-diffusion "a landscape" --quality draft

# Standard generation
./unhinged generate image stable-diffusion "a landscape" --quality standard

# High quality
./unhinged generate image stable-diffusion "a landscape" --quality high
```

## Expected Output

Each command will:
1. Display generation parameters
2. Generate the image on GPU/CPU
3. Save to `/build/tmp/generated/generated_YYYYMMDD_HHMMSS.png`
4. Display results (text or JSON format)

Example text output:
```
🎨 Generating image with stable-diffusion...
   Prompt: a serene mountain landscape at sunset
   Quality: standard
   Resolution: 512x512
✅ Image generated: /build/tmp/generated/generated_20251112_143022.png
   Generation time: 12.3s
   Model: stable-diffusion
   Device: cuda
```

Example JSON output:
```json
{
  "image_path": "/build/tmp/generated/generated_20251112_143022.png",
  "image_filename": "generated_20251112_143022.png",
  "prompt": "a serene mountain landscape at sunset",
  "generation_time": 12.3,
  "model": "stable-diffusion",
  "model_id": "runwayml/stable-diffusion-v1-5",
  "device": "cuda",
  "gpu_available": true,
  "quality": "standard",
  "num_inference_steps": 20,
  "guidance_scale": 7.5,
  "height": 512,
  "width": 512,
  "timestamp": "20251112_143022"
}
```

## Performance Targets

| Model | Quality | Steps | Time | VRAM |
|-------|---------|-------|------|------|
| SD1.5 | draft | 15 | ~8s | 3GB |
| SD1.5 | standard | 20 | ~10s | 4GB |
| SD1.5 | high | 30 | ~15s | 4GB |
| SD1.5 | ultra | 50 | ~25s | 4GB |
| SDXL | draft | 15 | ~20s | 6GB |
| SDXL | standard | 20 | ~30s | 8GB |
| SDXL | high | 30 | ~45s | 8GB |
| SDXL | ultra | 50 | ~75s | 8GB |

## Next Phase

**Phase 2: YOLO Integration** (Week 2)
- Add `/analyze` command for screenshot analysis
- Integrate YOLOv8 for GUI element detection
- Train on GTK4 components
- Screenshot-to-image workflow

## Troubleshooting

### "ModuleNotFoundError: No module named 'torch'"
```bash
pip install torch diffusers transformers
```

### "CUDA out of memory"
Use CPU:
```bash
CUDA_VISIBLE_DEVICES="" ./unhinged generate image stable-diffusion "prompt"
```

Or use smaller model:
```bash
./unhinged generate image stable-diffusion "prompt" --quality draft
```

### "Model not found"
First run will download the model (~4GB for SD1.5, ~7GB for SDXL). Be patient.

## Verification

To verify Phase 1 is working:
```bash
# Check help
./unhinged generate image --help

# Test basic generation
./unhinged generate image stable-diffusion "test"

# Check output directory
ls -lh /build/tmp/generated/
```

