# Service Framework Timeout Architecture

## Overview

This document explains how timeouts are properly configured at the **service framework level** (not at individual client layers). This ensures that ANY caller—whether it's the GTK4 GUI, a Kotlin service, or another Python service—gets consistent timeout behavior.

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│ Callers (GTK4 GUI, Kotlin Services, Python Services, etc)  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ Service Framework (libs/python/service_framework/)          │
│ - ConnectionPool: Manages all gRPC connections              │
│ - ServiceConfig: Per-service timeout configuration          │
│ - ServiceClient: Handles timeout enforcement                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ gRPC Services (speech-to-text, image-generation, etc)       │
└─────────────────────────────────────────────────────────────┘
```

## Key Principle

**Timeouts are configured at service registration time, not at call time.**

This means:
- ✅ A Kotlin service calling speech-to-text gets the 600s timeout
- ✅ The GTK4 GUI calling speech-to-text gets the 600s timeout
- ✅ A Python service calling speech-to-text gets the 600s timeout
- ❌ No need to patch individual callers

## Implementation

### 1. Service Configuration (libs/python/service_framework/connection_pool.py)

```python
@dataclass
class ServiceConfig:
    """Configuration for a gRPC service"""
    name: str
    address: str
    timeout: float = 120.0  # Default timeout
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
                # Log override
            except ValueError:
                # Log warning
```

**Key feature**: Environment variables override defaults
- Format: `{SERVICE_NAME}_TIMEOUT=seconds`
- Example: `SPEECH_TO_TEXT_TIMEOUT=600`

### 2. Service Registration (libs/python/grpc_clients/client_factory.py)

Services are registered with appropriate timeouts during framework initialization:

```python
# Speech-to-text service - longer timeout for audio transcription
register_service("speech_to_text", "localhost:1191", 
                stub_class=audio_pb2_grpc.AudioServiceStub, 
                timeout=600.0)  # 10 minutes

# Image generation service - longer timeout for image processing
register_service("image_generation", "localhost:9094", 
                stub_class=image_generation_pb2_grpc.ImageGenerationServiceStub, 
                timeout=180.0)  # 3 minutes

# Chat service - standard timeout
register_service("chat", "localhost:9095", 
                stub_class=chat_pb2_grpc.ChatServiceStub, 
                timeout=60.0)  # 1 minute
```

### 3. Timeout Enforcement (libs/python/service_framework/connection_pool.py)

When any caller makes a request, the framework automatically applies the configured timeout:

```python
def call_with_timeout(self, method_name: str, request, timeout: float | None = None) -> Any:
    """Call gRPC method with timeout"""
    stub = self.get_stub()
    call_timeout = timeout or self.config.timeout  # Use service's configured timeout
    
    for attempt in range(self.config.max_retries):
        try:
            method = getattr(stub, method_name)
            return method(request, timeout=call_timeout)
        except grpc.RpcError as e:
            # Handle errors...
```

## Configuration Hierarchy

1. **Environment Variable** (highest priority)
   - `SPEECH_TO_TEXT_TIMEOUT=900` → 15 minutes

2. **Service Registration** (medium priority)
   - `register_service("speech_to_text", ..., timeout=600.0)` → 10 minutes

3. **ServiceConfig Default** (lowest priority)
   - `timeout: float = 120.0` → 2 minutes

## Service Timeout Recommendations

| Service | Default | Reason | Override |
|---------|---------|--------|----------|
| speech_to_text | 600s (10m) | Audio transcription is slow (~10-20% of audio duration) | `SPEECH_TO_TEXT_TIMEOUT=900` |
| image_generation | 180s (3m) | Image generation takes time | `IMAGE_GENERATION_TIMEOUT=300` |
| text_to_speech | 120s (2m) | TTS is relatively fast | `TEXT_TO_SPEECH_TIMEOUT=180` |
| chat | 60s (1m) | LLM responses are fast | `CHAT_TIMEOUT=120` |
| persistence | 60s (1m) | Database operations are fast | `PERSISTENCE_TIMEOUT=120` |
| vision | 60s (1m) | Vision processing is moderate | `VISION_TIMEOUT=120` |

## Usage Examples

### Example 1: GTK4 GUI Transcribing Audio

```python
# In control/gtk4_gui/service_connector.py
from libs.python.service_framework import call_service

# The framework automatically uses the 600s timeout configured for speech_to_text
response = call_service("speech_to_text", "SpeechToText", request)
```

### Example 2: Kotlin Service Transcribing Audio

```kotlin
// In services/graph-service/src/main/kotlin/...
// The Kotlin service would use its own gRPC client, but the Python
// service framework ensures consistent timeouts at the service level
```

### Example 3: Override Timeout at Runtime

```bash
# For a 15-minute audio file
export SPEECH_TO_TEXT_TIMEOUT=900
./unhinged

# For a 30-minute audio file
export SPEECH_TO_TEXT_TIMEOUT=1800
./unhinged
```

## Why This Approach?

1. **Single Source of Truth**: Timeout configuration is in one place (service registration)
2. **Polyglot Support**: Any language can call the service and get the same timeout
3. **No Caller Patching**: Don't need to modify GTK4 GUI, Kotlin services, etc.
4. **Environment Override**: Easy to adjust for different deployment scenarios
5. **Future-Proof**: When we build our own service framework, this pattern scales

## Future Enhancements

1. **Adaptive Timeouts**: Adjust based on service load/health
2. **Timeout Profiles**: Different profiles for dev/staging/production
3. **Per-Operation Timeouts**: Different timeouts for different operations within a service
4. **Timeout Metrics**: Track timeout occurrences and adjust automatically
5. **Circuit Breaker**: Fail fast if service is consistently timing out

## Related Files

- `libs/python/service_framework/connection_pool.py` - Core timeout implementation
- `libs/python/grpc_clients/client_factory.py` - Service registration with timeouts
- `libs/python/service_framework/__init__.py` - Public API exports
- `services/speech-to-text/grpc_server.py` - Speech-to-text service implementation
- `services/image-generation/grpc_server.py` - Image generation service implementation

