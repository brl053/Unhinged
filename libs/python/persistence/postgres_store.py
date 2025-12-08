"""
@llm-type library.persistence.backend
@llm-does PostgreSQL implementation of document store using JSONB
@llm-rule use JSONB columns for flexible document storage

PostgreSQL Document Store Implementation

Uses PostgreSQL's JSONB type to store documents as JSON objects.
This gives us the flexibility of NoSQL with the reliability of SQL.

Schema:
    CREATE TABLE documents (
        id UUID PRIMARY KEY,
        collection VARCHAR(255) NOT NULL,
        tenant VARCHAR(64) NOT NULL DEFAULT 'default',
        data JSONB NOT NULL,
        created_at TIMESTAMP NOT NULL,
        updated_at TIMESTAMP NOT NULL,
        version INT NOT NULL DEFAULT 1
    );
    CREATE INDEX idx_documents_collection ON documents(collection);
    CREATE INDEX idx_documents_tenant ON documents(tenant);
    CREATE INDEX idx_documents_data ON documents USING GIN(data);
"""

import logging
import os
from datetime import datetime
from typing import Any

try:
    import psycopg2
    from psycopg2.extras import Json, RealDictCursor
except ImportError as e:
    raise ImportError("psycopg2 is required. Install with: pip install psycopg2-binary") from e

from .document_store import Document, DocumentStore

logger = logging.getLogger(__name__)


