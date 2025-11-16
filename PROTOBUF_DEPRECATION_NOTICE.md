# Protobuf Deprecation Notice

**Status**: DEPRECATED - Marked for removal  
**Date**: 2025-11-16  
**Reason**: Shift to Python-first, headless architecture with direct service wrappers in `/libs/services`

## Summary

Protobuf/gRPC has been deprecated in favor of direct Python service wrappers. All services now use pure Python implementations in `/libs/services` with no gRPC overhead.

## Files Marked for Removal

### Proto Definitions (entire `/proto` directory)
- `proto/audio.proto` - Audio service (replaced by TranscriptionService, TTSService)
- `proto/chat.proto` - Chat service (replaced by ChatService)
- `proto/chat_with_gateway.proto` - Chat gateway (deprecated)
- `proto/cdc_events.proto` - CDC events (deprecated)
- `proto/cdc_service.proto` - CDC service (deprecated)
- `proto/common.proto` - Common types (deprecated)
- `proto/context_service.proto` - Context service (replaced by TextGenerationService)
- `proto/document_store.proto` - Document store (replaced by DocumentStore in `/libs/python`)
- `proto/gateway_annotations.proto` - Gateway annotations (deprecated)
- `proto/graph_service.proto` - Graph service (deprecated)
- `proto/health/health.proto` - Health checks (deprecated)
- `proto/image_generation.proto` - Image generation (replaced by ImageGenerationService)
- `proto/llm.proto` - LLM service (replaced by TextGenerationService)
- `proto/messaging.proto` - Messaging (deprecated)
- `proto/minimal_event.proto` - Minimal events (deprecated)
- `proto/observability.proto` - Observability (deprecated)
- `proto/persistence_platform.proto` - Persistence (replaced by DocumentStore)
- `proto/universal_event.proto` - Universal events (deprecated)
- `proto/vision_service.proto` - Vision service (replaced by YOLOAnalysisService)
- `proto/google/protobuf/` - Google protobuf definitions (deprecated)

### gRPC Services (entire `/services` directory)
- `services/speech-to-text/grpc_server.py` - Replaced by TranscriptionService
- `services/text-to-speech/grpc_server.py` - Replaced by TTSService
- `services/image-generation/` - Replaced by ImageGenerationService
- `services/vision-ai/` - Replaced by YOLOAnalysisService
- `services/chat-with-sessions/` - Replaced by ChatService
- `services/graph-service/` - Deprecated
- `services/shared/` - Shared gRPC utilities (deprecated)

## Replacement Architecture

### New Pattern: CLI → /lib/services → Backend

```
unhinged generate text "prompt"
    ↓
cli/commands/generate.py
    ↓
libs/services/text_generation_service.py
    ↓
ollama/openai/anthropic (direct Python client)
```

### Service Wrappers in `/libs/services`

- `text_generation_service.py` - LLM text generation (ollama, openai, anthropic)
- `transcription_service.py` - Speech-to-text (Whisper)
- `tts_service.py` - Text-to-speech (gTTS)
- `image_generation_service.py` - Image generation (Stable Diffusion)
- `video_generation_service.py` - Video generation
- `chat_service.py` - Chat conversation management
- `yolo_analysis_service.py` - Vision/YOLO analysis
- `script_parser_service.py` - Script parsing
- `shortform_video_service.py` - Short-form video generation

## Benefits of Deprecation

1. **Simpler Architecture** - No gRPC complexity, direct Python imports
2. **Faster Development** - No proto compilation, no code generation
3. **Better Type Safety** - Python type hints instead of proto definitions
4. **Easier Testing** - Direct service instantiation, no network mocking
5. **Lower Overhead** - No serialization/deserialization, no network latency
6. **Headless-First** - Pure Python services, UI-agnostic

## Migration Timeline

- **Phase 4 (Current)**: Implement text generation and transcription CLI with new pattern
- **Phase 5**: Remove all protobuf files and gRPC services
- **Phase 6**: Archive `/services` directory to GitHub history

## Verification Checklist

Before removal, verify:
- [ ] All CLI commands use `/libs/services` wrappers
- [ ] All tests pass with new service wrappers
- [ ] No remaining imports from `proto/` or `services/`
- [ ] Man pages document new CLI interface
- [ ] GitHub Enterprise has full version history

## References

- `/libs/services/` - New service wrapper implementations
- `/cli/commands/generate.py` - Text generation CLI
- `/cli/commands/transcribe.py` - Transcription CLI
- `man/man1/unhinged-generate.1` - Generate command documentation
- `man/man1/unhinged-transcribe.1` - Transcribe command documentation

