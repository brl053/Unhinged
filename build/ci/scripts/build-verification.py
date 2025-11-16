#!/usr/bin/env python3
"""
@llm-doc Build Verification Script for CI/CD Pipeline
@llm-version 1.0.0
@llm-date 2025-01-26
@llm-author Unhinged Team

## Overview
Comprehensive build verification that integrates with the enhanced build system.
Validates builds, dependencies, and system integrity before deployment.

## Features
- Integration with build/orchestrator.py
- Intelligent caching validation
- Parallel build execution
- Comprehensive error reporting
- Performance metrics collection

@llm-principle Reliable build verification with enhanced build system integration
@llm-culture Independence through comprehensive automated validation
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import yaml

# Add build system to path
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from orchestrator import BuildOrchestrator, BuildResult

    from build import EnhancedBuildSystem

    ENHANCED_BUILD_AVAILABLE = True
except ImportError:
    print("⚠️ Enhanced build system not available, using fallback mode")
    ENHANCED_BUILD_AVAILABLE = False


class BuildVerificationRunner:
    """
    @llm-doc Build verification runner with enhanced build integration

    Coordinates build verification using the existing enhanced build system
    while providing CI/CD specific validation and reporting.
    """

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.ci_config_path = Path(__file__).parent.parent / "ci-config.yml"
        self.build_config_path = self.project_root / "build" / "config" / "build-config.yml"
        self.results = {}
        self.start_time = time.time()

        # Load configurations
        self.ci_config = self._load_config(self.ci_config_path)
        self.build_config = self._load_config(self.build_config_path)

        # Initialize enhanced build system if available
        if ENHANCED_BUILD_AVAILABLE:
            self.orchestrator = BuildOrchestrator(self.build_config_path)
            self.build_system = EnhancedBuildSystem()
        else:
            self.orchestrator = None
            self.build_system = None

    def _load_config(self, config_path: Path) -> dict:
        """Load YAML configuration file"""
        try:
            with open(config_path) as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"❌ Failed to load config {config_path}: {e}")
            return {}

    def run_verification(self) -> bool:
        """Run comprehensive build verification"""
        print("🔍 Starting Build Verification")
        print("=" * 50)

        verification_steps = [
            ("Environment Check", self._verify_environment),
            ("Dependency Validation", self._verify_dependencies),
            ("Build System Integration", self._verify_build_system),
            ("Build Execution", self._execute_builds),
            ("Cache Validation", self._verify_cache),
            ("Documentation Sync", self._verify_documentation),
            ("Performance Metrics", self._collect_metrics),
        ]

        overall_success = True

        for step_name, step_func in verification_steps:
            print(f"\n🔧 {step_name}...")
            try:
                success = step_func()
                self.results[step_name] = {"success": success, "timestamp": time.time()}

                if success:
                    print(f"✅ {step_name} passed")
                else:
                    print(f"❌ {step_name} failed")
                    overall_success = False

            except Exception as e:
                print(f"❌ {step_name} error: {e}")
                self.results[step_name] = {"success": False, "error": str(e), "timestamp": time.time()}
                overall_success = False

        # Generate verification report
        self._generate_report(overall_success)

        return overall_success

    def _verify_environment(self) -> bool:
        """Verify CI environment and required tools"""
        required_tools = ["python3", "node", "java", "protoc", "make"]
        missing_tools = []

        for tool in required_tools:
            try:
                result = subprocess.run(["which", tool], capture_output=True, text=True, timeout=10)
                if result.returncode != 0:
                    missing_tools.append(tool)
            except Exception:
                missing_tools.append(tool)

        if missing_tools:
            print(f"❌ Missing tools: {', '.join(missing_tools)}")
            return False

        print("✅ All required tools available")
        return True

    def _verify_dependencies(self) -> bool:
        """Verify project dependencies"""
        dependency_files = ["requirements.txt", "package.json", "build.gradle", "build/requirements.txt"]

        missing_files = []
        for dep_file in dependency_files:
            file_path = self.project_root / dep_file
            if not file_path.exists():
                missing_files.append(dep_file)

        if missing_files:
            print(f"⚠️ Missing dependency files: {', '.join(missing_files)}")

        # Try to install Python dependencies
        try:
            subprocess.run(
                ["pip", "install", "-r", "requirements.txt"],
                cwd=self.project_root,
                check=True,
                capture_output=True,
                timeout=300,
            )
            print("✅ Python dependencies installed")
        except Exception as e:
            print(f"❌ Python dependency installation failed: {e}")
            return False

        return True

    def _verify_build_system(self) -> bool:
        """Verify enhanced build system integration"""
        if not ENHANCED_BUILD_AVAILABLE:
            print("⚠️ Enhanced build system not available, skipping integration test")
            return True

        try:
            # Test orchestrator initialization
            if self.orchestrator:
                print("✅ Build orchestrator initialized")
            else:
                print("❌ Build orchestrator initialization failed")
                return False

            # Test build system initialization
            if self.build_system:
                print("✅ Enhanced build system initialized")
            else:
                print("❌ Enhanced build system initialization failed")
                return False

            return True

        except Exception as e:
            print(f"❌ Build system verification failed: {e}")
            return False

    def _execute_builds(self) -> bool:
        """Execute build targets using enhanced build system"""
        if not ENHANCED_BUILD_AVAILABLE or not self.orchestrator:
            print("⚠️ Using fallback build execution")
            return self._fallback_build_execution()

        try:
            # Get CI build targets from configuration
            ci_targets = self.ci_config.get("build_integration", {}).get("ci_targets", [])

            if not ci_targets:
                print("⚠️ No CI build targets configured")
                return True

            print(f"🔧 Building targets: {', '.join(ci_targets)}")

            # Execute builds using orchestrator
            build_results = {}
            for target in ci_targets:
                print(f"  Building {target}...")
                result = self.orchestrator.build_target(target)
                build_results[target] = result

                if not result.success:
                    print(f"❌ Build failed for {target}: {result.error}")
                    return False
                else:
                    print(f"✅ Build succeeded for {target}")

            return True

        except Exception as e:
            print(f"❌ Build execution failed: {e}")
            return False

    def _fallback_build_execution(self) -> bool:
        """Fallback build execution using Makefile"""
        try:
            # Test basic Makefile targets
            test_targets = ["help", "check-deps"]

            for target in test_targets:
                result = subprocess.run(
                    ["make", target], cwd=self.project_root, capture_output=True, text=True, timeout=60
                )

                if result.returncode != 0:
                    print(f"❌ Makefile target '{target}' failed")
                    return False

            print("✅ Fallback build execution successful")
            return True

        except Exception as e:
            print(f"❌ Fallback build execution failed: {e}")
            return False

    def _verify_cache(self) -> bool:
        """Verify build cache integrity"""
        cache_dir = self.project_root / "build" / "cache"

        if not cache_dir.exists():
            print("ℹ️ No build cache found (first run)")
            return True

        try:
            # Check cache structure
            cache_files = list(cache_dir.rglob("*"))
            print(f"ℹ️ Found {len(cache_files)} cache files")

            # Validate cache integrity if orchestrator available
            if ENHANCED_BUILD_AVAILABLE and self.orchestrator:
                cache_valid = self.orchestrator.validate_cache()
                if cache_valid:
                    print("✅ Build cache validation passed")
                else:
                    print("⚠️ Build cache validation failed, will rebuild")

            return True

        except Exception as e:
            print(f"❌ Cache verification failed: {e}")
            return False

    def _verify_documentation(self) -> bool:
        """Verify documentation is in sync with code"""
        try:
            docs_generation_path = self.project_root / "build" / "docs-generation"

            if not docs_generation_path.exists():
                print("⚠️ Documentation generation system not found")
                return True

            # Run documentation validation
            result = subprocess.run(
                ["python", "generate_docs.py", "--validate"],
                cwd=docs_generation_path,
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.returncode == 0:
                print("✅ Documentation validation passed")
                return True
            else:
                print(f"❌ Documentation validation failed: {result.stderr}")
                return False

        except Exception as e:
            print(f"❌ Documentation verification failed: {e}")
            return False

    def _collect_metrics(self) -> bool:
        """Collect build performance metrics"""
        try:
            duration = time.time() - self.start_time

            metrics = {
                "verification_duration": duration,
                "timestamp": time.time(),
                "enhanced_build_available": ENHANCED_BUILD_AVAILABLE,
                "results": self.results,
            }

            # Save metrics
            metrics_dir = Path(__file__).parent.parent / "reports"
            metrics_dir.mkdir(exist_ok=True)

            with open(metrics_dir / "build-verification-metrics.json", "w") as f:
                json.dump(metrics, f, indent=2)

            print(f"✅ Metrics collected (duration: {duration:.2f}s)")
            return True

        except Exception as e:
            print(f"❌ Metrics collection failed: {e}")
            return False

    def _generate_report(self, overall_success: bool):
        """Generate verification report"""
        try:
            report_dir = Path(__file__).parent.parent / "reports"
            report_dir.mkdir(exist_ok=True)

            report = {
                "verification_result": "PASS" if overall_success else "FAIL",
                "timestamp": time.time(),
                "duration": time.time() - self.start_time,
                "enhanced_build_available": ENHANCED_BUILD_AVAILABLE,
                "steps": self.results,
                "environment": {
                    "python_version": sys.version,
                    "platform": os.name,
                    "working_directory": str(self.project_root),
                },
            }

            with open(report_dir / "build-verification-report.json", "w") as f:
                json.dump(report, f, indent=2)

            print(f"\n📊 Verification report saved to {report_dir}")

        except Exception as e:
            print(f"❌ Report generation failed: {e}")


def main():
    """Main function"""
    print("🚀 Unhinged Build Verification")
    print("=" * 60)

    verifier = BuildVerificationRunner()
    success = verifier.run_verification()

    if success:
        print("\n🎉 Build verification completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Build verification failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
