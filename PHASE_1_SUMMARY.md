# Phase 1: Model Switching - Implementation Summary

## ✅ Completed

### Multi-Model Support
- **Stable Diffusion v1.5**: 512x512, fast, 4GB VRAM
- **SDXL**: 1024x1024, high quality, 8GB VRAM
- Model selection via `--model` parameter

### Quality Presets
```
draft:    15 steps, 7.0 guidance, 50% resolution (fastest)
standard: 20 steps, 7.5 guidance, 100% resolution (default)
high:     30 steps, 8.0 guidance, 100% resolution
ultra:    50 steps, 8.5 guidance, 100% resolution (best quality)
```

### Parameter Overrides
- `--quality` - Select preset (draft/standard/high/ultra)
- `--steps` - Override inference steps
- `--guidance` - Override guidance scale
- `--height` - Override image height
- `--width` - Override image width
- `--seed` - Set random seed for reproducibility

## Files Modified

1. **libs/services/image_generation_service.py** (195 → 250 lines)
   - Added MODELS dict with configurations
   - Added QUALITY_PRESETS dict
   - Updated __init__ for model selection
   - Updated _load_pipeline() for multi-model support
   - Updated generate_image() for quality presets

2. **control/generate_cli.py** (150 lines)
   - Updated generate_image() method
   - Added quality parameter support
   - Updated argument parser

3. **unhinged** (bash script)
   - Updated help text
   - Updated examples

## Output Directory

```
/build/tmp/generated/
```

Generated files: `generated_YYYYMMDD_HHMMSS.png`

## Test Commands (Copy & Paste)

### Test 1: Basic Stable Diffusion
```bash
./unhinged generate image stable-diffusion "a serene mountain landscape at sunset"
```

### Test 2: SDXL Standard Quality
```bash
./unhinged generate image sdxl "a professional portrait of a person"
```

### Test 3: SDXL High Quality
```bash
./unhinged generate image sdxl "a detailed fantasy landscape" --quality high
```

### Test 4: SDXL Ultra Quality (Best)
```bash
./unhinged generate image sdxl "a beautiful abstract artwork" --quality ultra
```

### Test 5: Draft Quality (Fastest)
```bash
./unhinged generate image stable-diffusion "a quick sketch" --quality draft
```

### Test 6: Custom Resolution
```bash
./unhinged generate image sdxl "a portrait" --quality high --width 768 --height 768
```

### Test 7: Reproducible (Same Seed)
```bash
./unhinged generate image stable-diffusion "a landscape" --seed 42
```

### Test 8: JSON Output
```bash
./unhinged generate image stable-diffusion "a landscape" --format json
```

### Test 9: Override Steps
```bash
./unhinged generate image sdxl "a portrait" --quality high --steps 40
```

### Test 10: Benchmark Comparison
```bash
./unhinged generate image stable-diffusion "a landscape" --quality draft
./unhinged generate image stable-diffusion "a landscape" --quality standard
./unhinged generate image stable-diffusion "a landscape" --quality high
```

## Expected Performance

| Model | Quality | Time | VRAM |
|-------|---------|------|------|
| SD1.5 | draft | ~8s | 3GB |
| SD1.5 | standard | ~10s | 4GB |
| SD1.5 | high | ~15s | 4GB |
| SD1.5 | ultra | ~25s | 4GB |
| SDXL | draft | ~20s | 6GB |
| SDXL | standard | ~30s | 8GB |
| SDXL | high | ~45s | 8GB |
| SDXL | ultra | ~75s | 8GB |

## Verification

Check that everything is working:
```bash
# Show help
./unhinged generate image --help

# Check output directory exists
ls -lh /build/tmp/generated/

# Verify syntax
python3 -m py_compile libs/services/image_generation_service.py
python3 -m py_compile control/generate_cli.py
```

## Architecture

```
./unhinged generate image [model] [prompt] [options]
    ↓
control/generate_cli.py
    ↓
ImageGenerationService(model="stable-diffusion" or "sdxl")
    ↓
StableDiffusionPipeline or StableDiffusionXLPipeline
    ↓
/build/tmp/generated/generated_YYYYMMDD_HHMMSS.png
```

## Key Features

✅ Multi-model support (SD1.5, SDXL)
✅ Quality presets (draft/standard/high/ultra)
✅ Parameter overrides
✅ Reproducible generation (seed)
✅ JSON output for scripting
✅ Automatic GPU/CPU fallback
✅ Memory optimization (attention slicing)

## Next Phase

**Phase 2: YOLO Integration** (Week 2)
- Add `/analyze` command for screenshot analysis
- Integrate YOLOv8 for GUI element detection
- Train on GTK4 components
- Screenshot-to-image workflow

## Troubleshooting

### Dependencies
```bash
pip install torch diffusers transformers
```

### CUDA Out of Memory
```bash
CUDA_VISIBLE_DEVICES="" ./unhinged generate image stable-diffusion "prompt"
```

### Use Smaller Model
```bash
./unhinged generate image stable-diffusion "prompt" --quality draft
```

## Notes

- First run downloads model (~4GB for SD1.5, ~7GB for SDXL)
- Models are cached for subsequent runs
- Output directory is `/build/tmp/generated/`
- All timestamps are in YYYYMMDD_HHMMSS format

