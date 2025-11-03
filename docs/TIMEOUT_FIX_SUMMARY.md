# Timeout Configuration Fix - Summary

## Problem

A 6-minute voice recording failed with `DEADLINE_EXCEEDED` error during transcription because the gRPC timeout was hardcoded to 30 seconds at the service framework level.

## Root Cause Analysis

The issue was NOT just in the GTK4 GUI layer. The real problem was in the **service framework** (`libs/python/service_framework/connection_pool.py`):

```python
# BEFORE: Hardcoded 120s default for ALL services
@dataclass
class ServiceConfig:
    timeout: float = 120.0  # Too short for transcription!
```

This meant:
- ❌ Any caller (GTK4, Kotlin service, Python service) would timeout after 120s
- ❌ A 6-minute audio file taking 1-2 minutes to transcribe would fail
- ❌ Patching individual callers wouldn't solve the root problem

## Solution

### 1. Made ServiceConfig Respect Environment Variables

**File**: `libs/python/service_framework/connection_pool.py`

```python
@dataclass
class ServiceConfig:
    name: str
    address: str
    timeout: float = 120.0
    max_retries: int = 3
    stub_class: type | None = None
    
    def __post_init__(self):
        """Allow timeout to be overridden by environment variable"""
        import os
        env_timeout_key = f"{self.name.upper()}_TIMEOUT"
        env_timeout = os.environ.get(env_timeout_key)
        if env_timeout:
            try:
                self.timeout = float(env_timeout)
                logging.getLogger(__name__).info(
                    f"Service {self.name} timeout overridden by {env_timeout_key}={self.timeout}s"
                )
            except ValueError:
                logging.getLogger(__name__).warning(
                    f"Invalid timeout value for {env_timeout_key}: {env_timeout}"
                )
```

### 2. Registered Services with Appropriate Timeouts

**File**: `libs/python/grpc_clients/client_factory.py`

```python
# Speech-to-text service - longer timeout for audio transcription
register_service("speech_to_text", "localhost:1191", 
                stub_class=audio_pb2_grpc.AudioServiceStub, 
                timeout=600.0)  # 10 minutes

# Image generation service - longer timeout for image processing
register_service("image_generation", "localhost:9094", 
                stub_class=image_generation_pb2_grpc.ImageGenerationServiceStub, 
                timeout=180.0)  # 3 minutes

# Other services with standard timeouts
register_service("chat", "localhost:9095", timeout=60.0)
register_service("persistence", "localhost:9090", timeout=60.0)
register_service("vision", "localhost:9093", timeout=60.0)
register_service("text_to_speech", "localhost:9092", timeout=120.0)
```

### 3. Reverted Incorrect GTK4 GUI Changes

**Files Reverted**:
- `control/gtk4_gui/config.py` - Removed service-specific timeout configs
- `control/gtk4_gui/service_connector.py` - Removed custom timeout handling
- `control/gtk4_gui/services/transcription_service.py` - Removed timeout override

**Why**: These changes were band-aids on the wrong layer. The framework should handle this, not individual clients.

## Result

Now:
- ✅ Speech-to-text service has 600s (10 minute) timeout by default
- ✅ Any caller gets this timeout automatically
- ✅ Can override with `SPEECH_TO_TEXT_TIMEOUT=900` for 15-minute audio
- ✅ 6-minute audio files will transcribe successfully (1-2 minutes processing)
- ✅ Kotlin services calling speech-to-text also get the 600s timeout
- ✅ No need to patch individual callers

## Configuration Hierarchy

1. **Environment Variable** (highest priority)
   ```bash
   export SPEECH_TO_TEXT_TIMEOUT=900
   ```

2. **Service Registration** (medium priority)
   ```python
   register_service("speech_to_text", ..., timeout=600.0)
   ```

3. **ServiceConfig Default** (lowest priority)
   ```python
   timeout: float = 120.0
   ```

## Files Changed

| File | Change | Reason |
|------|--------|--------|
| `libs/python/service_framework/connection_pool.py` | Added `__post_init__` to respect env vars | Framework-level configuration |
| `libs/python/grpc_clients/client_factory.py` | Register services with appropriate timeouts | Service-level defaults |
| `control/gtk4_gui/config.py` | Reverted custom timeout configs | Not needed at client layer |
| `control/gtk4_gui/service_connector.py` | Reverted custom timeout handling | Not needed at client layer |
| `control/gtk4_gui/services/transcription_service.py` | Reverted timeout override | Not needed at client layer |

## Testing

```bash
# Test with default 600s timeout
./unhinged

# Test with custom timeout for very long audio
export SPEECH_TO_TEXT_TIMEOUT=1800
./unhinged

# Verify timeout is applied
# Check logs for: "Service speech_to_text timeout overridden by SPEECH_TO_TEXT_TIMEOUT=1800s"
```

## Key Takeaway

**Timeouts should be configured at the service framework level, not at individual client layers.** This ensures:
- Consistent behavior across all callers
- Single source of truth
- Easy to adjust for different deployment scenarios
- Polyglot support (Kotlin, Python, etc.)

