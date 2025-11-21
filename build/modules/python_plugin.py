#!/usr/bin/env python3
"""
Python Builder Plugin

Implements the standardized plugin interface for Python builds.
Handles Python projects using pip/poetry with unified virtual environment.

@llm-type plugin.python
@llm-does python builds with standardized plugin interface
"""

import re
import time
from pathlib import Path
from typing import Any

try:
    from ..core.plugin_interface import (
        BuildArtifact,
        BuilderPlugin,
        FilePattern,
        PluginCapability,
        PluginMetadata,
        PluginResult,
    )
    from . import BuildContext, BuildUtils
except ImportError:
    import sys

    sys.path.insert(0, str(Path(__file__).parent.parent))
    from core.plugin_interface import (
        BuildArtifact,
        BuilderPlugin,
        FilePattern,
        PluginCapability,
        PluginMetadata,
        PluginResult,
    )

    from modules import BuildContext


class PythonBuilderPlugin(BuilderPlugin):
    """Python builder implementing standardized plugin interface."""

    def __init__(self, context: BuildContext):
        super().__init__(context)
        self.services_dir = self.context.project_root / "services"
        self.venv_dir = self.context.project_root / ".venv"
        self.python_executable = self.venv_dir / "bin" / "python3"
        self.pip_executable = self.venv_dir / "bin" / "pip"

    @property
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        return PluginMetadata(
            name="python",
            version="2.0.0",
            description="Python builder with unified virtual environment support",
            author="Unhinged Build System",
            supported_extensions=[".py", ".pyx", ".pyi"],
            capabilities={
                PluginCapability.INCREMENTAL_BUILD,
                PluginCapability.PARALLEL_BUILD,
                PluginCapability.DEPENDENCY_RESOLUTION,
                PluginCapability.CACHE_OPTIMIZATION,
                PluginCapability.TESTING,
                PluginCapability.LINTING,
                PluginCapability.PACKAGING,
            },
            dependencies=["python3", "pip"],
        )

    @property
    def file_patterns(self) -> list[FilePattern]:
        """Return file patterns this plugin can handle."""
        return [
            FilePattern(".py", priority=10, required_files=["requirements.txt"]),
            FilePattern(".py", priority=8, required_files=["pyproject.toml"]),
            FilePattern(".py", priority=5),  # Generic Python files
            FilePattern(".pyx", priority=7),  # Cython files
            FilePattern(".pyi", priority=3),  # Type stub files
        ]

    def detect_files(self, path: Path) -> list[Path]:
        """Return list of Python files this builder handles."""
        python_files = []

        # Look for Python files
        for pattern in ["**/*.py", "**/*.pyx", "**/*.pyi"]:
            python_files.extend(path.glob(pattern))

        # Filter out common non-source directories
        excluded_dirs = {".venv", "__pycache__", ".git", "node_modules", "build", "dist"}

        filtered_files = []
        for file_path in python_files:
            # Check if file is in excluded directory
            if any(excluded_dir in file_path.parts for excluded_dir in excluded_dirs):
                continue
            filtered_files.append(file_path)

        return filtered_files

    def calculate_checksum(self, file_paths: list[Path]) -> str:
        """Calculate content-based checksum for caching."""
        return self._calculate_combined_checksum(file_paths)

    def get_dependencies(self, file_paths: list[Path]) -> list[Path]:
        """Get list of file dependencies for Python files."""
        dependencies = set()

        for file_path in file_paths:
            # Add requirements files
            req_files = [
                file_path.parent / "requirements.txt",
                file_path.parent / "pyproject.toml",
                file_path.parent / "setup.py",
                file_path.parent / "setup.cfg",
            ]

            for req_file in req_files:
                if req_file.exists():
                    dependencies.add(req_file)

            # Parse imports from Python files
            if file_path.suffix == ".py":
                imported_files = self._parse_local_imports(file_path)
                dependencies.update(imported_files)

        return list(dependencies)

    def _parse_local_imports(self, file_path: Path) -> list[Path]:
        """Parse local imports from a Python file."""
        local_imports = []

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Find relative imports
            import_patterns = [
                r"from\s+\.(\w+)\s+import",  # from .module import
                r"from\s+\.\.(\w+)\s+import",  # from ..module import
                r"import\s+\.(\w+)",  # import .module
            ]

            base_dir = file_path.parent

            for pattern in import_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    # Convert module name to file path
                    module_file = base_dir / f"{match}.py"
                    if module_file.exists():
                        local_imports.append(module_file)

        except Exception as e:
            self.logger.warning(f"Failed to parse imports from {file_path}: {e}")

        return local_imports

    def validate_environment(self) -> list[str]:
        """Validate Python environment."""
        missing_requirements = []

        # Check Python executable
        if not self._check_tool_available("python3"):
            missing_requirements.append("python3")

        # Check unified virtual environment
        if not self.venv_dir.exists():
            missing_requirements.append("unified virtual environment (.venv)")

        # Check pip in venv
        if not self.pip_executable.exists():
            missing_requirements.append("pip in virtual environment")

        return missing_requirements

    def build(self, file_paths: list[Path], options: dict[str, Any] = None) -> PluginResult:
        """Execute Python build."""
        start_time = time.time()
        options = options or {}

        # Validate environment
        env_errors = self.validate_environment()
        if env_errors:
            return PluginResult(
                success=False,
                duration=0.0,
                artifacts=[],
                error_message=f"Environment validation failed: {'; '.join(env_errors)}",
            )

        self.logger.info(f"🐍 Building {len(file_paths)} Python files")

        artifacts = []
        warnings = []

        # Group files by service/project
        projects = self._group_files_by_project(file_paths)

        for project_path, project_files in projects.items():
            self.logger.info(f"📦 Building Python project: {project_path}")

            # Install dependencies if requirements exist
            req_result = self._install_dependencies(project_path)
            if not req_result.success:
                return req_result

            artifacts.extend(req_result.artifacts)
            warnings.extend(req_result.warnings)

            # Compile Python files (syntax check)
            compile_result = self._compile_python_files(project_files)
            if not compile_result.success:
                return compile_result

            artifacts.extend(compile_result.artifacts)
            warnings.extend(compile_result.warnings)

        duration = time.time() - start_time

        return PluginResult(
            success=True,
            duration=duration,
            artifacts=artifacts,
            warnings=warnings,
            metrics={"files_processed": len(file_paths), "projects_built": len(projects)},
        )

    def _group_files_by_project(self, file_paths: list[Path]) -> dict[Path, list[Path]]:
        """Group files by their containing project/service."""
        projects = {}

        for file_path in file_paths:
            # Find the project root (directory with requirements.txt or pyproject.toml)
            project_root = self._find_project_root(file_path)

            if project_root not in projects:
                projects[project_root] = []
            projects[project_root].append(file_path)

        return projects

    def _find_project_root(self, file_path: Path) -> Path:
        """Find the project root for a Python file."""
        current = file_path.parent

        # Look for project indicators
        project_files = ["requirements.txt", "pyproject.toml", "setup.py", "setup.cfg"]

        while current != self.context.project_root.parent:
            for project_file in project_files:
                if (current / project_file).exists():
                    return current
            current = current.parent

        # Default to file's directory
        return file_path.parent

    def _install_dependencies(self, project_path: Path) -> PluginResult:
        """Install dependencies for a Python project."""
        start_time = time.time()
        artifacts = []

        # Check for requirements files
        req_files = [project_path / "requirements.txt", project_path / "pyproject.toml"]

        for req_file in req_files:
            if req_file.exists():
                self.logger.info(f"📋 Installing dependencies from {req_file}")

                if req_file.name == "requirements.txt":
                    command = f"{self.pip_executable} install -r {req_file}"
                else:  # pyproject.toml
                    command = f"{self.pip_executable} install -e {project_path}"

                success, stdout, stderr = self._run_command(command, project_path)

                if not success:
                    return PluginResult(
                        success=False,
                        duration=time.time() - start_time,
                        artifacts=[],
                        error_message=f"Dependency installation failed: {stderr}",
                    )

                # Create artifact for successful installation
                artifacts.append(
                    BuildArtifact(
                        path=req_file,
                        artifact_type="dependencies",
                        size_bytes=req_file.stat().st_size,
                        checksum=self._calculate_file_checksum(req_file),
                        metadata={"installed": True},
                    )
                )

        return PluginResult(success=True, duration=time.time() - start_time, artifacts=artifacts)

    def _compile_python_files(self, file_paths: list[Path]) -> PluginResult:
        """Compile Python files (syntax check)."""
        start_time = time.time()
        artifacts = []
        warnings = []

        for file_path in file_paths:
            if file_path.suffix != ".py":
                continue

            # Compile for syntax checking
            command = f"{self.python_executable} -m py_compile {file_path}"
            success, stdout, stderr = self._run_command(command, file_path.parent)

            if not success:
                return PluginResult(
                    success=False,
                    duration=time.time() - start_time,
                    artifacts=[],
                    error_message=f"Python compilation failed for {file_path}: {stderr}",
                )

            # Create artifact for compiled file
            artifacts.append(
                BuildArtifact(
                    path=file_path,
                    artifact_type="compiled",
                    size_bytes=file_path.stat().st_size,
                    checksum=self._calculate_file_checksum(file_path),
                    metadata={"compiled": True},
                )
            )

        return PluginResult(success=True, duration=time.time() - start_time, artifacts=artifacts, warnings=warnings)

    def clean(self, file_paths: list[Path]) -> PluginResult:
        """Remove Python build artifacts."""
        start_time = time.time()
        cleaned_files = []

        for file_path in file_paths:
            # Remove __pycache__ directories
            pycache_dir = file_path.parent / "__pycache__"
            if pycache_dir.exists():
                import shutil

                shutil.rmtree(pycache_dir)
                cleaned_files.append(pycache_dir)

            # Remove .pyc files
            pyc_file = file_path.with_suffix(".pyc")
            if pyc_file.exists():
                pyc_file.unlink()
                cleaned_files.append(pyc_file)

        return PluginResult(
            success=True, duration=time.time() - start_time, artifacts=[], metrics={"files_cleaned": len(cleaned_files)}
        )

    def test(self, file_paths: list[Path], options: dict[str, Any] = None) -> PluginResult:
        """Run Python tests."""
        start_time = time.time()

        # Find test files
        test_files = [f for f in file_paths if "test" in f.name.lower()]

        if not test_files:
            return PluginResult(
                success=True, duration=time.time() - start_time, artifacts=[], warnings=["No test files found"]
            )

        # Run pytest if available
        command = f"{self.python_executable} -m pytest {' '.join(str(f) for f in test_files)}"
        success, stdout, stderr = self._run_command(command, self.context.project_root)

        return PluginResult(
            success=success,
            duration=time.time() - start_time,
            artifacts=[],
            error_message=stderr if not success else None,
            metrics={"tests_run": len(test_files)},
        )

    def lint(self, file_paths: list[Path], options: dict[str, Any] = None) -> PluginResult:
        """Run Python linting."""
        start_time = time.time()
        warnings = []

        # Run flake8 if available
        py_files = [f for f in file_paths if f.suffix == ".py"]
        command = f"{self.python_executable} -m flake8 {' '.join(str(f) for f in py_files)}"
        success, stdout, stderr = self._run_command(command, self.context.project_root)

        if stdout:
            warnings.extend(stdout.split("\n"))

        return PluginResult(
            success=True,  # Linting warnings don't fail the build
            duration=time.time() - start_time,
            artifacts=[],
            warnings=warnings,
            metrics={"files_linted": len(py_files)},
        )
