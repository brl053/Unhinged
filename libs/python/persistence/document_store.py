"""
@llm-type library.persistence.interface
@llm-does abstract interface for document storage
@llm-rule all document stores must implement this interface

Abstract Document Store Interface

Defines the contract for document storage backends. Think of this like
the file system API - all implementations must support the same operations.
"""

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class Document:
    """
    A document is a JSON-like object with metadata.

    Attributes:
        id: Unique identifier (UUID)
        collection: Which collection this document belongs to
        data: The actual document content (dict)
        created_at: When the document was created
        updated_at: When the document was last updated
        version: Document version for optimistic locking
    """

    id: str
    collection: str
    data: dict[str, Any]
    created_at: datetime
    updated_at: datetime
    version: int = 1

    @classmethod
    def create(cls, collection: str, data: dict[str, Any]) -> "Document":
        """Create a new document with auto-generated ID."""
        now = datetime.utcnow()
        return cls(
            id=str(uuid.uuid4()),
            collection=collection,
            data=data,
            created_at=now,
            updated_at=now,
            version=1,
        )


class DocumentStore(ABC):
    """
    Abstract base class for document storage.

    A document store is like a file system for structured data:
    - Collections are like directories
    - Documents are like files
    - Each document has an ID, content, and metadata
    """

    @abstractmethod
    def create(self, collection: str, data: dict[str, Any]) -> Document:
        """
        Create a new document in a collection.

        Args:
            collection: Collection name (e.g., "users", "posts")
            data: Document content as a dict

        Returns:
            Created Document with ID and metadata
        """
        pass

    @abstractmethod
    def read(self, collection: str, doc_id: str) -> Document | None:
        """
        Read a document by ID.

        Args:
            collection: Collection name
            doc_id: Document ID

        Returns:
            Document if found, None otherwise
        """
        pass

    @abstractmethod
    def update(self, collection: str, doc_id: str, data: dict[str, Any]) -> Document | None:
        """
        Update a document (merge with existing data).

        Args:
            collection: Collection name
            doc_id: Document ID
            data: Fields to update (merged with existing)

        Returns:
            Updated Document if found, None otherwise
        """
        pass

    @abstractmethod
    def delete(self, collection: str, doc_id: str) -> bool:
        """
        Delete a document.

        Args:
            collection: Collection name
            doc_id: Document ID

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    def query(self, collection: str, filters: dict[str, Any] | None = None, limit: int = 100) -> list[Document]:
        """
        Query documents in a collection.

        Args:
            collection: Collection name
            filters: Simple equality filters (e.g., {"status": "active"})
            limit: Maximum number of results

        Returns:
            List of matching Documents
        """
        pass

    @abstractmethod
    def list_collections(self) -> list[str]:
        """
        List all collections.

        Returns:
            List of collection names
        """
        pass

    @abstractmethod
    def delete_collection(self, collection: str) -> bool:
        """
        Delete an entire collection.

        Args:
            collection: Collection name

        Returns:
            True if deleted, False if not found
        """
        pass
