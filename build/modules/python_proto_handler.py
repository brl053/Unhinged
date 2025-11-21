#!/usr/bin/env python3

"""
@llm-type config.build
@llm-does python protobuf client generation handler for ai/ml
"""

from pathlib import Path

try:
    from . import BuildArtifact, BuildContext, BuildUtils
    from .polyglot_proto_engine import ProtoLanguageConfig, ProtoLanguageHandler
except ImportError:
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent))
    from __init__ import BuildArtifact, BuildUtils
    from polyglot_proto_engine import ProtoLanguageHandler


class PythonProtoHandler(ProtoLanguageHandler):
    """Python protobuf client generation handler"""

    def validate_tools(self) -> list[str]:
        """Validate Python protobuf tools are available"""
        missing_tools = []

        # Check for protoc
        if not BuildUtils.check_tool_available("protoc"):
            missing_tools.append("protoc")

        # Check for Python
        if not BuildUtils.check_tool_available("python3"):
            missing_tools.append("python3")

        # Check for grpcio-tools (protoc-gen-python)
        try:
            import grpc_tools
        except ImportError:
            missing_tools.append("grpcio-tools (run: pip install grpcio-tools)")

        return missing_tools

    def prepare_output_directory(self, output_dir: Path) -> bool:
        """Prepare Python output directory structure"""
        try:
            # Create Python package structure
            clients_dir = output_dir / "unhinged_proto_clients"
            clients_dir.mkdir(parents=True, exist_ok=True)

            # Create __init__.py files for proper Python packages
            init_files = [output_dir / "__init__.py", clients_dir / "__init__.py"]

            for init_file in init_files:
                if not init_file.exists():
                    with open(init_file, "w") as f:
                        f.write('"""Generated Unhinged Proto Clients"""\n')

            # Create setup.py for package installation
            setup_content = self._generate_setup_py()
            setup_file = output_dir / "setup.py"
            with open(setup_file, "w") as f:
                f.write(setup_content)

            # Create requirements.txt
            requirements_content = self._generate_requirements()
            requirements_file = output_dir / "requirements.txt"
            with open(requirements_file, "w") as f:
                f.write(requirements_content)

            # Create pyproject.toml for modern Python packaging
            pyproject_content = self._generate_pyproject_toml()
            pyproject_file = output_dir / "pyproject.toml"
            with open(pyproject_file, "w") as f:
                f.write(pyproject_content)

            return True

        except Exception as e:
            self.logger.error(f"Failed to prepare Python output directory: {e}")
            return False

    def build_protoc_command(self, proto_files: list[Path], output_dir: Path, proto_path: Path) -> list[str]:
        """Build protoc command for Python generation"""
        clients_dir = output_dir / "unhinged_proto_clients"

        cmd = [
            "python3",
            "-m",
            "grpc_tools.protoc",
            f"--proto_path={proto_path}",
            f"--python_out={clients_dir}",
            f"--grpc_python_out={clients_dir}",
        ]

        # Add proto files
        cmd.extend([str(pf) for pf in proto_files])

        return cmd

    def post_process_artifacts(self, output_dir: Path) -> list[BuildArtifact]:
        """Post-process Python generated files"""
        artifacts = []
        clients_dir = output_dir / "unhinged_proto_clients"

        try:
            # Fix import statements in generated files
            self._fix_python_imports(clients_dir)

            # Collect all generated Python files
            for py_file in clients_dir.rglob("*.py"):
                if py_file.name != "__init__.py":
                    artifacts.append(
                        BuildUtils.create_build_artifact(py_file, "python-client", {"language": "python", "grpc": True})
                    )

            # Create artifacts for package files
            setup_file = output_dir / "setup.py"
            if setup_file.exists():
                artifacts.append(
                    BuildUtils.create_build_artifact(
                        setup_file, "python-setup", {"language": "python", "type": "setup"}
                    )
                )

            requirements_file = output_dir / "requirements.txt"
            if requirements_file.exists():
                artifacts.append(
                    BuildUtils.create_build_artifact(
                        requirements_file, "python-requirements", {"language": "python", "type": "requirements"}
                    )
                )

            pyproject_file = output_dir / "pyproject.toml"
            if pyproject_file.exists():
                artifacts.append(
                    BuildUtils.create_build_artifact(
                        pyproject_file, "python-pyproject", {"language": "python", "type": "pyproject"}
                    )
                )

            # Update main __init__.py with exports
            self._update_main_init(output_dir, clients_dir)
            main_init = output_dir / "__init__.py"
            if main_init.exists():
                artifacts.append(
                    BuildUtils.create_build_artifact(
                        main_init, "python-init", {"language": "python", "type": "package-init"}
                    )
                )

            self.logger.info(f"Generated {len(artifacts)} Python proto artifacts")

        except Exception as e:
            self.logger.error(f"Error post-processing Python artifacts: {e}")

        return artifacts

    def _fix_python_imports(self, clients_dir: Path):
        """Fix relative imports in generated Python files"""
        try:
            for py_file in clients_dir.rglob("*_pb2_grpc.py"):
                content = py_file.read_text()

                # Fix imports to use relative imports within package
                lines = content.split("\n")
                fixed_lines = []

                for line in lines:
                    if line.startswith("import ") and "_pb2" in line:
                        # Convert absolute imports to relative imports
                        module_name = line.split("import ")[1].strip()
                        if not module_name.startswith("."):
                            fixed_line = f"from . import {module_name}"
                            fixed_lines.append(fixed_line)
                        else:
                            fixed_lines.append(line)
                    else:
                        fixed_lines.append(line)

                py_file.write_text("\n".join(fixed_lines))

        except Exception as e:
            self.logger.warning(f"Failed to fix Python imports: {e}")

    def _update_main_init(self, output_dir: Path, clients_dir: Path):
        """Update main __init__.py with exports"""
        try:
            exports = []

            # Find all generated modules
            for py_file in clients_dir.rglob("*_pb2.py"):
                if py_file.name != "__init__.py":
                    module_name = py_file.stem
                    exports.append(f"from .unhinged_proto_clients import {module_name}")

            if exports:
                init_content = (
                    '''"""
Unhinged Protocol Buffer Clients (Python)

Generated Python protobuf clients for the Unhinged platform.
Provides gRPC client stubs for all platform services.
"""

'''
                    + "\n".join(sorted(exports))
                    + """

__version__ = "1.0.0"
__author__ = "Unhinged Team"
"""
                )

                init_file = output_dir / "__init__.py"
                with open(init_file, "w") as f:
                    f.write(init_content)

        except Exception as e:
            self.logger.error(f"Failed to update Python main init: {e}")

    def _generate_setup_py(self) -> str:
        """Generate setup.py for Python package"""
        return '''#!/usr/bin/env python3
"""Setup script for Unhinged Proto Clients (Python)"""

from setuptools import setup, find_packages

setup(
    name="unhinged-proto-clients",
    version="1.0.0",
    description="Generated Python protobuf clients for Unhinged platform",
    author="Unhinged Team",
    author_email="team@unhinged.dev",
    packages=find_packages(),
    install_requires=[
        "grpcio>=1.50.0",
        "grpcio-tools>=1.50.0",
        "protobuf>=4.21.0",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="protobuf grpc unhinged",
)
'''

    def _generate_requirements(self) -> str:
        """Generate requirements.txt"""
        return """grpcio>=1.50.0
grpcio-tools>=1.50.0
protobuf>=4.21.0
"""

    def _generate_pyproject_toml(self) -> str:
        """Generate pyproject.toml for modern Python packaging"""
        return """[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "unhinged-proto-clients"
version = "1.0.0"
description = "Generated Python protobuf clients for Unhinged platform"
authors = [{name = "Unhinged Team", email = "team@unhinged.dev"}]
license = {text = "MIT"}
requires-python = ">=3.8"
dependencies = [
    "grpcio>=1.50.0",
    "grpcio-tools>=1.50.0",
    "protobuf>=4.21.0",
]
keywords = ["protobuf", "grpc", "unhinged"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
]

[project.urls]
Homepage = "https://github.com/unhinged/proto-clients"
Repository = "https://github.com/unhinged/proto-clients.git"
"""
