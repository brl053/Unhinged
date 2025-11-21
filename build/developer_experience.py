#!/usr/bin/env python3

"""
@llm-type service.api
@llm-does developer experience enhancements for the enhanced build
"""

import os
import threading
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass
class BuildProgress:
    """Build progress information"""

    current_target: str
    total_targets: int
    completed_targets: int
    current_step: str
    estimated_remaining: float
    cache_hits: int
    cache_misses: int


class ProgressIndicator:
    """Real-time progress indicator for builds"""

    def __init__(self):
        self.active = False
        self.thread = None
        self.progress = BuildProgress("", 0, 0, "", 0.0, 0, 0)
        self.start_time = 0.0

    def start(self, total_targets: int):
        """Start progress indicator"""
        self.active = True
        self.start_time = time.time()
        self.progress.total_targets = total_targets
        self.thread = threading.Thread(target=self._display_loop, daemon=True)
        self.thread.start()

    def update(self, current_target: str, completed: int, step: str = "", cache_hit: bool = False):
        """Update progress"""
        if cache_hit:
            self.progress.cache_hits += 1
        else:
            self.progress.cache_misses += 1

        self.progress.current_target = current_target
        self.progress.completed_targets = completed
        self.progress.current_step = step

        # Estimate remaining time
        elapsed = time.time() - self.start_time
        if completed > 0:
            avg_time_per_target = elapsed / completed
            remaining_targets = self.progress.total_targets - completed
            self.progress.estimated_remaining = avg_time_per_target * remaining_targets

    def stop(self):
        """Stop progress indicator"""
        self.active = False
        if self.thread:
            self.thread.join(timeout=1.0)
        # Clear the line
        print("\r" + " " * 80 + "\r", end="", flush=True)

    def _display_loop(self):
        """Display progress in a loop"""
        while self.active:
            self._display_progress()
            time.sleep(0.5)

    def _display_progress(self):
        """Display current progress"""
        if not self.active:
            return

        # Calculate progress percentage
        if self.progress.total_targets > 0:
            percentage = (self.progress.completed_targets / self.progress.total_targets) * 100
        else:
            percentage = 0

        # Create progress bar
        bar_width = 20
        filled = int(bar_width * percentage / 100)
        bar = "█" * filled + "░" * (bar_width - filled)

        # Format time
        elapsed = time.time() - self.start_time
        remaining = self.progress.estimated_remaining

        # Cache stats
        total_cache_ops = self.progress.cache_hits + self.progress.cache_misses
        cache_rate = (self.progress.cache_hits / total_cache_ops * 100) if total_cache_ops > 0 else 0

        # Build status line
        status = (
            f"\r🔨 [{bar}] {percentage:5.1f}% "
            f"({self.progress.completed_targets}/{self.progress.total_targets}) "
            f"⏱️ {elapsed:4.0f}s "
            f"📦 {cache_rate:3.0f}% cache "
            f"🎯 {self.progress.current_target[:20]:<20}"
        )

        if remaining > 0:
            status += f" ⏳ ~{remaining:3.0f}s"

        # Print without newline
        print(status[:79], end="", flush=True)


class QuickCommands:
    """Quick development commands and shortcuts"""

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def quick_setup(self) -> list[str]:
        """Get quick setup commands for new developers"""
        return [
            "# Quick Setup for Unhinged Development",
            "",
            "# 1. Fast development build (recommended)",
            "make build-enhanced",
            "",
            "# 2. Check build status",
            "make build-status",
            "",
            "# 3. Start development with watch mode",
            "make build-watch TARGET=backend-compile",
            "",
            "# 4. Open development URLs",
            "echo 'Frontend: http://localhost:3000'",
            "echo 'Backend: http://localhost:8080'",
            "",
            "# 5. Get help anytime",
            "make build-list",
            "make build-explain TARGET=dev-fast",
        ]

    def common_workflows(self) -> dict[str, list[str]]:
        """Get common development workflows"""
        return {
            "First Time Setup": ["make setup", "make build-enhanced", "make build-status"],
            "Daily Development": ["make build-enhanced", "make build-watch TARGET=backend-compile"],
            "Before Commit": ["python build/build.py build pre_commit_validation", "make test-fast"],
            "Troubleshooting": [
                "make build-status",
                "python build/build.py clean --smart",
                "make build-enhanced --verbose",
            ],
            "Performance Check": ["make build-performance-report", "make build-performance-metrics"],
        }

    def get_build_shortcuts(self) -> dict[str, str]:
        """Get build shortcuts and aliases"""
        return {
            "dev": "make build-enhanced",
            "dev-full": "make build-enhanced-full",
            "status": "make build-status",
            "clean": "python build/build.py clean --smart",
            "watch": "make build-watch TARGET=",
            "explain": "make build-explain TARGET=",
            "test": "python build/build.py build test-fast --parallel",
            "perf": "make build-performance-report",
        }


