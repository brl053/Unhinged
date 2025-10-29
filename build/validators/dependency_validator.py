"""
@llm-type util.validator
@llm-does dependency validation and conflict resolution across package managers
@llm-rule dependency conflicts must be resolved at build time to prevent runtime failures
"""

from dataclasses import dataclass
from typing import List, Dict, Set, Optional
import yaml
from pathlib import Path
import logging


@dataclass
class DependencyIssue:
    """Represents a dependency issue detected at build time"""
    service: str
    issue_type: str  # circular, missing, invalid
    description: str
    resolution_suggestions: List[str]
    severity: str = "error"


class DependencyValidator:
    """
    Build-time dependency validator
    
    Analyzes service dependencies to detect circular dependencies,
    missing services, and invalid dependency chains.
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logging.getLogger(__name__)
    
    def validate_dependencies(self) -> List[DependencyIssue]:
        """
        Validate all service dependencies in the project
        
        @llm-future This becomes part of Unhinged OS service orchestration compiler
        """
        issues = []
        
        # Extract dependency graph from docker-compose files
        dependency_graph = self._build_dependency_graph()
        
        # Check for circular dependencies
        issues.extend(self._detect_circular_dependencies(dependency_graph))
        
        # Check for missing dependencies
        issues.extend(self._detect_missing_dependencies(dependency_graph))
        
        # Validate dependency chains
        issues.extend(self._validate_dependency_chains(dependency_graph))
        
        return issues
    
    def _build_dependency_graph(self) -> Dict[str, List[str]]:
        """Build dependency graph from docker-compose files"""
        graph = {}
        
        compose_files = [
            "docker-compose.yml",
            "docker-compose.simple.yml",
            "docker-compose.observability.yml"
        ]
        
        for compose_file in compose_files:
            file_path = self.project_root / compose_file
            if file_path.exists():
                self._parse_dependencies_from_compose(file_path, graph)
        
        return graph
    
    def _parse_dependencies_from_compose(self, file_path: Path, graph: Dict[str, List[str]]):
        """Parse dependencies from a docker-compose file"""
        try:
            with open(file_path, 'r') as f:
                compose_data = yaml.safe_load(f)
            
            services = compose_data.get('services', {})
            
            for service_name, service_config in services.items():
                dependencies = []
                
                # depends_on dependencies
                depends_on = service_config.get('depends_on', [])
                if isinstance(depends_on, list):
                    dependencies.extend(depends_on)
                elif isinstance(depends_on, dict):
                    dependencies.extend(depends_on.keys())
                
                # links dependencies (deprecated but still used)
                links = service_config.get('links', [])
                for link in links:
                    if ':' in link:
                        dep_service = link.split(':')[0]
                    else:
                        dep_service = link
                    dependencies.append(dep_service)
                
                graph[service_name] = dependencies
                
        except Exception as e:
            self.logger.error(f"Failed to parse dependencies from {file_path}: {e}")
    
    def _detect_circular_dependencies(self, graph: Dict[str, List[str]]) -> List[DependencyIssue]:
        """Detect circular dependencies using DFS"""
        issues = []
        visited = set()
        rec_stack = set()
        
        def dfs(service: str, path: List[str]) -> Optional[List[str]]:
            if service in rec_stack:
                # Found cycle
                cycle_start = path.index(service)
                return path[cycle_start:] + [service]
            
            if service in visited:
                return None
            
            visited.add(service)
            rec_stack.add(service)
            
            for dependency in graph.get(service, []):
                cycle = dfs(dependency, path + [service])
                if cycle:
                    return cycle
            
            rec_stack.remove(service)
            return None
        
        for service in graph:
            if service not in visited:
                cycle = dfs(service, [])
                if cycle:
                    issues.append(DependencyIssue(
                        service=service,
                        issue_type="circular",
                        description=f"Circular dependency detected: {' -> '.join(cycle)}",
                        resolution_suggestions=[
                            "Remove one dependency from the cycle",
                            "Use init containers or health checks instead of depends_on",
                            "Restructure services to eliminate circular dependency"
                        ]
                    ))
        
        return issues
    
    def _detect_missing_dependencies(self, graph: Dict[str, List[str]]) -> List[DependencyIssue]:
        """Detect dependencies that reference non-existent services"""
        issues = []
        all_services = set(graph.keys())
        
        for service, dependencies in graph.items():
            for dependency in dependencies:
                if dependency not in all_services:
                    issues.append(DependencyIssue(
                        service=service,
                        issue_type="missing",
                        description=f"Service '{service}' depends on non-existent service '{dependency}'",
                        resolution_suggestions=[
                            f"Add service '{dependency}' to docker-compose.yml",
                            f"Remove dependency on '{dependency}' from '{service}'",
                            f"Check if '{dependency}' is defined in a different compose file"
                        ]
                    ))
        
        return issues
    
    def _validate_dependency_chains(self, graph: Dict[str, List[str]]) -> List[DependencyIssue]:
        """Validate dependency chains for potential issues"""
        issues = []
        
        # Check for very long dependency chains (potential performance issue)
        for service in graph:
            chain_length = self._calculate_max_chain_length(service, graph)
            if chain_length > 5:
                issues.append(DependencyIssue(
                    service=service,
                    issue_type="long_chain",
                    description=f"Service '{service}' has a dependency chain of length {chain_length}",
                    resolution_suggestions=[
                        "Consider flattening the dependency hierarchy",
                        "Use parallel startup where possible",
                        "Review if all dependencies are truly necessary"
                    ],
                    severity="warning"
                ))
        
        return issues
    
    def _calculate_max_chain_length(self, service: str, graph: Dict[str, List[str]], visited: Set[str] = None) -> int:
        """Calculate the maximum dependency chain length for a service"""
        if visited is None:
            visited = set()
        
        if service in visited:
            return 0  # Avoid infinite recursion
        
        visited.add(service)
        dependencies = graph.get(service, [])
        
        if not dependencies:
            return 1
        
        max_length = 0
        for dependency in dependencies:
            length = self._calculate_max_chain_length(dependency, graph, visited.copy())
            max_length = max(max_length, length)
        
        return max_length + 1
