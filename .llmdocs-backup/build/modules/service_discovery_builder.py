#!/usr/bin/env python3

"""
@llm-type build-module
@llm-legend Service discovery build module for compile-time service registry generation
@llm-key Discovers Docker and gRPC services at build time, generates static JavaScript registry for system health dashboard
@llm-map Integrates with existing build orchestrator using BuildModule contract for cached service discovery
@llm-axiom Service discovery must happen at build time to ensure HTML dashboard is always up-to-date
@llm-contract Implements BuildModule interface with docker-compose.yml and proto file parsing
@llm-token service-discovery-builder: Build-time service discovery for system health monitoring

Service Discovery Build Module

Discovers services at build time from:
- Docker Compose services (docker-compose.yml)
- gRPC services (proto/*.proto files)
- Health endpoint mappings
- Service dependency topology

Generates static JavaScript registry consumed by system-health.html dashboard.
Follows existing BuildModule contract pattern for consistency and caching.

Author: Unhinged Team
Version: 1.0.0
Date: 2025-10-20
"""

import json
import re
import time
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

try:
    from . import BuildModule, BuildContext, BuildModuleResult, BuildUtils, BuildArtifact
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from __init__ import BuildModule, BuildContext, BuildModuleResult, BuildUtils, BuildArtifact

