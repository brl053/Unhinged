# Hardware Specification - Unhinged Workstation

## GPU (Primary Compute)

**Model**: NVIDIA GeForce RTX 5070 Ti
- **Memory**: 16.3 GB GDDR7
- **Compute Capability**: 12.0 (Ada architecture)
- **CUDA Cores**: 4,480
- **Tensor Cores**: 560
- **Memory Bandwidth**: 576 GB/s
- **Power**: 300W TDP

**Software Stack**:
- Driver: 570.195.03
- CUDA: 12.8
- cuDNN: 8.9.2

**Status**: ✅ Fully Operational (14.6 GB free at idle)

## CPU (Host Compute)

**Model**: AMD Ryzen 9 9950X 16-Core Processor
- **Cores**: 16 physical cores
- **Threads**: 32 logical threads (2 per core)
- **Base Clock**: 4.3 GHz
- **Boost Clock**: 5.7 GHz
- **TDP**: 170W
- **Cache**: 128 MB L3
- **Architecture**: Zen 5

**Status**: ✅ Fully Operational (57% current load)

## System RAM

- **Total**: 60 GB DDR5
- **Used**: 7.5 GB
- **Available**: 52 GB
- **Free**: 10 GB

**Status**: ✅ Plenty Available

## Storage

- **Device**: /dev/nvme0n1p6 (NVMe SSD)
- **Total**: 894 GB
- **Used**: 540 GB (60%)
- **Available**: 310 GB (35%)
- **Speed**: ~7,000 MB/s

**Status**: ✅ Adequate Space

## Software Stack

- **Python**: 3.12.3
- **PyTorch**: 2.9.0 (CUDA 12.8)
- **cuDNN**: 8.9.2
- **Diffusers**: Latest (Hugging Face)
- **Transformers**: Latest (Hugging Face)

## Performance Profile

### Compute Power

| Component | Peak Performance | Notes |
|-----------|-----------------|-------|
| GPU FP32 | ~14.4 TFLOPS | Single precision |
| GPU Tensor | ~115 TFLOPS | With sparsity |
| CPU | ~1.8 TFLOPS | 32 threads × 5.7 GHz |
| **Ratio** | **GPU 64x faster** | For AI workloads |

### Memory Bandwidth

| Component | Bandwidth | Notes |
|-----------|-----------|-------|
| GPU | 576 GB/s | GDDR7 |
| CPU | ~200 GB/s | DDR5 |
| **Ratio** | **GPU 3x faster** | Memory access |

## Workload Suitability

✅ **Excellent For**:
- Image generation (Stable Diffusion)
- Video processing
- Deep learning inference
- Batch processing
- Real-time AI

⚠️ **Adequate For**:
- Multi-threaded CPU tasks
- Large dataset processing
- Model training

## Current Allocation (Video Generation)

### GPU Usage
- Model Loading: ~4-5 GB
- Inference Buffer: ~3-4 GB per image
- Optimization: ~1-2 GB
- **Total**: ~8-10 GB (out of 16.3 GB)
- **Headroom**: ~6-8 GB ✅

### CPU Usage
- Python Process: ~500 MB
- TTS Generation: ~200-300 MB
- Script Parsing: ~50 MB
- **Total**: ~1 GB (out of 60 GB)
- **Headroom**: ~59 GB ✅

### Storage Usage
- Per image: ~1-2 MB
- Per voiceover: ~30-50 KB
- Per generation: ~1-5 KB metadata
- **Status**: ✅ No constraints

## Conclusion

This is a **high-end workstation** perfectly suited for AI image/video generation. The RTX 5070 Ti provides excellent GPU acceleration, and the Ryzen 9 9950X offers strong CPU support. Current allocation is efficient with good headroom for scaling.

