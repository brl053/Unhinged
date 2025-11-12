"""
Document Manager

Manages document persistence and retrieval using the Python persistence platform.

@llm-type component.document-manager
@llm-does manage document CRUD operations with real persistence
"""

from typing import List, Dict, Any, Optional
import sys
from pathlib import Path

# Add libs to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "libs"))

try:
    from python.persistence import get_document_store
    PERSISTENCE_AVAILABLE = True
except ImportError:
    PERSISTENCE_AVAILABLE = False


class DocumentManager:
    """Document manager with real persistence"""

    COLLECTION = "documents"

    def __init__(self):
        """Initialize document manager"""
        self.store = None
        if PERSISTENCE_AVAILABLE:
            try:
                self.store = get_document_store()
            except Exception as e:
                print(f"Warning: Could not initialize persistence store: {e}")
                print("Documents will not be persisted.")
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """Get all documents"""
        if not self.store:
            return []

        try:
            docs = self.store.query(self.COLLECTION)
            return [self._document_to_dict(doc) for doc in docs]
        except Exception as e:
            print(f"Error fetching documents: {e}")
            return []

    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get a single document by ID"""
        if not self.store:
            return None

        try:
            doc = self.store.read(self.COLLECTION, document_id)
            return self._document_to_dict(doc) if doc else None
        except Exception as e:
            print(f"Error fetching document {document_id}: {e}")
            return None

    def create_document(self, title: str, doc_type: str, description: str = "") -> Optional[Dict[str, Any]]:
        """
        Create a new document.

        Fields at creation time:
        - title: Document title (required)
        - type: Document type (required) - e.g., "graph", "tool", "user"
        - description: Document description (optional)

        Auto-generated fields:
        - id: UUID (auto-generated)
        - created_at: Timestamp (auto-generated)
        - updated_at: Timestamp (auto-generated)
        - version: Version number (auto-generated, starts at 1)
        """
        if not self.store:
            print("Error: Persistence store not available")
            return None

        try:
            data = {
                "title": title,
                "type": doc_type,
                "description": description
            }
            doc = self.store.create(self.COLLECTION, data)
            return self._document_to_dict(doc)
        except Exception as e:
            print(f"Error creating document: {e}")
            return None

    def update_document(self, document_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Update a document"""
        if not self.store:
            return None

        try:
            # Only allow updating these fields
            allowed_fields = ["title", "description"]
            update_data = {k: v for k, v in kwargs.items() if k in allowed_fields}

            if not update_data:
                return self.get_document(document_id)

            doc = self.store.update(self.COLLECTION, document_id, update_data)
            return self._document_to_dict(doc) if doc else None
        except Exception as e:
            print(f"Error updating document {document_id}: {e}")
            return None

    def delete_document(self, document_id: str) -> bool:
        """Delete a document"""
        if not self.store:
            return False

        try:
            return self.store.delete(self.COLLECTION, document_id)
        except Exception as e:
            print(f"Error deleting document {document_id}: {e}")
            return False

    def search_documents(self, query: str) -> List[Dict[str, Any]]:
        """Search documents by title or description"""
        if not self.store:
            return []

        try:
            # Query all documents and filter in Python
            docs = self.store.query(self.COLLECTION)
            query_lower = query.lower()
            results = []

            for doc in docs:
                title = doc.data.get("title", "").lower()
                description = doc.data.get("description", "").lower()
                if query_lower in title or query_lower in description:
                    results.append(self._document_to_dict(doc))

            return results
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []

    def get_documents_by_type(self, doc_type: str) -> List[Dict[str, Any]]:
        """Get documents filtered by type"""
        if not self.store:
            return []

        try:
            docs = self.store.query(self.COLLECTION, {"type": doc_type})
            return [self._document_to_dict(doc) for doc in docs]
        except Exception as e:
            print(f"Error filtering documents by type: {e}")
            return []

    def _document_to_dict(self, doc) -> Dict[str, Any]:
        """Convert persistence Document to dict"""
        return {
            "id": doc.id,
            "title": doc.data.get("title", "Untitled"),
            "type": doc.data.get("type", "unknown"),
            "description": doc.data.get("description", ""),
            "created_at": doc.created_at.isoformat() if doc.created_at else None,
            "modified_at": doc.updated_at.isoformat() if doc.updated_at else None,
            "version": doc.version
        }

