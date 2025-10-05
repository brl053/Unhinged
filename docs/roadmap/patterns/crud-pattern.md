# E2E CRUD Pattern

## Overview

Standardized pattern for creating entities with full CRUD operations, event emission, and frontend integration. This pattern ensures consistency and rapid replication across all system entities.

## Pattern Structure

### 1. Database Schema
```sql
-- Entity table with standard fields
CREATE TABLE {entity_name}s (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(255),
    session_id VARCHAR(255),
    -- Entity-specific fields
    {entity_fields}
);

-- Indexes for performance
CREATE INDEX idx_{entity_name}s_session_id ON {entity_name}s(session_id);
CREATE INDEX idx_{entity_name}s_created_at ON {entity_name}s(created_at);
```

### 2. Protobuf Schema
```protobuf
// proto/{entity_name}.proto
syntax = "proto3";

message {EntityName} {
    string id = 1;
    int64 created_at = 2;
    int64 updated_at = 3;
    string created_by = 4;
    string session_id = 5;
    // Entity-specific fields
}

message Create{EntityName}Request {
    string session_id = 1;
    string created_by = 2;
    // Entity-specific fields
}

message {EntityName}Response {
    bool success = 1;
    string message = 2;
    {EntityName} data = 3;
}

message List{EntityName}sRequest {
    string session_id = 1;
    int32 limit = 2;
    int32 offset = 3;
}

message List{EntityName}sResponse {
    bool success = 1;
    repeated {EntityName} data = 2;
    int32 total = 3;
}
```

### 3. Backend API Endpoints
```typescript
// backend/src/routes/{entity_name}.ts
import { Router } from 'express';
import { {EntityName}Service } from '../services/{entity_name}Service';
import { EventEmitter } from '../events/EventEmitter';

const router = Router();

// CREATE
router.post('/api/{entity_name}s', async (req, res) => {
    const traceId = generateTraceId();
    const startTime = Date.now();
    
    try {
        const entity = await {EntityName}Service.create(req.body);
        
        // Emit event
        EventEmitter.emit({
            type: '{entity_name}.created',
            traceId,
            sessionId: req.body.session_id,
            userId: req.body.created_by,
            payload: { entityId: entity.id, ...req.body },
            latencyMs: Date.now() - startTime
        });
        
        res.json({ success: true, data: entity });
    } catch (error) {
        EventEmitter.emit({
            type: '{entity_name}.create.error',
            traceId,
            sessionId: req.body.session_id,
            userId: req.body.created_by,
            payload: { error: error.message },
            latencyMs: Date.now() - startTime
        });
        
        res.status(500).json({ success: false, message: error.message });
    }
});

// READ (single)
router.get('/api/{entity_name}s/:id', async (req, res) => {
    // Similar pattern with event emission
});

// READ (list)
router.get('/api/{entity_name}s', async (req, res) => {
    // Similar pattern with event emission
});

// UPDATE
router.put('/api/{entity_name}s/:id', async (req, res) => {
    // Similar pattern with event emission
});

// DELETE
router.delete('/api/{entity_name}s/:id', async (req, res) => {
    // Similar pattern with event emission
});

export default router;
```

### 4. Service Layer
```typescript
// backend/src/services/{entity_name}Service.ts
import { Database } from '../database/Database';
import { {EntityName} } from '../types/generated/{entity_name}';

export class {EntityName}Service {
    static async create(data: Create{EntityName}Request): Promise<{EntityName}> {
        const query = `
            INSERT INTO {entity_name}s (created_by, session_id, {fields})
            VALUES ($1, $2, {values})
            RETURNING *
        `;
        
        const result = await Database.query(query, [
            data.created_by,
            data.session_id,
            // Entity-specific values
        ]);
        
        return result.rows[0];
    }
    
    static async findById(id: string): Promise<{EntityName} | null> {
        const query = 'SELECT * FROM {entity_name}s WHERE id = $1';
        const result = await Database.query(query, [id]);
        return result.rows[0] || null;
    }
    
    static async findBySession(sessionId: string, limit = 50, offset = 0): Promise<{EntityName}[]> {
        const query = `
            SELECT * FROM {entity_name}s 
            WHERE session_id = $1 
            ORDER BY created_at DESC 
            LIMIT $2 OFFSET $3
        `;
        const result = await Database.query(query, [sessionId, limit, offset]);
        return result.rows;
    }
    
    static async update(id: string, data: Partial<{EntityName}>): Promise<{EntityName}> {
        // Update implementation with updated_at timestamp
    }
    
    static async delete(id: string): Promise<boolean> {
        const query = 'DELETE FROM {entity_name}s WHERE id = $1';
        const result = await Database.query(query, [id]);
        return result.rowCount > 0;
    }
}
```

### 5. Frontend Components
```typescript
// frontend/src/components/{EntityName}/{EntityName}List.tsx
import React, { useEffect, useState } from 'react';
import { {EntityName} } from '../../types/generated/{entity_name}';
import { {EntityName}Service } from '../../services/{entity_name}Service';

export const {EntityName}List: React.FC<{ sessionId: string }> = ({ sessionId }) => {
    const [entities, setEntities] = useState<{EntityName}[]>([]);
    const [loading, setLoading] = useState(true);
    
    useEffect(() => {
        const loadEntities = async () => {
            try {
                const response = await {EntityName}Service.list(sessionId);
                setEntities(response.data);
            } catch (error) {
                console.error('Failed to load {entity_name}s:', error);
            } finally {
                setLoading(false);
            }
        };
        
        loadEntities();
    }, [sessionId]);
    
    if (loading) return <div>Loading {entity_name}s...</div>;
    
    return (
        <div className="{entity_name}-list">
            {entities.map(entity => (
                <div key={entity.id} className="{entity_name}-item">
                    {/* Entity-specific rendering */}
                </div>
            ))}
        </div>
    );
};
```

### 6. Frontend Service
```typescript
// frontend/src/services/{entity_name}Service.ts
import { ApiClient } from './ApiClient';
import { {EntityName}, Create{EntityName}Request } from '../types/generated/{entity_name}';

export class {EntityName}Service {
    static async create(data: Create{EntityName}Request): Promise<{EntityName}> {
        const response = await ApiClient.post('/api/{entity_name}s', data);
        return response.data;
    }
    
    static async list(sessionId: string): Promise<{EntityName}[]> {
        const response = await ApiClient.get(`/api/{entity_name}s?session_id=${sessionId}`);
        return response.data;
    }
    
    static async getById(id: string): Promise<{EntityName}> {
        const response = await ApiClient.get(`/api/{entity_name}s/${id}`);
        return response.data;
    }
    
    static async update(id: string, data: Partial<{EntityName}>): Promise<{EntityName}> {
        const response = await ApiClient.put(`/api/{entity_name}s/${id}`, data);
        return response.data;
    }
    
    static async delete(id: string): Promise<boolean> {
        const response = await ApiClient.delete(`/api/{entity_name}s/${id}`);
        return response.success;
    }
}
```

## Implementation Checklist

For each new entity:

- [ ] Create database migration
- [ ] Define protobuf schema
- [ ] Generate TypeScript types
- [ ] Implement service layer
- [ ] Create API routes with event emission
- [ ] Build frontend components
- [ ] Add frontend service client
- [ ] Write tests
- [ ] Update documentation

## Event Types

Standard events emitted for each entity:
- `{entity_name}.created`
- `{entity_name}.updated`
- `{entity_name}.deleted`
- `{entity_name}.viewed`
- `{entity_name}.listed`
- `{entity_name}.{operation}.error`
