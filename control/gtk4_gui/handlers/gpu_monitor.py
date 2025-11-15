#!/usr/bin/env python3
"""
GPU Device Monitor

Provides real-time enumeration of GPU devices using nvidia-smi command.
Captures both basic and detailed output for display in UI.
"""

import logging
import sys
from pathlib import Path

# Add utils to path for subprocess_utils import
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))

from subprocess_utils import SystemCommandRunner

logger = logging.getLogger(__name__)


class GPUMonitor:
    """Monitor and enumerate GPU devices using nvidia-smi"""

    def __init__(self):
        """Initialize GPU monitor"""
        self.last_basic_output = ""
        self.last_detailed_output = ""
        self.runner = SystemCommandRunner(timeout=10)

    def get_basic_devices(self) -> str:
        """
        Get basic GPU device list using nvidia-smi.

        Returns:
            String containing nvidia-smi output
        """
        result = self.runner.run_nvidia_smi()

        if result["success"]:
            self.last_basic_output = result["output"]
            return result["output"]
        else:
            error_msg = result["error"] or f"nvidia-smi failed with code {result['returncode']}"
            logger.error(error_msg)
            return error_msg

    def get_detailed_devices(self) -> str:
        """
        Get detailed GPU device information using nvidia-smi --query-gpu.

        Returns:
            String containing nvidia-smi --query-gpu output
        """
        query = "index,name,driver_version,memory.total,memory.used,memory.free,temperature.gpu,utilization.gpu,utilization.memory"
        result = self.runner.run_nvidia_smi(query=query)

        if result["success"]:
            self.last_detailed_output = result["output"]
            return result["output"]
        else:
            error_msg = (
                result["error"] or f"nvidia-smi --query-gpu failed with code {result['returncode']}"
            )
            logger.warning(error_msg)
            return error_msg

    def refresh(self) -> tuple[str, str]:
        """
        Refresh both basic and detailed GPU device information.

        Returns:
            Tuple of (basic_output, detailed_output)
        """
        basic = self.get_basic_devices()
        detailed = self.get_detailed_devices()
        return basic, detailed

    def get_last_output(self) -> tuple[str, str]:
        """
        Get the last cached output without running commands.

        Returns:
            Tuple of (basic_output, detailed_output)
        """
        return self.last_basic_output, self.last_detailed_output
