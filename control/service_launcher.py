#!/usr/bin/env python3
"""
@llm-type control-system
@llm-legend Service launcher with unified service registry integration
@llm-key Launches essential services using centralized service discovery
@llm-map Core service orchestration component replacing hardcoded configurations
@llm-axiom Uses service registry for dynamic service discovery and health monitoring
@llm-contract Provides cohesive service integration for GUI startup
@llm-token service-launcher: Unified service orchestration with registry integration
"""
"""
🚀 Service Launcher - Cohesive Service Integration

Launches essential services before starting the native GUI.
Provides cohesive integration between `make start` and service composition.
"""

import subprocess
import time
import sys
import requests
from pathlib import Path
from typing import List, Dict, Optional
import json
from unhinged_events import create_service_logger

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from network import get_service_registry, ServiceStatus

# Initialize event logger
events = create_service_logger("service-launcher", "1.0.0")


class ServiceLauncher:
    """
    Launches and manages essential services for the native GUI.
    
    Provides cohesive integration between build system and service composition.
    """
    
    # Essential services for GUI functionality
    ESSENTIAL_SERVICES = [
        {
            "name": "LLM Service (Ollama)",
            "compose_service": "llm",
            "health_url": "http://localhost:1500/api/tags",
            "port": 1500,
            "required": True,
            "description": "Local LLM service for chat functionality"
        },
        {
            "name": "Persistence Platform",
            "compose_service": "persistence-platform",
            "health_url": "http://localhost:8190/api/v1/health",
            "port": 8190,
            "required": False,
            "description": "Independent Kotlin persistence platform (NO SPRING BOOT - pure independence)"
        },
        {
            "name": "Database",
            "compose_service": "database",
            "health_url": None,  # No HTTP health check
            "port": 1200,
            "required": False,
            "description": "PostgreSQL database"
        }
    ]
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.compose_file = self.project_root / "orchestration/docker-compose.production.yml"
        self.running_services: List[str] = []
        self.service_registry = get_service_registry()

    def launch_essential_services(self, timeout: int = 120) -> bool:
        """
        Launch essential services needed for GUI functionality.

        Returns True if all required services are running.
        """
        # Check if Docker is available
        if not self._check_docker():
            events.warn("Docker not available - GUI will run in offline mode")
            return False
        
        # Check which services are already running
        running = self._check_running_services()
        
        # Determine which services to start
        to_start = []
        for service in self.ESSENTIAL_SERVICES:
            if service["compose_service"] not in running:
                to_start.append(service)
        
        if not to_start:
            return True

        # Start missing services
        for service in to_start:
            if service["required"] or self._should_start_service(service):
                success = self._start_service(service, timeout)
                if service["required"] and not success:
                    events.error("Required service failed to start", {"service": service['name']})
                    return False

        return True
    
    def _check_docker(self) -> bool:
        """Check if Docker is available"""
        try:
            result = subprocess.run(
                ["docker", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _check_running_services(self) -> List[str]:
        """Check which services are currently running"""
        try:
            result = subprocess.run([
                "docker", "compose", "-f", str(self.compose_file), "ps", "--services", "--filter", "status=running"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return result.stdout.strip().split('\n') if result.stdout.strip() else []
            else:
                return []
        except Exception as e:
            return []
    
    def _should_start_service(self, service: Dict) -> bool:
        """Ask user if they want to start optional service"""
        if service["required"]:
            return True
        
        
        try:
            response = input("   Start this service? (y/N): ").strip().lower()
            return response in ['y', 'yes']
        except KeyboardInterrupt:
            return False
    
    def _start_service(self, service: Dict, timeout: int) -> bool:
        """Start a specific service"""
        service_name = service["compose_service"]
        
        try:
            # Start the service
            result = subprocess.run([
                "docker", "compose", "-f", str(self.compose_file), 
                "up", "-d", service_name
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                events.error("Failed to start service", {"service": service['name'], "error": result.stderr})
                return False
            
            # Wait for service to be healthy
            if service["health_url"]:
                return self._wait_for_health(service, timeout)
            else:
                # For services without health checks, wait a bit
                time.sleep(5)
                return True
                
        except Exception as e:
            events.error("Error starting service", exception=e, metadata={"service": service['name']})
            return False
    
    def _wait_for_health(self, service: Dict, timeout: int) -> bool:
        """Wait for service to become healthy"""
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(service["health_url"], timeout=5)
                if response.status_code == 200:
                    self.running_services.append(service["compose_service"])
                    return True
            except requests.RequestException:
                pass
            
            time.sleep(2)
        
        events.warn("Service did not become healthy", {"service": service['name'], "timeout": timeout})
        return False
    
    def get_service_status(self) -> Dict:
        """Get status of all services"""
        status = {}
        
        for service in self.ESSENTIAL_SERVICES:
            if service["health_url"]:
                try:
                    response = requests.get(service["health_url"], timeout=3)
                    status[service["name"]] = {
                        "running": response.status_code == 200,
                        "port": service["port"],
                        "url": service["health_url"]
                    }
                except requests.RequestException:
                    status[service["name"]] = {
                        "running": False,
                        "port": service["port"],
                        "url": service["health_url"]
                    }
            else:
                # Check if container is running
                running_services = self._check_running_services()
                status[service["name"]] = {
                    "running": service["compose_service"] in running_services,
                    "port": service["port"],
                    "url": None
                }
        
        return status
    
    def stop_services(self):
        """Stop services that were started by this launcher"""
        if not self.running_services:
            return
        
        
        try:
            subprocess.run([
                "docker", "compose", "-f", str(self.compose_file),
                "stop"
            ] + self.running_services, timeout=30)
            
            self.running_services.clear()
            
        except Exception as e:
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
