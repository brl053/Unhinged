# Audio Device Compatibility Guide

## Overview

Unhinged supports a wide range of audio input devices through automatic format negotiation. The audio handler detects the best supported format for your device at initialization time and caches the result to avoid repeated detection overhead.

## Supported Audio Devices

### Default Devices (Recommended)

| Device | Format | Sample Rate | Channels | Status |
|--------|--------|-------------|----------|--------|
| PipeWire (default) | S16_LE | 16000 Hz | 1 (mono) | ✅ Tested |
| ALSA (default) | S16_LE | 16000 Hz | 1 (mono) | ✅ Tested |

### USB Audio Devices

| Device | Format | Sample Rate | Notes |
|--------|--------|-------------|-------|
| Logitech Yeti GX | S24_3LE | 48000 Hz | ✅ Auto-detected, format negotiated |
| Generic USB Audio | S16_LE | 16000 Hz | ✅ Auto-detected |

### Format Negotiation

The audio handler automatically detects supported formats in this order:
1. S16_LE (16-bit signed little-endian) - Most common
2. S24_3LE (24-bit signed little-endian in 3 bytes) - USB audio devices
3. S32_LE (32-bit signed little-endian)
4. U8 (8-bit unsigned)
5. S8 (8-bit signed)

If your device doesn't support S16_LE, the handler will use the first supported format.

## Configuration

### Setting Audio Device

Set the `AUDIO_DEVICE` environment variable:

```bash
# Use default PipeWire device
export AUDIO_DEVICE="pipewire"

# Use ALSA default device
export AUDIO_DEVICE="default"

# Use specific USB device (e.g., Yeti GX on card 4, device 0)
export AUDIO_DEVICE="hw:4,0"

# Then run Unhinged
./unhinged
```

### Finding Your Device

List available audio input devices:

```bash
arecord -l
```

Output example:
```
**** List of CAPTURE Hardware Devices ****
card 4: GX [Yeti GX], device 0: USB Audio [USB Audio]
```

Use `hw:4,0` for this device.

## Performance

- **First initialization**: ~4 seconds (format detection)
- **Subsequent initializations**: <1 millisecond (cached)
- **Recording start**: <1 millisecond (no detection overhead)

Format detection runs once during `AudioHandler` initialization and results are cached globally.

## Troubleshooting

### "Sample format non available" Error

Your device doesn't support the default S16_LE format. The handler will automatically negotiate a compatible format. If this fails:

1. Check supported formats: `arecord -D hw:X,Y --help | grep -i format`
2. Report the device and supported formats to the team
3. Format support can be added to the negotiation list

### No Audio Input

1. Verify device is detected: `arecord -l`
2. Test recording: `arecord -D hw:X,Y -f S16_LE -r 16000 -c 1 -t wav -d 2 /tmp/test.wav`
3. Check logs for format negotiation results

## Adding New Devices

To add support for a new audio device:

1. Test format compatibility: `arecord -D hw:X,Y -f FORMAT -r 16000 -c 1 -t raw -d 1 /dev/null`
2. Report supported formats to the team
3. Update `detect_supported_formats()` if needed
4. Add device to this compatibility guide

## Technical Details

### Format Detection Architecture

- **Location**: `control/gtk4_gui/utils/audio_utils.py`
- **Cache**: Global module-level dictionary `_FORMAT_CACHE`
- **Scope**: Single-process application (cache not persistent across processes)
- **Isolation**: All format logic isolated for future refactoring

### Sample Width Mapping

| Format | Sample Width | Bits |
|--------|--------------|------|
| U8 | 1 byte | 8-bit |
| S8 | 1 byte | 8-bit |
| S16_LE | 2 bytes | 16-bit |
| S24_3LE | 3 bytes | 24-bit |
| S32_LE | 4 bytes | 32-bit |

### Logging

Format detection results are logged at INFO level:

```
Audio format detection: device=hw:4,0 cache_hit=false formats=['S24_3LE']
Audio handler initialized: device=hw:4,0 format=S24_3LE sample_width=3bytes
```

Monitor these logs to understand device compatibility in production.

## Future Enhancements

- [ ] Device-specific configuration profiles
- [ ] Sample rate negotiation (currently fixed at 16000 Hz)
- [ ] Automatic resampling for transcription service
- [ ] Audio quality metrics in UI
- [ ] Hardware-specific optimizations

