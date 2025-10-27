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
- mobile_ui_builder: Mobile-responsive UI framework with CSS generation and validation
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

    @staticmethod
    def validate_build_patterns(repo_root: Path) -> List[str]:
        """
        @llm-type validation
        @llm-legend Validate build system patterns and cultural commandments
        @llm-key Checks for scattered files, proper generated content location, and cultural compliance
        @llm-map Integrated enforcement that runs as part of build validation
        @llm-axiom Build validation must prevent chaos and maintain architectural integrity
        @llm-contract Returns list of violations, empty list means all patterns are valid
        @llm-token build-validation: Pattern enforcement integrated into build system

        Validate that build patterns are followed:
        - No scattered build files in root
        - Generated content in /generated/
        - No backup/temp files
        - Proper use of centralized Python environment
        """
        violations = []

        try:
            # Check for forbidden files in root
            forbidden_patterns = ["*.py", "*.js", "*.ts", "*.sh", "demo_*", "test_*", "*.backup*"]
            allowed_root_files = {"requirements.txt", "Makefile", "README.md", "build-config.yml", ".gitignore"}

            for pattern in forbidden_patterns:
                for match in repo_root.glob(pattern):
                    if match.is_file() and match.name not in allowed_root_files:
                        violations.append(f"Forbidden file in root: {match.name}")

            # Check for scattered build files
            scattered_files = ["gradlew", "package.json", "build.gradle"]
            for root_dir in repo_root.iterdir():
                if root_dir.is_dir() and root_dir.name not in {"build", "generated", ".git"}:
                    for scattered_file in scattered_files:
                        if (root_dir / scattered_file).exists():
                            violations.append(f"Scattered build file: {root_dir.name}/{scattered_file}")
        except Exception as e:
            violations.append(f"Validation error: {str(e)}")

        return violations

# Auto-register available build modules
def _auto_register_modules():
    """Automatically register available build modules"""
    # Create dummy context for registration
    dummy_context = BuildContext(
        project_root=Path.cwd(),
        target_name="dummy",
        config={}
    )

    # Try to register each module individually
    modules_to_register = [
        ('python_builder', 'PythonBuilder'),
        ('kotlin_builder', 'KotlinBuilder'),
        ('c_builder', 'CBuilder'),
        ('dual_system_builder', 'DualSystemBuilder'),
        ('design_token_builder', 'DesignTokenBuilder'),
    ]

    for module_name, class_name in modules_to_register:
        try:
            if module_name == 'python_builder':
                from .python_builder import PythonBuilder
                register_module(PythonBuilder(dummy_context))
            elif module_name == 'kotlin_builder':
                from .kotlin_builder import KotlinBuilder
                register_module(KotlinBuilder(dummy_context))
            elif module_name == 'c_builder':
                from .c_builder import CBuilder
                register_module(CBuilder(dummy_context))
            elif module_name == 'dual_system_builder':
                from .dual_system_builder import DualSystemBuilder
                register_module(DualSystemBuilder(dummy_context))
            elif module_name == 'design_token_builder':
                # Import from design system build directory
                import sys
                design_system_path = dummy_context.project_root / "libs" / "design_system" / "build"
                sys.path.insert(0, str(design_system_path))
                from design_token_builder import DesignTokenBuilder
                register_module(DesignTokenBuilder(dummy_context))
        except (ImportError, AttributeError) as e:
            # Module not available, skip silently
            logger.debug(f"Could not register {class_name}: {e}")

# Auto-register modules on import
_auto_register_modules()

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
