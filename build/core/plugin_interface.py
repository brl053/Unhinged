#!/usr/bin/env python3
"""
Plugin Interface for Build System

Defines the standard interface that all language builders must implement.
Based on expert recommendation to formalize plugin architecture with
consistent API contracts.

@llm-type core.plugin-system
@llm-does standardized plugin interface for polyglot build system
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Set, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import hashlib
import time
import logging
import sys

# Add control/gtk4_gui/utils to path for subprocess_utils import
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "control" / "gtk4_gui" / "utils"))

from subprocess_utils import SubprocessRunner

class PluginCapability(Enum):
    """Capabilities that plugins can declare support for."""
    INCREMENTAL_BUILD = "incremental_build"
    PARALLEL_BUILD = "parallel_build"
    DEPENDENCY_RESOLUTION = "dependency_resolution"
    CACHE_OPTIMIZATION = "cache_optimization"
    HOT_RELOAD = "hot_reload"
    TESTING = "testing"
    LINTING = "linting"
    PACKAGING = "packaging"

@dataclass
class FilePattern:
    """File pattern for plugin detection."""
    extension: str
    priority: int = 1  # Higher priority = more specific match
    required_files: List[str] = None  # Files that must exist (e.g., package.json)
    
    def __post_init__(self):
        if self.required_files is None:
            self.required_files = []

@dataclass
class BuildArtifact:
    """Represents a build artifact produced by a plugin."""
    path: Path
    artifact_type: str  # 'executable', 'library', 'package', 'documentation', etc.
    size_bytes: int
    checksum: str
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class PluginResult:
    """Result of a plugin operation."""
    success: bool
    duration: float
    artifacts: List[BuildArtifact]
    warnings: List[str] = None
    error_message: Optional[str] = None
    metrics: Dict[str, Any] = None
    cache_key: Optional[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
        if self.metrics is None:
            self.metrics = {}

@dataclass
class PluginMetadata:
    """Metadata about a plugin."""
    name: str
    version: str
    description: str
    author: str
    supported_extensions: List[str]
    capabilities: Set[PluginCapability]
    dependencies: List[str] = None  # External tool dependencies
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

class BuilderPlugin(ABC):
    """
    Standard interface for language builders.
    
    All language builders must implement this interface to ensure
    consistent behavior and integration with the build orchestrator.
    """
    
    def __init__(self, context: 'BuildContext'):
        self.context = context
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._metadata = None
        self._file_patterns = None
    
    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        pass
    
    @property
    @abstractmethod
    def file_patterns(self) -> List[FilePattern]:
        """Return file patterns this plugin can handle."""
        pass
    
    @abstractmethod
    def detect_files(self, path: Path) -> List[Path]:
        """
        Return list of files this builder handles in the given path.
        
        Args:
            path: Directory to scan for files
            
        Returns:
            List of file paths this plugin can build
        """
        pass
    
    @abstractmethod
    def calculate_checksum(self, file_paths: List[Path]) -> str:
        """
        Calculate content-based checksum for caching.
        
        Args:
            file_paths: List of files to include in checksum
            
        Returns:
            Hex string checksum for cache key generation
        """
        pass
    
    @abstractmethod
    def get_dependencies(self, file_paths: List[Path]) -> List[Path]:
        """
        Get list of file dependencies for the given files.
        
        Args:
            file_paths: Files to analyze for dependencies
            
        Returns:
            List of dependency file paths
        """
        pass
    
    @abstractmethod
    def validate_environment(self) -> List[str]:
        """
        Validate that required tools and environment are available.
        
        Returns:
            List of missing requirements (empty if all good)
        """
        pass
    
    @abstractmethod
    def build(self, file_paths: List[Path], options: Dict[str, Any] = None) -> PluginResult:
        """
        Execute build for given files.
        
        Args:
            file_paths: Files to build
            options: Build options (target-specific configuration)
            
        Returns:
            PluginResult with build outcome
        """
        pass
    
    @abstractmethod
    def clean(self, file_paths: List[Path]) -> PluginResult:
        """
        Remove build artifacts for given files.
        
        Args:
            file_paths: Files whose artifacts should be cleaned
            
        Returns:
            PluginResult with cleanup outcome
        """
        pass
    
    # Optional methods with default implementations
    
    def supports_capability(self, capability: PluginCapability) -> bool:
        """Check if plugin supports a specific capability."""
        return capability in self.metadata.capabilities
    
    def get_estimated_duration(self, file_paths: List[Path], options: Dict[str, Any] = None) -> float:
        """
        Estimate build duration in seconds.
        
        Default implementation returns 30 seconds.
        Plugins should override with more accurate estimates.
        """
        return 30.0
    
    def test(self, file_paths: List[Path], options: Dict[str, Any] = None) -> PluginResult:
        """
        Run tests for given files.
        
        Default implementation returns "not supported".
        Override if plugin supports testing.
        """
        if not self.supports_capability(PluginCapability.TESTING):
            return PluginResult(
                success=False,
                duration=0.0,
                artifacts=[],
                error_message=f"Plugin {self.metadata.name} does not support testing"
            )
        
        # Subclasses should override this
        raise NotImplementedError("Plugin claims to support testing but doesn't implement test()")
    
    def lint(self, file_paths: List[Path], options: Dict[str, Any] = None) -> PluginResult:
        """
        Run linting for given files.
        
        Default implementation returns "not supported".
        Override if plugin supports linting.
        """
        if not self.supports_capability(PluginCapability.LINTING):
            return PluginResult(
                success=False,
                duration=0.0,
                artifacts=[],
                error_message=f"Plugin {self.metadata.name} does not support linting"
            )
        
        # Subclasses should override this
        raise NotImplementedError("Plugin claims to support linting but doesn't implement lint()")
    
    def package(self, file_paths: List[Path], options: Dict[str, Any] = None) -> PluginResult:
        """
        Create distributable package from built files.
        
        Default implementation returns "not supported".
        Override if plugin supports packaging.
        """
        if not self.supports_capability(PluginCapability.PACKAGING):
            return PluginResult(
                success=False,
                duration=0.0,
                artifacts=[],
                error_message=f"Plugin {self.metadata.name} does not support packaging"
            )
        
        # Subclasses should override this
        raise NotImplementedError("Plugin claims to support packaging but doesn't implement package()")
    
    # Utility methods for plugin implementations
    
    def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate SHA-256 checksum of a single file."""
        hasher = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            self.logger.warning(f"Failed to checksum {file_path}: {e}")
            return "error"
    
    def _calculate_combined_checksum(self, file_paths: List[Path]) -> str:
        """Calculate combined checksum for multiple files."""
        hasher = hashlib.sha256()
        
        # Sort paths for consistent ordering
        sorted_paths = sorted(str(p) for p in file_paths)
        
        for path_str in sorted_paths:
            path = Path(path_str)
            if path.exists() and path.is_file():
                # Include file path and content in hash
                hasher.update(path_str.encode('utf-8'))
                file_checksum = self._calculate_file_checksum(path)
                hasher.update(file_checksum.encode('utf-8'))
        
        return hasher.hexdigest()
    
    def _run_command(self, command: str, working_dir: Path, timeout: int = 300) -> Tuple[bool, str, str]:
        """
        Run shell command and return result.

        Args:
            command: Command to execute
            working_dir: Working directory for command
            timeout: Timeout in seconds

        Returns:
            Tuple of (success, stdout, stderr)
        """
        runner = SubprocessRunner(timeout=timeout)
        result = runner.run_shell(command, cwd=working_dir)
        return result["success"], result["output"], result["error"]
    
    def _check_tool_available(self, tool_name: str) -> bool:
        """Check if a command-line tool is available."""
        import shutil
        return shutil.which(tool_name) is not None
