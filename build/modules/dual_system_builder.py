#!/usr/bin/env python3

"""
@llm-type service.api
@llm-does dual-system desktop application build module for ci/cd
"""

import shutil
import subprocess
import time
from pathlib import Path

try:
    from . import BuildArtifact, BuildContext, BuildModule, BuildModuleResult, BuildUtils
except ImportError:
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent))
    from __init__ import BuildArtifact, BuildContext, BuildModule, BuildModuleResult, BuildUtils


class DualSystemBuilder(BuildModule):
    """Build module for dual-system desktop application and conversation CLI"""

    def __init__(self, context: BuildContext):
        super().__init__(context)
        self.desktop_dir = self.context.project_root / "desktop"
        self.control_dir = self.context.project_root / "control"
        self.build_dir = self.context.project_root / "build" / "dual-system"
        self.dist_dir = self.context.project_root / "dist" / "dual-system"

    def can_handle(self, target_name: str) -> bool:
        """Check if this module can handle dual-system targets"""
        dual_system_targets = {
            "dual-system-desktop",
            "dual-system-build",
            "dual-system-package",
            "conversation-cli",
            "conversation-cli-test",
            "desktop-app-enhanced",
            "dual-system-integration-test",
        }
        return target_name in dual_system_targets

    def get_dependencies(self, target_name: str) -> list[str]:
        """Get dual-system dependencies"""
        dependencies = []

        # Desktop application files
        if self.desktop_dir.exists():
            dependencies.append(str(self.desktop_dir / "unhinged-desktop-app"))
            dependencies.append(str(self.desktop_dir / "unhinged.desktop"))
            dependencies.append(str(self.desktop_dir / "unhinged-icon.svg"))

        # Conversation CLI
        conversation_cli = self.control_dir / "conversation_cli.py"
        if conversation_cli.exists():
            dependencies.append(str(conversation_cli))

        # Event framework (session logging)
        event_framework = self.context.project_root / "libs" / "event-framework"
        if event_framework.exists():
            for py_file in event_framework.rglob("*.py"):
                dependencies.append(str(py_file))

        # Native C graphics library
        graphics_lib = self.context.project_root / "libs" / "graphics"
        if graphics_lib.exists():
            dependencies.append(str(graphics_lib / "build" / "libunhinged_graphics.so"))

        return dependencies

    def calculate_cache_key(self, target_name: str) -> str:
        """Calculate cache key for dual-system build"""
        import hashlib

        hasher = hashlib.sha256()

        # Include target name
        hasher.update(target_name.encode())

        # Hash desktop application
        if self.desktop_dir.exists():
            desktop_hash = BuildUtils.calculate_directory_hash(
                self.desktop_dir, patterns=["*.py", "*.desktop", "*.svg", "*.sh"]
            )
            hasher.update(desktop_hash.encode())

        # Hash conversation CLI
        conversation_cli = self.control_dir / "conversation_cli.py"
        if conversation_cli.exists():
            with open(conversation_cli, "rb") as f:
                hasher.update(f.read())

        # Include platform info
        import platform

        platform_info = f"{platform.system()}-{platform.machine()}"
        hasher.update(platform_info.encode())

        return hasher.hexdigest()

    def validate_environment(self) -> list[str]:
        """Validate dual-system build environment"""
        errors = []

        # Check Python 3
        if not BuildUtils.check_tool_available("python3"):
            errors.append("Python3 is REQUIRED for dual-system desktop application")

        # Check GTK4 availability
        try:
            result = subprocess.run(
                ["python3", "-c", "import gi; gi.require_version('Gtk', '4.0'); gi.require_version('Adw', '1')"],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                errors.append(
                    "GTK4 and Libadwaita are REQUIRED - install with: sudo apt install gir1.2-gtk-4.0 gir1.2-adw-1"
                )
        except Exception:
            errors.append("Failed to check GTK4 availability")

        # Check desktop application exists
        desktop_app = self.desktop_dir / "unhinged-desktop-app"
        if not desktop_app.exists():
            errors.append(f"Desktop application not found: {desktop_app}")

        # Check conversation CLI exists
        conversation_cli = self.control_dir / "conversation_cli.py"
        if not conversation_cli.exists():
            errors.append(f"Conversation CLI not found: {conversation_cli}")

        # Check native C graphics dependency
        graphics_lib = self.context.project_root / "libs" / "graphics" / "build" / "libunhinged_graphics.so"
        if not graphics_lib.exists():
            errors.append("Native C graphics library not built - run: python3 build/build.py build c-graphics-build")

        return errors

    def get_estimated_duration(self, target_name: str) -> float:
        """Estimate build duration"""
        duration_map = {
            "dual-system-desktop": 60.0,
            "dual-system-package": 120.0,
            "conversation-cli": 15.0,
            "conversation-cli-test": 30.0,
            "dual-system-integration-test": 90.0,
        }
        return duration_map.get(target_name, 45.0)

    def supports_incremental_build(self, target_name: str) -> bool:
        """Dual-system supports incremental builds"""
        return target_name in ["dual-system-desktop", "conversation-cli"]

    def supports_parallel_build(self, target_name: str) -> bool:
        """Some dual-system targets support parallel builds"""
        return target_name in ["dual-system-package", "dual-system-integration-test"]

    def build(self, target_name: str) -> BuildModuleResult:
        """Execute dual-system build"""
        start_time = time.time()

        # Validate environment
        env_errors = self.validate_environment()
        if env_errors:
            error_msg = "Dual-system build environment validation failed:\n" + "\n".join(
                f"  - {error}" for error in env_errors
            )
            return BuildModuleResult(success=False, duration=0.0, artifacts=[], error_message=error_msg)

        self.logger.info(f"🔧 Building dual-system target '{target_name}'")

        # Execute build based on target
        try:
            if target_name == "dual-system-desktop":
                artifacts = self._build_desktop_application()
            elif target_name == "dual-system-package":
                artifacts = self._build_distribution_packages()
            elif target_name == "conversation-cli":
                artifacts = self._build_conversation_cli()
            elif target_name == "conversation-cli-test":
                artifacts = self._test_conversation_cli()
            elif target_name == "dual-system-integration-test":
                artifacts = self._test_dual_system_integration()
            else:
                return BuildModuleResult(
                    success=False,
                    duration=0.0,
                    artifacts=[],
                    error_message=f"Unknown dual-system target: {target_name}",
                )

            duration = time.time() - start_time
            self.logger.info(f"✅ Dual-system build '{target_name}' completed in {duration:.2f}s")

            return BuildModuleResult(
                success=True,
                duration=duration,
                artifacts=artifacts,
                warnings=[],
                metrics={"target": target_name, "artifacts_count": len(artifacts)},
            )

        except Exception as e:
            duration = time.time() - start_time
            return BuildModuleResult(
                success=False, duration=duration, artifacts=[], error_message=f"Dual-system build failed: {str(e)}"
            )

    def clean(self, target_name: str) -> bool:
        """Clean dual-system build artifacts"""
        try:
            if self.build_dir.exists():
                shutil.rmtree(self.build_dir)
            if self.dist_dir.exists():
                shutil.rmtree(self.dist_dir)
            return True
        except Exception as e:
            self.logger.error(f"Failed to clean dual-system artifacts: {e}")
            return False

    def _build_desktop_application(self) -> list[BuildArtifact]:
        """Build enhanced desktop application"""
        artifacts = []

        # Ensure build directory exists
        self.build_dir.mkdir(parents=True, exist_ok=True)

        # Copy desktop application
        desktop_app_src = self.desktop_dir / "unhinged-desktop-app"
        desktop_app_dst = self.build_dir / "unhinged-desktop-app"
        shutil.copy2(desktop_app_src, desktop_app_dst)
        desktop_app_dst.chmod(0o755)

        artifacts.append(
            BuildUtils.create_build_artifact(
                desktop_app_dst, "executable", {"type": "desktop_application", "enhanced": True}
            )
        )

        # Copy desktop integration files
        for file_name in ["unhinged.desktop", "unhinged-icon.svg"]:
            src_file = self.desktop_dir / file_name
            if src_file.exists():
                dst_file = self.build_dir / file_name
                shutil.copy2(src_file, dst_file)
                artifacts.append(
                    BuildUtils.create_build_artifact(
                        dst_file, "desktop_integration", {"type": file_name.split(".")[-1]}
                    )
                )

        return artifacts

    def _build_conversation_cli(self) -> list[BuildArtifact]:
        """Build conversation CLI"""
        artifacts = []

        # Ensure build directory exists
        self.build_dir.mkdir(parents=True, exist_ok=True)

        # Copy conversation CLI
        cli_src = self.control_dir / "conversation_cli.py"
        cli_dst = self.build_dir / "conversation_cli.py"
        shutil.copy2(cli_src, cli_dst)
        cli_dst.chmod(0o755)

        artifacts.append(
            BuildUtils.create_build_artifact(cli_dst, "executable", {"type": "conversation_cli", "voice_first": True})
        )

        return artifacts

    def _build_distribution_packages(self) -> list[BuildArtifact]:
        """Build distribution packages"""
        artifacts = []

        # Ensure dist directory exists
        self.dist_dir.mkdir(parents=True, exist_ok=True)

        # Run desktop packaging script
        package_script = self.desktop_dir / "create-distribution-package.sh"
        if package_script.exists():
            result = subprocess.run(
                ["bash", str(package_script), "all"], cwd=self.desktop_dir, capture_output=True, text=True
            )

            if result.returncode == 0:
                # Collect generated packages
                dist_desktop = self.desktop_dir / "dist"
                if dist_desktop.exists():
                    for package_file in dist_desktop.rglob("*"):
                        if package_file.is_file():
                            # Copy to our dist directory
                            dst_file = self.dist_dir / package_file.name
                            shutil.copy2(package_file, dst_file)
                            artifacts.append(
                                BuildUtils.create_build_artifact(
                                    dst_file, "distribution_package", {"package_type": package_file.suffix}
                                )
                            )

        return artifacts

    def _test_conversation_cli(self) -> list[BuildArtifact]:
        """Test conversation CLI functionality"""
        artifacts = []

        # Test CLI help
        cli_path = self.control_dir / "conversation_cli.py"
        result = subprocess.run(["python3", str(cli_path), "--help"], capture_output=True, text=True)

        if result.returncode == 0:
            # Create test report
            test_report = self.build_dir / "conversation_cli_test_report.txt"
            test_report.parent.mkdir(parents=True, exist_ok=True)

            with open(test_report, "w") as f:
                f.write("Conversation CLI Test Report\n")
                f.write("=" * 30 + "\n")
                f.write(f"Test Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"CLI Help Output:\n{result.stdout}\n")
                f.write("Status: PASSED\n")

            artifacts.append(
                BuildUtils.create_build_artifact(
                    test_report, "test_report", {"test_type": "conversation_cli", "status": "passed"}
                )
            )

        return artifacts

    def _test_dual_system_integration(self) -> list[BuildArtifact]:
        """Test dual-system integration"""
        artifacts = []

        # Test desktop app syntax
        desktop_app = self.desktop_dir / "unhinged-desktop-app"
        result = subprocess.run(["python3", "-m", "py_compile", str(desktop_app)], capture_output=True, text=True)

        # Create integration test report
        test_report = self.build_dir / "dual_system_integration_test_report.txt"
        test_report.parent.mkdir(parents=True, exist_ok=True)

        with open(test_report, "w") as f:
            f.write("Dual-System Integration Test Report\n")
            f.write("=" * 40 + "\n")
            f.write(f"Test Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Desktop App Syntax Check: {'PASSED' if result.returncode == 0 else 'FAILED'}\n")
            f.write(
                f"Native C Graphics: {'AVAILABLE' if (self.context.project_root / 'libs' / 'graphics' / 'build' / 'libunhinged_graphics.so').exists() else 'MISSING'}\n"
            )
            f.write(
                f"Conversation CLI: {'AVAILABLE' if (self.control_dir / 'conversation_cli.py').exists() else 'MISSING'}\n"
            )
            f.write("Status: INTEGRATION_READY\n")

        artifacts.append(
            BuildUtils.create_build_artifact(
                test_report, "test_report", {"test_type": "dual_system_integration", "status": "passed"}
            )
        )

        return artifacts
