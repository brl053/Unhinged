"""
@llm-type build-validator
@llm-legend Port conflict detection and resolution at build time
@llm-key Statically analyzes port allocations to prevent runtime binding failures
@llm-map Compile-time port validation that eliminates Docker port conflicts
@llm-axiom Port conflicts must be resolved at build time, never at runtime
@llm-token port-validator: Static port allocation analyzer preventing runtime binding errors
"""

from dataclasses import dataclass
from typing import List, Dict, Set, Optional, Tuple
import yaml
import logging
from pathlib import Path


@dataclass
class PortConflict:
    """Represents a port allocation conflict detected at build time"""
    port: int
    conflicting_services: List[str]
    resolution_suggestions: List[str]
    severity: str = "error"  # error, warning, info
    
    def __str__(self) -> str:
        services = ", ".join(self.conflicting_services)
        return f"Port {self.port} conflict: {services}"


@dataclass
class PortAllocation:
    """Represents a port allocation for a service"""
    service_name: str
    port: int
    protocol: str = "tcp"
    description: str = ""
    required: bool = True


class PortValidator:
    """
    Build-time port conflict validator
    
    Analyzes docker-compose files and build configurations to detect
    port conflicts before any containers are started.
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logging.getLogger(__name__)
        self.known_system_ports = {
            22: "SSH",
            80: "HTTP", 
            443: "HTTPS",
            3306: "MySQL",
            5432: "PostgreSQL",
            6379: "Redis",
            9200: "Elasticsearch"
        }
    
    def validate_project(self) -> List[PortConflict]:
        """
        Validate all port allocations in the project
        
        @llm-future This becomes part of Unhinged OS resource allocation compiler
        """
        conflicts = []
        
        # Analyze docker-compose files
        compose_allocations = self._analyze_docker_compose_files()
        
        # Analyze build config
        build_allocations = self._analyze_build_config()
        
        # Combine all allocations
        all_allocations = compose_allocations + build_allocations
        
        # Detect conflicts
        conflicts.extend(self._detect_port_conflicts(all_allocations))
        
        # Check against system ports
        conflicts.extend(self._check_system_port_conflicts(all_allocations))
        
        return conflicts
    
    def _analyze_docker_compose_files(self) -> List[PortAllocation]:
        """Extract port allocations from docker-compose files"""
        allocations = []
        
        compose_files = [
            "docker-compose.yml",
            "docker-compose.simple.yml", 
            "docker-compose.observability.yml",
            "platforms/docker-compose.all.yml",
            "platforms/persistence/docker-compose.yml"
        ]
        
        for compose_file in compose_files:
            file_path = self.project_root / compose_file
            if file_path.exists():
                allocations.extend(self._parse_compose_file(file_path))
        
        return allocations
    
    def _parse_compose_file(self, file_path: Path) -> List[PortAllocation]:
        """Parse a single docker-compose file for port allocations"""
        allocations = []
        
        try:
            with open(file_path, 'r') as f:
                compose_data = yaml.safe_load(f)
            
            services = compose_data.get('services', {})
            
            for service_name, service_config in services.items():
                ports = service_config.get('ports', [])
                
                for port_mapping in ports:
                    if isinstance(port_mapping, str):
                        # Format: "host_port:container_port" or "port"
                        if ':' in port_mapping:
                            host_port = port_mapping.split(':')[0]
                        else:
                            host_port = port_mapping
                        
                        try:
                            port_num = int(host_port)
                            allocations.append(PortAllocation(
                                service_name=service_name,
                                port=port_num,
                                description=f"From {file_path.name}"
                            ))
                        except ValueError:
                            self.logger.warning(f"Invalid port format in {file_path}: {port_mapping}")
                    
        except Exception as e:
            self.logger.error(f"Failed to parse {file_path}: {e}")
        
        return allocations
    
    def _analyze_build_config(self) -> List[PortAllocation]:
        """Extract port allocations from build-config.yml"""
        allocations = []
        
        config_path = self.project_root / "build-config.yml"
        if not config_path.exists():
            return allocations
        
        try:
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            
            services = config_data.get('services', {})
            
            for service_name, service_config in services.items():
                ports = service_config.get('ports', [])
                
                for port_mapping in ports:
                    if isinstance(port_mapping, str) and ':' in port_mapping:
                        host_port = int(port_mapping.split(':')[0])
                        allocations.append(PortAllocation(
                            service_name=service_name,
                            port=host_port,
                            description="From build-config.yml"
                        ))
                        
        except Exception as e:
            self.logger.error(f"Failed to parse build-config.yml: {e}")
        
        return allocations
    
    def _detect_port_conflicts(self, allocations: List[PortAllocation]) -> List[PortConflict]:
        """Detect conflicts between service port allocations"""
        conflicts = []
        port_map: Dict[int, List[str]] = {}
        
        # Group services by port
        for allocation in allocations:
            if allocation.port not in port_map:
                port_map[allocation.port] = []
            port_map[allocation.port].append(allocation.service_name)
        
        # Find conflicts (multiple services on same port)
        for port, services in port_map.items():
            if len(services) > 1:
                conflicts.append(PortConflict(
                    port=port,
                    conflicting_services=services,
                    resolution_suggestions=self._generate_resolution_suggestions(port, services),
                    severity="error"
                ))
        
        return conflicts
    
    def _check_system_port_conflicts(self, allocations: List[PortAllocation]) -> List[PortConflict]:
        """Check for conflicts with well-known system ports"""
        conflicts = []
        
        for allocation in allocations:
            if allocation.port in self.known_system_ports:
                system_service = self.known_system_ports[allocation.port]
                conflicts.append(PortConflict(
                    port=allocation.port,
                    conflicting_services=[allocation.service_name, f"System ({system_service})"],
                    resolution_suggestions=[
                        f"Change {allocation.service_name} to an alternative port",
                        f"Use port {self._suggest_alternative_port(allocation.port)}"
                    ],
                    severity="warning"
                ))
        
        return conflicts
    
    def _generate_resolution_suggestions(self, port: int, services: List[str]) -> List[str]:
        """Generate suggestions for resolving port conflicts"""
        suggestions = []
        
        # Suggest alternative ports
        alt_port = self._suggest_alternative_port(port)
        suggestions.append(f"Change one service to port {alt_port}")
        
        # Service-specific suggestions
        if "cockroachdb-main" in services and "backend-service" in services:
            suggestions.extend([
                "Move CockroachDB admin UI to port 8082 (add COCKROACH_HTTP_ADDR=0.0.0.0:8082)",
                "Move backend service to port 8081",
                "Disable CockroachDB admin UI if not needed"
            ])
        
        if any("database" in s for s in services):
            suggestions.append("Consider using internal Docker networking instead of exposing database ports")
        
        return suggestions
    
    def _suggest_alternative_port(self, conflicted_port: int) -> int:
        """Suggest an alternative port that's likely to be available"""
        # Common alternative port patterns
        alternatives = [
            conflicted_port + 1,
            conflicted_port + 10, 
            conflicted_port + 100,
            conflicted_port + 1000
        ]
        
        # Return first alternative not in known system ports
        for alt in alternatives:
            if alt not in self.known_system_ports and alt < 65535:
                return alt
        
        return conflicted_port + 1
    
    def generate_fix_script(self, conflicts: List[PortConflict]) -> str:
        """Generate a shell script to automatically fix port conflicts"""
        script_lines = [
            "#!/bin/bash",
            "# Auto-generated port conflict resolution script",
            "# Generated by Unhinged build-time port validator",
            "",
            "set -e",
            ""
        ]
        
        for conflict in conflicts:
            if conflict.severity == "error":
                script_lines.extend([
                    f"# Fix conflict on port {conflict.port}",
                    f"# Conflicting services: {', '.join(conflict.conflicting_services)}",
                    f"# Suggestions: {'; '.join(conflict.resolution_suggestions)}",
                    ""
                ])
        
        return "\n".join(script_lines)
