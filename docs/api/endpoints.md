# 📡 API Endpoints Documentation

## Base URL
- **Development**: `http://localhost:8080`
- **Production**: TBD

## Authentication
Currently no authentication required (development mode).

## Chat API

### POST /chat (Legacy)
**Backward compatible endpoint for simple chat**

```bash
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello, how are you?"}'
```

**Response:**
```
Hello again! What would you like to discuss?
```

### POST /api/v1/chat (Modern)
**Full-featured chat endpoint with session management**

```bash
curl -X POST http://localhost:8080/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Hello, how are you?",
    "sessionId": "optional-session-id",
    "userId": "user-123"
  }'
```

**Response:**
```json
{
  "response": "Hello again! What would you like to discuss?",
  "sessionId": "session-abc-123",
  "messageId": "msg-456-789",
  "processingTimeMs": 45
}
```

## Session Management

### POST /api/v1/sessions
**Create a new chat session**

```bash
curl -X POST http://localhost:8080/api/v1/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "userId": "user-123",
    "title": "My Chat Session"
  }'
```

**Response:**
```json
{
  "sessionId": "session-abc-123",
  "userId": "user-123",
  "title": "My Chat Session",
  "createdAt": "2025-01-05T10:30:00Z",
  "isActive": true
}
```

### GET /api/v1/sessions/user/{userId}
**Get user's chat sessions**

```bash
curl http://localhost:8080/api/v1/sessions/user/user-123
```

**Response:**
```json
[
  {
    "sessionId": "session-abc-123",
    "userId": "user-123",
    "title": "My Chat Session",
    "createdAt": "2025-01-05T10:30:00Z",
    "isActive": true
  }
]
```

### GET /api/v1/sessions/{sessionId}
**Get specific session details**

```bash
curl http://localhost:8080/api/v1/sessions/session-abc-123
```

**Response:**
```json
{
  "sessionId": "session-abc-123",
  "userId": "user-123",
  "title": "My Chat Session",
  "createdAt": "2025-01-05T10:30:00Z",
  "isActive": true
}
```

### GET /api/v1/sessions/{sessionId}/messages
**Get conversation history**

```bash
curl "http://localhost:8080/api/v1/sessions/session-abc-123/messages?limit=50"
```

**Response:**
```json
{
  "sessionId": "session-abc-123",
  "messages": [
    {
      "id": "msg-123",
      "content": "Hello, how are you?",
      "role": "user",
      "timestamp": "2025-01-05T10:30:00Z"
    },
    {
      "id": "msg-124",
      "content": "Hello again! What would you like to discuss?",
      "role": "assistant",
      "timestamp": "2025-01-05T10:30:01Z"
    }
  ],
  "totalCount": 2
}
```

### DELETE /api/v1/sessions/{sessionId}
**Delete a session and all its messages**

```bash
curl -X DELETE http://localhost:8080/api/v1/sessions/session-abc-123
```

**Response:** `204 No Content`

## Health & Monitoring

### GET /api/v1/health
**Health check endpoint**

```bash
curl http://localhost:8080/api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "chat-use-cases",
  "timestamp": "2025-01-05T10:30:00Z",
  "version": "1.0.0"
}
```

### GET /
**Service information**

```bash
curl http://localhost:8080/
```

**Response:**
```
🔥 Unhinged Backend v2.0.0 - Clean Architecture

📋 Available endpoints:
- GET    /                           - This info
- GET    /api/v1/health             - Health check
- POST   /chat                      - Legacy chat (backward compatible)
- POST   /api/v1/chat               - Modern chat API
- POST   /api/v1/sessions           - Create session
- GET    /api/v1/sessions/user/{id} - Get user sessions
- GET    /api/v1/sessions/{id}      - Get session
- GET    /api/v1/sessions/{id}/messages - Get conversation
- DELETE /api/v1/sessions/{id}      - Delete session

🏗️  Architecture: Domain-Driven Design with Clean Architecture
📦 Layers: Domain → Application → Infrastructure → Presentation
🔄 Status: Ready for production scaling
```

## Error Responses

### 400 Bad Request
```json
{
  "error": "Invalid request format"
}
```

### 404 Not Found
```json
{
  "error": "Session not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Failed to process chat request: Database connection failed"
}
```

## Rate Limiting
Currently no rate limiting (development mode).

## CORS
Configured for development:
- Allows all origins (`*`)
- Allows all methods
- Allows all headers

## Data Types

### ChatMessage
```typescript
interface ChatMessage {
  id: string;
  content: string;
  role: 'user' | 'assistant' | 'system';
  timestamp: string; // ISO 8601
}
```

### ChatSession
```typescript
interface ChatSession {
  sessionId: string;
  userId: string;
  title?: string;
  createdAt: string; // ISO 8601
  isActive: boolean;
}
```

### ChatRequest
```typescript
interface ChatRequest {
  prompt: string;
  sessionId?: string;
  userId?: string;
}
```

### ChatResponse
```typescript
interface ChatResponse {
  response: string;
  sessionId: string;
  messageId: string;
  processingTimeMs: number;
}
```

## Frontend Integration

The frontend uses these endpoints through the `ChatService`:

```typescript
import { chatService } from '../services/ChatService';

// Send message
const response = await chatService.sendMessage({
  prompt: "Hello!",
  sessionId: "session-123",
  userId: "user-456"
});

// Get conversation
const conversation = await chatService.getConversation("session-123");
```
