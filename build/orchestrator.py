#!/usr/bin/env python3

"""
@llm-type service.orchestrator
@llm-does polyglot build orchestration with dependency resolution and intelligent caching
@llm-rule builds must be deterministic and provide comprehensive error reporting
"""

import asyncio
import hashlib
import json
import logging
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

# Import validation system
try:
    from validators import DependencyValidator, PortValidator, ResourceValidator

    VALIDATION_AVAILABLE = True
except ImportError:
    try:
        from .validators import DependencyValidator, PortValidator, ResourceValidator

        VALIDATION_AVAILABLE = True
    except ImportError:
        VALIDATION_AVAILABLE = False
        print("⚠️ Build validators not available")

# Import error guidance system
try:
    from diagnostics.error_guidance import ErrorGuidance, format_error_guidance

    ERROR_GUIDANCE_AVAILABLE = True
except ImportError:
    try:
        from .diagnostics.error_guidance import ErrorGuidance, format_error_guidance

        ERROR_GUIDANCE_AVAILABLE = True
    except ImportError:
        ERROR_GUIDANCE_AVAILABLE = False
        print("⚠️ Error guidance system not available")

# Import static analysis system
try:
    from static_analysis_manager import StaticAnalysisManager

    STATIC_ANALYSIS_AVAILABLE = True
except ImportError:
    try:
        from .static_analysis_manager import StaticAnalysisManager

        STATIC_ANALYSIS_AVAILABLE = True
    except ImportError:
        STATIC_ANALYSIS_AVAILABLE = False
        print("⚠️ Static analysis system not available")

# Import monitoring system
try:
    from monitoring import BuildPerformanceMonitor

    MONITORING_AVAILABLE = True
except ImportError:
    try:
        from .monitoring import BuildPerformanceMonitor

        MONITORING_AVAILABLE = True
    except ImportError:
        MONITORING_AVAILABLE = False

# Import module system
try:
    from modules import get_module_for_target

    MODULES_AVAILABLE = True
except ImportError:
    try:
        from .modules import get_module_for_target

        MODULES_AVAILABLE = True
    except ImportError:
        MODULES_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class BuildTarget:
    """Represents a build target with dependencies and metadata"""

    name: str
    description: str
    dependencies: list[str] = field(default_factory=list)
    commands: list[str] = field(default_factory=list)
    inputs: list[str] = field(default_factory=list)  # Files/directories that affect this target
    outputs: list[str] = field(default_factory=list)  # Generated files/directories
    cache_key: str | None = None
    parallel_safe: bool = True
    estimated_duration: float = 0.0  # seconds


@dataclass
class BuildResult:
    """Result of a build operation"""

    target: str
    success: bool
    duration: float
    cache_hit: bool = False
    error_message: str | None = None
    artifacts: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)


class DependencyGraph:
    """Manages build target dependencies and execution order"""

    def __init__(self):
        self.targets: dict[str, BuildTarget] = {}
        self.graph: dict[str, set[str]] = {}

    def add_target(self, target: BuildTarget):
        """Add a build target to the graph"""
        self.targets[target.name] = target
        self.graph[target.name] = set(target.dependencies)

    def get_execution_order(self, target_names: list[str]) -> list[list[str]]:
        """Get execution order with parallelizable groups"""
        # Topological sort with parallel groups
        visited = set()
        temp_visited = set()
        execution_groups = []

        def visit(node: str, current_group: set[str]):
            if node in temp_visited:
                raise ValueError(f"Circular dependency detected involving {node}")
            if node in visited:
                return

            temp_visited.add(node)

            # Visit all dependencies first
            for dep in self.graph.get(node, set()):
                visit(dep, current_group)

            temp_visited.remove(node)
            visited.add(node)
            current_group.add(node)

        # Build execution groups
        remaining = set(target_names)
        while remaining:
            current_group = set()
            for target in list(remaining):
                # Check if all dependencies are satisfied
                deps = self.graph.get(target, set())
                if deps.issubset(visited):
                    visit(target, current_group)
                    remaining.discard(target)

            if current_group:
                execution_groups.append(list(current_group))
            else:
                # Handle remaining circular dependencies
                if remaining:
                    raise ValueError(f"Circular dependencies detected: {remaining}")

        return execution_groups


