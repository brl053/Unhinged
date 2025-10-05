-- ============================================================================
-- Bookkeeping Entities Schema - Identity and Access Management
-- ============================================================================
-- 
-- @file V002__create_bookkeeping_entities.sql
-- @version 1.0.0
-- @author Unhinged Team
-- @date 2025-01-04
-- @description Core identity, team, and namespace management tables
-- 
-- This migration creates the foundational relational entities for:
-- - User identity and authentication
-- - Team organization and multi-tenancy
-- - Namespace isolation for environments
-- - Audit logging for compliance
-- - Permission management through team membership
-- 
-- Design Principles:
-- - UUID primary keys for all entities
-- - Proper foreign key constraints for referential integrity
-- - Optimized indexes for permission queries
-- - Multi-tenant isolation via team_id
-- - Comprehensive audit trail
-- ============================================================================

-- ============================================================================
-- Core Identity Management
-- ============================================================================

-- Users table for authentication and identity
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    auth_provider VARCHAR(50) NOT NULL, -- 'google', 'github', 'email', 'microsoft'
    auth_provider_id VARCHAR(255), -- External provider's user ID
    avatar_url TEXT,
    
    -- Account status and metadata
    is_active BOOLEAN NOT NULL DEFAULT true,
    is_verified BOOLEAN NOT NULL DEFAULT false,
    last_login_at TIMESTAMPTZ,
    preferences JSONB DEFAULT '{}',
    
    -- Audit timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_email CHECK (email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT valid_auth_provider CHECK (auth_provider IN ('google', 'github', 'email', 'microsoft', 'apple'))
);

-- Indexes for user queries
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_auth_provider ON users(auth_provider, auth_provider_id);
CREATE INDEX idx_users_active ON users(is_active) WHERE is_active = true;
CREATE INDEX idx_users_last_login ON users(last_login_at DESC) WHERE last_login_at IS NOT NULL;

-- ============================================================================
-- Team Organization and Multi-Tenancy
-- ============================================================================

-- Teams table for organization and billing
CREATE TABLE teams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    namespace VARCHAR(100) UNIQUE NOT NULL, -- URL-safe identifier: 'acme-corp'
    description TEXT,
    avatar_url TEXT,
    
    -- Subscription and billing
    subscription_tier VARCHAR(50) NOT NULL DEFAULT 'free',
    subscription_status VARCHAR(50) NOT NULL DEFAULT 'active',
    billing_email VARCHAR(255),
    
    -- Team settings
    settings JSONB DEFAULT '{}',
    
    -- Audit timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_namespace CHECK (namespace ~ '^[a-z0-9][a-z0-9-]*[a-z0-9]$'),
    CONSTRAINT valid_subscription_tier CHECK (subscription_tier IN ('free', 'pro', 'enterprise')),
    CONSTRAINT valid_subscription_status CHECK (subscription_status IN ('active', 'cancelled', 'past_due', 'suspended'))
);

-- Indexes for team queries
CREATE INDEX idx_teams_namespace ON teams(namespace);
CREATE INDEX idx_teams_subscription ON teams(subscription_tier, subscription_status);
CREATE INDEX idx_teams_created ON teams(created_at DESC);

-- ============================================================================
-- Team Membership and Permissions
-- ============================================================================

-- Team membership with role-based access control
CREATE TABLE team_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Role-based permissions
    role VARCHAR(50) NOT NULL DEFAULT 'member',
    permissions JSONB DEFAULT '[]', -- Additional granular permissions
    
    -- Invitation tracking
    invited_by UUID REFERENCES users(id),
    invitation_token VARCHAR(255) UNIQUE,
    invitation_expires_at TIMESTAMPTZ,
    
    -- Membership status
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    joined_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    left_at TIMESTAMPTZ,
    
    -- Audit timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(team_id, user_id),
    CONSTRAINT valid_role CHECK (role IN ('owner', 'admin', 'member', 'viewer', 'guest')),
    CONSTRAINT valid_status CHECK (status IN ('active', 'inactive', 'pending', 'suspended'))
);

-- Indexes for permission queries (critical for performance)
CREATE INDEX idx_team_members_user ON team_members(user_id) WHERE status = 'active';
CREATE INDEX idx_team_members_team ON team_members(team_id) WHERE status = 'active';
CREATE INDEX idx_team_members_role ON team_members(team_id, role) WHERE status = 'active';
CREATE INDEX idx_team_members_invitation ON team_members(invitation_token) WHERE invitation_token IS NOT NULL;

-- ============================================================================
-- Namespace Management for Environment Isolation
-- ============================================================================

-- Namespaces for environment separation (dev, staging, prod)
CREATE TABLE namespaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL, -- 'production', 'staging', 'development'
    description TEXT,
    
    -- Environment configuration
    environment_type VARCHAR(50) NOT NULL DEFAULT 'development',
    is_default BOOLEAN NOT NULL DEFAULT false,
    settings JSONB DEFAULT '{}',
    
    -- Resource limits
    max_documents INTEGER DEFAULT 10000,
    max_storage_mb INTEGER DEFAULT 1000,
    
    -- Audit timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(team_id, name),
    CONSTRAINT valid_environment_type CHECK (environment_type IN ('development', 'staging', 'production', 'testing')),
    CONSTRAINT valid_name CHECK (name ~ '^[a-z0-9][a-z0-9-]*[a-z0-9]$')
);

