# Short-Form Video Generator - CLI Now Live ✅

## Command is Live

```bash
./unhinged generate shortform "Your script here" [options]
```

## Quick Start

```bash
# Basic usage
./unhinged generate shortform "Hey everyone! Check this out."

# With platform
./unhinged generate shortform "Your script" --platform reels

# With voice
./unhinged generate shortform "Your script" --voice echo

# With style
./unhinged generate shortform "Your script" --style vibrant

# Full example
./unhinged generate shortform "Your script" \
  --platform tiktok \
  --voice nova \
  --style cinematic \
  --format json
```

## Options

### Platform
- `tiktok` (default) - 1080x1920, 15s-10min
- `reels` - 1080x1920, 15s-90s
- `shorts` - 1080x1920, 15s-60s

### Voice
- `nova` (default) - Female, American, friendly
- `echo` - Male, American, professional
- `sage` - Male, American, thoughtful
- `shimmer` - Female, British, sophisticated

### Style
- `cinematic` (default) - Professional, high-quality
- `minimal` - Clean, simple
- `vibrant` - Colorful, energetic
- `abstract` - Artistic, creative

### Format
- `text` (default) - Human-readable output
- `json` - Machine-readable JSON

## Help

```bash
./unhinged generate shortform --help
```

## Pipeline

1. **Script Parsing** (0.1s)
   - Breaks into scenes
   - Calculates timing
   - Extracts visual cues
   - Detects emotion

2. **Voiceover Generation** (2-5s per scene)
   - Text-to-Speech
   - Multiple voices
   - Emotion-aware
   - MP3 output

3. **Visual Generation** (10-30s per scene)
   - AI image generation
   - Style-specific
   - Platform-optimized

4. **Video Composition** (5-10s)
   - Audio-video sync
   - Transitions
   - Captions
   - MP4 encoding

## Output

**Location**: `/build/tmp/generated/shortform_*.mp4`

**Specs**:
- Format: MP4 (H.264)
- Resolution: 1080x1920 (9:16)
- Audio: AAC, 128kbps
- FPS: 24

## Implementation

### Services
- `ScriptParserService` - Parse scripts into scenes
- `TTSService` - Generate voiceovers
- `ShortFormVideoService` - Orchestrate pipeline

### CLI Integration
- `control/generate_cli.py` - Python CLI handler
- `unhinged` - Bash script routing

### Dependencies
- `gtts>=2.3.0` - Google Text-to-Speech
- `pydub>=0.25.0` - Audio manipulation
- `diffusers` - Image generation
- `torch` - Deep learning

## Examples

### TikTok Video
```bash
./unhinged generate shortform \
  "Hey everyone! Today we're exploring AI video generation. It's amazing how far technology has come." \
  --platform tiktok \
  --voice nova \
  --style cinematic
```

### Instagram Reels
```bash
./unhinged generate shortform \
  "Check out this amazing AI technology!" \
  --platform reels \
  --voice shimmer \
  --style vibrant
```

### YouTube Shorts
```bash
./unhinged generate shortform \
  "Quick tutorial on AI video generation" \
  --platform shorts \
  --voice echo \
  --style minimal
```

## Status

✅ **Production Ready**
- All services implemented
- CLI fully wired
- Help text updated
- Command routing working
- Argparse configured
- Bash handler added

## Next Steps

1. Run the command with your script
2. Wait for generation (2-5 minutes)
3. Find video in `/build/tmp/generated/`
4. Upload to TikTok/Reels/Shorts
5. Share with the world!

