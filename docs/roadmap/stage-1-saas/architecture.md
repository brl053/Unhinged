# Stage 1: SaaS Architecture

## System Overview

Unhinged Stage 1 is a locally-hosted SaaS product with agent orchestration capabilities, built on event-driven architecture with PostgreSQL persistence.

## Core Components

### Frontend
- **Technology**: React + TypeScript
- **Purpose**: User interface for agent interactions
- **Key Features**:
  - Real-time chat interface
  - Agent orchestration dashboard
  - Event log visualization
  - Session management

### Backend
- **Technology**: Node.js + TypeScript (migrated from Kotlin)
- **Purpose**: API server and business logic
- **Key Features**:
  - RESTful API with protobuf serialization
  - Event emission system
  - Agent orchestration engine
  - Session context management

### Database Layer
- **Primary**: PostgreSQL with document store abstraction
- **Caching**: Redis for session and frequently accessed data
- **Purpose**: Persistent storage with flexible schema support

### Event System
- **Technology**: Custom event emitter with PostgreSQL persistence
- **Purpose**: Capture all system interactions for context and analytics
- **Features**:
  - Type-based event registration
  - Session-based event querying
  - OpenTelemetry compliance with trace IDs

### Agent Framework
- **Purpose**: Orchestrate multi-step LLM workflows
- **Components**:
  - Research Manager Agent
  - Resource Locator Agent
  - Web Scraper Agent
  - Presentation Agent
  - DSL Agent
  - LLM_SDUI Agent

## Data Flow

```
User Request → Frontend → Backend API → Agent Orchestration
                                    ↓
Event Emission → PostgreSQL → Context Retrieval → LLM Processing
                                    ↓
Response Generation → Frontend Update → Real-time WebSocket
```

## Development Patterns

### Entity Creation
All entities follow the standardized CRUD pattern:
1. Database schema with standard fields
2. Protobuf definition
3. Service layer implementation
4. API routes with event emission
5. Frontend components and services

### Event Emission
Every significant operation emits structured events:
- Operation start/completion
- Error conditions
- Performance metrics
- User interactions

### Session Management
Sessions provide context boundaries:
- All events tagged with session_id
- Session-based data retrieval
- Context accumulation for LLM interactions

## Technology Stack

### Core Technologies
- **Frontend**: React, TypeScript, WebSockets
- **Backend**: Node.js, TypeScript, Express
- **Database**: PostgreSQL, Redis
- **Serialization**: Protocol Buffers
- **Build System**: Custom Rush-equivalent

### External Integrations
- **LLM**: Ollama (local), OpenAI (fallback)
- **Monitoring**: Custom event system
- **Development**: Docker Compose for local development

## Deployment Architecture

### Local Development
- Docker Compose orchestration
- Hot reloading for development
- Integrated database and caching
- Custom terminal integration

### Production (Future)
- Kubernetes deployment
- Horizontal scaling
- Load balancing
- Monitoring and alerting

## Security Considerations

### Authentication
- Session-based authentication
- API key management for external services
- User context isolation

### Data Protection
- Event data encryption
- Session data isolation
- Audit trail maintenance

## Performance Requirements

### Response Times
- API responses: < 200ms
- LLM interactions: < 5s
- Real-time updates: < 100ms

### Scalability
- Support for concurrent sessions
- Horizontal scaling capability
- Database query optimization

## Migration Path to Stage 2

The SaaS architecture is designed to facilitate migration to the ring-zero OS:
- Event-driven foundation supports OS-level integration
- Agent framework becomes OS service layer
- UI components become dynamic OS rendering
- Database layer becomes system persistence
