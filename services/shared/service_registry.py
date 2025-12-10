#!/usr/bin/env python3
"""
@llm-type service.api
@llm-does service_registry.py - central service discovery and regis...
"""

import json
import time
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path

import requests


class ServiceStatus(Enum):
    """Service health status enumeration."""

    UNKNOWN = "unknown"
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    STARTING = "starting"
    STOPPED = "stopped"


@dataclass
class ServiceEndpoint:
    """
    Service endpoint configuration with proper protocol separation.

    - gRPC services use health.proto for internal health checking
    - HTTP services use traditional HTTP health endpoints
    - TCP services use port connectivity checks
    """

    name: str
    host: str
    port: int
    protocol: str  # "grpc", "http", "tcp", "postgresql"
    health_url: str | None = None  # For HTTP services only
    description: str = ""
    required: bool = False
    tags: list[str] | None = None
    # gRPC-specific configuration
    grpc_port: int | None = None  # If different from main port
    implements_health_proto: bool = False  # Uses health.proto gRPC service

    def __post_init__(self) -> None:
        if self.tags is None:
            self.tags = []
        # Set grpc_port to main port if not specified for gRPC services
        if self.protocol == "grpc" and self.grpc_port is None:
            self.grpc_port = self.port

    @property
    def base_url(self) -> str:
        """Get base URL for HTTP services."""
        if self.protocol in ["http", "https"]:
            return f"{self.protocol}://{self.host}:{self.port}"
        return f"{self.host}:{self.port}"

    @property
    def grpc_endpoint(self) -> str | None:
        """Get gRPC endpoint for health.proto checking."""
        if self.protocol == "grpc" and self.grpc_port:
            return f"{self.host}:{self.grpc_port}"
        return None

    @property
    def full_health_url(self) -> str:
        """Get full health check URL for HTTP services."""
        if self.protocol in ["http", "https"] and self.health_url:
            if self.health_url.startswith("http"):
                return self.health_url
            return f"{self.base_url}{self.health_url}"
        return f"{self.base_url}/health"

    @property
    def health_check_method(self) -> str:
        """Determine the appropriate health check method."""
        if self.protocol == "grpc" and self.implements_health_proto:
            return "grpc_health_proto"
        elif self.protocol in ["http", "https"]:
            return "http_endpoint"
        else:
            return "tcp_port"


