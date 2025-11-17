# LLM Model Management for Unhinged

**Status**: ✅ COMPLETE  
**Commit**: `1927301`  
**Architecture**: On-Premise, Mobile-Optimized  
**Default Model**: Mistral 7B (3.5GB)  
**Minimum Target**: Google Pixel 9XL (4GB RAM)

## Overview

Unhinged uses **local LLM inference** via Ollama for all reasoning operations. Models are downloaded during initial setup and cached locally. No external API calls.

## Model Specifications

### Mistral 7B (Recommended)
- **Size**: 3.5GB (quantized Q4_K_M)
- **RAM Required**: 4GB
- **Speed**: Fast reasoning
- **Quality**: Good
- **Target Device**: Google Pixel 9XL, desktop
- **Use Case**: Default for reasoning engine

### Llama 2 7B (Alternative)
- **Size**: 3.8GB (quantized Q4_0)
- **RAM Required**: 4GB
- **Speed**: Moderate
- **Quality**: General purpose
- **Use Case**: Fallback option

### Neural Chat 7B (Alternative)
- **Size**: 3.8GB
- **RAM Required**: 4GB
- **Speed**: Fast
- **Quality**: Conversational
- **Use Case**: Chat-focused tasks

## Setup & Installation

### Automatic (Recommended)
```bash
# During initial setup
python3 build/python/setup.py

# This automatically:
# 1. Checks if Ollama is running
# 2. Downloads recommended models
# 3. Verifies model availability
```

### Manual Download
```bash
# List available models
python3 build/tools/download-llm-models.py --list

# Download specific model
python3 build/tools/download-llm-models.py --model mistral

# Download all recommended models
python3 build/tools/download-llm-models.py --recommended
```

## Deployment Scenarios

### Desktop Development
```bash
# Start Ollama container
docker-compose up llm

# Models auto-download on first run
unhinged orchestrate solve --explain "..."
```

### Mobile (Pixel 9XL)
```bash
# Alpine custom image at /vm
# Mistral 7B fits in 4GB RAM
# Models pre-cached in image
```

### Production
```bash
# Same as desktop
# Models cached in persistent volume
# No re-download on restart
```

## Architecture

```
Reasoning Engine
    ↓
TextGenerationService
    ↓
Ollama (localhost:1500)
    ↓
Local Model (Mistral)
    ↓
On-Premise Inference
```

## Troubleshooting

### Model Not Found
```
Error: model 'mistral' not found (status code: 404)
```
**Solution**: Download model
```bash
python3 build/tools/download-llm-models.py --model mistral
```

### Ollama Not Running
```
Error: Ollama service not running at localhost:1500
```
**Solution**: Start container
```bash
docker-compose up llm
```

### Disk Space Issues
- Mistral: 3.5GB
- Llama2: 3.8GB
- Neural Chat: 3.8GB
- Total: ~11GB for all models

## System Engineer Perspective

✅ **Sovereign Computation**: All inference local  
✅ **No Vendor Lock-in**: Open-source models  
✅ **No API Keys**: No external dependencies  
✅ **Mobile-First**: Optimized for 4GB RAM  
✅ **Offline Capable**: Works without internet  
✅ **Reproducible**: Same model, same results  

## Next Steps

- Alpine custom image with pre-cached models
- Model quantization optimization
- Multi-model inference pipeline

