"""
gRPC Client Factory

Creates gRPC clients using the generated protobuf code from /proto.
Provides a centralized way to create and configure gRPC connections.
"""

import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import grpc


class GrpcClientFactory:
    """Factory for creating gRPC clients using generated protobuf code."""

    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or self._find_project_root()
        self._ensure_protobuf_clients_in_path()
        self._clients_cache: dict[str, Any] = {}

    def _find_project_root(self) -> Path:
        """Find the project root directory."""
        current = Path(__file__).parent
        while current.parent != current:
            if (current / "proto").exists() and (current / "generated").exists():
                return current
            current = current.parent
        raise RuntimeError("Could not find project root with proto/ and generated/ directories")

    def _ensure_protobuf_clients_in_path(self):
        """Ensure generated protobuf clients are in Python path."""
        protobuf_clients = self.project_root / "generated" / "python" / "clients"
        if protobuf_clients.exists() and str(protobuf_clients) not in sys.path:
            sys.path.insert(0, str(protobuf_clients))

    @contextmanager
    def create_channel(self, address: str, options: list | None = None):
        """Create a gRPC channel with proper cleanup and increased message size limits."""
        # Default options for large message support (256MB for long audio recordings)
        MAX_MESSAGE_SIZE = 1024 * 1024 * 1024  # 1GB
        default_options = [
            ('grpc.max_receive_message_length', MAX_MESSAGE_SIZE),
            ('grpc.max_send_message_length', MAX_MESSAGE_SIZE),
        ]

        # Merge with provided options
        if options:
            default_options.extend(options)

        channel = grpc.insecure_channel(address, options=default_options)
        try:
            yield channel
        finally:
            channel.close()

    def create_audio_client(self, address: str = 'localhost:9091'):
        """Create an AudioService gRPC client with large message support."""
        try:
            from unhinged_proto_clients import audio_pb2_grpc

            if address not in self._clients_cache:
                # Create channel with large message size support
                MAX_MESSAGE_SIZE = 1024 * 1024 * 1024  # 1GB
                options = [
                    ('grpc.max_receive_message_length', MAX_MESSAGE_SIZE),
                    ('grpc.max_send_message_length', MAX_MESSAGE_SIZE),
                ]

                channel = grpc.insecure_channel(address, options=options)
                client = audio_pb2_grpc.AudioServiceStub(channel)
                self._clients_cache[address] = {
                    'client': client,
                    'channel': channel,
                    'service_type': 'audio'
                }

            return self._clients_cache[address]['client']

        except ImportError as e:
            raise RuntimeError(f"Failed to import audio protobuf clients: {e}. "
                             f"Make sure protobuf clients are generated.")

    def create_llm_client(self, address: str = 'localhost:9092'):
        """Create an LLM service gRPC client."""
        try:
            from unhinged_proto_clients import llm_pb2_grpc

            if address not in self._clients_cache:
                channel = grpc.insecure_channel(address)
                client = llm_pb2_grpc.LLMServiceStub(channel)
                self._clients_cache[address] = {
                    'client': client,
                    'channel': channel,
                    'service_type': 'llm'
                }

            return self._clients_cache[address]['client']

        except ImportError as e:
            raise RuntimeError(f"Failed to import LLM protobuf clients: {e}. "
                             f"Make sure protobuf clients are generated.")

    def create_vision_client(self, address: str = 'localhost:9093'):
        """Create a Vision AI service gRPC client."""
        try:
            from unhinged_proto_clients import vision_pb2_grpc

            if address not in self._clients_cache:
                channel = grpc.insecure_channel(address)
                client = vision_pb2_grpc.VisionServiceStub(channel)
                self._clients_cache[address] = {
                    'client': client,
                    'channel': channel,
                    'service_type': 'vision'
                }

            return self._clients_cache[address]['client']

        except ImportError as e:
            raise RuntimeError(f"Failed to import Vision protobuf clients: {e}. "
                             f"Make sure protobuf clients are generated.")

    def create_chat_client(self, address: str = 'localhost:9095'):
        """Create a Chat service gRPC client."""
        try:
            from unhinged_proto_clients import chat_pb2_grpc

            if address not in self._clients_cache:
                channel = grpc.insecure_channel(address)
                client = chat_pb2_grpc.ChatServiceStub(channel)
                self._clients_cache[address] = {
                    'client': client,
                    'channel': channel,
                    'service_type': 'chat'
                }

            return self._clients_cache[address]['client']

        except ImportError as e:
            raise RuntimeError(f"Failed to import Chat protobuf clients: {e}. "
                             f"Make sure protobuf clients are generated.")

    def create_image_generation_client(self, address: str = 'localhost:9094'):
        """Create an Image Generation service gRPC client with large message support."""
        try:
            from unhinged_proto_clients import image_generation_pb2_grpc

            if address not in self._clients_cache:
                # Create channel with large message size support for images
                MAX_MESSAGE_SIZE = 1024 * 1024 * 1024  # 1GB
                options = [
                    ('grpc.max_receive_message_length', MAX_MESSAGE_SIZE),
                    ('grpc.max_send_message_length', MAX_MESSAGE_SIZE),
                ]

                channel = grpc.insecure_channel(address, options=options)
                client = image_generation_pb2_grpc.ImageGenerationServiceStub(channel)
                self._clients_cache[address] = {
                    'client': client,
                    'channel': channel,
                    'service_type': 'image_generation'
                }

            return self._clients_cache[address]['client']

        except ImportError as e:
            raise RuntimeError(f"Failed to import Image Generation protobuf clients: {e}. "
                             f"Make sure protobuf clients are generated.")

    def create_chat_client(self, address: str = 'localhost:9095'):
        """Create a Chat service gRPC client."""
        try:
            from unhinged_proto_clients import chat_pb2_grpc

            if address not in self._clients_cache:
                channel = grpc.insecure_channel(address)
                client = chat_pb2_grpc.ChatServiceStub(channel)
                self._clients_cache[address] = {
                    'client': client,
                    'channel': channel,
                    'service_type': 'chat'
                }

            return self._clients_cache[address]['client']

        except ImportError as e:
            raise RuntimeError(f"Failed to import Chat protobuf clients: {e}. "
                             f"Make sure protobuf clients are generated.")



    def create_image_generation_client(self, address: str = 'localhost:9094'):
        """Create an Image Generation service gRPC client."""
        try:
            from unhinged_proto_clients import image_generation_pb2_grpc

            image_gen_address = f"{address}_image_gen"
            if image_gen_address not in self._clients_cache:
                channel = grpc.insecure_channel(address)
                client = image_generation_pb2_grpc.ImageGenerationServiceStub(channel)
                self._clients_cache[image_gen_address] = {
                    'client': client,
                    'channel': channel,
                    'service_type': 'image_generation'
                }

            return self._clients_cache[image_gen_address]['client']

        except ImportError as e:
            raise RuntimeError(f"Failed to import Image Generation protobuf clients: {e}. "
                             f"Make sure protobuf clients are generated.")

    def create_health_client(self, address: str):
        """Create a Health check gRPC client."""
        try:
            from unhinged_proto_clients.health import health_pb2_grpc

            health_address = f"{address}_health"
            if health_address not in self._clients_cache:
                channel = grpc.insecure_channel(address)
                client = health_pb2_grpc.HealthStub(channel)
                self._clients_cache[health_address] = {
                    'client': client,
                    'channel': channel,
                    'service_type': 'health'
                }

            return self._clients_cache[health_address]['client']

        except ImportError as e:
            raise RuntimeError(f"Failed to import Health protobuf clients: {e}. "
                             f"Make sure protobuf clients are generated.")

    def close_all_connections(self):
        """Close all cached gRPC connections."""
        for cached_client in self._clients_cache.values():
            if 'channel' in cached_client:
                cached_client['channel'].close()
        self._clients_cache.clear()

    def get_protobuf_modules(self):
        """Get all available protobuf modules for debugging."""
        try:
            from unhinged_proto_clients import audio_pb2, common_pb2
            modules = {
                'audio_pb2': audio_pb2,
                'common_pb2': common_pb2
            }

            # Try to import optional modules
            try:
                from unhinged_proto_clients import llm_pb2
                modules['llm_pb2'] = llm_pb2
            except ImportError:
                pass

            try:
                from unhinged_proto_clients import vision_pb2
                modules['vision_pb2'] = vision_pb2
            except ImportError:
                pass

            try:
                from unhinged_proto_clients.health import health_pb2
                modules['health_pb2'] = health_pb2
            except ImportError:
                pass

            return modules

        except ImportError as e:
            raise RuntimeError(f"No protobuf clients found: {e}")


