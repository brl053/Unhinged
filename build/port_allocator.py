#!/usr/bin/env python3
"""
@llm-type infrastructure-tool
@llm-legend Foundational port allocation system for Unhinged architecture
@llm-key Manages systematic port assignment across service categories using safe 1000-1999 range
@llm-map Core infrastructure that eliminates port conflicts through logical categorization
@llm-axiom All services must have predictable, conflict-free port assignments within categorical ranges
@llm-token port-allocator: Production-ready port management with categorical allocation strategy

Unhinged Port Allocation Infrastructure:
- Frontend Services: 1000-1099
- Backend APIs: 1100-1199  
- Databases: 1200-1299
- Vector/AI Stores: 1300-1399
- Message Queues: 1400-1499
- AI/ML Services: 1500-1599
- Admin UIs: 1600-1699
- Storage: 1700-1799
- Observability: 1800-1899
- Platform: 1900-1999
- Gateway (Future): 2000-2099
- Security (Future): 2100-2199
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import yaml
import logging

logger = logging.getLogger(__name__)

@dataclass
class ServicePortMapping:
    """Represents a service's port allocation within the Unhinged architecture"""
    service_name: str
    category: str
    external_port: int
    internal_port: int
    description: str
    docker_compose_files: List[str]

@dataclass
class PortCategory:
    """Defines a port range category with allocation rules"""
    name: str
    range_start: int
    range_end: int
    description: str
    next_available: int

