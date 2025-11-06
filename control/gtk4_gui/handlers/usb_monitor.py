#!/usr/bin/env python3
"""
USB Device Monitor

Provides real-time enumeration of USB devices using lsusb command.
Captures both basic and verbose output for display in UI.
"""

import subprocess
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class USBMonitor:
    """Monitor and enumerate USB devices using lsusb"""

    def __init__(self):
        """Initialize USB monitor"""
        self.last_basic_output = ""
        self.last_verbose_output = ""

    def get_basic_devices(self) -> str:
        """
        Get basic USB device list using lsusb.
        
        Returns:
            String containing lsusb output
        """
        try:
            result = subprocess.run(
                ['lsusb'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                self.last_basic_output = result.stdout
                return result.stdout
            else:
                error_msg = f"lsusb failed: {result.stderr}"
                logger.error(error_msg)
                return error_msg
                
        except subprocess.TimeoutExpired:
            error_msg = "lsusb command timed out"
            logger.error(error_msg)
            return error_msg
        except FileNotFoundError:
            error_msg = "lsusb command not found"
            logger.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Error running lsusb: {e}"
            logger.error(error_msg)
            return error_msg

    def get_verbose_devices(self) -> str:
        """
        Get verbose USB device information using lsusb -v.
        
        Returns:
            String containing lsusb -v output
        """
        try:
            result = subprocess.run(
                ['lsusb', '-v'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                self.last_verbose_output = result.stdout
                return result.stdout
            else:
                # lsusb -v may fail due to permissions, try with sudo
                try:
                    result = subprocess.run(
                        ['sudo', 'lsusb', '-v'],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if result.returncode == 0:
                        self.last_verbose_output = result.stdout
                        return result.stdout
                except Exception:
                    pass
                
                error_msg = f"lsusb -v failed: {result.stderr}"
                logger.warning(error_msg)
                return error_msg
                
        except subprocess.TimeoutExpired:
            error_msg = "lsusb -v command timed out"
            logger.warning(error_msg)
            return error_msg
        except FileNotFoundError:
            error_msg = "lsusb command not found"
            logger.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Error running lsusb -v: {e}"
            logger.error(error_msg)
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

