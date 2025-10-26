#!/usr/bin/env python3

"""
@llm-type service
@llm-legend C/C++ build module with CMake integration and CFFI bindings
@llm-key Provides optimized C builds with CMake, custom memory management, and Python CFFI integration
@llm-map C build module that integrates with CMake build system and provides graphics rendering capabilities
@llm-axiom C builds must be deterministic, fast, and provide direct CPU instruction access for maximum performance
@llm-contract Returns BuildModuleResult with shared library artifacts and CFFI bindings
@llm-token c-builder: CMake-based build module for C graphics rendering layer

C Graphics Build Module

Provides optimized builds for C graphics rendering projects with:
- CMake configuration and build management
- SIMD optimization detection (AVX2, NEON)
- Platform-specific optimizations
- CFFI Python bindings generation
- Custom memory allocators
- Performance profiling integration

Author: Unhinged Team
Version: 1.0.0
Date: 2025-10-25
"""

import os
import platform
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional
try:
    from . import BuildModule, BuildContext, BuildModuleResult, BuildUtils, BuildArtifact
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from __init__ import BuildModule, BuildContext, BuildModuleResult, BuildUtils, BuildArtifact

class CBuilder(BuildModule):
    """Build module for C graphics rendering projects using CMake"""
    
    def __init__(self, context: BuildContext):
        super().__init__(context)
        self.graphics_dir = self.context.project_root / "libs" / "graphics"
        self.build_dir = self.graphics_dir / "build"
        self.install_dir = self.context.project_root / "generated" / "c" / "graphics"
        self.cffi_dir = self.context.project_root / "generated" / "python" / "graphics"
        
    def can_handle(self, target_name: str) -> bool:
        """Check if this module can handle C graphics targets"""
        c_targets = {
            'c-graphics-build', 'c-graphics-test', 'c-graphics-install',
            'graphics-render', 'graphics-primitives', 'graphics-simd',
            'graphics-memory', 'graphics-platform', 'graphics-cffi'
        }
        return (target_name in c_targets or 
                'graphics' in target_name or 
                'c-' in target_name)
    
    def get_dependencies(self, target_name: str) -> List[str]:
        """Get C source dependencies"""
        dependencies = []
        
        if not self.graphics_dir.exists():
            return dependencies
            
        # C source files
        for c_file in self.graphics_dir.rglob("*.c"):
            dependencies.append(str(c_file))
        
        # Header files
        for h_file in self.graphics_dir.rglob("*.h"):
            dependencies.append(str(h_file))
            
        # CMake files
        for cmake_file in self.graphics_dir.rglob("CMakeLists.txt"):
            dependencies.append(str(cmake_file))
        
        # CFFI build scripts
        cffi_build = self.graphics_dir / "cffi_build.py"
        if cffi_build.exists():
            dependencies.append(str(cffi_build))
        
        return dependencies
    
    def calculate_cache_key(self, target_name: str) -> str:
        """Calculate cache key based on source files and configuration"""
        import hashlib
        hasher = hashlib.sha256()
        
        # Include target name
        hasher.update(target_name.encode())
        
        # Hash source files
        if self.graphics_dir.exists():
            src_hash = BuildUtils.calculate_directory_hash(
                self.graphics_dir,
                patterns=["*.c", "*.h", "CMakeLists.txt", "*.py"]
            )
            hasher.update(src_hash.encode())
        
        # Include compiler version and platform
        compiler_info = self._get_compiler_info()
        hasher.update(compiler_info.encode())
        
        # Include platform and architecture
        platform_info = f"{platform.system()}-{platform.machine()}"
        hasher.update(platform_info.encode())
        
        return hasher.hexdigest()
    
    def validate_environment(self) -> List[str]:
        """Validate C build environment (all dependencies are REQUIRED - HARD FAIL)"""
        errors = []

        # Check CMake (REQUIRED)
        if not BuildUtils.check_tool_available("cmake"):
            errors.append("CMake is REQUIRED but not found in PATH - install with: sudo apt-get install cmake")

        # Check C compiler (REQUIRED)
        if not (BuildUtils.check_tool_available("gcc") or
                BuildUtils.check_tool_available("clang")):
            errors.append("C compiler (gcc or clang) is REQUIRED but not found - install with: sudo apt-get install build-essential")

        # Check Python for CFFI (REQUIRED)
        if not BuildUtils.check_tool_available("python3"):
            errors.append("Python3 is REQUIRED but not found in PATH")

        # Check CFFI availability in centralized Python environment (REQUIRED)
        venv_python = self.context.project_root / "build" / "python" / "venv" / "bin" / "python"
        if venv_python.exists():
            try:
                result = subprocess.run([str(venv_python), "-c", "import cffi"],
                                      capture_output=True, text=True)
                if result.returncode != 0:
                    errors.append("CFFI is REQUIRED but not available in centralized Python environment")
            except Exception:
                errors.append("CFFI is REQUIRED but not available in centralized Python environment")
        else:
            errors.append("Centralized Python environment not found - run: cd build/python && python3 setup.py")

        # HARD REQUIREMENT: DRM headers for native C graphics (CRITICAL)
        drm_errors = self._validate_drm_environment()
        if drm_errors:
            errors.extend(drm_errors)

        return errors

    def _validate_drm_environment(self) -> List[str]:
        """Validate DRM environment for native C graphics (HARD REQUIREMENT)"""
        errors = []

        # Check for DRM headers (CRITICAL for native C graphics)
        drm_headers = [
            "/usr/include/xf86drm.h",
            "/usr/include/xf86drmMode.h",
            "/usr/include/drm/drm.h",
            "/usr/include/drm/drm_mode.h"
        ]

        missing_headers = []
        for header in drm_headers:
            if not Path(header).exists():
                missing_headers.append(header)

        if missing_headers:
            errors.append(f"CRITICAL: DRM headers REQUIRED for native C graphics but missing: {missing_headers}")
            errors.append("Install with: sudo apt-get install libdrm-dev")

        # Check for libdrm library
        try:
            result = subprocess.run(["pkg-config", "--exists", "libdrm"],
                                  capture_output=True, text=True)
            if result.returncode != 0:
                errors.append("CRITICAL: libdrm development library REQUIRED but not found")
                errors.append("Install with: sudo apt-get install libdrm-dev")
        except FileNotFoundError:
            errors.append("pkg-config not found - install with: sudo apt-get install pkg-config")

        # Test DRM compilation capability
        test_drm_errors = self._test_drm_compilation()
        if test_drm_errors:
            errors.extend(test_drm_errors)

        return errors

    def _test_drm_compilation(self) -> List[str]:
        """Test DRM compilation capability with detailed diagnostics"""
        errors = []

        # Create a minimal DRM test program
        test_code = '''
#include <stdio.h>
#include <xf86drm.h>
#include <xf86drmMode.h>
#include <drm/drm.h>
#include <drm/drm_mode.h>

int main() {
    printf("DRM compilation test successful\\n");
    return 0;
}
'''

        # Write test file
        test_dir = self.context.project_root / "build" / "tmp"
        test_dir.mkdir(parents=True, exist_ok=True)
        test_file = test_dir / "drm_test.c"

        try:
            with open(test_file, 'w') as f:
                f.write(test_code)

            # Attempt compilation
            result = subprocess.run([
                "gcc", "-o", str(test_dir / "drm_test"), str(test_file), "-ldrm"
            ], capture_output=True, text=True)

            if result.returncode != 0:
                errors.append(f"CRITICAL: DRM compilation test FAILED - {result.stderr}")
                errors.append("This is a HARD REQUIREMENT for native C graphics")

            # Clean up test files
            test_file.unlink(missing_ok=True)
            (test_dir / "drm_test").unlink(missing_ok=True)

        except Exception as e:
            errors.append(f"CRITICAL: DRM compilation test failed with exception: {e}")

        return errors

    def get_estimated_duration(self, target_name: str) -> float:
        """Estimate build duration based on target type"""
        duration_map = {
            'c-graphics-build': 45.0,
            'c-graphics-test': 30.0,
            'c-graphics-install': 15.0,
            'graphics-cffi': 20.0,
            'graphics-simd': 60.0,  # Longer due to optimization testing
        }
        return duration_map.get(target_name, 30.0)
    
    def supports_incremental_build(self, target_name: str) -> bool:
        """C supports incremental builds with CMake"""
        return target_name in ['c-graphics-build', 'graphics-primitives', 'graphics-simd']
    
    def supports_parallel_build(self, target_name: str) -> bool:
        """CMake supports parallel builds"""
        return True
    
    def build(self, target_name: str) -> BuildModuleResult:
        """Execute C graphics build"""
        start_time = time.time()
        
        # HARD FAIL REQUIREMENT: Validate environment first - ALL DEPENDENCIES ARE REQUIRED
        env_errors = self.validate_environment()
        if env_errors:
            error_msg = f"🚨 HARD FAIL: C Graphics dependencies are REQUIRED but missing:\n" + '\n'.join(f"  - {error}" for error in env_errors)
            error_msg += f"\n\n🔧 Run 'make graphics-install-deps' to install required dependencies."
            error_msg += f"\n\n⚠️  CRITICAL: Native C graphics compilation is a HARD REQUIREMENT for Unhinged dual-system architecture."
            error_msg += f"\n   The system CANNOT proceed without functional DRM graphics support."

            # Log to centralized event framework
            self._log_graphics_failure(target_name, env_errors)

            return BuildModuleResult(
                success=False,
                duration=0.0,
                artifacts=[],
                error_message=error_msg
            )
        
        # Determine build steps based on target
        build_steps = self._get_build_steps(target_name)
        if not build_steps:
            return BuildModuleResult(
                success=False,
                duration=0.0,
                artifacts=[],
                error_message=f"Unknown C graphics target: {target_name}"
            )
        
        self.logger.info(f"🔧 Building C graphics target '{target_name}'")
        
        # Execute build steps
        all_artifacts = []
        all_warnings = []
        all_metrics = {}
        
        for step_name, command, working_dir in build_steps:
            self.logger.info(f"🔨 {step_name}: {command}")
            
            success, stdout, stderr = BuildUtils.run_command(
                command,
                working_dir,
                timeout=300  # 5 minutes for C builds
            )
            
            if not success:
                duration = time.time() - start_time
                return BuildModuleResult(
                    success=False,
                    duration=duration,
                    artifacts=all_artifacts,
                    error_message=f"Step '{step_name}' failed: {stderr}",
                    warnings=all_warnings
                )
            
            # Collect warnings from this step
            step_warnings = self._extract_warnings(stderr)
            all_warnings.extend(step_warnings)
            
            # Collect metrics from this step
            step_metrics = self._extract_build_metrics(stdout, step_name)
            all_metrics.update(step_metrics)
        
        # Collect build artifacts
        artifacts = self._collect_artifacts(target_name)
        all_artifacts.extend(artifacts)
        
        duration = time.time() - start_time
        
        self.logger.info(f"✅ C graphics build '{target_name}' completed in {duration:.2f}s")
        
        return BuildModuleResult(
            success=True,
            duration=duration,
            artifacts=all_artifacts,
            warnings=all_warnings,
            metrics=all_metrics
        )
    
    def clean(self, target_name: str) -> bool:
        """Clean C build artifacts"""
        try:
            if self.build_dir.exists():
                import shutil
                shutil.rmtree(self.build_dir)
            return True
        except Exception as e:
            self.logger.error(f"Failed to clean C build artifacts: {e}")
            return False
    
    def _get_compiler_info(self) -> str:
        """Get compiler version information"""
        try:
            if BuildUtils.check_tool_available("gcc"):
                result = subprocess.run(["gcc", "--version"], 
                                      capture_output=True, text=True)
                return result.stdout.split('\n')[0] if result.returncode == 0 else "gcc-unknown"
            elif BuildUtils.check_tool_available("clang"):
                result = subprocess.run(["clang", "--version"], 
                                      capture_output=True, text=True)
                return result.stdout.split('\n')[0] if result.returncode == 0 else "clang-unknown"
        except Exception:
            pass
        return "unknown-compiler"

    def _get_build_steps(self, target_name: str) -> List[tuple]:
        """Get build steps for the target"""
        steps = []

        # Ensure directories exist
        self.build_dir.mkdir(parents=True, exist_ok=True)
        self.install_dir.mkdir(parents=True, exist_ok=True)

        if target_name in ['c-graphics-build', 'graphics-primitives', 'graphics-simd']:
            # CMake configure step
            cmake_args = self._get_cmake_args(target_name)
            configure_cmd = f"cmake {' '.join(cmake_args)} {self.graphics_dir}"
            steps.append(("CMake Configure", configure_cmd, self.build_dir))

            # Build step
            parallel_jobs = os.cpu_count() or 4
            build_cmd = f"cmake --build . --parallel {parallel_jobs}"
            steps.append(("CMake Build", build_cmd, self.build_dir))

        if target_name in ['c-graphics-install', 'graphics-cffi']:
            # Install step
            install_cmd = f"cmake --install . --prefix {self.install_dir}"
            steps.append(("CMake Install", install_cmd, self.build_dir))

        if target_name == 'graphics-cffi':
            # CFFI binding generation using centralized Python environment
            venv_python = self.context.project_root / "build" / "python" / "venv" / "bin" / "python"
            cffi_cmd = f"{venv_python} cffi_build.py"
            steps.append(("CFFI Build", cffi_cmd, self.graphics_dir))

        if target_name == 'c-graphics-test':
            # Test step
            test_cmd = "ctest --output-on-failure"
            steps.append(("CTest", test_cmd, self.build_dir))

        return steps

    def _get_cmake_args(self, target_name: str) -> List[str]:
        """Get CMake configuration arguments"""
        args = [
            f"-DCMAKE_BUILD_TYPE={'Debug' if self.context.environment == 'development' else 'Release'}",
            f"-DCMAKE_INSTALL_PREFIX={self.install_dir}",
            "-DBUILD_SHARED_LIBS=ON",
            "-DENABLE_SIMD=ON",
            "-DENABLE_TESTING=ON"
        ]

        # Platform-specific optimizations
        if platform.system() == "Linux":
            args.append("-DENABLE_DRM=ON")
            args.append("-DENABLE_WAYLAND=ON")

        # SIMD detection
        if self._supports_avx2():
            args.append("-DENABLE_AVX2=ON")
        if self._supports_neon():
            args.append("-DENABLE_NEON=ON")

        return args

    def _supports_avx2(self) -> bool:
        """Check if the platform supports AVX2"""
        try:
            if platform.machine() in ['x86_64', 'AMD64']:
                # Check /proc/cpuinfo on Linux
                if platform.system() == "Linux":
                    with open('/proc/cpuinfo', 'r') as f:
                        cpuinfo = f.read()
                        return 'avx2' in cpuinfo
                # For other platforms, assume modern x86_64 supports AVX2
                return True
        except Exception:
            pass
        return False

    def _supports_neon(self) -> bool:
        """Check if the platform supports NEON"""
        try:
            if platform.machine() in ['aarch64', 'arm64']:
                return True
            if platform.machine().startswith('arm'):
                # Check /proc/cpuinfo on Linux
                if platform.system() == "Linux":
                    with open('/proc/cpuinfo', 'r') as f:
                        cpuinfo = f.read()
                        return 'neon' in cpuinfo
        except Exception:
            pass
        return False

    def _extract_warnings(self, stderr: str) -> List[str]:
        """Extract warnings from compiler output"""
        warnings = []
        for line in stderr.split('\n'):
            if 'warning:' in line.lower():
                warnings.append(line.strip())
        return warnings

    def _extract_build_metrics(self, stdout: str, step_name: str) -> Dict[str, any]:
        """Extract build metrics from output"""
        metrics = {}

        # Extract compilation time if available
        for line in stdout.split('\n'):
            if 'Built target' in line:
                metrics[f'{step_name}_targets'] = metrics.get(f'{step_name}_targets', 0) + 1
            if 'Linking' in line:
                metrics[f'{step_name}_linking'] = True

        return metrics

    def _collect_artifacts(self, target_name: str) -> List[BuildArtifact]:
        """Collect build artifacts"""
        artifacts = []

        # Shared library artifacts
        lib_patterns = ["*.so", "*.dylib", "*.dll"]
        for pattern in lib_patterns:
            for lib_file in self.build_dir.rglob(pattern):
                if lib_file.is_file():
                    artifacts.append(BuildUtils.create_build_artifact(
                        lib_file, "shared_library",
                        {"target": target_name, "language": "c"}
                    ))

        # Static library artifacts
        for static_lib in self.build_dir.rglob("*.a"):
            if static_lib.is_file():
                artifacts.append(BuildUtils.create_build_artifact(
                    static_lib, "static_library",
                    {"target": target_name, "language": "c"}
                ))

        # Header files in install directory
        for header in self.install_dir.rglob("*.h"):
            if header.is_file():
                artifacts.append(BuildUtils.create_build_artifact(
                    header, "header",
                    {"target": target_name, "language": "c"}
                ))

        # CFFI artifacts
        for cffi_file in self.cffi_dir.rglob("*.py"):
            if cffi_file.is_file():
                artifacts.append(BuildUtils.create_build_artifact(
                    cffi_file, "cffi_binding",
                    {"target": target_name, "language": "python"}
                ))

        return artifacts

    def _log_graphics_failure(self, target_name: str, errors: List[str]):
        """Log graphics build failure to centralized event framework"""
        try:
            # Import session logging if available
            import sys
            sys.path.append(str(self.context.project_root / "libs" / "event-framework" / "python" / "src"))
            from unhinged_events import create_gui_session_logger

            logger = create_gui_session_logger(self.context.project_root)
            logger.log_gui_event(
                "GRAPHICS_BUILD_HARD_FAIL",
                f"Native C graphics build HARD FAIL for target '{target_name}': {'; '.join(errors)}"
            )
            logger.log_platform_output(f"🚨 CRITICAL: Graphics compilation failed - dual-system architecture compromised")
            logger.close_session()

        except Exception as e:
            # Fallback to standard logging if event framework unavailable
            self.logger.error(f"Failed to log graphics failure to event framework: {e}")
            self.logger.error(f"Graphics build HARD FAIL: {errors}")
