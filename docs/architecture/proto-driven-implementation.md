# Proto-Driven Implementation Plan

## Overview

The proto contracts are the source of truth for our system architecture. The existing `audio.proto` defines a comprehensive gRPC service that we must implement following clean architecture principles.

## Proto Contract Analysis

### Existing Audio Service Contract

The `audio.proto` defines a sophisticated audio processing service with:

**Core Services:**
- `TextToSpeech(TTSRequest) returns (stream StreamChunk)` - Streaming TTS
- `SpeechToText(stream StreamChunk) returns (STTResponse)` - Streaming STT  
- `ProcessAudioFile(ProcessAudioRequest) returns (ProcessAudioResponse)` - Batch processing
- Voice management (ListVoices, GetVoice, CreateCustomVoice)
- Audio utilities (ConvertAudioFormat, AnalyzeAudio)
- Standard health checks

**Key Features:**
- Uses `common.v1.StreamChunk` for universal streaming pattern
- Leverages `common.v1.ResourceMetadata` for consistent resource management
- Supports multiple audio formats (WAV, MP3, OGG, FLAC, PCM, OPUS, AAC)
- Advanced audio processing (effects, quality levels, metadata)
- Voice customization and management
- Comprehensive usage tracking with `common.v1.AudioUsage`

## Implementation Strategy

### Phase 1: gRPC Service Implementation (Clean Architecture)

#### 1.1 Domain Layer
```kotlin
// backend/src/main/kotlin/com/unhinged/domain/audio/
├── entities/
│   ├── AudioTranscription.kt    # Core transcription entity
│   ├── AudioSynthesis.kt        # Core synthesis entity
│   ├── Voice.kt                 # Voice entity
│   └── AudioSession.kt          # Processing session
├── services/
│   ├── AudioProcessingService.kt # Domain service interface
│   └── VoiceManagementService.kt # Voice domain service
└── repositories/
    ├── AudioRepository.kt       # Audio data interface
    └── VoiceRepository.kt       # Voice data interface
```

**Domain Entities (Proto-Aligned):**
```kotlin
data class AudioTranscription(
    val id: String,
    val transcript: String,
    val confidence: Float,
    val segments: List<TranscriptSegment>,
    val metadata: STTMetadata,
    val usage: AudioUsage
)

data class AudioSynthesis(
    val id: String,
    val text: String,
    val voiceId: String,
    val audioData: ByteArray,
    val format: AudioFormat,
    val usage: AudioUsage
)
```

#### 1.2 Application Layer
```kotlin
// backend/src/main/kotlin/com/unhinged/application/audio/
├── usecases/
│   ├── TextToSpeechUseCase.kt   # TTS business logic
│   ├── SpeechToTextUseCase.kt   # STT business logic
│   ├── ProcessAudioFileUseCase.kt # Batch processing
│   └── VoiceManagementUseCase.kt # Voice operations
└── services/
    └── AudioApplicationService.kt # Orchestration layer
```

**Use Cases (Proto-Aligned):**
```kotlin
class TextToSpeechUseCase(
    private val audioProcessingService: AudioProcessingService,
    private val voiceRepository: VoiceRepository
) {
    suspend fun execute(request: TTSRequest): Flow<StreamChunk> {
        // Validate voice exists
        // Process text with domain service
        // Stream audio chunks following proto contract
    }
}
```

#### 1.3 Infrastructure Layer
```kotlin
// backend/src/main/kotlin/com/unhinged/infrastructure/audio/
├── grpc/
│   └── AudioServiceImpl.kt      # gRPC service implementation
├── clients/
│   └── WhisperTtsClient.kt      # HTTP client to Python service
├── repositories/
│   ├── InMemoryAudioRepository.kt
│   └── InMemoryVoiceRepository.kt
└── config/
    └── AudioConfiguration.kt
```

**gRPC Service Implementation:**
```kotlin
@Service
class AudioServiceImpl(
    private val textToSpeechUseCase: TextToSpeechUseCase,
    private val speechToTextUseCase: SpeechToTextUseCase
) : AudioServiceGrpcKt.AudioServiceCoroutineImplBase() {

    override fun textToSpeech(request: TTSRequest): Flow<StreamChunk> {
        return textToSpeechUseCase.execute(request)
    }

    override suspend fun speechToText(requests: Flow<StreamChunk>): STTResponse {
        return speechToTextUseCase.execute(requests)
    }
}
```

#### 1.4 Presentation Layer
```kotlin
// backend/src/main/kotlin/com/unhinged/presentation/grpc/
├── AudioGrpcController.kt       # gRPC endpoint configuration
└── interceptors/
    ├── AudioAuthInterceptor.kt  # Authentication
    └── AudioMetricsInterceptor.kt # Usage tracking
```

### Phase 2: Python Service Integration

#### 2.1 Extract Whisper Service (Proto-Compliant)
```python
# services/whisper-tts/
├── app.py                       # Flask app (temporary bridge)
├── grpc_server.py              # gRPC server implementation
├── audio_processor.py          # Core processing logic
└── proto/                      # Generated Python proto files
    ├── audio_pb2.py
    ├── audio_pb2_grpc.py
    └── common_pb2.py
```

