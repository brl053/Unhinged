# Persistence Platform Migration Guide

**Date**: 2025-11-12  
**Status**: Phase 1 Complete - Python Platform Created  
**Next Phase**: Integration with services

## Overview

We are migrating from a complex Kotlin-based persistence platform to a simple, Python-based document store backed by PostgreSQL.

### Why?

1. **Simplicity**: File-like document abstraction instead of complex multi-database routing
2. **Homogeneity**: 100% Python codebase (no Kotlin/Java dependencies)
3. **Localhost-first**: PostgreSQL is sufficient for single-machine deployment
4. **Maintainability**: Easier to understand and modify

## Phase 1: Python Platform Creation ✅ COMPLETE

### What Was Done

1. **Marked Kotlin platform as deprecated**
   - Added deprecation notices to `/platforms/persistence/README.md`
   - Added deprecation markers to main Kotlin files
   - Preserved code for reference during migration

2. **Created Python persistence library**
   - Location: `/libs/python/persistence/`
   - Files:
     - `__init__.py` - Public API
     - `document_store.py` - Abstract interface
     - `postgres_store.py` - PostgreSQL implementation
     - `test_document_store.py` - Unit tests (8/8 passing ✅)
     - `README.md` - Documentation

### Architecture

```
┌─────────────────────────────────────────┐
│   Application Services                  │
│   (speech-to-text, chat, etc.)         │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│   Document Store Interface              │
│   (Abstract base class)                 │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│   PostgreSQL Document Store             │
│   (JSONB-backed implementation)         │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│   PostgreSQL Database                   │
│   (Already running on localhost)        │
└─────────────────────────────────────────┘
```

### Core Concepts

**Documents**: JSON-like objects with metadata
```python
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "collection": "users",
    "data": {
        "name": "Alice",
        "email": "alice@example.com",
        "status": "active"
    },
    "created_at": "2025-11-12T16:28:00Z",
    "updated_at": "2025-11-12T16:28:00Z",
    "version": 1
}
```

**Collections**: Logical groupings (like directories)
- `users` - User profiles
- `conversations` - Chat conversations
- `sessions` - User sessions
- etc.

### API

```python
from libs.python.persistence import get_document_store

store = get_document_store()

# Create
doc = store.create("users", {"name": "Alice"})

# Read
user = store.read("users", doc.id)

# Update
updated = store.update("users", doc.id, {"status": "active"})

# Delete
store.delete("users", doc.id)

# Query
active_users = store.query("users", {"status": "active"})

# List collections
collections = store.list_collections()

# Delete collection
store.delete_collection("users")
```

## Phase 2: Service Integration (Next)

### What Needs to Be Done

1. **Update service code** to use new persistence API
   - Replace gRPC calls to Kotlin platform
   - Use direct Python imports
   - Update chat service to use document store

2. **Migrate existing data** (if any)
   - Export from Kotlin platform
   - Transform to document format
   - Import using new API

3. **Update tests** to use new persistence layer

4. **Remove Kotlin platform** from deployment
   - Stop building Kotlin services
   - Remove from Docker Compose
   - Archive Kotlin code

### Services to Update

- [ ] Chat service (`services/chat-with-sessions/`)
- [ ] Session storage (`libs/python/session/`)
- [ ] Any other services using persistence

## Configuration

### Environment Variables

```bash
# PostgreSQL connection
export POSTGRES_CONNECTION_STRING="postgresql://localhost/unhinged"
```

### Database Schema

Automatically created on first use:

```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY,
    collection VARCHAR(255) NOT NULL,
    data JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    version INT NOT NULL DEFAULT 1
);

CREATE INDEX idx_documents_collection ON documents(collection);
CREATE INDEX idx_documents_data ON documents USING GIN(data);
```

## Testing

All tests pass:

```bash
cd libs/python/persistence
python3 test_document_store.py -v
# Ran 8 tests in 0.000s - OK
```

## Comparison: Old vs New

| Aspect | Kotlin Platform | Python Platform |
|--------|-----------------|-----------------|
| Language | Kotlin | Python |
| Database | 8 technologies | PostgreSQL only |
| Complexity | High | Low |
| Deployment | Docker + Java | Direct Python |
| Maintenance | Complex | Simple |
| Localhost | Overkill | Perfect fit |
| Lines of code | ~500 | ~150 |

## Migration Checklist

- [x] Create Python persistence library
- [x] Implement document store interface
- [x] Implement PostgreSQL backend
- [x] Write and pass unit tests
- [x] Document API and usage
- [x] Mark Kotlin platform as deprecated
- [ ] Update service code to use new API
- [ ] Migrate existing data
- [ ] Remove Kotlin platform from deployment
- [ ] Update documentation

## Rollback Plan

If issues arise:

1. Kotlin platform code is preserved at `/platforms/persistence/`
2. Can revert service code to use gRPC calls
3. Database schema is simple and can be backed up

## Questions?

Refer to:
- `/libs/python/persistence/README.md` - API documentation
- `/libs/python/persistence/test_document_store.py` - Usage examples
- `/libs/python/persistence/document_store.py` - Interface definition

