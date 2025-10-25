# 🏗️ Project Structure - Unhinged Platform

> **Purpose**: Comprehensive overview of project organization and components
> **Audience**: Developers and AI assistants working on the platform
> **Last Updated**: Auto-generated on 2025-10-24 22:33:42

## 📊 Project Overview

- **Total Files**: 1328
- **Services**: 4
- **Key Files**: 24

### File Type Distribution
```
.kt               488 files
.java             470 files
.py               125 files
.cc                50 files
.h                 50 files
.ts                30 files
.proto             28 files
.md                27 files
no_extension       14 files
.json              14 files
```

## 🚀 Services

### shared
- **Type**: unknown
- **Language**: unknown
- **Path**: `services/shared`
- **Dockerized**: ❌
- **Tests**: ❌

### speech-to-text
- **Type**: unknown
- **Language**: unknown
- **Path**: `services/speech-to-text`
- **Dockerized**: ✅
- **Tests**: ❌

### text-to-speech
- **Type**: Python Service
- **Language**: Python
- **Path**: `services/text-to-speech`
- **Dockerized**: ✅
- **Tests**: ❌

### vision-ai
- **Type**: Python Service
- **Language**: Python
- **Path**: `services/vision-ai`
- **Dockerized**: ✅
- **Tests**: ❌

## 🧩 Components

### services
- **Description**: Microservices and external integrations
- **Files**: 25
- **Subdirectories**: 4

### proto
- **Description**: Protocol buffer definitions
- **Files**: 29
- **Subdirectories**: 2

### docs
- **Description**: Project documentation
- **Files**: 10
- **Subdirectories**: 5

## 📋 Key Files

- **Makefile** (`Makefile`) - Build automation and development commands
- **README.md** (`README.md`) - Project overview and setup instructions
- **README.md** (`.augment/README.md`) - Project overview and setup instructions
- **README.md** (`services/README.md`) - Project overview and setup instructions
- **Dockerfile** (`services/speech-to-text/Dockerfile`) - Container build instructions
- **requirements.txt** (`services/text-to-speech/requirements.txt`) - Python dependencies
- **Dockerfile** (`services/text-to-speech/Dockerfile`) - Container build instructions
- **requirements.txt** (`services/vision-ai/requirements.txt`) - Python dependencies
- **Dockerfile** (`services/vision-ai/Dockerfile`) - Container build instructions
- **README.md** (`control/sdk/javascript/README.md`) - Project overview and setup instructions
- **requirements.txt** (`control/native_gui/requirements.txt`) - Python dependencies
- **build.gradle.kts** (`platforms/persistence/build.gradle.kts`) - Kotlin/Java build configuration
- **docker-compose.yml** (`platforms/persistence/docker-compose.yml`) - Service orchestration configuration
- **README.md** (`platforms/persistence/README.md`) - Project overview and setup instructions
- **Dockerfile** (`platforms/persistence/Dockerfile`) - Container build instructions
- **README.md** (`platforms/persistence/config/README.md`) - Project overview and setup instructions
- **README.md** (`proto/README.md`) - Project overview and setup instructions
- **README.md** (`libs/event-framework/README.md`) - Project overview and setup instructions
- **README.md** (`libs/event-framework/python/README.md`) - Project overview and setup instructions
- **build.gradle.kts** (`libs/event-framework/kotlin/build.gradle.kts`) - Kotlin/Java build configuration
- **package.json** (`libs/event-framework/typescript/package.json`) - Node.js dependencies and scripts
- **README.md** (`libs/event-framework/typescript/README.md`) - Project overview and setup instructions
- **build.gradle.kts** (`libs/service-framework/kotlin/build.gradle.kts`) - Kotlin/Java build configuration
- **build.gradle.kts** (`generated/kotlin/clients/build.gradle.kts`) - Kotlin/Java build configuration

---

**Note**: This documentation is automatically generated from project analysis.
Run `make docs-update` to refresh after structural changes.