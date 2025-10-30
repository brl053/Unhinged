#!/usr/bin/env python3
"""
C Builder Plugin

Implements the standardized plugin interface for C builds.
Handles C projects using Make or direct compilation.

@llm-type plugin.c
@llm-does c builds with standardized plugin interface
"""

import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Set, Any

try:
    from ..core.plugin_interface import (
        BuilderPlugin, PluginMetadata, PluginCapability, FilePattern, 
        PluginResult, BuildArtifact
    )
    from . import BuildContext, BuildUtils
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from core.plugin_interface import (
        BuilderPlugin, PluginMetadata, PluginCapability, FilePattern, 
        PluginResult, BuildArtifact
    )
    from modules import BuildContext, BuildUtils

class CBuilderPlugin(BuilderPlugin):
    """C builder implementing standardized plugin interface."""
    
    def __init__(self, context: BuildContext):
        super().__init__(context)
        self.compiler = self._detect_compiler()
        self.build_dir = self.context.project_root / "build" / "c"
        self.build_dir.mkdir(parents=True, exist_ok=True)
    
    def _detect_compiler(self) -> str:
        """Detect available C compiler."""
        compilers = ["gcc", "clang", "cc"]
        for compiler in compilers:
            if self._check_tool_available(compiler):
                return compiler
        return "gcc"  # Default fallback
    
    @property
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        return PluginMetadata(
            name="c",
            version="2.0.0",
            description="C builder with Make and direct compilation support",
            author="Unhinged Build System",
            supported_extensions=[".c", ".h"],
            capabilities={
                PluginCapability.INCREMENTAL_BUILD,
                PluginCapability.PARALLEL_BUILD,
                PluginCapability.DEPENDENCY_RESOLUTION,
                PluginCapability.CACHE_OPTIMIZATION,
                PluginCapability.TESTING,
                PluginCapability.PACKAGING
            },
            dependencies=["gcc", "make"]
        )
    
    @property
    def file_patterns(self) -> List[FilePattern]:
        """Return file patterns this plugin can handle."""
        return [
            FilePattern(".c", priority=10, required_files=["Makefile"]),
            FilePattern(".c", priority=8, required_files=["CMakeLists.txt"]),
            FilePattern(".c", priority=5),  # Generic C files
            FilePattern(".h", priority=3)   # Header files
        ]
    
    def detect_files(self, path: Path) -> List[Path]:
        """Return list of C files this builder handles."""
        c_files = []
        
        # Look for C source and header files
        for pattern in ["**/*.c", "**/*.h"]:
            c_files.extend(path.glob(pattern))
        
        # Filter out build directories and other non-source locations
        excluded_dirs = {"build", ".git", "node_modules", "target"}
        
        filtered_files = []
        for file_path in c_files:
            if any(excluded_dir in file_path.parts for excluded_dir in excluded_dirs):
                continue
            filtered_files.append(file_path)
        
        return filtered_files
    
    def calculate_checksum(self, file_paths: List[Path]) -> str:
        """Calculate content-based checksum for caching."""
        return self._calculate_combined_checksum(file_paths)
    
    def get_dependencies(self, file_paths: List[Path]) -> List[Path]:
        """Get list of file dependencies for C files."""
        dependencies = set()
        
        # Add build configuration files
        config_files = [
            Path("Makefile"),
            Path("CMakeLists.txt"),
            Path("configure"),
            Path("configure.ac"),
            Path("Makefile.am")
        ]
        
        for file_path in file_paths:
            project_root = self._find_project_root(file_path)
            for config_file in config_files:
                full_config_path = project_root / config_file
                if full_config_path.exists():
                    dependencies.add(full_config_path)
        
        # Parse #include dependencies
        for file_path in file_paths:
            if file_path.suffix == ".c":
                included_files = self._parse_includes(file_path)
                dependencies.update(included_files)
        
        return list(dependencies)
    
    def _find_project_root(self, file_path: Path) -> Path:
        """Find the project root for a C file."""
        current = file_path.parent
        
        # Look for project indicators
        project_files = ["Makefile", "CMakeLists.txt", "configure"]
        
        while current != self.context.project_root.parent:
            for project_file in project_files:
                if (current / project_file).exists():
                    return current
            current = current.parent
        
        # Default to file's directory
        return file_path.parent
    
    def _parse_includes(self, file_path: Path) -> List[Path]:
        """Parse #include dependencies from a C file."""
        includes = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find #include statements
            include_pattern = r'#include\s*[<"]([^>"]+)[>"]'
            matches = re.findall(include_pattern, content)
            
            base_dir = file_path.parent
            
            for include_file in matches:
                # Look for local header files (not system headers)
                if not include_file.startswith('/'):
                    header_path = base_dir / include_file
                    if header_path.exists():
                        includes.append(header_path)
                    else:
                        # Try relative to project root
                        project_root = self._find_project_root(file_path)
                        header_path = project_root / include_file
                        if header_path.exists():
                            includes.append(header_path)
        
        except Exception as e:
            self.logger.warning(f"Failed to parse includes from {file_path}: {e}")
        
        return includes
    
    def validate_environment(self) -> List[str]:
        """Validate C build environment."""
        missing_requirements = []
        
        # Check C compiler
        if not self._check_tool_available(self.compiler):
            missing_requirements.append(f"C compiler ({self.compiler})")
        
        # Check make
        if not self._check_tool_available("make"):
            missing_requirements.append("make")
        
        return missing_requirements
    
    def build(self, file_paths: List[Path], options: Dict[str, Any] = None) -> PluginResult:
        """Execute C build."""
        start_time = time.time()
        options = options or {}
        
        # Validate environment
        env_errors = self.validate_environment()
        if env_errors:
            return PluginResult(
                success=False,
                duration=0.0,
                artifacts=[],
                error_message=f"Environment validation failed: {'; '.join(env_errors)}"
            )
        
        self.logger.info(f"🔨 Building {len(file_paths)} C files")
        
        # Group files by project
        projects = self._group_files_by_project(file_paths)
        
        all_artifacts = []
        all_warnings = []
        
        for project_path, project_files in projects.items():
            self.logger.info(f"📦 Building C project: {project_path}")
            
            # Try Make first, then direct compilation
            if (project_path / "Makefile").exists():
                result = self._build_with_make(project_path, project_files, options)
            else:
                result = self._build_direct(project_path, project_files, options)
            
            if not result.success:
                return result
            
            all_artifacts.extend(result.artifacts)
            all_warnings.extend(result.warnings)
        
        duration = time.time() - start_time
        
        return PluginResult(
            success=True,
            duration=duration,
            artifacts=all_artifacts,
            warnings=all_warnings,
            metrics={
                "files_processed": len(file_paths),
                "projects_built": len(projects),
                "compiler": self.compiler
            }
        )
    
    def _group_files_by_project(self, file_paths: List[Path]) -> Dict[Path, List[Path]]:
        """Group files by their containing project."""
        projects = {}
        
        for file_path in file_paths:
            project_root = self._find_project_root(file_path)
            
            if project_root not in projects:
                projects[project_root] = []
            projects[project_root].append(file_path)
        
        return projects
    
    def _build_with_make(self, project_path: Path, file_paths: List[Path], options: Dict[str, Any]) -> PluginResult:
        """Build using Makefile."""
        start_time = time.time()
        
        # Run make
        make_target = options.get("target", "all")
        command = f"make {make_target}"
        
        success, stdout, stderr = self._run_command(command, project_path, timeout=300)
        
        duration = time.time() - start_time
        
        if not success:
            return PluginResult(
                success=False,
                duration=duration,
                artifacts=[],
                error_message=f"Make build failed: {stderr}"
            )
        
        # Collect build artifacts
        artifacts = self._collect_build_artifacts(project_path)
        warnings = self._extract_warnings(stdout)
        
        return PluginResult(
            success=True,
            duration=duration,
            artifacts=artifacts,
            warnings=warnings
        )
    
    def _build_direct(self, project_path: Path, file_paths: List[Path], options: Dict[str, Any]) -> PluginResult:
        """Build using direct compilation."""
        start_time = time.time()
        artifacts = []
        warnings = []
        
        # Get C source files
        c_files = [f for f in file_paths if f.suffix == ".c"]
        
        if not c_files:
            return PluginResult(
                success=True,
                duration=time.time() - start_time,
                artifacts=[],
                warnings=["No C source files to compile"]
            )
        
        # Compile each C file to object file
        for c_file in c_files:
            obj_file = self.build_dir / f"{c_file.stem}.o"
            
            # Basic compilation command
            command = f"{self.compiler} -c {c_file} -o {obj_file}"
            
            # Add include directories
            include_dirs = options.get("include_dirs", [])
            for include_dir in include_dirs:
                command += f" -I{include_dir}"
            
            # Add compiler flags
            cflags = options.get("cflags", ["-Wall", "-O2"])
            command += f" {' '.join(cflags)}"
            
            success, stdout, stderr = self._run_command(command, project_path)
            
            if not success:
                return PluginResult(
                    success=False,
                    duration=time.time() - start_time,
                    artifacts=[],
                    error_message=f"Compilation failed for {c_file}: {stderr}"
                )
            
            # Create artifact for object file
            if obj_file.exists():
                artifacts.append(BuildArtifact(
                    path=obj_file,
                    artifact_type="object",
                    size_bytes=obj_file.stat().st_size,
                    checksum=self._calculate_file_checksum(obj_file),
                    metadata={"source": str(c_file), "compiler": self.compiler}
                ))
            
            # Extract warnings
            if stderr:
                warnings.extend(stderr.split('\n'))
        
        # Link object files into executable if requested
        if options.get("link", True) and len(c_files) > 0:
            executable = self.build_dir / options.get("output", "program")
            obj_files = [self.build_dir / f"{f.stem}.o" for f in c_files]
            
            command = f"{self.compiler} {' '.join(str(f) for f in obj_files)} -o {executable}"
            
            # Add linker flags
            ldflags = options.get("ldflags", [])
            command += f" {' '.join(ldflags)}"
            
            success, stdout, stderr = self._run_command(command, project_path)
            
            if success and executable.exists():
                artifacts.append(BuildArtifact(
                    path=executable,
                    artifact_type="executable",
                    size_bytes=executable.stat().st_size,
                    checksum=self._calculate_file_checksum(executable),
                    metadata={"sources": [str(f) for f in c_files], "compiler": self.compiler}
                ))
        
        return PluginResult(
            success=True,
            duration=time.time() - start_time,
            artifacts=artifacts,
            warnings=warnings
        )
    
    def _collect_build_artifacts(self, project_path: Path) -> List[BuildArtifact]:
        """Collect build artifacts from Make build."""
        artifacts = []
        
        # Look for common artifact patterns
        artifact_patterns = ["*.o", "*.a", "*.so", "*.exe"]
        
        for pattern in artifact_patterns:
            for artifact_file in project_path.glob(pattern):
                artifact_type = {
                    ".o": "object",
                    ".a": "static_library", 
                    ".so": "shared_library",
                    ".exe": "executable"
                }.get(artifact_file.suffix, "unknown")
                
                artifacts.append(BuildArtifact(
                    path=artifact_file,
                    artifact_type=artifact_type,
                    size_bytes=artifact_file.stat().st_size,
                    checksum=self._calculate_file_checksum(artifact_file),
                    metadata={"language": "c"}
                ))
        
        return artifacts
    
    def _extract_warnings(self, output: str) -> List[str]:
        """Extract warnings from compiler output."""
        warnings = []
        
        for line in output.split('\n'):
            line = line.strip()
            if 'warning:' in line.lower():
                warnings.append(line)
        
        return warnings
    
    def clean(self, file_paths: List[Path]) -> PluginResult:
        """Clean C build artifacts."""
        start_time = time.time()
        
        # Group files by project and clean each
        projects = self._group_files_by_project(file_paths)
        cleaned_count = 0
        
        for project_path, _ in projects.items():
            if (project_path / "Makefile").exists():
                # Use make clean
                success, stdout, stderr = self._run_command("make clean", project_path)
                if success:
                    cleaned_count += 1
            else:
                # Remove object files manually
                for obj_file in project_path.glob("*.o"):
                    obj_file.unlink()
                    cleaned_count += 1
        
        # Clean build directory
        if self.build_dir.exists():
            import shutil
            shutil.rmtree(self.build_dir)
            self.build_dir.mkdir(parents=True, exist_ok=True)
        
        return PluginResult(
            success=True,
            duration=time.time() - start_time,
            artifacts=[],
            metrics={"projects_cleaned": cleaned_count}
        )
    
    def test(self, file_paths: List[Path], options: Dict[str, Any] = None) -> PluginResult:
        """Run C tests."""
        start_time = time.time()
        
        # Look for test files
        test_files = [f for f in file_paths if "test" in f.name.lower()]
        
        if not test_files:
            return PluginResult(
                success=True,
                duration=time.time() - start_time,
                artifacts=[],
                warnings=["No test files found"]
            )
        
        # Build and run tests
        test_results = {"tests_run": 0, "tests_passed": 0, "tests_failed": 0}
        
        for test_file in test_files:
            # Compile test
            test_exe = self.build_dir / f"{test_file.stem}_test"
            command = f"{self.compiler} {test_file} -o {test_exe}"
            
            success, stdout, stderr = self._run_command(command, test_file.parent)
            
            if success and test_exe.exists():
                # Run test
                success, stdout, stderr = self._run_command(str(test_exe), test_file.parent)
                test_results["tests_run"] += 1
                
                if success:
                    test_results["tests_passed"] += 1
                else:
                    test_results["tests_failed"] += 1
        
        return PluginResult(
            success=test_results["tests_failed"] == 0,
            duration=time.time() - start_time,
            artifacts=[],
            metrics=test_results
        )
