#!/usr/bin/env python3
"""
Session Store - Write-Through Architecture

Simple write-through implementation with Redis cache and CRDB persistence.
Optimized for local development with high-performance hardware.

@llm-type storage.session
@llm-does write-through session storage with Redis cache and CRDB persistence
"""

import json
import logging
import time
from dataclasses import dataclass
from typing import Any

try:
    import psycopg2
    import psycopg2.pool
    import redis
    from psycopg2.extras import RealDictCursor
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

    crdb_host: str = "localhost"
    crdb_port: int = 26257
    crdb_database: str = "unhinged"
    crdb_user: str = "root"
    crdb_password: str | None = None

    connection_pool_size: int = 10
    connection_timeout: int = 5

class SessionStoreError(Exception):
    """Base exception for session store operations"""
    pass

class SessionStore:
    """
    Write-through session storage implementation
    
    Simple pattern:
    - write(): Redis first, then CRDB synchronously
    - read(): Redis first, CRDB on miss with cache population
    - delete(): Remove from both stores atomically
    - exists(): Check Redis, fallback to CRDB if needed
    """

    def __init__(self, config: SessionStoreConfig | None = None):
        self.config = config or SessionStoreConfig()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Connection pools
        self.redis_client = None
        self.crdb_pool = None

        # Initialize connections
        self._initialize_connections()
        self._initialize_schema()

    def _initialize_connections(self):
        """Initialize Redis and CRDB connections"""
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
            # CRDB connection pool
            self.crdb_pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=self.config.connection_pool_size,
                host=self.config.crdb_host,
                port=self.config.crdb_port,
                database=self.config.crdb_database,
                user=self.config.crdb_user,
                password=self.config.crdb_password,
                cursor_factory=RealDictCursor
            )

            # Test CRDB connection
            conn = self.crdb_pool.getconn()
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT version()")
                    version = cursor.fetchone()
                    self.logger.info(f"CRDB connected: {version['version'][:50]}...")
            finally:
                self.crdb_pool.putconn(conn)

        except Exception as e:
            self.logger.error(f"Failed to connect to CRDB: {e}")
            raise SessionStoreError(f"CRDB connection failed: {e}")

    def _initialize_schema(self):
        """Initialize CRDB schema for session storage"""
        schema_sql = """
        CREATE TABLE IF NOT EXISTS sessions (
            key VARCHAR(255) PRIMARY KEY,
            value JSONB NOT NULL,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS idx_sessions_updated_at ON sessions(updated_at);
        """

        try:
            conn = self.crdb_pool.getconn()
            try:
                with conn.cursor() as cursor:
                    cursor.execute(schema_sql)
                    conn.commit()
                    self.logger.info("CRDB schema initialized")
            finally:
                self.crdb_pool.putconn(conn)
        except Exception as e:
            self.logger.error(f"Failed to initialize CRDB schema: {e}")
            raise SessionStoreError(f"Schema initialization failed: {e}")

    def write(self, key: str, value: Any) -> bool:
        """
        Write-through operation: Redis first, then CRDB synchronously
        
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

            # Write to CRDB synchronously
            conn = self.crdb_pool.getconn()
            try:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO sessions (key, value, updated_at) 
                        VALUES (%s, %s, NOW())
                        ON CONFLICT (key) 
                        DO UPDATE SET value = EXCLUDED.value, updated_at = NOW()
                    """, (key, json_value))
                    conn.commit()

                    self.logger.debug(f"Write-through completed for key: {key}")
                    return True

            except Exception as e:
                # If CRDB write fails, remove from Redis to maintain consistency
                self.redis_client.delete(key)
                self.logger.error(f"CRDB write failed for key {key}, removed from Redis: {e}")
                return False
            finally:
                self.crdb_pool.putconn(conn)

        except Exception as e:
            self.logger.error(f"Write operation failed for key {key}: {e}")
            return False

    def read(self, key: str) -> Any | None:
        """
        Read operation: Redis first, CRDB on miss with cache population
        
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

            # Cache miss - read from CRDB
            conn = self.crdb_pool.getconn()
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT value FROM sessions WHERE key = %s", (key,))
                    result = cursor.fetchone()

                    if result is None:
                        self.logger.debug(f"Key not found in CRDB: {key}")
                        return None

                    # Populate Redis cache atomically
                    json_value = result['value']
                    self.redis_client.set(key, json_value)

                    self.logger.debug(f"CRDB cache miss populated for key: {key}")
                    return json.loads(json_value)

            finally:
                self.crdb_pool.putconn(conn)

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

            # Delete from CRDB
            conn = self.crdb_pool.getconn()
            try:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM sessions WHERE key = %s", (key,))
                    crdb_deleted = cursor.rowcount > 0
                    conn.commit()

                    success = redis_deleted > 0 or crdb_deleted
                    self.logger.debug(f"Delete operation for key {key}: Redis={redis_deleted}, CRDB={crdb_deleted}")
                    return success

            finally:
                self.crdb_pool.putconn(conn)

        except Exception as e:
            self.logger.error(f"Delete operation failed for key {key}: {e}")
            return False

    def exists(self, key: str) -> bool:
        """
        Check if key exists: Redis first, CRDB fallback
        
        Args:
            key: Session key
            
        Returns:
            True if key exists in either store
        """
        try:
            # Check Redis first
            if self.redis_client.exists(key):
                return True

            # Fallback to CRDB
            conn = self.crdb_pool.getconn()
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1 FROM sessions WHERE key = %s LIMIT 1", (key,))
                    return cursor.fetchone() is not None
            finally:
                self.crdb_pool.putconn(conn)

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

            # Fallback to CRDB if Redis is empty
            conn = self.crdb_pool.getconn()
            try:
                with conn.cursor() as cursor:
                    # Convert Redis pattern to SQL LIKE pattern
                    sql_pattern = pattern.replace('*', '%').replace('?', '_')
                    cursor.execute("SELECT key FROM sessions WHERE key LIKE %s", (sql_pattern,))
                    return [row['key'] for row in cursor.fetchall()]
            finally:
                self.crdb_pool.putconn(conn)

        except Exception as e:
            self.logger.error(f"List keys failed for pattern {pattern}: {e}")
            return []

    def health_check(self) -> dict[str, Any]:
        """
        Health check for both stores
        
        Returns:
            Dict with health status for Redis and CRDB
        """
        health = {
            "redis": {"status": "unknown", "latency_ms": None},
            "crdb": {"status": "unknown", "latency_ms": None}
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

        # CRDB health check
        try:
            start_time = time.time()
            conn = self.crdb_pool.getconn()
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
                health["crdb"]["status"] = "healthy"
                health["crdb"]["latency_ms"] = (time.time() - start_time) * 1000
            finally:
                self.crdb_pool.putconn(conn)
        except Exception as e:
            health["crdb"]["status"] = "unhealthy"
            health["crdb"]["error"] = str(e)

        return health

    def close(self):
        """Close all connections"""
        try:
            if self.redis_client:
                self.redis_client.close()
            if self.crdb_pool:
                self.crdb_pool.closeall()
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