# Convenience functions for quick client creation
_default_factory = None

def _get_default_factory() -> GrpcClientFactory:
    """Get or create the default client factory."""
    global _default_factory
    if _default_factory is None:
        _default_factory = GrpcClientFactory()
    return _default_factory

def create_audio_client(address: str = 'localhost:1191'):
    """Create an AudioService gRPC client using default factory."""
    return _get_default_factory().create_audio_client(address)

def create_llm_client(address: str = 'localhost:9092'):
    """Create an LLM service gRPC client using default factory."""
    return _get_default_factory().create_llm_client(address)

def create_chat_client(address: str = 'localhost:9095'):
    """Create a Chat service gRPC client using default factory."""
    return _get_default_factory().create_chat_client(address)



def create_image_generation_client(address: str = 'localhost:9094'):
    """Create an Image Generation service gRPC client using default factory."""
    return _get_default_factory().create_image_generation_client(address)

def create_vision_client(address: str = 'localhost:9093'):
    """Create a Vision AI service gRPC client using default factory."""
    return _get_default_factory().create_vision_client(address)

def create_chat_client(address: str = 'localhost:9095'):
    """Create a Chat service gRPC client using default factory."""
    return _get_default_factory().create_chat_client(address)

# Service Framework Integration
# Expert recommendation: consolidate gRPC patterns with hardware-aware management

