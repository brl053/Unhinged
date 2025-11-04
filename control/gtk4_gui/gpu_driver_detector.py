#!/usr/bin/env python3
"""
GPU Driver Detection Module

Detects and reports GPU driver information for NVIDIA GPUs.
Provides read-only access to driver version, CUDA version, and GPU specifications.

Philosophy: GPUs first, then each vendor extends the GPU abstraction with their own implementation.
We don't care about proprietary vs open-source - we care about what works.
"""

import subprocess
import re
from dataclasses import dataclass
from typing import Optional, List, Dict, Any


@dataclass
class GPUInfo:
    """GPU information container"""
    name: str
    driver_version: str
    cuda_version: Optional[str]
    memory_mb: int
    compute_capability: Optional[str]
    status: str  # "OK", "WARNING", "ERROR"
    details: Dict[str, Any]


class GPUDriverDetector:
    """Detects GPU drivers and specifications"""

    def __init__(self):
        self.gpus: List[GPUInfo] = []
        self.nvidia_available = False
        self.driver_version = None
        self.cuda_version = None
        self._detect_nvidia()

    def _detect_nvidia(self):
        """Detect NVIDIA GPU and driver information"""
        try:
            # Check if nvidia-smi is available
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=index,name,driver_version,memory.total,compute_cap"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                self.nvidia_available = True
                self._parse_nvidia_output(result.stdout)
                self._get_cuda_version()
            else:
                self.nvidia_available = False

        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.nvidia_available = False

    def _parse_nvidia_output(self, output: str):
        """Parse nvidia-smi output"""
        try:
            lines = output.strip().split('\n')
            for line in lines:
                if not line.strip():
                    continue

                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 5:
                    try:
                        gpu_index = int(parts[0])
                        gpu_name = parts[1]
                        driver_version = parts[2]
                        memory_str = parts[3]
                        compute_cap = parts[4]

                        # Parse memory (format: "XXXX MiB")
                        memory_mb = int(memory_str.split()[0]) if memory_str else 0

                        # Store driver version
                        if not self.driver_version:
                            self.driver_version = driver_version

                        gpu_info = GPUInfo(
                            name=gpu_name,
                            driver_version=driver_version,
                            cuda_version=None,  # Will be filled by _get_cuda_version
                            memory_mb=memory_mb,
                            compute_capability=compute_cap,
                            status="OK",
                            details={
                                "index": gpu_index,
                                "memory_gb": round(memory_mb / 1024, 2),
                                "driver_type": self._detect_driver_type(driver_version)
                            }
                        )
                        self.gpus.append(gpu_info)

                    except (ValueError, IndexError):
                        continue

        except Exception as e:
            print(f"⚠️ Error parsing NVIDIA output: {e}")

    def _get_cuda_version(self):
        """Get CUDA version from nvidia-smi"""
        try:
            result = subprocess.run(
                ["nvidia-smi"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                # Look for CUDA Version line
                for line in result.stdout.split('\n'):
                    if 'CUDA Version' in line:
                        # Extract version (format: "CUDA Version: 12.8")
                        match = re.search(r'CUDA Version:\s+([\d.]+)', line)
                        if match:
                            self.cuda_version = match.group(1)
                            # Update all GPUs with CUDA version
                            for gpu in self.gpus:
                                gpu.cuda_version = self.cuda_version
                        break

        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    def _detect_driver_type(self, driver_version: str) -> str:
        """Detect if driver is open-source or proprietary"""
        # Open-source drivers typically have "-open" in the package name
        # But we detect from version patterns
        if "open" in driver_version.lower():
            return "Open-Source"
        else:
            return "Proprietary"

    def get_gpu_list(self) -> List[GPUInfo]:
        """Get list of detected GPUs"""
        return self.gpus

    def get_driver_info(self) -> Dict[str, Any]:
        """Get overall driver information"""
        return {
            "nvidia_available": self.nvidia_available,
            "driver_version": self.driver_version,
            "cuda_version": self.cuda_version,
            "gpu_count": len(self.gpus),
            "gpus": [
                {
                    "name": gpu.name,
                    "driver_version": gpu.driver_version,
                    "cuda_version": gpu.cuda_version,
                    "memory_gb": gpu.details.get("memory_gb", 0),
                    "compute_capability": gpu.compute_capability,
                    "driver_type": gpu.details.get("driver_type", "Unknown"),
                    "status": gpu.status
                }
                for gpu in self.gpus
            ]
        }

    def get_status_summary(self) -> str:
        """Get human-readable status summary"""
        if not self.nvidia_available:
            return "No NVIDIA GPU detected"

        if not self.gpus:
            return "NVIDIA driver not properly installed"

        gpu_count = len(self.gpus)
        total_memory = sum(gpu.memory_mb for gpu in self.gpus) / 1024
        driver_type = self.gpus[0].details.get("driver_type", "Unknown")

        return (
            f"{gpu_count} GPU(s) detected | "
            f"Driver: {self.driver_version} ({driver_type}) | "
            f"CUDA: {self.cuda_version or 'N/A'} | "
            f"Total Memory: {total_memory:.1f} GB"
        )

