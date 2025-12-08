"""
@llm-type test.e2e.fixtures
@llm-does pytest fixtures for e2e testing with tenant isolation

E2E Test Fixtures

Provides:
- e2e_store: Document store scoped to tenant='test'
- e2e_session: Session context with CDC capture
- e2e_cleanup: Automatic test data cleanup

Connection defaults to e2e database (port 1250).
Override with E2E_POSTGRES_CONNECTION_STRING env var.
"""

import os
from collections.abc import Generator

import pytest

# E2E database connection (different port from dev)
E2E_CONNECTION_STRING = os.environ.get(
    "E2E_POSTGRES_CONNECTION_STRING",
    "postgresql://postgres:e2e_test_password@localhost:1250/unhinged_e2e",
)


@pytest.fixture(scope="function")
def e2e_store():
    """
    Document store for e2e tests with automatic cleanup.

    Scoped to tenant='test' - completely isolated from production data.
    Cleans up all test data after each test function.
    """
    from libs.python.persistence import get_document_store
    from libs.python.persistence.postgres_store import PostgresDocumentStore

    # Get store for test tenant
    store = PostgresDocumentStore(connection_string=E2E_CONNECTION_STRING, tenant="test")

    yield store

    # Cleanup: delete all test tenant data
    store.delete_tenant_data()


@pytest.fixture(scope="function")
def e2e_session():
    """
    Session context for e2e tests.

    Provides:
    - session: SessionContext with CDC events accessible via session.cdc_feed()

    Note: This fixture does NOT require database connectivity.
    Use e2e_session_with_store if you need database access.
    """
    import uuid

    from libs.python.graph.context import SessionContext

    session = SessionContext(session_id=f"e2e-test-{uuid.uuid4().hex[:8]}")

    class E2ESession:
        def __init__(self):
            self.session = session
            self.store = None  # No store by default

    yield E2ESession()


@pytest.fixture(scope="function")
def e2e_session_with_store(e2e_store):
    """
    Session context with database store for e2e tests.

    Use this when tests need to persist/query data.
    Requires e2e database to be running.
    """
    import uuid

    from libs.python.graph.context import SessionContext

    session = SessionContext(session_id=f"e2e-test-{uuid.uuid4().hex[:8]}")

    class E2ESession:
        def __init__(self):
            self.session = session
            self.store = e2e_store

    yield E2ESession()


@pytest.fixture(scope="module")
def e2e_db_ready():
    """
    Ensure e2e database is available before running tests.

    Use this fixture when tests require database connectivity.
    Skips tests if database is not available.
    """
    try:
        import psycopg2

        conn = psycopg2.connect(E2E_CONNECTION_STRING)
        conn.close()
        return True
    except Exception as e:
        pytest.skip(f"E2E database not available: {e}")
        return False
