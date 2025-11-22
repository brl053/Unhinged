#!/usr/bin/env python3
"""
@llm-type service.api
@llm-does service launcher with unified service registry integration
"""

"""
🚀 Service Launcher - Cohesive Service Integration

Launches essential services before starting the native GUI.
Provides cohesive integration between `make start` and service composition.
"""

import logging
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import requests

sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent.parent / "libs" / "event-framework" / "python" / "src"))
sys.path.append(str(Path(__file__).parent.parent / "generated/python/clients"))

try:
    from events import EventLogger, create_service_logger

    # Initialize event logger
    events: EventLogger | logging.Logger = create_service_logger("service-launcher", "1.0.0")
    USING_EVENT_FRAMEWORK = True
except ImportError:
    # Fallback to basic logging if event framework not available
    events = logging.getLogger("service-launcher")
    USING_EVENT_FRAMEWORK = False

from network import get_service_registry


# Helper function to handle different logging APIs
def log_warning(message, metadata=None):
    """Log warning using appropriate API based on available logger"""
    if USING_EVENT_FRAMEWORK:
        events.warn(message, metadata or {})
    else:
        # Use warning() for standard logging module (warn() is deprecated)
        events.warning(message)


# gRPC health check imports
try:
    import grpc
    from unhinged_proto_clients.health import health_pb2, health_pb2_grpc

    GRPC_AVAILABLE = True
except ImportError:
    GRPC_AVAILABLE = False

# gRPC health check imports
try:
    import grpc
    from unhinged_proto_clients.health import health_pb2, health_pb2_grpc

    GRPC_AVAILABLE = True
except ImportError:
    GRPC_AVAILABLE = False
    log_warning("gRPC not available - falling back to HTTP health checks")


