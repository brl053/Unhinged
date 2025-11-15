# How to Generate Studio-Grade Short-Form Videos

## Quick Start

### 1. Write Your Script
```
"Hey everyone! Today we're exploring AI video generation.
It's amazing how far technology has come.
Let me show you what's possible."
```

### 2. Run the Command
```bash
./unhinged generate shortform "Your script here"
```

### 3. Get Your Video
Output: MP4 file optimized for TikTok/Reels/Shorts

## Command Options

### Basic
```bash
./unhinged generate shortform "Your script"
```

### With Platform Selection
```bash
./unhinged generate shortform "Your script" --platform tiktok
# Options: tiktok, reels, shorts
```

### With Voice Selection
```bash
./unhinged generate shortform "Your script" --voice nova
# Options: nova (female), echo (male), sage (male), shimmer (female)
```

### With Visual Style
```bash
./unhinged generate shortform "Your script" --style cinematic
# Options: cinematic, minimal, vibrant, abstract
```

### Full Example
```bash
./unhinged generate shortform "Your script" \
  --platform reels \
  --voice echo \
  --style vibrant \
  --format json
```

## What Happens Behind the Scenes

### Step 1: Script Parsing (0.1s)
- Breaks script into scenes
- Calculates timing per scene
- Extracts visual cues
- Detects emotion/tone

### Step 2: Voiceover Generation (2-5s per scene)
- Converts text to speech
- Uses selected voice
- Applies emotion
- Generates MP3 audio

### Step 3: Visual Generation (10-30s per scene)
- Creates AI images for each scene
- Applies selected style
- Optimizes for platform resolution
- Generates visual assets

### Step 4: Video Composition (5-10s)
- Syncs audio with visuals
- Adds transitions
- Adds captions
- Encodes to MP4

## Output

**Location**: `/build/tmp/generated/shortform_*.mp4`

**Specifications**:
- Resolution: 1080x1920 (9:16 mobile)
- Format: MP4 with H.264 codec
- Audio: AAC, 128kbps
- FPS: 24 (optimized for platforms)

## Python API

```python
from libs.services import ShortFormVideoService

service = ShortFormVideoService()

result = service.generate_from_script(
    script="Your script here",
    platform="tiktok",
    voice="nova",
    style="cinematic"
)

print(f"Video: {result['video_path']}")
print(f"Duration: {result['duration']}s")
print(f"Scenes: {result['scenes']}")
print(f"Time: {result['generation_time']:.1f}s")
```

## Voice Options

| Voice | Gender | Accent | Best For |
|-------|--------|--------|----------|
| nova | Female | American | Friendly, energetic |
| echo | Male | American | Professional, calm |
| sage | Male | American | Thoughtful, measured |
| shimmer | Female | British | Sophisticated, elegant |

## Style Options

| Style | Description | Best For |
|-------|-------------|----------|
| cinematic | Professional, high-quality | Premium content |
| minimal | Clean, simple | Educational |
| vibrant | Colorful, energetic | Entertainment |
| abstract | Artistic, creative | Artistic content |

## Platform Specs

### TikTok
- Duration: 15s-10min
- Resolution: 1080x1920
- Aspect: 9:16

### Instagram Reels
- Duration: 15s-90s
- Resolution: 1080x1920
- Aspect: 9:16

### YouTube Shorts
- Duration: 15s-60s
- Resolution: 1080x1920
- Aspect: 9:16

## Tips for Best Results

1. **Script Length**: 50-150 words works best
2. **Pacing**: Natural speech rhythm
3. **Visual Cues**: Use descriptive language
4. **Emotion**: Match voice to content
5. **Style**: Choose style matching content

## Troubleshooting

**GPU Memory Error**: Reduce resolution or use fewer scenes
**Slow Generation**: Normal for AI - first run loads models
**Audio Issues**: Check script for special characters
**Video Quality**: Use "cinematic" style for best results

## Next Steps

1. Generate your first video
2. Download from `/build/tmp/generated/`
3. Upload to TikTok/Reels/Shorts
4. Share with the world!

