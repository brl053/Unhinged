-- ============================================================================
-- DocumentStore Database Schema
-- ============================================================================
-- 
-- @file V001__create_document_store_schema.sql
-- @version 1.0.0
-- @author Unhinged Team
-- @date 2025-01-04
-- @description PostgreSQL schema for LLM-native document store with versioning
-- 
-- This schema implements the document store pattern with:
-- - Document-centric storage with JSONB for flexible content
-- - Separate header/body tables for performance optimization
-- - Version management through tagging system
-- - LLM-optimized indexes for session context queries
-- - Audit trails for compliance and debugging
-- 
-- LLM-Native Optimizations:
-- - Composite indexes on (session_id, type, created_at) for context queries
-- - JSON expression indexes on metadata fields for semantic search
-- - Separate body table to avoid large row performance issues
-- - Tag-based version serving for A/B testing LLM responses
-- ============================================================================

-- Enable required PostgreSQL extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ============================================================================
-- Document Header Table
-- ============================================================================
-- Primary table for document metadata and indexing
-- Optimized for fast queries and joins

CREATE TABLE document_header (
    -- Primary identification
    document_uuid UUID NOT NULL,
    type VARCHAR(100) NOT NULL,
    name VARCHAR(500),
    namespace VARCHAR(100) NOT NULL,
    version INTEGER NOT NULL,
    
    -- Content reference
    document_body_uuid UUID NOT NULL,
    
    -- LLM-optimized metadata stored as JSONB for flexible querying
    metadata JSONB DEFAULT '{}',
    
    -- Audit and tracking fields
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by VARCHAR(100),
    created_by_type VARCHAR(50),
    session_id VARCHAR(100),
    
    -- Primary key ensures unique document versions
    PRIMARY KEY (namespace, type, document_uuid, version)
);

-- ============================================================================
-- Document Body Table
-- ============================================================================
-- Separate table for large JSON payloads to avoid row size issues
-- Enables efficient metadata queries without loading large content

CREATE TABLE document_body (
    document_body_uuid UUID PRIMARY KEY,
    body JSONB NOT NULL
);

-- Foreign key constraint to ensure referential integrity
ALTER TABLE document_header 
ADD CONSTRAINT document_body_uuid_fkey 
FOREIGN KEY (document_body_uuid) 
REFERENCES document_body(document_body_uuid) 
ON DELETE CASCADE;

-- ============================================================================
-- Active Tag Table
-- ============================================================================
-- Version management through document tagging
-- Enables production/staging/experimental workflows

CREATE TABLE active_tag (
    document_uuid UUID NOT NULL,
    document_version INTEGER NOT NULL,
    tag VARCHAR(100) NOT NULL,
    
    -- Tag metadata
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_by VARCHAR(100),
    updated_by_type VARCHAR(50),
    session_id VARCHAR(100),
    
    -- Primary key ensures one tag per document
    PRIMARY KEY (tag, document_uuid)
);

-- ============================================================================
-- Tag Event Table
-- ============================================================================
-- Audit log for tag changes and version management
-- Provides complete history of version promotions

CREATE TABLE tag_event (
    tag_event_uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_uuid UUID NOT NULL,
    document_version INTEGER NOT NULL,
    tag VARCHAR(100) NOT NULL,
    operation VARCHAR(20) NOT NULL, -- 'add', 'remove', 'update'
    
    -- Event metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by VARCHAR(100),
    created_by_type VARCHAR(50),
    session_id VARCHAR(100)
);

-- ============================================================================
-- LLM-Optimized Performance Indexes
-- ============================================================================

-- Primary document lookup by UUID and version
CREATE INDEX CONCURRENTLY document_header_document_uuid_version_idx 
ON document_header (document_uuid, version) 
INCLUDE (name, metadata, document_body_uuid, created_at, created_by, created_by_type, session_id);

-- Time-based queries for recent documents
CREATE INDEX CONCURRENTLY document_header_created_at_idx 
ON document_header (created_at DESC) 
INCLUDE (document_uuid, type, name, namespace, version, metadata, session_id);

-- Session context queries (critical for LLM prompt construction)
CREATE INDEX CONCURRENTLY document_header_session_id_type_created_at_idx 
ON document_header (session_id, type, created_at DESC)
WHERE session_id IS NOT NULL;

-- Namespace and type filtering
CREATE INDEX CONCURRENTLY document_header_namespace_type_idx 
ON document_header (namespace, type, created_at DESC);

-- Tag-based document serving
CREATE INDEX CONCURRENTLY active_tag_version_idx 
ON active_tag (document_uuid, document_version);

CREATE INDEX CONCURRENTLY active_tag_updated_at_idx 
ON active_tag (updated_at DESC) 
INCLUDE (document_uuid, document_version, tag, updated_by, updated_by_type, session_id);

-- Tag event audit queries
CREATE INDEX CONCURRENTLY tag_event_document_uuid_tag_idx 
ON tag_event (document_uuid, tag, created_at DESC);

CREATE INDEX CONCURRENTLY tag_event_created_at_idx 
ON tag_event (created_at DESC) 
INCLUDE (document_uuid, document_version, tag, operation, created_by, created_by_type, session_id);

