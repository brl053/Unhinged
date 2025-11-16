#!/usr/bin/env python3
"""
@llm-doc System Information Collection Module for GTK4 UI
@llm-version 1.0.0
@llm-date 2025-11-15

Comprehensive system information gathering orchestrator.
Delegates to specialized collectors for CPU, memory, storage, GPU, network, and platform status.
"""

import logging
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Add utils to path for subprocess_utils import
sys.path.insert(0, str(Path(__file__).parent / "utils"))

# Set up logging
logger = logging.getLogger(__name__)


# Data classes (re-exported from here for backward compatibility)
@dataclass
class CPUInfo:
    """CPU information structure"""
    model: str = "Unknown"
    cores: int = 0
    threads: int = 0
    frequency_mhz: float = 0.0
    architecture: str = "Unknown"
    features: list[str] = field(default_factory=list)
    usage_percent: float = 0.0
    temperature_celsius: float | None = None


@dataclass
class MemoryInfo:
    """Memory information structure"""
    total_gb: float = 0.0
    available_gb: float = 0.0
    used_gb: float = 0.0
    usage_percent: float = 0.0
    swap_total_gb: float = 0.0
    swap_used_gb: float = 0.0
    swap_percent: float = 0.0


@dataclass
class StorageDevice:
    """Individual storage device information"""
    device: str = ""
    mountpoint: str = ""
    filesystem: str = ""
    total_gb: float = 0.0
    used_gb: float = 0.0
    free_gb: float = 0.0
    usage_percent: float = 0.0


@dataclass
class StorageInfo:
    """Storage information structure"""
    devices: list[StorageDevice] = field(default_factory=list)
    total_storage_gb: float = 0.0
    total_used_gb: float = 0.0
    total_free_gb: float = 0.0


@dataclass
class GPUInfo:
    """GPU information structure"""
    vendor: str = "Unknown"
    model: str = "Unknown"
    driver: str = "Unknown"
    memory_mb: int | None = None


@dataclass
class NetworkInterface:
    """Network interface information"""
    name: str = ""
    ip_address: str = ""
    mac_address: str = ""
    status: str = "Unknown"
    bytes_sent: int = 0
    bytes_recv: int = 0


@dataclass
class NetworkInfo:
    """Network information structure"""
    interfaces: list[NetworkInterface] = field(default_factory=list)
    hostname: str = "Unknown"
    total_bytes_sent: int = 0
    total_bytes_recv: int = 0


@dataclass
class SystemStatus:
    """System status information"""
    os_name: str = "Unknown"
    os_version: str = "Unknown"
    kernel_version: str = "Unknown"
    architecture: str = "Unknown"
    hostname: str = "Unknown"
    username: str = "Unknown"
    uptime_seconds: float = 0.0
    boot_time: float = 0.0
    load_average: list[float] = field(default_factory=list)


@dataclass
class PlatformStatus:
    """Unhinged platform-specific status"""
    services_running: list[str] = field(default_factory=list)
    services_failed: list[str] = field(default_factory=list)
    vm_status: dict[str, Any] = field(default_factory=dict)
    build_system_status: str = "Unknown"
    graphics_platform_status: str = "Unknown"


@dataclass
class SystemInformation:
    """Complete system information structure"""
    cpu: CPUInfo = field(default_factory=CPUInfo)
    memory: MemoryInfo = field(default_factory=MemoryInfo)
    storage: StorageInfo = field(default_factory=StorageInfo)
    gpu: GPUInfo = field(default_factory=GPUInfo)
    network: NetworkInfo = field(default_factory=NetworkInfo)
    system: SystemStatus = field(default_factory=SystemStatus)
    platform: PlatformStatus = field(default_factory=PlatformStatus)
    motherboard: dict = field(default_factory=dict)
    cpu_details: dict = field(default_factory=dict)
    collection_time: float = field(default_factory=time.time)
    collection_errors: list[str] = field(default_factory=list)