**gRPC Server Implementation:**
```python
class AudioServiceServicer(audio_pb2_grpc.AudioServiceServicer):
    def TextToSpeech(self, request, context):
        # Implement streaming TTS following proto contract
        for chunk in self._synthesize_streaming(request):
            yield chunk
    
    def SpeechToText(self, request_iterator, context):
        # Implement streaming STT following proto contract
        audio_chunks = []
        for chunk in request_iterator:
            audio_chunks.append(chunk.data)
        return self._transcribe_audio(audio_chunks)
```

#### 2.2 Service Communication Architecture
```
┌─────────────────┐    gRPC     ┌─────────────────┐
│   Kotlin        │◄───────────►│   Python        │
│   Backend       │             │   Whisper-TTS   │
│   (Clean Arch)  │             │   Service       │
└─────────────────┘             └─────────────────┘
        │                               │
        │ HTTP/REST                     │ gRPC
        ▼                               ▼
┌─────────────────┐             ┌─────────────────┐
│   Frontend      │             │   Proto         │
│   React/TS      │             │   Contracts     │
└─────────────────┘             └─────────────────┘
```

### Phase 3: Frontend Integration

#### 3.1 gRPC-Web Client
```typescript
// frontend/src/services/grpc/
├── AudioServiceClient.ts       # gRPC-Web client
├── proto/                      # Generated TypeScript files
│   ├── audio_pb.ts
│   ├── audio_grpc_web_pb.ts
│   └── common_pb.ts
└── streaming/
    └── AudioStreamManager.ts   # Stream management
```

**gRPC-Web Client:**
```typescript
export class AudioServiceClient {
    private client: AudioServiceClient;

    async textToSpeech(request: TTSRequest): Promise<ReadableStream<StreamChunk>> {
        const stream = this.client.textToSpeech(request);
        return this.convertToWebStream(stream);
    }

    async speechToText(audioStream: ReadableStream<Uint8Array>): Promise<STTResponse> {
        const chunks = this.convertToGrpcStream(audioStream);
        return this.client.speechToText(chunks);
    }
}
```

#### 3.2 React Components (Proto-Aligned)
```typescript
// frontend/src/components/audio/
├── VoiceInput/
│   ├── VoiceInput.tsx          # STT component
│   └── useVoiceInput.ts        # gRPC streaming hook
├── AudioPlayer/
│   ├── AudioPlayer.tsx         # TTS playback
│   └── useAudioSynthesis.ts    # gRPC TTS hook
└── VoiceSelector/
    ├── VoiceSelector.tsx       # Voice management UI
    └── useVoiceManagement.ts   # Voice gRPC operations
```

### Phase 4: Docker & Service Orchestration

#### 4.1 Service Configuration
```yaml
# docker-compose.yml
services:
  backend:
    build: ./backend
    ports:
      - "8080:8080"  # HTTP/REST
      - "9090:9090"  # gRPC
    environment:
      - AUDIO_SERVICE_HOST=whisper-tts:9091
  
  whisper-tts:
    build: ./services/whisper-tts
    ports:
      - "9091:9091"  # gRPC
    environment:
      - WHISPER_MODEL=base
      - GRPC_PORT=9091
```

#### 4.2 Proto Generation Pipeline
```bash
# proto/build.sh
#!/bin/bash

# Generate Kotlin files
protoc --kotlin_out=../backend/src/main/kotlin \
       --grpc-kotlin_out=../backend/src/main/kotlin \
       *.proto

# Generate Python files  
protoc --python_out=../services/whisper-tts \
       --grpc_python_out=../services/whisper-tts \
       *.proto

# Generate TypeScript files
protoc --js_out=import_style=commonjs:../frontend/src/proto \
       --grpc-web_out=import_style=typescript,mode=grpcwebtext:../frontend/src/proto \
       *.proto
```

## Implementation Timeline

### Week 1: Core gRPC Infrastructure
- Generate proto files for all languages
- Implement Kotlin gRPC service (clean architecture)
- Create Python gRPC server (extract from Flask)
- Basic streaming TTS/STT functionality

### Week 2: Advanced Features
- Voice management system
- Audio format conversion
- Usage tracking and metrics
- Error handling and health checks

### Week 3: Frontend Integration
- gRPC-Web client implementation
- React components with streaming
- Voice selection and management UI
- End-to-end testing

### Week 4: Production Readiness
- Docker orchestration
- Monitoring and observability
- Performance optimization
- Documentation and deployment

## Success Criteria

1. **Proto Compliance**: All implementations strictly follow proto contracts
2. **Clean Architecture**: Domain logic independent of gRPC infrastructure
3. **Streaming Performance**: Sub-100ms latency for audio streaming
4. **Type Safety**: Full type safety from proto to UI
5. **Testability**: All layers testable in isolation

This approach ensures we build a robust, scalable audio system that follows both clean architecture principles and gRPC best practices, with the proto contracts as our single source of truth.
