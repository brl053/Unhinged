#!/usr/bin/env python3
"""
@llm-type control-system
@llm-legend service_registry.py - Central service discovery and registration system
@llm-key Unified service discovery replacing hardcoded service configurations
@llm-map Core component of the network control system providing service location transparency
@llm-axiom Single source of truth for all service endpoints and health status
@llm-contract Provides standardized service discovery interface for all system components
@llm-token service_registry: Centralized service discovery and health monitoring
"""

import json
import time
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class ServiceStatus(Enum):
    """Service health status enumeration."""
    UNKNOWN = "unknown"
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    STARTING = "starting"
    STOPPED = "stopped"


@dataclass
class ServiceEndpoint:
    """Service endpoint configuration."""
    name: str
    host: str
    port: int
    protocol: str
    health_url: Optional[str] = None
    description: str = ""
    required: bool = False
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
    
    @property
    def base_url(self) -> str:
        """Get base URL for service."""
        return f"{self.protocol}://{self.host}:{self.port}"
    
    @property
    def full_health_url(self) -> str:
        """Get full health check URL."""
        if self.health_url:
            if self.health_url.startswith('http'):
                return self.health_url
            return f"{self.base_url}{self.health_url}"
        return f"{self.base_url}/health"


class ServiceRegistry:
    """
    Central service registry for unified service discovery.
    
    Replaces hardcoded service configurations with dynamic discovery
    and health monitoring across all system components.
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path("control/network/services.json")
        self.services: Dict[str, ServiceEndpoint] = {}
        self.health_cache: Dict[str, Tuple[ServiceStatus, float]] = {}
        self.cache_ttl = 30  # seconds
        
        self._load_service_definitions()
    
    def _load_service_definitions(self):
        """Load service definitions from configuration."""
        # Default service definitions
        default_services = {
            "llm": ServiceEndpoint(
                name="LLM Service (Ollama)",
                host="localhost",
                port=1500,
                protocol="http",
                health_url="/api/tags",
                description="Local LLM service for chat functionality",
                required=True,
                tags=["ai", "llm", "ollama"]
            ),
            "persistence-platform": ServiceEndpoint(
                name="Persistence Platform",
                host="localhost", 
                port=8190,
                protocol="http",
                health_url="/api/v1/health",
                description="Independent Kotlin persistence platform",
                required=False,
                tags=["database", "persistence", "kotlin"]
            ),
            "speech-to-text": ServiceEndpoint(
                name="Speech-to-Text Service",
                host="localhost",
                port=8100,
                protocol="http", 
                health_url="/health",
                description="Whisper-based speech transcription",
                required=False,
                tags=["ai", "speech", "whisper"]
            ),
            "text-to-speech": ServiceEndpoint(
                name="Text-to-Speech Service",
                host="localhost",
                port=8002,
                protocol="http",
                health_url="/health", 
                description="Neural voice synthesis",
                required=False,
                tags=["ai", "tts", "voice"]
            ),
            "vision-ai": ServiceEndpoint(
                name="Vision AI Service",
                host="localhost",
                port=8001,
                protocol="http",
                health_url="/health",
                description="BLIP-based image analysis",
                required=False,
                tags=["ai", "vision", "blip"]
            ),
            "database": ServiceEndpoint(
                name="Database",
                host="localhost",
                port=1200,
                protocol="postgresql",
                description="PostgreSQL database",
                required=False,
                tags=["database", "postgresql"]
            )
        }
        
        # Load from file if exists, otherwise use defaults
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config_data = json.load(f)
                    
                for service_id, service_data in config_data.items():
                    self.services[service_id] = ServiceEndpoint(**service_data)
            except Exception as e:
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
            with open(self.config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
        except Exception as e:
            # Failed to save service config
    
    def register_service(self, service_id: str, endpoint: ServiceEndpoint):
        """Register a new service endpoint."""
        self.services[service_id] = endpoint
        self._save_service_definitions()
    
    def get_service(self, service_id: str) -> Optional[ServiceEndpoint]:
        """Get service endpoint by ID."""
        return self.services.get(service_id)
    
    def get_services_by_tag(self, tag: str) -> List[Tuple[str, ServiceEndpoint]]:
        """Get all services with specific tag."""
        return [(sid, svc) for sid, svc in self.services.items() if tag in svc.tags]
    
    def get_all_services(self) -> Dict[str, ServiceEndpoint]:
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
    
    def get_service_status_report(self) -> Dict[str, Dict]:
        """Get comprehensive status report for all services."""
        report = {}
        
        for service_id, service in self.services.items():
            status = self.check_service_health(service_id)
            report[service_id] = {
                'name': service.name,
                'status': status.value,
                'endpoint': service.base_url,
                'required': service.required,
                'description': service.description,
                'tags': service.tags
            }
            
        return report
    
    def get_healthy_services(self) -> List[Tuple[str, ServiceEndpoint]]:
        """Get all currently healthy services."""
        healthy = []
        for service_id, service in self.services.items():
            if self.check_service_health(service_id) == ServiceStatus.HEALTHY:
                healthy.append((service_id, service))
        return healthy
    
    def get_required_services_status(self) -> Tuple[bool, List[str]]:
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
        report = registry.get_service_status_report()
            
    elif args.health_check:
        status = registry.check_service_health(args.health_check, force_refresh=True)
        service = registry.get_service(args.health_check)
        if service:
            
    elif args.list_services:
        services = registry.get_all_services()
            
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
