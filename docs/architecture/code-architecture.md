# 🗺️ Architectural Overview - Auto-Generated

> **Purpose**: System architecture extracted from code comments
> **Source**: Auto-generated from @llm-map and @llm-type comments
> **Last Updated**: 2025-10-05 21:18:04

## Config Components

### vision-ai
**File**: `docker-compose.yml`
**Language**: yaml
**Purpose**: Docker service configuration for AI-powered image analysis microservice
**Architecture**: Part of microservices architecture, connects backend to vision processing capabilities
**Implementation**: Defines Python container with BLIP model, Flask HTTP server, and persistent model storage

## Service Components

### unknown
**File**: `services/vision-ai/main.py`
**Language**: python
**Purpose**: Provides AI-powered image analysis using BLIP vision model for user-uploaded content
**Architecture**: Entry point for vision processing pipeline, integrates with backend via HTTP API
**Implementation**: Loads BLIP model on startup, serves Flask HTTP API on port 8001, implements health checks

### AudioService
**File**: `frontend/src/services/AudioService.ts`
**Language**: typescript
**Purpose**: Provides frontend audio processing capabilities including speech-to-text transcription
**Architecture**: Frontend service layer, communicates with whisper-tts service on port 8000
**Implementation**: Uses Fetch API with FormData for audio upload, implements error handling and retry logic

### HttpVisionProcessingService
**File**: `backend/src/main/kotlin/com/unhinged/infrastructure/vision/HttpVisionProcessingService.kt`
**Language**: kotlin
**Purpose**: Enables backend to request AI-powered image analysis from vision-ai microservice
**Architecture**: Infrastructure layer implementation, called by application services, connects to vision-ai on port 8001
**Implementation**: Uses Ktor HTTP client with JSON serialization, implements retry logic and error handling

## Function Components

### start_flask_server
**File**: `services/vision-ai/main.py`
**Language**: python
**Purpose**: Starts Flask HTTP server to handle image analysis requests from backend
**Architecture**: Called by main thread, serves HTTP endpoints defined in app.py
**Implementation**: Binds to all interfaces on port 8001, disables debug mode for production

### formData
**File**: `frontend/src/services/AudioService.ts`
**Language**: typescript
**Purpose**: Converts user audio recordings to text using AI speech recognition
**Architecture**: Core transcription function called by UI components, integrates with whisper-tts service
**Implementation**: Creates FormData with audio blob, sends POST to whisper service, handles JSON response
