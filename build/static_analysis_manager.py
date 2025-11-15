#!/usr/bin/env python3
"""
Static Analysis Manager - Automated code quality checking for Unhinged platform

Integrates with the existing checksum system to run static analysis only when
Python files change. Provides both automated and manual checking capabilities.

Usage:
    from build.static_analysis_manager import StaticAnalysisManager

    sam = StaticAnalysisManager()
    if sam.should_run_analysis("control/gtk4_gui"):
        results = sam.run_analysis("control/gtk4_gui")
        if not results.passed:
            print("❌ Static analysis failed")
"""

import json
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

try:
    from .checksum_manager import ChecksumManager
except ImportError:
    from checksum_manager import ChecksumManager


@dataclass
class AnalysisResult:
    """Result of static analysis run"""

    passed: bool
    errors: list[str]
    warnings: list[str]
    fixed_count: int
    total_issues: int
    execution_time: float
    module_path: str


class StaticAnalysisManager:
    """Manages static analysis integration with checksum-based change detection"""

    def __init__(self, build_dir: Optional[Path] = None):
        """Initialize static analysis manager

        Args:
            build_dir: Build directory path (defaults to ./build)
        """
        self.checksum_manager = ChecksumManager(build_dir)
        self.build_dir = self.checksum_manager.build_dir

        # Find project root
        self.project_root = self._find_project_root()

        # Find ruff executable
        self.ruff_path = self._find_ruff_executable()

        # Analysis results cache
        self.results_file = self.build_dir / "static_analysis_results.json"

    def _find_project_root(self) -> Path:
        """Find project root directory"""
        current = Path(__file__).parent
        while current.parent != current:
            if (current / "pyproject.toml").exists() or (current / ".git").exists():
                return current
            current = current.parent
        return Path.cwd()

    def _find_ruff_executable(self) -> Optional[Path]:
        """Find ruff executable in various locations"""
        # Check venv-production first
        venv_ruff = self.project_root / "venv-production" / "bin" / "ruff"
        if venv_ruff.exists():
            return venv_ruff

        # Check system PATH
        try:
            result = subprocess.run(["which", "ruff"], capture_output=True, text=True)
            if result.returncode == 0:
                return Path(result.stdout.strip())
        except:
            pass

        return None

    def should_run_analysis(self, module_path: str) -> bool:
        """Check if static analysis should run for module

        Args:
            module_path: Path to module directory (e.g., "control/gtk4_gui")

        Returns:
            True if analysis should run (Python files changed)
        """
        # Check if any Python files changed
        if not self.checksum_manager.has_changes(module_path):
            return False

        # Check if module contains Python files
        module_full_path = self.project_root / module_path
        if not module_full_path.exists():
            return False

        python_files = list(module_full_path.rglob("*.py"))
        return len(python_files) > 0

    def run_analysis(self, module_path: str, auto_fix: bool = True) -> AnalysisResult:
        """Run static analysis on module

        Args:
            module_path: Path to module directory
            auto_fix: Whether to auto-fix issues

        Returns:
            AnalysisResult with analysis details
        """
        start_time = time.time()

        if not self.ruff_path:
            return AnalysisResult(
                passed=False,
                errors=["Ruff executable not found"],
                warnings=[],
                fixed_count=0,
                total_issues=0,
                execution_time=time.time() - start_time,
                module_path=module_path,
            )

        module_full_path = self.project_root / module_path
        if not module_full_path.exists():
            return AnalysisResult(
                passed=False,
                errors=[f"Module path does not exist: {module_path}"],
                warnings=[],
                fixed_count=0,
                total_issues=0,
                execution_time=time.time() - start_time,
                module_path=module_path,
            )

        errors = []
        warnings = []
        fixed_count = 0

        try:
            # Run ruff format first if auto-fix is enabled
            if auto_fix:
                format_result = subprocess.run(
                    [str(self.ruff_path), "format", str(module_full_path)],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                )
                # Count formatted files
                if "reformatted" in format_result.stdout.lower():
                    try:
                        parts = format_result.stdout.split()
                        for i, part in enumerate(parts):
                            if part.isdigit() and i + 1 < len(parts) and "file" in parts[i + 1]:
                                fixed_count += int(part)
                    except:
                        pass

            # Run ruff check with auto-fix if requested
            cmd = [str(self.ruff_path), "check", str(module_full_path)]
            if auto_fix:
                cmd.extend(["--fix", "--unsafe-fixes"])

            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)

            # Parse ruff output
            if result.stdout:
                lines = result.stdout.strip().split("\n")
                for line in lines:
                    if "fixed" in line.lower():
                        # Extract fixed count
                        try:
                            parts = line.split()
                            for i, part in enumerate(parts):
                                if (
                                    part.isdigit()
                                    and i + 1 < len(parts)
                                    and "fixed" in parts[i + 1]
                                ):
                                    fixed_count += int(part)
                        except:
                            pass
                    elif line.strip():
                        if result.returncode != 0:
                            errors.append(line)
                        else:
                            warnings.append(line)

            # Count remaining issues
            if result.returncode != 0:
                # Run again without --fix to get current issue count
                check_result = subprocess.run(
                    [str(self.ruff_path), "check", str(module_full_path)],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                )
                total_issues = len(
                    [
                        line
                        for line in check_result.stdout.split("\n")
                        if line.strip() and not line.startswith("Found")
                    ]
                )
            else:
                total_issues = 0

        except Exception as e:
            errors.append(f"Failed to run ruff: {e}")
            total_issues = 1

        execution_time = time.time() - start_time
        passed = len(errors) == 0

        result = AnalysisResult(
            passed=passed,
            errors=errors,
            warnings=warnings,
            fixed_count=fixed_count,
            total_issues=total_issues,
            execution_time=execution_time,
            module_path=module_path,
        )

        # Save results
        self._save_results(result)

        return result

    def run_analysis_on_changed_modules(
        self, modules: list[str], auto_fix: bool = True
    ) -> dict[str, AnalysisResult]:
        """Run analysis on multiple modules that have changes

        Args:
            modules: List of module paths to check
            auto_fix: Whether to auto-fix issues

        Returns:
            Dictionary mapping module paths to analysis results
        """
        results = {}

        for module in modules:
            if self.should_run_analysis(module):
                print(f"🔍 Running static analysis on {module}...")
                result = self.run_analysis(module, auto_fix)
                results[module] = result

                if result.passed:
                    print(f"✅ {module}: Analysis passed")
                    if result.fixed_count > 0:
                        print(f"   🔧 Auto-fixed {result.fixed_count} issues")
                else:
                    print(f"❌ {module}: {result.total_issues} issues found")
                    for error in result.errors[:3]:  # Show first 3 errors
                        print(f"   • {error}")
                    if len(result.errors) > 3:
                        print(f"   ... and {len(result.errors) - 3} more")

        return results

    def _save_results(self, result: AnalysisResult):
        """Save analysis results to file"""
        try:
            # Load existing results
            if self.results_file.exists():
                with open(self.results_file) as f:
                    data = json.load(f)
            else:
                data = {}

            # Add new result
            data[result.module_path] = {
                "passed": result.passed,
                "errors": result.errors,
                "warnings": result.warnings,
                "fixed_count": result.fixed_count,
                "total_issues": result.total_issues,
                "execution_time": result.execution_time,
                "timestamp": time.time(),
            }

            # Save results
            with open(self.results_file, "w") as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            print(f"❌ Error saving analysis results: {e}")

    def get_last_results(self, module_path: str) -> Optional[AnalysisResult]:
        """Get last analysis results for module"""
        try:
            if not self.results_file.exists():
                return None

            with open(self.results_file) as f:
                data = json.load(f)

            if module_path not in data:
                return None

            result_data = data[module_path]
            return AnalysisResult(
                passed=result_data["passed"],
                errors=result_data["errors"],
                warnings=result_data["warnings"],
                fixed_count=result_data["fixed_count"],
                total_issues=result_data["total_issues"],
                execution_time=result_data["execution_time"],
                module_path=module_path,
            )

        except Exception as e:
            print(f"❌ Error loading analysis results: {e}")
            return None


