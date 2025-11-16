"""
@llm-doc Platform Status Information Collection
@llm-version 1.0.0
@llm-date 2025-11-15

Unhinged platform-specific status collection including services, VM, build system, and graphics.
"""

import contextlib
import logging
import os
import platform
import time
from pathlib import Path

from subprocess_utils import SubprocessRunner

# Import psutil with fallback
try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

logger = logging.getLogger(__name__)


class PlatformStatusCollector:
    """Collects Unhinged platform-specific status."""

    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.runner = SubprocessRunner(timeout=10)

    def collect_system_status(self):
        """Collect system status information"""
        from ..system_info import SystemStatus

        system_status = SystemStatus()

        system_status.os_name = platform.system()
        system_status.os_version = platform.release()
        system_status.architecture = platform.machine()
        system_status.hostname = platform.node()
        system_status.username = os.getenv("USER", "Unknown")

        result = self.runner.run_list(["uname", "-r"])
        if result["success"]:
            system_status.kernel_version = result["output"].strip()

        if PSUTIL_AVAILABLE:
            system_status.boot_time = psutil.boot_time()
            system_status.uptime_seconds = time.time() - system_status.boot_time

            with contextlib.suppress(AttributeError):
                system_status.load_average = list(psutil.getloadavg())
        else:
            try:
                with open("/proc/uptime") as f:
                    uptime_line = f.read().strip()
                    system_status.uptime_seconds = float(uptime_line.split()[0])
                    system_status.boot_time = time.time() - system_status.uptime_seconds
            except Exception:
                pass

            try:
                with open("/proc/loadavg") as f:
                    loadavg_line = f.read().strip()
                    loads = loadavg_line.split()[:3]
                    system_status.load_average = [float(load) for load in loads]
            except Exception:
                pass

        return system_status

    def collect_platform_status(self):
        """Collect Unhinged platform-specific status"""
        from ..system_info import PlatformStatus

        platform_status = PlatformStatus()

        try:
            try:
                from control.service_health_monitor import ServiceHealthMonitor

                health_monitor = ServiceHealthMonitor()
                service_results = health_monitor.monitor_and_recover_all()

                for service_id, result in service_results.items():
                    status = result.get("status", "unknown")
                    if status in ["healthy", "recovered"]:
                        platform_status.services_running.append(service_id)
                    else:
                        platform_status.services_failed.append(
                            f"{service_id}: {result.get('message', 'Unknown error')}"
                        )

            except Exception as e:
                logger.debug(f"Service health monitor not available: {e}")

                result = self.runner.run_list(["docker", "ps", "--format", "table {{.Names}}\t{{.Status}}"])
                if result["success"]:
                    lines = result["output"].split("\n")[1:]
                    for line in lines:
                        if line.strip():
                            parts = line.split("\t")
                            if len(parts) >= 2:
                                service_name = parts[0].strip()
                                status = parts[1].strip()
                                if "Up" in status:
                                    platform_status.services_running.append(service_name)
                                else:
                                    platform_status.services_failed.append(service_name)

            try:
                from control.vm_monitor import VMMonitor

                vm_monitor = VMMonitor()
                vm_status = vm_monitor.get_vm_status()

                platform_status.vm_status = {
                    "available": True,
                    "qemu_running": vm_status.get("qemu_running", False),
                    "shared_accessible": vm_status.get("shared_accessible", False),
                    "serial_active": vm_status.get("serial_active", False),
                    "last_check": vm_status.get("timestamp", time.time()),
                    "overall_status": "healthy"
                    if all(
                        [
                            vm_status.get("qemu_running", False),
                            vm_status.get("shared_accessible", False),
                        ]
                    )
                    else "degraded",
                }

            except Exception as e:
                logger.debug(f"VM monitor not available: {e}")
                platform_status.vm_status = {"available": False, "error": str(e)}

            build_cache_dir = self.project_root / ".build-cache"
            build_dir = self.project_root / "build"

            if build_cache_dir.exists() and build_dir.exists():
                try:
                    cache_files = list(build_cache_dir.glob("*"))
                    if cache_files:
                        latest_cache = max(cache_files, key=lambda p: p.stat().st_mtime)
                        cache_age = time.time() - latest_cache.stat().st_mtime
                        if cache_age < 3600:
                            platform_status.build_system_status = "Active (recent builds)"
                        else:
                            platform_status.build_system_status = "Available (idle)"
                    else:
                        platform_status.build_system_status = "Available (no cache)"
                except Exception:
                    platform_status.build_system_status = "Available"
            else:
                platform_status.build_system_status = "Not initialized"

            graphics_lib = self.project_root / "libs" / "graphics"
            vm_dir = self.project_root / "vm"

            if graphics_lib.exists() and vm_dir.exists():
                result = self.runner.run_list(["pgrep", "-f", "qemu.*gl"])
                if result["success"] and result["output"].strip():
                    platform_status.graphics_platform_status = "Active (GPU acceleration)"
                else:
                    platform_status.graphics_platform_status = "Available (software rendering)"
            elif graphics_lib.exists():
                platform_status.graphics_platform_status = "Available (no VM)"
            else:
                platform_status.graphics_platform_status = "Not found"

        except Exception as e:
            logger.warning(f"Failed to collect platform status: {e}")
            platform_status.services_failed = [f"Collection error: {str(e)}"]

        return platform_status
