#!/usr/bin/env python3
"""
@llm-doc Process Information Collection for GTK4 UI
@llm-version 1.0.0
@llm-date 2025-10-28

Cross-platform process monitoring using psutil for aux/top command equivalence
with efficient data collection, sorting, and process management capabilities.
"""

import logging
import time
from dataclasses import dataclass
from typing import Any

# Import psutil for cross-platform process information
try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class ProcessInfo:
    """Process information data structure"""

    pid: int
    name: str
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    user: str
    status: str
    command: str
    create_time: float
    parent_pid: int
    num_threads: int

    def __post_init__(self):
        """Post-initialization processing"""
        # Ensure command is not too long for display
        if len(self.command) > 200:
            self.command = self.command[:197] + "..."


class ProcessMonitor:
    """
    Process information collection using psutil.

    Features:
    - Cross-platform process enumeration
    - Process data structure with sorting capabilities
    - Process management (kill with safety checks)
    - Efficient caching for performance
    - Error handling for permission issues
    """

    def __init__(self):
        self.cache_duration = 1.0  # Cache for 1 second
        self._process_cache = {}
        self._last_update = 0
        self._cpu_percent_cache = {}

        # Performance tracking
        self._collection_count = 0
        self._error_count = 0

    def get_process_list(self, include_system: bool = True) -> list[ProcessInfo]:
        """
        Get list of all processes.

        Args:
            include_system: Whether to include system processes

        Returns:
            List of ProcessInfo objects
        """
        if not PSUTIL_AVAILABLE:
            logger.warning("psutil not available - cannot collect process information")
            return []

        try:
            processes = []

            # Get all processes
            for proc in psutil.process_iter(
                [
                    "pid",
                    "name",
                    "username",
                    "status",
                    "create_time",
                    "ppid",
                    "num_threads",
                ]
            ):
                try:
                    # Get basic process info
                    pinfo = proc.info

                    # Skip system processes if requested
                    if not include_system and pinfo["username"] in [
                        "root",
                        "system",
                        "daemon",
                    ]:
                        continue

                    # Get CPU and memory usage
                    cpu_percent = self._get_cpu_percent(proc)
                    memory_info = proc.memory_info()
                    memory_percent = proc.memory_percent()

                    # Get command line
                    try:
                        cmdline = proc.cmdline()
                        command = " ".join(cmdline) if cmdline else pinfo["name"]
                    except (psutil.AccessDenied, psutil.NoSuchProcess):
                        command = pinfo["name"]

                    # Create ProcessInfo object
                    process_info = ProcessInfo(
                        pid=pinfo["pid"],
                        name=pinfo["name"] or "Unknown",
                        cpu_percent=cpu_percent,
                        memory_percent=memory_percent,
                        memory_mb=memory_info.rss / 1024 / 1024,  # Convert to MB
                        user=pinfo["username"] or "unknown",
                        status=pinfo["status"] or "unknown",
                        command=command,
                        create_time=pinfo["create_time"] or 0,
                        parent_pid=pinfo["ppid"] or 0,
                        num_threads=pinfo["num_threads"] or 1,
                    )

                    processes.append(process_info)

                except (
                    psutil.NoSuchProcess,
                    psutil.AccessDenied,
                    psutil.ZombieProcess,
                ):
                    # Process disappeared or access denied - skip
                    continue
                except Exception as e:
                    logger.debug(
                        f"Error collecting info for process {pinfo.get('pid', 'unknown')}: {e}"
                    )
                    self._error_count += 1
                    continue

            self._collection_count += 1
            return processes

        except Exception as e:
            logger.error(f"Failed to collect process list: {e}")
            self._error_count += 1
            return []

    def get_top_processes(
        self, limit: int = 20, sort_by: str = "cpu_percent"
    ) -> list[ProcessInfo]:
        """
        Get top processes sorted by specified metric.

        Args:
            limit: Maximum number of processes to return
            sort_by: Sort criteria ('cpu_percent', 'memory_percent', 'memory_mb', 'name', 'pid')

        Returns:
            List of top ProcessInfo objects
        """
        processes = self.get_process_list()

        # Sort processes
        reverse = sort_by in ["cpu_percent", "memory_percent", "memory_mb"]

        try:
            sorted_processes = sorted(
                processes, key=lambda p: getattr(p, sort_by, 0), reverse=reverse
            )
        except (AttributeError, TypeError):
            # Fallback to PID sorting if sort_by is invalid
            sorted_processes = sorted(processes, key=lambda p: p.pid)

        return sorted_processes[:limit]

    def get_process_by_pid(self, pid: int) -> ProcessInfo | None:
        """Get detailed information for a specific process."""
        if not PSUTIL_AVAILABLE:
            return None

        try:
            proc = psutil.Process(pid)

            # Get process information
            cpu_percent = self._get_cpu_percent(proc)
            memory_info = proc.memory_info()
            memory_percent = proc.memory_percent()

            try:
                cmdline = proc.cmdline()
                command = " ".join(cmdline) if cmdline else proc.name()
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                command = proc.name()

            return ProcessInfo(
                pid=proc.pid,
                name=proc.name(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_mb=memory_info.rss / 1024 / 1024,
                user=proc.username(),
                status=proc.status(),
                command=command,
                create_time=proc.create_time(),
                parent_pid=proc.ppid(),
                num_threads=proc.num_threads(),
            )

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            return None
        except Exception as e:
            logger.error(f"Failed to get process {pid}: {e}")
            return None

    def kill_process(self, pid: int, force: bool = False) -> bool:
        """
        Kill a process with safety checks.

        Args:
            pid: Process ID to kill
            force: Whether to use SIGKILL (force) or SIGTERM (graceful)

        Returns:
            True if successful, False otherwise
        """
        if not PSUTIL_AVAILABLE:
            logger.warning("psutil not available - cannot kill process")
            return False

        try:
            proc = psutil.Process(pid)

            # Safety check - don't kill critical system processes
            if self._is_critical_process(proc):
                logger.warning(
                    f"Refusing to kill critical process: {proc.name()} (PID: {pid})"
                )
                return False

            # Kill the process
            if force:
                proc.kill()  # SIGKILL
                logger.info(f"Force killed process {proc.name()} (PID: {pid})")
            else:
                proc.terminate()  # SIGTERM
                logger.info(f"Terminated process {proc.name()} (PID: {pid})")

            return True

        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.warning(f"Cannot kill process {pid}: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to kill process {pid}: {e}")
            return False

    def _get_cpu_percent(self, proc) -> float:
        """Get CPU percentage with caching for better accuracy."""
        try:
            pid = proc.pid
            current_time = time.time()

            # Use cached value if available and recent
            if (
                pid in self._cpu_percent_cache
                and current_time - self._cpu_percent_cache[pid]["time"] < 1.0
            ):
                return self._cpu_percent_cache[pid]["value"]

            # Get CPU percent (this requires a previous call to be accurate)
            cpu_percent = proc.cpu_percent()

            # Cache the value
            self._cpu_percent_cache[pid] = {"value": cpu_percent, "time": current_time}

            return cpu_percent

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return 0.0

    def _is_critical_process(self, proc) -> bool:
        """Check if a process is critical and should not be killed."""
        try:
            name = proc.name().lower()
            pid = proc.pid

            # Never kill PID 1 (init)
            if pid == 1:
                return True

            # Critical system processes
            critical_names = {
                "systemd",
                "init",
                "kernel",
                "kthreadd",
                "ksoftirqd",
                "migration",
                "rcu_",
                "watchdog",
                "sshd",
                "dbus",
                "networkmanager",
                "systemd-",
                "gdm",
                "lightdm",
            }

            for critical in critical_names:
                if critical in name:
                    return True

            return False

        except Exception:
            # If we can't determine, err on the side of caution
            return True

    def get_statistics(self) -> dict[str, Any]:
        """Get monitoring statistics."""
        return {
            "psutil_available": PSUTIL_AVAILABLE,
            "collection_count": self._collection_count,
            "error_count": self._error_count,
            "error_rate": self._error_count / max(self._collection_count, 1),
            "cache_size": len(self._cpu_percent_cache),
            "cache_duration": self.cache_duration,
        }

    def clear_cache(self):
        """Clear internal caches."""
        self._process_cache.clear()
        self._cpu_percent_cache.clear()


# Convenience functions for easy access
def get_process_list(include_system: bool = True) -> list[ProcessInfo]:
    """Get list of all processes."""
    monitor = ProcessMonitor()
    return monitor.get_process_list(include_system)


def get_top_processes(
    limit: int = 20, sort_by: str = "cpu_percent"
) -> list[ProcessInfo]:
    """Get top processes sorted by specified metric."""
    monitor = ProcessMonitor()
    return monitor.get_top_processes(limit, sort_by)


def get_process_by_pid(pid: int) -> ProcessInfo | None:
    """Get detailed information for a specific process."""
    monitor = ProcessMonitor()
    return monitor.get_process_by_pid(pid)


def kill_process(pid: int, force: bool = False) -> bool:
    """Kill a process with safety checks."""
    monitor = ProcessMonitor()
    return monitor.kill_process(pid, force)


if __name__ == "__main__":
    # Test the process monitor
    print("🧪 Testing Process Monitor")
    print("=" * 40)

    if not PSUTIL_AVAILABLE:
        print("❌ psutil not available - install with: pip install psutil")
        exit(1)

    monitor = ProcessMonitor()

    # Test process list
    print("📊 Getting process list...")
    processes = monitor.get_process_list()
    print(f"✅ Found {len(processes)} processes")

    # Test top processes
    print("\n📈 Top 5 CPU processes:")
    top_cpu = monitor.get_top_processes(limit=5, sort_by="cpu_percent")
    for proc in top_cpu:
        print(
            f"  {proc.name} (PID: {proc.pid}): {proc.cpu_percent:.1f}% CPU, {proc.memory_percent:.1f}% Memory"
        )

    # Test top memory processes
    print("\n💾 Top 5 Memory processes:")
    top_mem = monitor.get_top_processes(limit=5, sort_by="memory_percent")
    for proc in top_mem:
        print(
            f"  {proc.name} (PID: {proc.pid}): {proc.cpu_percent:.1f}% CPU, {proc.memory_percent:.1f}% Memory"
        )

    # Test statistics
    stats = monitor.get_statistics()
    print("\n📊 Statistics:")
    print(f"  Collections: {stats['collection_count']}")
    print(f"  Errors: {stats['error_count']}")
    print(f"  Error rate: {stats['error_rate']:.2%}")

    print("✅ Process monitor test completed")
