# 🏗️ Domain-Driven Design Architecture

## Overview

Unhinged follows **Domain-Driven Design (DDD)** with **Clean Architecture** principles to ensure maintainable, testable, and scalable code.

## Architecture Layers

### 🎯 **Domain Layer** (`backend/src/main/kotlin/com/unhinged/domain/`)
**Pure business logic - no external dependencies**

```kotlin
// Example: ChatDomain.kt
data class ChatMessage(
    val id: String,
    val content: String,
    val role: MessageRole,
    val timestamp: String,
    val sessionId: String
)

class ChatDomainService {
    fun generateContextualResponse(
        userMessage: String,
        conversationHistory: List<ChatMessage>
    ): String {
        // Pure business logic
    }
}
```

**Key Principles:**
- ✅ No framework dependencies
- ✅ No database dependencies  
- ✅ Pure business rules
- ✅ Domain events for side effects

### 🎯 **Application Layer** (`backend/src/main/kotlin/com/unhinged/application/`)
**Use cases and application services**

```kotlin
// Example: ChatUseCases.kt
class ChatUseCases(
    private val messageRepository: ChatMessageRepository,
    private val sessionRepository: ChatSessionRepository,
    private val domainService: ChatDomainService
) {
    suspend fun sendMessage(request: SendMessageRequest): SendMessageResponse {
        // Orchestrate domain objects
        // Handle transactions
        // Coordinate with infrastructure
    }
}
```

**Key Principles:**
- ✅ Orchestrates domain objects
- ✅ Handles transactions
- ✅ Defines repository interfaces
- ✅ No direct infrastructure dependencies

### 🎯 **Infrastructure Layer** (`backend/src/main/kotlin/com/unhinged/infrastructure/`)
**External concerns - databases, APIs, etc.**

```kotlin
// Example: ChatRepository.kt
interface ChatMessageRepository {
    suspend fun save(message: ChatMessage): ChatMessage
    suspend fun findBySessionId(sessionId: String): List<ChatMessage>
}

class InMemoryChatMessageRepository : ChatMessageRepository {
    // Implementation details
}
```

**Key Principles:**
- ✅ Implements application interfaces
- ✅ Handles external systems
- ✅ Database access
- ✅ HTTP clients

### 🎯 **Presentation Layer** (`backend/src/main/kotlin/com/unhinged/presentation/`)
**HTTP controllers and API endpoints**

```kotlin
// Example: ChatController.kt
class ChatController(private val chatUseCases: ChatUseCases) {
    fun configureRoutes(routing: Routing) {
        routing.post("/api/v1/chat") {
            val request = call.receive<ChatRequest>()
            val response = chatUseCases.sendMessage(request)
            call.respond(response)
        }
    }
}
```

**Key Principles:**
- ✅ HTTP request/response handling
- ✅ Input validation
- ✅ Error handling
- ✅ API documentation

## Dependency Flow

```
Presentation → Application → Domain
     ↓              ↓
Infrastructure ←────┘
```

**Rules:**
- **Domain** depends on nothing
- **Application** depends only on Domain
- **Infrastructure** depends on Application + Domain
- **Presentation** depends on Application + Domain

## Benefits

### 🎯 **Testability**
- Domain logic can be tested in isolation
- Use cases can be tested with mock repositories
- Infrastructure can be tested separately

### 🎯 **Maintainability**
- Clear separation of concerns
- Easy to understand and modify
- Reduced coupling between layers

### 🎯 **Scalability**
- Easy to swap implementations
- Can scale different layers independently
- Ready for microservices if needed

## Frontend Architecture

The frontend follows similar principles:

```typescript
// Services layer (like Infrastructure)
export class ChatService {
    async sendMessage(request: ChatRequest): Promise<ChatResponse> {
        // HTTP client logic
    }
}

// Components (like Presentation)
export const Chatroom: React.FC = () => {
    const { mutate: sendMessage } = useChatMutation();
    // UI logic
};
```

## Key Files

### Backend
- `domain/chat/ChatDomain.kt` - Core business entities
- `application/chat/ChatUseCases.kt` - Use cases
- `infrastructure/chat/ChatRepository.kt` - Data access
- `presentation/http/ChatController.kt` - HTTP endpoints

### Frontend
- `services/ChatService.ts` - API client
- `queries/api.ts` - React Query hooks
- `pages/Chatroom/Chatroom.tsx` - Main UI component

## Adding New Features

1. **Start with Domain**: Define entities and business rules
2. **Add Use Cases**: Define application logic
3. **Create Infrastructure**: Implement repositories/external services
4. **Add Presentation**: Create HTTP endpoints or UI components
5. **Write Tests**: Test each layer independently

## Common Patterns

### Repository Pattern
```kotlin
interface ChatMessageRepository {
    suspend fun save(message: ChatMessage): ChatMessage
    suspend fun findBySessionId(sessionId: String): List<ChatMessage>
}
```

### Use Case Pattern
```kotlin
class SendMessageUseCase(
    private val messageRepository: ChatMessageRepository,
    private val domainService: ChatDomainService
) {
    suspend fun execute(request: SendMessageRequest): SendMessageResponse {
        // Use case logic
    }
}
```

### Domain Events
```kotlin
sealed class ChatDomainEvent {
    data class MessageCreated(val message: ChatMessage) : ChatDomainEvent()
    data class SessionCreated(val session: ChatSession) : ChatDomainEvent()
}
```

This architecture ensures the codebase remains clean, testable, and maintainable as it grows.
