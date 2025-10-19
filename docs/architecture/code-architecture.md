# 🗺️ Architectural Overview - Auto-Generated

> **Purpose**: System architecture extracted from code comments
> **Source**: Auto-generated from @llm-map and @llm-type comments
> **Last Updated**: 2025-10-18 19:47:57

## Config Components

### vision-ai
**File**: `docker-compose.yml`
**Language**: yaml
**Purpose**: Docker service configuration for AI-powered image analysis microservice
**Architecture**: Part of microservices architecture, connects backend to vision processing capabilities
**Implementation**: Defines Python container with BLIP model, Flask HTTP server, and persistent model storage

## Service Components

### unknown
**File**: `build/llm_integration.py`
**Language**: python
**Purpose**: LLM integration for enhanced build system with context generation and error explanation
**Architecture**: LLM integration layer that connects build system with existing documentation system for enhanced developer experience
**Implementation**: Provides AI-powered build assistance, error explanation, and context generation for developer onboarding

### unknown
**File**: `build/cli.py`
**Language**: python
**Purpose**: Enhanced CLI interface for the Unhinged build system
**Architecture**: CLI layer that wraps the build orchestrator with enhanced user experience and developer tools
**Implementation**: Provides developer-friendly command-line interface with progress indicators, build status, and LLM integration

### unknown
**File**: `build/test_enhanced_system.py`
**Language**: python
**Purpose**: Test suite for the enhanced build system
**Architecture**: Test suite that validates all components of the enhanced build system
**Implementation**: Provides comprehensive testing and validation of the enhanced build system features

### unknown
**File**: `build/orchestrator.py`
**Language**: python
**Purpose**: Enhanced build orchestrator for Unhinged polyglot monorepo
**Architecture**: Central build coordination system that integrates with existing Makefile and Docker Compose workflows
**Implementation**: Provides intelligent dependency tracking, parallel execution, caching, and multi-language build coordination

### unknown
**File**: `build/monitoring.py`
**Language**: python
**Purpose**: Build performance monitoring and metrics collection system
**Architecture**: Performance monitoring system that tracks build metrics and provides optimization recommendations
**Implementation**: Provides comprehensive build performance tracking, caching analytics, and optimization insights

### unknown
**File**: `build/developer_experience.py`
**Language**: python
**Purpose**: Developer experience enhancements for the enhanced build system
**Architecture**: Developer experience layer that makes the build system more accessible and productive for developers
**Implementation**: Provides developer-friendly features like progress indicators, quick commands, and better error messages

### unknown
**File**: `build/build.py`
**Language**: python
**Purpose**: Main entry point for the enhanced Unhinged build system
**Architecture**: Entry point script that integrates enhanced build system with existing workflows
**Implementation**: Provides unified access to enhanced build orchestration with backward compatibility

### unknown
**File**: `build/modules/typescript_builder.py`
**Language**: python
**Purpose**: TypeScript/npm build module with webpack optimization and hot reloading
**Architecture**: TypeScript build module that integrates with npm/webpack build system and provides enhanced caching
**Implementation**: Provides optimized npm builds with webpack, hot module replacement, and intelligent caching

### unknown
**File**: `build/modules/python_builder.py`
**Language**: python
**Purpose**: Python build module with virtual environment management and dependency caching
**Architecture**: Python build module that integrates with pip/poetry build systems and provides enhanced caching
**Implementation**: Provides optimized Python builds with pip/poetry, virtual environments, and intelligent caching

### unknown
**File**: `build/modules/kotlin_builder.py`
**Language**: python
**Purpose**: Kotlin/Gradle build module with incremental compilation and caching
**Architecture**: Kotlin build module that integrates with Gradle build system and provides enhanced caching
**Implementation**: Provides optimized Gradle builds with parallel execution, incremental compilation, and intelligent caching

### AudioService
**File**: `frontend/src/services/AudioService.ts`
**Language**: typescript
**Purpose**: Provides frontend audio processing capabilities including speech-to-text transcription
**Architecture**: Frontend service layer, communicates with whisper-tts service on port 8000
**Implementation**: Uses Fetch API with FormData for audio upload, implements error handling and retry logic

### unknown
**File**: `services/vision-ai/main.py`
**Language**: python
**Purpose**: Provides AI-powered image analysis using BLIP vision model for user-uploaded content
**Architecture**: Entry point for vision processing pipeline, integrates with backend via HTTP API
**Implementation**: Loads BLIP model on startup, serves Flask HTTP API on port 8001, implements health checks

### HttpVisionProcessingService
**File**: `backend/temp-disabled/infrastructure/vision/HttpVisionProcessingService.kt`
**Language**: kotlin
**Purpose**: Enables backend to request AI-powered image analysis from vision-ai microservice
**Architecture**: Infrastructure layer implementation, called by application services, connects to vision-ai on port 8001
**Implementation**: Uses Ktor HTTP client with JSON serialization, implements retry logic and error handling

## Contract Components

### unknown
**File**: `build/modules/__init__.py`
**Language**: python
**Purpose**: Language-specific build modules for enhanced build orchestration
**Architecture**: Build module system that integrates with main orchestrator for multi-language support
**Implementation**: Provides specialized builders for Kotlin, TypeScript, Python, and Protobuf with caching and optimization

## Function Components

### formData
**File**: `frontend/src/services/AudioService.ts`
**Language**: typescript
**Purpose**: Converts user audio recordings to text using AI speech recognition
**Architecture**: Core transcription function called by UI components, integrates with whisper-tts service
**Implementation**: Creates FormData with audio blob, sends POST to whisper service, handles JSON response

### start_flask_server
**File**: `services/vision-ai/main.py`
**Language**: python
**Purpose**: Starts Flask HTTP server to handle image analysis requests from backend
**Architecture**: Called by main thread, serves HTTP endpoints defined in app.py
**Implementation**: Binds to all interfaces on port 8001, disables debug mode for production

## Validator Components

### test_parse_llm_tags_with_context
**File**: `scripts/docs/test_llm_extraction.py`
**Language**: python
**Purpose**: Validates user input
**Architecture**: Part of validation pipeline
**Implementation**: Checks format and business rules
