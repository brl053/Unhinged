# Slash Commands Implementation Roadmap

## Phase 1: Verify /image Command (Immediate)

**Goal**: Ensure existing `/image` command works end-to-end

**Tasks**:
1. Test `/image draft` in GTK4 UI
2. Verify image generates and displays in chat
3. Check error handling and logging
4. Document any issues

**Expected Output**: Working `/image` command with proper error handling

---

## Phase 2: Text Generation Service (Headless)

**Goal**: Create reusable text generation service with proper data contracts

**Step 1: Define Proto Schemas**
- File: `proto/text_generation.proto`
- Define `TextGenerationRequest` and `TextGenerationResponse`
- Include metadata: tokens, generation_time, model_info

**Step 2: Create Service**
- File: `libs/services/text_generation_service.py`
- Class: `TextGenerationService`
- Methods:
  - `__init__()` - Initialize (no model loading yet)
  - `generate_text(prompt, max_tokens=100, temperature=0.7)` - Generate text
  - `_load_model()` - Lazy load LLM model
  - `_unload_model()` - Memory cleanup

**Step 3: Implementation Details**
- Use same pattern as `ImageGenerationService`
- Lazy load model on first call
- Support multiple models (future)
- Return structured response with metadata
- Handle GPU/CPU fallback

**Step 4: Test Headless**
```python
from libs.services import TextGenerationService
service = TextGenerationService()
result = service.generate_text("Write a haiku about code")
print(result)  # Should print structured response
```

**Expected Output**: Working text generation service, testable independently

---

## Phase 3: TTS Service (Headless)

**Goal**: Create text-to-speech service with audio output

**Step 1: Define Proto Schemas**
- File: `proto/tts.proto`
- Define `TextToSpeechRequest` and `TextToSpeechResponse`
- Include metadata: duration, audio_format, voice_id

**Step 2: Create Service**
- File: `libs/services/tts_service.py`
- Class: `TextToSpeechService`
- Methods:
  - `synthesize(text, voice_id="default", speed=1.0)` - Generate audio
  - `_get_available_voices()` - List voices (future)
  - `_save_audio(audio_bytes, format)` - Save to temp file

**Step 3: Implementation Details**
- Use system TTS: `espeak` (simple, available on Linux)
- Alternative: `pyttsx3` (Python library, cross-platform)
- Output to `/build/tmp/tts_audio/` with timestamp
- Return audio path + metadata
- Handle errors gracefully

**Step 4: Test Headless**
```python
from libs.services import TextToSpeechService
service = TextToSpeechService()
result = service.synthesize("Hello world")
print(result)  # Should print audio path and metadata
```

**Expected Output**: Working TTS service, audio files generated

---

## Phase 4: Slash Command Router (Headless)

**Goal**: Parse and route slash commands to appropriate services

**Step 1: Define Proto Schemas**
- File: `proto/slash_commands.proto`
- Define `SlashCommandRequest` and `SlashCommandResponse`
- Include command_name, arguments, flags, result_type

**Step 2: Create Router**
- File: `libs/services/slash_command_router.py`
- Class: `SlashCommandRouter`
- Methods:
  - `route(command_string)` - Parse and route command
  - `_parse_command(command_string)` - Extract command and args
  - `_execute_command(command_name, args)` - Route to service

**Step 3: Supported Commands**
- `/image <prompt>` → ImageGenerationService
- `/text <prompt>` → TextGenerationService (future)
- `/tts <text>` → TextToSpeechService (future)

**Step 4: Test Headless**
```python
from libs.services import SlashCommandRouter
router = SlashCommandRouter()
result = router.route("/image a rubber duck")
print(result)  # Should print SlashCommandResponse
```

**Expected Output**: Working command router, all commands testable

---

## Phase 5: UI Integration (UI-First Planning, Headless Implementation)

**Goal**: Wire UI to use slash command services

**Step 1: Update ChatroomView**
- File: `control/gtk4_gui/views/chatroom_view.py`
- Modify `_on_send_clicked()` to detect slash commands
- Use `SlashCommandRouter` to process commands
- Display results using appropriate widgets

**Step 2: Add Audio Player Widget**
- File: `control/gtk4_gui/components/audio_player_widget.py`
- Display audio player inline in chat
- Play/pause controls
- Duration display

**Step 3: Add Microphone Button**
- Add button to text responses
- Trigger TTS for response text
- Display audio player below response

**Step 4: Test End-to-End**
- Type `/image draft` → Image displays
- Type normal message → Text response + microphone button
- Click microphone → Audio plays

**Expected Output**: Fully functional slash commands with UI display

---

## Implementation Checklist

### Phase 1: Verify /image
- [ ] Test `/image draft` in UI
- [ ] Verify image displays
- [ ] Check error handling
- [ ] Document findings

### Phase 2: Text Generation
- [ ] Create `proto/text_generation.proto`
- [ ] Create `libs/services/text_generation_service.py`
- [ ] Implement lazy model loading
- [ ] Test headless
- [ ] Add to `libs/services/__init__.py`

### Phase 3: TTS
- [ ] Create `proto/tts.proto`
- [ ] Create `libs/services/tts_service.py`
- [ ] Implement audio generation
- [ ] Test headless
- [ ] Add to `libs/services/__init__.py`

### Phase 4: Router
- [ ] Create `proto/slash_commands.proto`
- [ ] Create `libs/services/slash_command_router.py`
- [ ] Implement command parsing
- [ ] Test headless
- [ ] Add to `libs/services/__init__.py`

### Phase 5: UI
- [ ] Update `chatroom_view.py`
- [ ] Create audio player widget
- [ ] Add microphone button
- [ ] Test end-to-end

---

## Key Principles

1. **Headless-First**: Each service works independently before UI integration
2. **Structured Responses**: All services return typed responses with metadata
3. **Lazy Loading**: Models load on first use
4. **Error Handling**: Graceful degradation with clear messages
5. **Simplicity**: No complex options, just works
6. **Session Context**: All operations logged with session_id

---

## Success Metrics

- ✅ All services testable independently
- ✅ All services return structured responses
- ✅ UI properly displays all result types
- ✅ Error handling works throughout
- ✅ Session logging captures all operations
- ✅ No external dependencies beyond system TTS

