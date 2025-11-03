# Architectural Reasoning: Why Service Framework Timeouts Matter

## The Problem with Client-Layer Fixes

When I initially fixed the timeout issue, I made changes at the **client layer** (GTK4 GUI):

```python
# ❌ WRONG: Patching individual clients
control/gtk4_gui/config.py:
    self.transcription_timeout = 600  # 10 minutes

control/gtk4_gui/service_connector.py:
    response = client.SpeechToText(..., timeout=app_config.transcription_timeout)
```

**Why this is wrong:**

1. **Polyglot Problem**: A Kotlin service calling speech-to-text would still timeout after 120s
2. **Maintenance Nightmare**: Every client needs the same patch
3. **Inconsistency**: Different clients might have different timeouts
4. **Scalability**: As we add more services and clients, this becomes unmaintainable
5. **Not Future-Proof**: When we build our own service framework, this pattern breaks

## The Correct Approach: Framework-Level Configuration

The fix should be at the **service framework level** where ALL callers converge:

```python
# ✅ CORRECT: Configure at framework level
libs/python/service_framework/connection_pool.py:
    @dataclass
    class ServiceConfig:
        timeout: float = 120.0
        
        def __post_init__(self):
            # Respect environment variables
            env_timeout = os.environ.get(f"{self.name.upper()}_TIMEOUT")
            if env_timeout:
                self.timeout = float(env_timeout)

libs/python/grpc_clients/client_factory.py:
    register_service("speech_to_text", "localhost:1191", timeout=600.0)
```

**Why this is correct:**

1. **Single Source of Truth**: One place to configure all service timeouts
2. **Polyglot Support**: Kotlin, Python, Go—all get the same timeout
3. **Automatic**: No need to patch individual clients
4. **Environment Override**: Easy to adjust for different scenarios
5. **Scalable**: Works for 5 services or 50 services

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ CALLERS (Multiple Languages & Frameworks)                   │
├─────────────────────────────────────────────────────────────┤
│ • GTK4 GUI (Python)                                         │
│ • Graph Service (Kotlin)                                    │
│ • Speech-to-Text Service (Python)                           │
│ • Future Services (Go, Rust, etc.)                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ All callers use the same framework
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ SERVICE FRAMEWORK (libs/python/service_framework/)          │
├─────────────────────────────────────────────────────────────┤
│ • ConnectionPool: Manages all connections                   │
│ • ServiceConfig: Per-service configuration                  │
│ • ServiceClient: Enforces timeouts                          │
│                                                              │
│ Configuration Hierarchy:                                    │
│ 1. Environment Variables (highest priority)                 │
│ 2. Service Registration (medium priority)                   │
│ 3. ServiceConfig Defaults (lowest priority)                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ Framework applies timeout to all calls
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ gRPC SERVICES                                               │
├─────────────────────────────────────────────────────────────┤
│ • Speech-to-Text (600s timeout)                             │
│ • Image Generation (180s timeout)                           │
│ • Chat (60s timeout)                                        │
│ • Persistence (60s timeout)                                 │
└─────────────────────────────────────────────────────────────┘
```

## Real-World Scenario: 6-Minute Audio Transcription

### Before (Client-Layer Fix)

```
GTK4 GUI transcribes 6-minute audio:
  ✅ Works (has custom 600s timeout)

Kotlin Graph Service transcribes 6-minute audio:
  ❌ FAILS (still uses framework's 120s default)
  
Python Speech-to-Text Service transcribes 6-minute audio:
  ❌ FAILS (still uses framework's 120s default)
```

### After (Framework-Level Fix)

```
GTK4 GUI transcribes 6-minute audio:
  ✅ Works (framework provides 600s timeout)

Kotlin Graph Service transcribes 6-minute audio:
  ✅ Works (framework provides 600s timeout)
  
Python Speech-to-Text Service transcribes 6-minute audio:
  ✅ Works (framework provides 600s timeout)
```

## Configuration Hierarchy in Action

```bash
# Scenario 1: Use default 600s timeout
./unhinged
# Result: speech_to_text uses 600s (from register_service call)

# Scenario 2: Override for very long audio
export SPEECH_TO_TEXT_TIMEOUT=1800
./unhinged
# Result: speech_to_text uses 1800s (from environment variable)

# Scenario 3: Override for short audio
export SPEECH_TO_TEXT_TIMEOUT=300
./unhinged
# Result: speech_to_text uses 300s (from environment variable)
```

## Why This Matters for Future Development

As Unhinged grows into an operating system:

1. **Service Mesh**: When we add service discovery, this pattern scales
2. **Custom Framework**: When we build our own service framework, this is the pattern
3. **Multi-Language**: Kotlin, Python, Go, Rust—all use the same framework
4. **Deployment Flexibility**: Different timeouts for dev/staging/production
5. **Monitoring**: Framework can track timeout occurrences and alert

## Key Principles

1. **Configuration at the Right Layer**: Framework, not clients
2. **Single Source of Truth**: One place to configure all timeouts
3. **Environment Override**: Easy to adjust without code changes
4. **Polyglot Support**: Works across all languages
5. **Scalability**: Works for 5 services or 500 services

## Files Involved

| File | Role | Change |
|------|------|--------|
| `libs/python/service_framework/connection_pool.py` | Core framework | Added env var override in `__post_init__` |
| `libs/python/grpc_clients/client_factory.py` | Service registration | Register services with appropriate timeouts |
| `control/gtk4_gui/config.py` | Client layer | Reverted (not needed) |
| `control/gtk4_gui/service_connector.py` | Client layer | Reverted (not needed) |
| `control/gtk4_gui/services/transcription_service.py` | Client layer | Reverted (not needed) |

## Conclusion

The timeout configuration is now properly implemented at the **service framework level**, ensuring that:
- ✅ All callers get consistent timeout behavior
- ✅ No need to patch individual clients
- ✅ Easy to adjust for different scenarios
- ✅ Scales as the system grows
- ✅ Polyglot-friendly (Kotlin, Python, etc.)

