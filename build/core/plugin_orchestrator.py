#!/usr/bin/env python3
"""
Plugin-Aware Build Orchestrator

Enhanced build orchestrator that uses the standardized plugin system.
Provides intelligent plugin selection, parallel execution, and caching.

@llm-type core.orchestrator
@llm-does plugin-based build orchestration with intelligent selection
"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from ..modules import BuildContext
    from .plugin_interface import BuilderPlugin, PluginCapability, PluginResult
    from .plugin_registry import PluginRegistry
except ImportError:
    import sys

    sys.path.insert(0, str(Path(__file__).parent.parent))
    from core.plugin_interface import BuilderPlugin, PluginCapability, PluginResult
    from core.plugin_registry import PluginRegistry
    from modules import BuildContext


@dataclass
class BuildTask:
    """Represents a build task for the orchestrator."""

    name: str
    files: list[Path]
    plugin: BuilderPlugin
    options: dict[str, Any]
    dependencies: list[str] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class BuildPlan:
    """Represents a complete build plan."""

    tasks: list[BuildTask]
    execution_order: list[str]
    estimated_duration: float
    parallelizable_groups: list[list[str]]


class PluginBuildOrchestrator:
    """
    Plugin-aware build orchestrator.

    Automatically discovers plugins, selects appropriate plugins for files,
    and orchestrates parallel execution with dependency resolution.
    """

    def __init__(self, context: BuildContext):
        self.context = context
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Initialize plugin system
        self.plugin_registry = PluginRegistry(context)
        self.plugin_registry.discover_plugins()

        # Build state
        self.build_cache = {}
        self.build_results = {}

        # Performance tracking
        self.build_metrics = {"total_builds": 0, "cache_hits": 0, "cache_misses": 0, "parallel_efficiency": 0.0}

    def create_build_plan(self, target_files: list[Path], options: dict[str, Any] = None) -> BuildPlan:
        """
        Create an optimized build plan for the given files.

        Args:
            target_files: Files to build
            options: Build options

        Returns:
            BuildPlan with tasks and execution order
        """
        options = options or {}
        self.logger.info(f"📋 Creating build plan for {len(target_files)} files")

        # Group files by best plugin
        plugin_groups = self._group_files_by_plugin(target_files)

        # Create build tasks
        tasks = []
        for plugin, files in plugin_groups.items():
            task_name = f"{plugin.metadata.name}_build"

            # Get plugin-specific options
            plugin_options = options.get(plugin.metadata.name, {})

            task = BuildTask(name=task_name, files=files, plugin=plugin, options=plugin_options)
            tasks.append(task)

        # Calculate dependencies and execution order
        execution_order = self._calculate_execution_order(tasks)
        parallelizable_groups = self._find_parallelizable_groups(tasks)

        # Estimate total duration
        estimated_duration = self._estimate_build_duration(tasks, parallelizable_groups)

        build_plan = BuildPlan(
            tasks=tasks,
            execution_order=execution_order,
            estimated_duration=estimated_duration,
            parallelizable_groups=parallelizable_groups,
        )

        self._log_build_plan(build_plan)
        return build_plan

    def _group_files_by_plugin(self, files: list[Path]) -> dict[BuilderPlugin, list[Path]]:
        """Group files by their best-matching plugin."""
        plugin_groups = {}
        unhandled_files = []

        for file_path in files:
            plugins = self.plugin_registry.get_plugins_for_file(file_path)

            if plugins:
                # Use the highest priority plugin
                best_plugin = plugins[0]

                if best_plugin not in plugin_groups:
                    plugin_groups[best_plugin] = []
                plugin_groups[best_plugin].append(file_path)
            else:
                unhandled_files.append(file_path)

        if unhandled_files:
            self.logger.warning(f"⚠️ No plugins found for {len(unhandled_files)} files:")
            for file_path in unhandled_files[:5]:  # Show first 5
                self.logger.warning(f"  • {file_path}")
            if len(unhandled_files) > 5:
                self.logger.warning(f"  • ... and {len(unhandled_files) - 5} more")

        return plugin_groups

    def _calculate_execution_order(self, tasks: list[BuildTask]) -> list[str]:
        """Calculate optimal execution order for tasks."""
        # For now, simple ordering by plugin priority
        # TODO: Implement proper dependency graph resolution

        task_priorities = {}
        for task in tasks:
            # Plugins with more capabilities get higher priority
            priority = len(task.plugin.metadata.capabilities)
            task_priorities[task.name] = priority

        # Sort by priority (higher first)
        ordered_tasks = sorted(tasks, key=lambda t: task_priorities[t.name], reverse=True)
        return [task.name for task in ordered_tasks]

    def _find_parallelizable_groups(self, tasks: list[BuildTask]) -> list[list[str]]:
        """Find groups of tasks that can be executed in parallel."""
        # Simple grouping: tasks with parallel capability can run together
        parallel_tasks = []
        sequential_tasks = []

        for task in tasks:
            if task.plugin.supports_capability(PluginCapability.PARALLEL_BUILD):
                parallel_tasks.append(task.name)
            else:
                sequential_tasks.append(task.name)

        groups = []
        if parallel_tasks:
            groups.append(parallel_tasks)

        # Sequential tasks each get their own group
        for task_name in sequential_tasks:
            groups.append([task_name])

        return groups

    def _estimate_build_duration(self, tasks: list[BuildTask], groups: list[list[str]]) -> float:
        """Estimate total build duration considering parallelization."""
        total_duration = 0.0

        task_map = {task.name: task for task in tasks}

        for group in groups:
            if len(group) == 1:
                # Sequential task
                task = task_map[group[0]]
                duration = task.plugin.get_estimated_duration(task.files, task.options)
                total_duration += duration
            else:
                # Parallel group - use maximum duration
                max_duration = 0.0
                for task_name in group:
                    task = task_map[task_name]
                    duration = task.plugin.get_estimated_duration(task.files, task.options)
                    max_duration = max(max_duration, duration)
                total_duration += max_duration

        return total_duration

    def execute_build_plan(self, build_plan: BuildPlan) -> dict[str, PluginResult]:
        """
        Execute the build plan.

        Args:
            build_plan: Plan to execute

        Returns:
            Dict mapping task names to their results
        """
        start_time = time.time()
        self.logger.info(f"🚀 Executing build plan with {len(build_plan.tasks)} tasks")

        task_map = {task.name: task for task in build_plan.tasks}
        results = {}

        # Execute parallelizable groups
        for group in build_plan.parallelizable_groups:
            if len(group) == 1:
                # Sequential execution
                task_name = group[0]
                task = task_map[task_name]

                self.logger.info(f"🔧 Executing task: {task_name}")
                result = self._execute_task(task)
                results[task_name] = result

                if not result.success:
                    self.logger.error(f"❌ Task {task_name} failed: {result.error_message}")
                    break
            else:
                # Parallel execution
                self.logger.info(f"⚡ Executing {len(group)} tasks in parallel")
                parallel_results = self._execute_tasks_parallel([task_map[name] for name in group])
                results.update(parallel_results)

                # Check if any parallel task failed
                failed_tasks = [name for name, result in parallel_results.items() if not result.success]
                if failed_tasks:
                    self.logger.error(f"❌ Parallel tasks failed: {failed_tasks}")
                    break

        # Update metrics
        total_duration = time.time() - start_time
        self._update_build_metrics(results, total_duration, build_plan.estimated_duration)

        self.logger.info(f"✅ Build plan completed in {total_duration:.2f}s")
        return results

    def _execute_task(self, task: BuildTask) -> PluginResult:
        """Execute a single build task."""
        self.build_metrics["total_builds"] += 1

        # Check cache first
        cache_key = self._calculate_task_cache_key(task)
        if cache_key in self.build_cache:
            self.build_metrics["cache_hits"] += 1
            self.logger.debug(f"💾 Cache hit for task: {task.name}")
            return self.build_cache[cache_key]

        self.build_metrics["cache_misses"] += 1

        # Validate plugin environment
        env_errors = task.plugin.validate_environment()
        if env_errors:
            return PluginResult(
                success=False,
                duration=0.0,
                artifacts=[],
                error_message=f"Environment validation failed: {'; '.join(env_errors)}",
            )

        # Execute the build
        result = task.plugin.build(task.files, task.options)

        # Cache successful results
        if result.success:
            self.build_cache[cache_key] = result

        return result

    def _execute_tasks_parallel(self, tasks: list[BuildTask]) -> dict[str, PluginResult]:
        """Execute multiple tasks in parallel."""
        results = {}

        with ThreadPoolExecutor(max_workers=min(len(tasks), 4)) as executor:
            # Submit all tasks
            future_to_task = {executor.submit(self._execute_task, task): task for task in tasks}

            # Collect results
            for future in as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    result = future.result()
                    results[task.name] = result
                except Exception as e:
                    self.logger.error(f"Task {task.name} raised exception: {e}")
                    results[task.name] = PluginResult(
                        success=False, duration=0.0, artifacts=[], error_message=f"Task execution failed: {e}"
                    )

        return results

    def _calculate_task_cache_key(self, task: BuildTask) -> str:
        """Calculate cache key for a task."""
        # Combine file checksums with plugin version and options
        file_checksum = task.plugin.calculate_checksum(task.files)
        plugin_version = task.plugin.metadata.version
        options_str = str(sorted(task.options.items()))

        combined = f"{file_checksum}:{plugin_version}:{options_str}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]

    def _update_build_metrics(
        self, results: dict[str, PluginResult], actual_duration: float, estimated_duration: float
    ):
        """Update build performance metrics."""
        successful_builds = sum(1 for result in results.values() if result.success)
        total_builds = len(results)

        # Calculate parallel efficiency
        if estimated_duration > 0:
            self.build_metrics["parallel_efficiency"] = estimated_duration / actual_duration

        self.logger.info(
            f"📊 Build metrics: {successful_builds}/{total_builds} successful, "
            f"cache hit rate: {self.build_metrics['cache_hits']}/{self.build_metrics['total_builds']}"
        )

    def _log_build_plan(self, build_plan: BuildPlan):
        """Log build plan details."""
        self.logger.info("📋 Build Plan Summary:")
        self.logger.info(f"   Tasks: {len(build_plan.tasks)}")
        self.logger.info(f"   Estimated duration: {build_plan.estimated_duration:.1f}s")
        self.logger.info(f"   Parallel groups: {len(build_plan.parallelizable_groups)}")

        for i, task in enumerate(build_plan.tasks):
            plugin_name = task.plugin.metadata.name
            file_count = len(task.files)
            self.logger.info(f"   {i + 1}. {task.name} ({plugin_name}) - {file_count} files")

    def get_plugin_info(self) -> dict[str, Any]:
        """Get information about registered plugins."""
        return {
            "registered_plugins": self.plugin_registry.list_plugins(),
            "plugin_validation": self.plugin_registry.validate_all_plugins(),
            "build_metrics": self.build_metrics,
        }

    def clean_all(self, target_files: list[Path]) -> dict[str, PluginResult]:
        """Clean build artifacts for all files."""
        self.logger.info(f"🧹 Cleaning artifacts for {len(target_files)} files")

        plugin_groups = self._group_files_by_plugin(target_files)
        results = {}

        for plugin, files in plugin_groups.items():
            task_name = f"{plugin.metadata.name}_clean"
            self.logger.info(f"🗑️ Cleaning with {plugin.metadata.name}")

            result = plugin.clean(files)
            results[task_name] = result

            if not result.success:
                self.logger.error(f"❌ Clean failed for {plugin.metadata.name}: {result.error_message}")

        return results