class ServiceLauncher:
    """
    Launches and manages essential services for the native GUI.

    Provides cohesive integration between build system and service composition.
    """

    # Essential services for GUI functionality
    # ALL SERVICES ARE ESSENTIAL - the system requires complete service availability
    ESSENTIAL_SERVICES: list[dict[str, Any]] = [
        {
            "name": "Database",
            "compose_service": "database",
            "health_url": None,  # No HTTP health check
            "port": 1200,
            "required": True,
            "description": "PostgreSQL database - foundation for all persistence",
        },
        {
            "name": "Redis Cache",
            "compose_service": "redis",
            "health_url": None,  # Redis uses PING command
            "port": 1201,
            "required": True,
            "description": "Redis cache for session management and write-through architecture",
        },
        {
            "name": "Persistence Platform",
            "compose_service": "persistence-platform",
            "health_url": "http://localhost:1300/api/v1/health",
            "port": 1300,
            "required": True,
            "description": "Kotlin persistence platform for data storage and retrieval",
        },
        {
            "name": "LLM Service (Ollama)",
            "compose_service": "llm",
            "health_url": "http://localhost:1500/api/tags",
            "port": 1500,
            "required": True,
            "description": "Local LLM service for chat and conversation functionality",
        },
        {
            "name": "Speech-to-Text Service",
            "compose_service": "speech-to-text",
            "health_url": "http://localhost:1101/health",
            "port": 1101,
            "grpc_port": 9091,
            "implements_health_proto": True,
            "required": True,
            "description": "Whisper-based speech transcription service for voice input",
        },
        {
            "name": "Text-to-Speech Service",
            "compose_service": "text-to-speech",
            "health_url": "http://localhost:1102/health",
            "port": 1102,
            "grpc_port": 9092,
            "implements_health_proto": True,
            "required": True,
            "description": "Neural voice synthesis service for audio output",
        },
        {
            "name": "Vision AI Service",
            "compose_service": "vision-ai",
            "health_url": "http://localhost:1103/health",
            "port": 1103,
            "grpc_port": 9093,
            "implements_health_proto": True,
            "required": True,
            "description": "BLIP-based image analysis service for vision capabilities",
        },
        {
            "name": "Chat Service with Sessions",
            "compose_service": "chat-with-sessions",
            "health_url": None,  # gRPC service, uses health proto
            "port": 9095,
            "grpc_port": 9095,
            "implements_health_proto": True,
            "required": True,
            "description": "Chat service with embedded session management and write-through persistence",
        },
    ]

    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or Path.cwd()
        self.compose_file = self.project_root / "build/orchestration/docker-compose.production.yml"
        self.running_services: list[str] = []
        self.service_registry = get_service_registry()

    def launch_essential_services(self, timeout: int = 120) -> bool:
        """
        Launch essential services needed for GUI functionality.

        Returns True if all required services are running.
        """
        print("🔍 Checking Docker availability...")
        # Check if Docker is available
        if not self._check_docker():
            log_warning("Docker not available - GUI will run in offline mode")
            return False

        # Check which services are already running
        running = self._check_running_services()

        # Determine which services to start
        to_start = []
        for service in self.ESSENTIAL_SERVICES:
            if service["compose_service"] is None:
                # Direct service - check if it's running via health check
                if not self._is_service_healthy(service):
                    to_start.append(service)
            elif service["compose_service"] not in running:
                to_start.append(service)

        if not to_start:
            print("✅ Services initialized (all running)")
            return True

        # Start missing services
        failed_required = []
        started_count = 0
        for service in to_start:
            if service["required"] or self._should_start_service(service):
                success = self._start_service(service, min(timeout, 30))  # Cap individual service timeout
                if service["required"] and not success:
                    failed_required.append(service["name"])
                    events.error("Required service failed to start", None, {"service": service["name"]})
                elif success:
                    started_count += 1

        if failed_required:
            print(f"⚠️  Some services failed to start: {', '.join(failed_required)}")
            print("   Continuing with available services")
            return True

        print(f"✅ Services initialized ({len(running) + started_count}/{len(self.ESSENTIAL_SERVICES)} running)")
        return True

    def _check_docker(self) -> bool:
        """Check if Docker is available"""
        try:
            result = subprocess.run(["docker", "--version"], capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except Exception:
            return False

    def _check_running_services(self) -> list[str]:
        """Check which services are currently running"""
        try:
            result = subprocess.run(
                [
                    "docker",
                    "compose",
                    "-f",
                    str(self.compose_file),
                    "ps",
                    "--services",
                    "--filter",
                    "status=running",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                return result.stdout.strip().split("\n") if result.stdout.strip() else []
            else:
                return []
        except Exception:
            return []

    def _should_start_service(self, service: dict) -> bool:
        """Determine if a service should be started"""
        # All services marked as required MUST be started
        # Optional services are skipped in non-interactive mode
        return service["required"]

    def _start_service(self, service: dict, timeout: int) -> bool:
        """Start a specific service"""
        service_name = service["compose_service"]

        try:
            # Check if this is a direct command service
            if service_name is None and "start_command" in service:
                print("      🐍 Starting direct Python service...")
                return self._start_direct_service(service, timeout)

            print(f"      🐳 Starting Docker service: {service_name}")
            # Start the service via Docker Compose
            result = subprocess.run(
                [
                    "docker",
                    "compose",
                    "-f",
                    str(self.compose_file),
                    "up",
                    "-d",
                    service_name,
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                print(f"      ❌ Docker start failed: {result.stderr.strip()}")
                events.error(
                    "Failed to start service",
                    None,
                    {"service": service["name"], "error": result.stderr},
                )
                return False

            print("      🔍 Waiting for health check...")
            # Wait for service to be healthy
            if service["health_url"]:
                return self._wait_for_health(service, timeout)
            else:
                # For services without health checks, wait a bit
                print("      ⏳ No health check - waiting 5 seconds...")
                time.sleep(5)
                return True

        except subprocess.TimeoutExpired:
            print("      ⏰ Service startup timed out after 30 seconds")
            return False
        except Exception as e:
            print(f"      ❌ Unexpected error: {str(e)}")
            if USING_EVENT_FRAMEWORK:
                events.error(
                    "Error starting service",
                    exception=e,
                    metadata={"service": service["name"]},
                )
            else:
                events.error(f"Error starting service {service['name']}: {e}")
            return False

    def _start_direct_service(self, service: dict, timeout: int) -> bool:
        """
        Start a service using direct command execution rather than Docker Compose.

        This method extends the service launcher to support services that run directly
        as Python processes rather than Docker containers, enabling integration of
        components like the Whisper transcription service into the standard startup flow.

        Key Features:
        - Environment variable setup (PYTHONPATH, etc.)
        - Background process execution
        - Health check integration
        - Consistent service management interface

        Args:
            service: Service configuration dictionary with start_command
            timeout: Maximum time to wait for service health check

        Returns:
            bool: True if service started successfully and passed health check
        """
        try:
            import os

            # Set up environment
            env = os.environ.copy()
            env[
                "PYTHONPATH"
            ] = f"{self.project_root}/build/python/venv/lib/python3.12/site-packages:{env.get('PYTHONPATH', '')}"

            # Start the service in background
            command = service["start_command"].split()
            process = subprocess.Popen(
                command,
                cwd=str(self.project_root),
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )

            events.info(
                "Started direct service",
                {"service": service["name"], "pid": process.pid},
            )

            # Wait for service to be healthy
            if service["health_url"]:
                return self._wait_for_health(service, timeout)
            else:
                time.sleep(3)
                return True

        except Exception as e:
            events.error(
                "Failed to start direct service",
                e,
                {"service": service["name"]},
            )
            return False

    def _is_service_healthy(self, service: dict) -> bool:
        """
        Check if a service is currently healthy via HTTP health endpoint.

        This method provides unified health checking for both Docker Compose services
        and direct command services, enabling consistent service monitoring across
        the voice transcription pipeline.

        Args:
            service: Service configuration with health_url

        Returns:
            bool: True if service responds successfully to health check
        """
        if not service.get("health_url"):
            return False

        try:
            response = requests.get(service["health_url"], timeout=3)
            return response.status_code == 200
        except Exception:
            return False

    def _wait_for_health(self, service: dict, timeout: int) -> bool:
        """Wait for service to become healthy"""

        start_time = time.time()
        attempts = 0
        while time.time() - start_time < timeout:
            attempts += 1
            try:
                response = requests.get(service["health_url"], timeout=3)
                if response.status_code == 200:
                    print(f"      ✅ Health check passed after {attempts} attempts")
                    if service["compose_service"]:
                        self.running_services.append(service["compose_service"])
                    return True
                else:
                    print(f"      🔄 Health check attempt {attempts}: HTTP {response.status_code}")
            except requests.RequestException as e:
                print(f"      🔄 Health check attempt {attempts}: {type(e).__name__}")

            if attempts % 5 == 0:  # Progress update every 10 seconds
                elapsed = time.time() - start_time
                print(f"      ⏳ Still waiting for health check... ({elapsed:.1f}s elapsed)")

            time.sleep(2)

        print(f"      ❌ Health check failed after {timeout}s timeout")
        log_warning(
            "Service did not become healthy",
            {"service": service["name"], "timeout": timeout},
        )
        return False

    def _check_grpc_health(self, port: int) -> bool:
        """Check service health via gRPC health.proto"""
        if not GRPC_AVAILABLE:
            return False

        try:
            channel = grpc.insecure_channel(f"localhost:{port}")
            stub = health_pb2_grpc.HealthServiceStub(channel)
            request = health_pb2.HeartbeatRequest()
            response = stub.Heartbeat(request, timeout=5)
            return response.alive and response.status == 1
        except Exception:
            return False

    def _check_service_health(self, service: dict) -> bool:
        """Check if service is healthy via gRPC or HTTP"""
        # Try gRPC health check first if service implements health proto
        if service.get("implements_health_proto") and GRPC_AVAILABLE:
            grpc_port = service.get("grpc_port")
            if grpc_port:
                try:
                    return self._check_grpc_health(grpc_port)
                except Exception as e:
                    log_warning(
                        f"gRPC health check failed for {service['name']}",
                        {"error": str(e)},
                    )

        # Fallback to HTTP health check
        if not service.get("health_url"):
            return False

        try:
            response = requests.get(service["health_url"], timeout=3)
            return response.status_code == 200
        except Exception:
            return False

    def get_service_status(self) -> dict:
        """Get status of all services using gRPC health checks when available"""
        status = {}

        for service in self.ESSENTIAL_SERVICES:
            service_healthy = False
            health_method = "unknown"

            # Try gRPC health check first if available
            if service.get("implements_health_proto") and GRPC_AVAILABLE:
                grpc_port = service.get("grpc_port")
                if grpc_port:
                    try:
                        service_healthy = self._check_grpc_health(grpc_port)
                        health_method = f"gRPC:{grpc_port}"
                    except Exception:
                        pass

            # Fallback to HTTP health check
            if not service_healthy and service.get("health_url"):
                try:
                    response = requests.get(service["health_url"], timeout=3)
                    service_healthy = response.status_code == 200
                    health_method = f"HTTP:{service['port']}"
                except requests.RequestException:
                    pass

            # Fallback to container status check
            if not service_healthy and not service.get("health_url"):
                running_services = self._check_running_services()
                service_healthy = service.get("compose_service") in running_services
                health_method = "container"

            status[service["name"]] = {
                "running": service_healthy,
                "port": service["port"],
                "url": service.get("health_url"),
                "health_method": health_method,
            }

        return status

    def initialize_session(self, timeout: int = 30) -> str | None:
        """
        Initialize a chat session after services are ready.

        Returns:
            session_id: UUID of created session, or None if initialization fails
        """
        try:
            from libs.python.session.session_initialization import (
                SessionInitializationService,
            )

            events.info("Initializing chat session...")
            service = SessionInitializationService(timeout=timeout)
            session_id = service.create_session()
            events.info(f"Session initialized: {session_id}")
            return session_id

        except Exception as e:
            events.error(f"Session initialization failed: {e}")
            return None

    def stop_services(self):
        """Stop services that were started by this launcher"""
        if not self.running_services:
            return

        try:
            subprocess.run(
                ["docker", "compose", "-f", str(self.compose_file), "stop"] + self.running_services,
                timeout=30,
            )

            self.running_services.clear()

        except Exception:
            pass


def main():
    """CLI interface for service launcher"""
    import argparse

    parser = argparse.ArgumentParser(description="Launch essential services for Unhinged GUI")
    parser.add_argument("--timeout", type=int, default=120, help="Timeout for service startup")
    parser.add_argument("--status", action="store_true", help="Show service status")
    parser.add_argument("--stop", action="store_true", help="Stop services")

    args = parser.parse_args()

    launcher = ServiceLauncher()

    if args.status:
        status = launcher.get_service_status()
        for name, info in status.items():
            status_icon = "🟢" if info["running"] else "🔴"
            print(f"{status_icon} {name}: {info}")
        return

    if args.stop:
        launcher.stop_services()
        return

    # Launch services
    success = launcher.launch_essential_services(args.timeout)

    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