-- Indexes for namespace queries
CREATE INDEX idx_namespaces_team ON namespaces(team_id);
CREATE INDEX idx_namespaces_default ON namespaces(team_id, is_default) WHERE is_default = true;
CREATE INDEX idx_namespaces_environment ON namespaces(environment_type);

-- Ensure only one default namespace per team
CREATE UNIQUE INDEX idx_namespaces_team_default ON namespaces(team_id) WHERE is_default = true;

-- ============================================================================
-- Comprehensive Audit Logging
-- ============================================================================

-- Audit logs for compliance and security monitoring
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Context identification
    team_id UUID NOT NULL REFERENCES teams(id),
    user_id UUID REFERENCES users(id), -- NULL for system actions
    namespace_id UUID REFERENCES namespaces(id),
    session_id VARCHAR(255), -- Link to user session
    
    -- Action details
    action VARCHAR(100) NOT NULL, -- 'document.created', 'user.invited', 'team.updated'
    resource_type VARCHAR(50) NOT NULL, -- 'document', 'user', 'team', 'namespace'
    resource_id UUID NOT NULL,
    
    -- Change tracking
    old_values JSONB,
    new_values JSONB,
    metadata JSONB DEFAULT '{}',
    
    -- Request context
    ip_address INET,
    user_agent TEXT,
    request_id VARCHAR(255),
    
    -- Audit timestamp
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_action CHECK (action ~ '^[a-z_]+\.[a-z_]+$'),
    CONSTRAINT valid_resource_type CHECK (resource_type ~ '^[a-z_]+$')
);

-- Indexes for audit queries (time-series optimized)
CREATE INDEX idx_audit_team_created ON audit_logs(team_id, created_at DESC);
CREATE INDEX idx_audit_user_created ON audit_logs(user_id, created_at DESC) WHERE user_id IS NOT NULL;
CREATE INDEX idx_audit_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_action ON audit_logs(action, created_at DESC);
CREATE INDEX idx_audit_session ON audit_logs(session_id) WHERE session_id IS NOT NULL;

-- Partition audit_logs by month for performance (PostgreSQL 10+)
-- This can be added later as data grows

-- ============================================================================
-- Integration with DocumentStore
-- ============================================================================

-- Update document_header table to include bookkeeping references
ALTER TABLE document_header 
ADD COLUMN team_id UUID REFERENCES teams(id),
ADD COLUMN namespace_id UUID REFERENCES namespaces(id),
ADD COLUMN created_by_user_id UUID REFERENCES users(id);

-- Indexes for document permission queries
CREATE INDEX idx_document_header_team ON document_header(team_id);
CREATE INDEX idx_document_header_namespace ON document_header(namespace_id);
CREATE INDEX idx_document_header_creator ON document_header(created_by_user_id);

-- Composite index for multi-tenant document queries
CREATE INDEX idx_document_header_team_namespace_created 
ON document_header(team_id, namespace_id, created_at DESC);

-- ============================================================================
-- Row Level Security (RLS) Setup
-- ============================================================================

-- Enable RLS on all tables for multi-tenant security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE teams ENABLE ROW LEVEL SECURITY;
ALTER TABLE team_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE namespaces ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_header ENABLE ROW LEVEL SECURITY;

-- RLS policies will be added in a separate migration
-- This ensures proper multi-tenant data isolation

-- ============================================================================
-- Initial Data and Constraints
-- ============================================================================

-- Create system user for automated actions
INSERT INTO users (id, email, name, auth_provider, is_active, is_verified) 
VALUES (
    '00000000-0000-0000-0000-000000000000',
    'system@unhinged.dev',
    'System',
    'email',
    true,
    true
);

-- Create default team for system operations
INSERT INTO teams (id, name, namespace, subscription_tier) 
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'System',
    'system',
    'enterprise'
);

-- Add system user to system team as owner
INSERT INTO team_members (team_id, user_id, role, status) 
VALUES (
    '00000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000000',
    'owner',
    'active'
);

-- Create default namespace for system team
INSERT INTO namespaces (team_id, name, environment_type, is_default) 
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'system',
    'production',
    true
);

-- ============================================================================
-- Comments for Documentation
-- ============================================================================

COMMENT ON TABLE users IS 'User identity and authentication information';
COMMENT ON TABLE teams IS 'Team organization for multi-tenancy and billing';
COMMENT ON TABLE team_members IS 'Team membership with role-based access control';
COMMENT ON TABLE namespaces IS 'Environment isolation within teams';
COMMENT ON TABLE audit_logs IS 'Comprehensive audit trail for compliance';

COMMENT ON COLUMN users.auth_provider_id IS 'External authentication provider user ID';
COMMENT ON COLUMN teams.namespace IS 'URL-safe team identifier for routing';
COMMENT ON COLUMN team_members.permissions IS 'Additional granular permissions beyond role';
COMMENT ON COLUMN namespaces.is_default IS 'Default namespace for team operations';
COMMENT ON COLUMN audit_logs.metadata IS 'Additional context-specific audit information';
