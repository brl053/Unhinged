"""
@llm-type contract
@llm-legend Language-specific build modules for enhanced build orchestration
@llm-key Provides specialized builders for Kotlin, TypeScript, Python, and Protobuf with caching and optimization
@llm-map Build module system that integrates with main orchestrator for multi-language support
@llm-axiom Each language builder must provide consistent interface and caching capabilities
@llm-contract All builders implement BuildModule interface with build, cache, and validate methods
@llm-token build-modules: Specialized build handlers for different programming languages

Enhanced Build Modules Package

Provides language-specific build modules that integrate with the main build orchestrator
to provide optimized, cached, and parallel builds for different technologies.

Modules:
- kotlin_builder: Gradle-based Kotlin/JVM builds with incremental compilation
- typescript_builder: npm/webpack-based TypeScript builds with hot reloading
- python_builder: pip/poetry-based Python builds with virtual environment management
- protobuf_builder: Multi-language protobuf generation with smart caching
- docker_builder: Container build optimization with layer caching

Author: Unhinged Team
Version: 2.0.0
Date: 2025-10-19
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

@dataclass
class BuildContext:
    """Context information for build operations"""
    project_root: Path
    target_name: str
    config: Dict[str, Any]
    cache_enabled: bool = True
    parallel: bool = True
    incremental: bool = True
    environment: str = "development"  # development, staging, production

@dataclass
class BuildArtifact:
    """Represents a build artifact"""
    path: Path
    type: str  # jar, js, py, proto, docker
    size: int
    checksum: str
    metadata: Dict[str, Any]

@dataclass
class BuildModuleResult:
    """Result from a build module operation"""
    success: bool
    duration: float
    artifacts: List[BuildArtifact]
    cache_hit: bool = False
    error_message: Optional[str] = None
    warnings: List[str] = None
    metrics: Dict[str, Any] = None

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
        if self.metrics is None:
            self.metrics = {}

class BuildModule(ABC):
    """Abstract base class for language-specific build modules"""
    
    def __init__(self, context: BuildContext):
        self.context = context
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    def can_handle(self, target_name: str) -> bool:
        """Check if this module can handle the given target"""
        pass
    
    @abstractmethod
    def get_dependencies(self, target_name: str) -> List[str]:
        """Get list of file dependencies for the target"""
        pass
    
    @abstractmethod
    def calculate_cache_key(self, target_name: str) -> str:
        """Calculate cache key for the target"""
        pass
    
    @abstractmethod
    def build(self, target_name: str) -> BuildModuleResult:
        """Execute the build for the target"""
        pass
    
    @abstractmethod
    def clean(self, target_name: str) -> bool:
        """Clean build artifacts for the target"""
        pass
    
    def validate_environment(self) -> List[str]:
        """Validate that the build environment is properly configured"""
        return []  # Return list of error messages, empty if valid
    
    def get_estimated_duration(self, target_name: str) -> float:
        """Get estimated build duration in seconds"""
        return 60.0  # Default estimate
    
    def supports_incremental_build(self, target_name: str) -> bool:
        """Check if incremental builds are supported for this target"""
        return False
    
    def supports_parallel_build(self, target_name: str) -> bool:
        """Check if parallel builds are supported for this target"""
        return True

class BuildModuleRegistry:
    """Registry for build modules"""
    
    def __init__(self):
        self.modules: List[BuildModule] = []
    
    def register(self, module: BuildModule):
        """Register a build module"""
        self.modules.append(module)
        logger.info(f"Registered build module: {module.__class__.__name__}")
    
    def get_module_for_target(self, target_name: str) -> Optional[BuildModule]:
        """Get the appropriate build module for a target"""
        for module in self.modules:
            if module.can_handle(target_name):
                return module
        return None
    
    def get_all_modules(self) -> List[BuildModule]:
        """Get all registered modules"""
        return self.modules.copy()

# Global registry instance
registry = BuildModuleRegistry()

def register_module(module: BuildModule):
    """Register a build module with the global registry"""
    registry.register(module)

def get_module_for_target(target_name: str) -> Optional[BuildModule]:
    """Get the appropriate build module for a target"""
    return registry.get_module_for_target(target_name)

# Module-specific utilities
class BuildUtils:
    """Utility functions for build modules"""
    
    @staticmethod
    def calculate_file_hash(file_path: Path) -> str:
        """Calculate SHA256 hash of a file"""
        import hashlib
        hasher = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except IOError:
            return ""
    
    @staticmethod
    def calculate_directory_hash(dir_path: Path, patterns: List[str] = None) -> str:
        """Calculate hash of directory contents"""
        import hashlib
        import fnmatch
        
        hasher = hashlib.sha256()
        
        if not dir_path.exists():
            return ""
        
        # Get all files, optionally filtered by patterns
        files = []
        for file_path in sorted(dir_path.rglob('*')):
            if file_path.is_file():
                if patterns:
                    # Check if file matches any pattern
                    relative_path = str(file_path.relative_to(dir_path))
                    if any(fnmatch.fnmatch(relative_path, pattern) for pattern in patterns):
                        files.append(file_path)
                else:
                    files.append(file_path)
        
        # Hash file paths and contents
        for file_path in files:
            hasher.update(str(file_path.relative_to(dir_path)).encode())
            hasher.update(BuildUtils.calculate_file_hash(file_path).encode())
        
        return hasher.hexdigest()
    
    @staticmethod
    def run_command(command: str, cwd: Path, timeout: int = 300) -> tuple[bool, str, str]:
        """Run a command and return success, stdout, stderr"""
        import subprocess
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", f"Command timed out after {timeout} seconds"
        except Exception as e:
            return False, "", str(e)
    
    @staticmethod
    def check_tool_available(tool_name: str) -> bool:
        """Check if a build tool is available"""
        import shutil
        return shutil.which(tool_name) is not None
    
    @staticmethod
    def get_file_size(file_path: Path) -> int:
        """Get file size in bytes"""
        try:
            return file_path.stat().st_size
        except OSError:
            return 0
    
    @staticmethod
    def create_build_artifact(file_path: Path, artifact_type: str, metadata: Dict[str, Any] = None) -> BuildArtifact:
        """Create a BuildArtifact from a file"""
        if metadata is None:
            metadata = {}
        
        return BuildArtifact(
            path=file_path,
            type=artifact_type,
            size=BuildUtils.get_file_size(file_path),
            checksum=BuildUtils.calculate_file_hash(file_path),
            metadata=metadata
        )

# Export main classes and functions
__all__ = [
    'BuildContext',
    'BuildArtifact', 
    'BuildModuleResult',
    'BuildModule',
    'BuildModuleRegistry',
    'BuildUtils',
    'register_module',
    'get_module_for_target',
    'registry'
]
