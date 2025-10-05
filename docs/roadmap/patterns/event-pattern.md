# Event Emission Pattern

## Overview

Standardized event emission system for capturing all system interactions with OpenTelemetry compliance and session-based context management.

## Event Structure

### Universal Event Schema
```typescript
interface UniversalEvent {
    id: string;                    // UUID
    event_type: string;           // Hierarchical type (e.g., "llm.inference.completed")
    trace_id: string;             // OpenTelemetry trace ID
    session_id: string;           // Session context
    user_id: string;              // User context
    timestamp_ms: number;         // Unix timestamp in milliseconds
    payload: Record<string, any>; // Event-specific data
    latency_ms?: number;          // Operation duration
    success: boolean;             // Operation success status
    error_message?: string;       // Error details if applicable
}
```

### Protobuf Definition
```protobuf
// proto/events.proto
syntax = "proto3";

message UniversalEvent {
    string id = 1;
    string event_type = 2;
    string trace_id = 3;
    string session_id = 4;
    string user_id = 5;
    int64 timestamp_ms = 6;
    map<string, string> payload = 7;
    int32 latency_ms = 8;
    bool success = 9;
    string error_message = 10;
}

message EventBatch {
    repeated UniversalEvent events = 1;
}
```

## Event Types Hierarchy

### System Events
- `system.startup`
- `system.shutdown`
- `system.health_check`
- `system.error`

### Session Events
- `session.created`
- `session.updated`
- `session.ended`
- `session.context_retrieved`

### LLM Events
- `llm.inference.started`
- `llm.inference.completed`
- `llm.inference.error`
- `llm.token_usage`

### Agent Events
- `agent.created`
- `agent.execution.started`
- `agent.execution.completed`
- `agent.execution.error`
- `agent.communication`

### Data Events
- `data.retrieved`
- `data.processed`
- `data.stored`
- `data.error`

### User Events
- `user.action`
- `user.request`
- `user.response_viewed`

## EventEmitter Implementation

### Core EventEmitter Class
```typescript
// backend/src/events/EventEmitter.ts
import { v4 as uuidv4 } from 'uuid';
import { Database } from '../database/Database';
import { UniversalEvent } from '../types/generated/events';

export class EventEmitter {
    private static instance: EventEmitter;
    
    static getInstance(): EventEmitter {
        if (!EventEmitter.instance) {
            EventEmitter.instance = new EventEmitter();
        }
        return EventEmitter.instance;
    }
    
    async emit(event: Omit<UniversalEvent, 'id' | 'timestamp_ms'>): Promise<string> {
        const fullEvent: UniversalEvent = {
            id: uuidv4(),
            timestamp_ms: Date.now(),
            ...event
        };
        
        // Store in database
        await this.persistEvent(fullEvent);
        
        // Emit to real-time subscribers (WebSocket)
        await this.broadcastEvent(fullEvent);
        
        return fullEvent.id;
    }
    
    private async persistEvent(event: UniversalEvent): Promise<void> {
        const query = `
            INSERT INTO events (id, event_type, trace_id, session_id, user_id, timestamp_ms, payload, success, error_message)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        `;
        
        await Database.query(query, [
            event.id,
            event.event_type,
            event.trace_id,
            event.session_id,
            event.user_id,
            event.timestamp_ms,
            JSON.stringify(event.payload),
            event.success,
            event.error_message || null
        ]);
    }
    
    private async broadcastEvent(event: UniversalEvent): Promise<void> {
        // WebSocket broadcast implementation
        // Will be implemented with WebSocket manager
    }
    
    async getSessionEvents(sessionId: string, limit = 100): Promise<UniversalEvent[]> {
        const query = `
            SELECT * FROM events 
            WHERE session_id = $1 
            ORDER BY timestamp_ms DESC 
            LIMIT $2
        `;
        
        const result = await Database.query(query, [sessionId, limit]);
        return result.rows.map(row => ({
            ...row,
            payload: JSON.parse(row.payload)
        }));
    }
    
    async getTraceEvents(traceId: string): Promise<UniversalEvent[]> {
        const query = `
            SELECT * FROM events 
            WHERE trace_id = $1 
            ORDER BY timestamp_ms ASC
        `;
        
        const result = await Database.query(query, [traceId]);
        return result.rows.map(row => ({
            ...row,
            payload: JSON.parse(row.payload)
        }));
    }
}

// Singleton instance
export const eventEmitter = EventEmitter.getInstance();
```

