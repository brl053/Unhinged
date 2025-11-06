#!/usr/bin/env python3
"""
GPU Device Monitor

Provides real-time enumeration of GPU devices using nvidia-smi command.
Captures both basic and detailed output for display in UI.
"""

import subprocess
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class GPUMonitor:
    """Monitor and enumerate GPU devices using nvidia-smi"""

    def __init__(self):
        """Initialize GPU monitor"""
        self.last_basic_output = ""
        self.last_detailed_output = ""

    def get_basic_devices(self) -> str:
        """
        Get basic GPU device list using nvidia-smi.
        
        Returns:
            String containing nvidia-smi output
        """
        try:
            result = subprocess.run(
                ['nvidia-smi'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                self.last_basic_output = result.stdout
                return result.stdout
            else:
                error_msg = f"nvidia-smi failed: {result.stderr}"
                logger.error(error_msg)
                return error_msg
                
        except subprocess.TimeoutExpired:
            error_msg = "nvidia-smi command timed out"
            logger.error(error_msg)
            return error_msg
        except FileNotFoundError:
            error_msg = "nvidia-smi command not found"
            logger.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Error running nvidia-smi: {e}"
            logger.error(error_msg)
            return error_msg

    def get_detailed_devices(self) -> str:
        """
        Get detailed GPU device information using nvidia-smi --query-gpu.
        
        Returns:
            String containing nvidia-smi --query-gpu output
        """
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=index,name,driver_version,memory.total,memory.used,memory.free,temperature.gpu,utilization.gpu,utilization.memory', '--format=csv'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                self.last_detailed_output = result.stdout
                return result.stdout
            else:
                error_msg = f"nvidia-smi --query-gpu failed: {result.stderr}"
                logger.warning(error_msg)
                return error_msg
                
        except subprocess.TimeoutExpired:
            error_msg = "nvidia-smi --query-gpu command timed out"
            logger.warning(error_msg)
            return error_msg
        except FileNotFoundError:
            error_msg = "nvidia-smi command not found"
            logger.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Error running nvidia-smi --query-gpu: {e}"
            logger.error(error_msg)
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

