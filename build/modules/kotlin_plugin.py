#!/usr/bin/env python3
"""
Kotlin Builder Plugin

Implements the standardized plugin interface for Kotlin builds.
Handles Kotlin projects using Gradle build system.

@llm-type plugin.kotlin
@llm-does kotlin builds with standardized plugin interface
"""

import os
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

class KotlinBuilderPlugin(BuilderPlugin):
    """Kotlin builder implementing standardized plugin interface."""
    
    def __init__(self, context: BuildContext):
        super().__init__(context)
        self.backend_dir = self.context.project_root / "backend"
        self.gradle_wrapper = self.backend_dir / "gradlew"
        self.build_dir = self.backend_dir / "build"
    
    @property
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        return PluginMetadata(
            name="kotlin",
            version="2.0.0",
            description="Kotlin builder with Gradle support",
            author="Unhinged Build System",
            supported_extensions=[".kt", ".kts"],
            capabilities={
                PluginCapability.INCREMENTAL_BUILD,
                PluginCapability.PARALLEL_BUILD,
                PluginCapability.DEPENDENCY_RESOLUTION,
                PluginCapability.CACHE_OPTIMIZATION,
                PluginCapability.TESTING,
                PluginCapability.PACKAGING
            },
            dependencies=["java", "gradle"]
        )
    
    @property
    def file_patterns(self) -> List[FilePattern]:
        """Return file patterns this plugin can handle."""
        return [
            FilePattern(".kt", priority=10, required_files=["build.gradle.kts", "gradlew"]),
            FilePattern(".kt", priority=8, required_files=["build.gradle"]),
            FilePattern(".kt", priority=5),  # Generic Kotlin files
            FilePattern(".kts", priority=7)  # Kotlin script files
        ]
    
    def detect_files(self, path: Path) -> List[Path]:
        """Return list of Kotlin files this builder handles."""
        kotlin_files = []
        
        # Look for Kotlin files
        for pattern in ["**/*.kt", "**/*.kts"]:
            kotlin_files.extend(path.glob(pattern))
        
        # Filter out build directories and other non-source locations
        excluded_dirs = {"build", ".gradle", "node_modules", ".git"}
        
        filtered_files = []
        for file_path in kotlin_files:
            if any(excluded_dir in file_path.parts for excluded_dir in excluded_dirs):
                continue
            filtered_files.append(file_path)
        
        return filtered_files
    
    def calculate_checksum(self, file_paths: List[Path]) -> str:
        """Calculate content-based checksum for caching."""
        return self._calculate_combined_checksum(file_paths)
    
    def get_dependencies(self, file_paths: List[Path]) -> List[Path]:
        """Get list of file dependencies for Kotlin files."""
        dependencies = set()
        
        # Add Gradle build files
        gradle_files = [
            self.backend_dir / "build.gradle.kts",
            self.backend_dir / "build.gradle",
            self.backend_dir / "settings.gradle.kts",
            self.backend_dir / "settings.gradle",
            self.backend_dir / "gradle.properties"
        ]
        
        for gradle_file in gradle_files:
            if gradle_file.exists():
                dependencies.add(gradle_file)
        
        # Add gradle wrapper files
        wrapper_files = [
            self.backend_dir / "gradlew",
            self.backend_dir / "gradlew.bat",
            self.backend_dir / "gradle" / "wrapper" / "gradle-wrapper.properties"
        ]
        
        for wrapper_file in wrapper_files:
            if wrapper_file.exists():
                dependencies.add(wrapper_file)
        
        return list(dependencies)
    
    def validate_environment(self) -> List[str]:
        """Validate Kotlin/Gradle environment."""
        missing_requirements = []
        
        # Check Java
        if not self._check_tool_available("java"):
            missing_requirements.append("java")
        
        # Check Gradle wrapper
        if not self.gradle_wrapper.exists():
            missing_requirements.append("gradle wrapper (gradlew)")
        
        # Check if gradlew is executable
        if self.gradle_wrapper.exists() and not os.access(self.gradle_wrapper, os.X_OK):
            missing_requirements.append("gradle wrapper executable permissions")
        
        return missing_requirements
    
    def build(self, file_paths: List[Path], options: Dict[str, Any] = None) -> PluginResult:
        """Execute Kotlin build."""
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
        
        self.logger.info(f"🔨 Building {len(file_paths)} Kotlin files")
        
        # Determine Gradle task based on options
        gradle_task = options.get("task", "build")
        gradle_args = options.get("args", [])
        
        # Build Gradle command
        command = f"./gradlew {gradle_task}"
        if gradle_args:
            command += f" {' '.join(gradle_args)}"
        
        self.logger.info(f"🔧 Running: {command}")
        
        # Execute build
        success, stdout, stderr = self._run_command(
            command, 
            self.backend_dir,
            timeout=600  # 10 minutes for Kotlin builds
        )
        
        duration = time.time() - start_time
        
        if not success:
            return PluginResult(
                success=False,
                duration=duration,
                artifacts=[],
                error_message=f"Gradle build failed: {stderr}",
                warnings=self._extract_warnings(stdout)
            )
        
        # Collect build artifacts
        artifacts = self._collect_build_artifacts()
        warnings = self._extract_warnings(stdout)
        
        return PluginResult(
            success=True,
            duration=duration,
            artifacts=artifacts,
            warnings=warnings,
            metrics={
                "files_processed": len(file_paths),
                "gradle_task": gradle_task
            }
        )
    
    def _collect_build_artifacts(self) -> List[BuildArtifact]:
        """Collect Kotlin build artifacts."""
        artifacts = []
        
        if not self.build_dir.exists():
            return artifacts
        
        # Look for JAR files
        jar_files = list(self.build_dir.glob("**/*.jar"))
        for jar_file in jar_files:
            artifacts.append(BuildArtifact(
                path=jar_file,
                artifact_type="jar",
                size_bytes=jar_file.stat().st_size,
                checksum=self._calculate_file_checksum(jar_file),
                metadata={"language": "kotlin"}
            ))
        
        # Look for class files
        class_files = list(self.build_dir.glob("**/*.class"))
        for class_file in class_files[:10]:  # Limit to avoid too many artifacts
            artifacts.append(BuildArtifact(
                path=class_file,
                artifact_type="class",
                size_bytes=class_file.stat().st_size,
                checksum=self._calculate_file_checksum(class_file),
                metadata={"language": "kotlin"}
            ))
        
        return artifacts
    
    def _extract_warnings(self, output: str) -> List[str]:
        """Extract warnings from Gradle output."""
        warnings = []
        
        for line in output.split('\n'):
            line = line.strip()
            if 'warning:' in line.lower() or 'deprecated' in line.lower():
                warnings.append(line)
        
        return warnings
    
    def clean(self, file_paths: List[Path]) -> PluginResult:
        """Clean Kotlin build artifacts."""
        start_time = time.time()
        
        # Run Gradle clean
        command = "./gradlew clean"
        success, stdout, stderr = self._run_command(command, self.backend_dir)
        
        duration = time.time() - start_time
        
        return PluginResult(
            success=success,
            duration=duration,
            artifacts=[],
            error_message=stderr if not success else None,
            metrics={"gradle_task": "clean"}
        )
    
    def test(self, file_paths: List[Path], options: Dict[str, Any] = None) -> PluginResult:
        """Run Kotlin tests."""
        start_time = time.time()
        
        # Run Gradle test
        command = "./gradlew test"
        success, stdout, stderr = self._run_command(command, self.backend_dir, timeout=300)
        
        duration = time.time() - start_time
        
        # Parse test results
        test_results = self._parse_test_results(stdout)
        
        return PluginResult(
            success=success,
            duration=duration,
            artifacts=[],
            error_message=stderr if not success else None,
            warnings=self._extract_warnings(stdout),
            metrics=test_results
        )
    
    def _parse_test_results(self, output: str) -> Dict[str, Any]:
        """Parse test results from Gradle output."""
        results = {
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "tests_skipped": 0
        }
        
        # Look for test summary in output
        for line in output.split('\n'):
            if 'tests completed' in line.lower():
                # Parse test counts from line like "5 tests completed, 1 failed"
                import re
                numbers = re.findall(r'\d+', line)
                if numbers:
                    results["tests_run"] = int(numbers[0])
                    if 'failed' in line:
                        results["tests_failed"] = int(numbers[-1])
                    results["tests_passed"] = results["tests_run"] - results["tests_failed"]
        
        return results
    
    def package(self, file_paths: List[Path], options: Dict[str, Any] = None) -> PluginResult:
        """Create Kotlin package."""
        start_time = time.time()
        
        # Run Gradle assemble to create packages
        command = "./gradlew assemble"
        success, stdout, stderr = self._run_command(command, self.backend_dir, timeout=600)
        
        duration = time.time() - start_time
        
        if not success:
            return PluginResult(
                success=False,
                duration=duration,
                artifacts=[],
                error_message=f"Gradle assemble failed: {stderr}"
            )
        
        # Collect package artifacts
        artifacts = self._collect_build_artifacts()
        
        return PluginResult(
            success=True,
            duration=duration,
            artifacts=artifacts,
            warnings=self._extract_warnings(stdout),
            metrics={"gradle_task": "assemble"}
        )