## Usage Patterns

### Basic Event Emission
```typescript
import { eventEmitter } from '../events/EventEmitter';
import { generateTraceId } from '../utils/tracing';

// In any service or route handler
const traceId = generateTraceId();

await eventEmitter.emit({
    event_type: 'llm.inference.started',
    trace_id: traceId,
    session_id: sessionId,
    user_id: userId,
    payload: {
        prompt: userPrompt,
        model: 'llama3.2'
    },
    success: true
});
```

### Operation Tracking Pattern
```typescript
async function performLLMInference(prompt: string, sessionId: string, userId: string) {
    const traceId = generateTraceId();
    const startTime = Date.now();
    
    try {
        // Emit start event
        await eventEmitter.emit({
            event_type: 'llm.inference.started',
            trace_id: traceId,
            session_id: sessionId,
            user_id: userId,
            payload: { prompt, model: 'llama3.2' },
            success: true
        });
        
        // Perform operation
        const response = await llmService.generate(prompt);
        const latencyMs = Date.now() - startTime;
        
        // Emit completion event
        await eventEmitter.emit({
            event_type: 'llm.inference.completed',
            trace_id: traceId,
            session_id: sessionId,
            user_id: userId,
            payload: {
                prompt,
                response,
                model: 'llama3.2',
                prompt_tokens: countTokens(prompt),
                response_tokens: countTokens(response)
            },
            latency_ms: latencyMs,
            success: true
        });
        
        return response;
        
    } catch (error) {
        // Emit error event
        await eventEmitter.emit({
            event_type: 'llm.inference.error',
            trace_id: traceId,
            session_id: sessionId,
            user_id: userId,
            payload: { prompt, model: 'llama3.2' },
            latency_ms: Date.now() - startTime,
            success: false,
            error_message: error.message
        });
        
        throw error;
    }
}
```

### Middleware Integration
```typescript
// Express middleware for automatic event emission
export const eventMiddleware = (eventType: string) => {
    return async (req: Request, res: Response, next: NextFunction) => {
        const traceId = generateTraceId();
        req.traceId = traceId;
        
        const startTime = Date.now();
        
        // Emit request start event
        await eventEmitter.emit({
            event_type: `${eventType}.started`,
            trace_id: traceId,
            session_id: req.sessionId,
            user_id: req.userId,
            payload: {
                method: req.method,
                path: req.path,
                body: req.body
            },
            success: true
        });
        
        // Override res.json to emit completion event
        const originalJson = res.json;
        res.json = function(data) {
            eventEmitter.emit({
                event_type: `${eventType}.completed`,
                trace_id: traceId,
                session_id: req.sessionId,
                user_id: req.userId,
                payload: { response: data },
                latency_ms: Date.now() - startTime,
                success: res.statusCode < 400
            });
            
            return originalJson.call(this, data);
        };
        
        next();
    };
};
```

## Context Retrieval

### Session Context API
```typescript
// Get all events for LLM context
router.get('/api/sessions/:sessionId/context', async (req, res) => {
    const { sessionId } = req.params;
    const limit = parseInt(req.query.limit as string) || 100;
    
    const events = await eventEmitter.getSessionEvents(sessionId, limit);
    
    // Transform events into LLM-friendly context
    const context = events.map(event => ({
        timestamp: new Date(event.timestamp_ms).toISOString(),
        type: event.event_type,
        data: event.payload,
        success: event.success
    }));
    
    res.json({ sessionId, context, count: context.length });
});
```

## Performance Considerations

### Batch Processing
- Events can be batched for high-throughput scenarios
- Async processing to avoid blocking main thread
- Database connection pooling for concurrent writes

### Indexing Strategy
- Index on session_id for context retrieval
- Index on timestamp_ms for chronological queries
- Index on event_type for filtering
- Index on trace_id for debugging

### Retention Policy
- Archive old events to separate tables
- Implement data lifecycle management
- Compress historical data
