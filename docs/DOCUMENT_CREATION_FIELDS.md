# Document Creation Fields

## Overview

Documents are created through the `DocumentManager.create_document()` method and persisted to PostgreSQL via the Python persistence platform.

## Fields at Creation Time

When you create a document, you provide these fields:

### Required Fields

**`title`** (string)
- Document title/name
- Example: "System Architecture", "Data Processor"
- Cannot be empty

**`type`** (string)
- Document type/category
- Examples: "graph", "tool", "user", "conversation", "session"
- Used for filtering and organization
- Cannot be empty

### Optional Fields

**`description`** (string)
- Human-readable description of the document
- Example: "System architecture diagram showing all components"
- Defaults to empty string if not provided

## Auto-Generated Fields

These fields are automatically created and managed by the persistence platform:

**`id`** (UUID)
- Unique identifier for the document
- Auto-generated as UUID v4
- Example: `550e8400-e29b-41d4-a716-446655440000`

**`created_at`** (ISO 8601 timestamp)
- When the document was created
- Set to current UTC time at creation
- Example: `2025-11-12T17:30:45.123456Z`
- Never changes after creation

**`updated_at`** (ISO 8601 timestamp)
- When the document was last updated
- Set to current UTC time at creation
- Updated every time the document is modified
- Example: `2025-11-12T17:30:45.123456Z`

**`version`** (integer)
- Document version number for optimistic locking
- Starts at 1
- Incremented on every update
- Used to detect concurrent modifications

## Example Usage

```python
from control.gtk4_gui.components.document_manager import DocumentManager

manager = DocumentManager()

# Create a document
doc = manager.create_document(
    title="My Graph",
    doc_type="graph",
    description="A system architecture diagram"
)

# Result:
# {
#     "id": "550e8400-e29b-41d4-a716-446655440000",
#     "title": "My Graph",
#     "type": "graph",
#     "description": "A system architecture diagram",
#     "created_at": "2025-11-12T17:30:45.123456Z",
#     "modified_at": "2025-11-12T17:30:45.123456Z",
#     "version": 1
# }
```

## Persistence

All documents are persisted to PostgreSQL in the `documents` table:

```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY,
    collection VARCHAR(255) NOT NULL,
    data JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    version INT NOT NULL DEFAULT 1
);
```

- **collection**: Always "documents" for GUI-created documents
- **data**: JSONB containing title, type, description
- **created_at**: Timestamp of creation
- **updated_at**: Timestamp of last update
- **version**: Version number

## Updating Documents

When updating a document, only these fields can be modified:
- `title`
- `description`

The `type` field is immutable after creation.

```python
# Update a document
updated = manager.update_document(
    document_id="550e8400-e29b-41d4-a716-446655440000",
    title="Updated Title",
    description="Updated description"
)

# Result:
# {
#     "id": "550e8400-e29b-41d4-a716-446655440000",
#     "title": "Updated Title",
#     "type": "graph",  # Unchanged
#     "description": "Updated description",
#     "created_at": "2025-11-12T17:30:45.123456Z",  # Unchanged
#     "modified_at": "2025-11-12T17:31:20.654321Z",  # Updated
#     "version": 2  # Incremented
# }
```

## Querying Documents

```python
# Get all documents
all_docs = manager.get_all_documents()

# Get a specific document
doc = manager.get_document("550e8400-e29b-41d4-a716-446655440000")

# Search by title or description
results = manager.search_documents("architecture")

# Filter by type
graphs = manager.get_documents_by_type("graph")
```

## Deleting Documents

```python
# Delete a document
success = manager.delete_document("550e8400-e29b-41d4-a716-446655440000")
```

## Notes

- All timestamps are in UTC (ISO 8601 format)
- Documents are immutable except for title and description
- Type cannot be changed after creation
- Version number is used for optimistic locking (prevents concurrent update conflicts)
- All documents are stored in the "documents" collection in PostgreSQL

