# Audio Integration Plan - Clean Architecture Implementation

## Overview

This document outlines the systematic integration of audio features from the `feat/whisper-tts-integration` branch into our clean architecture foundation.

## Integration Strategy

### Phase 1: Core Audio Domain (Week 1)

#### 1.1 Domain Layer Implementation
```kotlin
// backend/src/main/kotlin/com/unhinged/domain/audio/
├── AudioDomain.kt           # Core audio entities
├── AudioProcessingService.kt # Pure business logic
└── AudioRepository.kt       # Repository interface
```

**Key Entities:**
- `AudioTranscription` - Speech-to-text results
- `AudioSynthesis` - Text-to-speech requests/results  
- `AudioSession` - Audio processing session
- `AudioFormat` - Supported audio formats and settings

#### 1.2 Application Layer Implementation
```kotlin
// backend/src/main/kotlin/com/unhinged/application/audio/
├── AudioUseCases.kt         # Audio use cases
├── TranscribeAudioUseCase.kt # STT use case
└── SynthesizeTextUseCase.kt  # TTS use case
```

**Use Cases:**
- `TranscribeAudioUseCase` - Convert speech to text
- `SynthesizeTextUseCase` - Convert text to speech
- `ProcessAudioSessionUseCase` - Manage audio sessions

#### 1.3 Infrastructure Layer Implementation
```kotlin
// backend/src/main/kotlin/com/unhinged/infrastructure/audio/
├── WhisperTtsClient.kt      # HTTP client for Python service
├── AudioFileRepository.kt   # File storage implementation
└── AudioConfigurationService.kt # Configuration management
```

### Phase 2: Whisper TTS Service Integration (Week 1-2)

#### 2.1 Extract Python Service
```bash
# Copy from feat/whisper-tts-integration branch
services/whisper-tts/
├── app.py                   # Flask application
├── requirements.txt         # Python dependencies
├── Dockerfile              # Container configuration
└── health_check.py         # Health monitoring
```

#### 2.2 Clean Architecture Integration
```kotlin
// Infrastructure layer implementation
class WhisperTtsClient(
    private val httpClient: HttpClient,
    private val configuration: AudioConfiguration
) : AudioProcessingService {
    
    override suspend fun transcribeAudio(audio: AudioFile): AudioTranscription {
        // HTTP client implementation following clean architecture
    }
    
    override suspend fun synthesizeText(text: String, language: String): AudioFile {
        // HTTP client implementation following clean architecture
    }
}
```

#### 2.3 Presentation Layer Endpoints
```kotlin
// backend/src/main/kotlin/com/unhinged/presentation/http/AudioController.kt
class AudioController(private val audioUseCases: AudioUseCases) {
    fun configureRoutes(routing: Routing) {
        routing.route("/api/v1/audio") {
            post("/transcribe") { /* STT endpoint */ }
            post("/synthesize") { /* TTS endpoint */ }
            get("/health") { /* Health check */ }
        }
    }
}
```

### Phase 3: Frontend Audio Components (Week 2)

#### 3.1 Extract VoiceInput Component
```typescript
// frontend/src/components/audio/
├── VoiceInput/
│   ├── VoiceInput.tsx       # Main component
│   ├── VoiceInput.styles.ts # Styled components
│   └── VoiceInput.types.ts  # TypeScript types
├── AudioPlayer/
│   ├── AudioPlayer.tsx      # Audio playback component
│   └── AudioPlayer.styles.ts
└── hooks/
    ├── useVoiceRecorder.ts  # Recording hook
    ├── useAudioSynthesis.ts # TTS hook
    └── useAudioPlayback.ts  # Playback hook
```

#### 3.2 Service Layer Integration
```typescript
// frontend/src/services/AudioService.ts
export class AudioService {
    async transcribeAudio(audioBlob: Blob): Promise<TranscriptionResult> {
        // Clean service implementation
    }
    
    async synthesizeText(text: string, language?: string): Promise<AudioBlob> {
        // Clean service implementation
    }
}
```

#### 3.3 React Query Integration
```typescript
// frontend/src/queries/audioQueries.ts
export const useTranscribeAudio = () => {
    return useMutation({
        mutationFn: (audioBlob: Blob) => audioService.transcribeAudio(audioBlob),
        // Error handling and caching
    });
};

export const useSynthesizeText = () => {
    return useMutation({
        mutationFn: (request: SynthesisRequest) => audioService.synthesizeText(request.text, request.language),
        // Error handling and caching
    });
};
```

