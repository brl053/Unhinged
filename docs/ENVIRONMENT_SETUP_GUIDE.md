# Python Environment Setup Guide

## Overview

This guide explains how to properly set up the Python environment for Unhinged, particularly for GPU-accelerated image generation using Stable Diffusion on RTX 5070 Ti.

## System Requirements

- **GPU**: NVIDIA RTX 5070 Ti (16GB VRAM)
- **Driver**: 570.195.03-open (open-source kernel modules)
- **CUDA**: 12.8
- **Python**: 3.12.3
- **OS**: Ubuntu/Linux with kernel 6.14.0-1015-oem or later

## Quick Setup

### 1. Create Virtual Environment

```bash
cd /home/e-bliss-station-1/Projects/Unhinged
python3 -m venv .venv --clear
```

### 2. Activate Virtual Environment

```bash
source .venv/bin/activate
```

### 3. Install PyTorch with CUDA 12.8 Support

```bash
.venv/bin/pip install torch torchvision torchaudio \
  --index-url https://download.pytorch.org/whl/cu128
```

**Important**: Use the official PyTorch index for CUDA 12.8 wheels. This ensures compatibility with your RTX 5070 Ti.

### 4. Install Image Generation Stack

```bash
.venv/bin/pip install diffusers transformers safetensors accelerate \
  huggingface-hub omegaconf scipy matplotlib tqdm
```

**Note**: xformers is NOT included. While it provides memory optimizations, the prebuilt wheels are incompatible with PyTorch 2.9.0+cu128. Diffusers works fine without it (just slower). If you need xformers, you must build it from source for your specific PyTorch version.

## Dependency Resolution

### PyTorch Version

- **Current**: 2.9.0+cu128
- **Reason**: Latest stable version with CUDA 12.8 support
- **Compatibility**: Works with RTX 5070 Ti (Blackwell architecture)

### Key Packages

| Package | Version | Purpose |
|---------|---------|---------|
| torch | 2.9.0+cu128 | GPU tensor operations |
| torchvision | 0.24.0+cu128 | Image processing utilities |
| torchaudio | 2.9.0+cu128 | Audio processing |
| diffusers | 0.35.2+ | Stable Diffusion pipeline |
| transformers | 4.57.1+ | CLIP text encoder |
| safetensors | 0.6.2+ | Efficient model loading |
| accelerate | 1.11.0+ | Memory management |

### Known Issues & Solutions

#### Issue: xformers Import Error

**Symptom**: `ImportError: undefined symbol: _ZNK3c106SymInt6sym_neERKS0_`

**Root Cause**: xformers 0.0.32.post2 was built for PyTorch 2.8.0, not 2.9.0

**Solution**: Remove xformers from requirements. Diffusers gracefully falls back to standard attention (slower but functional).

```bash
pip uninstall xformers -y
```

#### Issue: Externally-Managed Environment

**Symptom**: `error: externally-managed-environment`

**Root Cause**: System Python is protected by PEP 668

**Solution**: Always use the virtual environment:

```bash
source .venv/bin/activate
```

## Verification

### Test GPU Access

```bash
python3 << 'EOF'
import torch
print(f"PyTorch: {torch.__version__}")
print(f"CUDA Available: {torch.cuda.is_available()}")
print(f"GPU: {torch.cuda.get_device_name(0)}")
EOF
```

Expected output:
```
PyTorch: 2.9.0+cu128
CUDA Available: True
GPU: NVIDIA GeForce RTX 5070 Ti
```

### Test Image Generation

```bash
python3 << 'EOF'
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from libs.services import ImageGenerationService

service = ImageGenerationService()
result = service.generate_image(
    prompt="a serene mountain landscape at sunset",
    num_inference_steps=20,
    height=512,
    width=512
)

print(f"✅ Image generated: {result['image_path']}")
print(f"   Time: {result['generation_time']:.2f}s")
EOF
```

## Performance Notes

- **First Run**: ~60-90 seconds (model download + compilation)
- **Subsequent Runs**: ~2-5 seconds per image (20 inference steps)
- **Memory Usage**: ~8-10GB VRAM (with float16 precision)
- **Optimization**: Lazy pipeline loading reduces startup time

## Troubleshooting

### CUDA Out of Memory

Reduce image size or inference steps:
```python
service.generate_image(
    prompt="...",
    num_inference_steps=15,  # Reduce from 20
    height=384,              # Reduce from 512
    width=384
)
```

### Slow Generation

This is expected without xformers. For faster generation, build xformers from source:
```bash
pip install xformers --no-binary xformers
```

### Model Download Issues

Models are cached in `~/.cache/huggingface/`. Clear cache if needed:
```bash
rm -rf ~/.cache/huggingface/hub/models--runwayml--stable-diffusion-v1-5
```

## References

- [PyTorch CUDA Installation](https://pytorch.org/get-started/locally/)
- [Diffusers Documentation](https://huggingface.co/docs/diffusers)
- [RTX 5070 Ti Specifications](https://www.nvidia.com/en-us/geforce/graphics-cards/50-series/)

