# 🔗 Unhinged Service Dependencies Map

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    UNHINGED CONSCIOUSNESS ECOSYSTEM             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │   Frontend  │    │   Backend   │    │ Observability│         │
│  │ (React/TS)  │◄──►│(Kotlin/Ktor)│◄──►│   Stack     │         │
│  │ Port: 3000  │    │ Port: 8080  │    │             │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│                             │                   │               │
│                             ▼                   ▼               │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                 AI SERVICES LAYER                           │ │
│  │                                                             │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │ │
│  │  │ Vision AI   │  │Whisper TTS  │  │Context LLM  │        │ │
│  │  │(Python/API) │  │(Python/API) │  │(Python/API) │        │ │
│  │  │ Port: 8001  │  │ Port: 8000  │  │ Port: 8002  │        │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘        │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                             │                                   │
│                             ▼                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                 DATA & INFRASTRUCTURE                       │ │
│  │                                                             │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │ │
│  │  │ PostgreSQL  │  │   Kafka     │  │   Ollama    │        │ │
│  │  │ Port: 5433  │  │ Port: 9092  │  │Port: 11434  │        │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘        │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 🎯 Critical Dependencies

### **1. Backend Service (Core)**
**Dependencies:**
- ✅ **PostgreSQL** (Required) - Data persistence
- ⚠️ **Observability Stack** (Monitoring) - Metrics/logs
- 🔧 **Context LLM** (Optional) - AI processing
- 🔧 **Vision AI** (Optional) - Image processing
- 🔧 **Whisper TTS** (Optional) - Audio processing

**Health Impact:**
- **PostgreSQL Down**: Backend degraded, data operations fail
- **Observability Down**: Monitoring blind, service continues
- **AI Services Down**: Reduced functionality, core API works

### **2. AI Services Layer**
**Vision AI Dependencies:**
- 🔧 **GPU/CUDA** (Optional) - Accelerated processing
- 🔧 **Model Files** (Required) - AI capabilities

**Whisper TTS Dependencies:**
- 🔧 **Audio Models** (Required) - Speech processing
- 🔧 **GPU/CUDA** (Optional) - Faster inference

**Context LLM Dependencies:**
- 🔧 **Ollama** (Optional) - Local LLM backend
- 🔧 **External LLM APIs** (Optional) - Cloud processing

### **3. Observability Stack**
**Grafana Dependencies:**
- ✅ **Prometheus** (Required) - Metrics data source
- ✅ **Loki** (Required) - Log data source
- ⚠️ **Tempo** (Optional) - Trace data source

**Prometheus Dependencies:**
- ✅ **Backend /metrics** (Required) - Application metrics
- 🔧 **AI Service metrics** (Optional) - Service metrics

## 🚨 Failure Cascade Analysis

### **Scenario 1: Database Failure**
```
PostgreSQL Down
    ↓
Backend Health: DEGRADED
    ↓
Data operations fail
    ↓
Frontend shows errors
    ↓
User experience impacted
```

### **Scenario 2: Observability Failure**
```
Prometheus/Grafana Down
    ↓
Monitoring blind
    ↓
Services continue normally
    ↓
No impact on user experience
    ↓
Reduced operational visibility
```

### **Scenario 3: AI Services Failure**
```
Vision AI / Whisper TTS Down
    ↓
Backend continues serving
    ↓
AI endpoints return errors
    ↓
Reduced functionality
    ↓
Core API remains available
```

## 🔍 Dependency Health Checks

### **Critical Path Monitoring**
```bash
# Check critical dependencies in order
./scripts/health-check.sh --service database
./scripts/health-check.sh --service backend
./scripts/health-check.sh --service observability

# Quick dependency chain check
curl -s http://localhost:8080/health | jq '.services'
```

### **Service Startup Order**
```bash
# 1. Infrastructure first
docker-compose up -d postgres
docker-compose -f docker-compose.observability.yml up -d

# 2. Core backend
cd backend && ./gradlew run &

# 3. AI services (parallel)
docker-compose up -d vision-ai whisper-tts

# 4. Optional services
docker-compose up -d frontend kafka ollama
```

## 📊 Dependency Metrics

### **Service Relationship Queries**
```promql
# Backend dependency health
up{job="unhinged-backend"} * on() group_left() up{job="postgres"}

# AI services availability
sum(up{job=~"unhinged-(vision|whisper|context).*"}) / 3

# Observability stack health
min(up{job=~"(grafana|prometheus|loki)"})
```

### **Cascade Failure Detection**
```promql
# Detect when backend is up but dependencies are down
up{job="unhinged-backend"} == 1 and up{job="postgres"} == 0

# AI services partial failure
count(up{job=~"unhinged-(vision|whisper|context).*"} == 0) > 0
```
