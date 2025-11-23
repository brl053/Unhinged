"""
@llm-type test.persistence.event_store
@llm-does unit tests for event_store helpers

Tests the thin convenience layer around the generic DocumentStore used
for persisting events. These tests avoid touching a real PostgreSQL
instance by patching the store accessor.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from libs.python.persistence import document_store, event_store


@dataclass
class _FakeDocument:
    data: dict[str, Any]


class _FakeStore(document_store.DocumentStore):
    def __init__(self) -> None:
        self.created: list[dict[str, Any]] = []
        self.collections_deleted: list[str] = []
        self._query_results: list[_FakeDocument] = []

    def create(self, collection: str, data: dict[str, Any]):  # type: ignore[override]
        self.created.append({"collection": collection, "data": data})
        return _FakeDocument(data=data)

    def read(self, collection: str, doc_id: str):  # type: ignore[override]
        return None

    def update(self, collection: str, doc_id: str, data: dict[str, Any]):  # type: ignore[override]
        return None

    def delete(self, collection: str, doc_id: str) -> bool:  # type: ignore[override]
        return False

    def query(self, collection: str, filters: dict[str, Any] | None = None, limit: int = 100):  # type: ignore[override]
        return list(self._query_results)[:limit]

    def list_collections(self) -> list[str]:  # type: ignore[override]
        return []

    def delete_collection(self, collection: str) -> bool:  # type: ignore[override]
        self.collections_deleted.append(collection)
        return True


def test_persist_event_uses_events_collection(monkeypatch):
    store = _FakeStore()
    monkeypatch.setattr(event_store, "_get_store", lambda: store)

    event_store.persist_event("svc", "evt", {"k": "v"}, level="ERROR", session_id="s1")

    assert len(store.created) == 1
    created = store.created[0]
    assert created["collection"] == event_store.EVENTS_COLLECTION
    data = created["data"]
    assert data["service_id"] == "svc"
    assert data["event_type"] == "evt"
    assert data["session_id"] == "s1"
    assert data["level"] == "ERROR"
    assert data["payload"] == {"k": "v"}
    assert "timestamp" in data


def test_dump_all_events_returns_document_data(monkeypatch):
    store = _FakeStore()
    store._query_results = [
        _FakeDocument(data={"service_id": "a"}),
        _FakeDocument(data={"service_id": "b"}),
    ]
    monkeypatch.setattr(event_store, "_get_store", lambda: store)

    events = event_store.dump_all_events(limit=10)
    assert events == [{"service_id": "a"}, {"service_id": "b"}]


def test_clear_all_events_deletes_events_collection(monkeypatch):
    store = _FakeStore()
    monkeypatch.setattr(event_store, "_get_store", lambda: store)

    result = event_store.clear_all_events()

    assert result is True
    assert store.collections_deleted == [event_store.EVENTS_COLLECTION]