class ServiceDiscoveryBuilder(BuildModule):
    """
    @llm-type build-module
    @llm-legend Build-time service discovery module following existing BuildModule contract
    @llm-key Parses docker-compose.yml and proto files to generate static service registry
    @llm-map Integrates with build orchestrator for cached, dependency-aware service discovery
    @llm-axiom Service registry must be generated before HTML dashboard access
    @llm-contract Returns BuildModuleResult with service-registry.js artifact
    @llm-token build-time-service-discovery: Compile-time service discovery for health monitoring
    """
    
    def __init__(self, context: BuildContext):
        super().__init__(context)
        self.docker_compose_file = context.project_root / "docker-compose.yml"
        self.proto_dir = context.project_root / "proto"
        self.output_dir = context.project_root / "generated" / "static_html"
        
    def can_handle(self, target_name: str) -> bool:
        """Check if this module can handle the given target"""
        service_discovery_targets = [
            "service-discovery", 
            "system-health", 
            "service-registry",
            "health-dashboard"
        ]
        return target_name in service_discovery_targets
    
    def get_dependencies(self, target_name: str) -> List[str]:
        """Get list of file dependencies for service discovery"""
        dependencies = []
        
        # Docker Compose file
        if self.docker_compose_file.exists():
            dependencies.append(str(self.docker_compose_file.relative_to(self.context.project_root)))
        
        # All proto files
        if self.proto_dir.exists():
            for proto_file in self.proto_dir.rglob("*.proto"):
                dependencies.append(str(proto_file.relative_to(self.context.project_root)))
        
        # Build config
        build_config = self.context.project_root / "build" / "config" / "build-config.yml"
        if build_config.exists():
            dependencies.append(str(build_config.relative_to(self.context.project_root)))
        
        return dependencies
    
    def calculate_cache_key(self, target_name: str) -> str:
        """Calculate cache key based on service definition files"""
        cache_inputs = []
        
        # Hash docker-compose.yml
        if self.docker_compose_file.exists():
            cache_inputs.append(BuildUtils.calculate_file_hash(self.docker_compose_file))
        
        # Hash proto directory
        if self.proto_dir.exists():
            cache_inputs.append(BuildUtils.calculate_directory_hash(
                self.proto_dir, 
                patterns=["*.proto"]
            ))
        
        # Combine all hashes
        import hashlib
        combined_hash = hashlib.sha256()
        for cache_input in cache_inputs:
            combined_hash.update(cache_input.encode())
        
        return combined_hash.hexdigest()
    
    def build(self, target_name: str) -> BuildModuleResult:
        """Execute service discovery and generate registry"""
        start_time = time.time()
        
        try:
            self.logger.info(f"Starting service discovery for target: {target_name}")
            
            # 1. Discover Docker services
            docker_services = self._discover_docker_services()
            self.logger.info(f"Discovered {len(docker_services)} Docker services")
            
            # 2. Discover gRPC services
            grpc_services = self._discover_grpc_services()
            self.logger.info(f"Discovered {len(grpc_services)} gRPC services")
            
            # 3. Map health endpoints
            health_endpoints = self._map_health_endpoints(docker_services, grpc_services)
            self.logger.info(f"Mapped {len(health_endpoints)} health endpoints")
            
            # 4. Build service topology
            topology = self._build_service_topology(docker_services, grpc_services)
            self.logger.info(f"Built topology with {len(topology['nodes'])} nodes, {len(topology['edges'])} edges")
            
            # 5. Generate JavaScript registry
            js_content = self._generate_service_registry_js(
                docker_services, grpc_services, health_endpoints, topology
            )
            
            # 6. Ensure output directory exists
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            # 7. Write registry file
            output_file = self.output_dir / "service-registry.js"
            output_file.write_text(js_content)
            
            # 8. Create build artifact
            artifact = BuildUtils.create_build_artifact(
                output_file,
                "javascript",
                {
                    "docker_services": len(docker_services),
                    "grpc_services": len(grpc_services),
                    "health_endpoints": len(health_endpoints),
                    "topology_nodes": len(topology['nodes']),
                    "topology_edges": len(topology['edges'])
                }
            )
            
            duration = time.time() - start_time
            self.logger.info(f"Service discovery completed in {duration:.3f}s")
            
            return BuildModuleResult(
                success=True,
                duration=duration,
                artifacts=[artifact],
                metrics={
                    "docker_services_count": len(docker_services),
                    "grpc_services_count": len(grpc_services),
                    "health_endpoints_count": len(health_endpoints),
                    "topology_complexity": len(topology['edges'])
                }
            )
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Service discovery failed: {str(e)}"
            self.logger.error(error_msg)
            
            return BuildModuleResult(
                success=False,
                duration=duration,
                artifacts=[],
                error_message=error_msg
            )
    
    def clean(self, target_name: str) -> bool:
        """Clean generated service registry artifacts"""
        try:
            output_file = self.output_dir / "service-registry.js"
            if output_file.exists():
                output_file.unlink()
                self.logger.info("Cleaned service registry artifacts")
            return True
        except Exception as e:
            self.logger.error(f"Failed to clean artifacts: {e}")
            return False
    
    def _discover_docker_services(self) -> Dict[str, Any]:
        """Parse docker-compose.yml to extract service definitions"""
        if not self.docker_compose_file.exists():
            self.logger.warning("docker-compose.yml not found")
            return {}
        
        try:
            with open(self.docker_compose_file) as f:
                compose_data = yaml.safe_load(f)
            
            services = {}
            for service_name, service_config in compose_data.get('services', {}).items():
                services[service_name] = {
                    'name': service_name,
                    'container_name': service_config.get('container_name', service_name),
                    'ports': self._extract_ports(service_config.get('ports', [])),
                    'health_check': service_config.get('healthcheck'),
                    'dependencies': service_config.get('depends_on', []),
                    'environment': service_config.get('environment', {}),
                    'type': self._classify_service_type(service_name, service_config),
                    'image': service_config.get('image', ''),
                    'build': service_config.get('build', {})
                }
            
            return services
            
        except Exception as e:
            self.logger.error(f"Failed to parse docker-compose.yml: {e}")
            return {}
    
    def _extract_ports(self, port_config: List) -> List[Dict]:
        """Extract port mappings from docker-compose port configuration"""
        ports = []
        for port in port_config:
            if isinstance(port, str) and ':' in port:
                host_port, container_port = port.split(':')
                ports.append({
                    'host': int(host_port),
                    'container': int(container_port),
                    'protocol': 'tcp'
                })
            elif isinstance(port, int):
                ports.append({
                    'host': port,
                    'container': port,
                    'protocol': 'tcp'
                })
        return ports
    
    def _classify_service_type(self, name: str, config: Dict) -> str:
        """Classify service type based on name and configuration"""
        name_lower = name.lower()
        
        # Database services
        if any(db in name_lower for db in ['database', 'postgres', 'mysql', 'redis', 'cassandra', 'cockroach']):
            return 'database'
        
        # Vector databases
        if any(vdb in name_lower for vdb in ['weaviate', 'chroma', 'pinecone']):
            return 'vector_database'
        
        # Search engines
        if any(search in name_lower for search in ['elasticsearch', 'solr', 'opensearch']):
            return 'search_engine'
        
        # Streaming services
        if any(stream in name_lower for stream in ['kafka', 'zookeeper', 'flink', 'pulsar']):
            return 'streaming'
        
        # Processing engines
        if any(proc in name_lower for proc in ['spark', 'hadoop', 'storm']):
            return 'processing'
        
        # AI/ML services
        if any(ai in name_lower for ai in ['llm', 'vision', 'speech', 'text-to-speech', 'whisper', 'ollama']):
            return 'ai_ml'
        
        # Application services
        if any(app in name_lower for app in ['backend', 'frontend', 'api', 'service', 'gateway']):
            return 'application'
        
        # Infrastructure
        return 'infrastructure'

    def _discover_grpc_services(self) -> Dict[str, Any]:
        """Parse proto files to extract gRPC service definitions"""
        if not self.proto_dir.exists():
            self.logger.warning("Proto directory not found")
            return {}

        grpc_services = {}

        for proto_file in self.proto_dir.rglob("*.proto"):
            try:
                services_in_file = self._parse_proto_file(proto_file)
                grpc_services.update(services_in_file)
            except Exception as e:
                self.logger.warning(f"Failed to parse {proto_file}: {e}")

        return grpc_services

    def _parse_proto_file(self, proto_file: Path) -> Dict[str, Any]:
        """Extract service definitions from a single proto file"""
        with open(proto_file) as f:
            content = f.read()

        # Extract package name
        package_match = re.search(r'package\s+([^;]+);', content)
        package_name = package_match.group(1) if package_match else ""

        services = {}

        # Extract service definitions
        service_pattern = r'service\s+(\w+)\s*\{([^}]+)\}'
        for service_match in re.finditer(service_pattern, content, re.DOTALL):
            service_name = service_match.group(1)
            service_body = service_match.group(2)

            # Extract RPC methods
            rpc_pattern = r'rpc\s+(\w+)\s*\(([^)]+)\)\s*returns\s*\(([^)]+)\)'
            methods = []
            for rpc_match in re.finditer(rpc_pattern, service_body):
                method_name = rpc_match.group(1)
                request_type = rpc_match.group(2).strip()
                response_type = rpc_match.group(3).strip()

                methods.append({
                    'name': method_name,
                    'request_type': request_type,
                    'response_type': response_type,
                    'is_health_check': self._is_health_method(method_name)
                })

            services[service_name] = {
                'name': service_name,
                'package': package_name,
                'proto_file': str(proto_file.relative_to(self.context.project_root)),
                'methods': methods,
                'health_methods': [m for m in methods if m['is_health_check']]
            }

        return services

    def _is_health_method(self, method_name: str) -> bool:
        """Check if a method is a health check method"""
        health_keywords = ['health', 'heartbeat', 'ping', 'status', 'alive']
        method_lower = method_name.lower()
        return any(keyword in method_lower for keyword in health_keywords)

    def _map_health_endpoints(self, docker_services: Dict, grpc_services: Dict) -> Dict[str, Any]:
        """Map gRPC health methods to Docker service endpoints"""
        health_endpoints = {}

        for service_name, service_info in grpc_services.items():
            if service_info['health_methods']:
                # Find matching Docker service
                docker_service = self._find_matching_docker_service(service_name, docker_services)

                if docker_service:
                    for health_method in service_info['health_methods']:
                        endpoint_key = f"{service_name}.{health_method['name']}"

                        # Get primary port for the service
                        primary_port = self._get_primary_port(docker_service)

                        health_endpoints[endpoint_key] = {
                            'service': service_name,
                            'method': health_method['name'],
                            'docker_service': docker_service['name'],
                            'container_name': docker_service['container_name'],
                            'grpc_endpoint': f"{docker_service['container_name']}:{primary_port}",
                            'http_endpoint': f"http://localhost:{primary_port}",
                            'request_type': health_method['request_type'],
                            'response_type': health_method['response_type'],
                            'port': primary_port
                        }

        return health_endpoints

    def _find_matching_docker_service(self, grpc_service_name: str, docker_services: Dict) -> Optional[Dict]:
        """Find Docker service that likely implements this gRPC service"""
        grpc_lower = grpc_service_name.lower()

        # Direct name matching
        for docker_name, docker_service in docker_services.items():
            docker_lower = docker_name.lower()

            # Exact match
            if grpc_lower == docker_lower:
                return docker_service

            # Partial matching
            if (grpc_lower in docker_lower or
                docker_lower in grpc_lower or
                any(word in docker_lower for word in grpc_lower.split('_')) or
                any(word in grpc_lower for word in docker_lower.split('-'))):
                return docker_service

        # Fallback: match by service type
        service_type_mapping = {
            'audioservice': 'ai_ml',
            'visionservice': 'ai_ml',
            'llmservice': 'ai_ml',
            'chatservice': 'ai_ml',
            'persistenceplatformservice': 'database',
            'observabilityservice': 'infrastructure'
        }

        expected_type = service_type_mapping.get(grpc_lower)
        if expected_type:
            for docker_service in docker_services.values():
                if docker_service['type'] == expected_type:
                    return docker_service

        return None

    def _get_primary_port(self, docker_service: Dict) -> int:
        """Get the primary port for a Docker service"""
        ports = docker_service.get('ports', [])
        if ports:
            return ports[0]['host']

        # Fallback to common ports by service type
        service_type = docker_service.get('type', '')
        type_ports = {
            'ai_ml': 8000,
            'application': 8080,
            'database': 5432,
            'streaming': 9092,
            'search_engine': 9200
        }

        return type_ports.get(service_type, 8080)

    def _build_service_topology(self, docker_services: Dict, grpc_services: Dict) -> Dict[str, Any]:
        """Build complete service dependency graph"""
        topology = {
            'nodes': [],
            'edges': [],
            'layers': {
                'application': [],
                'ai_ml': [],
                'database': [],
                'vector_database': [],
                'search_engine': [],
                'streaming': [],
                'processing': [],
                'infrastructure': []
            }
        }

        # Add Docker services as nodes
        for service_name, service_info in docker_services.items():
            node = {
                'id': service_name,
                'name': service_info['container_name'],
                'type': service_info['type'],
                'ports': service_info['ports'],
                'health_endpoint': self._get_service_health_endpoint(service_name, service_info),
                'status': 'unknown',  # Will be updated at runtime
                'grpc_service': self._find_grpc_service_for_docker(service_name, grpc_services)
            }

            topology['nodes'].append(node)
            topology['layers'][service_info['type']].append(service_name)

            # Add dependency edges
            for dependency in service_info['dependencies']:
                topology['edges'].append({
                    'from': service_name,
                    'to': dependency,
                    'type': 'depends_on'
                })

        return topology

    def _get_service_health_endpoint(self, service_name: str, service_info: Dict) -> Optional[str]:
        """Get health endpoint URL for a service"""
        ports = service_info.get('ports', [])
        if not ports:
            return None

        primary_port = ports[0]['host']

        # Common health check paths by service type
        health_paths = {
            'application': '/health',
            'ai_ml': '/health',
            'database': '/health',
            'search_engine': '/_cluster/health',
            'streaming': '/health',
            'infrastructure': '/health'
        }

        service_type = service_info.get('type', 'application')
        health_path = health_paths.get(service_type, '/health')

        return f"http://localhost:{primary_port}{health_path}"

    def _find_grpc_service_for_docker(self, docker_service_name: str, grpc_services: Dict) -> Optional[str]:
        """Find gRPC service that matches this Docker service"""
        docker_lower = docker_service_name.lower()

        for grpc_name in grpc_services.keys():
            grpc_lower = grpc_name.lower()

            if (grpc_lower in docker_lower or
                docker_lower in grpc_lower or
                any(word in docker_lower for word in grpc_lower.split('_'))):
                return grpc_name

        return None

    def _generate_service_registry_js(self, docker_services: Dict, grpc_services: Dict,
                                    health_endpoints: Dict, topology: Dict) -> str:
        """Generate static JavaScript service registry"""

        js_template = '''// AUTO-GENERATED SERVICE REGISTRY
// Generated at build time by ServiceDiscoveryBuilder
// DO NOT EDIT - This file is regenerated on every build

/**
 * Unhinged Service Registry
 *
 * Contains complete service information discovered at build time:
 * - Docker services from docker-compose.yml
 * - gRPC services from proto files
 * - Health endpoint mappings
 * - Service dependency topology
 *
 * Generated: {build_time}
 * Services: {service_count} Docker, {grpc_count} gRPC
 * Health Endpoints: {health_count}
 */

window.UnhingedServiceRegistry = {{
    // Build metadata
    buildTime: "{build_time}",
    version: "1.0.0",

    // Service counts
    counts: {{
        dockerServices: {docker_count},
        grpcServices: {grpc_count},
        healthEndpoints: {health_count},
        topologyNodes: {topology_nodes},
        topologyEdges: {topology_edges}
    }},

    // Docker Services (from docker-compose.yml)
    dockerServices: {docker_services_json},

    // gRPC Services (from proto files)
    grpcServices: {grpc_services_json},

    // Health Endpoints (mapped from gRPC to Docker)
    healthEndpoints: {health_endpoints_json},

    // Service Topology (dependency graph)
    topology: {topology_json},

    // Helper methods for service discovery
    getServiceByName: function(name) {{
        return this.dockerServices[name] || null;
    }},

    getServicesByType: function(type) {{
        return Object.values(this.dockerServices).filter(s => s.type === type);
    }},

    getHealthEndpoint: function(serviceName) {{
        for (const [key, endpoint] of Object.entries(this.healthEndpoints)) {{
            if (endpoint.service === serviceName || endpoint.docker_service === serviceName) {{
                return endpoint;
            }}
        }}
        return null;
    }},

    getDependencies: function(serviceName) {{
        return this.topology.edges
            .filter(edge => edge.from === serviceName)
            .map(edge => edge.to);
    }},

    getDependents: function(serviceName) {{
        return this.topology.edges
            .filter(edge => edge.to === serviceName)
            .map(edge => edge.from);
    }},

    getServiceLayers: function() {{
        return this.topology.layers;
    }},

    getAllServices: function() {{
        return Object.values(this.dockerServices);
    }},

    getGrpcServiceForDocker: function(dockerServiceName) {{
        const node = this.topology.nodes.find(n => n.id === dockerServiceName);
        return node ? node.grpc_service : null;
    }}
}};

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {{
    module.exports = window.UnhingedServiceRegistry;
}}

// Log registry information
console.log('🔍 Unhinged Service Registry loaded:', {{
    buildTime: window.UnhingedServiceRegistry.buildTime,
    dockerServices: window.UnhingedServiceRegistry.counts.dockerServices,
    grpcServices: window.UnhingedServiceRegistry.counts.grpcServices,
    healthEndpoints: window.UnhingedServiceRegistry.counts.healthEndpoints
}});
'''

        return js_template.format(
            build_time=datetime.now().isoformat(),
            service_count=len(docker_services),
            grpc_count=len(grpc_services),
            health_count=len(health_endpoints),
            docker_count=len(docker_services),
            topology_nodes=len(topology['nodes']),
            topology_edges=len(topology['edges']),
            docker_services_json=json.dumps(docker_services, indent=2),
            grpc_services_json=json.dumps(grpc_services, indent=2),
            health_endpoints_json=json.dumps(health_endpoints, indent=2),
            topology_json=json.dumps(topology, indent=2)
        )
