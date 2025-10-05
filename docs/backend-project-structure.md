# Backend Kotlin Microservices - Project Structure

## 🏗️ **Architecture Overview**

The Unhinged backend is a **LLM-native microservices platform** built with Kotlin, featuring:
- **Dual Protocol Support**: HTTP/REST (Ktor) + gRPC for high-performance inter-service communication
- **Event-Driven Architecture**: CDC (Change Data Capture) with Kafka for real-time workflow orchestration
- **LLM-Optimized Components**: Session context management, semantic analysis, and intelligent document ranking
- **Production-Ready Infrastructure**: Dependency injection, health monitoring, and comprehensive observability

## 📁 **Project Structure**

```
backend/
├── 📋 Build & Configuration
│   ├── build.gradle.kts              # Gradle build with gRPC, Koin DI, and LLM dependencies
│   ├── settings.gradle.kts           # Multi-module project configuration
│   ├── gradle.properties             # Gradle build properties
│   ├── gradle/libs.versions.toml     # Centralized dependency version management
│   └── Dockerfile                    # Production container image
│
├── 🧠 Source Code (src/)
│   ├── main/kotlin/com/unhinged/     # Core application code
│   ├── main/resources/               # Configuration and database migrations
│   ├── test/kotlin/                  # Unit and integration tests
│   ├── services/                     # Event streaming services (TypeScript)
│   └── types/generated/              # Generated protobuf types
│
└── 📚 Documentation
    └── README.md                     # Service documentation
```

## 🔧 **Core Application Structure**

### **`src/main/kotlin/com/unhinged/`** - Application Core

```
com/unhinged/
├── 🚀 Application.kt                 # Main entry point with dual protocol servers
├── 🔌 Dependency Injection (di/)
│   ├── DatabaseModule.kt             # HikariCP connection pools with read/write splitting
│   ├── DocumentStoreModule.kt        # DocumentStore service components with LLM features
│   ├── CDCModule.kt                  # Event streaming and CDC integration
│   └── SimpleImplementations.kt     # Basic implementations for rapid development
│
├── 📄 DocumentStore Service (documentstore/)
│   ├── DocumentStoreService.kt       # gRPC service with 11 endpoints + LLM optimization
│   ├── DocumentRepository.kt         # Interface for document persistence
│   ├── DocumentRepositoryImpl.kt     # PostgreSQL implementation with JSONB optimization
│   ├── DocumentEventEmitter.kt       # Interface for CDC event emission
│   └── DocumentEventEmitterImpl.kt   # CDC integration with semantic analysis
│
├── 📡 CDC & Events (cdc/)
│   ├── CDCService.kt                 # Change Data Capture service implementation
│   └── MinimalCDCService.kt          # Lightweight CDC service for development
│
├── 🔧 Legacy Ktor Components (to be refactored)
│   ├── Main.kt                       # Legacy main entry point
│   ├── Routing.kt                    # HTTP API routes
│   ├── Security.kt                   # Authentication and authorization
│   ├── Serialization.kt              # JSON serialization configuration
│   ├── Sockets.kt                    # WebSocket configuration
│   ├── Databases.kt                  # Legacy database configuration
│   ├── CitySchema.kt                 # Example schema (to be removed)
│   ├── UsersSchema.kt                # User management schema
│   └── service/LlmService.kt         # LLM integration service
│
└── 📤 Events (events/)
    └── EventEmitter.kt               # Generic event emission utilities
```

## 🤖 **Generated Protobuf Code**

### **`src/main/kotlin/unhinged/`** - Generated gRPC Services

```
unhinged/
├── 📄 document_store/                # DocumentStore gRPC generated code (30+ files)
│   ├── DocumentKt.kt                 # Document message types
│   ├── DocumentStoreKt.kt            # Service interfaces
│   ├── PutDocumentRequestKt.kt       # Request/response types
│   ├── GetSessionContextRequestKt.kt # LLM-specific context queries
│   └── [28+ more generated files]    # Complete gRPC API surface
│
├── 📡 cdc/                           # CDC Event System (70+ files)
│   ├── UniversalEventKt.kt           # Universal event envelope
│   ├── DocumentEventKt.kt            # Document lifecycle events
│   ├── LLMEventKt.kt                 # LLM interaction events
│   ├── AgentEventKt.kt               # Agent workflow events
│   ├── SessionEventKt.kt             # Session management events
│   ├── SystemEventKt.kt              # System monitoring events
│   ├── PublishEventRequestKt.kt      # Event publishing API
│   └── [65+ more generated files]    # Complete CDC event system
│
└── 💬 messaging/                     # Inter-Service Messaging (50+ files)
    ├── MessageKt.kt                  # Core message types
    ├── LLMMessageKt.kt               # LLM service communication
    ├── AgentMessageKt.kt             # Agent coordination messages
    ├── ToolMessageKt.kt              # Tool invocation and results
    ├── WorkflowMessageKt.kt          # Workflow orchestration
    ├── UIMessageKt.kt                # Real-time UI updates
    └── [45+ more generated files]    # Complete messaging system
```

