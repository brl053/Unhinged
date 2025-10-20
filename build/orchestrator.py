#!/usr/bin/env python3

"""
@llm-type service
@llm-legend Enhanced build orchestrator for Unhinged polyglot monorepo
@llm-key Provides intelligent dependency tracking, parallel execution, caching, and multi-language build coordination
@llm-map Central build coordination system that integrates with existing Makefile and Docker Compose workflows
@llm-axiom Build operations must be deterministic, cacheable, and provide clear feedback to developers
@llm-contract Returns BuildResult with success status, artifacts, and performance metrics
@llm-token build-orchestrator: Python service coordinating all build operations across languages

Enhanced Build Orchestrator for Unhinged Platform

Coordinates builds across Kotlin, TypeScript, Python, and Protobuf with intelligent
dependency tracking, parallel execution, and comprehensive caching.

Features:
- Dependency graph resolution
- Parallel execution with resource management
- Intelligent caching with content-based keys
- Build performance monitoring
- Integration with existing Makefile commands
- LLM-powered error explanation

Author: Unhinged Team
Version: 2.0.0
Date: 2025-10-19
"""

import asyncio
import hashlib
import json
import logging
import os
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
import yaml

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
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class BuildTarget:
    """Represents a build target with dependencies and metadata"""
    name: str
    description: str
    dependencies: List[str] = field(default_factory=list)
    commands: List[str] = field(default_factory=list)
    inputs: List[str] = field(default_factory=list)  # Files/directories that affect this target
    outputs: List[str] = field(default_factory=list)  # Generated files/directories
    cache_key: Optional[str] = None
    parallel_safe: bool = True
    estimated_duration: float = 0.0  # seconds

@dataclass
class BuildResult:
    """Result of a build operation"""
    target: str
    success: bool
    duration: float
    cache_hit: bool = False
    error_message: Optional[str] = None
    artifacts: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)

