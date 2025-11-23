"""
@llm-type library.persistence.event_store
@llm-does convenience helpers for storing and retrieving event documents

Event Store Helpers
-------------------

Thin convenience layer on top of the generic DocumentStore abstraction
for working with event-like documents. All events are stored in the
"events" collection using a simple, JSON-friendly shape so that they can
be inspected via CLI tooling (e.g. ``unhinged dev logs``).

This module does not introduce a new abstraction; it just standardizes
how we use the existing document store for event persistence.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from . import DocumentStore, get_document_store

logger = logging.getLogger(__name__)

EVENTS_COLLECTION = "events"

# Soft upper bound for ``unhinged dev logs``. This is intentionally
# generous so that in normal development workflows the command behaves
# like a full dump, while still avoiding unbounded result sets.
_MAX_EVENTS_DUMP = 100_000


def _get_store() -> DocumentStore:
    """Get the default document store.

    Kept as a tiny indirection to make testing easier (can be patched).
    """

    return get_document_store()


def persist_event(
    service_id: str,
    event_type: str,
    payload: dict[str, Any] | None = None,
    *,
    level: str = "INFO",
    session_id: str | None = None,
) -> None:
    """Persist a single event document to the ``events`` collection.

    Args:
        service_id: Logical service identifier (e.g. "speech-to-text").
        event_type: Application-level event type string.
        payload: Arbitrary JSON-serializable event payload.
        level: Text log level (e.g. "INFO", "DEBUG", "WARN", "ERROR").
        session_id: Optional higher-level session identifier.

    Raises:
        Whatever ``DocumentStore.create`` may raise. Callers that treat
        persistence as best-effort (e.g. CLI flows) should wrap this in
        their own try/except.
    """

    store = _get_store()
    data: dict[str, Any] = {
        "service_id": service_id,
        "event_type": event_type,
        "session_id": session_id,
        "level": level,
        "timestamp": datetime.utcnow().isoformat(),
        "payload": payload or {},
    }

    logger.debug("Persisting event", extra={"collection": EVENTS_COLLECTION, "event_type": event_type})
    store.create(EVENTS_COLLECTION, data)


def dump_all_events(limit: int = _MAX_EVENTS_DUMP) -> list[dict[str, Any]]:
    """Return up to ``limit`` event documents as plain dicts.

    The results come directly from the underlying ``DocumentStore`` and
    are intended for human inspection and simple tooling (e.g. piping
    through grep/less).
    """

    store = _get_store()
    documents = store.query(EVENTS_COLLECTION, filters=None, limit=limit)
    return [doc.data for doc in documents]


def clear_all_events() -> bool:
    """Delete all documents in the ``events`` collection.

    Returns:
        True if any documents were deleted, False if the collection was
        already empty.
    """

    store = _get_store()
    return store.delete_collection(EVENTS_COLLECTION)


__all__ = [
    "EVENTS_COLLECTION",
    "persist_event",
    "dump_all_events",
    "clear_all_events",
]
