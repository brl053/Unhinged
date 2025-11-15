"""
Configuration management for Unhinged Desktop GUI

This module provides centralized configuration management with environment variable
support and validation. It follows the principle of configuration over hardcoding.
"""

import logging
import os
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ServiceEndpoint:
    """Represents a service endpoint with host, port, and protocol information"""

    host: str
    port: int
    protocol: str = "grpc"

    @property
    def address(self) -> str:
        """Get the full address string for connecting to this service"""
        return f"{self.host}:{self.port}"

    @property
    def url(self) -> str:
        """Get the full URL for HTTP services"""
        if self.protocol == "http":
            return f"http://{self.host}:{self.port}"
        elif self.protocol == "https":
            return f"https://{self.host}:{self.port}"
        else:
            return self.address


class ServiceConfig:
    """Centralized service configuration with environment variable support"""

    # Default service configurations
    _DEFAULTS = {
        "speech_to_text": ServiceEndpoint(
            host=os.environ.get("STT_HOST", "localhost"),
            port=int(os.environ.get("STT_GRPC_PORT", "1191")),
            protocol="grpc",
        ),
        "text_to_speech": ServiceEndpoint(
            host=os.environ.get("TTS_HOST", "localhost"),
            port=int(os.environ.get("TTS_GRPC_PORT", "9092")),
            protocol="grpc",
        ),
        "vision_ai": ServiceEndpoint(
            host=os.environ.get("VISION_HOST", "localhost"),
            port=int(os.environ.get("VISION_GRPC_PORT", "9093")),
            protocol="grpc",
        ),
        "llm": ServiceEndpoint(
            host=os.environ.get("LLM_HOST", "localhost"),
            port=int(os.environ.get("LLM_HTTP_PORT", "1500")),
            protocol="http",
        ),
        "chat": ServiceEndpoint(
            host=os.environ.get("CHAT_HOST", "localhost"),
            port=int(os.environ.get("CHAT_GRPC_PORT", "9095")),
            protocol="grpc",
        ),
        "persistence": ServiceEndpoint(
            host=os.environ.get("PERSISTENCE_HOST", "localhost"),
            port=int(os.environ.get("PERSISTENCE_HTTP_PORT", "1300")),
            protocol="http",
        ),
        "redis": ServiceEndpoint(
            host=os.environ.get("REDIS_HOST", "localhost"),
            port=int(os.environ.get("REDIS_PORT", "1201")),
            protocol="redis",
        ),
        "postgres": ServiceEndpoint(
            host=os.environ.get("POSTGRES_HOST", "localhost"),
            port=int(os.environ.get("POSTGRES_PORT", "1200")),
            protocol="postgres",
        ),
    }

    def __init__(self, config_file: Path | None = None):
        """Initialize service configuration

        Args:
            config_file: Optional path to configuration file (for future use)
        """
        self._endpoints = self._DEFAULTS.copy()
        self._config_file = config_file

        # Load from config file if provided
        if config_file and config_file.exists():
            self._load_from_file(config_file)

    def get_endpoint(self, service_name: str) -> ServiceEndpoint:
        """Get endpoint configuration for a service

        Args:
            service_name: Name of the service (e.g., 'speech_to_text', 'llm')

        Returns:
            ServiceEndpoint object with connection details

        Raises:
            KeyError: If service name is not configured
        """
        if service_name not in self._endpoints:
            raise KeyError(f"Unknown service: {service_name}")

        return self._endpoints[service_name]

    def set_endpoint(self, service_name: str, endpoint: ServiceEndpoint) -> None:
        """Set endpoint configuration for a service

        Args:
            service_name: Name of the service
            endpoint: ServiceEndpoint object with connection details
        """
        self._endpoints[service_name] = endpoint
        logger.info(f"Updated {service_name} endpoint to {endpoint.address}")

    def get_all_endpoints(self) -> dict[str, ServiceEndpoint]:
        """Get all configured service endpoints"""
        return self._endpoints.copy()

    def validate_configuration(self) -> dict[str, bool]:
        """Validate that all required services are configured

        Returns:
            Dictionary mapping service names to validation status
        """
        validation_results = {}
        required_services = ["speech_to_text", "llm", "persistence"]

        for service in required_services:
            try:
                endpoint = self.get_endpoint(service)
                # Basic validation - check that port is reasonable
                is_valid = (
                    1 <= endpoint.port <= 65535
                    and endpoint.host
                    and endpoint.protocol in ["grpc", "http", "https", "redis", "postgres"]
                )
                validation_results[service] = is_valid

                if not is_valid:
                    logger.warning(f"Invalid configuration for {service}: {endpoint}")

            except KeyError:
                validation_results[service] = False
                logger.error(f"Missing configuration for required service: {service}")

        return validation_results

    def _load_from_file(self, config_file: Path) -> None:
        """Load configuration from file (placeholder for future implementation)"""
        # TODO: Implement YAML/JSON config file loading
        logger.info(f"Config file loading not yet implemented: {config_file}")


