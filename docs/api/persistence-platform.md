# 🏗️ Persistence Platform API Documentation

## Overview

The Unhinged Persistence Platform provides a unified API for interacting with multiple database technologies through a single abstraction layer. This document covers all available contracts and interfaces.

## Base URLs

- **REST API**: `http://localhost:8090/api/v1`
- **gRPC API**: `localhost:9090`
- **Health Check**: `http://localhost:8090/api/v1/health`
- **Metrics**: `http://localhost:8090/api/v1/metrics`

## Contract Locations

### 1. **Protobuf Contracts** (`proto/`)
- **`persistence_platform.proto`** - Main gRPC service definitions
- **`document_store.proto`** - Existing document store service (legacy)
- **`cdc_events.proto`** - Event streaming contracts

### 2. **Kotlin Interfaces** (`platforms/persistence/src/main/kotlin/`)
- **`PersistenceManager.kt`** - Core platform interface
- **`DatabaseProvider.kt`** - Database provider contracts
- **`CoreModels.kt`** - Data models and request/response types

### 3. **Configuration Contracts** (`platforms/persistence/config/`)
- **`persistence-platform.yaml`** - Declarative configuration schema
- **`schema.json`** - JSON schema validation

## API Contracts

### **1. Core CRUD Operations**

#### **Insert Record**
```http
POST /api/v1/tables/{tableName}
Content-Type: application/json

{
  "email": "user@example.com",
  "profile": {
    "name": "John Doe",
    "age": 30
  }
}
```

**gRPC:**
```protobuf
rpc Insert(InsertRequest) returns (InsertResponse);

message InsertRequest {
  string table_name = 1;
  Record record = 2;
  ExecutionContext context = 3;
}
```

#### **Batch Insert**
```http
POST /api/v1/tables/{tableName}/batch
Content-Type: application/json

[
  {"email": "user1@example.com", "name": "User 1"},
  {"email": "user2@example.com", "name": "User 2"}
]
```

#### **Update Record**
```http
PUT /api/v1/tables/{tableName}/{id}
Content-Type: application/json

{
  "profile": {
    "name": "Updated Name"
  }
}
```

#### **Delete Records**
```http
DELETE /api/v1/tables/{tableName}
Content-Type: application/json

{
  "criteria": {
    "type": "Equals",
    "field": "status",
    "value": "inactive"
  }
}
```

### **2. Query Operations**

#### **Execute Named Query**
```http
POST /api/v1/query/{queryName}
Content-Type: application/json

{
  "parameters": {
    "userId": "123e4567-e89b-12d3-a456-426614174000",
    "status": "active",
    "limit": 10
  }
}
```

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "data": {
        "email": "user@example.com",
        "profile": {"name": "John Doe"}
      },
      "created_at": "2025-10-19T10:00:00Z"
    }
  ],
  "count": 1,
  "execution_time_ms": 45,
  "from_cache": false
}
```

#### **Raw Query Execution**
```http
POST /api/v1/query/raw
Content-Type: application/json

{
  "query_spec": {
    "table_name": "users",
    "query_type": "RANGE_SCAN",
    "criteria": {
      "type": "GreaterThan",
      "field": "created_at",
      "value": "2025-01-01T00:00:00Z"
    },
    "limit": 100
  }
}
```

### **3. Vector Operations**

#### **Vector Search**
```http
POST /api/v1/vector/search/{tableName}
Content-Type: application/json

{
  "queryVector": [0.1, 0.2, 0.3, 0.4, 0.5],
  "limit": 10,
  "threshold": 0.7,
  "distanceMetric": "cosine"
}
```

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "record": {
        "id": "doc-123",
        "data": {"title": "Similar Document"}
      },
      "similarity_score": 0.95,
      "distance": 0.05
    }
  ],
  "execution_time_ms": 120
}
```

### **4. Graph Operations**

#### **Graph Traversal**
```http
POST /api/v1/graph/traverse/{tableName}
Content-Type: application/json

{
  "startNode": "user-123",
  "traversalSpec": {
    "traversalType": "BREADTH_FIRST",
    "maxDepth": 3,
    "relationshipTypes": ["FOLLOWS", "LIKES"],
    "nodeFilter": {
      "type": "Equals",
      "field": "active",
      "value": true
    }
  }
}
```

**Response:**
```json
{
  "success": true,
  "nodes": [
    {
      "id": "user-123",
      "label": "User",
      "properties": {"name": "John Doe"}
    }
  ],
  "edges": [
    {
      "id": "edge-456",
      "source_id": "user-123",
      "target_id": "user-789",
      "relationship_type": "FOLLOWS"
    }
  ],
  "execution_time_ms": 200
}
```

### **5. Complex Operations**

#### **Execute Complex Operation**
```http
POST /api/v1/operations/{operationName}
Content-Type: application/json

{
  "parameters": {
    "userId": "123e4567-e89b-12d3-a456-426614174000",
    "action": "create_user_complete",
    "profile": {
      "name": "John Doe",
      "email": "john@example.com"
    }
  }
}
```

**Response:**
```json
{
  "success": true,
  "result": {
    "userId": "123e4567-e89b-12d3-a456-426614174000",
    "sessionId": "session-789",
    "profileCreated": true
  },
  "execution_time_ms": 350,
  "affected_tables": ["users", "user_sessions", "user_profiles"]
}
```

