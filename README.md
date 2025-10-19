# 🎛️ Unhinged AI Platform

> **Unified Control Plane**: Voice-driven UI generation with LLM intelligence and human oversight

## 🚀 **Quick Start**

**Run `make start` from monorepo root.**

```bash
# From the root of this monorepo
make start
```

This will:
1. 🔍 Scan and generate file registry
2. 🎛️ Start the DAG Control Plane
3. 🌐 Open browser interface automatically

## 📁 **What You Get**

- **DAG Control Plane**: Build orchestration with human oversight
- **AI Services**: Text generation, vision AI, voice processing
- **Self-Organizing Interface**: Auto-discovers all capabilities
- **Plug-and-Play**: Works immediately with zero setup

---

**Everything else is discoverable through the browser interface.**

## 🏗️ **Architecture Overview**

### **Domain-Driven Design with Clean Architecture**

```
📦 Unhinged/
├── 🎯 backend/          # Clean Architecture (Kotlin/Ktor)
│   ├── domain/          # Pure business logic
│   ├── application/     # Use cases
│   ├── infrastructure/  # Repository implementations
│   └── presentation/    # HTTP controllers
├── 🎨 frontend/         # React/TypeScript SPA
│   ├── src/services/    # API clients
│   ├── src/components/  # UI components
│   └── src/pages/       # Route components
├── 🏗️ platforms/        # Complex multi-technology platforms
│   ├── persistence/     # Multi-database abstraction platform
│   ├── agent/          # AI agent orchestration (future)
│   └── workflow/       # Business process automation (future)
├── 🔧 services/         # Simple, single-purpose services
│   ├── speech-to-text/ # Voice transcription
│   ├── text-to-speech/ # Voice synthesis
│   └── vision-ai/      # Image processing
├── 📚 docs/             # Technical documentation
└── 🔧 tools/            # Development utilities
```

### **Platforms vs Services Architecture**

**🏗️ Platforms** (Complex Multi-Technology Offerings):
- **Persistence Platform**: Abstracts 8 database technologies behind unified APIs
- **Agent Platform** (Future): AI agent orchestration and lifecycle management
- **Workflow Platform** (Future): Business process automation and orchestration

**🔧 Services** (Simple Single-Purpose Offerings):
- **Speech-to-Text**: Voice transcription service
- **Text-to-Speech**: Voice synthesis service
- **Vision-AI**: Image processing and analysis

## 📋 **LLM Navigation Guide**

| Task | Documentation |
|------|---------------|
| **Backend Development** | [`/docs/backend/`](./docs/backend/) |
| **Frontend Development** | [`/docs/frontend/`](./docs/frontend/) |
| **API Reference** | [`/docs/api/`](./docs/api/) |
| **Architecture Decisions** | [`/docs/architecture/`](./docs/architecture/) |
| **Testing Strategy** | [`/docs/testing/`](./docs/testing/) |
| **Deployment** | [`/docs/deployment/`](./docs/deployment/) |

## 🚀 **Current Status**

### ✅ **Working Components**
- **Clean Architecture Backend** (Domain → Application → Infrastructure → Presentation)
- **React Frontend** with TypeScript and styled-components
- **REST API** with full CRUD operations
- **In-Memory Storage** (ready for database integration)
- **CORS-enabled** for local development

### 🔄 **Active Development**
- Chat functionality with contextual responses
- Session management
- Health monitoring
- Error handling and logging

## 🎯 **For LLM Assistants**

### **Common Tasks**
1. **Adding new features**: Start with `/docs/architecture/domain-driven-design.md`
2. **API changes**: Reference `/docs/api/endpoints.md`
3. **Frontend updates**: Check `/docs/frontend/component-architecture.md`
4. **Testing**: Follow `/docs/testing/strategy.md`
5. **Debugging**: Use `/docs/troubleshooting/common-issues.md`

### **Key Files to Understand**
- `backend/src/main/kotlin/com/unhinged/domain/chat/ChatDomain.kt` - Core business logic
- `frontend/src/services/ChatService.ts` - API client
- `frontend/src/pages/Chatroom/Chatroom.tsx` - Main UI component

## 🔧 **Development Commands**

```bash
# Backend
cd backend
./gradlew build          # Build
./gradlew test           # Test
./gradlew run            # Run (port 8080)

# Frontend  
cd frontend
npm install              # Install dependencies
npm start                # Dev server (port 8081)
npm run build            # Production build

# Full System
make dev                 # Start both services
make test                # Run all tests
make clean               # Clean build artifacts
```

## 📊 **Service Endpoints**

### **Backend API (localhost:8080)**
- `GET /` - Service information
- `POST /chat` - Legacy chat endpoint
- `POST /api/v1/chat` - Modern chat API
- `GET /api/v1/health` - Health check
- `POST /api/v1/sessions` - Create session
- `GET /api/v1/sessions/{id}/messages` - Get conversation

### **Persistence Platform (localhost:8090)**
- `GET /api/v1/health` - Platform health check
- `GET /api/v1/metrics` - Platform metrics
- `POST /api/v1/query/{queryName}` - Execute named queries
- `POST /api/v1/tables/{tableName}` - CRUD operations
- `POST /api/v1/vector/search/{tableName}` - Vector search
- `POST /api/v1/graph/traverse/{tableName}` - Graph traversal
- `POST /api/v1/operations/{operationName}` - Complex operations

### **Frontend (localhost:8081)**
- `/` - Chat interface
- React Router handles SPA navigation

## 🎨 **Tech Stack**

### **Backend**
- **Language**: Kotlin
- **Framework**: Ktor
- **Architecture**: Clean Architecture + DDD
- **Storage**: In-memory (PostgreSQL ready)
- **API**: REST with JSON

### **Frontend**
- **Language**: TypeScript
- **Framework**: React 19
- **Styling**: styled-components
- **State**: React Query
- **Routing**: React Router v7
- **Build**: Webpack

## 📚 **Documentation Structure**

```
docs/
├── architecture/        # System design & patterns
├── api/                # API documentation
├── backend/            # Backend-specific docs
├── frontend/           # Frontend-specific docs
├── testing/            # Testing strategies
├── deployment/         # Deployment guides
└── troubleshooting/    # Common issues & solutions
```

## 🤝 **Contributing**

1. Read `/docs/architecture/` for system understanding
2. Check `/docs/testing/` for testing requirements
3. Follow clean architecture principles
4. Update documentation for any changes

---

**🎯 LLM Tip**: Always check `/docs/` for detailed context before making changes. This README provides quick navigation - the real documentation is in the docs folder.
