# Unhinged Persistence Library

**Status**: Production-ready  
**Language**: Python  
**Backend**: PostgreSQL with JSONB  
**Philosophy**: Simple, file-like document abstraction

## Overview

A lightweight document store library that provides a file-like interface for persisting data to PostgreSQL. Think of it like a file system, but for structured JSON documents.

### Core Concepts

- **Documents**: JSON-like objects with an ID, content, and metadata
- **Collections**: Logical groupings of documents (like directories)
- **Queries**: Simple filtering and searching
- **Flexibility**: No rigid schema enforcement - documents are flexible

## Quick Start

### Installation

```bash
pip install psycopg2-binary
```

### Basic Usage

```python
from libs.python.persistence import get_document_store

# Get the default store
store = get_document_store()

# Create a document
user = store.create("users", {
    "name": "Alice",
    "email": "alice@example.com",
    "status": "active"
})
print(f"Created user: {user.id}")

# Read a document
retrieved = store.read("users", user.id)
print(f"User: {retrieved.data}")

# Update a document
updated = store.update("users", user.id, {
    "status": "inactive"
})
print(f"Updated user version: {updated.version}")

# Query documents
active_users = store.query("users", {"status": "active"})
print(f"Found {len(active_users)} active users")

# Delete a document
deleted = store.delete("users", user.id)
print(f"Deleted: {deleted}")

# List all collections
collections = store.list_collections()
print(f"Collections: {collections}")
```

## API Reference

### DocumentStore Interface

All document stores implement this interface:

#### `create(collection: str, data: Dict) -> Document`
Create a new document in a collection.

#### `read(collection: str, doc_id: str) -> Optional[Document]`
Read a document by ID.

#### `update(collection: str, doc_id: str, data: Dict) -> Optional[Document]`
Update a document (merges with existing data).

#### `delete(collection: str, doc_id: str) -> bool`
Delete a document.

#### `query(collection: str, filters: Dict = None, limit: int = 100) -> List[Document]`
Query documents with optional filters.

#### `list_collections() -> List[str]`
List all collections.

#### `delete_collection(collection: str) -> bool`
Delete an entire collection.

### Document Class

```python
@dataclass
class Document:
    id: str                    # UUID
    collection: str            # Collection name
    data: Dict[str, Any]      # Document content
    created_at: datetime       # Creation timestamp
    updated_at: datetime       # Last update timestamp
    version: int               # Version number (incremented on updates)
```

## Configuration

### Environment Variables

- `POSTGRES_CONNECTION_STRING`: PostgreSQL connection string
  - Default: `postgresql://localhost/unhinged`
  - Example: `postgresql://user:password@host:5432/dbname`

### Custom Connection

```python
from libs.python.persistence import PostgresDocumentStore

store = PostgresDocumentStore("postgresql://user:pass@localhost/mydb")
```

## Database Schema

The library automatically creates the required schema:

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

Run the test suite:

```bash
cd libs/python/persistence
python -m pytest test_document_store.py -v
```

Or with unittest:

```bash
python test_document_store.py
```

## Design Philosophy

### Why Document Store?

1. **Flexibility**: No rigid schema - documents can have different structures
2. **Simplicity**: File-like interface is intuitive
3. **PostgreSQL**: Reliable, battle-tested, JSONB support
4. **No Overkill**: Simpler than the Kotlin persistence platform

### Why Not CockroachDB?

For localhost development and single-machine deployment, PostgreSQL is sufficient. CockroachDB adds complexity without benefit for our use case.

### Why Not MongoDB?

We want to keep everything in Python and PostgreSQL. MongoDB would add another dependency and operational complexity.

## Limitations

- **No complex queries**: Use simple equality filters only
- **No transactions**: Each operation is atomic
- **No relationships**: Documents are independent
- **No full-text search**: Use PostgreSQL directly for advanced queries

## Future Enhancements

- [ ] Complex query support (ranges, regex, etc.)
- [ ] Transactions across multiple documents
- [ ] Full-text search integration
- [ ] Caching layer
- [ ] Replication support

## Migration from Kotlin Platform

If you're migrating from the deprecated Kotlin persistence platform:

1. Export data from Kotlin platform
2. Transform to document format
3. Use `store.create()` to import
4. Update service code to use new API

## Contributing

When adding features:

1. Update the `DocumentStore` interface first
2. Implement in `PostgresDocumentStore`
3. Add tests to `test_document_store.py`
4. Update this README

## License

MIT

