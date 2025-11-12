#!/usr/bin/env python3
"""
USB Device Monitor

Provides real-time enumeration of USB devices using lsusb command.
Captures both basic and verbose output for display in UI.
"""

import logging
import sys
from typing import Optional
from pathlib import Path

# Add utils to path for subprocess_utils import
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))

from subprocess_utils import SystemCommandRunner

logger = logging.getLogger(__name__)


class USBMonitor:
    """Monitor and enumerate USB devices using lsusb"""

    def __init__(self):
        """Initialize USB monitor"""
        self.last_basic_output = ""
        self.last_verbose_output = ""
        self.runner = SystemCommandRunner(timeout=5)

    def get_basic_devices(self) -> str:
        """
        Get basic USB device list using lsusb.

        Returns:
            String containing lsusb output
        """
        result = self.runner.run_lsusb(verbose=False)

        if result["success"]:
            self.last_basic_output = result["output"]
            return result["output"]
        else:
            error_msg = result["error"] or f"lsusb failed with code {result['returncode']}"
            logger.error(error_msg)
            return error_msg

    def get_verbose_devices(self) -> str:
        """
        Get verbose USB device information using lsusb -v.

        Returns:
            String containing lsusb -v output
        """
        result = self.runner.run_lsusb(verbose=True)

        if result["success"]:
            self.last_verbose_output = result["output"]
            return result["output"]
        else:
            error_msg = result["error"] or f"lsusb -v failed with code {result['returncode']}"
            logger.warning(error_msg)
            return error_msg

    def refresh(self) -> tuple[str, str]:
        """
        Refresh both basic and verbose USB device information.
        
        Returns:
            Tuple of (basic_output, verbose_output)
        """
        basic = self.get_basic_devices()
        verbose = self.get_verbose_devices()
        return basic, verbose

    def get_last_output(self) -> tuple[str, str]:
        """
        Get the last cached output without running commands.
        
        Returns:
            Tuple of (basic_output, verbose_output)
        """
        return self.last_basic_output, self.last_verbose_output

