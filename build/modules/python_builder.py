#!/usr/bin/env python3

"""
@llm-type service.api
@llm-does python build module with virtual environment management
"""

import os
import re
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

class PythonBuilder(BuildModule):
    """Build module for Python projects using pip/poetry"""
    
    def __init__(self, context: BuildContext):
        super().__init__(context)
        self.services_dir = self.context.project_root / "services"
        self.venv_dir = self.context.project_root / ".venv"
        
    def can_handle(self, target_name: str) -> bool:
        """Check if this module can handle Python targets"""
        python_targets = {
            'python-build', 'python-test', 'python-install',
            'whisper-tts-build', 'vision-ai-build', 'context-llm-build',
            'services-build', 'python-services'
        }
        return (target_name in python_targets or 
                'python' in target_name or 
                any(service in target_name for service in ['whisper-tts', 'vision-ai', 'context-llm']))
    
    def get_dependencies(self, target_name: str) -> List[str]:
        """Get Python source dependencies"""
        dependencies = []
        
        # Determine which Python service we're building
        service_dirs = self._get_service_directories(target_name)
        
        for service_dir in service_dirs:
            if not service_dir.exists():
                continue
                
            # Python source files
            for py_file in service_dir.rglob("*.py"):
                dependencies.append(str(py_file))
            
            # Requirements files
            for req_file in ["requirements.txt", "pyproject.toml", "setup.py", "setup.cfg"]:
                req_path = service_dir / req_file
                if req_path.exists():
                    dependencies.append(str(req_path))
            
            # Dockerfile for containerized services
            dockerfile = service_dir / "Dockerfile"
            if dockerfile.exists():
                dependencies.append(str(dockerfile))
        
        return dependencies
    
    def calculate_cache_key(self, target_name: str) -> str:
        """Calculate cache key based on source files and requirements"""
        import hashlib
        hasher = hashlib.sha256()
        
        # Include target name
        hasher.update(target_name.encode())
        
        # Hash source files for relevant services
        service_dirs = self._get_service_directories(target_name)
        for service_dir in service_dirs:
            if service_dir.exists():
                src_hash = BuildUtils.calculate_directory_hash(
                    service_dir,
                    patterns=["*.py", "requirements.txt", "pyproject.toml"]
                )
                hasher.update(src_hash.encode())
        
        # Include Python version
        python_version = self._get_python_version()
        hasher.update(python_version.encode())
        
        return hasher.hexdigest()
    
    def validate_environment(self) -> List[str]:
        """Validate Python environment"""
        errors = []
        
        # Check if Python is available
        if not BuildUtils.check_tool_available("python3"):
            errors.append("Python 3 not found in PATH")
        
        # Check if pip is available
        if not BuildUtils.check_tool_available("pip3"):
            errors.append("pip3 not found in PATH")
        
        # Check Python version
        python_version = self._get_python_version()
        if python_version.startswith("3."):
            version_parts = python_version.split(".")
            if len(version_parts) >= 2:
                major, minor = int(version_parts[0]), int(version_parts[1])
                if major < 3 or (major == 3 and minor < 8):
                    errors.append(f"Python 3.8+ required, found {python_version}")
        else:
            errors.append(f"Invalid Python version: {python_version}")
        
        return errors
    
    def get_estimated_duration(self, target_name: str) -> float:
        """Estimate build duration based on target type"""
        duration_map = {
            'python-install': 45.0,
            'python-build': 30.0,
            'python-test': 60.0,
            'whisper-tts-build': 90.0,  # Longer due to ML dependencies
            'vision-ai-build': 120.0,   # Longer due to ML dependencies
            'context-llm-build': 60.0
        }
        return duration_map.get(target_name, 45.0)
    
    def supports_incremental_build(self, target_name: str) -> bool:
        """Python supports incremental builds for some targets"""
        return 'install' not in target_name  # Installation always needs to be complete
    
    def supports_parallel_build(self, target_name: str) -> bool:
        """Python builds can be parallelized"""
        return True
    
    def build(self, target_name: str) -> BuildModuleResult:
        """Execute Python build"""
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
        
        # Determine build steps based on target
        build_steps = self._get_build_steps(target_name)
        if not build_steps:
            return BuildModuleResult(
                success=False,
                duration=0.0,
                artifacts=[],
                error_message=f"Unknown Python target: {target_name}"
            )
        
        self.logger.info(f"🐍 Building Python target '{target_name}'")
        
        # Execute build steps
        all_artifacts = []
        all_warnings = []
        all_metrics = {}
        
        for step_name, command, working_dir in build_steps:
            self.logger.info(f"🔧 {step_name}: {command}")
            
            success, stdout, stderr = BuildUtils.run_command(
                command,
                working_dir,
                timeout=600  # 10 minutes for Python builds (ML deps can be slow)
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
            step_warnings = self._extract_warnings(stdout)
            all_warnings.extend(step_warnings)
            
            # Collect metrics from this step
            step_metrics = self._extract_build_metrics(stdout, step_name)
            all_metrics.update(step_metrics)
        
        # Collect build artifacts
        artifacts = self._collect_artifacts(target_name)
        all_artifacts.extend(artifacts)
        
        duration = time.time() - start_time
        
        self.logger.info(f"✅ Python build '{target_name}' completed in {duration:.2f}s")
        
        return BuildModuleResult(
            success=True,
            duration=duration,
            artifacts=all_artifacts,
            warnings=all_warnings,
            metrics=all_metrics
        )
    
    def clean(self, target_name: str) -> bool:
        """Clean Python build artifacts"""
        service_dirs = self._get_service_directories(target_name)
        
        for service_dir in service_dirs:
            if not service_dir.exists():
                continue
            
            # Remove __pycache__ directories
            for pycache in service_dir.rglob("__pycache__"):
                if pycache.is_dir():
                    import shutil
                    shutil.rmtree(pycache)
            
            # Remove .pyc files
            for pyc_file in service_dir.rglob("*.pyc"):
                pyc_file.unlink()
            
            # Remove build directories
            for build_dir in ["build", "dist", "*.egg-info"]:
                for path in service_dir.glob(build_dir):
                    if path.is_dir():
                        import shutil
                        shutil.rmtree(path)
        
        return True
    
    def _get_service_directories(self, target_name: str) -> List[Path]:
        """Get list of service directories based on target"""
        if 'whisper-tts' in target_name:
            return [self.services_dir / "whisper-tts"]
        elif 'vision-ai' in target_name:
            return [self.services_dir / "vision-ai"]
        elif 'context-llm' in target_name:
            return [self.services_dir / "context-llm"]
        elif target_name in ['python-build', 'python-test', 'services-build']:
            # All Python services
            python_services = []
            for service_dir in self.services_dir.iterdir():
                if service_dir.is_dir() and (service_dir / "requirements.txt").exists():
                    python_services.append(service_dir)
            return python_services
        else:
            return []
    
    def _get_build_steps(self, target_name: str) -> List[tuple]:
        """Get build steps for the target"""
        steps = []
        service_dirs = self._get_service_directories(target_name)
        
        for service_dir in service_dirs:
            if not service_dir.exists():
                continue
            
            service_name = service_dir.name
            
            # Install dependencies
            if (service_dir / "requirements.txt").exists():
                steps.append((
                    f"Install {service_name} dependencies",
                    "pip3 install -r requirements.txt",
                    service_dir
                ))
            elif (service_dir / "pyproject.toml").exists():
                steps.append((
                    f"Install {service_name} dependencies",
                    "pip3 install .",
                    service_dir
                ))
            
            # Run tests if this is a test target
            if 'test' in target_name:
                if (service_dir / "tests").exists():
                    steps.append((
                        f"Run {service_name} tests",
                        "python3 -m pytest tests/ -v",
                        service_dir
                    ))
                elif (service_dir / "test.py").exists():
                    steps.append((
                        f"Run {service_name} tests",
                        "python3 test.py",
                        service_dir
                    ))
            
            # Build package if this is a build target
            if 'build' in target_name and (service_dir / "setup.py").exists():
                steps.append((
                    f"Build {service_name} package",
                    "python3 setup.py build",
                    service_dir
                ))
        
        return steps
    
    def _get_python_version(self) -> str:
        """Get Python version for cache key"""
        try:
            result = subprocess.run(
                ["python3", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                # Output is like "Python 3.9.7"
                return result.stdout.strip().split()[-1]
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            pass
        
        return "unknown"
    
    def _collect_artifacts(self, target_name: str) -> List[BuildArtifact]:
        """Collect build artifacts from Python build"""
        artifacts = []
        service_dirs = self._get_service_directories(target_name)
        
        for service_dir in service_dirs:
            if not service_dir.exists():
                continue
            
            # Python packages
            dist_dir = service_dir / "dist"
            if dist_dir.exists():
                for wheel_file in dist_dir.glob("*.whl"):
                    artifacts.append(BuildUtils.create_build_artifact(
                        wheel_file,
                        "python_wheel",
                        {"service": service_dir.name}
                    ))
                
                for tar_file in dist_dir.glob("*.tar.gz"):
                    artifacts.append(BuildUtils.create_build_artifact(
                        tar_file,
                        "python_sdist",
                        {"service": service_dir.name}
                    ))
            
            # Test reports
            if 'test' in target_name:
                for report_file in service_dir.glob("test-report*.xml"):
                    artifacts.append(BuildUtils.create_build_artifact(
                        report_file,
                        "test_report",
                        {"format": "junit", "service": service_dir.name}
                    ))
        
        return artifacts
    
    def _extract_warnings(self, python_output: str) -> List[str]:
        """Extract warnings from Python output"""
        warnings = []
        
        for line in python_output.split('\n'):
            if any(keyword in line.lower() for keyword in ['warning:', 'deprecated', 'warn']):
                warnings.append(line.strip())
        
        return warnings
    
    def _extract_build_metrics(self, python_output: str, step_name: str) -> Dict[str, any]:
        """Extract build metrics from Python output"""
        metrics = {}
        
        # Extract pip install metrics
        if 'install' in step_name.lower():
            # Count installed packages
            installed_pattern = r'Successfully installed (.+)'
            match = re.search(installed_pattern, python_output)
            if match:
                packages = match.group(1).split()
                metrics[f'{step_name}_packages_installed'] = len(packages)
        
        # Extract test metrics
        if 'test' in step_name.lower():
            # pytest output
            test_pattern = r'(\d+) passed.*?(\d+) failed.*?(\d+) error'
            match = re.search(test_pattern, python_output)
            if match:
                metrics[f'{step_name}_tests_passed'] = int(match.group(1))
                metrics[f'{step_name}_tests_failed'] = int(match.group(2))
                metrics[f'{step_name}_tests_errors'] = int(match.group(3))
        
        return metrics
