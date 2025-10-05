# Stage 1 Entities

## Core Entities

### 1. Session
Primary context boundary for all user interactions.

**Fields:**
- id (UUID)
- user_id (string)
- created_at (timestamp)
- updated_at (timestamp)
- metadata (jsonb)

**Purpose:**
- Context isolation
- Event grouping
- LLM context management

### 2. Event
Universal event storage for all system interactions.

**Fields:**
- id (UUID)
- event_type (string)
- trace_id (UUID)
- session_id (UUID)
- user_id (string)
- timestamp_ms (bigint)
- payload (jsonb)
- created_at (timestamp)

**Purpose:**
- System observability
- Context reconstruction
- Analytics foundation

### 3. Agent
Represents individual agents in the orchestration system.

**Fields:**
- id (UUID)
- name (string)
- type (string)
- configuration (jsonb)
- status (enum)
- session_id (UUID)
- created_at (timestamp)
- updated_at (timestamp)

**Purpose:**
- Agent lifecycle management
- Configuration persistence
- Status tracking

### 4. AgentExecution
Records of agent execution instances.

**Fields:**
- id (UUID)
- agent_id (UUID)
- session_id (UUID)
- input_data (jsonb)
- output_data (jsonb)
- status (enum)
- started_at (timestamp)
- completed_at (timestamp)
- error_message (text)

**Purpose:**
- Execution tracking
- Result persistence
- Error handling

### 5. LLMInteraction
Records of all LLM API calls and responses.

**Fields:**
- id (UUID)
- session_id (UUID)
- agent_id (UUID, nullable)
- prompt (text)
- response (text)
- model (string)
- prompt_tokens (integer)
- response_tokens (integer)
- latency_ms (integer)
- success (boolean)
- error_message (text)
- created_at (timestamp)

**Purpose:**
- LLM usage tracking
- Cost monitoring
- Performance analysis

### 6. Document
Stores documents and data retrieved by agents.

**Fields:**
- id (UUID)
- session_id (UUID)
- agent_id (UUID)
- title (string)
- content (text)
- content_type (string)
- source_url (string, nullable)
- metadata (jsonb)
- created_at (timestamp)

**Purpose:**
- Data persistence
- Context building
- Reference management

## Entity Relationships

```
Session (1) → (many) Event
Session (1) → (many) Agent
Session (1) → (many) LLMInteraction
Session (1) → (many) Document

Agent (1) → (many) AgentExecution
Agent (1) → (many) LLMInteraction
Agent (1) → (many) Document

AgentExecution (1) → (many) Event
LLMInteraction (1) → (many) Event
```

## Implementation Priority

1. **Session** - Foundation for all context
2. **Event** - Core observability system
3. **LLMInteraction** - Basic LLM functionality
4. **Agent** - Agent framework foundation
5. **AgentExecution** - Agent orchestration
6. **Document** - Data persistence

## Database Schema

```sql
-- Sessions table
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Events table
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(100) NOT NULL,
    trace_id UUID NOT NULL,
    session_id UUID NOT NULL REFERENCES sessions(id),
    user_id VARCHAR(255) NOT NULL,
    timestamp_ms BIGINT NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Agents table
CREATE TABLE agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100) NOT NULL,
    configuration JSONB DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'inactive',
    session_id UUID NOT NULL REFERENCES sessions(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Agent executions table
CREATE TABLE agent_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES agents(id),
    session_id UUID NOT NULL REFERENCES sessions(id),
    input_data JSONB NOT NULL,
    output_data JSONB,
    status VARCHAR(50) DEFAULT 'pending',
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT
);

-- LLM interactions table
CREATE TABLE llm_interactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES sessions(id),
    agent_id UUID REFERENCES agents(id),
    prompt TEXT NOT NULL,
    response TEXT,
    model VARCHAR(100) NOT NULL,
    prompt_tokens INTEGER DEFAULT 0,
    response_tokens INTEGER DEFAULT 0,
    latency_ms INTEGER DEFAULT 0,
    success BOOLEAN DEFAULT false,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Documents table
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES sessions(id),
    agent_id UUID REFERENCES agents(id),
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    content_type VARCHAR(100) DEFAULT 'text/plain',
    source_url TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_events_session_id ON events(session_id);
CREATE INDEX idx_events_timestamp ON events(timestamp_ms);
CREATE INDEX idx_events_type ON events(event_type);
CREATE INDEX idx_agents_session_id ON agents(session_id);
CREATE INDEX idx_agent_executions_session_id ON agent_executions(session_id);
CREATE INDEX idx_llm_interactions_session_id ON llm_interactions(session_id);
CREATE INDEX idx_documents_session_id ON documents(session_id);
```