## 🗄️ **Resources & Configuration**

### **`src/main/resources/`** - Configuration & Migrations

```
resources/
├── ⚙️ application.conf               # HOCON configuration with LLM-specific settings
│   ├── Database: Connection pools, read/write splitting
│   ├── LLM: Context limits, token estimation, semantic analysis
│   ├── Events: Kafka configuration, CDC settings
│   ├── Cache: Document caching, session context optimization
│   └── Monitoring: Health checks, metrics, logging
│
└── 🗄️ db/migration/                  # Flyway database migrations
    └── V001__create_document_store_schema.sql
        ├── document_header: Metadata with LLM-optimized indexes
        ├── document_body: JSONB content storage
        ├── active_tag: Version management for A/B testing
        ├── tag_event: Audit trail for version promotions
        └── Performance views and indexes for LLM workloads
```

## 🧪 **Testing Structure**

### **`src/test/kotlin/`** - Test Suite

```
test/kotlin/
├── ApplicationTest.kt                # Integration tests for main application
├── documentstore/                    # DocumentStore service tests
│   ├── DocumentStoreServiceTest.kt   # gRPC service testing
│   ├── DocumentRepositoryTest.kt     # Database layer testing with Testcontainers
│   └── DocumentEventEmitterTest.kt   # CDC integration testing
├── di/                              # Dependency injection tests
│   └── ModuleTest.kt                # DI module validation
└── integration/                     # End-to-end integration tests
    ├── DatabaseIntegrationTest.kt    # Database connectivity and performance
    ├── EventStreamingTest.kt         # CDC event flow testing
    └── LLMWorkflowTest.kt            # LLM-native feature testing
```

## 🔧 **Build & Deployment**

### **Build Configuration**

```kotlin
// build.gradle.kts - Key dependencies and configurations
dependencies {
    // Kotlin & Coroutines
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.3")
    
    // gRPC & Protobuf
    implementation("io.grpc:grpc-kotlin-stub:1.4.0")
    implementation("com.google.protobuf:protobuf-kotlin:3.25.1")
    
    // Dependency Injection
    implementation("io.insert-koin:koin-core:3.5.3")
    implementation("io.insert-koin:koin-ktor:3.5.3")
    
    // Database
    implementation("org.postgresql:postgresql:42.7.1")
    implementation("com.zaxxer:HikariCP:5.1.0")
    
    // Event Streaming
    implementation("org.apache.kafka:kafka-clients:3.5.1")
    
    // Ktor (HTTP/WebSocket)
    implementation("io.ktor:ktor-server-core:2.3.4")
    implementation("io.ktor:ktor-server-netty:2.3.4")
}
```

### **Container Deployment**

```dockerfile
# Dockerfile - Multi-stage production build
FROM gradle:8.5-jdk17 AS build
COPY . /app
WORKDIR /app
RUN gradle fatJar

FROM openjdk:17-jre-slim
COPY --from=build /app/build/libs/*-fat.jar app.jar
EXPOSE 8080 9090
CMD ["java", "-jar", "app.jar"]
```

## 🎯 **Key Features by Component**

### **DocumentStore Service**
- **11 gRPC endpoints** for complete document lifecycle
- **LLM-native session context** aggregation for prompt construction
- **Automatic versioning** with tag-based A/B testing
- **Real-time event emission** for workflow orchestration
- **PostgreSQL JSONB** optimization for flexible document storage

### **CDC Event System**
- **Universal event envelope** for all system events
- **5 event categories**: Document, LLM, Agent, Session, System
- **Event streaming** with Kafka integration
- **Dead letter queue** management for failed events
- **Event replay** capabilities for system recovery

