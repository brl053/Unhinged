#!/usr/bin/env python3
"""
@llm-doc System Information Collection Module for GTK4 UI
@llm-version 1.0.0
@llm-date 2025-10-28

Comprehensive system information gathering using psutil, platform, and system utilities.
Provides structured data for the GTK4 system info page with proper error handling and caching.
"""

import json
import logging
import os
import platform
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Add utils to path for subprocess_utils import
sys.path.insert(0, str(Path(__file__).parent / "utils"))

import builtins
import contextlib

from subprocess_utils import SubprocessRunner

# Import psutil with fallback
try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# Set up logging
logger = logging.getLogger(__name__)


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
    Main system information collector class.

    Gathers comprehensive system information using multiple sources:
    - psutil for performance metrics
    - platform module for system details
    - System utilities (lscpu, lshw, lsblk, etc.)
    - Existing Unhinged monitoring systems
    """

    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self._cache = {}
        self._cache_timeout = 5.0  # Cache for 5 seconds
        self._last_collection = 0.0

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
            system_info.motherboard = self._collect_motherboard_info()
        except Exception as e:
            logger.error(f"Failed to collect motherboard info: {e}")
            system_info.collection_errors.append(f"Motherboard: {str(e)}")

        try:
            system_info.cpu = self._collect_cpu_info()
        except Exception as e:
            logger.error(f"Failed to collect CPU info: {e}")
            system_info.collection_errors.append(f"CPU: {str(e)}")

        try:
            system_info.cpu_details = self._collect_cpu_details()
        except Exception as e:
            logger.error(f"Failed to collect CPU details: {e}")
            system_info.collection_errors.append(f"CPU Details: {str(e)}")

        try:
            system_info.memory = self._collect_memory_info()
        except Exception as e:
            logger.error(f"Failed to collect memory info: {e}")
            system_info.collection_errors.append(f"Memory: {str(e)}")

        try:
            system_info.storage = self._collect_storage_info()
        except Exception as e:
            logger.error(f"Failed to collect storage info: {e}")
            system_info.collection_errors.append(f"Storage: {str(e)}")

        try:
            system_info.gpu = self._collect_gpu_info()
        except Exception as e:
            logger.error(f"Failed to collect GPU info: {e}")
            system_info.collection_errors.append(f"GPU: {str(e)}")

        try:
            system_info.network = self._collect_network_info()
        except Exception as e:
            logger.error(f"Failed to collect network info: {e}")
            system_info.collection_errors.append(f"Network: {str(e)}")

        try:
            system_info.system = self._collect_system_status()
        except Exception as e:
            logger.error(f"Failed to collect system status: {e}")
            system_info.collection_errors.append(f"System: {str(e)}")

        try:
            system_info.platform = self._collect_platform_status()
        except Exception as e:
            logger.error(f"Failed to collect platform status: {e}")
            system_info.collection_errors.append(f"Platform: {str(e)}")

        # Update cache
        self._cache["system_info"] = system_info
        self._last_collection = current_time

        # Log collection summary
        if system_info.collection_errors:
            logger.warning(
                f"⚠️  System information collected with {len(system_info.collection_errors)} errors"
            )
            for error in system_info.collection_errors:
                logger.warning(f"  - {error}")
        else:
            logger.info("✅ System information collected successfully")

        return system_info

    def _run_command(self, command: list[str], timeout: int = 10) -> tuple[bool, str]:
        """
        Run a system command safely with timeout.

        Returns:
            Tuple of (success, output)
        """
        runner = SubprocessRunner(timeout=timeout)
        result = runner.run_list(command)
        return result["success"], result["output"]

    def _collect_motherboard_info(self) -> dict:
        """Collect motherboard information from dmidecode or /sys/class/dmi/id/"""
        motherboard = {}

        # Try dmidecode first (requires root)
        success, output = self._run_command(["dmidecode", "-t", "baseboard"])
        if success:
            for line in output.split("\n"):
                line = line.strip()
                if line.startswith("Manufacturer:"):
                    motherboard["manufacturer"] = line.split(":", 1)[1].strip()
                elif line.startswith("Product Name:"):
                    motherboard["model"] = line.split(":", 1)[1].strip()
                elif line.startswith("Serial Number:"):
                    motherboard["serial"] = line.split(":", 1)[1].strip()
                elif line.startswith("Version:"):
                    motherboard["version"] = line.split(":", 1)[1].strip()
            return motherboard

        # Fallback to /sys/class/dmi/id/ (no root needed)
        dmi_path = Path("/sys/class/dmi/id")
        if dmi_path.exists():
            # Try to read each file, skip if permission denied
            for dmi_file, key in [
                ("board_vendor", "manufacturer"),
                ("board_name", "model"),
                ("board_serial", "serial"),
                ("board_version", "version"),
            ]:
                try:
                    file_path = dmi_path / dmi_file
                    if file_path.exists():
                        motherboard[key] = file_path.read_text().strip()
                except (PermissionError, OSError):
                    # Skip files we can't read
                    pass
                except Exception as e:
                    logger.debug(f"Failed to read {dmi_file}: {e}")

        return motherboard

    def _collect_cpu_details(self) -> dict:
        """Collect detailed CPU information (brand, series, cache, stepping)"""
        cpu_details = {}

        # Try to read from /proc/cpuinfo
        try:
            with open("/proc/cpuinfo") as f:
                cpuinfo_content = f.read()

            # Parse cpuinfo
            for line in cpuinfo_content.split("\n"):
                line = line.strip()

                # Get model name (contains brand and series)
                if line.startswith("model name"):
                    model_name = line.split(":", 1)[1].strip()
                    cpu_details["model_name"] = model_name

                    # Extract brand (Intel or AMD)
                    if "Intel" in model_name:
                        cpu_details["brand"] = "Intel"
                    elif "AMD" in model_name:
                        cpu_details["brand"] = "AMD"

                # Get stepping
                elif line.startswith("stepping"):
                    with contextlib.suppress(builtins.BaseException):
                        cpu_details["stepping"] = line.split(":", 1)[1].strip()

                # Get cache info
                elif line.startswith("cache size"):
                    try:
                        cache_str = line.split(":", 1)[1].strip()
                        cpu_details["cache"] = cache_str
                    except:
                        pass

                # Get family
                elif line.startswith("cpu family"):
                    with contextlib.suppress(builtins.BaseException):
                        cpu_details["family"] = line.split(":", 1)[1].strip()

                # Get model number
                elif line.startswith("model") and "model name" not in line:
                    with contextlib.suppress(builtins.BaseException):
                        cpu_details["model_number"] = line.split(":", 1)[1].strip()
        except Exception as e:
            logger.debug(f"Failed to read /proc/cpuinfo: {e}")

        return cpu_details

    def _collect_cpu_info(self) -> CPUInfo:
        """Collect CPU information from multiple sources"""
        cpu_info = CPUInfo()

        # Basic info from platform
        cpu_info.architecture = platform.machine()

        if PSUTIL_AVAILABLE:
            cpu_info.cores = psutil.cpu_count(logical=False) or 0
            cpu_info.threads = psutil.cpu_count(logical=True) or 0
            cpu_info.usage_percent = psutil.cpu_percent(interval=1)

            # CPU frequency
            try:
                freq = psutil.cpu_freq()
                if freq:
                    cpu_info.frequency_mhz = freq.current
            except:
                pass

        # Try to get detailed info from lscpu
        success, output = self._run_command(["lscpu"])
        if success:
            for line in output.split("\n"):
                if "Model name:" in line:
                    cpu_info.model = line.split(":", 1)[1].strip()
                elif "CPU(s):" in line and "NUMA" not in line:
                    with contextlib.suppress(builtins.BaseException):
                        cpu_info.threads = int(line.split(":", 1)[1].strip())
                elif "Core(s) per socket:" in line:
                    try:
                        cores_per_socket = int(line.split(":", 1)[1].strip())
                        # Get socket count
                        socket_count = 1
                        for l in output.split("\n"):
                            if "Socket(s):" in l:
                                socket_count = int(l.split(":", 1)[1].strip())
                                break
                        cpu_info.cores = cores_per_socket * socket_count
                    except:
                        pass
                elif "Flags:" in line:
                    flags = line.split(":", 1)[1].strip().split()
                    # Filter for interesting features
                    interesting_features = [
                        "avx",
                        "avx2",
                        "sse",
                        "sse2",
                        "sse3",
                        "sse4_1",
                        "sse4_2",
                        "aes",
                        "fma",
                    ]
                    cpu_info.features = [
                        f for f in flags if any(feat in f.lower() for feat in interesting_features)
                    ]

        return cpu_info

    def _collect_memory_info(self) -> MemoryInfo:
        """Collect memory information"""
        memory_info = MemoryInfo()

        if PSUTIL_AVAILABLE:
            # Virtual memory
            vm = psutil.virtual_memory()
            memory_info.total_gb = vm.total / (1024**3)
            memory_info.available_gb = vm.available / (1024**3)
            memory_info.used_gb = vm.used / (1024**3)
            memory_info.usage_percent = vm.percent

            # Swap memory
            swap = psutil.swap_memory()
            memory_info.swap_total_gb = swap.total / (1024**3)
            memory_info.swap_used_gb = swap.used / (1024**3)
            memory_info.swap_percent = swap.percent
        else:
            # Fallback to /proc/meminfo
            try:
                with open("/proc/meminfo") as f:
                    meminfo = f.read()

                for line in meminfo.split("\n"):
                    if "MemTotal:" in line:
                        memory_info.total_gb = int(line.split()[1]) / (1024**2)
                    elif "MemAvailable:" in line:
                        memory_info.available_gb = int(line.split()[1]) / (1024**2)
                    elif "SwapTotal:" in line:
                        memory_info.swap_total_gb = int(line.split()[1]) / (1024**2)
                    elif "SwapFree:" in line:
                        swap_free = int(line.split()[1]) / (1024**2)
                        memory_info.swap_used_gb = memory_info.swap_total_gb - swap_free

                if memory_info.total_gb > 0:
                    memory_info.used_gb = memory_info.total_gb - memory_info.available_gb
                    memory_info.usage_percent = (memory_info.used_gb / memory_info.total_gb) * 100

                if memory_info.swap_total_gb > 0:
                    memory_info.swap_percent = (
                        memory_info.swap_used_gb / memory_info.swap_total_gb
                    ) * 100

            except Exception as e:
                logger.warning(f"Failed to read /proc/meminfo: {e}")

        return memory_info

    def _collect_storage_info(self) -> StorageInfo:
        """Collect storage information"""
        storage_info = StorageInfo()

        if PSUTIL_AVAILABLE:
            # Get disk partitions
            partitions = psutil.disk_partitions()

            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)

                    device = StorageDevice(
                        device=partition.device,
                        mountpoint=partition.mountpoint,
                        filesystem=partition.fstype,
                        total_gb=usage.total / (1024**3),
                        used_gb=usage.used / (1024**3),
                        free_gb=usage.free / (1024**3),
                        usage_percent=(usage.used / usage.total) * 100 if usage.total > 0 else 0,
                    )

                    storage_info.devices.append(device)
                    storage_info.total_storage_gb += device.total_gb
                    storage_info.total_used_gb += device.used_gb
                    storage_info.total_free_gb += device.free_gb

                except PermissionError:
                    # Skip inaccessible partitions
                    continue
                except Exception as e:
                    logger.warning(f"Failed to get usage for {partition.mountpoint}: {e}")
                    continue
        else:
            # Fallback to lsblk command
            success, output = self._run_command(
                ["lsblk", "-J", "-o", "NAME,SIZE,MOUNTPOINT,FSTYPE"]
            )
            if success:
                try:
                    data = json.loads(output)
                    for device in data.get("blockdevices", []):
                        self._parse_lsblk_device(device, storage_info)
                except json.JSONDecodeError:
                    logger.warning("Failed to parse lsblk JSON output")

        return storage_info

    def _parse_lsblk_device(self, device: dict, storage_info: StorageInfo):
        """Parse lsblk device information recursively"""
        if device.get("mountpoint") and device.get("size"):
            # Try to get usage information
            mountpoint = device["mountpoint"]
            try:
                if PSUTIL_AVAILABLE:
                    usage = psutil.disk_usage(mountpoint)
                    total_gb = usage.total / (1024**3)
                    used_gb = usage.used / (1024**3)
                    free_gb = usage.free / (1024**3)
                    usage_percent = (usage.used / usage.total) * 100 if usage.total > 0 else 0
                else:
                    # Parse size string (e.g., "100G", "1.5T")
                    size_str = device["size"]
                    total_gb = self._parse_size_string(size_str)
                    used_gb = 0  # Can't determine without df
                    free_gb = total_gb
                    usage_percent = 0

                storage_device = StorageDevice(
                    device=device.get("name", ""),
                    mountpoint=mountpoint,
                    filesystem=device.get("fstype", ""),
                    total_gb=total_gb,
                    used_gb=used_gb,
                    free_gb=free_gb,
                    usage_percent=usage_percent,
                )

                storage_info.devices.append(storage_device)
                storage_info.total_storage_gb += total_gb
                storage_info.total_used_gb += used_gb
                storage_info.total_free_gb += free_gb

            except Exception as e:
                logger.warning(f"Failed to get usage for {mountpoint}: {e}")

        # Process children recursively
        for child in device.get("children", []):
            self._parse_lsblk_device(child, storage_info)

    def _parse_size_string(self, size_str: str) -> float:
        """Parse size string like '100G' or '1.5T' to GB"""
        if not size_str:
            return 0.0

        size_str = size_str.strip().upper()
        if size_str[-1] in "KMGTPE":
            multipliers = {
                "K": 1 / 1024,
                "M": 1,
                "G": 1024,
                "T": 1024**2,
                "P": 1024**3,
                "E": 1024**4,
            }
            try:
                number = float(size_str[:-1])
                unit = size_str[-1]
                return number * multipliers.get(unit, 1) / 1024  # Convert to GB
            except ValueError:
                return 0.0
        else:
            try:
                return float(size_str) / (1024**3)  # Assume bytes
            except ValueError:
                return 0.0

    def _collect_gpu_info(self) -> GPUInfo:
        """Collect GPU information"""
        gpu_info = GPUInfo()

        # Try lspci for GPU information
        success, output = self._run_command(["lspci", "-v"])
        if success:
            for line in output.split("\n"):
                if "VGA compatible controller" in line or "Display controller" in line:
                    # Extract vendor and model
                    parts = line.split(": ", 1)
                    if len(parts) > 1:
                        gpu_desc = parts[1]

                        # Detect vendor
                        if "Intel" in gpu_desc:
                            gpu_info.vendor = "Intel"
                        elif "NVIDIA" in gpu_desc or "GeForce" in gpu_desc:
                            gpu_info.vendor = "NVIDIA"
                        elif "AMD" in gpu_desc or "Radeon" in gpu_desc or "ATI" in gpu_desc:
                            gpu_info.vendor = "AMD"
                        else:
                            gpu_info.vendor = "Unknown"

                        gpu_info.model = gpu_desc
                    break

        # Try to get driver information
        if gpu_info.vendor == "NVIDIA":
            success, output = self._run_command(
                [
                    "nvidia-smi",
                    "--query-gpu=driver_version",
                    "--format=csv,noheader,nounits",
                ]
            )
            if success:
                gpu_info.driver = f"NVIDIA {output.strip()}"
        elif gpu_info.vendor == "AMD":
            # Try to find AMD driver info
            success, output = self._run_command(["modinfo", "amdgpu"])
            if success:
                for line in output.split("\n"):
                    if "version:" in line:
                        gpu_info.driver = f"AMDGPU {line.split(':', 1)[1].strip()}"
                        break

        return gpu_info

    def _collect_network_info(self) -> NetworkInfo:
        """Collect network information"""
        network_info = NetworkInfo()

        # Get hostname
        network_info.hostname = platform.node()

        if PSUTIL_AVAILABLE:
            # Get network interfaces
            interfaces = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            io_counters = psutil.net_io_counters(pernic=True)

            for interface_name, addresses in interfaces.items():
                if interface_name == "lo":  # Skip loopback
                    continue

                interface = NetworkInterface(name=interface_name)

                # Get IP and MAC addresses
                for addr in addresses:
                    if addr.family.name == "AF_INET":
                        interface.ip_address = addr.address
                    elif addr.family.name == "AF_PACKET":
                        interface.mac_address = addr.address

                # Get interface status
                if interface_name in stats:
                    interface.status = "Up" if stats[interface_name].isup else "Down"

                # Get I/O statistics
                if interface_name in io_counters:
                    io = io_counters[interface_name]
                    interface.bytes_sent = io.bytes_sent
                    interface.bytes_recv = io.bytes_recv
                    network_info.total_bytes_sent += io.bytes_sent
                    network_info.total_bytes_recv += io.bytes_recv

                network_info.interfaces.append(interface)
        else:
            # Fallback to ip command
            success, output = self._run_command(["ip", "addr", "show"])
            if success:
                current_interface = None
                for line in output.split("\n"):
                    line = line.strip()
                    if ": " in line and "state" in line:
                        # New interface
                        parts = line.split(": ")
                        if len(parts) > 1:
                            interface_name = parts[1].split("@")[0]
                            if interface_name != "lo":
                                current_interface = NetworkInterface(name=interface_name)
                                if "state UP" in line:
                                    current_interface.status = "Up"
                                else:
                                    current_interface.status = "Down"
                                network_info.interfaces.append(current_interface)
                    elif current_interface and "inet " in line:
                        # IP address
                        parts = line.split()
                        if len(parts) > 1:
                            current_interface.ip_address = parts[1].split("/")[0]
                    elif current_interface and "link/ether" in line:
                        # MAC address
                        parts = line.split()
                        if len(parts) > 1:
                            current_interface.mac_address = parts[1]

        return network_info

    def _collect_system_status(self) -> SystemStatus:
        """Collect system status information"""
        system_status = SystemStatus()

        # Basic platform information
        system_status.os_name = platform.system()
        system_status.os_version = platform.release()
        system_status.architecture = platform.machine()
        system_status.hostname = platform.node()
        system_status.username = os.getenv("USER", "Unknown")

        # Kernel version
        success, output = self._run_command(["uname", "-r"])
        if success:
            system_status.kernel_version = output.strip()

        if PSUTIL_AVAILABLE:
            # Boot time and uptime
            system_status.boot_time = psutil.boot_time()
            system_status.uptime_seconds = time.time() - system_status.boot_time

            # Load average
            try:
                system_status.load_average = list(psutil.getloadavg())
            except AttributeError:
                # getloadavg not available on all platforms
                pass
        else:
            # Fallback to /proc/uptime
            try:
                with open("/proc/uptime") as f:
                    uptime_line = f.read().strip()
                    system_status.uptime_seconds = float(uptime_line.split()[0])
                    system_status.boot_time = time.time() - system_status.uptime_seconds
            except Exception:
                pass

            # Fallback to /proc/loadavg
            try:
                with open("/proc/loadavg") as f:
                    loadavg_line = f.read().strip()
                    loads = loadavg_line.split()[:3]
                    system_status.load_average = [float(load) for load in loads]
            except Exception:
                pass

        return system_status

    def _collect_platform_status(self) -> PlatformStatus:
        """Collect Unhinged platform-specific status"""
        platform_status = PlatformStatus()

        try:
            # Enhanced service health monitoring
            try:
                from control.service_health_monitor import ServiceHealthMonitor

                health_monitor = ServiceHealthMonitor()

                # Get all service statuses
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

                # Fallback to Docker container checking
                success, output = self._run_command(
                    ["docker", "ps", "--format", "table {{.Names}}\t{{.Status}}"]
                )
                if success:
                    lines = output.split("\n")[1:]  # Skip header
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

            # Enhanced VM status monitoring
            try:
                from control.vm_monitor import VMMonitor

                vm_monitor = VMMonitor()
                vm_status = vm_monitor.get_vm_status()

                # Enhance VM status with additional details
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

            # Enhanced build system status
            build_cache_dir = self.project_root / ".build-cache"
            build_dir = self.project_root / "build"

            if build_cache_dir.exists() and build_dir.exists():
                # Check for recent build activity
                try:
                    cache_files = list(build_cache_dir.glob("*"))
                    if cache_files:
                        latest_cache = max(cache_files, key=lambda p: p.stat().st_mtime)
                        cache_age = time.time() - latest_cache.stat().st_mtime
                        if cache_age < 3600:  # Less than 1 hour old
                            platform_status.build_system_status = "Active (recent builds)"
                        else:
                            platform_status.build_system_status = "Available (idle)"
                    else:
                        platform_status.build_system_status = "Available (no cache)"
                except Exception:
                    platform_status.build_system_status = "Available"
            else:
                platform_status.build_system_status = "Not initialized"

            # Enhanced graphics platform status
            graphics_lib = self.project_root / "libs" / "graphics"
            vm_dir = self.project_root / "vm"

            if graphics_lib.exists() and vm_dir.exists():
                # Check for graphics-related processes
                success, output = self._run_command(["pgrep", "-f", "qemu.*gl"])
                if success and output.strip():
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

    def get_performance_summary(self) -> dict[str, Any]:
        """Get a quick performance summary for dashboard display"""
        try:
            system_info = self.collect_all(use_cache=True)

            return {
                "cpu_usage": system_info.cpu.usage_percent,
                "memory_usage": system_info.memory.usage_percent,
                "storage_usage": (
                    system_info.storage.total_used_gb / system_info.storage.total_storage_gb * 100
                )
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
    """
    Convenience function to get system information.

    Args:
        project_root: Path to project root (auto-detected if None)
        use_cache: Whether to use cached data

    Returns:
        SystemInformation object
    """
    collector = SystemInfoCollector(project_root)
    return collector.collect_all(use_cache=use_cache)


def get_performance_summary(project_root: Path | None = None) -> dict[str, Any]:
    """
    Convenience function to get performance summary.

    Args:
        project_root: Path to project root (auto-detected if None)

    Returns:
        Dictionary with performance metrics
    """
    collector = SystemInfoCollector(project_root)
    return collector.get_performance_summary()


if __name__ == "__main__":
    # Test the system info collection
    import pprint

    print("🔍 Testing System Information Collection")
    print("=" * 50)

    collector = SystemInfoCollector()
    system_info = collector.collect_all(use_cache=False)

    print(f"Collection time: {time.ctime(system_info.collection_time)}")
    print(f"Errors: {len(system_info.collection_errors)}")

    if system_info.collection_errors:
        print("Errors encountered:")
        for error in system_info.collection_errors:
            print(f"  - {error}")

    print("\n📊 Performance Summary:")
    summary = collector.get_performance_summary()
    pprint.pprint(summary)

    print("\n💻 System Overview:")
    print(f"OS: {system_info.system.os_name} {system_info.system.os_version}")
    print(f"CPU: {system_info.cpu.model} ({system_info.cpu.cores} cores)")
    print(f"Memory: {system_info.memory.total_gb:.1f} GB total")
    print(f"Storage: {system_info.storage.total_storage_gb:.1f} GB total")
    print(f"GPU: {system_info.gpu.vendor} {system_info.gpu.model}")

    print("\n✅ System information collection test completed")