if __name__ == "__main__":
    """Command line interface for static analysis"""
    import argparse

    parser = argparse.ArgumentParser(description="Run static analysis on Python modules")
    parser.add_argument("modules", nargs="*", help="Module paths to analyze")
    parser.add_argument("--no-fix", action="store_true", help="Don't auto-fix issues")
    parser.add_argument("--check-changes", action="store_true", help="Only analyze changed modules")

    args = parser.parse_args()

    sam = StaticAnalysisManager()

    if not args.modules:
        # Default modules to check
        args.modules = ["control/gtk4_gui", "libs/python", "services"]

    auto_fix = not args.no_fix

    if args.check_changes:
        results = sam.run_analysis_on_changed_modules(args.modules, auto_fix)
    else:
        results = {}
        for module in args.modules:
            results[module] = sam.run_analysis(module, auto_fix)

    # Summary
    total_modules = len(results)
    passed_modules = sum(1 for r in results.values() if r.passed)
    total_fixed = sum(r.fixed_count for r in results.values())

    print("\n📊 Static Analysis Summary:")
    print(f"   Modules analyzed: {total_modules}")
    print(f"   Modules passed: {passed_modules}")
    print(f"   Issues auto-fixed: {total_fixed}")

    if passed_modules < total_modules:
        print(f"❌ {total_modules - passed_modules} modules have issues")
        sys.exit(1)
    else:
        print("✅ All modules passed static analysis")
