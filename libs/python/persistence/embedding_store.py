"""
@llm-type library.persistence.embedding
@llm-does decorator that auto-embeds documents on write

Embedding Document Store
------------------------

Wraps any DocumentStore and automatically embeds documents to the
vector database on create/update. Uses VectorBridge for embedding.

This is the wiring that connects document persistence to semantic recall.
Embedding is best-effort - failures do not block document operations.

Transparency: Register an observer callback to see all embedding activity.
This supports max-transparency CLI mode.

Usage:
    from libs.python.persistence import get_document_store
    from libs.python.persistence.embedding_store import EmbeddingDocumentStore

    base_store = get_document_store()
    store = EmbeddingDocumentStore(base_store)

    # Register observer for transparency
    store.add_observer(lambda event: print(f"[embed] {event}"))

    # Now all creates/updates are automatically embedded
    store.create("sessions", {"text": "user said hello"})
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from .document_store import Document, DocumentStore

logger = logging.getLogger(__name__)


class EmbedEventType(Enum):
    """Type of embedding event."""

    EMBED_START = "embed_start"
    EMBED_SUCCESS = "embed_success"
    EMBED_FAILED = "embed_failed"
    EMBED_SKIPPED = "embed_skipped"


@dataclass
class EmbedEvent:
    """Event emitted during embedding operations.

    Used for CLI transparency - observers see all embedding activity.
    """

    event_type: EmbedEventType
    collection: str
    document_id: str
    timestamp: datetime
    text_preview: str = ""  # First 80 chars of embedded text
    error: str = ""

    def __str__(self) -> str:
        """Human-readable format for CLI display."""
        ts = self.timestamp.strftime("%H:%M:%S")
        if self.event_type == EmbedEventType.EMBED_START:
            return f"{ts} embedding {self.collection}/{self.document_id[:8]}..."
        elif self.event_type == EmbedEventType.EMBED_SUCCESS:
            preview = self.text_preview[:40] + "..." if len(self.text_preview) > 40 else self.text_preview
            return f"{ts} embedded {self.collection}/{self.document_id[:8]} [{preview}]"
        elif self.event_type == EmbedEventType.EMBED_FAILED:
            return f"{ts} embed failed {self.collection}/{self.document_id[:8]}: {self.error}"
        elif self.event_type == EmbedEventType.EMBED_SKIPPED:
            return f"{ts} embed skipped {self.collection}/{self.document_id[:8]} (not in whitelist)"
        return f"{ts} {self.event_type.value} {self.collection}/{self.document_id[:8]}"


# Type alias for observer callbacks
EmbedObserver = Callable[[EmbedEvent], None]


class EmbeddingDocumentStore(DocumentStore):
    """Document store wrapper that auto-embeds on write.

    Delegates all operations to the wrapped store. On create/update,
    also embeds the document to the vector database via VectorBridge.

    Embedding is best-effort and non-blocking.

    Transparency: Register observers via add_observer() to see all
    embedding activity. Used for CLI max-transparency mode.
    """

    # Collections to embed. None = all collections.
    # Can be overridden at construction.
    DEFAULT_COLLECTIONS: set[str] | None = {
        "session_contexts",
        "session_cdc",
        "execution_audit",
    }

    def __init__(
        self,
        wrapped: DocumentStore,
        collections: set[str] | None = None,
        embed_all: bool = False,
    ) -> None:
        """Initialize embedding wrapper.

        Args:
            wrapped: The underlying document store
            collections: Set of collection names to embed. If None, uses DEFAULT_COLLECTIONS.
            embed_all: If True, embed all collections (ignores collections parameter)
        """
        self._wrapped = wrapped
        self._bridge: Any = None  # VectorBridge, lazy-loaded
        self._embed_all = embed_all
        self._collections = collections if collections is not None else self.DEFAULT_COLLECTIONS
        self._observers: list[EmbedObserver] = []

    def add_observer(self, observer: EmbedObserver) -> None:
        """Register an observer for embedding events.

        Observers are called synchronously for each embedding event.
        Used for CLI transparency.
        """
        self._observers.append(observer)

    def remove_observer(self, observer: EmbedObserver) -> None:
        """Remove a registered observer."""
        if observer in self._observers:
            self._observers.remove(observer)

    def _emit(self, event: EmbedEvent) -> None:
        """Emit event to all observers."""
        from contextlib import suppress

        for observer in self._observers:
            with suppress(Exception):
                observer(event)

    def _get_bridge(self):
        """Lazy-load VectorBridge."""
        if self._bridge is None:
            try:
                from .vector_bridge import VectorBridge

                self._bridge = VectorBridge()
            except ImportError:
                logger.debug("VectorBridge not available")
        return self._bridge

    def _should_embed(self, collection: str) -> bool:
        """Check if collection should be embedded."""
        if self._embed_all:
            return True
        if self._collections is None:
            return True
        return collection in self._collections

    def _extract_text_preview(self, data: dict[str, Any]) -> str:
        """Extract text preview for transparency display."""
        for key in ("text", "content", "message"):
            if key in data and isinstance(data[key], str):
                text: str = data[key]
                return text[:80]
        return ""

    def _try_embed(self, collection: str, doc_id: str, data: dict[str, Any]) -> None:
        """Attempt to embed document. Best-effort, non-blocking."""
        now = datetime.utcnow()
        text_preview = self._extract_text_preview(data)

        if not self._should_embed(collection):
            self._emit(
                EmbedEvent(
                    event_type=EmbedEventType.EMBED_SKIPPED,
                    collection=collection,
                    document_id=doc_id,
                    timestamp=now,
                )
            )
            return

        bridge = self._get_bridge()
        if bridge is None:
            return

        self._emit(
            EmbedEvent(
                event_type=EmbedEventType.EMBED_START,
                collection=collection,
                document_id=doc_id,
                timestamp=now,
            )
        )

        try:
            bridge.embed_document(collection, doc_id, data)
            self._emit(
                EmbedEvent(
                    event_type=EmbedEventType.EMBED_SUCCESS,
                    collection=collection,
                    document_id=doc_id,
                    timestamp=now,
                    text_preview=text_preview,
                )
            )
        except Exception as e:
            logger.debug(f"Embedding failed for {collection}/{doc_id}: {e}")
            self._emit(
                EmbedEvent(
                    event_type=EmbedEventType.EMBED_FAILED,
                    collection=collection,
                    document_id=doc_id,
                    timestamp=now,
                    error=str(e),
                )
            )

    # === Delegated operations with embedding hooks ===

    def create(self, collection: str, data: dict[str, Any]) -> Document:
        """Create document and embed."""
        doc = self._wrapped.create(collection, data)
        self._try_embed(collection, doc.id, data)
        return doc

    def update(self, collection: str, doc_id: str, data: dict[str, Any]) -> Document | None:
        """Update document and re-embed."""
        doc = self._wrapped.update(collection, doc_id, data)
        if doc is not None:
            self._try_embed(collection, doc_id, doc.data)
        return doc

    # === Pure delegation (no embedding needed) ===

    def read(self, collection: str, doc_id: str) -> Document | None:
        return self._wrapped.read(collection, doc_id)

    def delete(self, collection: str, doc_id: str) -> bool:
        return self._wrapped.delete(collection, doc_id)

    def query(self, collection: str, filters: dict[str, Any] | None = None, limit: int = 100) -> list[Document]:
        return self._wrapped.query(collection, filters, limit)

    def list_collections(self) -> list[str]:
        return self._wrapped.list_collections()

    def delete_collection(self, collection: str) -> bool:
        return self._wrapped.delete_collection(collection)
