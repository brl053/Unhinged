#!/usr/bin/env python3
"""
Chat Service

Manages chat conversations and message storage.
Direct Python implementation - no gRPC overhead.
"""

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """Chat message"""

    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class Conversation:
    """Chat conversation"""

    conversation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    messages: list[Message] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


class ChatService:
    """Chat conversation management"""

    def __init__(self):
        """Initialize chat service"""
        self.conversations: dict[str, Conversation] = {}
        logger.info("ChatService initialized")

    def create_conversation(self, metadata: dict[str, Any] | None = None) -> Conversation:
        """
        Create a new conversation.

        Args:
            metadata: Optional metadata for the conversation

        Returns:
            Conversation object with unique ID
        """
        conversation = Conversation(metadata=metadata or {})
        self.conversations[conversation.conversation_id] = conversation

        logger.info(f"Created conversation: {conversation.conversation_id}")
        return conversation

    def send_message(self, conversation_id: str, role: str, content: str) -> Message:
        """
        Add a message to a conversation.

        Args:
            conversation_id: ID of the conversation
            role: Message role ("user" or "assistant")
            content: Message content

        Returns:
            Message object

        Raises:
            ValueError: If conversation not found
        """
        if conversation_id not in self.conversations:
            raise ValueError(f"Conversation not found: {conversation_id}")

        message = Message(role=role, content=content)
        self.conversations[conversation_id].messages.append(message)

        logger.info(f"Added {role} message to conversation {conversation_id}")
        return message

    def get_conversation(self, conversation_id: str) -> Conversation | None:
        """Get conversation by ID"""
        return self.conversations.get(conversation_id)

    def get_messages(self, conversation_id: str) -> list[Message]:
        """Get all messages in a conversation"""
        conversation = self.conversations.get(conversation_id)
        return conversation.messages if conversation else []

    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation"""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            logger.info(f"Deleted conversation: {conversation_id}")
            return True
        return False