class BuildStatusDashboard:
    """Interactive build status dashboard"""

    def __init__(self, orchestrator):
        self.orchestrator = orchestrator

    def display_dashboard(self):
        """Display interactive build status dashboard"""
        # Clear screen
        os.system("clear" if os.name == "posix" else "cls")

        print("🚀 UNHINGED BUILD SYSTEM DASHBOARD")
        print("=" * 60)
        print()

        # System status
        self._display_system_status()
        print()

        # Cache status
        self._display_cache_status()
        print()

        # Available targets
        self._display_available_targets()
        print()

        # Quick actions
        self._display_quick_actions()

    def _display_system_status(self):
        """Display system status section"""
        print("🖥️  SYSTEM STATUS")
        print("-" * 30)

        try:
            import psutil

            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage(".")

            print(f"⚡ CPU: {cpu_percent:5.1f}% ({psutil.cpu_count()} cores)")
            print(f"💾 Memory: {memory.percent:5.1f}% used ({memory.available / (1024**3):4.1f}GB free)")
            print(f"💿 Disk: {(disk.used / disk.total * 100):5.1f}% used ({disk.free / (1024**3):5.1f}GB free)")
        except ImportError:
            print("📊 System monitoring not available (install psutil)")

    def _display_cache_status(self):
        """Display cache status section"""
        print("💾 CACHE STATUS")
        print("-" * 30)

        if self.orchestrator.monitor:
            cache_metrics = self.orchestrator.monitor.get_cache_metrics()
            print(f"📦 Entries: {cache_metrics.total_entries}")
            print(f"💿 Size: {cache_metrics.total_size_mb:6.1f} MB")
            print(f"🎯 Hit Rate: {cache_metrics.hit_rate:5.1f}%")
            print(f"❌ Miss Rate: {cache_metrics.miss_rate:5.1f}%")
        else:
            print("📊 Cache monitoring not available")

    def _display_available_targets(self):
        """Display available build targets"""
        print("🎯 AVAILABLE TARGETS")
        print("-" * 30)

        targets = self.orchestrator.dependency_graph.targets

        # Group targets by category
        categories = {"Development": [], "Testing": [], "Production": [], "Utilities": []}

        for name, target in targets.items():
            if any(word in name for word in ["dev", "fast", "watch"]):
                categories["Development"].append((name, target.description))
            elif "test" in name:
                categories["Testing"].append((name, target.description))
            elif any(word in name for word in ["prod", "deploy", "release"]):
                categories["Production"].append((name, target.description))
            else:
                categories["Utilities"].append((name, target.description))

        for category, target_list in categories.items():
            if target_list:
                print(f"\n📋 {category}:")
                for name, desc in target_list[:3]:  # Show top 3
                    print(f"  • {name:<20} {desc[:40]}")
                if len(target_list) > 3:
                    print(f"  ... and {len(target_list) - 3} more")

    def _display_quick_actions(self):
        """Display quick action commands"""
        print("⚡ QUICK ACTIONS")
        print("-" * 30)
        print("🔨 make build-enhanced          # Fast development build")
        print("📊 make build-status            # Show detailed status")
        print("📋 make build-list              # List all targets")
        print("🔍 make build-explain TARGET=X  # Explain target")
        print("👁️  make build-watch TARGET=X   # Watch mode")
        print("🧹 python build/build.py clean --smart  # Smart cleanup")
        print("📈 make build-performance-report # Performance report")


class ErrorRecovery:
    """Error recovery and troubleshooting assistance"""

    def __init__(self, llm_integration):
        self.llm_integration = llm_integration

    def suggest_recovery_actions(self, error_message: str, target: str) -> list[str]:
        """Suggest recovery actions for build errors"""
        suggestions = []
        error_lower = error_message.lower()

        # Common error patterns and solutions
        if "permission denied" in error_lower:
            suggestions.extend(
                [
                    "Check file permissions: ls -la",
                    "Fix permissions: chmod +x gradlew",
                    "Run as different user if needed",
                ]
            )

        if "no such file" in error_lower or "not found" in error_lower:
            suggestions.extend(
                ["Verify file paths are correct", "Run setup: make setup", "Check if dependencies are installed"]
            )

        if "out of memory" in error_lower or "heap" in error_lower:
            suggestions.extend(
                [
                    "Increase memory: export GRADLE_OPTS='-Xmx4g'",
                    "Close other applications",
                    "Use incremental builds: make build-enhanced",
                ]
            )

        if "network" in error_lower or "connection" in error_lower:
            suggestions.extend(
                ["Check internet connection", "Try again in a few minutes", "Use cached dependencies if available"]
            )

        # Target-specific suggestions
        if "backend" in target:
            suggestions.extend(
                [
                    "Clean Gradle cache: ./gradlew clean",
                    "Refresh dependencies: ./gradlew --refresh-dependencies",
                    "Check Java version: java --version",
                ]
            )

        if "frontend" in target:
            suggestions.extend(
                [
                    "Clear npm cache: npm cache clean --force",
                    "Delete node_modules: rm -rf node_modules && npm install",
                    "Check Node.js version: node --version",
                ]
            )

        # Always add generic recovery steps
        suggestions.extend(
            [
                "Clean and retry: python build/build.py clean --smart",
                "Check build status: make build-status",
                "Get detailed error: python build/build.py build " + target + " --verbose",
                "Ask for help: make build-explain-error TARGET=" + target,
            ]
        )

        return suggestions[:8]  # Limit to 8 suggestions

    def create_recovery_script(self, suggestions: list[str], target: str) -> str:
        """Create a recovery script from suggestions"""
        script_lines = [
            "#!/bin/bash",
            f"# Recovery script for build target: {target}",
            f"# Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "echo '🔧 Starting build recovery process...'",
            "",
        ]

        for i, suggestion in enumerate(suggestions, 1):
            script_lines.extend(
                [
                    f"echo '📋 Step {i}: {suggestion}'",
                    f"# {suggestion}",
                    "read -p 'Press Enter to continue or Ctrl+C to skip...'",
                    "",
                ]
            )

        script_lines.extend(
            [
                "echo '✅ Recovery process completed!'",
                "echo '🔨 Try building again: python build/build.py build " + target + "'",
            ]
        )

        return "\n".join(script_lines)
