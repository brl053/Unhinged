"""
@llm-type library.persistence.vector_bridge
@llm-does bridge document store to vector DB for semantic recall

Vector Bridge
-------------

Automatic embedding of documents on write. When a document is created
in the document store, the bridge:
1. Generates embedding via sentence-transformers
2. Upserts to Weaviate with document ID as reference
3. Enables semantic recall via natural language query

This is the "recall" capability for self-querying sessions.

Usage:
    bridge = VectorBridge()
    bridge.embed_document("sessions", doc_id, {"text": "user said X"})
    results = bridge.recall("what did the user say?", collection="sessions")
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)

# Lazy-loaded dependencies
_model = None
_weaviate_client = None


def _get_model():
    """Lazy-load sentence transformer model."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer

            _model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
            logger.info("Loaded embedding model: all-MiniLM-L6-v2")
        except ImportError:
            logger.warning("sentence-transformers not available")
    return _model


def _get_weaviate():
    """Lazy-load Weaviate client."""
    global _weaviate_client
    if _weaviate_client is None:
        try:
            import weaviate

            _weaviate_client = weaviate.connect_to_local()
            logger.info("Connected to Weaviate")
        except Exception as e:
            logger.warning(f"Weaviate not available: {e}")
    return _weaviate_client


@dataclass
class RecallResult:
    """Single result from semantic recall."""

    document_id: str
    collection: str
    text: str
    score: float
    metadata: dict[str, Any]


class VectorBridge:
    """Bridge between document store and vector database.

    Embeds documents on write and enables semantic recall.
    Falls back gracefully when dependencies unavailable.
    """

    COLLECTION_PREFIX = "unhinged_"

    def __init__(self) -> None:
        self._model = None
        self._client = None

    def _ensure_model(self):
        if self._model is None:
            self._model = _get_model()
        return self._model

    def _ensure_client(self):
        if self._client is None:
            self._client = _get_weaviate()
        return self._client

    def _collection_name(self, collection: str) -> str:
        """Convert document store collection to Weaviate class name."""
        # Weaviate requires PascalCase class names
        name = collection.replace("_", " ").title().replace(" ", "")
        return f"{self.COLLECTION_PREFIX}{name}"

    def _extract_text(self, data: dict[str, Any]) -> str:
        """Extract embeddable text from document data."""
        # Priority: explicit text field, then concatenate string values
        if "text" in data:
            return str(data["text"])
        if "content" in data:
            return str(data["content"])
        if "message" in data:
            return str(data["message"])

        # Fallback: concatenate all string values
        parts = []
        for v in data.values():
            if isinstance(v, str) and len(v) < 1000:
                parts.append(v)
        return " ".join(parts)

    def embed_document(
        self,
        collection: str,
        document_id: str,
        data: dict[str, Any],
    ) -> bool:
        """Embed document and upsert to vector store.

        Returns True if successful, False otherwise (best-effort).
        """
        model = self._ensure_model()
        client = self._ensure_client()

        if model is None or client is None:
            return False

        try:
            text = self._extract_text(data)
            if not text:
                return False

            embedding = model.encode(text).tolist()
            class_name = self._collection_name(collection)

            # Ensure collection exists
            self._ensure_collection(client, class_name)

            # Upsert with document ID
            client.collections.get(class_name).data.insert(
                properties={
                    "document_id": document_id,
                    "collection": collection,
                    "text": text[:10000],  # Truncate for storage
                },
                vector=embedding,
                uuid=document_id,
            )

            logger.debug(f"Embedded document {document_id} in {class_name}")
            return True

        except Exception as e:
            logger.warning(f"Failed to embed document: {e}")
            return False

    def _ensure_collection(self, client, class_name: str) -> None:
        """Ensure Weaviate collection exists."""
        try:
            if not client.collections.exists(class_name):
                client.collections.create(
                    name=class_name,
                    properties=[
                        {"name": "document_id", "data_type": ["text"]},
                        {"name": "collection", "data_type": ["text"]},
                        {"name": "text", "data_type": ["text"]},
                    ],
                )
        except Exception:
            pass  # Collection may already exist

    def recall(
        self,
        query: str,
        collection: str | None = None,
        limit: int = 5,
        threshold: float = 0.5,
    ) -> list[RecallResult]:
        """Semantic recall via natural language query.

        Args:
            query: Natural language query
            collection: Optional filter to specific document collection
            limit: Max results to return
            threshold: Minimum similarity score (0-1)

        Returns:
            List of RecallResult ordered by relevance
        """
        model = self._ensure_model()
        client = self._ensure_client()

        if model is None or client is None:
            return []

        try:
            query_embedding = model.encode(query).tolist()

            results = []

            # Search across all unhinged collections or specific one
            if collection:
                collections_to_search = [self._collection_name(collection)]
            else:
                # Get all unhinged_ prefixed collections
                all_collections = client.collections.list_all()
                collections_to_search = [c for c in all_collections if c.startswith(self.COLLECTION_PREFIX)]

            for class_name in collections_to_search:
                try:
                    coll = client.collections.get(class_name)
                    response = coll.query.near_vector(
                        near_vector=query_embedding,
                        limit=limit,
                        return_metadata=["distance"],
                    )

                    for obj in response.objects:
                        # Weaviate returns distance, convert to similarity
                        distance = obj.metadata.distance or 0
                        score = 1.0 - distance

                        if score >= threshold:
                            results.append(
                                RecallResult(
                                    document_id=obj.properties.get("document_id", ""),
                                    collection=obj.properties.get("collection", ""),
                                    text=obj.properties.get("text", ""),
                                    score=score,
                                    metadata={},
                                )
                            )
                except Exception as e:
                    logger.debug(f"Search failed for {class_name}: {e}")
                    continue

            # Sort by score descending
            results.sort(key=lambda r: r.score, reverse=True)
            return results[:limit]

        except Exception as e:
            logger.warning(f"Recall failed: {e}")
            return []
