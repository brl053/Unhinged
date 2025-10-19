# 🏛️ Code Philosophy - Unhinged Platform

> **Purpose**: Fundamental design principles extracted from codebase
> **Source**: Auto-generated from @llm-axiom and @llm-token comments
> **Last Updated**: 2025-10-18 18:37:59

## 🎯 Fundamental Axioms

These are the non-negotiable principles that guide all development:

### vision-ai (yaml)
**File**: `docker-compose.yml`
**Axiom**: Vision service must be accessible on port 8001 for backend integration
**Context**: Docker service configuration for AI-powered image analysis microservice

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