class BuildCache:
    """Intelligent build caching system"""

    def __init__(self, cache_dir: Path = Path(".build-cache")):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)
        self.metadata_file = cache_dir / "metadata.json"
        self.metadata = self._load_metadata()

    def _load_metadata(self) -> dict[str, Any]:
        """Load cache metadata"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file) as f:
                    return json.load(f)
            except (OSError, json.JSONDecodeError):
                logger.warning("Failed to load cache metadata, starting fresh")
        return {}

    def _save_metadata(self):
        """Save cache metadata"""
        try:
            with open(self.metadata_file, "w") as f:
                json.dump(self.metadata, f, indent=2)
        except OSError as e:
            logger.error(f"Failed to save cache metadata: {e}")

    def calculate_cache_key(self, target: BuildTarget) -> str:
        """Calculate content-based cache key for a target"""
        hasher = hashlib.sha256()

        # Include target definition
        hasher.update(target.name.encode())
        hasher.update(str(target.commands).encode())

        # Include input file contents
        for input_path in target.inputs:
            path = Path(input_path)
            if path.exists():
                if path.is_file():
                    try:
                        hasher.update(path.read_bytes())
                    except OSError:
                        # If we can't read the file, include its mtime
                        hasher.update(str(path.stat().st_mtime).encode())
                elif path.is_dir():
                    # For directories, include file list and mtimes
                    for file_path in sorted(path.rglob("*")):
                        if file_path.is_file():
                            hasher.update(str(file_path.relative_to(path)).encode())
                            hasher.update(str(file_path.stat().st_mtime).encode())

        return hasher.hexdigest()

    def is_cached(self, cache_key: str) -> bool:
        """Check if build result is cached"""
        return cache_key in self.metadata and (self.cache_dir / cache_key).exists()

    def get_cached_result(self, cache_key: str) -> BuildResult | None:
        """Get cached build result"""
        if not self.is_cached(cache_key):
            return None

        try:
            metadata = self.metadata[cache_key]
            return BuildResult(
                target=metadata["target"],
                success=metadata["success"],
                duration=0.0,  # Cache hit, no duration
                cache_hit=True,
                artifacts=metadata.get("artifacts", []),
            )
        except (KeyError, TypeError) as e:
            logger.error(f"Failed to load cached result: {e}")
            return None

    def store_result(self, cache_key: str, result: BuildResult):
        """Store build result in cache"""
        try:
            # Store metadata
            self.metadata[cache_key] = {
                "target": result.target,
                "success": result.success,
                "timestamp": time.time(),
                "artifacts": result.artifacts,
            }

            # Create cache marker file
            cache_file = self.cache_dir / cache_key
            cache_file.write_text(
                json.dumps({"target": result.target, "success": result.success, "duration": result.duration})
            )

            self._save_metadata()
        except OSError as e:
            logger.error(f"Failed to store cache result: {e}")


class BuildOrchestrator:
    """Main build orchestration system"""

    def __init__(self, config_path: Path | None = None):
        self.project_root = Path(__file__).parent.parent
        self.config_path = config_path or self.project_root / "build" / "config" / "build-config.yml"
        self.config = self._load_config()
        self.dependency_graph = DependencyGraph()
        self.cache = BuildCache()
        self.max_workers = self.config.get("build_system", {}).get("parallelism", {}).get("max_workers", 4)

        # Initialize performance monitoring
        if MONITORING_AVAILABLE:
            self.monitor = BuildPerformanceMonitor(self.project_root)
        else:
            self.monitor = None

        # Initialize static analysis
        if STATIC_ANALYSIS_AVAILABLE:
            self.static_analyzer = StaticAnalysisManager(self.project_root / "build")
        else:
            self.static_analyzer = None

        # Load build targets
        self._load_targets()

    def _load_config(self) -> dict[str, Any]:
        """Load build configuration"""
        try:
            with open(self.config_path) as f:
                return yaml.safe_load(f)
        except (FileNotFoundError, yaml.YAMLError) as e:
            logger.error(f"Failed to load config from {self.config_path}: {e}")
            return {}

    def _load_targets(self):
        """Load build targets from configuration"""
        # Load targets from 'targets' section
        targets_config = self.config.get("targets", {})
        self._load_targets_from_section(targets_config)

        # Load targets from 'services' section (for proto-clients, registry, etc.)
        services_config = self.config.get("services", {})
        self._load_targets_from_section(services_config)

    def _load_targets_from_section(self, targets_config: dict):
        """Load targets from a configuration section"""
        for name, target_config in targets_config.items():
            # Skip if this is a regular service definition (has 'type' or 'image')
            if "type" in target_config or "image" in target_config:
                continue

            # Extract commands from steps
            commands = []
            inputs = target_config.get("inputs", [])
            dependencies = target_config.get("dependencies", [])

            for step in target_config.get("steps", []):
                if "command" in step:
                    commands.append(step["command"])
                elif "target" in step:
                    # This step depends on another target
                    dependencies.append(step["target"])

            # Auto-detect inputs if not specified
            if not inputs:
                inputs = self._auto_detect_inputs(name, commands)

            # Create build target
            target = BuildTarget(
                name=name,
                description=target_config.get("description", ""),
                dependencies=dependencies,
                commands=commands,
                inputs=inputs,
                parallel_safe=target_config.get("parallel", True),
                estimated_duration=target_config.get("estimated_duration", 60.0),
            )

            # Calculate cache key
            target.cache_key = self.cache.calculate_cache_key(target)

            self.dependency_graph.add_target(target)

    def _auto_detect_inputs(self, target_name: str, commands: list[str]) -> list[str]:
        """Auto-detect input files/directories for a target"""
        inputs = []

        # Language-specific input detection
        if "backend" in target_name or "kotlin" in target_name:
            inputs.extend(["backend/src/**/*.kt", "backend/build.gradle.kts", "backend/gradle.properties"])

        if "frontend" in target_name or "typescript" in target_name:
            inputs.extend(
                ["frontend/src/**/*.ts", "frontend/src/**/*.tsx", "frontend/package.json", "frontend/webpack.config.js"]
            )

        if "python" in target_name or any(
            service in target_name for service in ["whisper-tts", "vision-ai", "context-llm"]
        ):
            inputs.extend(["libs/python/**/*.py"])

        if "proto" in target_name:
            inputs.extend(["proto/*.proto"])

        if "docker" in target_name:
            inputs.extend(["**/Dockerfile", "docker-compose*.yml"])

        # Command-based input detection
        for command in commands:
            if "proto" in command and "build.sh" in command:
                inputs.append("proto/*.proto")
            if "gradlew" in command:
                inputs.extend(["backend/src/**/*.kt", "backend/build.gradle.kts"])
            if "npm" in command:
                inputs.extend(["frontend/src/**/*", "frontend/package.json"])

        return inputs

    async def build_target(self, target_name: str) -> BuildResult:
        """Build a single target"""
        target = self.dependency_graph.targets.get(target_name)
        if not target:
            return BuildResult(
                target=target_name, success=False, duration=0.0, error_message=f"Target '{target_name}' not found"
            )

        # Check cache first
        cache_hit = False
        if target.cache_key and self.cache.is_cached(target.cache_key):
            cached_result = self.cache.get_cached_result(target.cache_key)
            if cached_result:
                logger.info(f"✅ Cache hit for target '{target_name}'")
                cached_result.cache_hit = True
                return cached_result

        # Start performance monitoring
        monitoring_state = None
        if self.monitor:
            monitoring_state = self.monitor.start_build_monitoring(target_name)

        # Execute target
        logger.info(f"🔨 Building target '{target_name}': {target.description}")
        start_time = time.time()

        try:
            # Try to use build module first if available
            if MODULES_AVAILABLE:
                module = get_module_for_target(target_name)
                if module:
                    logger.info(f"🔧 Using build module: {module.__class__.__name__}")
                    module_result = module.build(target_name)

                    duration = time.time() - start_time
                    build_result = BuildResult(
                        target=target_name,
                        success=module_result.success,
                        duration=duration,
                        cache_hit=module_result.cache_hit,
                        error_message=module_result.error_message,
                    )

                    if module_result.success:
                        logger.info(f"✅ Module build for '{target_name}' completed in {duration:.2f}s")
                        # Cache successful result
                        if target.cache_key:
                            self.cache.store_result(target.cache_key, build_result)
                    else:
                        logger.error(f"❌ Module build for '{target_name}' failed: {module_result.error_message}")

                        # Provide enhanced error guidance
                        if ERROR_GUIDANCE_AVAILABLE and module_result.error_message:
                            guidance = ErrorGuidance(self.project_root)
                            error_analysis = guidance.analyze_error(
                                module_result.error_message, f"building {target_name}"
                            )
                            formatted_guidance = format_error_guidance(error_analysis)
                            print(formatted_guidance)

                    return build_result

            # Fallback to command execution
            for command in target.commands:
                logger.info(f"💻 Executing: {command}")
                result = subprocess.run(
                    command,
                    shell=True,
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5 minute timeout
                )

                if result.returncode != 0:
                    error_msg = f"Command failed: {command}\nError: {result.stderr}"
                    logger.error(error_msg)

                    # Provide enhanced error guidance
                    if ERROR_GUIDANCE_AVAILABLE:
                        guidance = ErrorGuidance(self.project_root)
                        error_analysis = guidance.analyze_error(result.stderr or error_msg, f"executing {command}")
                        formatted_guidance = format_error_guidance(error_analysis)
                        print(formatted_guidance)

                    return BuildResult(
                        target=target_name, success=False, duration=time.time() - start_time, error_message=error_msg
                    )

                if result.stdout:
                    logger.info(f"📤 Output: {result.stdout.strip()}")

            duration = time.time() - start_time
            build_result = BuildResult(target=target_name, success=True, duration=duration, cache_hit=cache_hit)

            # Cache successful result
            if target.cache_key:
                self.cache.store_result(target.cache_key, build_result)

            # End performance monitoring
            if self.monitor and monitoring_state:
                self.monitor.end_build_monitoring(monitoring_state, success=True, cache_hit=cache_hit)

            logger.info(f"✅ Target '{target_name}' completed in {duration:.2f}s")
            return build_result

        except subprocess.TimeoutExpired:
            error_msg = f"Target '{target_name}' timed out after 5 minutes"
            logger.error(error_msg)
            duration = time.time() - start_time

            # End performance monitoring for timeout
            if self.monitor and monitoring_state:
                self.monitor.end_build_monitoring(
                    monitoring_state, success=False, cache_hit=False, error_message=error_msg
                )

            return BuildResult(target=target_name, success=False, duration=duration, error_message=error_msg)
        except Exception as e:
            error_msg = f"Unexpected error building '{target_name}': {e}"
            logger.error(error_msg)
            duration = time.time() - start_time

            # End performance monitoring for error
            if self.monitor and monitoring_state:
                self.monitor.end_build_monitoring(
                    monitoring_state, success=False, cache_hit=False, error_message=error_msg
                )

            return BuildResult(target=target_name, success=False, duration=duration, error_message=error_msg)

    def validate_build_configuration(self) -> list[str]:
        """
        Validate build configuration at compile time

        @llm-future This becomes part of Unhinged OS resource allocation compiler
        Returns list of validation errors that must be fixed before build
        """
        if not VALIDATION_AVAILABLE:
            logger.warning("⚠️ Build validation skipped - validators not available")
            return []

        validation_errors = []
        project_root = self.project_root

        logger.info("🔍 Running build-time validation...")

        # Port conflict validation
        try:
            port_validator = PortValidator(project_root)
            port_conflicts = port_validator.validate_project()

            for conflict in port_conflicts:
                if conflict.severity == "error":
                    validation_errors.append(f"PORT CONFLICT: {conflict}")
                else:
                    logger.warning(f"⚠️ PORT WARNING: {conflict}")

            if port_conflicts:
                logger.info(f"🔍 Found {len(port_conflicts)} port issues")

        except Exception as e:
            logger.error(f"❌ Port validation failed: {e}")

        # Dependency validation
        try:
            dep_validator = DependencyValidator(project_root)
            dep_issues = dep_validator.validate_dependencies()

            for issue in dep_issues:
                if issue.severity == "error":
                    validation_errors.append(f"DEPENDENCY ERROR: {issue.description}")
                else:
                    logger.warning(f"⚠️ DEPENDENCY WARNING: {issue.description}")

        except Exception as e:
            logger.error(f"❌ Dependency validation failed: {e}")

        # Resource validation
        try:
            resource_validator = ResourceValidator(project_root)
            resource_issues = resource_validator.validate_resources()

            for issue in resource_issues:
                if issue.severity == "error":
                    validation_errors.append(f"RESOURCE ERROR: {issue.description}")
                else:
                    logger.warning(f"⚠️ RESOURCE WARNING: {issue.description}")

        except Exception as e:
            logger.error(f"❌ Resource validation failed: {e}")

        if validation_errors:
            logger.error("❌ Build validation failed! Fix these issues before proceeding:")
            for error in validation_errors:
                logger.error(f"   • {error}")
        else:
            logger.info("✅ Build validation passed - no blocking issues found")

        return validation_errors

    async def build_targets(self, target_names: list[str]) -> list[BuildResult]:
        """Build multiple targets with dependency resolution and parallelization"""

        # COMPILE-TIME VALIDATION: Prevent runtime errors
        validation_errors = self.validate_build_configuration()
        if validation_errors:
            logger.error("🚫 Build aborted due to validation failures")
            return [
                BuildResult(
                    target="validation",
                    success=False,
                    duration=0.0,
                    error_message=f"Build validation failed: {'; '.join(validation_errors)}",
                )
            ]

        # STATIC ANALYSIS: Check Python code quality before building
        if self.static_analyzer:
            logger.info("🔍 Running static analysis on changed Python modules...")
            python_modules = ["cli", "libs/python", "services", "control"]
            analysis_results = self.static_analyzer.run_analysis_on_changed_modules(python_modules, auto_fix=True)

            failed_modules = [module for module, result in analysis_results.items() if not result.passed]
            if failed_modules:
                logger.error(f"🚫 Build aborted due to static analysis failures in: {', '.join(failed_modules)}")
                return [
                    BuildResult(
                        target="static_analysis",
                        success=False,
                        duration=sum(r.execution_time for r in analysis_results.values()),
                        error_message=f"Static analysis failed for modules: {', '.join(failed_modules)}",
                    )
                ]
            elif analysis_results:
                total_fixed = sum(r.fixed_count for r in analysis_results.values())
                if total_fixed > 0:
                    logger.info(f"✅ Static analysis passed, auto-fixed {total_fixed} issues")
                else:
                    logger.info("✅ Static analysis passed, no issues found")

        try:
            execution_groups = self.dependency_graph.get_execution_order(target_names)
            all_results = []

            logger.info(f"🚀 Building targets: {target_names}")
            logger.info(f"📋 Execution plan: {len(execution_groups)} groups")

            for i, group in enumerate(execution_groups):
                logger.info(f"🔄 Group {i + 1}/{len(execution_groups)}: {group}")

                # Execute group in parallel
                with ThreadPoolExecutor(max_workers=min(len(group), self.max_workers)) as executor:
                    futures = [executor.submit(asyncio.run, self.build_target(target)) for target in group]
                    group_results = []

                    for future in as_completed(futures):
                        result = future.result()
                        group_results.append(result)

                        if not result.success:
                            logger.error(f"❌ Build failed for target '{result.target}': {result.error_message}")
                            # Cancel remaining builds
                            for f in futures:
                                f.cancel()
                            return all_results + group_results

                all_results.extend(group_results)

            # Summary
            successful = sum(1 for r in all_results if r.success)
            total_duration = sum(r.duration for r in all_results)
            cache_hits = sum(1 for r in all_results if r.cache_hit)

            logger.info(f"🎉 Build completed: {successful}/{len(all_results)} targets successful")
            logger.info(f"⏱️  Total duration: {total_duration:.2f}s")
            logger.info(f"🚀 Cache hits: {cache_hits}/{len(all_results)}")

            return all_results

        except ValueError as e:
            logger.error(f"❌ Dependency error: {e}")
            return [BuildResult(target="dependency_resolution", success=False, duration=0.0, error_message=str(e))]
