# gRPC Timeout Configuration Guide

## Problem Statement

The Unhinged service framework had hardcoded gRPC timeouts that were too short for long-running operations like audio transcription. A 6-minute voice recording would fail with `DEADLINE_EXCEEDED` errors because the 30-second timeout was insufficient.

## Solution: Service-Level Timeout Configuration

The framework now supports **service-specific timeout overrides** at the configuration level, allowing each service to define appropriate timeouts for its operations.

## Configuration Hierarchy

```
Environment Variables (Highest Priority)
    ↓
Application Config (app_config)
    ↓
Service-Specific Defaults (Lowest Priority)
```

## Available Timeout Settings

### Global gRPC Timeout
```bash
export GRPC_TIMEOUT=300  # Default: 5 minutes (300 seconds)
```
- Used for general gRPC operations
- Fallback for services without specific timeout

### Transcription Timeout
```bash
export TRANSCRIPTION_TIMEOUT=600  # Default: 10 minutes (600 seconds)
```
- Used for speech-to-text operations
- Handles audio files up to ~10 minutes
- Calculation: 30 seconds per minute of audio + 60 second buffer

### Image Generation Timeout
```bash
export IMAGE_GENERATION_TIMEOUT=120  # Default: 2 minutes (120 seconds)
```
- Used for image generation operations
- Handles most image generation requests

## Configuration in Code

### `control/gtk4_gui/config.py`

```python
# Global gRPC timeout (5 minutes)
self.grpc_timeout = int(os.environ.get('GRPC_TIMEOUT', '300'))

# Service-specific timeouts
self.transcription_timeout = int(os.environ.get('TRANSCRIPTION_TIMEOUT', '600'))
self.image_generation_timeout = int(os.environ.get('IMAGE_GENERATION_TIMEOUT', '120'))
```

### Usage in Services

```python
# In service_connector.py
response = client.SpeechToText(
    generate_chunks(), 
    timeout=app_config.transcription_timeout  # Uses service-specific timeout
)

# In transcription_service.py
def transcribe_audio_file(self, audio_file_path: str, timeout: float = 600.0):
    # Default 10-minute timeout for transcription
    response = self.client.SpeechToText(generate_audio_chunks(), timeout=timeout)
```

## Timeout Recommendations

### Audio Transcription
- **Short clips (< 1 min)**: 60 seconds
- **Medium clips (1-5 min)**: 300 seconds (5 minutes)
- **Long clips (5-10 min)**: 600 seconds (10 minutes)
- **Very long clips (> 10 min)**: 900+ seconds (15+ minutes)

**Formula**: `30 seconds per minute of audio + 60 second buffer`

### Image Generation
- **Small images**: 60 seconds
- **Medium images**: 120 seconds (2 minutes)
- **Large/complex images**: 180+ seconds (3+ minutes)

### General gRPC Operations
- **Fast operations**: 30 seconds
- **Standard operations**: 60 seconds
- **Slow operations**: 120+ seconds

## Setting Timeouts at Runtime

### Option 1: Environment Variables (Recommended)
```bash
# Before starting the application
export TRANSCRIPTION_TIMEOUT=900  # 15 minutes
export IMAGE_GENERATION_TIMEOUT=180  # 3 minutes
./unhinged
```

### Option 2: Docker/Container
```dockerfile
ENV TRANSCRIPTION_TIMEOUT=900
ENV IMAGE_GENERATION_TIMEOUT=180
```

### Option 3: Makefile
```makefile
start-gui:
	TRANSCRIPTION_TIMEOUT=900 IMAGE_GENERATION_TIMEOUT=180 ./unhinged
```

## Monitoring Timeout Issues

### Symptoms of Timeout Problems
- `DEADLINE_EXCEEDED` errors in logs
- Operations fail after exactly N seconds
- Inconsistent failures on long operations

### Debugging
```python
# Check current timeout configuration
from control.gtk4_gui.config import AppConfig
config = AppConfig()
print(f"Transcription timeout: {config.transcription_timeout}s")
print(f"Image generation timeout: {config.image_generation_timeout}s")
```

### Logs to Check
```bash
# Look for deadline exceeded errors
grep -i "deadline" /var/log/unhinged/*.log

# Check service startup logs
grep -i "timeout" /var/log/unhinged/*.log
```

## Future Enhancements

### 1. Per-Operation Timeouts
```python
# Allow timeout override per operation
transcribe(audio_file, timeout=1200)  # 20 minutes for this specific file
```

### 2. Adaptive Timeouts
```python
# Estimate timeout based on file size
estimated_duration = estimate_audio_duration(audio_file)
timeout = (estimated_duration * 0.3) + 60  # 30% of duration + buffer
```

### 3. Timeout Profiles
```python
# Predefined timeout profiles
TIMEOUT_PROFILES = {
    'fast': {'transcription': 60, 'image_gen': 60},
    'standard': {'transcription': 300, 'image_gen': 120},
    'slow': {'transcription': 600, 'image_gen': 180},
    'very_slow': {'transcription': 900, 'image_gen': 300},
}
```

### 4. Service-Level Configuration
```yaml
# services/speech-to-text/config.yaml
timeout:
  default: 600
  max: 1800
  per_minute_of_audio: 30
  buffer: 60
```

## Polyglot Framework Support

The Unhinged service framework supports multiple languages (Python, Kotlin, etc.). Each language binding should implement similar timeout configuration:

### Python
```python
self.transcription_timeout = int(os.environ.get('TRANSCRIPTION_TIMEOUT', '600'))
```

### Kotlin
```kotlin
val transcriptionTimeout = System.getenv("TRANSCRIPTION_TIMEOUT")?.toIntOrNull() ?: 600
```

### Configuration Pattern
All language bindings should:
1. Support environment variable overrides
2. Provide sensible defaults
3. Document timeout recommendations
4. Allow per-operation timeout specification

## Summary

✅ **Fixed**: Hardcoded 30-second timeout
✅ **Added**: Service-specific timeout configuration
✅ **Enabled**: Environment variable overrides
✅ **Documented**: Timeout recommendations and usage

The framework now properly handles long-running operations while remaining configurable for different deployment scenarios.

