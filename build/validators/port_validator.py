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
            "# Run this script to automatically resolve detected port conflicts",
            "",
            "set -e",
            "",
            "echo '🔧 Unhinged Port Conflict Auto-Fix Script'",
            "echo '========================================='",
            "echo ''",
            ""
        ]

        backup_commands = []
        fix_commands = []

        for conflict in conflicts:
            if conflict.severity == "error":
                script_lines.extend([
                    f"echo '🔍 Fixing port {conflict.port} conflict...'",
                    f"echo 'Conflicting services: {', '.join(conflict.conflicting_services)}'",
                    ""
                ])

                # Generate specific fixes based on conflict type
                if conflict.port == 8080 and "backend" in conflict.conflicting_services and "database" in conflict.conflicting_services:
                    backup_commands.extend([
                        "# Backup original docker-compose files",
                        "cp docker-compose.yml docker-compose.yml.backup.$(date +%Y%m%d_%H%M%S)",
                    ])

                    fix_commands.extend([
                        "# Fix port 8080 conflict: Move CockroachDB admin UI to 8082",
                        "sed -i 's/8080:8080/8082:8080/g' docker-compose.yml",
                        "echo 'CockroachDB admin UI moved to port 8082'",
                        ""
                    ])

                elif conflict.port == 3000 and "frontend" in conflict.conflicting_services and "grafana" in conflict.conflicting_services:
                    fix_commands.extend([
                        "# Fix port 3000 conflict: Move Grafana to 3001",
                        "sed -i 's/3000:3000/3001:3000/g' docker-compose.yml",
                        "echo 'Grafana moved to port 3001'",
                        ""
                    ])

                elif conflict.port == 8081:
                    fix_commands.extend([
                        "# Fix port 8081 conflict: Move cdc-service to 8083",
                        "sed -i 's/8081:8081/8083:8081/g' docker-compose.yml",
                        "echo 'CDC service moved to port 8083'",
                        ""
                    ])

                elif conflict.port == 9000:
                    fix_commands.extend([
                        "# Fix port 9000 conflict: Move MinIO to 9002",
                        "sed -i 's/9000:9000/9002:9000/g' docker-compose.yml",
                        "echo 'MinIO moved to port 9002 (our control proxy needs 9000)'",
                        ""
                    ])

                else:
                    # Generic fix: increment port by 100
                    new_port = conflict.port + 100
                    fix_commands.extend([
                        f"# Generic fix for port {conflict.port}: Move to {new_port}",
                        f"sed -i 's/{conflict.port}:{conflict.port}/{new_port}:{conflict.port}/g' docker-compose.yml",
                        f"echo 'Services moved from port {conflict.port} to {new_port}'",
                        ""
                    ])

        # Add backup commands first
        script_lines.extend(backup_commands)
        script_lines.append("")

        # Add fix commands
        script_lines.extend(fix_commands)

        # Add validation step
        script_lines.extend([
            "echo '✅ Port conflict fixes applied!'",
            "echo ''",
            "echo '🔍 Re-running validation to verify fixes...'",
            "cd build && python build.py validate-ports",
            "",
            "echo '🎉 Port conflict resolution complete!'",
            "echo 'You can now run: make start'",
            ""
        ])

        return "\n".join(script_lines)

    def generate_port_allocation_report(self, allocations: List[PortAllocation]) -> str:
        """Generate a comprehensive port allocation report"""
        report_lines = [
            "# Unhinged Port Allocation Report",
            f"# Generated: {__import__('datetime').datetime.now().isoformat()}",
            "",
            "## Current Port Allocations",
            ""
        ]

        # Group by port
        port_map = {}
        for allocation in allocations:
            if allocation.port not in port_map:
                port_map[allocation.port] = []
            port_map[allocation.port].append(allocation)

        # Sort by port number
        for port in sorted(port_map.keys()):
            services = port_map[port]
            if len(services) > 1:
                report_lines.append(f"⚠️  **Port {port}** - CONFLICT")
            else:
                report_lines.append(f"✅ **Port {port}** - OK")

            for service in services:
                report_lines.append(f"   - {service.service_name} ({service.description})")
            report_lines.append("")

        # Add recommendations
        report_lines.extend([
            "## Recommendations",
            "",
            "### Standard Port Ranges",
            "- **Frontend Services**: 3000-3099",
            "- **Backend APIs**: 8000-8099",
            "- **Databases**: 5400-5499",
            "- **Message Queues**: 9090-9199",
            "- **Monitoring**: 9200-9299",
            "- **Admin UIs**: 8100-8199",
            "",
            "### Conflict Resolution Priority",
            "1. Move admin UIs to higher ports (8100+)",
            "2. Keep core services on standard ports",
            "3. Use internal Docker networking where possible",
            ""
        ])

        return "\n".join(report_lines)
