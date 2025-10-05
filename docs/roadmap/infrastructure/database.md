# Database Architecture

## Document Store Pattern

We implement a document-style storage over PostgreSQL that provides NoSQL-like API interface with versioning, tagging, and CDC capabilities.

## Core Design Principles

### 1. Document-Centric Storage
- Store JSON documents with metadata in relational tables
- Separate document headers from bodies for performance
- Support versioning and tagging for document lifecycle management
- Enable composite indexing on JSON fields

### 2. Key-Value Architecture Over SQL
- Use PostgreSQL's JSONB support for flexible document storage
- Design primary keys for optimal distribution and performance
- Leverage JSON expression indexes for query performance
- Maintain relational benefits while providing document store interface

## Table Design

### document_header Table
Primary table for document metadata and indexing.

```sql
CREATE TABLE document_header (
    document_uuid UUID NOT NULL,
    type STRING NOT NULL,
    name STRING,
    namespace STRING NOT NULL,
    version INT NOT NULL,
    metadata JSONB,
    document_body_uuid UUID NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by STRING,
    created_by_type STRING,
    session_id STRING,
    PRIMARY KEY (namespace, type, document_uuid, version)
);

-- Performance indexes
CREATE INDEX CONCURRENTLY document_header_document_uuid_version_idx 
ON document_header (document_uuid, version) 
STORING (name, metadata, document_body_uuid, created_at, created_by, created_by_type, session_id);

CREATE INDEX CONCURRENTLY document_header_created_at_idx 
ON document_header (created_at DESC) 
STORING (name, metadata, document_body_uuid, created_at, created_by, created_by_type, session_id);

CREATE INDEX CONCURRENTLY document_header_session_id_idx 
ON document_header (session_id, created_at DESC);
```

### document_body Table
Separate table for large JSON payloads to avoid row size issues.

```sql
CREATE TABLE document_body (
    document_body_uuid UUID NOT NULL,
    body JSONB NOT NULL,
    PRIMARY KEY (document_body_uuid)
);

ALTER TABLE document_header 
ADD CONSTRAINT document_body_uuid_fkey 
FOREIGN KEY (document_body_uuid) 
REFERENCES document_body(document_body_uuid) 
ON DELETE CASCADE;
```

### active_tag Table
Version management through document tagging.

```sql
CREATE TABLE active_tag (
    document_uuid UUID NOT NULL,
    document_version INT NOT NULL,
    tag STRING NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_by STRING,
    updated_by_type STRING,
    session_id STRING,
    PRIMARY KEY (tag, document_uuid)
);

CREATE INDEX CONCURRENTLY active_tag_version_idx 
ON active_tag (document_uuid, document_version);

CREATE INDEX CONCURRENTLY active_tag_updated_at_idx 
ON active_tag (updated_at) 
STORING (document_version, updated_by, updated_by_type, session_id);
```

### tag_event Table
Audit log for tag changes and version management.

```sql
CREATE TABLE tag_event (
    tag_event_uuid UUID NOT NULL,
    document_uuid UUID NOT NULL,
    document_version INT NOT NULL,
    tag STRING NOT NULL,
    operation STRING,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by STRING,
    created_by_type STRING,
    session_id STRING,
    PRIMARY KEY (tag, tag_event_uuid)
);

CREATE INDEX CONCURRENTLY tag_event_document_uuid_tag_idx 
ON tag_event (document_uuid, tag);

CREATE INDEX CONCURRENTLY tag_event_created_at_idx 
ON tag_event (created_at DESC) 
STORING (document_uuid, document_version, tag, operation, created_by, created_by_type, session_id);
```

## Document Types for Unhinged

### Core Document Types
1. **Session Context** - User session data and conversation history
2. **Agent Configuration** - Agent definitions and parameters
3. **Workflow Definition** - DAG definitions and execution plans
4. **LLM Interaction** - Prompts, responses, and metadata
5. **Knowledge Base** - Reference documents and embeddings
6. **User Feedback** - Ratings, corrections, and annotations

### Versioning Strategy
- Each document identified by `document_uuid`
- Versions increment automatically on updates
- Tags enable production/staging/experimental workflows
- Audit trail through `tag_event` table

### Composite Indexing
JSON expression indexes on metadata for performance:

```sql
-- Example: Index agent configurations by type and status
CREATE INDEX idx_agent_config_type_status 
ON document_header (type, (metadata->>'agent_type'), (metadata->>'status'))
WHERE type = 'agent_configuration';

-- Example: Index sessions by user and activity
CREATE INDEX idx_session_user_activity 
ON document_header (type, (metadata->>'user_id'), (metadata->>'last_activity'))
WHERE type = 'session_context';
```

## Integration with Event System

### CDC Integration
- All document operations emit events through our event system
- Document changes trigger workflow executions
- Version changes tracked for audit and rollback

### Session Context API
Documents provide rich context for LLM interactions:

```typescript
// Get all documents for session context
const sessionDocs = await DocumentStore.getBySession(sessionId, {
  types: ['llm_interaction', 'user_feedback', 'agent_configuration'],
  includeBody: true,
  limit: 100
});

// Emit event for document access
await eventEmitter.emit({
  event_type: 'document.accessed',
  trace_id: traceId,
  session_id: sessionId,
  user_id: userId,
  payload: {
    document_count: sessionDocs.length,
    document_types: sessionDocs.map(d => d.type)
  }
});
```

## Performance Considerations

### Query Optimization
- Primary key design enables efficient range scans
- Separate body table prevents large row performance issues
- JSON indexes on frequently queried metadata fields
- Pagination using keyset pagination on timestamps

### Scaling Strategy
- Horizontal scaling through namespace partitioning
- Read replicas for query-heavy workloads
- Archive old versions using TTL policies
- Composite index tuning based on query patterns

## Migration and Evolution

### Adding New Document Types
Simply insert documents with new `type` values - no schema changes required.

### Adding New Indexes
```sql
-- Add new composite index for specific document type
CREATE INDEX CONCURRENTLY idx_document_custom_field 
ON document_header (type, (metadata->>'custom_field'))
WHERE type = 'new_document_type';
```

### Data Lifecycle Management
- TTL-based cleanup of old versions
- Preserve tagged versions longer
- Archive to cold storage for compliance
- CDC events for downstream processing
