"""
Service Connector Layer for Unhinged Desktop GUI

This module provides a clean abstraction layer for all service communications,
hiding gRPC/HTTP implementation details from the UI layer.
"""

import logging
import socket
import time
from pathlib import Path
from typing import Any

try:
    from .config import ServiceEndpoint, app_config, service_config
    from .exceptions import (
        AudioFileSizeError,
        AudioTranscriptionError,
        ServiceResponseError,
        ServiceTimeoutError,
        ServiceUnavailableError,
        handle_grpc_error,
    )
except ImportError:
    # Fallback for direct execution
    from config import ServiceEndpoint, app_config, service_config
    from exceptions import (
        AudioFileSizeError,
        AudioTranscriptionError,
        ServiceUnavailableError,
        handle_grpc_error,
    )

logger = logging.getLogger(__name__)


class ServiceConnector:
    """Handles all service communications with proper error handling and retries"""

    def __init__(self):
        self._connection_cache: dict[str, Any] = {}
        self._health_status: dict[str, bool] = {}
        self._last_health_check: dict[str, float] = {}

    def check_service_health(
        self, service_name: str, force_check: bool = False
    ) -> bool:
        """Check if a service is healthy and available

        Args:
            service_name: Name of the service to check
            force_check: Force a new health check even if cached result exists

        Returns:
            True if service is healthy, False otherwise
        """
        current_time = time.time()

        # Use cached result if recent and not forcing
        if not force_check and service_name in self._last_health_check:
            time_since_check = current_time - self._last_health_check[service_name]
            if time_since_check < app_config.health_check_interval:
                return self._health_status.get(service_name, False)

        try:
            endpoint = service_config.get_endpoint(service_name)
            is_healthy = self._perform_health_check(endpoint)

            self._health_status[service_name] = is_healthy
            self._last_health_check[service_name] = current_time

            logger.debug(
                f"Health check for {service_name}: {'healthy' if is_healthy else 'unhealthy'}"
            )
            return is_healthy

        except Exception as e:
            logger.warning(f"Health check failed for {service_name}: {e}")
            self._health_status[service_name] = False
            self._last_health_check[service_name] = current_time
            return False

    def _perform_health_check(self, endpoint: ServiceEndpoint) -> bool:
        """Perform actual health check on an endpoint"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(app_config.health_check_timeout)
            result = sock.connect_ex((endpoint.host, endpoint.port))
            sock.close()
            return result == 0
        except Exception:
            return False

    def transcribe_audio(self, audio_file_path: Path) -> str:
        """Transcribe audio file using speech-to-text service

        Args:
            audio_file_path: Path to the audio file to transcribe

        Returns:
            Transcribed text

        Raises:
            ServiceUnavailableError: If speech-to-text service is not available
            AudioTranscriptionError: If transcription fails
            AudioFileSizeError: If audio file is too large
        """
        service_name = "speech_to_text"

        # Check service health first
        if not self.check_service_health(service_name):
            endpoint = service_config.get_endpoint(service_name)
            raise ServiceUnavailableError(service_name, endpoint.address)

        # Validate file size
        if not audio_file_path.exists():
            raise AudioTranscriptionError("Audio file not found", str(audio_file_path))

        file_size = audio_file_path.stat().st_size
        max_size = app_config.grpc_max_message_size
        min_size = 44  # Minimum WAV header size

        if file_size > max_size:
            raise AudioFileSizeError(file_size, max_size=max_size)

        if file_size < min_size:
            raise AudioFileSizeError(file_size, min_size=min_size)

        # Perform transcription with retries
        for attempt in range(app_config.max_retry_attempts):
            try:
                return self._transcribe_with_grpc(audio_file_path)
            except Exception as e:
                logger.warning(f"Transcription attempt {attempt + 1} failed: {e}")

                if attempt < app_config.max_retry_attempts - 1:
                    time.sleep(
                        app_config.retry_delay * (attempt + 1)
                    )  # Exponential backoff
                else:
                    # Convert to our error hierarchy
                    if "grpc" in str(type(e)).lower():
                        service_error = handle_grpc_error(e, service_name)
                        raise AudioTranscriptionError(
                            str(service_error), str(audio_file_path)
                        )
                    else:
                        raise AudioTranscriptionError(str(e), str(audio_file_path))

    def _transcribe_with_grpc(self, audio_file_path: Path) -> str:
        """Perform actual gRPC transcription call"""
        try:
            # Import gRPC modules
            import sys
            from pathlib import Path as PathlibPath

            project_root = PathlibPath(__file__).parent.parent.parent
            protobuf_path = project_root / "generated" / "python" / "clients"
            if protobuf_path.exists():
                sys.path.insert(0, str(protobuf_path))

            import grpc
            from unhinged_proto_clients import audio_pb2, audio_pb2_grpc, common_pb2

            # Get service endpoint
            endpoint = service_config.get_endpoint("speech_to_text")

            # Configure gRPC options
            options = [
                ("grpc.max_receive_message_length", app_config.grpc_max_message_size),
                ("grpc.max_send_message_length", app_config.grpc_max_message_size),
            ]

            # Create gRPC channel and client
            with grpc.insecure_channel(endpoint.address, options=options) as channel:
                client = audio_pb2_grpc.AudioServiceStub(channel)

                # Read audio file
                with open(audio_file_path, "rb") as f:
                    audio_data = f.read()

                # Create streaming chunks (the service expects StreamChunk iterator)
                def generate_chunks():
                    # Send audio data as chunks
                    chunk_size = 8192  # 8KB chunks
                    for i in range(0, len(audio_data), chunk_size):
                        chunk_data = audio_data[i : i + chunk_size]
                        chunk = common_pb2.StreamChunk(
                            type=common_pb2.CHUNK_TYPE_DATA, data=chunk_data
                        )
                        yield chunk

                # Make streaming gRPC call with timeout
                response = client.SpeechToText(
                    generate_chunks(), timeout=app_config.grpc_timeout
                )

                # Check response and extract transcript
                if response and hasattr(response, "transcript"):
                    return response.transcript.strip()
                else:
                    raise AudioTranscriptionError(
                        "Invalid response from transcription service",
                        file_path=str(audio_file_path),
                    )

        except ImportError as e:
            raise AudioTranscriptionError(f"gRPC client not available: {e}")
        except Exception as e:
            # Re-raise as our exception type
            raise e

    def get_service_status(self) -> dict[str, dict[str, Any]]:
        """Get status of all configured services

        Returns:
            Dictionary with service status information
        """
        status = {}

        for service_name in [
            "speech_to_text",
            "text_to_speech",
            "vision_ai",
            "llm",
            "persistence",
        ]:
            try:
                endpoint = service_config.get_endpoint(service_name)
                is_healthy = self.check_service_health(service_name)

                status[service_name] = {
                    "healthy": is_healthy,
                    "endpoint": endpoint.address,
                    "protocol": endpoint.protocol,
                    "last_checked": self._last_health_check.get(service_name, 0),
                }
            except KeyError:
                status[service_name] = {
                    "healthy": False,
                    "endpoint": "not configured",
                    "protocol": "unknown",
                    "last_checked": 0,
                }

        return status

    def refresh_all_health_checks(self) -> dict[str, bool]:
        """Force refresh health checks for all services

        Returns:
            Dictionary mapping service names to health status
        """
        results = {}

        for service_name in [
            "speech_to_text",
            "text_to_speech",
            "vision_ai",
            "llm",
            "persistence",
        ]:
            results[service_name] = self.check_service_health(
                service_name, force_check=True
            )

        return results


class ServiceRegistry:
    """Service discovery and registration system"""

    def __init__(self):
        self._discovered_services: dict[str, list[ServiceEndpoint]] = {}
        self._preferred_endpoints: dict[str, ServiceEndpoint] = {}

    def discover_service(
        self, service_name: str, port_range: list[int] | None = None
    ) -> ServiceEndpoint | None:
        """Discover a service by checking multiple possible endpoints

        Args:
            service_name: Name of the service to discover
            port_range: List of ports to check (defaults to common ports)

        Returns:
            First working endpoint found, or None if service not found
        """
        if port_range is None:
            # Default port ranges for different services
            port_ranges = {
                "speech_to_text": [1191, 9091, 8000],
                "text_to_speech": [9092, 8001],
                "vision_ai": [9093, 8002],
                "llm": [1500, 11434, 8080],
                "persistence": [1300, 8090, 8080],
            }
            port_range = port_ranges.get(service_name, [8000, 8080, 9000])

        discovered = []

        for port in port_range:
            endpoint = ServiceEndpoint(host="localhost", port=port)
            connector = ServiceConnector()

            if connector._perform_health_check(endpoint):
                discovered.append(endpoint)
                logger.info(f"Discovered {service_name} at {endpoint.address}")

                # Cache the first working endpoint
                if service_name not in self._preferred_endpoints:
                    self._preferred_endpoints[service_name] = endpoint
                    # Update global config
                    service_config.set_endpoint(service_name, endpoint)

                break

        self._discovered_services[service_name] = discovered
        return discovered[0] if discovered else None

    def get_preferred_endpoint(self, service_name: str) -> ServiceEndpoint | None:
        """Get the preferred endpoint for a service"""
        return self._preferred_endpoints.get(service_name)


# Global instances
service_connector = ServiceConnector()
service_registry = ServiceRegistry()
