-- ============================================================================
-- MINIMAL CDC DATABASE SCHEMA - MVP VERTICAL SLICE
-- ============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Simple events table for MVP
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_id VARCHAR(100) NOT NULL UNIQUE,
    event_type VARCHAR(100) NOT NULL,
    timestamp_ms BIGINT NOT NULL,
    user_id VARCHAR(100) NOT NULL,
    session_id VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for real-time queries
CREATE INDEX idx_events_timestamp ON events (timestamp_ms DESC);
CREATE INDEX idx_events_user_session ON events (user_id, session_id, timestamp_ms DESC);
CREATE INDEX idx_events_type ON events (event_type, timestamp_ms DESC);

-- JSONB index for payload queries
CREATE INDEX idx_events_payload ON events USING GIN (payload);

-- Insert a test event to verify setup
INSERT INTO events (event_id, event_type, timestamp_ms, user_id, session_id, payload)
VALUES (
    'test-event-001',
    'system.initialization',
    EXTRACT(EPOCH FROM NOW()) * 1000,
    'system',
    'init-session',
    '{"message": "CDC system initialized", "version": "minimal-v1"}'::jsonb
);

-- Create a view for easy event browsing
CREATE VIEW recent_events AS
SELECT 
    event_id,
    event_type,
    TO_TIMESTAMP(timestamp_ms / 1000) as event_time,
    user_id,
    session_id,
    payload,
    created_at
FROM events
ORDER BY timestamp_ms DESC
LIMIT 100;
