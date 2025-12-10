#!/usr/bin/env python3

"""
Service Health Monitor with Auto-Recovery

Monitors the health of all 4 core services and automatically restarts
failed containers to ensure the voice/AI pipeline is fully operational.
"""

import logging
import subprocess

# Import ServiceRegistry for unified service configuration
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests

sys.path.append(str(Path(__file__).parent.parent.parent))
import builtins
import contextlib

from services.shared.service_registry import ServiceEndpoint, ServiceRegistry

# Import gRPC health checking (optional)
try:
    import grpc
    from unhinged_proto_clients.health import health_pb2, health_pb2_grpc

    GRPC_HEALTH_AVAILABLE = True
except ImportError:
    GRPC_HEALTH_AVAILABLE = False


@dataclass
class ServiceConfig:
    """Legacy configuration for a monitored service - DEPRECATED"""

    name: str
    container_name: str
    health_url: str | None
    health_port: int
    compose_service: str
    compose_file: str
    timeout: int = 10
    critical: bool = True


class ServiceHealthMonitor:
    """
    Enhanced service health monitor with protocol-aware checking.

    Uses ServiceRegistry for unified service configuration and supports:
    - gRPC health.proto checking for internal services
    - HTTP health endpoints for external services
    - TCP port checking for database services
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logging.getLogger(__name__)

        # Use ServiceRegistry for unified configuration
        self.service_registry = ServiceRegistry()
        self.services = self._load_service_configs()  # Legacy compatibility
        self.service_endpoints = self.service_registry.get_all_services()

        # Container mapping for Docker operations
        self.container_mapping = {
            "llm": "ollama-service",
            "persistence-platform": "persistence-platform-service",
            "speech-to-text": "speech-to-text-service",
            "text-to-speech": "text-to-speech-service",
            "vision-ai": "vision-ai-service",
            "database": "unhinged-postgres",
        }

    def _load_service_configs(self) -> dict[str, ServiceConfig]:
        """Load service configurations"""
        return {
            "llm": ServiceConfig(
                name="LLM Service (Ollama)",
                container_name="ollama-service",
                health_url="http://localhost:1500/api/tags",
                health_port=1500,
                compose_service="llm",
                compose_file="orchestration/docker-compose.production.yml",
                timeout=15,
                critical=True,
            ),
            "persistence": ServiceConfig(
                name="Persistence Platform",
                container_name="persistence-platform-service",
                health_url="http://localhost:1300/api/v1/health",
                health_port=1300,
                compose_service="persistence-platform",
                compose_file="orchestration/docker-compose.production.yml",
                timeout=10,
                critical=True,
            ),
            "database": ServiceConfig(
                name="Database",
                container_name="unhinged-postgres",
                health_url=None,  # TCP port check only
                health_port=1200,
                compose_service="database",
                compose_file="orchestration/docker-compose.production.yml",
                timeout=5,
                critical=True,
            ),
            "speech-to-text": ServiceConfig(
                name="Speech-to-Text Service",
                container_name="speech-to-text-service",
                health_url=None,  # gRPC service, use TCP port check
                health_port=1191,  # gRPC port
                compose_service="speech-to-text",
                compose_file="orchestration/docker-compose.production.yml",
                timeout=10,
                critical=True,
            ),
        }

    def check_service_health(self, service_id: str) -> tuple[bool, str]:
        """
        Enhanced health checking with protocol awareness.

        Uses ServiceRegistry configuration to determine appropriate health check method:
        - gRPC services: health.proto checking
        - HTTP services: HTTP endpoint checking
        - TCP services: Port connectivity checking
        """
        # Check if service exists in registry
        if service_id not in self.service_endpoints:
            return False, f"Unknown service: {service_id}"

        endpoint = self.service_endpoints[service_id]

        # Check if container is running (if applicable)
        if service_id in self.container_mapping:
            container_name = self.container_mapping[service_id]
            container_running = self._is_container_running(container_name)
            if not container_running:
                return False, f"Container {container_name} is not running"

        # Use protocol-aware health checking
        health_method = endpoint.health_check_method

        if health_method == "grpc_health_proto":
            return self._check_grpc_health(endpoint)
        elif health_method == "http_endpoint":
            return self._check_http_health(endpoint)
        else:  # tcp_port
            return self._check_tcp_health(endpoint)

    def _check_grpc_health(self, endpoint: ServiceEndpoint) -> tuple[bool, str]:
        """Check health using gRPC health.proto"""
        if not GRPC_HEALTH_AVAILABLE:
            return False, "gRPC health checking not available (missing proto clients)"

        try:
            channel = grpc.insecure_channel(endpoint.grpc_endpoint)
            health_client = health_pb2_grpc.HealthServiceStub(channel)

            request = health_pb2.HeartbeatRequest()
            response = health_client.Heartbeat(request, timeout=5.0)

            if response.alive and response.status == health_pb2.HEALTH_STATUS_HEALTHY:
                return (
                    True,
                    f"gRPC healthy (v{response.version}, uptime: {response.uptime_ms}ms)",
                )
            else:
                return False, f"gRPC unhealthy (status: {response.status})"

        except grpc.RpcError as e:
            return False, f"gRPC health check failed: {e.code()}"
        except Exception as e:
            return False, f"gRPC health check error: {e}"
        finally:
            with contextlib.suppress(builtins.BaseException):
                channel.close()

    def _check_http_health(self, endpoint: ServiceEndpoint) -> tuple[bool, str]:
        """Check health using HTTP endpoint"""
        try:
            response = requests.get(endpoint.full_health_url, timeout=10)
            if response.status_code == 200:
                return True, "HTTP healthy"
            else:
                return False, f"HTTP health check failed: {response.status_code}"
        except requests.exceptions.RequestException as e:
            return False, f"HTTP health check failed: {e}"

    def _check_tcp_health(self, endpoint: ServiceEndpoint) -> tuple[bool, str]:
        """Check health using TCP port connectivity"""
        is_healthy = self._check_tcp_port(endpoint.port)
        return is_healthy, "TCP port check"

    def _is_container_running(self, container_name: str) -> bool:
        """Check if Docker container is running"""
        try:
            result = subprocess.run(
                [
                    "docker",
                    "ps",
                    "--filter",
                    f"name={container_name}",
                    "--format",
                    "{{.Names}}",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            return container_name in result.stdout
        except subprocess.TimeoutExpired:
            self.logger.warning(f"Timeout checking container {container_name}")
            return False
        except Exception as e:
            self.logger.error(f"Error checking container {container_name}: {e}")
            return False

    def _check_tcp_port(self, port: int) -> bool:
        """Check if TCP port is listening"""
        try:
            import socket

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex(("localhost", port))
            sock.close()
            return result == 0
        except Exception:
            return False

    def restart_service(self, service_id: str) -> tuple[bool, str]:
        """Restart a failed service"""
        if service_id not in self.services:
            return False, f"Unknown service: {service_id}"

        service = self.services[service_id]
        compose_file = self.project_root / service.compose_file

        if not compose_file.exists():
            return False, f"Compose file not found: {compose_file}"

        try:
            self.logger.info(f"🔄 Restarting service: {service.name}")

            # Stop the service
            stop_result = subprocess.run(
                [
                    "docker",
                    "compose",
                    "-f",
                    str(compose_file),
                    "stop",
                    service.compose_service,
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if stop_result.returncode != 0:
                self.logger.warning(f"Stop command had issues: {stop_result.stderr}")

            # Remove the container
            rm_result = subprocess.run(
                [
                    "docker",
                    "compose",
                    "-f",
                    str(compose_file),
                    "rm",
                    "-f",
                    service.compose_service,
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if rm_result.returncode != 0:
                self.logger.warning(f"Remove command had issues: {rm_result.stderr}")

            # Start the service
            start_result = subprocess.run(
                [
                    "docker",
                    "compose",
                    "-f",
                    str(compose_file),
                    "up",
                    "-d",
                    service.compose_service,
                ],
                capture_output=True,
                text=True,
                timeout=120,
            )

            if start_result.returncode != 0:
                return False, f"Failed to start service: {start_result.stderr}"

            # Wait for service to be ready
            self.logger.info(f"⏳ Waiting for {service.name} to be ready...")
            for attempt in range(12):  # 60 seconds total
                time.sleep(5)
                healthy, status = self.check_service_health(service_id)
                if healthy:
                    self.logger.info(f"✅ {service.name} is now healthy")
                    return True, "Service restarted successfully"
                self.logger.info(f"🔄 Attempt {attempt + 1}/12: {status}")

            return False, "Service started but failed health checks after 60 seconds"

        except subprocess.TimeoutExpired:
            return False, "Timeout while restarting service"
        except Exception as e:
            return False, f"Error restarting service: {e}"

    def monitor_and_recover_all(self) -> dict[str, dict]:
        """Monitor all services and auto-recover failed ones"""
        results = {}

        self.logger.info("🏥 Starting comprehensive service health check...")

        for service_id, service in self.services.items():
            self.logger.info(f"🔍 Checking {service.name}...")

            healthy, status = self.check_service_health(service_id)

            if healthy:
                self.logger.info(f"🟢 {service.name}: Healthy")
                results[service_id] = {
                    "status": "healthy",
                    "message": status,
                    "action": "none",
                }
            else:
                self.logger.warning(f"🔴 {service.name}: {status}")

                if service.critical:
                    self.logger.info(f"🔄 Attempting auto-recovery for {service.name}...")
                    success, message = self.restart_service(service_id)

                    if success:
                        self.logger.info(f"✅ {service.name}: Auto-recovery successful")
                        results[service_id] = {
                            "status": "recovered",
                            "message": message,
                            "action": "restarted",
                        }
                    else:
                        self.logger.error(f"❌ {service.name}: Auto-recovery failed - {message}")
                        results[service_id] = {
                            "status": "failed",
                            "message": message,
                            "action": "restart_failed",
                        }
                else:
                    results[service_id] = {
                        "status": "unhealthy",
                        "message": status,
                        "action": "skipped_non_critical",
                    }

        return results

    def get_service_status_summary(self) -> dict[str, Any]:
        """Get current status of all services without recovery"""
        summary: dict[str, Any] = {
            "healthy": [],
            "unhealthy": [],
            "total": len(self.services),
            "critical_healthy": 0,
            "critical_total": 0,
        }

        for service_id, service in self.services.items():
            healthy, status = self.check_service_health(service_id)

            service_info = {
                "id": service_id,
                "name": service.name,
                "status": status,
                "critical": service.critical,
            }

            if healthy:
                summary["healthy"].append(service_info)
                if service.critical:
                    summary["critical_healthy"] += 1
            else:
                summary["unhealthy"].append(service_info)

            if service.critical:
                summary["critical_total"] += 1

        summary["health_percentage"] = (len(summary["healthy"]) / summary["total"]) * 100
        summary["critical_health_percentage"] = (
            (summary["critical_healthy"] / summary["critical_total"]) * 100 if summary["critical_total"] > 0 else 0
        )

        return summary


def main():
    """CLI interface for service health monitoring"""
    import argparse

    parser = argparse.ArgumentParser(description="Service Health Monitor with Auto-Recovery")
    parser.add_argument("--status", action="store_true", help="Show service status only")
    parser.add_argument(
        "--recover",
        action="store_true",
        help="Monitor and auto-recover failed services",
    )
    parser.add_argument("--service", help="Check specific service only")

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    monitor = ServiceHealthMonitor(Path("."))

    if args.service:
        healthy, status = monitor.check_service_health(args.service)
        print(f"{'🟢' if healthy else '🔴'} {args.service}: {status}")
        return 0 if healthy else 1

    elif args.status:
        summary = monitor.get_service_status_summary()
        print("\n🏥 SERVICE HEALTH SUMMARY")
        print(f"Overall Health: {summary['health_percentage']:.1f}% ({len(summary['healthy'])}/{summary['total']})")
        print(
            f"Critical Services: {summary['critical_health_percentage']:.1f}% "
            f"({summary['critical_healthy']}/{summary['critical_total']})"
        )

        print("\n🟢 HEALTHY SERVICES:")
        for service in summary["healthy"]:
            print(f"  • {service['name']}")

        if summary["unhealthy"]:
            print("\n🔴 UNHEALTHY SERVICES:")
            for service in summary["unhealthy"]:
                print(f"  • {service['name']}: {service['status']}")

        return 0 if summary["critical_health_percentage"] == 100 else 1

    elif args.recover:
        results = monitor.monitor_and_recover_all()

        print("\n🏥 AUTO-RECOVERY RESULTS:")
        for service_id, result in results.items():
            service_name = monitor.services[service_id].name
            status_icon = {
                "healthy": "🟢",
                "recovered": "✅",
                "failed": "❌",
                "unhealthy": "🔴",
            }.get(result["status"], "🔵")

            print(f"{status_icon} {service_name}: {result['message']}")

        # Return success if all critical services are healthy or recovered
        critical_ok = all(
            results[sid]["status"] in ["healthy", "recovered"]
            for sid, service in monitor.services.items()
            if service.critical
        )
        return 0 if critical_ok else 1

    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    exit(main())
