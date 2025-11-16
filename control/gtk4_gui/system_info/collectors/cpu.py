"""
@llm-doc CPU and Motherboard Information Collection
@llm-version 1.0.0
@llm-date 2025-11-15

CPU and motherboard information collection from system utilities and /proc/cpuinfo.
"""

import builtins
import contextlib
import logging
import platform
from pathlib import Path

from subprocess_utils import SubprocessRunner

# Import psutil with fallback
try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

logger = logging.getLogger(__name__)


class CPUCollector:
    """Collects CPU and motherboard information."""

    def __init__(self):
        self.runner = SubprocessRunner(timeout=10)

    def collect_motherboard_info(self) -> dict:
        """Collect motherboard information from dmidecode or /sys/class/dmi/id/"""
        motherboard = {}

        # Try dmidecode first (requires root)
        result = self.runner.run_list(["dmidecode", "-t", "baseboard"])
        if result["success"]:
            for line in result["output"].split("\n"):
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
                    pass
                except Exception as e:
                    logger.debug(f"Failed to read {dmi_file}: {e}")

        return motherboard

    def collect_cpu_details(self) -> dict:
        """Collect detailed CPU information (brand, series, cache, stepping)"""
        cpu_details = {}

        try:
            with open("/proc/cpuinfo") as f:
                cpuinfo_content = f.read()

            for line in cpuinfo_content.split("\n"):
                line = line.strip()

                if line.startswith("model name"):
                    model_name = line.split(":", 1)[1].strip()
                    cpu_details["model_name"] = model_name
                    if "Intel" in model_name:
                        cpu_details["brand"] = "Intel"
                    elif "AMD" in model_name:
                        cpu_details["brand"] = "AMD"

                elif line.startswith("stepping"):
                    with contextlib.suppress(builtins.BaseException):
                        cpu_details["stepping"] = line.split(":", 1)[1].strip()

                elif line.startswith("cache size"):
                    try:
                        cache_str = line.split(":", 1)[1].strip()
                        cpu_details["cache"] = cache_str
                    except:
                        pass

                elif line.startswith("cpu family"):
                    with contextlib.suppress(builtins.BaseException):
                        cpu_details["family"] = line.split(":", 1)[1].strip()

                elif line.startswith("model") and "model name" not in line:
                    with contextlib.suppress(builtins.BaseException):
                        cpu_details["model_number"] = line.split(":", 1)[1].strip()
        except Exception as e:
            logger.debug(f"Failed to read /proc/cpuinfo: {e}")

        return cpu_details

    def collect_cpu_info(self):
        """Collect CPU information from multiple sources"""
        from ..system_info import CPUInfo

        cpu_info = CPUInfo()
        cpu_info.architecture = platform.machine()

        if PSUTIL_AVAILABLE:
            cpu_info.cores = psutil.cpu_count(logical=False) or 0
            cpu_info.threads = psutil.cpu_count(logical=True) or 0
            cpu_info.usage_percent = psutil.cpu_percent(interval=1)

            try:
                freq = psutil.cpu_freq()
                if freq:
                    cpu_info.frequency_mhz = freq.current
            except:
                pass

        # Get detailed info from lscpu
        result = self.runner.run_list(["lscpu"])
        if result["success"]:
            for line in result["output"].split("\n"):
                if "Model name:" in line:
                    cpu_info.model = line.split(":", 1)[1].strip()
                elif "CPU(s):" in line and "NUMA" not in line:
                    with contextlib.suppress(builtins.BaseException):
                        cpu_info.threads = int(line.split(":", 1)[1].strip())
                elif "Core(s) per socket:" in line:
                    try:
                        cores_per_socket = int(line.split(":", 1)[1].strip())
                        socket_count = 1
                        for line_item in result["output"].split("\n"):
                            if "Socket(s):" in line_item:
                                socket_count = int(line_item.split(":", 1)[1].strip())
                                break
                        cpu_info.cores = cores_per_socket * socket_count
                    except:
                        pass
                elif "Flags:" in line:
                    flags = line.split(":", 1)[1].strip().split()
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
                    cpu_info.features = [f for f in flags if any(feat in f.lower() for feat in interesting_features)]

        return cpu_info