class PostgresDocumentStore(DocumentStore):
    """
    PostgreSQL-backed document store using JSONB columns.

    This implementation stores documents as JSON in PostgreSQL's JSONB type,
    providing both flexibility and queryability.

    Multi-tenancy:
        All documents are scoped to a tenant. Default tenant is 'default'.
        Use tenant='test' for e2e tests - this data is isolated and can be
        bulk-deleted without affecting production data.
    """

    def __init__(self, connection_string: str | None = None, tenant: str = "default"):
        """
        Initialize PostgreSQL document store.

        Args:
            connection_string: PostgreSQL connection string. If None, uses
                             POSTGRES_CONNECTION_STRING environment variable
                             or default "postgresql://localhost/unhinged"
            tenant: Tenant identifier for multi-tenancy isolation.
                   Default is 'default'. Use 'test' for e2e tests.
        """
        if connection_string is None:
            connection_string = os.environ.get("POSTGRES_CONNECTION_STRING", "postgresql://localhost/unhinged")

        self.connection_string = connection_string
        self.tenant = tenant
        self._init_schema()

    def _get_connection(self):
        """Get a database connection."""
        return psycopg2.connect(self.connection_string)

    def _init_schema(self):
        """Initialize database schema if needed, with tenant column migration."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Create documents table if it doesn't exist
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    id UUID PRIMARY KEY,
                    collection VARCHAR(255) NOT NULL,
                    tenant VARCHAR(64) NOT NULL DEFAULT 'default',
                    data JSONB NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL,
                    version INT NOT NULL DEFAULT 1
                );
            """
            )

            # Migration: add tenant column if table exists without it
            cursor.execute(
                """
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'documents' AND column_name = 'tenant'
                    ) THEN
                        ALTER TABLE documents
                        ADD COLUMN tenant VARCHAR(64) NOT NULL DEFAULT 'default';
                    END IF;
                END $$;
            """
            )

            # Create indexes
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_documents_collection
                ON documents(collection);
            """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_documents_tenant
                ON documents(tenant);
            """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_documents_data
                ON documents USING GIN(data);
            """
            )

            conn.commit()
            cursor.close()
            conn.close()
            logger.info("Database schema initialized (tenant-aware)")
        except Exception as e:
            logger.error(f"Failed to initialize schema: {e}")
            raise

    def create(self, collection: str, data: dict[str, Any]) -> Document:
        """Create a new document in the current tenant."""
        doc = Document.create(collection, data)

        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO documents (id, collection, tenant, data, created_at, updated_at, version)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
                (
                    doc.id,
                    doc.collection,
                    self.tenant,
                    Json(doc.data),
                    doc.created_at,
                    doc.updated_at,
                    doc.version,
                ),
            )

            conn.commit()
            cursor.close()
            conn.close()
            logger.info(f"Created document {doc.id} in {collection} (tenant={self.tenant})")
            return doc
        except Exception as e:
            logger.error(f"Failed to create document: {e}")
            raise

    def read(self, collection: str, doc_id: str) -> Document | None:
        """Read a document by ID (scoped to current tenant)."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            cursor.execute(
                """
                SELECT * FROM documents WHERE id = %s AND collection = %s AND tenant = %s
            """,
                (doc_id, collection, self.tenant),
            )

            row = cursor.fetchone()
            cursor.close()
            conn.close()

            if row:
                return Document(
                    id=str(row["id"]),
                    collection=row["collection"],
                    data=row["data"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                    version=row["version"],
                )
            return None
        except Exception as e:
            logger.error(f"Failed to read document: {e}")
            raise

    def update(self, collection: str, doc_id: str, data: dict[str, Any]) -> Document | None:
        """Update a document (merge with existing, scoped to current tenant)."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # Get existing document
            cursor.execute(
                """
                SELECT data FROM documents WHERE id = %s AND collection = %s AND tenant = %s
            """,
                (doc_id, collection, self.tenant),
            )

            row = cursor.fetchone()
            if not row:
                cursor.close()
                conn.close()
                return None

            # Merge data
            merged_data = {**row["data"], **data}
            now = datetime.utcnow()

            # Update document
            cursor.execute(
                """
                UPDATE documents
                SET data = %s, updated_at = %s, version = version + 1
                WHERE id = %s AND collection = %s AND tenant = %s
                RETURNING *
            """,
                (Json(merged_data), now, doc_id, collection, self.tenant),
            )

            updated_row = cursor.fetchone()
            conn.commit()
            cursor.close()
            conn.close()

            return Document(
                id=str(updated_row["id"]),
                collection=updated_row["collection"],
                data=updated_row["data"],
                created_at=updated_row["created_at"],
                updated_at=updated_row["updated_at"],
                version=updated_row["version"],
            )
        except Exception as e:
            logger.error(f"Failed to update document: {e}")
            raise

    def delete(self, collection: str, doc_id: str) -> bool:
        """Delete a document (scoped to current tenant)."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                DELETE FROM documents WHERE id = %s AND collection = %s AND tenant = %s
            """,
                (doc_id, collection, self.tenant),
            )

            deleted = cursor.rowcount > 0
            conn.commit()
            cursor.close()
            conn.close()

            if deleted:
                logger.info(f"Deleted document {doc_id} from {collection}")
            return deleted  # type: ignore[no-any-return]
        except Exception as e:
            logger.error(f"Failed to delete document: {e}")
            raise

    def query(self, collection: str, filters: dict[str, Any] | None = None, limit: int = 100) -> list[Document]:
        """Query documents in a collection (scoped to current tenant)."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # Build WHERE clause with tenant scoping
            where_parts = ["collection = %s", "tenant = %s"]
            params: list[Any] = [collection, self.tenant]

            if filters:
                for key, value in filters.items():
                    where_parts.append(f"data->'{key}' = %s")
                    params.append(Json(value))

            where_clause = " AND ".join(where_parts)
            query = f"SELECT * FROM documents WHERE {where_clause} LIMIT %s"
            params.append(limit)

            cursor.execute(query, params)
            rows = cursor.fetchall()
            cursor.close()
            conn.close()

            return [
                Document(
                    id=str(row["id"]),
                    collection=row["collection"],
                    data=row["data"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                    version=row["version"],
                )
                for row in rows
            ]
        except Exception as e:
            logger.error(f"Failed to query documents: {e}")
            raise

    def list_collections(self) -> list[str]:
        """List all collections (scoped to current tenant)."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT DISTINCT collection FROM documents WHERE tenant = %s ORDER BY collection",
                (self.tenant,),
            )
            collections = [row[0] for row in cursor.fetchall()]
            cursor.close()
            conn.close()

            return collections
        except Exception as e:
            logger.error(f"Failed to list collections: {e}")
            raise

    def delete_collection(self, collection: str) -> bool:
        """Delete an entire collection (scoped to current tenant)."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "DELETE FROM documents WHERE collection = %s AND tenant = %s",
                (collection, self.tenant),
            )
            deleted = cursor.rowcount > 0
            conn.commit()
            cursor.close()
            conn.close()

            if deleted:
                logger.info(f"Deleted collection {collection} (tenant={self.tenant})")
            return deleted  # type: ignore[no-any-return]
        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")
            raise

    def delete_tenant_data(self) -> int:
        """Delete ALL data for current tenant. Used for e2e test cleanup.

        Returns:
            Number of documents deleted.
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("DELETE FROM documents WHERE tenant = %s", (self.tenant,))
            deleted_count = cursor.rowcount
            conn.commit()
            cursor.close()
            conn.close()

            logger.info(f"Deleted {deleted_count} documents for tenant={self.tenant}")
            return deleted_count  # type: ignore[no-any-return]
        except Exception as e:
            logger.error(f"Failed to delete tenant data: {e}")
            raise
