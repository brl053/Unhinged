"""
@llm-doc GPU Information Collection
@llm-version 1.0.0
@llm-date 2025-11-15

GPU information collection using lspci, nvidia-smi, and modinfo.
"""

import logging

from subprocess_utils import SubprocessRunner

logger = logging.getLogger(__name__)


class GPUCollector:
    """Collects GPU information."""

    def __init__(self):
        self.runner = SubprocessRunner(timeout=10)

    def collect_gpu_info(self):
        """Collect GPU information"""
        from ..system_info import GPUInfo

        gpu_info = GPUInfo()

        # Try lspci for GPU information
        result = self.runner.run_list(["lspci", "-v"])
        if result["success"]:
            for line in result["output"].split("\n"):
                if "VGA compatible controller" in line or "Display controller" in line:
                    parts = line.split(": ", 1)
                    if len(parts) > 1:
                        gpu_desc = parts[1]

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
            result = self.runner.run_list(
                [
                    "nvidia-smi",
                    "--query-gpu=driver_version",
                    "--format=csv,noheader,nounits",
                ]
            )
            if result["success"]:
                gpu_info.driver = f"NVIDIA {result['output'].strip()}"
        elif gpu_info.vendor == "AMD":
            result = self.runner.run_list(["modinfo", "amdgpu"])
            if result["success"]:
                for line in result["output"].split("\n"):
                    if "version:" in line:
                        gpu_info.driver = f"AMDGPU {line.split(':', 1)[1].strip()}"
                        break

        return gpu_info
