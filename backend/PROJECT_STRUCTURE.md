# Backend Project Structure

## 🎯 **Clean Organization**

```
backend/
├── 🚀 Application Entry Point
│   └── src/main/kotlin/com/unhinged/
│       ├── Application.kt              # Main app with HTTP + gRPC servers
│       └── di/                         # Dependency injection modules
│           ├── DatabaseModule.kt       # HikariCP connection pools
│           ├── DocumentStoreModule.kt  # DocumentStore service DI
│           ├── CDCModule.kt           # Event streaming DI
│           └── SimpleImplementations.kt # Basic implementations
│
├── 🔧 Services (Hand-Written Business Logic)
│   └── src/main/kotlin/com/unhinged/services/
│       ├── documentstore/              # DocumentStore service
│       │   ├── DocumentStoreService.kt     # gRPC service (11 endpoints)
│       │   ├── DocumentRepository.kt       # Interface
│       │   ├── DocumentRepositoryImpl.kt   # PostgreSQL implementation
│       │   ├── DocumentEventEmitter.kt     # Interface
│       │   └── DocumentEventEmitterImpl.kt # CDC integration
│       │
│       └── cdc/                        # CDC service
│           ├── CDCService.kt           # Change data capture service
│           └── MinimalCDCService.kt    # Lightweight implementation
│
├── 🤖 Generated Code (Don't Touch)
│   └── src/generated/kotlin/unhinged/
│       ├── document_store/             # Generated from document_store.proto
│       ├── cdc/                        # Generated from cdc_*.proto
│       └── messaging/                  # Generated from messaging.proto
│
├── 🗄️ Resources
│   └── src/main/resources/
│       ├── application.conf            # HOCON configuration
│       └── db/migration/               # Flyway SQL migrations
│           └── V001__create_document_store_schema.sql
│
├── 🧪 Tests
│   └── src/test/kotlin/
│       └── ApplicationTest.kt
│
├── 🗑️ Legacy (To Be Refactored)
│   └── src/main/kotlin/com/unhinged/legacy/
│       ├── Main.kt                     # Old Ktor entry point
│       ├── Routing.kt                  # HTTP routes
│       ├── Security.kt                 # Auth
│       ├── Serialization.kt            # JSON config
│       ├── Sockets.kt                  # WebSocket config
│       └── Databases.kt                # Old DB config
│
└── 📋 Build Configuration
    ├── build.gradle.kts                # Dependencies + protobuf generation
    ├── settings.gradle.kts             # Project settings
    └── Dockerfile                      # Container build
```

## 🎯 **What You Actually Work On**

### **Core Services** (`src/main/kotlin/com/unhinged/services/`)
- **DocumentStore**: Complete gRPC service with LLM features
- **CDC**: Event streaming and change data capture

### **Configuration** (`src/main/kotlin/com/unhinged/di/`)
- **Dependency Injection**: Koin modules for all services
- **Database**: Connection pools and transaction management

### **Database** (`src/main/resources/db/migration/`)
- **SQL Migrations**: PostgreSQL schema with JSONB optimization

## 🤖 **What's Auto-Generated**

### **Protobuf Code** (`src/generated/kotlin/unhinged/`)
- Generated from 4 `.proto` files
- gRPC service stubs and message types
- **Don't edit these files directly**

## 🔧 **Key Files**

| File | Purpose |
|------|---------|
| `Application.kt` | Main entry point, starts HTTP:8080 + gRPC:9090 |
| `DocumentStoreService.kt` | 11 gRPC endpoints for document management |
| `DocumentRepositoryImpl.kt` | PostgreSQL implementation with JSONB |
| `DocumentEventEmitterImpl.kt` | CDC integration for real-time events |
| `application.conf` | Configuration with LLM-specific settings |
| `build.gradle.kts` | Dependencies and protobuf generation |

## 🚀 **Development Workflow**

1. **Modify protobuf schemas** in `proto/` directory
2. **Run protobuf generation** → updates `src/generated/`
3. **Implement business logic** in `src/main/kotlin/com/unhinged/services/`
4. **Update DI configuration** in `src/main/kotlin/com/unhinged/di/`
5. **Add database migrations** in `src/main/resources/db/migration/`

## 🎯 **Clean Separation**

- ✅ **Services**: Hand-written business logic
- ✅ **Generated**: Auto-generated protobuf code
- ✅ **Legacy**: Old code to be refactored
- ✅ **Resources**: Configuration and migrations
- ✅ **Tests**: Unit and integration tests

No more organizational cruft!
