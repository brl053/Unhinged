# 🏗️ Project Structure - Unhinged Platform

> **Purpose**: Comprehensive overview of project organization and components
> **Audience**: Developers and AI assistants working on the platform
> **Last Updated**: Auto-generated on 2025-10-18 18:37:59

## 📊 Project Overview

- **Total Files**: 570
- **Services**: 10
- **Key Files**: 42

### File Type Distribution
```
.kt               185 files
.md                69 files
.ts                65 files
.py                38 files
.c                 34 files
.sh                26 files
.proto             26 files
.json              18 files
no_extension       18 files
.tsx               18 files
```

## 🚀 Services

### multimodal-orchestrator
- **Type**: Python Service
- **Language**: Python
- **Path**: `services/multimodal-orchestrator`
- **Dockerized**: ✅
- **Tests**: ❌

### api-gateway
- **Type**: Python Service
- **Language**: Python
- **Path**: `services/api-gateway`
- **Dockerized**: ✅
- **Tests**: ❌

### vision-ai-enhanced
- **Type**: Python Service
- **Language**: Python
- **Path**: `services/vision-ai-enhanced`
- **Dockerized**: ✅
- **Tests**: ❌

### context-llm
- **Type**: Python Service
- **Language**: Python
- **Path**: `services/context-llm`
- **Dockerized**: ✅
- **Tests**: ❌

### presentation-gateway
- **Type**: Node.js Service
- **Language**: JavaScript/TypeScript
- **Path**: `services/presentation-gateway`
- **Dockerized**: ❌
- **Tests**: ❌

### whisper-tts
- **Type**: Python Service
- **Language**: Python
- **Path**: `services/whisper-tts`
- **Dockerized**: ✅
- **Tests**: ❌
- **Description**: This service provides both Speech-to-Text (STT) and Text-to-Speech (TTS) capabilities for the Unhing

### vision-ai
- **Type**: Python Service
- **Language**: Python
- **Path**: `services/vision-ai`
- **Dockerized**: ✅
- **Tests**: ❌
- **Description**: This service provides image analysis, description, and processing capabilities for the Unhinged proj

### backend
- **Type**: Kotlin Service
- **Language**: Kotlin
- **Path**: `backend`
- **Dockerized**: ✅
- **Tests**: ❌
- **Description**: This is the Kotlin backend for the Unhinged multimodal AI platform, built with **Ktor** and **gRPC**

### frontend
- **Type**: Node.js Service
- **Language**: JavaScript/TypeScript
- **Path**: `frontend`
- **Dockerized**: ✅
- **Tests**: ✅

### llm
- **Type**: unknown
- **Language**: unknown
- **Path**: `llm`
- **Dockerized**: ✅
- **Tests**: ❌

## 🧩 Components

### backend
- **Description**: Backend API and business logic
- **Files**: 208
- **Subdirectories**: 4

### frontend
- **Description**: Frontend user interface
- **Files**: 7997
- **Subdirectories**: 7

### services
- **Description**: Microservices and external integrations
- **Files**: 40
- **Subdirectories**: 7

### proto
- **Description**: Protocol buffer definitions
- **Files**: 29
- **Subdirectories**: 1

### docs
- **Description**: Project documentation
- **Files**: 48
- **Subdirectories**: 14

### scripts
- **Description**: Build and automation scripts
- **Files**: 34
- **Subdirectories**: 2

### infrastructure
- **Description**: Infrastructure as code
- **Files**: 1
- **Subdirectories**: 1

## 📋 Key Files

- **Makefile** (`Makefile`) - Build automation and development commands
- **docker-compose.yml** (`docker-compose.yml`) - Service orchestration configuration
- **package.json** (`package.json`) - Node.js dependencies and scripts
- **README.md** (`README.md`) - Project overview and setup instructions
- **README.md** (`docs/README.md`) - Project overview and setup instructions
- **README.md** (`docs/roadmap/README.md`) - Project overview and setup instructions
- **package.json** (`shared/events/package.json`) - Node.js dependencies and scripts
- **README.md** (`shared/events/README.md`) - Project overview and setup instructions
- **package.json** (`frontend/package.json`) - Node.js dependencies and scripts
- **Dockerfile** (`frontend/Dockerfile`) - Container build instructions
- **README.md** (`.augment/README.md`) - Project overview and setup instructions
- **requirements.txt** (`services/multimodal-orchestrator/requirements.txt`) - Python dependencies
- **Dockerfile** (`services/multimodal-orchestrator/Dockerfile`) - Container build instructions
- **requirements.txt** (`services/api-gateway/requirements.txt`) - Python dependencies
- **Dockerfile** (`services/api-gateway/Dockerfile`) - Container build instructions
- **requirements.txt** (`services/vision-ai-enhanced/requirements.txt`) - Python dependencies
- **Dockerfile** (`services/vision-ai-enhanced/Dockerfile`) - Container build instructions
- **requirements.txt** (`services/context-llm/requirements.txt`) - Python dependencies
- **Dockerfile** (`services/context-llm/Dockerfile`) - Container build instructions
- **package.json** (`services/presentation-gateway/package.json`) - Node.js dependencies and scripts
- **requirements.txt** (`services/whisper-tts/requirements.txt`) - Python dependencies
- **README.md** (`services/whisper-tts/README.md`) - Project overview and setup instructions
- **Dockerfile** (`services/whisper-tts/Dockerfile`) - Container build instructions
- **requirements.txt** (`services/vision-ai/requirements.txt`) - Python dependencies
- **README.md** (`services/vision-ai/README.md`) - Project overview and setup instructions
- **Dockerfile** (`services/vision-ai/Dockerfile`) - Container build instructions
- **README.md** (`scripts/docs/README.md`) - Project overview and setup instructions
- **README.md** (`scripts/python/README.md`) - Project overview and setup instructions
- **README.md** (`tools/README.md`) - Project overview and setup instructions
- **README.md** (`tools/dependency-tracker/README.md`) - Project overview and setup instructions
- **README.md** (`proto/README.md`) - Project overview and setup instructions
- **README.md** (`static_html/shared/README.md`) - Project overview and setup instructions
- **Dockerfile** (`database/Dockerfile`) - Container build instructions
- **README.md** (`packages/observability/README.md`) - Project overview and setup instructions
- **Dockerfile** (`llm/Dockerfile`) - Container build instructions
- **README.md** (`static-dashboard/README.md`) - Project overview and setup instructions
- **build.gradle.kts** (`backend/build.gradle.kts`) - Kotlin/Java build configuration
- **README.md** (`backend/README.md`) - Project overview and setup instructions
- **Dockerfile** (`backend/Dockerfile`) - Container build instructions
- **package.json** (`backend/cdc-service/package.json`) - Node.js dependencies and scripts
- **requirements.txt** (`backend/cdc-service/requirements.txt`) - Python dependencies
- **Dockerfile** (`backend/cdc-service/Dockerfile`) - Container build instructions

---

**Note**: This documentation is automatically generated from project analysis.
Run `make docs-update` to refresh after structural changes.