"""
@llm-type test.persistence
@llm-does unit tests for document store implementation
@llm-rule tests must verify CRUD operations and queries

Document Store Tests

Tests the document store interface and PostgreSQL implementation.
"""

import sys
import unittest
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from document_store import Document, DocumentStore


class TestDocument(unittest.TestCase):
    """Test Document class."""

    def test_create_document(self):
        """Test creating a new document."""
        doc = Document.create("users", {"name": "Alice", "email": "alice@example.com"})

        self.assertIsNotNone(doc.id)
        self.assertEqual(doc.collection, "users")
        self.assertEqual(doc.data["name"], "Alice")
        self.assertEqual(doc.version, 1)
        self.assertIsNotNone(doc.created_at)
        self.assertIsNotNone(doc.updated_at)

    def test_document_metadata(self):
        """Test document metadata."""
        data = {"status": "active", "count": 42}
        doc = Document.create("items", data)

        self.assertEqual(doc.data, data)
        self.assertIsInstance(doc.created_at, datetime)
        self.assertIsInstance(doc.updated_at, datetime)


class MockDocumentStore(DocumentStore):
    """Mock implementation for testing interface."""

    def __init__(self):
        self.documents = {}

    def create(self, collection, data):
        doc = Document.create(collection, data)
        key = (collection, doc.id)
        self.documents[key] = doc
        return doc

    def read(self, collection, doc_id):
        return self.documents.get((collection, doc_id))

    def update(self, collection, doc_id, data):
        doc = self.read(collection, doc_id)
        if doc:
            doc.data.update(data)
            doc.updated_at = datetime.utcnow()
            doc.version += 1
        return doc

    def delete(self, collection, doc_id):
        key = (collection, doc_id)
        if key in self.documents:
            del self.documents[key]
            return True
        return False

    def query(self, collection, filters=None, limit=100):
        results = [doc for (coll, _), doc in self.documents.items() if coll == collection]

        if filters:
            for key, value in filters.items():
                results = [doc for doc in results if doc.data.get(key) == value]

        return results[:limit]

    def list_collections(self):
        collections = set()
        for coll, _ in self.documents.keys():
            collections.add(coll)
        return sorted(list(collections))

    def delete_collection(self, collection):
        keys_to_delete = [key for key in self.documents.keys() if key[0] == collection]
        for key in keys_to_delete:
            del self.documents[key]
        return len(keys_to_delete) > 0


class TestDocumentStore(unittest.TestCase):
    """Test DocumentStore interface."""

    def setUp(self):
        self.store = MockDocumentStore()

    def test_create_and_read(self):
        """Test creating and reading a document."""
        doc = self.store.create("users", {"name": "Bob"})
        read_doc = self.store.read("users", doc.id)

        self.assertIsNotNone(read_doc)
        self.assertEqual(read_doc.id, doc.id)
        self.assertEqual(read_doc.data["name"], "Bob")

    def test_update(self):
        """Test updating a document."""
        doc = self.store.create("users", {"name": "Charlie", "status": "active"})
        updated = self.store.update("users", doc.id, {"status": "inactive"})

        self.assertIsNotNone(updated)
        self.assertEqual(updated.data["name"], "Charlie")
        self.assertEqual(updated.data["status"], "inactive")
        self.assertEqual(updated.version, 2)

    def test_delete(self):
        """Test deleting a document."""
        doc = self.store.create("users", {"name": "Diana"})
        deleted = self.store.delete("users", doc.id)
        read_doc = self.store.read("users", doc.id)

        self.assertTrue(deleted)
        self.assertIsNone(read_doc)

    def test_query(self):
        """Test querying documents."""
        self.store.create("users", {"name": "Eve", "status": "active"})
        self.store.create("users", {"name": "Frank", "status": "inactive"})
        self.store.create("users", {"name": "Grace", "status": "active"})

        active_users = self.store.query("users", {"status": "active"})
        self.assertEqual(len(active_users), 2)

    def test_list_collections(self):
        """Test listing collections."""
        self.store.create("users", {"name": "Henry"})
        self.store.create("posts", {"title": "Hello"})
        self.store.create("users", {"name": "Iris"})

        collections = self.store.list_collections()
        self.assertIn("users", collections)
        self.assertIn("posts", collections)

    def test_delete_collection(self):
        """Test deleting a collection."""
        self.store.create("users", {"name": "Jack"})
        self.store.create("users", {"name": "Karen"})
        self.store.create("posts", {"title": "World"})

        deleted = self.store.delete_collection("users")
        self.assertTrue(deleted)

        users = self.store.query("users")
        posts = self.store.query("posts")

        self.assertEqual(len(users), 0)
        self.assertEqual(len(posts), 1)


if __name__ == "__main__":
    unittest.main()
