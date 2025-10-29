#!/usr/bin/env python3

"""
@llm-type service.builder
@llm-does kotlin/gradle builds with incremental compilation and parallel execution
@llm-rule gradle builds must be deterministic and support incremental compilation
"""

import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Set
try:
    from . import BuildModule, BuildContext, BuildModuleResult, BuildUtils, BuildArtifact
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from __init__ import BuildModule, BuildContext, BuildModuleResult, BuildUtils, BuildArtifact

class KotlinBuilder(BuildModule):
    """Build module for Kotlin projects using Gradle"""
    
    def __init__(self, context: BuildContext):
        super().__init__(context)
        self.gradle_wrapper = self.context.project_root / "backend" / "gradlew"
        self.backend_dir = self.context.project_root / "backend"
        self.build_dir = self.backend_dir / "build"
        
    def can_handle(self, target_name: str) -> bool:
        """Check if this module can handle Kotlin/Gradle targets"""
        kotlin_targets = {
            'backend-build', 'backend-compile', 'backend-test', 
            'backend-clean', 'kotlin-build', 'gradle-build'
        }
        return target_name in kotlin_targets or 'kotlin' in target_name or 'backend' in target_name
    
    def get_dependencies(self, target_name: str) -> List[str]:
        """Get Kotlin source dependencies"""
        dependencies = []
        
        # Kotlin source files
        src_dir = self.backend_dir / "src"
        if src_dir.exists():
            for kt_file in src_dir.rglob("*.kt"):
                dependencies.append(str(kt_file))
        
        # Build configuration files
        build_files = [
            "build.gradle.kts",
            "settings.gradle.kts", 
            "gradle.properties",
            "gradle/libs.versions.toml"
        ]
        
        for build_file in build_files:
            file_path = self.backend_dir / build_file
            if file_path.exists():
                dependencies.append(str(file_path))
        
        # Generated protobuf files (if they exist)
        proto_generated = self.backend_dir / "src" / "main" / "kotlin" / "com" / "unhinged" / "proto"
        if proto_generated.exists():
            for proto_file in proto_generated.rglob("*.kt"):
                dependencies.append(str(proto_file))
        
        return dependencies
    
    def calculate_cache_key(self, target_name: str) -> str:
        """Calculate cache key based on source files and configuration"""
        import hashlib
        hasher = hashlib.sha256()
        
        # Include target name
        hasher.update(target_name.encode())
        
        # Hash source files
        src_hash = BuildUtils.calculate_directory_hash(
            self.backend_dir / "src",
            patterns=["*.kt", "*.java"]
        )
        hasher.update(src_hash.encode())
        
        # Hash build configuration
        for config_file in ["build.gradle.kts", "gradle.properties"]:
            config_path = self.backend_dir / config_file
            if config_path.exists():
                hasher.update(BuildUtils.calculate_file_hash(config_path).encode())
        
        # Include Gradle version
        gradle_version = self._get_gradle_version()
        hasher.update(gradle_version.encode())
        
        return hasher.hexdigest()
    
    def validate_environment(self) -> List[str]:
        """Validate Gradle environment"""
        errors = []
        
        # Check if Gradle wrapper exists
        if not self.gradle_wrapper.exists():
            errors.append(f"Gradle wrapper not found: {self.gradle_wrapper}")
        elif not self.gradle_wrapper.is_file():
            errors.append(f"Gradle wrapper is not a file: {self.gradle_wrapper}")
        
        # Check if backend directory exists
        if not self.backend_dir.exists():
            errors.append(f"Backend directory not found: {self.backend_dir}")
        
        # Check if build.gradle.kts exists
        build_gradle = self.backend_dir / "build.gradle.kts"
        if not build_gradle.exists():
            errors.append(f"build.gradle.kts not found: {build_gradle}")
        
        # Check Java version
        java_available = BuildUtils.check_tool_available("java")
        if not java_available:
            errors.append("Java not found in PATH")
        
        return errors
    
    def get_estimated_duration(self, target_name: str) -> float:
        """Estimate build duration based on target type"""
        duration_map = {
            'backend-compile': 30.0,
            'backend-build': 120.0,
            'backend-test': 180.0,
            'backend-clean': 10.0
        }
        return duration_map.get(target_name, 60.0)
    
    def supports_incremental_build(self, target_name: str) -> bool:
        """Kotlin supports incremental compilation"""
        return target_name in ['backend-compile', 'backend-build']
    
    def supports_parallel_build(self, target_name: str) -> bool:
        """Gradle supports parallel builds"""
        return True
    
    def build(self, target_name: str) -> BuildModuleResult:
        """Execute Kotlin/Gradle build"""
        start_time = time.time()
        
        # Validate environment first
        env_errors = self.validate_environment()
        if env_errors:
            return BuildModuleResult(
                success=False,
                duration=0.0,
                artifacts=[],
                error_message=f"Environment validation failed: {'; '.join(env_errors)}"
            )
        
        # Determine Gradle task based on target
        gradle_task = self._get_gradle_task(target_name)
        if not gradle_task:
            return BuildModuleResult(
                success=False,
                duration=0.0,
                artifacts=[],
                error_message=f"Unknown Kotlin target: {target_name}"
            )
        
        # Build Gradle command
        gradle_args = self._get_gradle_args(target_name)
        command = f"./gradlew {gradle_task} {' '.join(gradle_args)}"
        
        self.logger.info(f"🔨 Building Kotlin target '{target_name}' with command: {command}")
        
        # Execute build
        success, stdout, stderr = BuildUtils.run_command(
            command, 
            self.backend_dir,
            timeout=600  # 10 minutes for Kotlin builds
        )
        
        duration = time.time() - start_time
        
        if not success:
            return BuildModuleResult(
                success=False,
                duration=duration,
                artifacts=[],
                error_message=f"Gradle build failed: {stderr}",
                warnings=self._extract_warnings(stdout)
            )
        
        # Collect build artifacts
        artifacts = self._collect_artifacts(target_name)
        
        # Extract build metrics
        metrics = self._extract_build_metrics(stdout)
        
        self.logger.info(f"✅ Kotlin build '{target_name}' completed in {duration:.2f}s")
        
        return BuildModuleResult(
            success=True,
            duration=duration,
            artifacts=artifacts,
            warnings=self._extract_warnings(stdout),
            metrics=metrics
        )
    
    def clean(self, target_name: str) -> bool:
        """Clean Kotlin build artifacts"""
        command = "./gradlew clean"
        success, _, _ = BuildUtils.run_command(command, self.backend_dir)
        return success
    
    def _get_gradle_task(self, target_name: str) -> Optional[str]:
        """Map target name to Gradle task"""
        task_map = {
            'backend-compile': 'compileKotlin',
            'backend-build': 'build',
            'backend-test': 'test',
            'backend-clean': 'clean',
            'kotlin-build': 'build',
            'gradle-build': 'build'
        }
        return task_map.get(target_name)
    
    def _get_gradle_args(self, target_name: str) -> List[str]:
        """Get Gradle arguments based on context and target"""
        args = []
        
        # Always use no-daemon for CI/build systems
        args.append("--no-daemon")
        
        # Enable parallel builds if supported
        if self.context.parallel and self.supports_parallel_build(target_name):
            args.append("--parallel")
        
        # Enable incremental builds if supported
        if self.context.incremental and self.supports_incremental_build(target_name):
            args.append("--build-cache")
        
        # Environment-specific args
        if self.context.environment == "production":
            args.append("-Pprod")
        elif self.context.environment == "development":
            args.append("-Pdev")
        
        # Add info logging for better feedback
        args.append("--info")
        
        return args
    
    def _get_gradle_version(self) -> str:
        """Get Gradle version for cache key"""
        command = "./gradlew --version"
        success, stdout, _ = BuildUtils.run_command(command, self.backend_dir, timeout=30)
        
        if success:
            # Extract version from output
            for line in stdout.split('\n'):
                if 'Gradle' in line and any(char.isdigit() for char in line):
                    return line.strip()
        
        return "unknown"
    
    def _collect_artifacts(self, target_name: str) -> List[BuildArtifact]:
        """Collect build artifacts from Gradle build"""
        artifacts = []
        
        # JAR files
        libs_dir = self.build_dir / "libs"
        if libs_dir.exists():
            for jar_file in libs_dir.glob("*.jar"):
                artifacts.append(BuildUtils.create_build_artifact(
                    jar_file, 
                    "jar",
                    {"gradle_task": self._get_gradle_task(target_name)}
                ))
        
        # Class files (for compile-only targets)
        classes_dir = self.build_dir / "classes"
        if classes_dir.exists() and target_name == 'backend-compile':
            artifacts.append(BuildUtils.create_build_artifact(
                classes_dir,
                "classes",
                {"type": "compiled_classes"}
            ))
        
        # Test reports
        test_reports = self.build_dir / "reports" / "tests"
        if test_reports.exists() and 'test' in target_name:
            artifacts.append(BuildUtils.create_build_artifact(
                test_reports,
                "test_report",
                {"format": "html"}
            ))
        
        return artifacts
    
    def _extract_warnings(self, gradle_output: str) -> List[str]:
        """Extract warnings from Gradle output"""
        warnings = []
        
        for line in gradle_output.split('\n'):
            if 'warning:' in line.lower() or 'deprecated' in line.lower():
                warnings.append(line.strip())
        
        return warnings
    
    def _extract_build_metrics(self, gradle_output: str) -> Dict[str, any]:
        """Extract build metrics from Gradle output"""
        metrics = {}
        
        # Extract build time
        build_time_pattern = r'BUILD SUCCESSFUL in (\d+)s'
        match = re.search(build_time_pattern, gradle_output)
        if match:
            metrics['gradle_build_time'] = int(match.group(1))
        
        # Extract task execution times
        task_times = {}
        task_pattern = r'> Task :(\w+) .*?(\d+)ms'
        for match in re.finditer(task_pattern, gradle_output):
            task_name = match.group(1)
            task_time = int(match.group(2))
            task_times[task_name] = task_time
        
        if task_times:
            metrics['task_execution_times'] = task_times
        
        # Count compiled files
        compiled_pattern = r'(\d+) source files'
        match = re.search(compiled_pattern, gradle_output)
        if match:
            metrics['compiled_files'] = int(match.group(1))
        
        return metrics
