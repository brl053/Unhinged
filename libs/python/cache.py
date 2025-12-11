"""
@llm-type library.cache
@llm-does LRU cache with document store persistence

LRU Cache
---------

A simple LRU (Least Recently Used) cache backed by the document store.
When the cache exceeds max_size, the least recently used entries are evicted.

Usage:
    from libs.python.cache import LRUCache
    from libs.python.persistence import PostgresDocumentStore

    store = PostgresDocumentStore(...)
    cache = LRUCache(store, namespace="session_outputs", max_size=100)

    # Set/get
    cache.set("key1", {"data": "value"})
    value = cache.get("key1")  # Moves key1 to most-recently-used

    # Persist to document store
    cache.save()

    # Load from document store (on restart)
    cache.load()
"""

from __future__ import annotations

from collections import OrderedDict
from collections.abc import Callable
from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from libs.python.persistence.document_store import DocumentStore

# Callback type for eviction notifications
EvictCallback = Callable[[str, Any], None]  # (key, value) -> None


class LRUCache:
    """LRU cache with document store persistence.

    Uses OrderedDict for O(1) access and LRU ordering.
    Persists as a single document in the store.
    """

    def __init__(
        self,
        store: DocumentStore | None = None,
        namespace: str = "cache",
        max_size: int = 100,
        on_evict: EvictCallback | None = None,
    ) -> None:
        """Initialize LRU cache.

        Args:
            store: Document store for persistence. None = in-memory only.
            namespace: Collection/document ID prefix for storage.
            max_size: Maximum number of entries before LRU eviction.
            on_evict: Optional callback called when an entry is evicted.
        """
        self._store = store
        self._namespace = namespace
        self._max_size = max_size
        self._on_evict = on_evict
        self._cache: OrderedDict[str, Any] = OrderedDict()
        self._hits = 0
        self._misses = 0

    def set_on_evict(self, callback: EvictCallback | None) -> None:
        """Set the eviction callback."""
        self._on_evict = callback

    def get(self, key: str, default: Any = None) -> Any:
        """Get value by key. Moves key to most-recently-used."""
        if key in self._cache:
            self._hits += 1
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            return self._cache[key]
        self._misses += 1
        return default

    def set(self, key: str, value: Any) -> None:
        """Set key-value. Evicts LRU entries if over max_size."""
        if key in self._cache:
            # Update existing - move to end
            self._cache.move_to_end(key)
        self._cache[key] = value

        # Evict LRU entries if over max_size
        while len(self._cache) > self._max_size:
            evicted_key, evicted_value = self._cache.popitem(last=False)
            if self._on_evict:
                self._on_evict(evicted_key, evicted_value)

    def delete(self, key: str) -> bool:
        """Delete key. Returns True if key existed."""
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    def clear(self) -> None:
        """Clear all entries."""
        self._cache.clear()

    def keys(self) -> list[str]:
        """Get all keys in LRU order (oldest first)."""
        return list(self._cache.keys())

    def size(self) -> int:
        """Current number of entries."""
        return len(self._cache)

    def stats(self) -> dict[str, Any]:
        """Cache statistics."""
        total = self._hits + self._misses
        return {
            "size": len(self._cache),
            "max_size": self._max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": self._hits / total if total > 0 else 0.0,
        }

    def to_dict(self) -> dict[str, Any]:
        """Serialize cache for embedding in another structure."""
        return {
            "entries": dict(self._cache),
            "key_order": list(self._cache.keys()),
            "max_size": self._max_size,
        }

    def from_dict(self, data: dict[str, Any]) -> None:
        """Restore cache from serialized dict."""
        entries = data.get("entries", {})
        order = data.get("key_order", list(entries.keys()))
        self._max_size = data.get("max_size", self._max_size)
        self._cache = OrderedDict()
        for key in order:
            if key in entries:
                self._cache[key] = entries[key]

    def items(self) -> list[tuple[str, Any]]:
        """Get all (key, value) pairs in LRU order (oldest first)."""
        return list(self._cache.items())

    def save(self) -> bool:
        """Persist cache to document store. Returns True on success."""
        if not self._store:
            return False

        data = {
            "namespace": self._namespace,
            "entries": dict(self._cache),  # OrderedDict → dict for JSON
            "key_order": list(self._cache.keys()),  # Preserve LRU order
            "max_size": self._max_size,
            "saved_at": datetime.utcnow().isoformat(),
            "stats": self.stats(),
        }

        # Query for existing cache doc by namespace
        existing = self._store.query("caches", {"namespace": self._namespace}, limit=1)
        if existing:
            self._store.update("caches", existing[0].id, data)
        else:
            self._store.create("caches", data)
        return True

    def load(self) -> bool:
        """Load cache from document store. Returns True if found."""
        if not self._store:
            return False

        # Query for cache doc by namespace
        docs = self._store.query("caches", {"namespace": self._namespace}, limit=1)
        doc = docs[0] if docs else None
        if not doc:
            return False

        # Restore in LRU order
        entries = doc.data.get("entries", {})
        key_order = doc.data.get("key_order", list(entries.keys()))

        self._cache = OrderedDict()
        for key in key_order:
            if key in entries:
                self._cache[key] = entries[key]

        self._max_size = doc.data.get("max_size", self._max_size)
        return True

