
import logging; gui_logger = logging.getLogger(__name__)

"""
Build System Integration

Integrates API development tool with build system for proto generation,
client generation, and service discovery operations.
"""

import sys
import json
import time
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Add build system to path
project_root = Path(__file__).parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root / "build"))

try:
    from orchestrator import BuildOrchestrator
    from modules import BuildContext
    BUILD_SYSTEM_AVAILABLE = True
except ImportError:
    BUILD_SYSTEM_AVAILABLE = False


class BuildStatus(Enum):
    """Build operation status"""
    IDLE = "idle"
    BUILDING = "building"
    SUCCESS = "success"
    FAILED = "failed"
    CACHED = "cached"


@dataclass
class BuildOperation:
    """Represents a build operation"""
    target: str
    status: BuildStatus
    start_time: float
    duration: float = 0.0
    error_message: Optional[str] = None
    artifacts: List[str] = None
    cache_hit: bool = False


class BuildSystemIntegration:
    """
    @llm-type integration-class
    @llm-legend Build system integration for API development tool
    @llm-key Provides integration between API dev tool and build system
    @llm-map Central integration point for build operations in API development workflow
    @llm-axiom Build operations must be non-blocking and provide real-time feedback
    @llm-contract Provides unified interface for proto generation, client generation, and service discovery
    @llm-token BuildSystemIntegration: Build system integration for API development workflow

    Integrates the API development tool with the build system for:
    - Proto file generation and validation
    - gRPC client generation (Python, TypeScript, Kotlin)
    - Service discovery and registry updates
    - Build status monitoring
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.orchestrator = None
        self.build_context = None
        self.current_operations: Dict[str, BuildOperation] = {}
        self.service_registry_cache = {}
        self.proto_clients_cache = {}
        
        # Initialize build system if available
        if BUILD_SYSTEM_AVAILABLE:
            self._initialize_build_system()
        
    
    def _initialize_build_system(self):
        """Initialize build system orchestrator"""
        try:
            config_path = self.project_root / "build" / "config" / "build-config.yml"
            self.orchestrator = BuildOrchestrator(config_path)
            
            self.build_context = BuildContext(
                project_root=self.project_root,
                target_name="",  # Will be set per operation
                config=self.orchestrator.config
            )
            
            
        except Exception as e:
            self.orchestrator = None
    
    def is_available(self) -> bool:
        """Check if build system integration is available"""
        return BUILD_SYSTEM_AVAILABLE and self.orchestrator is not None
    
    def get_proto_files(self) -> Dict[str, Any]:
        """
        @llm-type method
        @llm-legend Get all proto files from build system configuration
        @llm-key Retrieves proto files from build system proto directories
        """
        if not self.is_available():
            return {"success": False, "error": "Build system not available", "proto_files": []}
        
        try:
            proto_files = []
            config = self.orchestrator.config
            
            # Get proto directories from build config
            proto_dirs = []
            if "modules" in config and "proto_client_builder" in config["modules"]:
                proto_config = config["modules"]["proto_client_builder"]["config"]
                proto_dirs = proto_config.get("proto_directories", [])
            
            # Scan proto directories
            for proto_dir_pattern in proto_dirs:
                proto_path = self.project_root / proto_dir_pattern
                if proto_path.exists() and proto_path.is_dir():
                    for proto_file in proto_path.rglob("*.proto"):
                        proto_files.append({
                            "name": proto_file.name,
                            "path": str(proto_file.relative_to(self.project_root)),
                            "absolute_path": str(proto_file),
                            "size": proto_file.stat().st_size,
                            "modified": proto_file.stat().st_mtime,
                            "directory": proto_dir_pattern
                        })
            
            return {
                "success": True,
                "proto_files": proto_files,
                "count": len(proto_files),
                "directories": proto_dirs
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get proto files: {e}",
                "proto_files": []
            }
    
    def generate_proto_clients(self, languages: List[str] = None) -> BuildOperation:
        """
        @llm-type method
        @llm-legend Generate gRPC clients for specified languages
        @llm-key Triggers proto client generation through build system
        """
        if not self.is_available():
            return BuildOperation(
                target="proto-clients",
                status=BuildStatus.FAILED,
                start_time=time.time(),
                error_message="Build system not available"
            )
        
        languages = languages or ["python", "typescript"]
        target = "proto-clients"
        
        # Create build operation
        operation = BuildOperation(
            target=target,
            status=BuildStatus.BUILDING,
            start_time=time.time()
        )
        
        self.current_operations[target] = operation
        
        try:

            # Trigger build through orchestrator
            result = asyncio.run(self.orchestrator.build_target(target))

            # Update operation status
            operation.duration = time.time() - operation.start_time
            operation.cache_hit = result.cache_hit

            if result.success:
                operation.status = BuildStatus.CACHED if result.cache_hit else BuildStatus.SUCCESS
                operation.artifacts = self._get_generated_client_artifacts(languages)
            else:
                operation.status = BuildStatus.FAILED
                operation.error_message = result.error_message
            
            return operation
            
        except Exception as e:
            operation.duration = time.time() - operation.start_time
            operation.status = BuildStatus.FAILED
            operation.error_message = f"Build system error: {e}"
            return operation
    
    def update_service_discovery(self) -> BuildOperation:
        """
        @llm-type method
        @llm-legend Update service discovery registry
        @llm-key Triggers service discovery build to refresh service registry
        """
        if not self.is_available():
            return BuildOperation(
                target="service-discovery",
                status=BuildStatus.FAILED,
                start_time=time.time(),
                error_message="Build system not available"
            )
        
        target = "service-discovery"
        
        # Create build operation
        operation = BuildOperation(
            target=target,
            status=BuildStatus.BUILDING,
            start_time=time.time()
        )
        
        self.current_operations[target] = operation
        
        try:

            # Trigger build through orchestrator
            result = asyncio.run(self.orchestrator.build_target(target))

            # Update operation status
            operation.duration = time.time() - operation.start_time
            operation.cache_hit = result.cache_hit

            if result.success:
                operation.status = BuildStatus.CACHED if result.cache_hit else BuildStatus.SUCCESS
                operation.artifacts = self._get_service_discovery_artifacts()

                # Update service registry cache
                self._update_service_registry_cache()

            else:
                operation.status = BuildStatus.FAILED
                operation.error_message = result.error_message
            
            return operation
            
        except Exception as e:
            operation.duration = time.time() - operation.start_time
            operation.status = BuildStatus.FAILED
            operation.error_message = f"Build system error: {e}"
            return operation
    
    def get_service_registry(self) -> Dict[str, Any]:
        """
        @llm-type method
        @llm-legend Get current service registry from build system
        @llm-key Retrieves service registry generated by service discovery builder
        """
        try:
            registry_file = self.project_root / "generated" / "service-registry.js"
            topology_file = self.project_root / "generated" / "service-topology.json"
            health_file = self.project_root / "generated" / "health-endpoints.json"
            
            registry_data = {}
            
            # Load service topology if available
            if topology_file.exists():
                with open(topology_file, 'r') as f:
                    registry_data["topology"] = json.load(f)
            
            # Load health endpoints if available
            if health_file.exists():
                with open(health_file, 'r') as f:
                    registry_data["health_endpoints"] = json.load(f)
            
            # Parse JavaScript registry file for service data
            if registry_file.exists():
                registry_content = registry_file.read_text()
                # Extract service data from JavaScript (simplified parsing)
                registry_data["registry_available"] = True
                registry_data["registry_file"] = str(registry_file)
            else:
                registry_data["registry_available"] = False
            
            return {
                "success": True,
                "registry": registry_data,
                "last_updated": registry_file.stat().st_mtime if registry_file.exists() else None
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get service registry: {e}",
                "registry": {}
            }
    
    def _get_generated_client_artifacts(self, languages: List[str]) -> List[str]:
        """Get list of generated client artifacts"""
        artifacts = []
        clients_dir = self.project_root / "generated" / "clients"
        
        if clients_dir.exists():
            for lang in languages:
                lang_dir = clients_dir / lang
                if lang_dir.exists():
                    for artifact in lang_dir.rglob("*"):
                        if artifact.is_file():
                            artifacts.append(str(artifact.relative_to(self.project_root)))
        
        return artifacts
    
    def _get_service_discovery_artifacts(self) -> List[str]:
        """Get list of service discovery artifacts"""
        artifacts = []
        generated_dir = self.project_root / "generated"
        
        artifact_files = [
            "service-registry.js",
            "service-topology.json", 
            "health-endpoints.json"
        ]
        
        for artifact_file in artifact_files:
            artifact_path = generated_dir / artifact_file
            if artifact_path.exists():
                artifacts.append(str(artifact_path.relative_to(self.project_root)))
        
        return artifacts
    
    def _update_service_registry_cache(self):
        """Update internal service registry cache"""
        try:
            registry_data = self.get_service_registry()
            if registry_data["success"]:
                self.service_registry_cache = registry_data["registry"]
        except Exception as e:
            pass

    def get_build_status(self, target: str) -> Optional[BuildOperation]:
        """Get current build status for a target"""
        return self.current_operations.get(target)
    
    def get_all_build_operations(self) -> Dict[str, BuildOperation]:
        """Get all current build operations"""
        return self.current_operations.copy()
    
    def clear_completed_operations(self):
        """Clear completed build operations"""
        completed = [
            target for target, op in self.current_operations.items()
            if op.status in [BuildStatus.SUCCESS, BuildStatus.FAILED, BuildStatus.CACHED]
        ]
        
        for target in completed:
            del self.current_operations[target]
        
