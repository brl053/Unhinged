# 🏗️ Project Structure - Unhinged Platform

> **Purpose**: Comprehensive overview of project organization and components
> **Audience**: Developers and AI assistants working on the platform
> **Last Updated**: Auto-generated on 2025-10-05 21:18:04

## 📊 Project Overview

- **Total Files**: 685
- **Services**: 7
- **Key Files**: 29

### File Type Distribution
```
.kt               386 files
.ts                68 files
.md                64 files
.proto             21 files
.py                20 files
.json              19 files
.tsx               17 files
no_extension       15 files
.sh                12 files
.js                10 files
```

## 🚀 Services

### research-orchestrator
- **Type**: unknown
- **Language**: unknown
- **Path**: `services/research-orchestrator`
- **Dockerized**: ❌
- **Tests**: ❌

### vision-ai
- **Type**: Python Service
- **Language**: Python
- **Path**: `services/vision-ai`
- **Dockerized**: ✅
- **Tests**: ❌
- **Description**: This service provides image analysis, description, and processing capabilities for the Unhinged proj

### go-services
- **Type**: unknown
- **Language**: unknown
- **Path**: `services/go-services`
- **Dockerized**: ❌
- **Tests**: ❌

### whisper-tts
- **Type**: Python Service
- **Language**: Python
- **Path**: `services/whisper-tts`
- **Dockerized**: ✅
- **Tests**: ❌
- **Description**: This service provides both Speech-to-Text (STT) and Text-to-Speech (TTS) capabilities for the Unhing

### backend
- **Type**: Kotlin Service
- **Language**: Kotlin
- **Path**: `backend`
- **Dockerized**: ✅
- **Tests**: ❌
- **Description**: This project was created using the [Ktor Project Generator](https://start.ktor.io).

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
- **Files**: 1412
- **Subdirectories**: 5

### frontend
- **Description**: Frontend user interface
- **Files**: 8001
- **Subdirectories**: 9

### services
- **Description**: Microservices and external integrations
- **Files**: 14
- **Subdirectories**: 4

### proto
- **Description**: Protocol buffer definitions
- **Files**: 23
- **Subdirectories**: 1

### docs
- **Description**: Project documentation
- **Files**: 44
- **Subdirectories**: 15

### scripts
- **Description**: Build and automation scripts
- **Files**: 20
- **Subdirectories**: 2

### infrastructure
- **Description**: Infrastructure as code
- **Files**: 1
- **Subdirectories**: 1

### monitoring
- **Description**: Monitoring and observability
- **Files**: 0
- **Subdirectories**: 2

## 📋 Key Files

- **Makefile** (`Makefile`) - Build automation and development commands
- **package.json** (`package.json`) - Node.js dependencies and scripts
- **docker-compose.yml** (`docker-compose.yml`) - Service orchestration configuration
- **README.md** (`README.md`) - Project overview and setup instructions
- **Dockerfile** (`services/vision-ai/Dockerfile`) - Container build instructions
- **requirements.txt** (`services/vision-ai/requirements.txt`) - Python dependencies
- **README.md** (`services/vision-ai/README.md`) - Project overview and setup instructions
- **Dockerfile** (`services/whisper-tts/Dockerfile`) - Container build instructions
- **requirements.txt** (`services/whisper-tts/requirements.txt`) - Python dependencies
- **README.md** (`services/whisper-tts/README.md`) - Project overview and setup instructions
- **package.json** (`shared/events/package.json`) - Node.js dependencies and scripts
- **README.md** (`shared/events/README.md`) - Project overview and setup instructions
- **README.md** (`proto/README.md`) - Project overview and setup instructions
- **README.md** (`.augment/README.md`) - Project overview and setup instructions
- **README.md** (`docs/README.md`) - Project overview and setup instructions
- **README.md** (`docs/roadmap/README.md`) - Project overview and setup instructions
- **README.md** (`tools/README.md`) - Project overview and setup instructions
- **package.json** (`frontend/package.json`) - Node.js dependencies and scripts
- **Dockerfile** (`frontend/Dockerfile`) - Container build instructions
- **README.md** (`scripts/docs/README.md`) - Project overview and setup instructions
- **README.md** (`scripts/python/README.md`) - Project overview and setup instructions
- **Dockerfile** (`llm/Dockerfile`) - Container build instructions
- **build.gradle.kts** (`backend/build.gradle.kts`) - Kotlin/Java build configuration
- **Dockerfile** (`backend/Dockerfile`) - Container build instructions
- **README.md** (`backend/README.md`) - Project overview and setup instructions
- **package.json** (`cdc-service/package.json`) - Node.js dependencies and scripts
- **Dockerfile** (`cdc-service/Dockerfile`) - Container build instructions
- **requirements.txt** (`cdc-service/requirements.txt`) - Python dependencies
- **Dockerfile** (`database/Dockerfile`) - Container build instructions

---

**Note**: This documentation is automatically generated from project analysis.
Run `make docs-update` to refresh after structural changes.