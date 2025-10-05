-- ============================================================================
-- Migration: 001_cdc_foundation
-- Description: CDC foundation with tenant-aware event storage and analytics
-- Author: LLM Agent
-- Created: 2025-01-04
-- ============================================================================

-- Create schema_migrations table if it doesn't exist
CREATE TABLE IF NOT EXISTS schema_migrations (
    version VARCHAR(20) PRIMARY KEY,
    description TEXT NOT NULL,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Record this migration
INSERT INTO schema_migrations (version, description) 
VALUES ('001', 'CDC foundation with tenant-aware event storage and analytics')
ON CONFLICT (version) DO NOTHING;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "btree_gin";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ============================================================================
-- CORE EVENT STORAGE - OLTP Optimized
-- ============================================================================

-- Main events table - high-throughput writes, tenant-aware, protobuf optimized
CREATE TABLE events (
    -- Primary identifiers
    event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type VARCHAR(100) NOT NULL,
    event_version VARCHAR(20) NOT NULL DEFAULT '1.0.0',
    timestamp_ms BIGINT NOT NULL,

    -- Correlation and causation
    correlation_id UUID NOT NULL,
    causation_id UUID,
    sequence_number BIGINT NOT NULL,

    -- Multi-tenancy and context
    tenant_id VARCHAR(50) NOT NULL,
    user_id UUID,
    session_id UUID,
    workflow_id UUID,

    -- Source information
    source_service VARCHAR(100) NOT NULL,
    source_component VARCHAR(100),
    environment VARCHAR(20) NOT NULL DEFAULT 'DEVELOPMENT',
    region VARCHAR(50) NOT NULL DEFAULT 'us-east-1',
    instance_id VARCHAR(100),
    request_id UUID,

    -- Event payload (JSONB for flexible querying, converted from protobuf)
    payload JSONB NOT NULL,

    -- Metadata and categorization
    metadata JSONB DEFAULT '{}',
    tags TEXT[] DEFAULT '{}',
    pii_fields TEXT[] DEFAULT '{}',
    retention_policy VARCHAR(20) NOT NULL DEFAULT 'OPERATIONAL',

    -- Raw protobuf data (for exact reconstruction)
    protobuf_data BYTEA,

    -- Audit fields
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT events_environment_check CHECK (environment IN ('DEVELOPMENT', 'STAGING', 'PRODUCTION')),
    CONSTRAINT events_retention_check CHECK (retention_policy IN ('OPERATIONAL', 'ANALYTICAL', 'AUDIT', 'TRAINING'))
);

-- ============================================================================
-- REAL-TIME ANALYTICS - OLAP Optimized
-- ============================================================================

-- Hourly event aggregations for dashboards
CREATE TABLE event_aggregations_hourly (
    aggregation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    hour_bucket TIMESTAMPTZ NOT NULL,
    tenant_id VARCHAR(50) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    source_service VARCHAR(100) NOT NULL,
    environment VARCHAR(20) NOT NULL,
    
    -- Event counts
    event_count BIGINT NOT NULL DEFAULT 0,
    error_count BIGINT NOT NULL DEFAULT 0,
    success_count BIGINT NOT NULL DEFAULT 0,
    unique_users BIGINT NOT NULL DEFAULT 0,
    unique_sessions BIGINT NOT NULL DEFAULT 0,
    
    -- Performance percentiles (pre-computed for speed)
    avg_sequence_gap DECIMAL(10,2),
    p50_processing_time_ms BIGINT,
    p95_processing_time_ms BIGINT,
    p99_processing_time_ms BIGINT,
    
    -- Resource utilization
    total_payload_size_mb DECIMAL(12,2),
    avg_payload_size_kb DECIMAL(10,2),
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    UNIQUE(hour_bucket, tenant_id, event_type, source_service, environment)
);

-- ============================================================================
-- DOMAIN-SPECIFIC ANALYTICS
-- ============================================================================

-- LLM inference analytics for AI/ML insights
CREATE TABLE llm_inference_analytics (
    analytics_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_id UUID NOT NULL REFERENCES events(event_id) ON DELETE CASCADE,
    tenant_id VARCHAR(50) NOT NULL,
    
    -- Model performance
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    prompt_tokens INTEGER NOT NULL,
    response_tokens INTEGER NOT NULL,
    total_tokens INTEGER NOT NULL,
    tokens_per_second DECIMAL(10,2),
    latency_ms BIGINT NOT NULL,
    cost_estimate_usd DECIMAL(10,4),
    
    -- Quality metrics
    confidence_score DECIMAL(5,4),
    finish_reason VARCHAR(50),
    success BOOLEAN NOT NULL,
    
    -- Context analysis
    conversation_history_length INTEGER DEFAULT 0,
    rag_context_used BOOLEAN DEFAULT false,
    tool_calling_enabled BOOLEAN DEFAULT false,
    function_calls_count INTEGER DEFAULT 0,
    
    -- Rationale extraction (for ML training)
    intent_category VARCHAR(100),
    reasoning_depth INTEGER DEFAULT 0,
    decision_factors_count INTEGER DEFAULT 0,
    alternatives_considered_count INTEGER DEFAULT 0,
    
    -- User satisfaction (when available)
    user_satisfaction VARCHAR(20),
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT llm_analytics_satisfaction_check CHECK (user_satisfaction IS NULL OR user_satisfaction IN ('VERY_LOW', 'LOW', 'MEDIUM', 'HIGH', 'VERY_HIGH'))
);

-- Tool usage analytics for effectiveness tracking
CREATE TABLE tool_usage_analytics (
    analytics_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_id UUID NOT NULL REFERENCES events(event_id) ON DELETE CASCADE,
    tenant_id VARCHAR(50) NOT NULL,
    
    -- Tool identification
    tool_name VARCHAR(100) NOT NULL,
    tool_version VARCHAR(50) NOT NULL,
    tool_category VARCHAR(50) NOT NULL,
    
    -- Execution metrics
    execution_time_ms BIGINT NOT NULL,
    success BOOLEAN NOT NULL,
    retry_count INTEGER DEFAULT 0,
    
    -- Data metrics
    input_size_bytes BIGINT,
    output_size_bytes BIGINT,
    data_quality_score DECIMAL(5,4),
    
    -- Context-specific metrics
    web_scraping_pages INTEGER,
    api_response_status INTEGER,
    cache_hit BOOLEAN DEFAULT false,
    
    -- Outcome analysis
    met_expectations BOOLEAN,
    quality_score DECIMAL(5,4),
    completeness_score DECIMAL(5,4),
    accuracy_score DECIMAL(5,4),
    
    -- Learning metrics
    lessons_learned_count INTEGER DEFAULT 0,
    improvement_suggestions_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Workflow execution tracking for DAG decision engine
CREATE TABLE workflow_executions (
    execution_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id VARCHAR(50) NOT NULL,
    workflow_id UUID NOT NULL,
    workflow_name VARCHAR(200) NOT NULL,
    workflow_version VARCHAR(50) NOT NULL,
    
    -- Execution status
    status VARCHAR(20) NOT NULL DEFAULT 'RUNNING',
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    
    -- Progress tracking
    total_steps INTEGER NOT NULL,
    completed_steps INTEGER NOT NULL DEFAULT 0,
    failed_steps INTEGER NOT NULL DEFAULT 0,
    current_step VARCHAR(200),
    
    -- Decision tracking
    decision_points_count INTEGER DEFAULT 0,
    historical_data_used BOOLEAN DEFAULT false,
    
    -- Performance
    total_execution_time_ms BIGINT,
    total_cost_estimate_usd DECIMAL(10,4),
    
    -- Context
    trigger_event_id UUID REFERENCES events(event_id),
    user_id UUID,
    session_id UUID,
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT workflow_status_check CHECK (status IN ('RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED'))
);

-- ============================================================================
-- INDEXES - Optimized for Multi-Tenant Queries
-- ============================================================================

-- Primary event indexes (tenant-aware)
CREATE INDEX CONCURRENTLY idx_events_tenant_timestamp ON events USING BTREE (tenant_id, timestamp DESC);
CREATE INDEX CONCURRENTLY idx_events_tenant_type_timestamp ON events USING BTREE (tenant_id, event_type, timestamp DESC);
CREATE INDEX CONCURRENTLY idx_events_correlation_id ON events USING BTREE (correlation_id);
CREATE INDEX CONCURRENTLY idx_events_session_tenant ON events USING BTREE (session_id, tenant_id) WHERE session_id IS NOT NULL;
CREATE INDEX CONCURRENTLY idx_events_workflow_tenant ON events USING BTREE (workflow_id, tenant_id) WHERE workflow_id IS NOT NULL;
CREATE INDEX CONCURRENTLY idx_events_user_tenant ON events USING BTREE (user_id, tenant_id) WHERE user_id IS NOT NULL;

-- JSONB indexes for flexible querying
CREATE INDEX CONCURRENTLY idx_events_payload_gin ON events USING GIN (payload);
CREATE INDEX CONCURRENTLY idx_events_metadata_gin ON events USING GIN (metadata);
CREATE INDEX CONCURRENTLY idx_events_tags_gin ON events USING GIN (tags);

-- Source service indexes
CREATE INDEX CONCURRENTLY idx_events_source_tenant_timestamp ON events USING BTREE (source_service, tenant_id, timestamp DESC);

-- Analytics table indexes
CREATE INDEX CONCURRENTLY idx_event_agg_hourly_tenant_bucket ON event_aggregations_hourly USING BTREE (tenant_id, hour_bucket DESC);
CREATE INDEX CONCURRENTLY idx_event_agg_hourly_type_tenant ON event_aggregations_hourly USING BTREE (event_type, tenant_id, hour_bucket DESC);

-- LLM analytics indexes
CREATE INDEX CONCURRENTLY idx_llm_analytics_tenant_model ON llm_inference_analytics USING BTREE (tenant_id, model_name, created_at DESC);
CREATE INDEX CONCURRENTLY idx_llm_analytics_success_tenant ON llm_inference_analytics USING BTREE (success, tenant_id, created_at DESC);

-- Tool analytics indexes
CREATE INDEX CONCURRENTLY idx_tool_analytics_tenant_tool ON tool_usage_analytics USING BTREE (tenant_id, tool_name, created_at DESC);
CREATE INDEX CONCURRENTLY idx_tool_analytics_category_tenant ON tool_usage_analytics USING BTREE (tool_category, tenant_id, created_at DESC);

-- Workflow indexes
CREATE INDEX CONCURRENTLY idx_workflow_exec_tenant_status ON workflow_executions USING BTREE (tenant_id, status, started_at DESC);
CREATE INDEX CONCURRENTLY idx_workflow_exec_workflow_tenant ON workflow_executions USING BTREE (workflow_id, tenant_id, started_at DESC);

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) - Multi-Tenant Isolation
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE events ENABLE ROW LEVEL SECURITY;
ALTER TABLE event_aggregations_hourly ENABLE ROW LEVEL SECURITY;
ALTER TABLE llm_inference_analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE tool_usage_analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE workflow_executions ENABLE ROW LEVEL SECURITY;

-- Create tenant isolation policies (will be activated when roles are created)
-- These policies ensure users can only see data for their tenant

-- Events table policy
CREATE POLICY events_tenant_isolation ON events
    FOR ALL
    USING (tenant_id = current_setting('app.current_tenant_id', true));

-- Analytics tables policies
CREATE POLICY event_agg_tenant_isolation ON event_aggregations_hourly
    FOR ALL
    USING (tenant_id = current_setting('app.current_tenant_id', true));

CREATE POLICY llm_analytics_tenant_isolation ON llm_inference_analytics
    FOR ALL
    USING (tenant_id = current_setting('app.current_tenant_id', true));

CREATE POLICY tool_analytics_tenant_isolation ON tool_usage_analytics
    FOR ALL
    USING (tenant_id = current_setting('app.current_tenant_id', true));

CREATE POLICY workflow_exec_tenant_isolation ON workflow_executions
    FOR ALL
    USING (tenant_id = current_setting('app.current_tenant_id', true));

-- ============================================================================
-- TRIGGERS AND FUNCTIONS
-- ============================================================================

-- Update timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply update triggers
CREATE TRIGGER update_event_aggregations_updated_at 
    BEFORE UPDATE ON event_aggregations_hourly 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_workflow_executions_updated_at 
    BEFORE UPDATE ON workflow_executions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- INITIAL CONFIGURATION
-- ============================================================================

-- Create default tenant for development
INSERT INTO events (event_id, event_type, correlation_id, tenant_id, source_service, payload, payload_schema)
VALUES (
    uuid_generate_v4(),
    'system.initialization.completed',
    uuid_generate_v4(),
    'default-tenant',
    'database-migration',
    '{"message": "CDC foundation initialized", "version": "001"}',
    'system-event-payload'
) ON CONFLICT DO NOTHING;

COMMIT;