class UnhingedPortAllocator:
    """
    @llm-type infrastructure-manager
    @llm-legend Central port allocation system implementing categorical port assignment
    @llm-key Provides conflict-free port allocation using predefined categorical ranges
    @llm-map Foundation for all Unhinged service port management and docker-compose generation
    @llm-axiom Port allocation must be deterministic, categorical, and conflict-free
    @llm-token port-allocator-core: Systematic port management for microservices architecture
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.categories = self._initialize_port_categories()
        self.service_mappings: Dict[str, ServicePortMapping] = {}
        self._load_current_allocations()
    
    def _initialize_port_categories(self) -> Dict[str, PortCategory]:
        """Initialize the Unhinged port category system"""
        return {
            "frontend": PortCategory("Frontend Services", 1000, 1099, "Web interfaces and user-facing applications", 1000),
            "backend": PortCategory("Backend APIs", 1100, 1199, "REST APIs and application services", 1100),
            "database": PortCategory("Databases", 1200, 1299, "SQL, NoSQL, and graph databases", 1200),
            "vector": PortCategory("Vector/AI Stores", 1300, 1399, "Vector databases and AI data stores", 1300),
            "messaging": PortCategory("Message Queues", 1400, 1499, "Event streaming and message brokers", 1400),
            "ai_ml": PortCategory("AI/ML Services", 1500, 1599, "Machine learning and AI processing", 1500),
            "admin": PortCategory("Admin UIs", 1600, 1699, "Management and administrative interfaces", 1600),
            "storage": PortCategory("Storage", 1700, 1799, "Object storage and file systems", 1700),
            "observability": PortCategory("Observability", 1800, 1899, "Monitoring, logging, and tracing", 1800),
            "platform": PortCategory("Platform Services", 1900, 1999, "Core platform and infrastructure", 1900),
            "gateway": PortCategory("Gateway/Ingress", 2000, 2099, "API gateways and ingress controllers", 2000),
            "security": PortCategory("Security Services", 2100, 2199, "Authentication and security tools", 2100),
        }
    
    def _load_current_allocations(self):
        """Load existing service allocations from the project"""
        # This will be implemented to scan current docker-compose files
        # and build the current state mapping
        pass
    
    def allocate_port(self, service_name: str, category: str, internal_port: int, 
                     description: str = "", preferred_port: Optional[int] = None) -> ServicePortMapping:
        """
        Allocate a port for a service within the specified category
        
        Args:
            service_name: Name of the service
            category: Port category (frontend, backend, database, etc.)
            internal_port: Internal container port
            description: Service description
            preferred_port: Preferred external port (must be within category range)
        
        Returns:
            ServicePortMapping with allocated external port
        """
        if category not in self.categories:
            raise ValueError(f"Unknown port category: {category}")
        
        cat = self.categories[category]
        
        # Use preferred port if specified and available
        if preferred_port:
            if not (cat.range_start <= preferred_port <= cat.range_end):
                raise ValueError(f"Preferred port {preferred_port} outside {category} range {cat.range_start}-{cat.range_end}")
            if self._is_port_available(preferred_port):
                external_port = preferred_port
            else:
                raise ValueError(f"Preferred port {preferred_port} already allocated")
        else:
            # Find next available port in category
            external_port = self._find_next_available_port(category)
        
        # Create mapping
        mapping = ServicePortMapping(
            service_name=service_name,
            category=category,
            external_port=external_port,
            internal_port=internal_port,
            description=description,
            docker_compose_files=[]
        )
        
        self.service_mappings[service_name] = mapping
        self._update_category_next_available(category, external_port + 1)
        
        logger.info(f"✅ Allocated port {external_port} to {service_name} in {category} category")
        return mapping
    
    def _is_port_available(self, port: int) -> bool:
        """Check if a port is available for allocation"""
        return not any(mapping.external_port == port for mapping in self.service_mappings.values())
    
    def _find_next_available_port(self, category: str) -> int:
        """Find the next available port in the specified category"""
        cat = self.categories[category]
        
        for port in range(cat.next_available, cat.range_end + 1):
            if self._is_port_available(port):
                return port
        
        raise RuntimeError(f"No available ports in {category} category ({cat.range_start}-{cat.range_end})")
    
    def _update_category_next_available(self, category: str, next_port: int):
        """Update the next available port for a category"""
        cat = self.categories[category]
        if next_port <= cat.range_end:
            cat.next_available = next_port
    
    def get_service_mapping(self, service_name: str) -> Optional[ServicePortMapping]:
        """Get port mapping for a specific service"""
        return self.service_mappings.get(service_name)
    
    def get_category_allocations(self, category: str) -> List[ServicePortMapping]:
        """Get all port allocations for a specific category"""
        return [mapping for mapping in self.service_mappings.values() if mapping.category == category]
    
    def generate_port_summary(self) -> str:
        """Generate a human-readable summary of port allocations"""
        lines = [
            "# Unhinged Port Allocation Summary",
            f"# Generated: {__import__('datetime').datetime.now().isoformat()}",
            "",
            "## Port Categories",
            ""
        ]
        
        for category_name, category in self.categories.items():
            allocations = self.get_category_allocations(category_name)
            lines.extend([
                f"### {category.name} ({category.range_start}-{category.range_end})",
                f"*{category.description}*",
                ""
            ])
            
            if allocations:
                for mapping in sorted(allocations, key=lambda x: x.external_port):
                    lines.append(f"- **{mapping.service_name}**: {mapping.external_port}:{mapping.internal_port} - {mapping.description}")
                lines.append(f"- *Next available: {category.next_available}*")
            else:
                lines.append(f"- *No allocations (next: {category.next_available})*")
            
            lines.append("")
        
        return "\n".join(lines)
    
    def validate_allocations(self) -> List[str]:
        """Validate current port allocations for conflicts and issues"""
        issues = []
        
        # Check for port conflicts
        used_ports = {}
        for mapping in self.service_mappings.values():
            port = mapping.external_port
            if port in used_ports:
                issues.append(f"Port conflict: {port} used by both {used_ports[port]} and {mapping.service_name}")
            else:
                used_ports[port] = mapping.service_name
        
        # Check for out-of-range allocations
        for mapping in self.service_mappings.values():
            category = self.categories.get(mapping.category)
            if category and not (category.range_start <= mapping.external_port <= category.range_end):
                issues.append(f"Out of range: {mapping.service_name} port {mapping.external_port} outside {mapping.category} range")
        
        return issues


def main():
    """CLI entry point for port allocator"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Unhinged Port Allocation System")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(), help="Project root directory")
    parser.add_argument("--summary", action="store_true", help="Generate port allocation summary")
    parser.add_argument("--validate", action="store_true", help="Validate current allocations")
    
    args = parser.parse_args()
    
    allocator = UnhingedPortAllocator(args.project_root)
    
    if args.summary:
        print(allocator.generate_port_summary())
    
    if args.validate:
        issues = allocator.validate_allocations()
        if issues:
            print("❌ Validation issues found:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("✅ All port allocations valid")


if __name__ == "__main__":
    main()
