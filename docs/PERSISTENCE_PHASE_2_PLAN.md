# Persistence Platform - Phase 2: Service Integration Plan

**Date**: 2025-11-12  
**Status**: Planning  
**Scope**: Integrate Python persistence platform with existing services

## Current State Analysis

### What's Already Using Persistence

1. **Session Store** (`libs/python/session/session_store.py`)
   - Currently uses: CRDB (CockroachDB) directly + Redis cache
   - Used by: Chat service with sessions
   - Pattern: Write-through (Redis → CRDB)

2. **Chat Service** (`services/chat-with-sessions/grpc_server.py`)
   - Uses: SessionStore for session management
   - Stores: Conversations, messages, session state
   - Pattern: gRPC service with embedded session management

3. **gRPC Client Factory** (`libs/python/grpc_clients/client_factory.py`)
   - Has: Persistence client code (unused)
   - Status: Dead code, can be removed

### What's NOT Using Persistence

- Speech-to-text service
- Image generation service
- Vision AI service
- Text-to-speech service
- DAG execution service

## Phase 2 Implementation Strategy

### Step 1: Migrate Session Store to Python Persistence (PRIORITY)

**File**: `libs/python/session/session_store.py`

**Current**: Uses CRDB directly + Redis cache  
**Target**: Use Python persistence platform + Redis cache

**Changes**:
```python
# Before
from psycopg2 import connect
conn = psycopg2.connect(...)

# After
from libs.python.persistence import get_document_store
store = get_document_store()
```

**Benefits**:
- Removes direct CRDB dependency
- Uses consistent document abstraction
- Easier to test and maintain
- Aligns with new architecture

**Effort**: ~30 minutes

### Step 2: Update Chat Service (DEPENDENT)

**File**: `services/chat-with-sessions/grpc_server.py`

**Current**: Uses SessionStore (which uses CRDB)  
**Target**: SessionStore now uses Python persistence

**Changes**: None needed! SessionStore API stays the same.

**Effort**: 0 minutes (automatic)

### Step 3: Clean Up gRPC Client Factory

**File**: `libs/python/grpc_clients/client_factory.py`

**Current**: Has unused persistence client code  
**Target**: Remove dead code

**Changes**:
- Remove `create_persistence_client()` method
- Remove persistence service registration
- Update imports

**Effort**: ~10 minutes

### Step 4: Update Docker Compose

**File**: `build/orchestration/docker-compose.production.yml`

**Current**: Includes persistence-platform service  
**Target**: Remove Kotlin persistence service

**Changes**:
- Remove `persistence-platform` service
- Remove port mappings (1300, 1301)
- Remove dependencies

**Effort**: ~5 minutes

### Step 5: Update Build Configuration

**Files**:
- `build/config/build-config.yml`
- `build/build.py`

**Current**: Includes Kotlin persistence platform build  
**Target**: Remove Kotlin build targets

**Changes**:
- Remove Kotlin persistence build target
- Remove Gradle build steps
- Update dependencies

**Effort**: ~10 minutes

## Implementation Order

1. ✅ **Phase 1 Complete**: Python persistence platform created
2. **Phase 2a**: Migrate session store to use Python persistence
3. **Phase 2b**: Clean up gRPC client factory
4. **Phase 2c**: Update Docker Compose
5. **Phase 2d**: Update build configuration
6. **Phase 3**: Archive Kotlin platform code

## Testing Strategy

### Unit Tests
- Session store tests with new backend
- Document store CRUD operations
- Query functionality

### Integration Tests
- Chat service with new session store
- End-to-end conversation flow
- Session persistence and recovery

### Smoke Tests
- Service startup
- Basic CRUD operations
- Error handling

## Rollback Plan

If issues arise:
1. Revert session store to use CRDB directly
2. Keep Python persistence platform for future use
3. No data loss (PostgreSQL schema is simple)

## Success Criteria

- [ ] Session store uses Python persistence platform
- [ ] All session tests pass
- [ ] Chat service works end-to-end
- [ ] No performance degradation
- [ ] Kotlin platform removed from deployment
- [ ] Build time reduced (no Gradle)

## Timeline

- **Phase 2a**: 30 minutes
- **Phase 2b**: 10 minutes
- **Phase 2c**: 5 minutes
- **Phase 2d**: 10 minutes
- **Testing**: 30 minutes
- **Total**: ~1.5 hours

## Next Steps

1. Review this plan
2. Approve Phase 2a (session store migration)
3. Execute implementation
4. Run tests
5. Verify no regressions