class ServiceRegistry:
    """
    Central service registry for unified service discovery.

    Replaces hardcoded service configurations with dynamic discovery
    and health monitoring across all system components.
    """

    def __init__(self, config_path: Path | None = None):
        self.config_path = config_path or Path("services/shared/services.json")
        self.services: dict[str, ServiceEndpoint] = {}
        self.health_cache: dict[str, tuple[ServiceStatus, float]] = {}
        self.cache_ttl = 30  # seconds

        self._load_service_definitions()

    def _load_service_definitions(self):
        """Load service definitions from configuration."""
        # Service definitions with correct protocol configurations
        default_services = {
            "llm": ServiceEndpoint(
                name="LLM Service (Ollama)",
                host="localhost",
                port=1500,
                protocol="http",
                health_url="/api/tags",  # Ollama's health endpoint
                description="Local LLM service for chat functionality",
                required=True,
                tags=["ai", "llm", "ollama"],
            ),
            "persistence-platform": ServiceEndpoint(
                name="Persistence Platform",
                host="localhost",
                port=1300,
                protocol="http",
                health_url="/api/v1/health",
                description="Independent Kotlin persistence platform",
                required=False,
                tags=["database", "persistence", "kotlin"],
                grpc_port=1301,  # Future gRPC port
                implements_health_proto=False,  # Not yet implemented
            ),
            "speech-to-text": ServiceEndpoint(
                name="Speech-to-Text Service",
                host="localhost",
                port=1191,  # gRPC port (external mapping)
                protocol="grpc",
                description="Whisper-based speech transcription",
                required=False,
                tags=["ai", "speech", "whisper"],
                implements_health_proto=True,  # Uses health.proto
            ),
            "text-to-speech": ServiceEndpoint(
                name="Text-to-Speech Service",
                host="localhost",
                port=9092,  # Internal gRPC port
                protocol="grpc",
                description="Neural voice synthesis",
                required=False,
                tags=["ai", "tts", "voice"],
                implements_health_proto=True,  # Uses health.proto
            ),
            "vision-ai": ServiceEndpoint(
                name="Vision AI Service",
                host="localhost",
                port=9093,  # Internal gRPC port
                protocol="grpc",
                description="BLIP-based image analysis",
                required=False,
                tags=["ai", "vision", "blip"],
                implements_health_proto=True,  # Uses health.proto
            ),
            "database": ServiceEndpoint(
                name="Database",
                host="localhost",
                port=1200,
                protocol="postgresql",
                description="PostgreSQL database",
                required=False,
                tags=["database", "postgresql"],
                # Uses TCP port check (default for non-HTTP/gRPC)
            ),
        }

        # Load from file if exists, otherwise use defaults
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    config_data = json.load(f)

                for service_id, service_data in config_data.items():
                    self.services[service_id] = ServiceEndpoint(**service_data)
            except Exception:
                # Failed to load service config, using defaults
                self.services = default_services
        else:
            self.services = default_services
            self._save_service_definitions()

    def _save_service_definitions(self):
        """Save current service definitions to file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        config_data = {}
        for service_id, service in self.services.items():
            config_data[service_id] = asdict(service)

        try:
            with open(self.config_path, "w") as f:
                json.dump(config_data, f, indent=2)
        except Exception:
            # Failed to save service config
            pass

    def register_service(self, service_id: str, endpoint: ServiceEndpoint):
        """Register a new service endpoint."""
        self.services[service_id] = endpoint
        self._save_service_definitions()

    def get_service(self, service_id: str) -> ServiceEndpoint | None:
        """Get service endpoint by ID."""
        return self.services.get(service_id)

    def get_services_by_tag(self, tag: str) -> list[tuple[str, ServiceEndpoint]]:
        """Get all services with specific tag."""
        return [(sid, svc) for sid, svc in self.services.items() if svc.tags and tag in svc.tags]

    def get_all_services(self) -> dict[str, ServiceEndpoint]:
        """Get all registered services."""
        return self.services.copy()

    def check_service_health(self, service_id: str, force_refresh: bool = False) -> ServiceStatus:
        """Check health status of a service."""
        service = self.get_service(service_id)
        if not service:
            return ServiceStatus.UNKNOWN

        # Check cache first
        if not force_refresh and service_id in self.health_cache:
            status, timestamp = self.health_cache[service_id]
            if time.time() - timestamp < self.cache_ttl:
                return status

        # Perform health check
        status = self._perform_health_check(service)
        self.health_cache[service_id] = (status, time.time())
        return status

    def _perform_health_check(self, service: ServiceEndpoint) -> ServiceStatus:
        """Perform actual health check against service."""
        if not service.health_url:
            return ServiceStatus.UNKNOWN

        try:
            response = requests.get(service.full_health_url, timeout=5)
            if response.status_code == 200:
                return ServiceStatus.HEALTHY
            else:
                return ServiceStatus.UNHEALTHY
        except requests.exceptions.ConnectionError:
            return ServiceStatus.STOPPED
        except requests.exceptions.Timeout:
            return ServiceStatus.UNHEALTHY
        except Exception:
            return ServiceStatus.UNKNOWN

    def get_service_status_report(self) -> dict[str, dict]:
        """Get comprehensive status report for all services."""
        report = {}

        for service_id, service in self.services.items():
            status = self.check_service_health(service_id)
            report[service_id] = {
                "name": service.name,
                "status": status.value,
                "endpoint": service.base_url,
                "required": service.required,
                "description": service.description,
                "tags": service.tags,
            }

        return report

    def get_healthy_services(self) -> list[tuple[str, ServiceEndpoint]]:
        """Get all currently healthy services."""
        healthy = []
        for service_id, service in self.services.items():
            if self.check_service_health(service_id) == ServiceStatus.HEALTHY:
                healthy.append((service_id, service))
        return healthy

    def get_required_services_status(self) -> tuple[bool, list[str]]:
        """Check if all required services are healthy."""
        failed_required = []

        for service_id, service in self.services.items():
            if service.required:
                status = self.check_service_health(service_id)
                if status != ServiceStatus.HEALTHY:
                    failed_required.append(service_id)

        return len(failed_required) == 0, failed_required


# Global service registry instance
_registry_instance = None


def get_service_registry() -> ServiceRegistry:
    """Get global service registry instance."""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = ServiceRegistry()
    return _registry_instance


def main():
    """CLI interface for service registry."""
    import argparse

    parser = argparse.ArgumentParser(description="Service Registry Management")
    parser.add_argument("--status", action="store_true", help="Show service status")
    parser.add_argument("--health-check", help="Check health of specific service")
    parser.add_argument("--list-services", action="store_true", help="List all services")

    args = parser.parse_args()

    registry = get_service_registry()

    if args.status:
        registry.get_service_status_report()

    elif args.health_check:
        registry.check_service_health(args.health_check, force_refresh=True)
        service = registry.get_service(args.health_check)
        if service:
            pass

    elif args.list_services:
        registry.get_all_services()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
