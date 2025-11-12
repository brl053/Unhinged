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
        data JSONB NOT NULL,
        created_at TIMESTAMP NOT NULL,
        updated_at TIMESTAMP NOT NULL,
        version INT NOT NULL DEFAULT 1
    );
    CREATE INDEX idx_documents_collection ON documents(collection);
    CREATE INDEX idx_documents_data ON documents USING GIN(data);
"""

import os
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

try:
    import psycopg2
    from psycopg2.extras import Json, RealDictCursor
except ImportError:
    raise ImportError("psycopg2 is required. Install with: pip install psycopg2-binary")

from .document_store import DocumentStore, Document

logger = logging.getLogger(__name__)


class PostgresDocumentStore(DocumentStore):
    """
    PostgreSQL-backed document store using JSONB columns.
    
    This implementation stores documents as JSON in PostgreSQL's JSONB type,
    providing both flexibility and queryability.
    """
    
    def __init__(self, connection_string: str = None):
        """
        Initialize PostgreSQL document store.
        
        Args:
            connection_string: PostgreSQL connection string. If None, uses
                             POSTGRES_CONNECTION_STRING environment variable
                             or default "postgresql://localhost/unhinged"
        """
        if connection_string is None:
            connection_string = os.environ.get(
                "POSTGRES_CONNECTION_STRING",
                "postgresql://localhost/unhinged"
            )
        
        self.connection_string = connection_string
        self._init_schema()
    
    def _get_connection(self):
        """Get a database connection."""
        return psycopg2.connect(self.connection_string)
    
    def _init_schema(self):
        """Initialize database schema if needed."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Create documents table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id UUID PRIMARY KEY,
                    collection VARCHAR(255) NOT NULL,
                    data JSONB NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL,
                    version INT NOT NULL DEFAULT 1
                );
            """)
            
            # Create indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_documents_collection 
                ON documents(collection);
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_documents_data 
                ON documents USING GIN(data);
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
            logger.info("Database schema initialized")
        except Exception as e:
            logger.error(f"Failed to initialize schema: {e}")
            raise
    
    def create(self, collection: str, data: Dict[str, Any]) -> Document:
        """Create a new document."""
        doc = Document.create(collection, data)
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO documents (id, collection, data, created_at, updated_at, version)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                doc.id,
                doc.collection,
                Json(doc.data),
                doc.created_at,
                doc.updated_at,
                doc.version
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            logger.info(f"Created document {doc.id} in {collection}")
            return doc
        except Exception as e:
            logger.error(f"Failed to create document: {e}")
            raise
    
    def read(self, collection: str, doc_id: str) -> Optional[Document]:
        """Read a document by ID."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT * FROM documents WHERE id = %s AND collection = %s
            """, (doc_id, collection))
            
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if row:
                return Document(
                    id=str(row['id']),
                    collection=row['collection'],
                    data=row['data'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    version=row['version']
                )
            return None
        except Exception as e:
            logger.error(f"Failed to read document: {e}")
            raise
    
    def update(self, collection: str, doc_id: str, data: Dict[str, Any]) -> Optional[Document]:
        """Update a document (merge with existing)."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get existing document
            cursor.execute("""
                SELECT data FROM documents WHERE id = %s AND collection = %s
            """, (doc_id, collection))
            
            row = cursor.fetchone()
            if not row:
                cursor.close()
                conn.close()
                return None
            
            # Merge data
            merged_data = {**row['data'], **data}
            now = datetime.utcnow()
            
            # Update document
            cursor.execute("""
                UPDATE documents 
                SET data = %s, updated_at = %s, version = version + 1
                WHERE id = %s AND collection = %s
                RETURNING *
            """, (Json(merged_data), now, doc_id, collection))
            
            updated_row = cursor.fetchone()
            conn.commit()
            cursor.close()
            conn.close()
            
            return Document(
                id=str(updated_row['id']),
                collection=updated_row['collection'],
                data=updated_row['data'],
                created_at=updated_row['created_at'],
                updated_at=updated_row['updated_at'],
                version=updated_row['version']
            )
        except Exception as e:
            logger.error(f"Failed to update document: {e}")
            raise
    
    def delete(self, collection: str, doc_id: str) -> bool:
        """Delete a document."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM documents WHERE id = %s AND collection = %s
            """, (doc_id, collection))
            
            deleted = cursor.rowcount > 0
            conn.commit()
            cursor.close()
            conn.close()
            
            if deleted:
                logger.info(f"Deleted document {doc_id} from {collection}")
            return deleted
        except Exception as e:
            logger.error(f"Failed to delete document: {e}")
            raise
    
    def query(self, collection: str, filters: Dict[str, Any] = None, limit: int = 100) -> List[Document]:
        """Query documents in a collection."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            if filters:
                # Build WHERE clause for JSONB filters
                where_parts = ["collection = %s"]
                params = [collection]
                
                for key, value in filters.items():
                    where_parts.append(f"data->'{key}' = %s")
                    params.append(Json(value))
                
                where_clause = " AND ".join(where_parts)
                query = f"SELECT * FROM documents WHERE {where_clause} LIMIT %s"
                params.append(limit)
            else:
                query = "SELECT * FROM documents WHERE collection = %s LIMIT %s"
                params = [collection, limit]
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            
            return [
                Document(
                    id=str(row['id']),
                    collection=row['collection'],
                    data=row['data'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at'],
                    version=row['version']
                )
                for row in rows
            ]
        except Exception as e:
            logger.error(f"Failed to query documents: {e}")
            raise
    
    def list_collections(self) -> List[str]:
        """List all collections."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT DISTINCT collection FROM documents ORDER BY collection")
            collections = [row[0] for row in cursor.fetchall()]
            cursor.close()
            conn.close()
            
            return collections
        except Exception as e:
            logger.error(f"Failed to list collections: {e}")
            raise
    
    def delete_collection(self, collection: str) -> bool:
        """Delete an entire collection."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM documents WHERE collection = %s", (collection,))
            deleted = cursor.rowcount > 0
            conn.commit()
            cursor.close()
            conn.close()
            
            if deleted:
                logger.info(f"Deleted collection {collection}")
            return deleted
        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")
            raise