class AppConfig:
    """Application-wide configuration settings"""

    def __init__(self):
        # Audio recording settings
        self.audio_sample_rate = int(os.environ.get("AUDIO_SAMPLE_RATE", "16000"))
        self.audio_channels = int(os.environ.get("AUDIO_CHANNELS", "1"))
        self.audio_format = os.environ.get("AUDIO_FORMAT", "S16_LE")
        self.audio_device = os.environ.get("AUDIO_DEVICE", "pipewire")
        self.recording_duration = int(os.environ.get("RECORDING_DURATION", "10"))

        # gRPC settings
        self.grpc_max_message_size = int(
            os.environ.get("GRPC_MAX_MESSAGE_SIZE", str(1024 * 1024 * 1024))
        )  # 1GB
        self.grpc_timeout = int(os.environ.get("GRPC_TIMEOUT", "30"))

        # UI settings
        self.enable_debug_mode = os.environ.get("DEBUG_MODE", "false").lower() == "true"
        self.log_level = os.environ.get("LOG_LEVEL", "INFO").upper()

        # Service health check settings
        self.health_check_timeout = int(os.environ.get("HEALTH_CHECK_TIMEOUT", "5"))
        self.health_check_interval = int(os.environ.get("HEALTH_CHECK_INTERVAL", "30"))
        self.max_retry_attempts = int(os.environ.get("MAX_RETRY_ATTEMPTS", "3"))
        self.retry_delay = float(os.environ.get("RETRY_DELAY", "1.0"))


# Global configuration instances
service_config = ServiceConfig()
app_config = AppConfig()


def get_service_endpoint(service_name: str) -> ServiceEndpoint:
    """Convenience function to get a service endpoint"""
    return service_config.get_endpoint(service_name)


def validate_all_services() -> bool:
    """Validate all service configurations

    Returns:
        True if all required services are properly configured
    """
    validation_results = service_config.validate_configuration()
    all_valid = all(validation_results.values())

    if not all_valid:
        failed_services = [name for name, valid in validation_results.items() if not valid]
        logger.error(f"Configuration validation failed for services: {failed_services}")

    return all_valid


def log_configuration() -> None:
    """Log current configuration for debugging"""
    logger.info("=== Service Configuration ===")
    for name, endpoint in service_config.get_all_endpoints().items():
        logger.info(f"{name}: {endpoint.protocol}://{endpoint.address}")

    logger.info("=== App Configuration ===")
    logger.info(
        f"Audio: {app_config.audio_sample_rate}Hz, {app_config.audio_channels}ch, {app_config.audio_format}"
    )
    logger.info(
        f"gRPC: max_message_size={app_config.grpc_max_message_size}, timeout={app_config.grpc_timeout}s"
    )
    logger.info(f"Debug mode: {app_config.enable_debug_mode}")
