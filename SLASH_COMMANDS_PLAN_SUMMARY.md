# Slash Commands Implementation Plan - Executive Summary

## Your Vision

Enable slash commands in the OS Chatroom to test different modalities through the UI, with results displayed inline. Close the UI loop - no external file navigation needed.

**Examples**:
- `/image draft` → Image displays in chat
- Normal message → Text response + microphone button → Click to hear TTS

## Our Approach: Headless-First

**Think UI-first for planning, implement headless-first (data contracts, schemas, proto definitions).**

This means:
1. Define what data flows through the system (proto schemas)
2. Build services that work independently of UI
3. Test each service in isolation
4. Finally, wire UI to display results

**Why?** Avoids UI bikeshedding, ensures services are reusable, makes testing easier.

---

## Current State

### ✅ Working
- `/image <prompt>` command exists
- Image display widget exists
- Chat infrastructure in place

### ❌ Broken
- Text generation returns mock response (line 1460 in chatroom_view.py)
- No TTS integration
- No microphone button for audio playback

---

## Implementation Plan (5 Phases)

### Phase 1: Verify /image Command
**Goal**: Ensure existing command works end-to-end
- Test `/image draft` in UI
- Verify image displays and error handling works
- **Effort**: 30 minutes

### Phase 2: Text Generation Service (Headless)
**Goal**: Create reusable text generation service
- Define `TextGenerationRequest/Response` in proto
- Create `TextGenerationService` with lazy LLM loading
- Test independently (no UI yet)
- **Effort**: 2-3 hours
- **Files**: `proto/text_generation.proto`, `libs/services/text_generation_service.py`

### Phase 3: TTS Service (Headless)
**Goal**: Create text-to-speech service
- Define `TextToSpeechRequest/Response` in proto
- Create `TextToSpeechService` using espeak/pyttsx3
- Test independently (no UI yet)
- **Effort**: 1-2 hours
- **Files**: `proto/tts.proto`, `libs/services/tts_service.py`

### Phase 4: Slash Command Router (Headless)
**Goal**: Parse and route commands to services
- Define `SlashCommandRequest/Response` in proto
- Create `SlashCommandRouter` to parse `/image`, `/text`, `/tts`
- Test independently (no UI yet)
- **Effort**: 1 hour
- **Files**: `proto/slash_commands.proto`, `libs/services/slash_command_router.py`

### Phase 5: UI Integration
**Goal**: Wire UI to use services
- Update `chatroom_view.py` to use router
- Create audio player widget
- Add microphone button to text responses
- Test end-to-end
- **Effort**: 2-3 hours
- **Files**: `control/gtk4_gui/views/chatroom_view.py`, new widget files

**Total Effort**: ~8-10 hours

---

## Key Design Principles

1. **Headless-First**: All services work independently before UI integration
2. **Structured Responses**: All services return typed responses with metadata
3. **Lazy Loading**: Models load on first use (memory efficient)
4. **Error Handling**: Graceful degradation with clear error messages
5. **Session Context**: All operations include session_id for logging
6. **Simplicity**: No voice selection, no complex options - just works

---

## Data Flow Examples

### /image Command
```
User: "/image draft"
  ↓
SlashCommandRouter.route("/image draft")
  ↓
ImageGenerationService.generate_image("draft")
  ↓
Returns: {image_path, generation_time, model, device, steps}
  ↓
ChatroomView displays image in chat
```

### Normal Text Message
```
User: "Write a haiku about code"
  ↓
SlashCommandRouter.route("Write a haiku about code")
  ↓
TextGenerationService.generate_text("Write a haiku about code")
  ↓
Returns: {text, tokens_generated, generation_time}
  ↓
ChatroomView displays text + microphone button
  ↓
User clicks microphone
  ↓
TextToSpeechService.synthesize(text)
  ↓
Returns: {audio_path, duration, format}
  ↓
AudioPlayerWidget plays audio inline
```

---

## Files to Create/Modify

### New Files
- `proto/text_generation.proto` - Text generation data contract
- `proto/tts.proto` - TTS data contract
- `proto/slash_commands.proto` - Command routing data contract
- `libs/services/text_generation_service.py` - Text generation service
- `libs/services/tts_service.py` - TTS service
- `libs/services/slash_command_router.py` - Command router
- `control/gtk4_gui/components/audio_player_widget.py` - Audio player UI

### Modified Files
- `libs/services/__init__.py` - Export new services
- `control/gtk4_gui/views/chatroom_view.py` - Use router, add UI integration

---

## Success Criteria

- ✅ `/image <prompt>` generates and displays images in chat
- ✅ Normal text messages generate responses (not mock)
- ✅ Text responses have microphone button
- ✅ Microphone button plays TTS audio inline
- ✅ All operations logged with session context
- ✅ Graceful error handling throughout
- ✅ All services testable independently

---

## Next Steps

1. **Review this plan** - Confirm approach aligns with your vision
2. **Phase 1**: Verify `/image` command works
3. **Phase 2**: Build text generation service (headless)
4. **Phase 3**: Build TTS service (headless)
5. **Phase 4**: Build command router (headless)
6. **Phase 5**: Wire UI to services

Each phase is independent and testable before moving to the next.

---

## Documentation Created

- `SLASH_COMMANDS_ARCHITECTURE.md` - Detailed architecture design
- `IMPLEMENTATION_ROADMAP.md` - Step-by-step implementation guide
- `SLASH_COMMANDS_PLAN_SUMMARY.md` - This document

See these files for detailed implementation steps and code examples.

