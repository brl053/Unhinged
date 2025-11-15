"""
@llm-type library.persistence
@llm-does document-based persistence abstraction layer for Unhinged
@llm-rule persistence must be simple, file-like interface with PostgreSQL backend

Unhinged Persistence Library - Document Store Abstraction

This library provides a simple, file-like document abstraction for persisting
data to PostgreSQL. Think of it like a file system, but for structured documents.

Core Concepts:
- Documents: JSON-like objects with an ID and metadata
- Collections: Logical groupings of documents (like directories)
- Queries: Simple filtering and searching
- No complex schema enforcement - documents are flexible

Usage:
    from libs.python.persistence import get_document_store

    store = get_document_store()

    # Create a document
    doc = store.create("users", {"name": "Alice", "email": "alice@example.com"})

    # Read a document
    user = store.read("users", doc.id)

    # Update a document
    store.update("users", doc.id, {"name": "Alice Smith"})

    # Query documents
    results = store.query("users", {"email": "alice@example.com"})

    # Delete a document
    store.delete("users", doc.id)
"""

from .document_store import DocumentStore, Document
from .postgres_store import PostgresDocumentStore

__all__ = [
    "DocumentStore",
    "Document",
    "PostgresDocumentStore",
    "get_document_store",
]

_default_store = None


def get_document_store(connection_string: str = None) -> DocumentStore:
    """
    Get the default document store instance.

    Args:
        connection_string: PostgreSQL connection string. If None, uses environment
                          variable POSTGRES_CONNECTION_STRING or default.

    Returns:
        DocumentStore instance (PostgreSQL-backed)
    """
    global _default_store

    if _default_store is None:
        _default_store = PostgresDocumentStore(connection_string)

    return _default_store
