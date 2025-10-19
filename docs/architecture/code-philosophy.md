# 🏛️ Code Philosophy - Unhinged Platform

> **Purpose**: Fundamental design principles extracted from codebase
> **Source**: Auto-generated from @llm-axiom and @llm-token comments
> **Last Updated**: 2025-10-18 19:47:57

## 🎯 Fundamental Axioms

These are the non-negotiable principles that guide all development:

### vision-ai (yaml)
**File**: `docker-compose.yml`
**Axiom**: Vision service must be accessible on port 8001 for backend integration
**Context**: Docker service configuration for AI-powered image analysis microservice

### unknown (python)
**File**: `build/llm_integration.py`
**Axiom**: LLM integration must provide helpful, accurate, and contextual assistance without overwhelming developers
**Context**: LLM integration for enhanced build system with context generation and error explanation

### unknown (python)
**File**: `build/cli.py`
**Axiom**: CLI must provide clear feedback, helpful error messages, and efficient developer workflows
**Context**: Enhanced CLI interface for the Unhinged build system

### unknown (python)
**File**: `build/test_enhanced_system.py`
**Axiom**: Tests must be comprehensive, fast, and provide clear feedback on system health
**Context**: Test suite for the enhanced build system

### unknown (python)
**File**: `build/orchestrator.py`
**Axiom**: Build operations must be deterministic, cacheable, and provide clear feedback to developers
**Context**: Enhanced build orchestrator for Unhinged polyglot monorepo

### unknown (python)
**File**: `build/monitoring.py`
**Axiom**: Performance monitoring must be lightweight and provide actionable insights for developers
**Context**: Build performance monitoring and metrics collection system

### unknown (python)
**File**: `build/developer_experience.py`
**Axiom**: Developer experience must reduce friction and provide clear, actionable feedback
**Context**: Developer experience enhancements for the enhanced build system

### unknown (python)
**File**: `build/build.py`
**Axiom**: Build system must maintain backward compatibility while providing enhanced features
**Context**: Main entry point for the enhanced Unhinged build system

### unknown (python)
**File**: `build/modules/typescript_builder.py`
**Axiom**: TypeScript builds must support hot reloading for development and optimization for production
**Context**: TypeScript/npm build module with webpack optimization and hot reloading

### unknown (python)
**File**: `build/modules/__init__.py`
**Axiom**: Each language builder must provide consistent interface and caching capabilities
**Context**: Language-specific build modules for enhanced build orchestration

### unknown (python)
**File**: `build/modules/python_builder.py`
**Axiom**: Python builds must use isolated virtual environments and cache dependencies effectively
**Context**: Python build module with virtual environment management and dependency caching

### unknown (python)
**File**: `build/modules/kotlin_builder.py`
**Axiom**: Gradle builds must be deterministic and support incremental compilation for fast development
**Context**: Kotlin/Gradle build module with incremental compilation and caching

### AudioService (typescript)
**File**: `frontend/src/services/AudioService.ts`
**Axiom**: All audio operations must provide user feedback and handle network failures gracefully
**Context**: Provides frontend audio processing capabilities including speech-to-text transcription

### unknown (python)
**File**: `services/vision-ai/main.py`
**Axiom**: Vision model must be loaded and ready before accepting any processing requests
**Context**: Provides AI-powered image analysis using BLIP vision model for user-uploaded content

### test_parse_llm_tags_with_context (python)
**File**: `scripts/docs/test_llm_extraction.py`
**Axiom**: Never trust user input
**Context**: Validates user input

### HttpVisionProcessingService (kotlin)
**File**: `backend/temp-disabled/infrastructure/vision/HttpVisionProcessingService.kt`
**Axiom**: All HTTP calls must have timeouts and proper error handling to prevent system hangs
**Context**: Enables backend to request AI-powered image analysis from vision-ai microservice

## 📚 Domain Vocabulary

Project-specific terminology and concepts:

### vision-ai
**Definition**: vision-models: Docker volume for persistent transformer model cache
**Source**: `docker-compose.yml` (yaml)

### unknown
**Definition**: llm-build-integration: AI-powered assistance for build system operations
**Source**: `build/llm_integration.py` (python)

### unknown
**Definition**: build-cli: Command-line interface for enhanced build system
**Source**: `build/cli.py` (python)

### unknown
**Definition**: build-test: Comprehensive test suite for enhanced build system
**Source**: `build/test_enhanced_system.py` (python)

### unknown
**Definition**: build-orchestrator: Python service coordinating all build operations across languages
**Source**: `build/orchestrator.py` (python)

### unknown
**Definition**: build-monitoring: Performance tracking and analytics for build system
**Source**: `build/monitoring.py` (python)

### unknown
**Definition**: dev-experience: Developer productivity enhancements for build system
**Source**: `build/developer_experience.py` (python)

### unknown
**Definition**: build-entry: Main entry point for enhanced build system
**Source**: `build/build.py` (python)

### unknown
**Definition**: typescript-builder: npm/webpack-based build module for TypeScript/React projects
**Source**: `build/modules/typescript_builder.py` (python)

### unknown
**Definition**: build-modules: Specialized build handlers for different programming languages
**Source**: `build/modules/__init__.py` (python)

### unknown
**Definition**: python-builder: pip/poetry-based build module for Python services
**Source**: `build/modules/python_builder.py` (python)

### unknown
**Definition**: kotlin-builder: Gradle-based build module for Kotlin/JVM projects
**Source**: `build/modules/kotlin_builder.py` (python)

### AudioService
**Definition**: whisper-service: Python microservice providing speech-to-text capabilities
**Source**: `frontend/src/services/AudioService.ts` (typescript)

### unknown
**Definition**: BLIP: Bootstrapping Language-Image Pre-training model for image captioning
**Source**: `services/vision-ai/main.py` (python)

### test_parse_llm_tags_with_context
**Definition**: user-validator
**Source**: `scripts/docs/test_llm_extraction.py` (python)

### HttpVisionProcessingService
**Definition**: vision-ai-service: Python microservice running BLIP model for image analysis
**Source**: `backend/temp-disabled/infrastructure/vision/HttpVisionProcessingService.kt` (kotlin)
