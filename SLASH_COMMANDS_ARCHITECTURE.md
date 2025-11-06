# Slash Commands Architecture Plan

**Principle**: Think UI-first for planning, implement headless-first (data contracts, schemas, proto definitions).

## Vision

Enable slash commands in the OS Chatroom to test different modalities through the UI, with results displayed inline in the chat. This closes the UI loop - no need to navigate to external files or viewers.

**Examples**:
- `/image draft` → Generates image, displays in chat
- Normal message → Text generation → Microphone button for TTS playback

## Current State

### Working
- ✅ `/image <prompt>` command exists and partially works
- ✅ Image display widget (`GeneratedArtifactWidget`) exists
- ✅ Chat message display infrastructure in place

### Broken
- ❌ Text generation returns mock framework response (line 1460)
- ❌ No TTS integration for text responses
- ❌ No microphone button for audio playback

## Architecture (Headless-First)

### Layer 1: Data Contracts & Schemas

**Command Request Schema**:
```protobuf
message SlashCommandRequest {
  string command_name = 1;      // "image", "tts", etc.
  string arguments = 2;          // Raw arguments string
  map<string, string> flags = 3; // Parsed flags
  string session_id = 4;         // Session context
  int64 timestamp = 5;           // Request time
}

message SlashCommandResponse {
  string command_name = 1;
  bool success = 2;
  string result_type = 3;        // "image", "text", "audio", etc.
  bytes result_data = 4;         // Serialized result
  string error_message = 5;
  int64 execution_time_ms = 6;
}
```

**Text Generation Schema**:
```protobuf
message TextGenerationRequest {
  string prompt = 1;
  int32 max_tokens = 2;
  float temperature = 3;
  string session_id = 4;
}

message TextGenerationResponse {
  string text = 1;
  int32 tokens_generated = 2;
  float generation_time_ms = 3;
}
```

**TTS Schema**:
```protobuf
message TextToSpeechRequest {
  string text = 1;
  string voice_id = 2;           // "default" for now
  float speed = 3;               // 1.0 = normal
}

message TextToSpeechResponse {
  bytes audio_data = 1;          // WAV format
  string audio_format = 2;       // "wav", "mp3"
  float duration_seconds = 3;
}
```

### Layer 2: Service Interfaces

**TextGenerationService** (libs/services/text_generation_service.py):
- `generate_text(prompt, max_tokens, temperature) → TextGenerationResponse`
- Lazy-load LLM model (similar to image generation)
- Return structured response with metadata

**TextToSpeechService** (libs/services/tts_service.py):
- `synthesize(text, voice_id, speed) → TextToSpeechResponse`
- Support multiple voices (future)
- Return audio bytes + metadata

**SlashCommandRouter** (libs/services/slash_command_router.py):
- Parse command string: `/image draft` → `SlashCommandRequest`
- Route to appropriate service
- Return `SlashCommandResponse`

### Layer 3: UI Integration (After Headless Works)

**ChatroomView Changes**:
1. Parse slash commands in `_on_send_clicked()`
2. Route to `SlashCommandRouter`
3. Display results using appropriate widgets:
   - Images: `GeneratedArtifactWidget`
   - Text: `ChatMessage` + microphone button
   - Audio: Audio player widget

**New UI Components**:
- `AudioPlayerWidget`: Play TTS audio inline
- `MicrophoneButton`: Trigger TTS for text responses

## Implementation Order (Headless-First)

### Phase 1: Text Generation Service
1. Create `libs/services/text_generation_service.py`
2. Define `TextGenerationRequest/Response` in proto
3. Implement lazy LLM loading (similar to image generation)
4. Test with simple prompt

### Phase 2: TTS Service
1. Create `libs/services/tts_service.py`
2. Define `TextToSpeechRequest/Response` in proto
3. Integrate with system TTS (espeak, festival, or pyttsx3)
4. Test audio generation

### Phase 3: Slash Command Router
1. Create `libs/services/slash_command_router.py`
2. Parse command syntax
3. Route to appropriate service
4. Return structured response

### Phase 4: UI Integration
1. Update `chatroom_view.py` to use router
2. Add audio player widget
3. Add microphone button to text responses
4. Test end-to-end

## Key Design Principles

1. **Headless-First**: All services work independently of UI
2. **Structured Responses**: All services return typed responses with metadata
3. **Lazy Loading**: Models load on first use (memory efficient)
4. **Error Handling**: Graceful degradation, clear error messages
5. **Session Context**: All operations include session_id for logging
6. **Simplicity**: No voice selection, no complex options - just works

## Files to Create/Modify

**New Files**:
- `libs/services/text_generation_service.py`
- `libs/services/tts_service.py`
- `libs/services/slash_command_router.py`
- `proto/text_generation.proto`
- `proto/tts.proto`
- `proto/slash_commands.proto`

**Modified Files**:
- `control/gtk4_gui/views/chatroom_view.py` (Phase 4 only)
- `libs/services/__init__.py` (add new services)

## Success Criteria

- ✅ `/image <prompt>` generates and displays images
- ✅ Normal text messages generate responses (not mock)
- ✅ Text responses have microphone button
- ✅ Microphone button plays TTS audio inline
- ✅ All operations logged with session context
- ✅ Graceful error handling throughout