class SystemInfoCollector:
    """
    Main system information collector orchestrator.
    Delegates to specialized collectors for each information category.
    """

    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self._cache = {}
        self._cache_timeout = 5.0
        self._last_collection = 0.0

        # Import collectors
        from .collectors.cpu import CPUCollector
        from .collectors.memory import MemoryCollector
        from .collectors.storage import StorageCollector
        from .collectors.gpu import GPUCollector
        from .collectors.network import NetworkCollector
        from .collectors.platform import PlatformStatusCollector

        self.cpu_collector = CPUCollector()
        self.memory_collector = MemoryCollector()
        self.storage_collector = StorageCollector()
        self.gpu_collector = GPUCollector()
        self.network_collector = NetworkCollector()
        self.platform_collector = PlatformStatusCollector(project_root)

    def collect_all(self, use_cache: bool = True) -> SystemInformation:
        """
        Collect all system information.

        Args:
            use_cache: Whether to use cached data if available

        Returns:
            SystemInformation object with all collected data
        """
        current_time = time.time()

        # Check cache
        if use_cache and self._cache and current_time - self._last_collection < self._cache_timeout:
            return self._cache.get("system_info", SystemInformation())

        logger.info("🔍 Collecting system information...")

        system_info = SystemInformation()
        system_info.collection_time = current_time

        # Collect each category with error handling
        try:
            system_info.motherboard = self.cpu_collector.collect_motherboard_info()
        except Exception as e:
            logger.error(f"Failed to collect motherboard info: {e}")
            system_info.collection_errors.append(f"Motherboard: {str(e)}")

        try:
            system_info.cpu = self.cpu_collector.collect_cpu_info()
        except Exception as e:
            logger.error(f"Failed to collect CPU info: {e}")
            system_info.collection_errors.append(f"CPU: {str(e)}")

        try:
            system_info.cpu_details = self.cpu_collector.collect_cpu_details()
        except Exception as e:
            logger.error(f"Failed to collect CPU details: {e}")
            system_info.collection_errors.append(f"CPU Details: {str(e)}")

        try:
            system_info.memory = self.memory_collector.collect_memory_info()
        except Exception as e:
            logger.error(f"Failed to collect memory info: {e}")
            system_info.collection_errors.append(f"Memory: {str(e)}")

        try:
            system_info.storage = self.storage_collector.collect_storage_info()
        except Exception as e:
            logger.error(f"Failed to collect storage info: {e}")
            system_info.collection_errors.append(f"Storage: {str(e)}")

        try:
            system_info.gpu = self.gpu_collector.collect_gpu_info()
        except Exception as e:
            logger.error(f"Failed to collect GPU info: {e}")
            system_info.collection_errors.append(f"GPU: {str(e)}")

        try:
            system_info.network = self.network_collector.collect_network_info()
        except Exception as e:
            logger.error(f"Failed to collect network info: {e}")
            system_info.collection_errors.append(f"Network: {str(e)}")

        try:
            system_info.system = self.platform_collector.collect_system_status()
        except Exception as e:
            logger.error(f"Failed to collect system status: {e}")
            system_info.collection_errors.append(f"System Status: {str(e)}")

        try:
            system_info.platform = self.platform_collector.collect_platform_status()
        except Exception as e:
            logger.error(f"Failed to collect platform status: {e}")
            system_info.collection_errors.append(f"Platform Status: {str(e)}")

        # Cache the result
        self._cache["system_info"] = system_info
        self._last_collection = current_time

        # Log collection summary
        if system_info.collection_errors:
            logger.warning(f"⚠️  System information collected with {len(system_info.collection_errors)} errors")
            for error in system_info.collection_errors:
                logger.warning(f"  - {error}")
        else:
            logger.info("✅ System information collected successfully")

        return system_info

    def get_performance_summary(self) -> dict[str, Any]:
        """Get a quick performance summary for dashboard display"""
        try:
            system_info = self.collect_all(use_cache=True)

            return {
                "cpu_usage": system_info.cpu.usage_percent,
                "memory_usage": system_info.memory.usage_percent,
                "storage_usage": (system_info.storage.total_used_gb / system_info.storage.total_storage_gb * 100)
                if system_info.storage.total_storage_gb > 0
                else 0,
                "services_count": len(system_info.platform.services_running),
                "errors_count": len(system_info.collection_errors),
                "last_updated": system_info.collection_time,
            }
        except Exception as e:
            logger.error(f"Failed to get performance summary: {e}")
            return {
                "cpu_usage": 0,
                "memory_usage": 0,
                "storage_usage": 0,
                "services_count": 0,
                "errors_count": 1,
                "last_updated": time.time(),
                "error": str(e),
            }

    def clear_cache(self):
        """Clear the information cache to force fresh collection"""
        self._cache.clear()
        self._last_collection = 0.0

    def is_cache_valid(self) -> bool:
        """Check if cached data is still valid"""
        return self._cache and time.time() - self._last_collection < self._cache_timeout


# Convenience function for quick access
def get_system_info(project_root: Path | None = None, use_cache: bool = True) -> SystemInformation:
    """Get system information with optional caching"""
    collector = SystemInfoCollector(project_root)
    return collector.collect_all(use_cache=use_cache)


def get_performance_summary(project_root: Path | None = None) -> dict[str, Any]:
    """Get performance summary for dashboard"""
    collector = SystemInfoCollector(project_root)
    return collector.get_performance_summary()