### **Dependency Injection**
- **Koin framework** for lightweight, Kotlin-native DI
- **Environment-specific** configuration with HOCON
- **Connection pool management** with read/write splitting
- **Health monitoring** for all components
- **LLM-optimized** service configurations

### **Database Layer**
- **HikariCP connection pools** optimized for LLM workloads
- **Read/write splitting** for performance optimization
- **JSONB document storage** with semantic search indexes
- **Flyway migrations** for schema evolution
- **Performance monitoring** and health checks

## 🚀 **Production Readiness**

- ✅ **Dual Protocol Support**: HTTP + gRPC for different use cases
- ✅ **Event-Driven Architecture**: Real-time workflow orchestration
- ✅ **LLM-Native Optimizations**: Context management, token estimation
- ✅ **Comprehensive DI**: Koin-based dependency injection
- ✅ **Database Optimization**: Connection pooling, JSONB indexes
- ✅ **Health Monitoring**: Component health checks and metrics
- ✅ **Container Ready**: Docker multi-stage builds
- ✅ **Testing Suite**: Unit, integration, and end-to-end tests

## 📊 **Component Statistics**

### **Generated Code (Auto-generated from Protobuf)**
- **DocumentStore**: 30 Kotlin files (11 gRPC endpoints)
- **CDC Events**: 70 Kotlin files (5 event categories, universal envelope)
- **Messaging**: 50 Kotlin files (inter-service communication)
- **Total Generated**: **150+ files** from 4 protobuf schemas

### **Hand-Written Code (Core Business Logic)**
- **Application Core**: 15 Kotlin files (DI, services, repositories)
- **Database Layer**: 2 SQL migration files with LLM-optimized schemas
- **Configuration**: 1 HOCON file with 200+ settings
- **Legacy Components**: 10 Kotlin files (to be refactored)
- **Total Hand-Written**: **28 files** with comprehensive documentation

### **File Organization**
```
📁 Total Files: 180+
├── 🤖 Generated (150+): Type-safe gRPC services and message types
├── 🧠 Core Logic (15): LLM-native business logic and DI
├── 🗄️ Database (2): PostgreSQL schemas with performance optimization
├── ⚙️ Config (1): Comprehensive HOCON configuration
└── 🔧 Legacy (10): Ktor components for HTTP/WebSocket support
```

## 🔄 **Service Communication Flow**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (TypeScript)  │    │   (Kotlin)      │    │   (PostgreSQL)  │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ DocumentStore   │◄──►│ gRPC Service    │◄──►│ JSONB Storage   │
│ Client          │    │ (Port 9090)     │    │ + Indexes       │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ HTTP/WebSocket  │◄──►│ Ktor Server     │    │ Connection      │
│ API Client      │    │ (Port 8080)     │    │ Pools           │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Event Stream   │
                    │  (Kafka CDC)    │
                    │                 │
                    │ • Document      │
                    │ • LLM Events    │
                    │ • Agent Tasks   │
                    │ • Workflows     │
                    └─────────────────┘
```

## 🎯 **Development Workflow**

### **1. Adding New Features**
```bash
# 1. Update protobuf schemas
vim proto/document_store.proto

# 2. Regenerate code
npm run proto:generate

# 3. Implement service logic
vim src/main/kotlin/com/unhinged/documentstore/DocumentStoreService.kt

# 4. Update DI configuration
vim src/main/kotlin/com/unhinged/di/DocumentStoreModule.kt

# 5. Add database migrations
vim src/main/resources/db/migration/V002__add_new_feature.sql

# 6. Write tests
vim src/test/kotlin/documentstore/NewFeatureTest.kt
```

### **2. Running the Application**
```bash
# Development mode (with hot reload)
./gradlew runDev

# Production build
./gradlew fatJar
java -jar build/libs/backend-1.0.0-fat.jar

# Docker deployment
docker build -t unhinged/backend:1.0.0 .
docker run -p 8080:8080 -p 9090:9090 unhinged/backend:1.0.0
```

### **3. Testing Strategy**
```bash
# Unit tests
./gradlew test

# Integration tests with Testcontainers
./gradlew integrationTest

# gRPC service testing
./gradlew grpcTest

# Database migration testing
./gradlew flywayMigrate -Pprofile=test
```

This architecture provides a solid foundation for LLM-native applications with high-performance document management, real-time event processing, and intelligent context aggregation.
