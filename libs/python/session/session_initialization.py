#!/usr/bin/env python3
"""
Session Initialization Service

Creates chat sessions before GUI startup with persistence layer verification.
Ensures session_id is available at GUI initialization time.

@llm-type service.session
@llm-does session initialization with persistence verification
@llm-rule creates sessions before GUI startup, fails fast if persistence unavailable
"""

import logging
import time
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


class SessionInitializationError(Exception):
    """Base exception for session initialization failures"""

    pass


class PersistenceLayerUnavailableError(SessionInitializationError):
    """Raised when Redis or CRDB not available"""

    pass


class SessionCreationFailedError(SessionInitializationError):
    """Raised when ChatService fails to create conversation"""

    pass


class SessionPersistenceFailedError(SessionInitializationError):
    """Raised when SessionStore write fails"""

    pass


class SessionInitializationService:
    """Initialize sessions with persistence layer verification"""

    def __init__(self, timeout: int = 30):
        """
        Initialize session service.

        Args:
            timeout: Max seconds to wait for persistence layer
        """
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)

    def create_session(self, session_name: str | None = None) -> str:
        """
        Create a new session with persistence verification.

        Args:
            session_name: Optional session name (default: timestamp-based)

        Returns:
            session_id: UUID of created session

        Raises:
            SessionInitializationError: If persistence layer unavailable
                or session creation fails
        """
        try:
            # Verify persistence layer is live
            self._verify_persistence_layer()

            # Create conversation via ChatService
            session_id = self._create_conversation(session_name)

            # Persist session to SessionStore
            self._persist_session(session_id, {"title": session_name or "Chat Session"})

            self.logger.info(f"Session created and persisted: {session_id}")
            return session_id

        except SessionInitializationError:
            raise
        except Exception as e:
            self.logger.error(f"Session initialization failed: {e}")
            raise SessionInitializationError(f"Session initialization failed: {e}") from e

    def _verify_persistence_layer(self) -> None:
        """
        Verify Redis and CRDB are available.

        Raises:
            PersistenceLayerUnavailableError: If persistence layer unavailable
        """
        try:
            import redis  # type: ignore

            # Test Redis connection
            redis_client = redis.Redis(
                host="localhost",
                port=6379,
                socket_connect_timeout=self.timeout,
                socket_timeout=self.timeout,
            )
            redis_client.ping()
            self.logger.debug("Redis connection verified")

        except Exception as e:
            self.logger.error(f"Redis verification failed: {e}")
            raise PersistenceLayerUnavailableError(f"Redis unavailable: {e}") from e

        try:
            from libs.python.persistence import get_document_store

            get_document_store()
            # Verify document store is accessible
            self.logger.debug("Document store connection verified")

        except Exception as e:
            self.logger.error(f"Document store verification failed: {e}")
            raise PersistenceLayerUnavailableError(f"Document store unavailable: {e}") from e

    def _create_conversation(self, session_name: str | None = None) -> str:
        """
        Create conversation via ChatService.

        Args:
            session_name: Optional session name

        Returns:
            conversation_id: UUID of created conversation

        Raises:
            SessionCreationFailedError: If ChatService fails
        """
        try:
            from libs.python.clients.chat_service import ChatService

            service = ChatService()
            conversation = service.create_conversation(
                metadata={"title": session_name or f"Session {datetime.now().isoformat()}"}
            )

            if not conversation or not conversation.conversation_id:
                raise SessionCreationFailedError("ChatService returned invalid conversation")

            self.logger.info(f"Conversation created: {conversation.conversation_id}")
            return conversation.conversation_id

        except SessionCreationFailedError:
            raise
        except Exception as e:
            self.logger.error(f"Conversation creation failed: {e}")
            raise SessionCreationFailedError(f"Failed to create conversation: {e}") from e

    def _persist_session(self, session_id: str, metadata: dict[str, Any]) -> None:
        """
        Persist session to SessionStore.

        Args:
            session_id: Session ID to persist
            metadata: Session metadata

        Raises:
            SessionPersistenceFailedError: If SessionStore write fails
        """
        try:
            from libs.python.session.session_store import SessionStore

            store = SessionStore()
            session_key = f"session:{session_id}:metadata"
            session_data = {
                "conversation_id": session_id,
                "created_at": time.time(),
                "status": "active",
                **metadata,
            }

            if not store.write(session_key, session_data):
                raise SessionPersistenceFailedError("SessionStore write returned False")

            self.logger.info(f"Session persisted: {session_key}")

        except SessionPersistenceFailedError:
            raise
        except Exception as e:
            self.logger.error(f"Session persistence failed: {e}")
            raise SessionPersistenceFailedError(f"Failed to persist session: {e}") from e
