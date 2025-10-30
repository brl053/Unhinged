#!/usr/bin/env python3
"""
@llm-type service.api
@llm-does chat service with embedded session management using write-through architecture
"""

import os
import sys
import time
import uuid
from collections.abc import Iterator
from concurrent import futures
from pathlib import Path
from typing import Any

import grpc

# Add paths for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "libs" / "python"))
sys.path.insert(0, str(project_root / "generated" / "python" / "clients"))

# Health proto imports
from unhinged_proto_clients.health import health_pb2, health_pb2_grpc

# Chat proto imports
try:
    from unhinged_proto_clients import chat_pb2, chat_pb2_grpc, common_pb2
except ImportError:
    print("⚠️ Chat protobuf clients not generated yet")
    print("💡 Run: ./proto/build_chat.sh to generate protobuf clients")
    sys.exit(1)

# Session store import
try:
    from session.session_store import SessionStore, SessionStoreConfig
except ImportError as e:
    print(f"⚠️ Session store not available: {e}")
    print("💡 Make sure session store is properly installed")
    sys.exit(1)

# Event logging
from events import create_service_logger

# Initialize event logger
events = create_service_logger("chat-with-sessions", "1.0.0")

class ChatWithSessionsServicer(
    chat_pb2_grpc.ChatServiceServicer,
    health_pb2_grpc.HealthServiceServicer
):
    """
    Chat service with embedded session management using write-through architecture
    
    Implements:
    - Standard chat service operations
    - Session management with Redis/CRDB write-through
    - Progressive disclosure UI support
    - Health checks for both chat and session storage
    """

    def __init__(self):
        self.start_time = time.time()
        self.service_ready = False

        # Initialize session store
        self._initialize_session_store()

        # Active conversations (in-memory cache)
        self.active_conversations = {}

        events.info("Chat service with sessions initialized", {
            "session_store_ready": self.session_store is not None,
            "service_ready": self.service_ready
        })

    def _initialize_session_store(self):
        """Initialize session store with write-through architecture"""
        try:
            # Use environment variables for configuration
            config = SessionStoreConfig(
                redis_host=os.getenv('REDIS_HOST', 'localhost'),
                redis_port=int(os.getenv('REDIS_PORT', '6379')),
                redis_db=int(os.getenv('REDIS_DB', '0')),
                crdb_host=os.getenv('CRDB_HOST', 'localhost'),
                crdb_port=int(os.getenv('CRDB_PORT', '26257')),
                crdb_database=os.getenv('CRDB_DATABASE', 'unhinged'),
                crdb_user=os.getenv('CRDB_USER', 'root')
            )

            self.session_store = SessionStore(config)
            self.service_ready = True

            events.info("Session store initialized", {
                "redis_host": config.redis_host,
                "crdb_host": config.crdb_host,
                "write_through": True
            })

        except Exception as e:
            events.error("Failed to initialize session store", exception=e)
            self.session_store = None
            self.service_ready = False

    # ========================================================================
    # Session Management Methods
    # ========================================================================

    def _create_session(self, conversation_id: str, metadata: dict[str, Any]) -> bool:
        """Create session with write-through storage"""
        try:
            session_key = f"session:{conversation_id}:metadata"
            session_data = {
                "conversation_id": conversation_id,
                "created_at": time.time(),
                "status": "active",
                **metadata
            }

            success = self.session_store.write(session_key, session_data)
            if success:
                events.info("Session created", {
                    "conversation_id": conversation_id,
                    "session_key": session_key
                })

            return success

        except Exception as e:
            events.error("Session creation failed", {
                "conversation_id": conversation_id,
                "error": str(e)
            })
            return False

    def _get_session(self, conversation_id: str) -> dict[str, Any] | None:
        """Get session data with Redis-first read"""
        try:
            session_key = f"session:{conversation_id}:metadata"
            return self.session_store.read(session_key)
        except Exception as e:
            events.error("Session read failed", {
                "conversation_id": conversation_id,
                "error": str(e)
            })
            return None

    def _update_session_state(self, conversation_id: str, state_data: dict[str, Any]) -> bool:
        """Update session state with write-through"""
        try:
            state_key = f"session:{conversation_id}:state"
            return self.session_store.write(state_key, state_data)
        except Exception as e:
            events.error("Session state update failed", {
                "conversation_id": conversation_id,
                "error": str(e)
            })
            return False

    # ========================================================================
    # Chat Service Implementation
    # ========================================================================

    def CreateConversation(self, request: chat_pb2.CreateConversationRequest, context) -> chat_pb2.CreateConversationResponse:
        """Create conversation with embedded session management"""
        try:
            if not self.service_ready:
                context.set_code(grpc.StatusCode.UNAVAILABLE)
                context.set_details("Session store not available")
                return chat_pb2.CreateConversationResponse()

            # Generate conversation ID
            conversation_id = str(uuid.uuid4())

            events.info("Creating conversation with session", {
                "conversation_id": conversation_id,
                "team_id": request.team_id,
                "namespace_id": request.namespace_id,
                "title": request.title
            })

            # Create session first (write-through to Redis + CRDB)
            session_metadata = {
                "team_id": request.team_id,
                "namespace_id": request.namespace_id,
                "title": request.title,
                "description": request.description,
                "settings": {
                    "model": request.settings.model,
                    "temperature": request.settings.temperature,
                    "max_tokens": request.settings.max_tokens,
                    "include_context": request.settings.include_context,
                    "enable_tools": request.settings.enable_tools
                }
            }

            if not self._create_session(conversation_id, session_metadata):
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details("Failed to create session")
                return chat_pb2.CreateConversationResponse()

            # Create conversation object
            conversation = chat_pb2.Conversation()
            conversation.metadata.id = conversation_id
            conversation.metadata.team_id = request.team_id
            conversation.metadata.namespace_id = request.namespace_id
            conversation.metadata.created_at.GetCurrentTime()
            conversation.metadata.updated_at.GetCurrentTime()

            conversation.title = request.title
            conversation.description = request.description
            conversation.settings.CopyFrom(request.settings)
            conversation.status = chat_pb2.CONVERSATION_STATUS_ACTIVE
            conversation.message_count = 0

            # Cache active conversation
            self.active_conversations[conversation_id] = conversation

            # Create response
            response = chat_pb2.CreateConversationResponse()
            response.response.success = True
            response.response.message = "Conversation created with session"
            response.conversation.CopyFrom(conversation)

            events.info("Conversation created successfully", {
                "conversation_id": conversation_id,
                "session_created": True
            })

            return response

        except Exception as e:
            events.error("Conversation creation failed", exception=e)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Conversation creation failed: {str(e)}")
            return chat_pb2.CreateConversationResponse()

    def GetConversation(self, request: chat_pb2.GetConversationRequest, context) -> chat_pb2.GetConversationResponse:
        """Get conversation with session validation"""
        try:
            conversation_id = request.conversation_id

            # Check if session exists
            session_data = self._get_session(conversation_id)
            if not session_data:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Session not found")
                return chat_pb2.GetConversationResponse()

            # Get conversation from cache or reconstruct
            if conversation_id in self.active_conversations:
                conversation = self.active_conversations[conversation_id]
            else:
                # Reconstruct from session data
                conversation = self._reconstruct_conversation(conversation_id, session_data)
                self.active_conversations[conversation_id] = conversation

            response = chat_pb2.GetConversationResponse()
            response.response.success = True
            response.response.message = "Conversation retrieved"
            response.conversation.CopyFrom(conversation)

            return response

        except Exception as e:
            events.error("Get conversation failed", exception=e)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to get conversation: {str(e)}")
            return chat_pb2.GetConversationResponse()

    def SendMessage(self, request: chat_pb2.SendMessageRequest, context) -> chat_pb2.SendMessageResponse:
        """Send message with session state update"""
        try:
            conversation_id = request.conversation_id

            # Validate session exists
            session_data = self._get_session(conversation_id)
            if not session_data:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Session not found")
                return chat_pb2.SendMessageResponse()

            # Create message
            message = chat_pb2.ChatMessage()
            message.metadata.id = str(uuid.uuid4())
            message.metadata.created_at.GetCurrentTime()
            message.conversation_id = conversation_id
            message.role = request.role
            message.content = request.content
            message.status = chat_pb2.MESSAGE_STATUS_SENT

            # Store message in session context
            context_key = f"session:{conversation_id}:context"
            context_data = self.session_store.read(context_key) or {"messages": []}
            context_data["messages"].append({
                "id": message.metadata.id,
                "role": request.role,
                "content": request.content,
                "timestamp": time.time()
            })

            # Write-through to both stores
            self.session_store.write(context_key, context_data)

            # Update conversation message count
            if conversation_id in self.active_conversations:
                self.active_conversations[conversation_id].message_count += 1

            response = chat_pb2.SendMessageResponse()
            response.response.success = True
            response.response.message = "Message sent and stored in session"
            response.message.CopyFrom(message)

            events.info("Message sent", {
                "conversation_id": conversation_id,
                "message_id": message.metadata.id,
                "role": request.role
            })

            return response

        except Exception as e:
            events.error("Send message failed", exception=e)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to send message: {str(e)}")
            return chat_pb2.SendMessageResponse()

    def _reconstruct_conversation(self, conversation_id: str, session_data: dict[str, Any]) -> chat_pb2.Conversation:
        """Reconstruct conversation from session data"""
        conversation = chat_pb2.Conversation()
        conversation.metadata.id = conversation_id
        conversation.metadata.team_id = session_data.get("team_id", "")
        conversation.metadata.namespace_id = session_data.get("namespace_id", "")
        conversation.title = session_data.get("title", "")
        conversation.description = session_data.get("description", "")
        conversation.status = chat_pb2.CONVERSATION_STATUS_ACTIVE

        # Get message count from context
        context_key = f"session:{conversation_id}:context"
        context_data = self.session_store.read(context_key) or {"messages": []}
        conversation.message_count = len(context_data.get("messages", []))

        return conversation

    # ========================================================================
    # Health Check Implementation
    # ========================================================================

    def Check(self, request: health_pb2.HealthCheckRequest, context) -> health_pb2.HealthCheckResponse:
        """Health check including session store status"""
        response = health_pb2.HealthCheckResponse()

        if self.service_ready and self.session_store:
            # Check session store health
            health = self.session_store.health_check()
            redis_healthy = health["redis"]["status"] == "healthy"
            crdb_healthy = health["crdb"]["status"] == "healthy"

            if redis_healthy and crdb_healthy:
                response.status = health_pb2.HealthCheckResponse.SERVING
            else:
                response.status = health_pb2.HealthCheckResponse.NOT_SERVING
        else:
            response.status = health_pb2.HealthCheckResponse.NOT_SERVING

        return response

    def Watch(self, request: health_pb2.HealthCheckRequest, context) -> Iterator[health_pb2.HealthCheckResponse]:
        """Health check watch implementation"""
        while True:
            yield self.Check(request, context)
            time.sleep(5)

def serve():
    """Start the gRPC server with embedded session management"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    servicer = ChatWithSessionsServicer()

    # Register services
    chat_pb2_grpc.add_ChatServiceServicer_to_server(servicer, server)
    health_pb2_grpc.add_HealthServiceServicer_to_server(servicer, server)

    listen_addr = '[::]:9095'  # Chat service with sessions
    server.add_insecure_port(listen_addr)

    events.info("Starting chat service with sessions", {"address": listen_addr})
    server.start()

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        events.info("Shutting down chat service")
        if servicer.session_store:
            servicer.session_store.close()
        server.stop(0)

if __name__ == '__main__':
    serve()