def initialize_service_framework():
    """Initialize service framework with hardware-aware resource management"""
    try:
        import sys
        from pathlib import Path

        # Add service framework to path
        service_framework_path = Path(__file__).parent.parent / "service_framework"
        if service_framework_path.exists():
            sys.path.insert(0, str(service_framework_path.parent))

        from service_framework import get_global_pool, register_service

        # Register common services with the global connection pool
        # Service timeouts are configurable via environment variables: {SERVICE_NAME}_TIMEOUT
        # Import stub classes for proper gRPC service registration

        # Chat service - standard timeout
        try:
            from unhinged_proto_clients import chat_pb2_grpc
            register_service("chat", "localhost:9095", stub_class=chat_pb2_grpc.ChatServiceStub, timeout=60.0)
        except ImportError:
            register_service("chat", "localhost:9095", timeout=60.0)  # Fallback without stub

        # Image generation service - longer timeout for image processing
        try:
            from unhinged_proto_clients import image_generation_pb2_grpc
            register_service("image_generation", "localhost:9094", stub_class=image_generation_pb2_grpc.ImageGenerationServiceStub, timeout=180.0)
        except ImportError:
            register_service("image_generation", "localhost:9094", timeout=180.0)  # Fallback without stub

        # Vision service - standard timeout
        try:
            from unhinged_proto_clients import vision_pb2_grpc
            register_service("vision", "localhost:9093", stub_class=vision_pb2_grpc.VisionServiceStub, timeout=60.0)
        except ImportError:
            register_service("vision", "localhost:9093", timeout=60.0)  # Fallback without stub

        # Speech-to-text service - longer timeout for audio transcription
        try:
            from unhinged_proto_clients import audio_pb2_grpc
            register_service("speech_to_text", "localhost:1191", stub_class=audio_pb2_grpc.AudioServiceStub, timeout=600.0)
        except ImportError:
            register_service("speech_to_text", "localhost:1191", timeout=600.0)  # Fallback without stub

        # Text-to-speech service - standard timeout
        try:
            from unhinged_proto_clients import audio_pb2_grpc
            register_service("text_to_speech", "localhost:9092", stub_class=audio_pb2_grpc.AudioServiceStub, timeout=120.0)
        except ImportError:
            register_service("text_to_speech", "localhost:9092", timeout=120.0)  # Fallback without stub

        print("✅ Service framework initialized with hardware-aware resource management")
        return True

    except ImportError as e:
        print(f"⚠️ Service framework not available: {e}")
        return False


def get_service_framework_client(service_name: str):
    """Get service client using new service framework (hardware-aware)"""
    try:
        from service_framework import get_global_pool
        return get_global_pool().get_client(service_name)
    except ImportError:
        raise RuntimeError("Service framework not available. Use legacy create_*_client functions.")


def call_service_method(service_name: str, method_name: str, request, timeout: float = 120.0):
    """Call service method using hardware-aware service framework"""
    try:
        from service_framework import call_service
        return call_service(service_name, method_name, request, timeout)
    except ImportError:
        raise RuntimeError("Service framework not available. Use legacy client methods.")


def stream_service_method(service_name: str, method_name: str, request, timeout: float = 120.0):
    """Call streaming service method using hardware-aware service framework"""
    try:
        from service_framework import stream_service
        return stream_service(service_name, method_name, request, timeout)
    except ImportError:
        raise RuntimeError("Service framework not available. Use legacy client methods.")


# Auto-initialize service framework if available
_framework_initialized = initialize_service_framework()