-- ============================================================================
-- LLM-Specific JSON Expression Indexes
-- ============================================================================
-- These indexes enable fast queries on document metadata for LLM workflows

-- Index for agent configurations by type and status
CREATE INDEX CONCURRENTLY idx_agent_config_type_status 
ON document_header USING GIN ((metadata->>'agent_type'), (metadata->>'status'))
WHERE type = 'agent_configuration';

-- Index for LLM interactions by model and completion status
CREATE INDEX CONCURRENTLY idx_llm_interaction_model_status 
ON document_header USING GIN ((metadata->>'model_name'), (metadata->>'completion_status'))
WHERE type = 'llm_interaction';

-- Index for session context by user and activity timestamp
CREATE INDEX CONCURRENTLY idx_session_user_activity 
ON document_header USING GIN ((metadata->>'user_id'), (metadata->>'last_activity'))
WHERE type = 'session_context';

-- Index for knowledge base documents by topic and relevance
CREATE INDEX CONCURRENTLY idx_knowledge_base_topic_relevance 
ON document_header USING GIN ((metadata->>'topic'), (metadata->>'relevance_score'))
WHERE type = 'knowledge_base';

-- Full-text search on document content (for semantic search)
CREATE INDEX CONCURRENTLY idx_document_body_fulltext 
ON document_body USING GIN (to_tsvector('english', body::text));

-- ============================================================================
-- Performance and Maintenance Views
-- ============================================================================

-- View for latest document versions (commonly used in LLM contexts)
CREATE VIEW latest_documents AS
SELECT DISTINCT ON (document_uuid) 
    document_uuid, type, name, namespace, version, metadata, 
    document_body_uuid, created_at, created_by, created_by_type, session_id
FROM document_header
ORDER BY document_uuid, version DESC;

-- View for tagged documents (for production/staging workflows)
CREATE VIEW tagged_documents AS
SELECT 
    dh.document_uuid, dh.type, dh.name, dh.namespace, dh.version,
    dh.metadata, dh.document_body_uuid, dh.created_at, dh.created_by, 
    dh.created_by_type, dh.session_id,
    at.tag, at.updated_at as tagged_at, at.updated_by as tagged_by
FROM document_header dh
JOIN active_tag at ON dh.document_uuid = at.document_uuid 
                  AND dh.version = at.document_version;

-- View for session context with document counts (for LLM optimization)
CREATE VIEW session_document_stats AS
SELECT 
    session_id,
    COUNT(*) as total_documents,
    COUNT(DISTINCT type) as document_types,
    MAX(created_at) as last_activity,
    SUM(LENGTH(db.body::text)) as total_content_size
FROM document_header dh
JOIN document_body db ON dh.document_body_uuid = db.document_body_uuid
WHERE session_id IS NOT NULL
GROUP BY session_id;

-- ============================================================================
-- Data Integrity Constraints
-- ============================================================================

-- Ensure document versions are positive
ALTER TABLE document_header 
ADD CONSTRAINT document_header_version_positive 
CHECK (version > 0);

-- Ensure tag names follow naming conventions
ALTER TABLE active_tag 
ADD CONSTRAINT active_tag_name_format 
CHECK (tag ~ '^[a-z0-9_-]+$');

-- Ensure operation types are valid
ALTER TABLE tag_event 
ADD CONSTRAINT tag_event_operation_valid 
CHECK (operation IN ('add', 'remove', 'update'));

-- ============================================================================
-- Row Level Security (Future Enhancement)
-- ============================================================================
-- Placeholder for multi-tenant security policies

-- Enable RLS on all tables (disabled by default)
-- ALTER TABLE document_header ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE document_body ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE active_tag ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE tag_event ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- Comments for Documentation
-- ============================================================================

COMMENT ON TABLE document_header IS 'Primary document metadata table optimized for LLM context queries';
COMMENT ON TABLE document_body IS 'Document content storage separated for performance optimization';
COMMENT ON TABLE active_tag IS 'Version management through document tagging for A/B testing';
COMMENT ON TABLE tag_event IS 'Audit trail for tag changes and version promotions';

COMMENT ON COLUMN document_header.metadata IS 'JSONB metadata for flexible LLM-specific attributes';
COMMENT ON COLUMN document_header.session_id IS 'Session identifier for LLM context aggregation';
COMMENT ON COLUMN document_body.body IS 'JSONB document content for flexible schema evolution';

-- ============================================================================
-- Initial Data and Configuration
-- ============================================================================

-- Insert initial configuration documents
INSERT INTO document_body (document_body_uuid, body) VALUES 
(uuid_generate_v4(), '{"system": "document_store", "version": "1.0.0", "initialized": true}');

INSERT INTO document_header (
    document_uuid, type, name, namespace, version, metadata, 
    document_body_uuid, created_by, created_by_type
) VALUES (
    uuid_generate_v4(), 
    'system_config', 
    'DocumentStore Configuration', 
    'system', 
    1, 
    '{"component": "document_store", "version": "1.0.0"}',
    (SELECT document_body_uuid FROM document_body WHERE body->>'system' = 'document_store'),
    'system',
    'migration'
);
