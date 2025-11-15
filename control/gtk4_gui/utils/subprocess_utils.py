"""
Unified subprocess execution wrapper with standard error handling.

Eliminates duplicate error handling patterns across the codebase.
Provides consistent interface for subprocess execution with timeouts,
error handling, and optional output caching.
"""

import subprocess
from typing import Dict, Any, Optional
from pathlib import Path


class SubprocessRunner:
    """Unified subprocess execution with standard error handling."""

    def __init__(self, timeout: int = 10, cache: bool = False):
        """
        Initialize subprocess runner.

        Args:
            timeout: Default timeout in seconds
            cache: Whether to cache last output
        """
        self.timeout = timeout
        self.cache = cache
        self._last_output: Optional[str] = None
        self._last_error: Optional[str] = None

    def run(
        self,
        command: list[str],
        timeout: Optional[int] = None,
        cwd: Optional[Path] = None,
        shell: bool = False,
    ) -> Dict[str, Any]:
        """
        Execute command with standard error handling.

        Args:
            command: Command as list of strings (or string if shell=True)
            timeout: Override default timeout
            cwd: Working directory
            shell: Whether to use shell execution

        Returns:
            Dict with keys: success, output, error, returncode
        """
        timeout = timeout or self.timeout

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd,
                shell=shell,
            )

            success = result.returncode == 0
            output = result.stdout.strip() if success else result.stderr.strip()

            if self.cache:
                if success:
                    self._last_output = output
                else:
                    self._last_error = output

            return {
                "success": success,
                "output": output,
                "error": result.stderr.strip() if not success else "",
                "returncode": result.returncode,
            }

        except subprocess.TimeoutExpired:
            error_msg = f"Command timed out after {timeout} seconds"
            if self.cache:
                self._last_error = error_msg
            return {
                "success": False,
                "output": "",
                "error": error_msg,
                "returncode": -1,
            }

        except FileNotFoundError as e:
            error_msg = f"Command not found: {str(e)}"
            if self.cache:
                self._last_error = error_msg
            return {
                "success": False,
                "output": "",
                "error": error_msg,
                "returncode": -1,
            }

        except Exception as e:
            error_msg = f"Command execution failed: {str(e)}"
            if self.cache:
                self._last_error = error_msg
            return {
                "success": False,
                "output": "",
                "error": error_msg,
                "returncode": -1,
            }

    def run_shell(
        self, command: str, timeout: Optional[int] = None, cwd: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Execute shell command (string-based).

        Args:
            command: Shell command as string
            timeout: Override default timeout
            cwd: Working directory

        Returns:
            Dict with keys: success, output, error, returncode
        """
        return self.run(command, timeout=timeout, cwd=cwd, shell=True)

    def run_list(
        self,
        command: list[str],
        timeout: Optional[int] = None,
        cwd: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """
        Execute command as list (no shell).

        Args:
            command: Command as list of strings
            timeout: Override default timeout
            cwd: Working directory

        Returns:
            Dict with keys: success, output, error, returncode
        """
        return self.run(command, timeout=timeout, cwd=cwd, shell=False)

    def get_last_output(self) -> Optional[str]:
        """Get cached last successful output."""
        return self._last_output

    def get_last_error(self) -> Optional[str]:
        """Get cached last error."""
        return self._last_error


class SystemCommandRunner(SubprocessRunner):
    """Specialized runner for system commands (nvidia-smi, lsusb, arecord, etc)."""

    def run_nvidia_smi(
        self, query: Optional[str] = None, timeout: int = 10
    ) -> Dict[str, Any]:
        """
        Run nvidia-smi command.

        Args:
            query: Optional query string (e.g., 'index,name,driver_version')
            timeout: Command timeout

        Returns:
            Dict with success, output, error, returncode
        """
        if query:
            cmd = ["nvidia-smi", f"--query-gpu={query}", "--format=csv"]
        else:
            cmd = ["nvidia-smi"]

        return self.run_list(cmd, timeout=timeout)

    def run_lsusb(self, verbose: bool = False, timeout: int = 10) -> Dict[str, Any]:
        """
        Run lsusb command.

        Args:
            verbose: Whether to use verbose output (-v flag)
            timeout: Command timeout

        Returns:
            Dict with success, output, error, returncode
        """
        cmd = ["lsusb"]
        if verbose:
            cmd.append("-v")

        return self.run_list(cmd, timeout=timeout)

    def run_arecord(
        self,
        device: Optional[str] = None,
        format: str = "S16_LE",
        rate: int = 16000,
        channels: int = 1,
        timeout: int = 10,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Run arecord command.

        Args:
            device: Audio device (e.g., 'hw:0,0')
            format: Audio format (default: S16_LE)
            rate: Sample rate (default: 16000)
            channels: Number of channels (default: 1)
            timeout: Command timeout
            **kwargs: Additional arguments

        Returns:
            Dict with success, output, error, returncode
        """
        cmd = ["arecord"]

        if device:
            cmd.extend(["-D", device])

        cmd.extend(["-f", format, "-r", str(rate), "-c", str(channels)])

        return self.run_list(cmd, timeout=timeout)

    def run_aplay_list(self, timeout: int = 10) -> Dict[str, Any]:
        """
        List audio playback devices using aplay.

        Args:
            timeout: Command timeout

        Returns:
            Dict with success, output, error, returncode
        """
        return self.run_list(["aplay", "-l"], timeout=timeout)

    def run_arecord_list(self, timeout: int = 10) -> Dict[str, Any]:
        """
        List audio capture devices using arecord.

        Args:
            timeout: Command timeout

        Returns:
            Dict with success, output, error, returncode
        """
        return self.run_list(["arecord", "-l"], timeout=timeout)
