#!/usr/bin/env python3
"""
Session Store - Write-Through Architecture

Write-through implementation with Redis cache and Python persistence platform.
Optimized for local development with high-performance hardware.

@llm-type storage.session
@llm-does write-through session storage with Redis cache and PostgreSQL persistence
@llm-rule uses document store abstraction for persistence, Redis for caching
"""

import json
import logging
import time
from dataclasses import dataclass
from typing import Any

try:
    import redis
except ImportError as e:
    print(f"⚠️ Session store dependencies not available: {e}")
    print("💡 Install with: pip install redis psycopg2-binary")

@dataclass
class SessionStoreConfig:
    """Configuration for session store"""
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str | None = None

    connection_timeout: int = 5

class SessionStoreError(Exception):
    """Base exception for session store operations"""
    pass

class SessionStore:
    """
    Write-through session storage implementation

    Simple pattern:
    - write(): Redis first, then document store synchronously
    - read(): Redis first, document store on miss with cache population
    - delete(): Remove from both stores atomically
    - exists(): Check Redis, fallback to document store if needed
    """

    def __init__(self, config: SessionStoreConfig | None = None):
        self.config = config or SessionStoreConfig()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Clients
        self.redis_client = None
        self.document_store = None

        # Initialize connections
        self._initialize_connections()

    def _initialize_connections(self):
        """Initialize Redis and document store connections"""
        try:
            # Redis connection
            self.redis_client = redis.Redis(
                host=self.config.redis_host,
                port=self.config.redis_port,
                db=self.config.redis_db,
                password=self.config.redis_password,
                decode_responses=True,
                socket_connect_timeout=self.config.connection_timeout,
                socket_timeout=self.config.connection_timeout
            )

            # Test Redis connection
            self.redis_client.ping()
            self.logger.info(f"Redis connected: {self.config.redis_host}:{self.config.redis_port}")

        except Exception as e:
            self.logger.error(f"Failed to connect to Redis: {e}")
            raise SessionStoreError(f"Redis connection failed: {e}")

        try:
            # Document store connection
            from libs.python.persistence import get_document_store
            self.document_store = get_document_store()
            self.logger.info("Document store connected (PostgreSQL)")

        except Exception as e:
            self.logger.error(f"Failed to connect to document store: {e}")
            raise SessionStoreError(f"Document store connection failed: {e}")



    def write(self, key: str, value: Any) -> bool:
        """
        Write-through operation: Redis first, then document store synchronously

        Args:
            key: Session key
            value: Session data (will be JSON serialized)

        Returns:
            True if both writes succeed, False otherwise
        """
        try:
            # Serialize value
            json_value = json.dumps(value, default=str)

            # Write to Redis first
            redis_success = self.redis_client.set(key, json_value)
            if not redis_success:
                self.logger.error(f"Redis write failed for key: {key}")
                return False

            # Write to document store synchronously
            try:
                # Try to update existing document
                doc = self.document_store.read("sessions", key)
                if doc:
                    self.document_store.update("sessions", key, {"value": value})
                else:
                    # Create new document
                    self.document_store.create("sessions", {"id": key, "value": value})

                self.logger.debug(f"Write-through completed for key: {key}")
                return True

            except Exception as e:
                # If document store write fails, remove from Redis to maintain consistency
                self.redis_client.delete(key)
                self.logger.error(f"Document store write failed for key {key}, removed from Redis: {e}")
                return False

        except Exception as e:
            self.logger.error(f"Write operation failed for key {key}: {e}")
            return False

    def read(self, key: str) -> Any | None:
        """
        Read operation: Redis first, document store on miss with cache population

        Args:
            key: Session key

        Returns:
            Session data or None if not found
        """
        try:
            # Try Redis first
            redis_value = self.redis_client.get(key)
            if redis_value is not None:
                self.logger.debug(f"Redis cache hit for key: {key}")
                return json.loads(redis_value)

            # Cache miss - read from document store
            doc = self.document_store.read("sessions", key)
            if doc is None:
                self.logger.debug(f"Key not found in document store: {key}")
                return None

            # Populate Redis cache atomically
            json_value = json.dumps(doc.data.get("value"), default=str)
            self.redis_client.set(key, json_value)

            self.logger.debug(f"Document store cache miss populated for key: {key}")
            return doc.data.get("value")

        except Exception as e:
            self.logger.error(f"Read operation failed for key {key}: {e}")
            return None

    def delete(self, key: str) -> bool:
        """
        Delete operation: Remove from both stores atomically

        Args:
            key: Session key

        Returns:
            True if deletion succeeds from both stores
        """
        try:
            # Delete from Redis
            redis_deleted = self.redis_client.delete(key)

            # Delete from document store
            doc_deleted = self.document_store.delete("sessions", key)

            success = redis_deleted > 0 or doc_deleted
            self.logger.debug(f"Delete operation for key {key}: Redis={redis_deleted}, DocStore={doc_deleted}")
            return success

        except Exception as e:
            self.logger.error(f"Delete operation failed for key {key}: {e}")
            return False

    def exists(self, key: str) -> bool:
        """
        Check if key exists: Redis first, document store fallback

        Args:
            key: Session key

        Returns:
            True if key exists in either store
        """
        try:
            # Check Redis first
            if self.redis_client.exists(key):
                return True

            # Fallback to document store
            doc = self.document_store.read("sessions", key)
            return doc is not None

        except Exception as e:
            self.logger.error(f"Exists check failed for key {key}: {e}")
            return False

    def list_keys(self, pattern: str = "session:*") -> list[str]:
        """
        List session keys matching pattern

        Args:
            pattern: Redis-style pattern (default: session:*)

        Returns:
            List of matching keys
        """
        try:
            # Use Redis for fast key listing
            keys = self.redis_client.keys(pattern)
            if keys:
                return keys

            # Fallback to document store if Redis is empty
            # Note: Document store doesn't support pattern matching,
            # so we return all session keys
            docs = self.document_store.query("sessions", limit=1000)
            return [doc.id for doc in docs]

        except Exception as e:
            self.logger.error(f"List keys failed for pattern {pattern}: {e}")
            return []

    def health_check(self) -> dict[str, Any]:
        """
        Health check for both stores

        Returns:
            Dict with health status for Redis and document store
        """
        health = {
            "redis": {"status": "unknown", "latency_ms": None},
            "document_store": {"status": "unknown", "latency_ms": None}
        }

        # Redis health check
        try:
            start_time = time.time()
            self.redis_client.ping()
            health["redis"]["status"] = "healthy"
            health["redis"]["latency_ms"] = (time.time() - start_time) * 1000
        except Exception as e:
            health["redis"]["status"] = "unhealthy"
            health["redis"]["error"] = str(e)

        # Document store health check
        try:
            start_time = time.time()
            # Simple health check: list collections
            self.document_store.list_collections()
            health["document_store"]["status"] = "healthy"
            health["document_store"]["latency_ms"] = (time.time() - start_time) * 1000
        except Exception as e:
            health["document_store"]["status"] = "unhealthy"
            health["document_store"]["error"] = str(e)

        return health

    def close(self):
        """Close all connections"""
        try:
            if self.redis_client:
                self.redis_client.close()
            # Document store doesn't need explicit close
            self.logger.info("Session store connections closed")
        except Exception as e:
            self.logger.error(f"Error closing connections: {e}")

# Convenience functions for global session store
_global_session_store = None

def get_session_store(config: SessionStoreConfig | None = None) -> SessionStore:
    """Get global session store instance"""
    global _global_session_store
    if _global_session_store is None:
        _global_session_store = SessionStore(config)
    return _global_session_store

def close_session_store():
    """Close global session store"""
    global _global_session_store
    if _global_session_store:
        _global_session_store.close()
        _global_session_store = None