class DependencyGraph:
    """Manages build target dependencies and execution order"""
    
    def __init__(self):
        self.targets: Dict[str, BuildTarget] = {}
        self.graph: Dict[str, Set[str]] = {}
    
    def add_target(self, target: BuildTarget):
        """Add a build target to the graph"""
        self.targets[target.name] = target
        self.graph[target.name] = set(target.dependencies)
    
    def get_execution_order(self, target_names: List[str]) -> List[List[str]]:
        """Get execution order with parallelizable groups"""
        # Topological sort with parallel groups
        visited = set()
        temp_visited = set()
        execution_groups = []
        
        def visit(node: str, current_group: Set[str]):
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
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load cache metadata"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                logger.warning("Failed to load cache metadata, starting fresh")
        return {}
    
    def _save_metadata(self):
        """Save cache metadata"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except IOError as e:
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
                    except IOError:
                        # If we can't read the file, include its mtime
                        hasher.update(str(path.stat().st_mtime).encode())
                elif path.is_dir():
                    # For directories, include file list and mtimes
                    for file_path in sorted(path.rglob('*')):
                        if file_path.is_file():
                            hasher.update(str(file_path.relative_to(path)).encode())
                            hasher.update(str(file_path.stat().st_mtime).encode())
        
        return hasher.hexdigest()
    
    def is_cached(self, cache_key: str) -> bool:
        """Check if build result is cached"""
        return cache_key in self.metadata and \
               (self.cache_dir / cache_key).exists()
    
    def get_cached_result(self, cache_key: str) -> Optional[BuildResult]:
        """Get cached build result"""
        if not self.is_cached(cache_key):
            return None
        
        try:
            metadata = self.metadata[cache_key]
            return BuildResult(
                target=metadata['target'],
                success=metadata['success'],
                duration=0.0,  # Cache hit, no duration
                cache_hit=True,
                artifacts=metadata.get('artifacts', [])
            )
        except (KeyError, TypeError) as e:
            logger.error(f"Failed to load cached result: {e}")
            return None
    
    def store_result(self, cache_key: str, result: BuildResult):
        """Store build result in cache"""
        try:
            # Store metadata
            self.metadata[cache_key] = {
                'target': result.target,
                'success': result.success,
                'timestamp': time.time(),
                'artifacts': result.artifacts
            }
            
            # Create cache marker file
            cache_file = self.cache_dir / cache_key
            cache_file.write_text(json.dumps({
                'target': result.target,
                'success': result.success,
                'duration': result.duration
            }))
            
            self._save_metadata()
        except IOError as e:
            logger.error(f"Failed to store cache result: {e}")

class BuildOrchestrator:
    """Main build orchestration system"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.project_root = Path(__file__).parent.parent
        self.config_path = config_path or self.project_root / "build-config.yml"
        self.config = self._load_config()
        self.dependency_graph = DependencyGraph()
        self.cache = BuildCache()
        self.max_workers = self.config.get('build_system', {}).get('parallelism', {}).get('max_workers', 4)

        # Initialize performance monitoring
        if MONITORING_AVAILABLE:
            self.monitor = BuildPerformanceMonitor(self.project_root)
        else:
            self.monitor = None

        # Load build targets
        self._load_targets()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load build configuration"""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except (FileNotFoundError, yaml.YAMLError) as e:
            logger.error(f"Failed to load config from {self.config_path}: {e}")
            return {}
    
    def _load_targets(self):
        """Load build targets from configuration"""
        # Load targets from 'targets' section
        targets_config = self.config.get('targets', {})
        self._load_targets_from_section(targets_config)

        # Load targets from 'services' section (for proto-clients, registry, etc.)
        services_config = self.config.get('services', {})
        self._load_targets_from_section(services_config)

    def _load_targets_from_section(self, targets_config: dict):
        """Load targets from a configuration section"""
        for name, target_config in targets_config.items():
            # Skip if this is a regular service definition (has 'type' or 'image')
            if 'type' in target_config or 'image' in target_config:
                continue

            # Extract commands from steps
            commands = []
            inputs = target_config.get('inputs', [])
            dependencies = target_config.get('dependencies', [])

            for step in target_config.get('steps', []):
                if 'command' in step:
                    commands.append(step['command'])
                elif 'target' in step:
                    # This step depends on another target
                    dependencies.append(step['target'])

            # Auto-detect inputs if not specified
            if not inputs:
                inputs = self._auto_detect_inputs(name, commands)

            # Create build target
            target = BuildTarget(
                name=name,
                description=target_config.get('description', ''),
                dependencies=dependencies,
                commands=commands,
                inputs=inputs,
                parallel_safe=target_config.get('parallel', True),
                estimated_duration=target_config.get('estimated_duration', 60.0)
            )

            # Calculate cache key
            target.cache_key = self.cache.calculate_cache_key(target)

            self.dependency_graph.add_target(target)

    def _auto_detect_inputs(self, target_name: str, commands: List[str]) -> List[str]:
        """Auto-detect input files/directories for a target"""
        inputs = []

        # Language-specific input detection
        if 'backend' in target_name or 'kotlin' in target_name:
            inputs.extend([
                "backend/src/**/*.kt",
                "backend/build.gradle.kts",
                "backend/gradle.properties"
            ])

        if 'frontend' in target_name or 'typescript' in target_name:
            inputs.extend([
                "frontend/src/**/*.ts",
                "frontend/src/**/*.tsx",
                "frontend/package.json",
                "frontend/webpack.config.js"
            ])

        if 'python' in target_name or any(service in target_name for service in ['whisper-tts', 'vision-ai', 'context-llm']):
            inputs.extend([
                "services/**/*.py",
                "services/**/requirements.txt",
                "services/**/pyproject.toml"
            ])

        if 'proto' in target_name:
            inputs.extend([
                "proto/*.proto"
            ])

        if 'docker' in target_name:
            inputs.extend([
                "**/Dockerfile",
                "docker-compose*.yml"
            ])

        # Command-based input detection
        for command in commands:
            if 'proto' in command and 'build.sh' in command:
                inputs.append("proto/*.proto")
            if 'gradlew' in command:
                inputs.extend(["backend/src/**/*.kt", "backend/build.gradle.kts"])
            if 'npm' in command:
                inputs.extend(["frontend/src/**/*", "frontend/package.json"])

        return inputs
    
    async def build_target(self, target_name: str) -> BuildResult:
        """Build a single target"""
        target = self.dependency_graph.targets.get(target_name)
        if not target:
            return BuildResult(
                target=target_name,
                success=False,
                duration=0.0,
                error_message=f"Target '{target_name}' not found"
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
                        error_message=module_result.error_message
                    )

                    if module_result.success:
                        logger.info(f"✅ Module build for '{target_name}' completed in {duration:.2f}s")
                        # Cache successful result
                        if target.cache_key:
                            self.cache.store_result(target.cache_key, build_result)
                    else:
                        logger.error(f"❌ Module build for '{target_name}' failed: {module_result.error_message}")

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
                    timeout=300  # 5 minute timeout
                )

                if result.returncode != 0:
                    error_msg = f"Command failed: {command}\nError: {result.stderr}"
                    logger.error(error_msg)
                    return BuildResult(
                        target=target_name,
                        success=False,
                        duration=time.time() - start_time,
                        error_message=error_msg
                    )

                if result.stdout:
                    logger.info(f"📤 Output: {result.stdout.strip()}")
            
            duration = time.time() - start_time
            build_result = BuildResult(
                target=target_name,
                success=True,
                duration=duration,
                cache_hit=cache_hit
            )

            # Cache successful result
            if target.cache_key:
                self.cache.store_result(target.cache_key, build_result)

            # End performance monitoring
            if self.monitor and monitoring_state:
                self.monitor.end_build_monitoring(
                    monitoring_state,
                    success=True,
                    cache_hit=cache_hit
                )

            logger.info(f"✅ Target '{target_name}' completed in {duration:.2f}s")
            return build_result
            
        except subprocess.TimeoutExpired:
            error_msg = f"Target '{target_name}' timed out after 5 minutes"
            logger.error(error_msg)
            duration = time.time() - start_time

            # End performance monitoring for timeout
            if self.monitor and monitoring_state:
                self.monitor.end_build_monitoring(
                    monitoring_state,
                    success=False,
                    cache_hit=False,
                    error_message=error_msg
                )

            return BuildResult(
                target=target_name,
                success=False,
                duration=duration,
                error_message=error_msg
            )
        except Exception as e:
            error_msg = f"Unexpected error building '{target_name}': {e}"
            logger.error(error_msg)
            duration = time.time() - start_time

            # End performance monitoring for error
            if self.monitor and monitoring_state:
                self.monitor.end_build_monitoring(
                    monitoring_state,
                    success=False,
                    cache_hit=False,
                    error_message=error_msg
                )

            return BuildResult(
                target=target_name,
                success=False,
                duration=duration,
                error_message=error_msg
            )
    
    async def build_targets(self, target_names: List[str]) -> List[BuildResult]:
        """Build multiple targets with dependency resolution and parallelization"""
        try:
            execution_groups = self.dependency_graph.get_execution_order(target_names)
            all_results = []
            
            logger.info(f"🚀 Building targets: {target_names}")
            logger.info(f"📋 Execution plan: {len(execution_groups)} groups")
            
            for i, group in enumerate(execution_groups):
                logger.info(f"🔄 Group {i+1}/{len(execution_groups)}: {group}")
                
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
            return [BuildResult(
                target="dependency_resolution",
                success=False,
                duration=0.0,
                error_message=str(e)
            )]
