
import logging; gui_logger = logging.getLogger(__name__)

"""
@llm-type control-system
@llm-legend network_scanner.py - system control component
@llm-key Core functionality for network_scanner
@llm-map Part of the Unhinged system architecture
@llm-axiom Maintains system independence and architectural compliance
@llm-contract Provides standardized interface for system integration
@llm-token network_scanner: system control component
"""
"""
🌐 Network Scanner - Service Discovery

Discovers gRPC services on the network using multiple methods:
1. Port scanning for common gRPC ports
2. Service discovery integration (Consul, etc.)
3. Network broadcast discovery
4. Manual service registration

Features:
- Network port scanning
- Service health checking
- Automatic service registration
- Integration with existing service discovery
"""

import socket
import threading
import time
import json
import requests
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import subprocess


class NetworkScanner:
    """
    Network service discovery for gRPC services.
    
    Discovers services through multiple methods and maintains
    a registry of available services for the API dev tool.
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        
        # Common gRPC ports to scan
        self.common_grpc_ports = [
            50051,  # Default gRPC port
            8080,   # Common HTTP/gRPC gateway
            8081,   # Alternative HTTP port
            8090,   # Alternative gRPC port
            9090,   # Prometheus/monitoring
            8500,   # Consul
            8501,   # Consul HTTPS
            3000,   # Development servers
            5000,   # Flask/development
            6000,   # Alternative development
            7000,   # Alternative development
            8000,   # Common development
            8001,   # Microservice port
            8002,   # Microservice port
            8003,   # Microservice port
        ]
        
        # Network ranges to scan
        self.scan_ranges = [
            "127.0.0.1",      # Localhost
            "localhost",      # Localhost alias
            "0.0.0.0",        # All interfaces
            # Add more ranges as needed
        ]
        
        # Discovered services cache
        self.discovered_services = {}
        self.last_scan_time = 0
        self.scan_cache_duration = 300  # 5 minutes
        
        gui_logger.info(" Network scanner initialized", {"event_type": "network_ready"})
    
    def discover_services(self, force_rescan: bool = False) -> Dict[str, Any]:
        """
        Discover all available gRPC services on the network.
        
        Args:
            force_rescan: Force a new scan even if cache is valid
            
        Returns:
            Dict with discovered services and metadata
        """
        current_time = time.time()
        
        # Check cache validity
        if not force_rescan and (current_time - self.last_scan_time) < self.scan_cache_duration:
            if self.discovered_services:
                return {
                    "success": True,
                    "services": self.discovered_services,
                    "scan_time": self.last_scan_time,
                    "cached": True
                }
        
        gui_logger.debug(" Starting network service discovery...", {"event_type": "scanning"})
        discovered = {}
        
        try:
            # Method 1: Service Discovery Integration
            consul_services = self._discover_from_consul()
            discovered.update(consul_services)
            
            # Method 2: Port Scanning
            scanned_services = self._scan_network_ports()
            discovered.update(scanned_services)
            
            # Method 3: Docker Services
            docker_services = self._discover_docker_services()
            discovered.update(docker_services)
            
            # Method 4: Known Service Endpoints
            known_services = self._check_known_endpoints()
            discovered.update(known_services)
            
            # Update cache
            self.discovered_services = discovered
            self.last_scan_time = current_time
            
            return {
                "success": True,
                "services": discovered,
                "scan_time": current_time,
                "cached": False,
                "methods_used": ["consul", "port_scan", "docker", "known_endpoints"]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Service discovery failed: {str(e)}",
                "services": {},
                "scan_time": current_time
            }
    
    def _discover_from_consul(self) -> Dict[str, Any]:
        """Discover services from Consul service registry"""
        services = {}
        
        try:
            # Try to connect to local Consul
            consul_urls = [
                "http://localhost:8500",
                "http://127.0.0.1:8500",
                "http://consul:8500"  # Docker container name
            ]
            
            for consul_url in consul_urls:
                try:
                    # Get all services
                    response = requests.get(f"{consul_url}/v1/catalog/services", timeout=2)
                    if response.status_code == 200:
                        consul_services = response.json()
                        
                        for service_name, tags in consul_services.items():
                            # Get service details
                            detail_response = requests.get(
                                f"{consul_url}/v1/catalog/service/{service_name}", 
                                timeout=2
                            )
                            
                            if detail_response.status_code == 200:
                                service_details = detail_response.json()
                                
                                for instance in service_details:
                                    service_key = f"{service_name}_{instance['ServiceAddress']}_{instance['ServicePort']}"
                                    services[service_key] = {
                                        "name": service_name,
                                        "host": instance['ServiceAddress'] or instance['Address'],
                                        "port": instance['ServicePort'],
                                        "tags": tags,
                                        "source": "consul",
                                        "health": "unknown",
                                        "endpoint": f"{instance['ServiceAddress'] or instance['Address']}:{instance['ServicePort']}"
                                    }
                        
                        break
                        
                except requests.exceptions.RequestException:
                    continue
                    
        except Exception as e:
            gui_logger.warn(f" Consul discovery failed: {e}")
        
        return services
    
    def _scan_network_ports(self) -> Dict[str, Any]:
        """Scan network for gRPC services on common ports"""
        services = {}
        
        try:
            for host in self.scan_ranges:
                for port in self.common_grpc_ports:
                    if self._is_port_open(host, port):
                        # Check if it's a gRPC service
                        service_info = self._probe_grpc_service(host, port)
                        if service_info:
                            service_key = f"scanned_{host}_{port}"
                            services[service_key] = {
                                "name": service_info.get("name", f"Service-{port}"),
                                "host": host,
                                "port": port,
                                "source": "port_scan",
                                "health": "up",
                                "endpoint": f"{host}:{port}",
                                "proto_info": service_info.get("proto_info", {})
                            }
            
            
        except Exception as e:
            gui_logger.warn(f" Port scanning failed: {e}")
        
        return services
    
    def _discover_docker_services(self) -> Dict[str, Any]:
        """Discover services from Docker containers"""
        services = {}
        
        try:
            # Get running containers
            result = subprocess.run(
                ["docker", "ps", "--format", "json"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        container = json.loads(line)
                        
                        # Look for gRPC-related containers
                        if any(keyword in container.get('Image', '').lower() 
                               for keyword in ['grpc', 'service', 'api']):
                            
                            # Extract port mappings
                            ports = container.get('Ports', '')
                            if ports:
                                # Parse port mappings (e.g., "0.0.0.0:8080->8080/tcp")
                                for port_mapping in ports.split(', '):
                                    if '->' in port_mapping and 'tcp' in port_mapping:
                                        external_part = port_mapping.split('->')[0]
                                        if ':' in external_part:
                                            host_port = external_part.split(':')[-1]
                                            try:
                                                port = int(host_port)
                                                service_key = f"docker_{container['Names']}_{port}"
                                                services[service_key] = {
                                                    "name": container['Names'].lstrip('/'),
                                                    "host": "localhost",
                                                    "port": port,
                                                    "source": "docker",
                                                    "health": "up",
                                                    "endpoint": f"localhost:{port}",
                                                    "container_id": container['ID'],
                                                    "image": container['Image']
                                                }
                                            except ValueError:
                                                continue
                
                
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError) as e:
            gui_logger.warn(f" Docker discovery failed: {e}")
        
        return services
    
    def _check_known_endpoints(self) -> Dict[str, Any]:
        """Check known service endpoints from configuration"""
        services = {}
        
        # Known endpoints that are commonly used in development
        known_endpoints = [
            {"name": "Local gRPC", "host": "localhost", "port": 50051},
            {"name": "API Gateway", "host": "localhost", "port": 8080},
            {"name": "Service Discovery", "host": "localhost", "port": 8500},
        ]
        
        for endpoint in known_endpoints:
            if self._is_port_open(endpoint["host"], endpoint["port"]):
                service_key = f"known_{endpoint['name'].replace(' ', '_')}_{endpoint['port']}"
                services[service_key] = {
                    "name": endpoint["name"],
                    "host": endpoint["host"],
                    "port": endpoint["port"],
                    "source": "known_endpoint",
                    "health": "up",
                    "endpoint": f"{endpoint['host']}:{endpoint['port']}"
                }
        
        return services
    
    def _is_port_open(self, host: str, port: int, timeout: float = 1.0) -> bool:
        """Check if a port is open on a host"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                result = sock.connect_ex((host, port))
                return result == 0
        except Exception:
            return False
    
    def _probe_grpc_service(self, host: str, port: int) -> Optional[Dict[str, Any]]:
        """Probe a service to see if it's gRPC and get basic info"""
        try:
            # This is a basic probe - in a full implementation,
            # you'd use gRPC reflection to get actual service info
            
            # For now, just return basic info if port is open
            return {
                "name": f"gRPC-Service-{port}",
                "proto_info": {
                    "reflection_available": False,
                    "services": []
                }
            }
            
        except Exception as e:
            gui_logger.warn(f" gRPC probe failed for {host}:{port}: {e}")
            return None
    
    def get_service_health(self, host: str, port: int) -> str:
        """Check the health status of a specific service"""
        if self._is_port_open(host, port, timeout=2.0):
            return "up"
        else:
            return "down"
    
    def refresh_service_health(self) -> Dict[str, Any]:
        """Refresh health status for all discovered services"""
        updated_services = {}
        
        for service_key, service_info in self.discovered_services.items():
            health = self.get_service_health(service_info["host"], service_info["port"])
            service_info["health"] = health
            service_info["last_checked"] = time.time()
            updated_services[service_key] = service_info
        
        self.discovered_services = updated_services
        
        return {
            "success": True,
            "services": updated_services,
            "updated_count": len(updated_services)
        }