### **6. Platform Management**

#### **Health Check**
```http
GET /api/v1/health
```

**Response:**
```json
{
  "healthy": true,
  "version": "1.0.0",
  "uptime_seconds": 3600,
  "technology_health": [
    {
      "technology": "redis",
      "healthy": true,
      "status": "connected",
      "response_time_ms": 5
    },
    {
      "technology": "cockroachdb",
      "healthy": true,
      "status": "connected",
      "response_time_ms": 15
    }
  ]
}
```

#### **Platform Information**
```http
GET /api/v1/info
```

**Response:**
```json
{
  "platform_name": "Unhinged Persistence Platform",
  "version": "1.0.0",
  "supported_technologies": [
    "redis", "cockroachdb", "mongodb", "weaviate",
    "elasticsearch", "cassandra", "neo4j", "data_lake"
  ],
  "supported_features": [
    "CRUD", "VECTOR_SEARCH", "GRAPH_TRAVERSAL", 
    "FULL_TEXT_SEARCH", "TRANSACTIONS", "CACHING"
  ]
}
```

#### **Metrics**
```http
GET /api/v1/metrics
Accept: application/json
```

**Response (Prometheus format):**
```
# HELP persistence_query_duration_seconds Query execution duration
# TYPE persistence_query_duration_seconds histogram
persistence_query_duration_seconds_bucket{query="get_user_by_id",technology="redis",le="0.005"} 100
persistence_query_duration_seconds_bucket{query="get_user_by_id",technology="redis",le="0.01"} 150
...
```

## Data Models

### **ExecutionContext**
```typescript
interface ExecutionContext {
  requestId: string;
  userId?: string;
  sessionId?: string;
  traceId?: string;
  spanId?: string;
  timestamp: string; // ISO 8601
  metadata?: Record<string, any>;
}
```

### **Record**
```typescript
interface Record {
  id: string;
  data: Record<string, any>;
  created_at: string; // ISO 8601
  updated_at?: string; // ISO 8601
  version?: string;
}
```

### **QueryCriteria**
```typescript
type QueryCriteria = 
  | { type: "Equals"; field: string; value: any }
  | { type: "GreaterThan"; field: string; value: any }
  | { type: "LessThan"; field: string; value: any }
  | { type: "In"; field: string; values: any[] }
  | { type: "Range"; field: string; min_value: any; max_value: any }
  | { type: "TextSearch"; fields: string[]; query: string }
  | { type: "VectorSearch"; field: string; query_vector: number[]; threshold: number }
  | { type: "And"; filters: QueryCriteria[] }
  | { type: "Or"; filters: QueryCriteria[] };
```

## Configuration Schema

### **Platform Configuration**
```yaml
persistence_platform:
  version: "2.1.0"
  
  technologies:
    redis:
      type: "cache"
      clusters: ["redis-cache"]
      connection:
        host: "localhost"
        port: 6379
      
  databases:
    user_data:
      primary_technology: "cockroachdb"
      use_case: "user_profiles"
      
  tables:
    users:
      database: "user_data"
      technology: "cockroachdb"
      schema:
        id: { type: "uuid", primary_key: true }
        email: { type: "string", unique: true, indexed: true }
        
  queries:
    get_user_by_id:
      table: "users"
      type: "point_lookup"
      parameters: ["user_id"]
      cache_strategy: "redis_aside"
      cache_ttl: "5m"
```

## Error Handling

### **Standard Error Response**
```json
{
  "success": false,
  "error": "VALIDATION_ERROR",
  "message": "Invalid query parameters",
  "details": {
    "field": "user_id",
    "reason": "must be a valid UUID"
  }
}
```

### **Error Codes**
- `VALIDATION_ERROR` - Invalid request parameters
- `NOT_FOUND` - Resource not found
- `TECHNOLOGY_UNAVAILABLE` - Database technology unavailable
- `QUERY_TIMEOUT` - Query execution timeout
- `INSUFFICIENT_PERMISSIONS` - Access denied
- `INTERNAL_ERROR` - Internal platform error

## Client Libraries

### **Kotlin Client**
```kotlin
val persistenceManager = PersistenceManagerImpl(config)

// Insert record
val user = mapOf("email" to "user@example.com")
val result = persistenceManager.insert("users", user, context)

// Execute query
val users = persistenceManager.executeQuery<Map<String, Any>>(
    "get_active_users", 
    mapOf("status" to "active"), 
    context
).toList()
```

### **TypeScript Client**
```typescript
import { PersistencePlatformClient } from './generated/persistence_platform';

const client = new PersistencePlatformClient('localhost:9090');

// Insert record
const response = await client.insert({
  tableName: 'users',
  record: {
    data: { email: 'user@example.com' }
  }
});
```

## Authentication & Authorization

Currently in development mode with no authentication required. Production deployment will include:
- JWT token authentication
- Role-based access control (RBAC)
- API key management
- Rate limiting per client

## Rate Limiting

Development: No limits
Production: 
- 1000 requests/minute per API key
- 100 concurrent connections per client
- Burst allowance of 200 requests

---

**For complete implementation details, see the source code in `platforms/persistence/` and protobuf definitions in `proto/`.**
