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

from typing import Any, Optional

from .document_store import Document, DocumentStore

# Try to import PostgreSQL store, but make it optional for testing
try:
    from .postgres_store import PostgresDocumentStore

    _POSTGRES_AVAILABLE = True
except ImportError:
    PostgresDocumentStore = None  # type: ignore
    _POSTGRES_AVAILABLE = False

# Vector bridge for semantic recall (optional dependency)
try:
    from .vector_bridge import RecallResult, VectorBridge

    _VECTOR_AVAILABLE = True
except ImportError:
    VectorBridge = None  # type: ignore
    RecallResult = None  # type: ignore
    _VECTOR_AVAILABLE = False

# Embedding store wrapper (optional - requires VectorBridge)
try:
    from .embedding_store import (
        EmbeddingDocumentStore,
        EmbedEvent,
        EmbedEventType,
        EmbedObserver,
    )

    _EMBEDDING_AVAILABLE = True
except ImportError:
    EmbeddingDocumentStore = None  # type: ignore
    EmbedEvent = None  # type: ignore
    EmbedEventType = None  # type: ignore
    EmbedObserver = None  # type: ignore
    _EMBEDDING_AVAILABLE = False

__all__ = [
    "DocumentStore",
    "Document",
    "PostgresDocumentStore",
    "get_document_store",
    # Vector bridge
    "VectorBridge",
    "RecallResult",
    # Embedding store + transparency
    "EmbeddingDocumentStore",
    "EmbedEvent",
    "EmbedEventType",
    "EmbedObserver",
]

_default_store: DocumentStore | None = None


def get_document_store(
    connection_string: str | None = None,
    with_embedding: bool = True,
    tenant: str = "default",
) -> DocumentStore:
    """
    Get a document store instance.

    Args:
        connection_string: PostgreSQL connection string. If None, uses environment
                          variable POSTGRES_CONNECTION_STRING or default Docker container.
        with_embedding: If True and VectorBridge is available, wrap store to auto-embed
                       documents on create/update. Default True.
        tenant: Tenant identifier for multi-tenancy isolation.
               Default is 'default'. Use 'test' for e2e tests.

    Returns:
        DocumentStore instance (PostgreSQL-backed, optionally with embedding)

    Raises:
        ImportError: If PostgreSQL dependencies are not installed

    Default connection (Docker):
        postgresql://postgres:password@localhost:1200/unhinged

    Multi-tenancy:
        All documents are scoped to the specified tenant. Tenants are isolated -
        a store for tenant='test' cannot see or modify tenant='default' data.
        Use tenant='test' for e2e tests, then call delete_tenant_data() for cleanup.
    """
    global _default_store

    # Only cache default tenant store - test tenants get fresh instances
    if tenant == "default" and _default_store is not None:
        return _default_store

    if not _POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL dependencies not available. Install with: pip install psycopg2-binary")

    # Default to Docker container if no connection string provided
    if connection_string is None:
        import os

        connection_string = os.environ.get(
            "POSTGRES_CONNECTION_STRING", "postgresql://postgres:password@localhost:1200/unhinged"
        )

    base_store = PostgresDocumentStore(connection_string, tenant=tenant)

    # Wrap with embedding if available and requested
    result_store: DocumentStore
    if with_embedding and _EMBEDDING_AVAILABLE and _VECTOR_AVAILABLE:
        result_store = EmbeddingDocumentStore(base_store)
    else:
        result_store = base_store

    # Only cache default tenant
    if tenant == "default":
        _default_store = result_store

    return result_store
