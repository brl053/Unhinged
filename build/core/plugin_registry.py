#!/usr/bin/env python3
"""
Plugin Registry for Build System

Manages registration, discovery, and selection of build plugins.
Provides centralized plugin management with automatic discovery.

@llm-type core.plugin-registry
@llm-does plugin discovery and management for build system
"""

import importlib
import importlib.util
import inspect
import logging
from pathlib import Path

from .plugin_interface import BuilderPlugin, PluginCapability, PluginMetadata


class PluginRegistry:
    """
    Central registry for build system plugins.

    Handles plugin discovery, registration, and selection based on
    file patterns and capabilities.
    """

    def __init__(self, context: "BuildContext"):
        self.context = context
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Registry storage
        self._plugins: dict[str, BuilderPlugin] = {}
        self._plugin_classes: dict[str, type[BuilderPlugin]] = {}
        self._file_pattern_map: dict[str, list[str]] = {}  # extension -> plugin names
        self._capability_map: dict[PluginCapability, list[str]] = {}  # capability -> plugin names

        # Discovery paths
        self.plugin_paths = [
            self.context.project_root / "build" / "modules",
            self.context.project_root / "build" / "plugins",  # Future extension point
        ]

    def discover_plugins(self) -> int:
        """
        Discover and register all available plugins.

        Returns:
            Number of plugins discovered and registered
        """
        self.logger.info("🔍 Discovering build plugins...")

        discovered_count = 0

        for plugin_path in self.plugin_paths:
            if not plugin_path.exists():
                continue

            discovered_count += self._discover_plugins_in_path(plugin_path)

        self._build_lookup_maps()

        self.logger.info(f"✅ Discovered {discovered_count} plugins")
        self._log_plugin_summary()

        return discovered_count

    def _discover_plugins_in_path(self, path: Path) -> int:
        """Discover plugins in a specific directory."""
        count = 0

        # Look for Python files that might contain plugins
        plugin_patterns = ["*_builder.py", "*_plugin.py"]

        for pattern in plugin_patterns:
            for py_file in path.glob(pattern):
                if py_file.name.startswith("__"):
                    continue

                try:
                    plugin_class = self._load_plugin_from_file(py_file)
                    if plugin_class:
                        self.register_plugin_class(plugin_class)
                        count += 1

                except Exception as e:
                    self.logger.warning(f"Failed to load plugin from {py_file}: {e}")

        return count

    def _load_plugin_from_file(self, py_file: Path) -> type[BuilderPlugin] | None:
        """Load plugin class from Python file."""
        module_name = py_file.stem

        # Import the module
        spec = importlib.util.spec_from_file_location(module_name, py_file)
        if not spec or not spec.loader:
            return None

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Find BuilderPlugin subclasses
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, BuilderPlugin) and obj != BuilderPlugin and not inspect.isabstract(obj):
                return obj

        return None

    def register_plugin_class(self, plugin_class: type[BuilderPlugin]) -> bool:
        """
        Register a plugin class.

        Args:
            plugin_class: Plugin class to register

        Returns:
            True if registered successfully
        """
        try:
            # Create instance to get metadata
            plugin_instance = plugin_class(self.context)
            plugin_name = plugin_instance.metadata.name

            self._plugin_classes[plugin_name] = plugin_class
            self._plugins[plugin_name] = plugin_instance

            self.logger.debug(f"Registered plugin: {plugin_name}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to register plugin {plugin_class.__name__}: {e}")
            return False

    def register_plugin_instance(self, plugin: BuilderPlugin) -> bool:
        """
        Register a plugin instance directly.

        Args:
            plugin: Plugin instance to register

        Returns:
            True if registered successfully
        """
        try:
            plugin_name = plugin.metadata.name
            self._plugins[plugin_name] = plugin
            self._plugin_classes[plugin_name] = plugin.__class__

            self.logger.debug(f"Registered plugin instance: {plugin_name}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to register plugin instance: {e}")
            return False

    def _build_lookup_maps(self):
        """Build lookup maps for efficient plugin selection."""
        self._file_pattern_map.clear()
        self._capability_map.clear()

        for plugin_name, plugin in self._plugins.items():
            # Build file pattern map
            for pattern in plugin.file_patterns:
                ext = pattern.extension
                if ext not in self._file_pattern_map:
                    self._file_pattern_map[ext] = []
                self._file_pattern_map[ext].append(plugin_name)

            # Build capability map
            for capability in plugin.metadata.capabilities:
                if capability not in self._capability_map:
                    self._capability_map[capability] = []
                self._capability_map[capability].append(plugin_name)

    def get_plugin(self, name: str) -> BuilderPlugin | None:
        """Get plugin by name."""
        return self._plugins.get(name)

    def get_plugins_for_file(self, file_path: Path) -> list[BuilderPlugin]:
        """
        Get plugins that can handle the given file.

        Args:
            file_path: File to find plugins for

        Returns:
            List of plugins that can handle the file, sorted by priority
        """
        extension = file_path.suffix.lower()
        plugin_names = self._file_pattern_map.get(extension, [])

        plugins = []
        for name in plugin_names:
            plugin = self._plugins.get(name)
            if plugin:
                plugins.append(plugin)

        # Sort by pattern priority (higher priority first)
        def get_priority(plugin: BuilderPlugin) -> int:
            for pattern in plugin.file_patterns:
                if pattern.extension == extension:
                    return pattern.priority
            return 0

        plugins.sort(key=get_priority, reverse=True)
        return plugins

    def get_plugins_with_capability(self, capability: PluginCapability) -> list[BuilderPlugin]:
        """
        Get plugins that support a specific capability.

        Args:
            capability: Capability to search for

        Returns:
            List of plugins with the capability
        """
        plugin_names = self._capability_map.get(capability, [])
        return [self._plugins[name] for name in plugin_names if name in self._plugins]

    def get_best_plugin_for_files(self, file_paths: list[Path]) -> BuilderPlugin | None:
        """
        Get the best plugin to handle a set of files.

        Args:
            file_paths: Files to find plugin for

        Returns:
            Best plugin for the files, or None if no plugin can handle them
        """
        if not file_paths:
            return None

        # Count how many files each plugin can handle
        plugin_scores = {}

        for file_path in file_paths:
            plugins = self.get_plugins_for_file(file_path)
            for plugin in plugins:
                name = plugin.metadata.name
                if name not in plugin_scores:
                    plugin_scores[name] = 0
                plugin_scores[name] += 1

        if not plugin_scores:
            return None

        # Return plugin that can handle the most files
        best_plugin_name = max(plugin_scores.keys(), key=lambda k: plugin_scores[k])
        return self._plugins[best_plugin_name]

    def list_plugins(self) -> list[str]:
        """Get list of all registered plugin names."""
        return list(self._plugins.keys())

    def get_plugin_info(self, name: str) -> PluginMetadata | None:
        """Get metadata for a specific plugin."""
        plugin = self._plugins.get(name)
        return plugin.metadata if plugin else None

    def validate_all_plugins(self) -> dict[str, list[str]]:
        """
        Validate all registered plugins.

        Returns:
            Dict mapping plugin names to lists of missing requirements
        """
        validation_results = {}

        for name, plugin in self._plugins.items():
            try:
                missing_requirements = plugin.validate_environment()
                validation_results[name] = missing_requirements
            except Exception as e:
                validation_results[name] = [f"Validation failed: {e}"]

        return validation_results

    def _log_plugin_summary(self):
        """Log summary of registered plugins."""
        if not self._plugins:
            return

        self.logger.info("📋 Registered plugins:")
        for name, plugin in self._plugins.items():
            metadata = plugin.metadata
            extensions = ", ".join(metadata.supported_extensions)
            capabilities = len(metadata.capabilities)
            self.logger.info(f"  • {name} v{metadata.version} - {extensions} ({capabilities} capabilities)")

    def clear(self):
        """Clear all registered plugins."""
        self._plugins.clear()
        self._plugin_classes.clear()
        self._file_pattern_map.clear()
        self._capability_map.clear()
