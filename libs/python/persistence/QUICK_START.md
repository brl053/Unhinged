# Persistence Library - Quick Start

## Installation

```bash
pip install psycopg2-binary
```

## Basic Usage

```python
from libs.python.persistence import get_document_store

# Get store
store = get_document_store()

# Create a document
user = store.create("users", {
    "name": "Alice",
    "email": "alice@example.com"
})
print(user.id)  # UUID

# Read a document
doc = store.read("users", user.id)
print(doc.data)  # {"name": "Alice", "email": "alice@example.com"}

# Update a document
updated = store.update("users", user.id, {"status": "active"})
print(updated.version)  # 2

# Query documents
results = store.query("users", {"status": "active"})
print(len(results))  # Number of active users

# Delete a document
store.delete("users", user.id)

# List collections
collections = store.list_collections()
print(collections)  # ["users", "posts", ...]

# Delete entire collection
store.delete_collection("users")
```

## Common Patterns

### Store User Profile

```python
store.create("users", {
    "username": "alice",
    "email": "alice@example.com",
    "created_at": "2025-11-12",
    "preferences": {
        "theme": "dark",
        "notifications": True
    }
})
```

### Store Chat Message

```python
store.create("messages", {
    "conversation_id": "conv-123",
    "sender": "alice",
    "text": "Hello!",
    "timestamp": "2025-11-12T16:28:00Z"
})
```

### Store Session

```python
store.create("sessions", {
    "user_id": "user-123",
    "token": "abc123xyz",
    "expires_at": "2025-11-13T16:28:00Z"
})
```

### Query by Field

```python
# Find all active users
active = store.query("users", {"status": "active"})

# Find all messages in a conversation
messages = store.query("messages", {"conversation_id": "conv-123"})

# Find user by email
users = store.query("users", {"email": "alice@example.com"})
```

### Update Nested Data

```python
# Update preferences
store.update("users", user_id, {
    "preferences": {
        "theme": "light",
        "notifications": False
    }
})
```

## Document Structure

Every document has:

```python
Document(
    id="550e8400-e29b-41d4-a716-446655440000",  # UUID
    collection="users",                          # Collection name
    data={...},                                  # Your data
    created_at=datetime(...),                    # Auto-set
    updated_at=datetime(...),                    # Auto-updated
    version=1                                    # Incremented on update
)
```

## Configuration

### Default Connection

Uses `POSTGRES_CONNECTION_STRING` environment variable or:
```
postgresql://localhost/unhinged
```

### Custom Connection

```python
from libs.python.persistence import PostgresDocumentStore

store = PostgresDocumentStore("postgresql://user:pass@host/db")
```

## Error Handling

```python
try:
    doc = store.read("users", "invalid-id")
    if doc is None:
        print("Document not found")
except Exception as e:
    print(f"Error: {e}")
```

## Testing

```python
from libs.python.persistence.test_document_store import MockDocumentStore

# Use mock for testing
store = MockDocumentStore()
doc = store.create("users", {"name": "Test"})
assert doc.data["name"] == "Test"
```

## Limits

- **No complex queries**: Only simple equality filters
- **No transactions**: Each operation is atomic
- **No relationships**: Documents are independent
- **No full-text search**: Use PostgreSQL directly if needed

## Performance Tips

1. **Batch operations**: Create multiple documents in a loop
2. **Limit queries**: Use `limit` parameter to avoid large result sets
3. **Index collections**: Collections are indexed automatically
4. **Archive old data**: Delete old documents to keep table size manageable

## Troubleshooting

### "No module named 'psycopg2'"
```bash
pip install psycopg2-binary
```

### "Connection refused"
Check PostgreSQL is running:
```bash
psql -U postgres -d unhinged
```

### "Table does not exist"
The table is created automatically on first use. If not:
```python
store._init_schema()
```

## Next Steps

- Read full documentation: `README.md`
- View API reference: `document_store.py`
- Run tests: `python3 test_document_store.py`
- Check examples: `test_document_store.py`

