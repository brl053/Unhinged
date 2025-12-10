#!/usr/bin/env python3
"""
Pre-flight Check System - Ensures code updates are properly loaded

Integrates with ./unhinged entry point to detect code changes and ensure
deterministic application launches with updated code.

Usage:
    from build.preflight_check import PreflightChecker

    checker = PreflightChecker()
    if checker.run_preflight_checks():
        # Safe to launch application
        launch_app()
    else:
        # Handle update required
        print("Update required, restarting...")
"""

import subprocess
import sys
import time
from pathlib import Path

try:
    from .checksum_manager import ChecksumManager
except ImportError:
    # Handle when running as script
    sys.path.insert(0, str(Path(__file__).parent))
    from checksum_manager import ChecksumManager


class PreflightChecker:
    """Handles pre-flight checks for deterministic application launches"""

    def __init__(self, project_root: Path | None = None):
        """Initialize preflight checker

        Args:
            project_root: Project root directory (auto-detected if None)
        """
        if project_root is None:
            # Auto-detect project root
            current = Path(__file__).parent
            if current.name == "build":
                self.project_root = current.parent
            else:
                self.project_root = current
        else:
            self.project_root = Path(project_root)

        self.checksum_manager = ChecksumManager(self.project_root / "build")

        # Define critical modules to check
        self.critical_modules = ["cli", "libs/python", "build"]

    def check_python_cache(self) -> bool:
        """Check and clear Python cache if needed"""
        try:
            cache_dirs = []

            # Find __pycache__ directories
            for module in self.critical_modules:
                module_path = self.project_root / module
                if module_path.exists():
                    cache_dirs.extend(module_path.rglob("__pycache__"))

            if cache_dirs:
                cleared = 0
                failed = 0

                # Clear cache directories (silently)
                for cache_dir in cache_dirs:
                    try:
                        import shutil

                        shutil.rmtree(cache_dir)
                        cleared += 1
                    except Exception:
                        failed += 1

                # Aggregate output
                print(f"✅ Python cache cleared ({cleared} directories)")
                if failed > 0:
                    print(f"⚠️  Failed to clear {failed} directories (may be in use)")
                return True
            else:
                print("✅ No Python cache to clear")
                return False

        except Exception as e:
            print(f"❌ Error checking Python cache: {e}")
            return False

    def check_module_changes(self) -> dict[str, bool]:
        """Check all critical modules for changes"""
        print("🔍 Checking for code changes...")

        changes = {}
        any_changes = False

        for module in self.critical_modules:
            module_path = self.project_root / module
            if module_path.exists():
                has_changes = self.checksum_manager.has_changes(str(module))
                changes[module] = has_changes
                if has_changes:
                    any_changes = True
            else:
                print(f"⚠️ Module not found: {module}")
                changes[module] = False

        if any_changes:
            print("🔄 Code changes detected!")
        else:
            print("✅ No code changes detected")

        return changes

    def update_checksums_for_changed_modules(self, changes: dict[str, bool]):
        """Update checksums for modules that have changed"""
        changed_modules = [module for module, changed in changes.items() if changed]

        if changed_modules:
            print(f"💾 Updating checksums for {len(changed_modules)} changed modules...")
            for module in changed_modules:
                self.checksum_manager.update_checksums(module)
            print("✅ Checksums updated")
        else:
            print("✅ No checksum updates needed")

    def check_running_processes(self) -> list[str]:
        """Check for running Unhinged processes that might need restart"""
        try:
            # Check for running Python processes with our modules
            result = subprocess.run(["pgrep", "-f", "desktop_app.py"], capture_output=True, text=True)

            if result.returncode == 0:
                pids = result.stdout.strip().split("\n")
                print(f"🔄 Found {len(pids)} running desktop_app processes")
                return pids
            else:
                print("✅ No running desktop_app processes found")
                return []

        except Exception as e:
            print(f"⚠️ Error checking running processes: {e}")
            return []

    def suggest_restart_strategy(self, running_pids: list[str], changes: dict[str, bool]) -> str:
        """Suggest restart strategy based on changes and running processes"""
        any_changes = any(changes.values())

        if not any_changes and not running_pids:
            return "✅ SAFE_TO_LAUNCH - No changes, no running processes"

        elif not any_changes and running_pids:
            return "✅ SAFE_TO_LAUNCH - No changes, existing processes can continue"

        elif any_changes and not running_pids:
            return "🔄 RESTART_RECOMMENDED - Changes detected, no conflicts"

        else:  # any_changes and running_pids
            return "⚠️ RESTART_REQUIRED - Changes detected with running processes"

    def run_preflight_checks(self, auto_update: bool = True) -> bool:
        """Run complete preflight check sequence

        Args:
            auto_update: Whether to automatically update checksums

        Returns:
            True if safe to launch, False if restart/update needed
        """
        print("🚀 Running pre-flight checks...")
        print(f"📁 Project root: {self.project_root}")

        # Step 1: Check for code changes
        changes = self.check_module_changes()

        # Step 2: Check running processes
        running_pids = self.check_running_processes()

        # Step 3: Check Python cache
        self.check_python_cache()

        # Step 4: Update checksums if auto-update enabled (before strategy check)
        if auto_update:
            self.update_checksums_for_changed_modules(changes)

        # Step 5: Get restart strategy
        strategy = self.suggest_restart_strategy(running_pids, changes)

        # Step 6: Determine if safe to launch
        if strategy.startswith("✅"):
            print("🎯 Pre-flight checks PASSED - Safe to launch")
            return True
        elif strategy.startswith("🔄"):
            # Changes detected but no conflicts - update checksums and launch
            return True
        else:  # ⚠️ RESTART_REQUIRED
            print("⚠️ Pre-flight checks FAILED - Restart required")
            print("   Reason: Code changes detected with running processes")
            print("   Action: Kill existing processes or use different launch method")
            return False

    def force_clean_restart(self):
        """Force a clean restart by clearing cache and killing processes"""
        print("🧹 Forcing clean restart...")

        # Clear Python cache
        self.check_python_cache()

        # Kill running processes
        running_pids = self.check_running_processes()
        if running_pids:
            print(f"🔄 Killing {len(running_pids)} running processes...")
            for pid in running_pids:
                try:
                    subprocess.run(["kill", pid], check=True)
                    print(f"   ✅ Killed process {pid}")
                except Exception as e:
                    print(f"   ⚠️ Failed to kill process {pid}: {e}")

        # Update all checksums
        self.checksum_manager.force_update_all(self.critical_modules)

        print("✅ Clean restart preparation complete")

    def get_status_report(self) -> str:
        """Get comprehensive status report"""
        lines = [
            "📊 Unhinged Pre-flight Status Report",
            "=" * 40,
            f"📁 Project Root: {self.project_root}",
            f"🕒 Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "📦 Module Status:",
        ]

        # Module checksums
        for module in self.critical_modules:
            has_changes = self.checksum_manager.has_changes(module)
            status = "🔄 CHANGED" if has_changes else "✅ CURRENT"
            lines.append(f"   {module}: {status}")

        lines.append("")

        # Running processes
        running_pids = self.check_running_processes()
        if running_pids:
            lines.append(f"🔄 Running Processes: {len(running_pids)}")
            for pid in running_pids[:5]:  # Show first 5
                lines.append(f"   PID {pid}")
            if len(running_pids) > 5:
                lines.append(f"   ... and {len(running_pids) - 5} more")
        else:
            lines.append("✅ No Running Processes")

        return "\n".join(lines)


def main():
    """CLI interface for preflight checker"""
    import argparse

    parser = argparse.ArgumentParser(description="Unhinged Pre-flight Checker")
    parser.add_argument("command", choices=["check", "status", "clean", "force-clean"], help="Command to execute")
    parser.add_argument("--no-auto-update", action="store_true", help="Don't automatically update checksums")

    args = parser.parse_args()

    checker = PreflightChecker()

    if args.command == "check":
        success = checker.run_preflight_checks(auto_update=not args.no_auto_update)
        sys.exit(0 if success else 1)

    elif args.command == "status":
        print(checker.get_status_report())

    elif args.command == "clean":
        checker.check_python_cache()

    elif args.command == "force-clean":
        checker.force_clean_restart()


if __name__ == "__main__":
    main()
