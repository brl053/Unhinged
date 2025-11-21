#!/usr/bin/env python3
"""
Minimal Chat Service for Testing Session Creation
"""

import sys
import time
import uuid
from concurrent import futures
from pathlib import Path

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

# Event logging
from events import create_service_logger

# Initialize event logger
events = create_service_logger("minimal-chat", "1.0.0")


class MinimalChatServicer(chat_pb2_grpc.ChatServiceServicer, health_pb2_grpc.HealthServiceServicer):
    """Minimal chat service for testing session creation"""

    def __init__(self):
        self.start_time = time.time()
        self.service_ready = True
        events.info("Minimal chat service initialized")

    def CreateConversation(self, request, context):
        """Create a new conversation (session)"""
        try:
            events.info(
                "Creating conversation",
                {
                    "team_id": request.team_id,
                    "namespace_id": request.namespace_id,
                    "title": request.title,
                },
            )

            # Generate a simple conversation ID
            conversation_id = str(uuid.uuid4())

            # Create timestamps
            from google.protobuf.timestamp_pb2 import Timestamp

            now = Timestamp()
            now.GetCurrentTime()

            # Create response
            conversation = chat_pb2.Conversation(
                metadata=common_pb2.ResourceMetadata(
                    resource_id=conversation_id,
                    team_id=request.team_id,
                    namespace_id=request.namespace_id,
                    created_by="system",  # TODO: Get from auth context
                    created_at=now,
                    updated_at=now,
                    version=1,
                ),
                title=request.title,
                description=request.description,
                settings=request.settings,
                status=chat_pb2.ConversationStatus.CONVERSATION_STATUS_ACTIVE,
            )

            response = chat_pb2.CreateConversationResponse(
                response=common_pb2.StandardResponse(success=True, message="Conversation created successfully"),
                conversation=conversation,
            )

            events.info("Conversation created", {"conversation_id": conversation_id})
            return response

        except Exception as e:
            events.error("Failed to create conversation", exception=e)
            return chat_pb2.CreateConversationResponse(
                response=common_pb2.StandardResponse(success=False, message=f"Failed to create conversation: {e}")
            )

    def Check(self, request, context):
        """Health check implementation"""
        return health_pb2.HealthCheckResponse(status=health_pb2.HealthCheckResponse.SERVING)

    def Watch(self, request, context):
        """Health watch implementation"""
        while True:
            yield health_pb2.HealthCheckResponse(status=health_pb2.HealthCheckResponse.SERVING)
            time.sleep(30)


def serve():
    """Start the minimal gRPC server"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    servicer = MinimalChatServicer()

    # Register services
    chat_pb2_grpc.add_ChatServiceServicer_to_server(servicer, server)
    health_pb2_grpc.add_HealthServiceServicer_to_server(servicer, server)

    listen_addr = "[::]:9095"  # Chat service port
    server.add_insecure_port(listen_addr)

    events.info("Starting minimal chat service", {"address": listen_addr})
    server.start()

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        events.info("Shutting down minimal chat service")
        server.stop(0)


if __name__ == "__main__":
    serve()