### Phase 4: Docker Integration (Week 2-3)

#### 4.1 Service Orchestration
```yaml
# docker-compose.yml updates
services:
  whisper-tts:
    build: ./services/whisper-tts
    container_name: whisper-tts-service
    environment:
      - WHISPER_MODEL=base
      - TTS_ENGINE=gtts
    ports:
      - "8000:8000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

#### 4.2 Environment Configuration
```kotlin
// backend/src/main/kotlin/com/unhinged/infrastructure/config/AudioConfiguration.kt
@ConfigurationProperties("audio")
data class AudioConfiguration(
    val whisperTtsHost: String = "http://localhost:8000",
    val defaultLanguage: String = "en",
    val maxAudioDuration: Duration = Duration.ofMinutes(5),
    val supportedFormats: List<String> = listOf("wav", "mp3", "m4a")
)
```

### Phase 5: Testing Integration (Week 3)

#### 5.1 Backend Tests
```kotlin
// backend/src/test/kotlin/com/unhinged/
├── domain/audio/AudioDomainTest.kt
├── application/audio/AudioUseCasesTest.kt
├── infrastructure/audio/WhisperTtsClientTest.kt
└── presentation/http/AudioControllerTest.kt
```

#### 5.2 Frontend Tests
```typescript
// frontend/src/components/audio/__tests__/
├── VoiceInput.test.tsx
├── AudioPlayer.test.tsx
└── audioService.test.ts
```

#### 5.3 Integration Tests
```typescript
// frontend/tests/audio/
├── audio-pipeline.spec.ts   # End-to-end audio testing
├── tts-stt-roundtrip.spec.ts # Round-trip validation
└── audio-error-handling.spec.ts # Error scenarios
```

## Implementation Guidelines

### Clean Architecture Principles

1. **Domain Independence**: Audio domain logic has no external dependencies
2. **Dependency Inversion**: Infrastructure depends on domain interfaces
3. **Single Responsibility**: Each layer has clear, focused responsibilities
4. **Testability**: All layers can be tested in isolation

### Error Handling Strategy

```kotlin
// Domain layer error types
sealed class AudioError : Exception() {
    object TranscriptionFailed : AudioError()
    object SynthesisFailed : AudioError()
    object UnsupportedFormat : AudioError()
    object ServiceUnavailable : AudioError()
}
```

### Configuration Management

```yaml
# application.yml
audio:
  whisper-tts-host: ${WHISPER_TTS_HOST:http://localhost:8000}
  default-language: ${AUDIO_DEFAULT_LANGUAGE:en}
  max-duration: ${AUDIO_MAX_DURATION:PT5M}
  supported-formats:
    - wav
    - mp3
    - m4a
```

## Success Metrics

### Technical Metrics
- All audio features working with clean architecture
- 100% test coverage for audio domain logic
- Sub-500ms response times for TTS/STT
- Zero architectural violations

### User Experience Metrics
- Seamless voice input in chat interface
- Audio playback for AI responses
- Proper error handling and user feedback
- Accessibility compliance for audio features

## Risk Mitigation

### Technical Risks
1. **Performance**: Audio processing can be CPU intensive
   - **Mitigation**: Async processing, proper resource management
2. **Dependencies**: Python service adds complexity
   - **Mitigation**: Health checks, circuit breaker pattern
3. **File Storage**: Audio files require storage management
   - **Mitigation**: Temporary file cleanup, size limits

### Integration Risks
1. **Architecture Violations**: Temptation to bypass clean architecture
   - **Mitigation**: Code reviews, architectural tests
2. **Testing Complexity**: Audio testing is challenging
   - **Mitigation**: Mock services, synthetic audio files
3. **Configuration Drift**: Multiple services need coordination
   - **Mitigation**: Centralized configuration, environment validation

## Timeline

- **Week 1**: Domain and Application layers, Python service extraction
- **Week 2**: Infrastructure integration, Frontend components
- **Week 3**: Testing, Documentation, Polish
- **Week 4**: Production deployment, Monitoring setup

This plan ensures we get the valuable audio features while maintaining the clean architecture principles that make the codebase maintainable and scalable.
