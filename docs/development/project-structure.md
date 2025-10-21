# 🏗️ Project Structure - Unhinged Platform

> **Purpose**: Comprehensive overview of project organization and components
> **Audience**: Developers and AI assistants working on the platform
> **Last Updated**: Auto-generated on 2025-10-20 19:14:38

## 📊 Project Overview

- **Total Files**: 2968
- **Services**: 4
- **Key Files**: 36

### File Type Distribution
```
.py              1306 files
.kt               483 files
.java             470 files
no_extension      230 files
.md                71 files
.txt               50 files
.cc                50 files
.h                 50 files
.proto             40 files
.typed             37 files
```

## 🚀 Services

### speech-to-text
- **Type**: Python Service
- **Language**: Python
- **Path**: `services/speech-to-text`
- **Dockerized**: ✅
- **Tests**: ❌
- **Description**: This service provides Speech-to-Text (STT) capabilities for the Unhinged project using OpenAI's Whis

### text-to-speech
- **Type**: Python Service
- **Language**: Python
- **Path**: `services/text-to-speech`
- **Dockerized**: ✅
- **Tests**: ❌
- **Description**: This service provides local Text-to-Speech (TTS) capabilities for the Unhinged project using Coqui T

### vision-ai
- **Type**: Python Service
- **Language**: Python
- **Path**: `services/vision-ai`
- **Dockerized**: ✅
- **Tests**: ❌
- **Description**: This service provides image analysis, description, and processing capabilities for the Unhinged proj

### llm
- **Type**: unknown
- **Language**: unknown
- **Path**: `llm`
- **Dockerized**: ✅
- **Tests**: ❌

## 🧩 Components

### services
- **Description**: Microservices and external integrations
- **Files**: 16
- **Subdirectories**: 3

### proto
- **Description**: Protocol buffer definitions
- **Files**: 30
- **Subdirectories**: 2

### docs
- **Description**: Project documentation
- **Files**: 46
- **Subdirectories**: 15

### scripts
- **Description**: Build and automation scripts
- **Files**: 23
- **Subdirectories**: 1

## 📋 Key Files

- **Makefile** (`Makefile`) - Build automation and development commands
- **docker-compose.yml** (`docker-compose.yml`) - Service orchestration configuration
- **package.json** (`package.json`) - Node.js dependencies and scripts
- **requirements.txt** (`requirements.txt`) - Python dependencies
- **README.md** (`README.md`) - Project overview and setup instructions
- **README.md** (`docs/roadmap/README.md`) - Project overview and setup instructions
- **package.json** (`shared/events/package.json`) - Node.js dependencies and scripts
- **README.md** (`shared/events/README.md`) - Project overview and setup instructions
- **build.gradle.kts** (`platform/example-service/build.gradle.kts`) - Kotlin/Java build configuration
- **README.md** (`data-lake/README.md`) - Project overview and setup instructions
- **README.md** (`.augment/README.md`) - Project overview and setup instructions
- **requirements.txt** (`services/speech-to-text/requirements.txt`) - Python dependencies
- **README.md** (`services/speech-to-text/README.md`) - Project overview and setup instructions
- **Dockerfile** (`services/speech-to-text/Dockerfile`) - Container build instructions
- **requirements.txt** (`services/text-to-speech/requirements.txt`) - Python dependencies
- **README.md** (`services/text-to-speech/README.md`) - Project overview and setup instructions
- **Dockerfile** (`services/text-to-speech/Dockerfile`) - Container build instructions
- **requirements.txt** (`services/vision-ai/requirements.txt`) - Python dependencies
- **README.md** (`services/vision-ai/README.md`) - Project overview and setup instructions
- **Dockerfile** (`services/vision-ai/Dockerfile`) - Container build instructions
- **README.md** (`scripts/python/README.md`) - Project overview and setup instructions
- **README.md** (`control/static_html/shared/README.md`) - Project overview and setup instructions
- **README.md** (`control/sdk/javascript/README.md`) - Project overview and setup instructions
- **Makefile** (`platforms/Makefile`) - Build automation and development commands
- **README.md** (`platforms/README.md`) - Project overview and setup instructions
- **build.gradle.kts** (`platforms/persistence/build.gradle.kts`) - Kotlin/Java build configuration
- **docker-compose.yml** (`platforms/persistence/docker-compose.yml`) - Service orchestration configuration
- **README.md** (`platforms/persistence/README.md`) - Project overview and setup instructions
- **Dockerfile** (`platforms/persistence/Dockerfile`) - Container build instructions
- **README.md** (`platforms/persistence/config/README.md`) - Project overview and setup instructions
- **README.md** (`proto/README.md`) - Project overview and setup instructions
- **build.gradle.kts** (`libs/service-framework/kotlin/build.gradle.kts`) - Kotlin/Java build configuration
- **requirements.txt** (`generated/python/clients/requirements.txt`) - Python dependencies
- **build.gradle.kts** (`generated/kotlin/clients/build.gradle.kts`) - Kotlin/Java build configuration
- **package.json** (`generated/typescript/clients/package.json`) - Node.js dependencies and scripts
- **Dockerfile** (`llm/Dockerfile`) - Container build instructions

---

**Note**: This documentation is automatically generated from project analysis.
Run `make docs-update` to refresh after structural changes.