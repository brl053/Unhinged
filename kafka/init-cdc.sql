-- ============================================================================
-- UNHINGED CDC DATABASE INITIALIZATION
-- ============================================================================
-- 
-- This script creates the CDC (Change Data Capture) database schema for the
-- Universal System. It includes OLTP tables for real-time operations and
-- OLAP-optimized structures for analytics and AI/ML data lakes.
--
-- Author: LLM Agent
-- Version: 1.0.0
-- Date: 2025-01-04
-- ============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "btree_gin";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ============================================================================
-- OLTP TABLES - Real-time Event Processing
-- ============================================================================

-- Main events table - optimized for high-throughput writes
CREATE TABLE events (
    event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type VARCHAR(50) NOT NULL,
    event_version VARCHAR(20) NOT NULL DEFAULT '1.0.0',
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    correlation_id UUID,
    causation_id UUID,
    session_id UUID,
    user_id UUID,
    source_service VARCHAR(100) NOT NULL,
    source_component VARCHAR(100),
    aggregate_id UUID,
    aggregate_type VARCHAR(100),
    
    -- Event data (JSONB for flexible querying)
    event_data JSONB NOT NULL,
    
    -- Context information
    environment VARCHAR(20) NOT NULL DEFAULT 'DEVELOPMENT',
    region VARCHAR(50) NOT NULL DEFAULT 'us-east-1',
    instance_id VARCHAR(100),
    request_id UUID,
    
    -- Performance metrics
    duration_ms BIGINT,
    memory_usage_mb DECIMAL(10,2),
    cpu_usage_percent DECIMAL(5,2),
    
    -- Categorization and search
    tags TEXT[],
    
    -- Error information
    error_code VARCHAR(100),
    error_message TEXT,
    stack_trace TEXT,
    recovery_action TEXT,
    
    -- Audit fields
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Event streams table - for real-time processing
CREATE TABLE event_streams (
    stream_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    stream_name VARCHAR(100) NOT NULL UNIQUE,
    event_types TEXT[] NOT NULL,
    filter_criteria JSONB,
    processing_status VARCHAR(20) NOT NULL DEFAULT 'active',
    last_processed_event_id UUID,
    last_processed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Event subscriptions - for real-time notifications
CREATE TABLE event_subscriptions (
    subscription_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    subscriber_name VARCHAR(100) NOT NULL,
    event_types TEXT[] NOT NULL,
    filter_criteria JSONB,
    webhook_url VARCHAR(500),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- OLAP TABLES - Analytics and Data Lake
-- ============================================================================

-- Event aggregations by hour - for real-time dashboards
CREATE TABLE event_aggregations_hourly (
    aggregation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    hour_bucket TIMESTAMPTZ NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    source_service VARCHAR(100) NOT NULL,
    environment VARCHAR(20) NOT NULL,
    
    -- Counts
    event_count BIGINT NOT NULL DEFAULT 0,
    error_count BIGINT NOT NULL DEFAULT 0,
    success_count BIGINT NOT NULL DEFAULT 0,
    
    -- Performance metrics
    avg_duration_ms DECIMAL(10,2),
    min_duration_ms BIGINT,
    max_duration_ms BIGINT,
    p95_duration_ms BIGINT,
    p99_duration_ms BIGINT,
    
    -- Resource usage
    avg_memory_usage_mb DECIMAL(10,2),
    max_memory_usage_mb DECIMAL(10,2),
    avg_cpu_usage_percent DECIMAL(5,2),
    max_cpu_usage_percent DECIMAL(5,2),
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    UNIQUE(hour_bucket, event_type, source_service, environment)
);

-- LLM inference analytics - specialized for AI/ML insights
CREATE TABLE llm_inference_analytics (
    analytics_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_id UUID NOT NULL REFERENCES events(event_id),
    
    -- Model information
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    
    -- Token metrics
    prompt_tokens INTEGER NOT NULL,
    response_tokens INTEGER NOT NULL,
    total_tokens INTEGER NOT NULL,
    
    -- Performance metrics
    tokens_per_second DECIMAL(10,2),
    latency_ms BIGINT NOT NULL,
    cost_estimate_usd DECIMAL(10,4),
    
    -- Quality metrics
    confidence_score DECIMAL(5,4),
    finish_reason VARCHAR(50),
    
    -- Context analysis
    conversation_history_length INTEGER,
    context_window_utilization DECIMAL(5,4),
    rag_context_used BOOLEAN DEFAULT false,
    tool_calling_enabled BOOLEAN DEFAULT false,
    
    -- Intent and rationale
    detected_intent VARCHAR(200),
    reasoning_chain TEXT[],
    decision_factors TEXT[],
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Tool usage analytics - for understanding tool effectiveness
CREATE TABLE tool_usage_analytics (
    analytics_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_id UUID NOT NULL REFERENCES events(event_id),
    
    -- Tool information
    tool_name VARCHAR(100) NOT NULL,
    tool_version VARCHAR(50) NOT NULL,
    tool_category VARCHAR(50) NOT NULL,
    
    -- Usage metrics
    execution_time_ms BIGINT NOT NULL,
    success BOOLEAN NOT NULL,
    retry_count INTEGER DEFAULT 0,
    
    -- Data metrics
    input_size_bytes BIGINT,
    output_size_bytes BIGINT,
    network_bytes_transferred BIGINT,
    
    -- Web scraping specific
    target_domain VARCHAR(200),
    robots_txt_compliant BOOLEAN,
    rate_limiting_applied BOOLEAN,
    data_extraction_success BOOLEAN,
    
    -- Rationale analysis
    tool_selection_reason TEXT,
    alternative_tools_considered TEXT[],
    risk_assessment TEXT,
    success_criteria TEXT[],
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- User interaction patterns - for UX optimization
CREATE TABLE user_interaction_patterns (
    pattern_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_id UUID NOT NULL REFERENCES events(event_id),
    
    -- Interaction details
    interaction_type VARCHAR(50) NOT NULL,
    ui_element_type VARCHAR(100),
    page_url VARCHAR(500),
    
    -- User context
    user_expertise_level VARCHAR(20),
    session_duration_ms BIGINT,
    interaction_sequence_number INTEGER,
    
    -- Intent analysis
    detected_intent VARCHAR(200),
    intent_confidence DECIMAL(5,4),
    alternative_intents TEXT[],
    
    -- Response analysis
    system_response_time_ms BIGINT,
    response_success BOOLEAN,
    user_satisfaction_inferred VARCHAR(20),
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Workflow execution tracking - for DAG decision engine
CREATE TABLE workflow_executions (
    execution_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workflow_id UUID NOT NULL,
    workflow_name VARCHAR(200) NOT NULL,
    workflow_version VARCHAR(50) NOT NULL,
    
    -- Execution status
    status VARCHAR(20) NOT NULL DEFAULT 'running',
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    
    -- Step tracking
    total_steps INTEGER NOT NULL,
    completed_steps INTEGER NOT NULL DEFAULT 0,
    failed_steps INTEGER NOT NULL DEFAULT 0,
    current_step VARCHAR(200),
    
    -- Decision tracking
    decision_points JSONB,
    historical_data_used BOOLEAN DEFAULT false,
    
    -- Performance
    total_execution_time_ms BIGINT,
    total_cost_estimate_usd DECIMAL(10,4),
    
    -- Context
    trigger_event_id UUID REFERENCES events(event_id),
    business_context JSONB,
    user_context JSONB,
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Workflow steps - detailed step execution tracking
CREATE TABLE workflow_steps (
    step_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    execution_id UUID NOT NULL REFERENCES workflow_executions(execution_id),
    event_id UUID NOT NULL REFERENCES events(event_id),
    
    -- Step details
    step_name VARCHAR(200) NOT NULL,
    step_index INTEGER NOT NULL,
    step_type VARCHAR(100) NOT NULL,
    step_status VARCHAR(20) NOT NULL,
    
    -- Decision data
    decision_point VARCHAR(200),
    available_options TEXT[],
    chosen_option VARCHAR(200),
    decision_criteria TEXT[],
    confidence_score DECIMAL(5,4),
    
    -- Performance
    execution_time_ms BIGINT,
    memory_peak_mb DECIMAL(10,2),
    
    -- Data flow
    input_data JSONB,
    output_data JSONB,
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================================
-- INDEXES - Optimized for both OLTP and OLAP workloads
-- ============================================================================

-- OLTP indexes - optimized for real-time queries
CREATE INDEX CONCURRENTLY idx_events_timestamp ON events USING BTREE (timestamp DESC);
CREATE INDEX CONCURRENTLY idx_events_type_timestamp ON events USING BTREE (event_type, timestamp DESC);
CREATE INDEX CONCURRENTLY idx_events_correlation_id ON events USING BTREE (correlation_id) WHERE correlation_id IS NOT NULL;
CREATE INDEX CONCURRENTLY idx_events_session_id ON events USING BTREE (session_id) WHERE session_id IS NOT NULL;
CREATE INDEX CONCURRENTLY idx_events_user_id ON events USING BTREE (user_id) WHERE user_id IS NOT NULL;
CREATE INDEX CONCURRENTLY idx_events_source_service ON events USING BTREE (source_service, timestamp DESC);

-- JSONB indexes for flexible querying
CREATE INDEX CONCURRENTLY idx_events_data_gin ON events USING GIN (event_data);
CREATE INDEX CONCURRENTLY idx_events_tags_gin ON events USING GIN (tags);

-- Full-text search indexes
CREATE INDEX CONCURRENTLY idx_events_error_message_trgm ON events USING GIN (error_message gin_trgm_ops) WHERE error_message IS NOT NULL;

-- OLAP indexes - optimized for analytics
CREATE INDEX CONCURRENTLY idx_event_agg_hourly_bucket ON event_aggregations_hourly USING BTREE (hour_bucket DESC);
CREATE INDEX CONCURRENTLY idx_event_agg_hourly_type_bucket ON event_aggregations_hourly USING BTREE (event_type, hour_bucket DESC);

-- Analytics table indexes
CREATE INDEX CONCURRENTLY idx_llm_analytics_model_created ON llm_inference_analytics USING BTREE (model_name, created_at DESC);
CREATE INDEX CONCURRENTLY idx_tool_analytics_tool_created ON tool_usage_analytics USING BTREE (tool_name, created_at DESC);
CREATE INDEX CONCURRENTLY idx_user_patterns_type_created ON user_interaction_patterns USING BTREE (interaction_type, created_at DESC);

-- Workflow indexes
CREATE INDEX CONCURRENTLY idx_workflow_exec_status_started ON workflow_executions USING BTREE (status, started_at DESC);
CREATE INDEX CONCURRENTLY idx_workflow_steps_exec_index ON workflow_steps USING BTREE (execution_id, step_index);

-- ============================================================================
-- TRIGGERS - Automatic data management
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
CREATE TRIGGER update_events_updated_at BEFORE UPDATE ON events FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_event_streams_updated_at BEFORE UPDATE ON event_streams FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_event_subscriptions_updated_at BEFORE UPDATE ON event_subscriptions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_workflow_executions_updated_at BEFORE UPDATE ON workflow_executions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- PARTITIONING - For high-volume event storage
-- ============================================================================

-- Partition events table by month for better performance
-- This will be implemented as the system scales

-- ============================================================================
-- INITIAL DATA
-- ============================================================================

-- Create default event stream
INSERT INTO event_streams (stream_name, event_types, filter_criteria) VALUES
('universal_stream', ARRAY['LLM_INFERENCE', 'TOOL_USAGE', 'VOICE_TRANSCRIPTION', 'TTS_SYNTHESIS', 'UI_GENERATION', 'USER_INTERACTION', 'WORKFLOW_EXECUTION', 'SYSTEM_STATE_CHANGE'], '{}');

-- Create system health subscription
INSERT INTO event_subscriptions (subscriber_name, event_types, filter_criteria) VALUES
('system_health_monitor', ARRAY['ERROR_EVENT', 'PERFORMANCE_METRIC'], '{"environment": "PRODUCTION"}');

COMMIT;
