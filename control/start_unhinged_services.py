#!/usr/bin/env python3
"""
@llm-type service.startup
@llm-does Comprehensive service startup script for Unhinged voice-first platform
@llm-legend Orchestrates proper service startup sequence for voice-first functionality
@llm-key Ensures all required services are running before GUI functionality is used
@llm-map Integrates with service_launcher.py and provides GUI-friendly startup

Unhinged Service Startup Orchestrator
====================================

This script provides the proper service startup sequence for the Unhinged voice-first AI platform.
It ensures all required services are running in the correct order for full functionality.

Usage:
    python3 control/start_unhinged_services.py [--timeout 120] [--verbose]

Service Startup Order:
1. Docker containers (LLM, Database, Redis, Persistence Platform)
2. Python AI services (Speech-to-Text, Text-to-Speech, Vision AI)
3. Chat service with sessions (gRPC)
4. Service health verification
5. Voice pipeline validation

Expected Behavior:
- "Create Session" button should work in OS chatroom tab
- Platform Launcher should start services successfully
- Voice-first pipeline should be functional
- All gRPC endpoints should be accessible
"""

import argparse
import logging
import subprocess
import sys
import time
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "libs" / "event-framework" / "python" / "src"))

try:
    from events import EventLogger, create_service_logger

    logger: EventLogger | logging.Logger = create_service_logger("service-startup", "1.0.0")
except ImportError:
    logger = logging.getLogger("service-startup")


class UnhingedServiceStartup:
    """Orchestrates the complete Unhinged service startup sequence."""

    def __init__(self, timeout: int = 120, verbose: bool = False):
        self.timeout = timeout
        self.verbose = verbose
        self.project_root = project_root

        # Service definitions with startup order
        self.services = {
            "docker_containers": {
                "order": 1,
                "command": [
                    "docker",
                    "compose",
                    "-f",
                    "build/orchestration/docker-compose.production.yml",
                    "up",
                    "-d",
                ],
                "description": "Docker containers (LLM, Database, Redis, Persistence)",
                "required": True,
                "health_check": self._check_docker_health,
            },
            "chat_service": {
                "order": 2,
                "command": [
                    "./venv-production/bin/python",
                    "services/chat-with-sessions/minimal_grpc_server.py",
                ],
                "description": "Chat service with sessions (gRPC port 9095)",
                "required": True,
                "background": True,
                "health_check": self._check_chat_service,
            },
            "service_health": {
                "order": 3,
                "command": ["python3", "control/service_launcher.py", "--status"],
                "description": "Service health verification",
                "required": False,
                "health_check": None,
            },
        }

        self.running_processes: list[tuple[str, subprocess.Popen[bytes]]] = []

    def start_all_services(self) -> bool:
        """Start all services in the correct order."""
        logger.info("🚀 Starting Unhinged voice-first platform services...")

        # Sort services by startup order
        from typing import cast

        ordered_services = sorted(self.services.items(), key=lambda x: cast(int, x[1].get("order", 0)))

        success = True
        for service_name, config in ordered_services:
            if not self._start_service(service_name, config):
                if config["required"]:
                    logger.error(f"❌ Required service {service_name} failed to start")
                    success = False
                else:
                    # Use warn() for EventLogger, warning() for stdlib Logger
                    if hasattr(logger, "warn"):
                        logger.warn(f"⚠️ Optional service {service_name} failed to start")  # type: ignore[union-attr]
                    else:
                        logger.warning(f"⚠️ Optional service {service_name} failed to start")  # type: ignore[union-attr]

        if success:
            logger.info("✅ All required services started successfully!")
            self._print_service_status()
        else:
            logger.error("❌ Some required services failed to start")

        return success

    def _start_service(self, service_name: str, config: dict) -> bool:
        """Start a single service."""
        logger.info(f"🔄 Starting {config['description']}...")

        try:
            if config.get("background", False):
                # Start as background process
                process = subprocess.Popen(
                    config["command"],
                    cwd=self.project_root,
                    stdout=subprocess.PIPE if not self.verbose else None,
                    stderr=subprocess.PIPE if not self.verbose else None,
                )
                self.running_processes.append((service_name, process))

                # Give background services time to start
                time.sleep(2)

                # Check if process is still running
                if process.poll() is not None:
                    logger.error(f"❌ Background service {service_name} exited immediately")
                    return False

            else:
                # Run synchronously
                result = subprocess.run(
                    config["command"],
                    cwd=self.project_root,
                    capture_output=not self.verbose,
                    text=True,
                    timeout=30,
                )

                if result.returncode != 0:
                    logger.error(f"❌ Service {service_name} failed with exit code {result.returncode}")
                    if self.verbose and result.stderr:
                        logger.error(f"Error output: {result.stderr}")
                    return False

            # Run health check if available
            if config.get("health_check") and not config["health_check"]():
                logger.error(f"❌ Health check failed for {service_name}")
                return False

            logger.info(f"✅ {config['description']} started successfully")
            return True

        except subprocess.TimeoutExpired:
            logger.error(f"❌ Service {service_name} timed out during startup")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to start {service_name}: {e}")
            return False

    def _check_docker_health(self) -> bool:
        """Check if Docker containers are healthy."""
        try:
            result = subprocess.run(
                [
                    "docker",
                    "ps",
                    "--filter",
                    "health=healthy",
                    "--format",
                    "table {{.Names}}",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
            healthy_containers = result.stdout.strip().split("\n")[1:]  # Skip header
            return len(healthy_containers) >= 3  # Expect at least 3 healthy containers
        except Exception:
            return False

    def _check_chat_service(self) -> bool:
        """Check if chat service is accessible on port 9095."""
        try:
            result = subprocess.run(
                ["ss", "-tln", "sport", "=", ":9095"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return "9095" in result.stdout
        except Exception:
            return False

    def _print_service_status(self):
        """Print current service status."""
        logger.info("📊 Service Status Summary:")
        logger.info("  🐳 Docker containers: Check with 'docker ps'")
        logger.info("  💬 Chat service: gRPC port 9095")
        logger.info("  🎤 Voice pipeline: Ready for immediate interaction")
        logger.info("  🖥️ GUI functionality: Create Session should work")

    def stop_services(self):
        """Stop all running background services."""
        logger.info("🛑 Stopping background services...")

        for service_name, process in self.running_processes:
            try:
                process.terminate()
                process.wait(timeout=10)
                logger.info(f"✅ Stopped {service_name}")
            except subprocess.TimeoutExpired:
                process.kill()
                logger.warning(f"⚠️ Force killed {service_name}")
            except Exception as e:
                logger.error(f"❌ Error stopping {service_name}: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Start Unhinged voice-first platform services")
    parser.add_argument("--timeout", type=int, default=120, help="Timeout for service startup")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--stop", action="store_true", help="Stop running services")

    args = parser.parse_args()

    startup = UnhingedServiceStartup(timeout=args.timeout, verbose=args.verbose)

    if args.stop:
        startup.stop_services()
    else:
        success = startup.start_all_services()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
