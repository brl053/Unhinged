# 🏛️ Code Philosophy - Unhinged Platform

> **Purpose**: Fundamental design principles extracted from codebase
> **Source**: Auto-generated from @llm-axiom and @llm-token comments
> **Last Updated**: 2025-10-05 21:18:04

## 🎯 Fundamental Axioms

These are the non-negotiable principles that guide all development:

### vision-ai (yaml)
**File**: `docker-compose.yml`
**Axiom**: Vision service must be accessible on port 8001 for backend integration
**Context**: Docker service configuration for AI-powered image analysis microservice

### unknown (python)
**File**: `services/vision-ai/main.py`
**Axiom**: Vision model must be loaded and ready before accepting any processing requests
**Context**: Provides AI-powered image analysis using BLIP vision model for user-uploaded content

### AudioService (typescript)
**File**: `frontend/src/services/AudioService.ts`
**Axiom**: All audio operations must provide user feedback and handle network failures gracefully
**Context**: Provides frontend audio processing capabilities including speech-to-text transcription

### HttpVisionProcessingService (kotlin)
**File**: `backend/src/main/kotlin/com/unhinged/infrastructure/vision/HttpVisionProcessingService.kt`
**Axiom**: All HTTP calls must have timeouts and proper error handling to prevent system hangs
**Context**: Enables backend to request AI-powered image analysis from vision-ai microservice

## 📚 Domain Vocabulary

Project-specific terminology and concepts:

### vision-ai
**Definition**: vision-models: Docker volume for persistent transformer model cache
**Source**: `docker-compose.yml` (yaml)

### unknown
**Definition**: BLIP: Bootstrapping Language-Image Pre-training model for image captioning
**Source**: `services/vision-ai/main.py` (python)

### AudioService
**Definition**: whisper-service: Python microservice providing speech-to-text capabilities
**Source**: `frontend/src/services/AudioService.ts` (typescript)

### HttpVisionProcessingService
**Definition**: vision-ai-service: Python microservice running BLIP model for image analysis
**Source**: `backend/src/main/kotlin/com/unhinged/infrastructure/vision/HttpVisionProcessingService.kt` (kotlin)
