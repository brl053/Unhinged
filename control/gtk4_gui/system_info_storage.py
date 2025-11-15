"""
@llm-doc Storage Information Collection
@llm-version 1.0.0
@llm-date 2025-11-15

Storage device and filesystem information collection using psutil and lsblk.
"""

import json
import logging

from subprocess_utils import SubprocessRunner

# Import psutil with fallback
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

logger = logging.getLogger(__name__)


class StorageCollector:
    """Collects storage and filesystem information."""

    def __init__(self):
        self.runner = SubprocessRunner(timeout=10)

    def collect_storage_info(self):
        """Collect storage information"""
        from .system_info import StorageInfo, StorageDevice

        storage_info = StorageInfo()

        if PSUTIL_AVAILABLE:
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
                    continue
                except Exception as e:
                    logger.warning(f"Failed to get usage for {partition.mountpoint}: {e}")
                    continue
        else:
            # Fallback to lsblk command
            result = self.runner.run_list(["lsblk", "-J", "-o", "NAME,SIZE,MOUNTPOINT,FSTYPE"])
            if result["success"]:
                try:
                    data = json.loads(result["output"])
                    for device in data.get("blockdevices", []):
                        self._parse_lsblk_device(device, storage_info)
                except json.JSONDecodeError:
                    logger.warning("Failed to parse lsblk JSON output")

        return storage_info

    def _parse_lsblk_device(self, device: dict, storage_info):
        """Parse lsblk device information recursively"""
        from .system_info import StorageDevice

        if device.get("mountpoint") and device.get("size"):
            mountpoint = device["mountpoint"]
            try:
                if PSUTIL_AVAILABLE:
                    usage = psutil.disk_usage(mountpoint)
                    total_gb = usage.total / (1024**3)
                    used_gb = usage.used / (1024**3)
                    free_gb = usage.free / (1024**3)
                    usage_percent = (usage.used / usage.total) * 100 if usage.total > 0 else 0
                else:
                    size_str = device["size"]
                    total_gb = self._parse_size_string(size_str)
                    used_gb = 0
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
                return number * multipliers.get(unit, 1) / 1024
            except ValueError:
                return 0.0
        else:
            try:
                return float(size_str) / (1024**3)
            except ValueError:
                return 0.0

