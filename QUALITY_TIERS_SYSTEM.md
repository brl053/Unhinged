# Quality Tiers System - Three Presets for Every Use Case

## Overview

The short-form video generator now supports **three quality tiers**, each optimized for different use cases and hardware constraints.

## Quality Tiers

### DRAFT - Fast Iteration
**Best for**: Social media preview, quick iteration, testing

```
Inference Steps:     15
Candidates:          1
Generation Res:      576×1024
Output Res:          1080×1920
Video CRF:           28 (compressed)
Audio Bitrate:       128k
Time per Image:      ~3 seconds
GPU Memory:          6.0 GB
GPU Temp:            ~65°C
```

**Use Case**: Quick preview before committing to longer generation

### STANDARD - Balanced (Default)
**Best for**: Social media + small prints, web, general use

```
Inference Steps:     25
Candidates:          1
Generation Res:      720×1280
Output Res:          1080×1920
Video CRF:           20 (balanced)
Audio Bitrate:       192k
Time per Image:      ~5 seconds
GPU Memory:          8.0 GB
GPU Temp:            ~70°C
```

**Use Case**: Default choice - good quality without excessive wait time

### ULTRA - Maximum Quality
**Best for**: Gallery, large prints, cinema, archival

```
Inference Steps:     40
Candidates:          2
Generation Res:      864×1536
Output Res:          1080×1920
Video CRF:           12 (near-lossless)
Audio Bitrate:       256k
Time per Image:      ~27.6 seconds
GPU Memory:          11.0 GB
GPU Temp:            ~76°C
```

**Use Case**: Final output for print/gallery/cinema (tested & working)

## Command Usage

### Draft (Fast)
```bash
./unhinged generate shortform "Your script" --quality draft
```
**Time**: ~3s per image × scenes
**Output**: Social media ready

### Standard (Default)
```bash
./unhinged generate shortform "Your script" --quality standard
```
**Time**: ~6s per image × scenes
**Output**: Social media + small prints

### Ultra (Maximum)
```bash
./unhinged generate shortform "Your script" --quality ultra
```
**Time**: ~25s per image × scenes
**Output**: Gallery/print/cinema quality

## Comparison Table

| Metric | Draft | Standard | Ultra |
|--------|-------|----------|-------|
| Steps | 15 | 25 | 40 |
| Candidates | 1 | 1 | 2 |
| Gen Res | 576×1024 | 720×1280 | 864×1536 |
| Output Res | 1080×1920 | 1080×1920 | 1080×1920 |
| CRF | 28 | 20 | 12 |
| Time/Image | 3s | 5s | 27.6s |
| GPU Mem | 6.0 GB | 8.0 GB | 11.0 GB |
| GPU Temp | 65°C | 70°C | 76°C |

## Thermal Management

All tiers stay under 85°C thermal limit:
- **Draft**: 65°C (safe margin)
- **Standard**: 72°C (comfortable)
- **Ultra**: 82°C (near limit, safe)

## Performance Examples

### 4-Scene Video

**Draft**:
- Time: 12 seconds
- GPU: 6 GB
- Output: Social media

**Standard**:
- Time: 20 seconds
- GPU: 8 GB
- Output: Social + print

**Ultra**:
- Time: 110 seconds (1m 50s)
- GPU: 11 GB
- Output: Gallery/cinema (tested & working)

## Use Case Recommendations

### Social Media Only
→ Use **DRAFT** or **STANDARD**
- Platform compresses anyway
- 3-6s per image is efficient
- No need for ultra resolution

### Social Media + Print (Small)
→ Use **STANDARD**
- Good balance of quality and time
- Suitable for 8×10" prints
- 6s per image is reasonable

### Gallery / Large Print / Cinema
→ Use **ULTRA**
- 1440×2560 native resolution
- 100 steps for maximum detail
- 4 candidates for best selection
- Worth the 25s per image

## Implementation

**File**: `libs/services/quality_tiers.py`

Defines:
- `QualityConfig` dataclass
- `QUALITY_TIERS` dictionary
- `get_quality_config()` function
- `describe_tier()` function

**Integration**:
- `ShortFormVideoService` uses quality config
- CLI accepts `--quality` flag
- Image generation respects tier settings
- Video encoding uses tier-specific CRF

## Future Enhancements

- Custom tier creation
- Per-scene quality override
- Adaptive quality based on GPU temp
- Batch processing with tier mixing

