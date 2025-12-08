"""Strace integration for kernel-level syscall capture.

Provides optional strace wrapping for graph execution to capture
all syscalls at the kernel level. This feeds into the CDC stream.

Usage:
    from libs.python.graph.strace import run_with_strace

    result, syscalls = run_with_strace(
        [sys.executable, script_path],
        capture_output=True,
    )

    for call in syscalls:
        session_ctx.syscall(call["name"], call["args"], call["result"])

Requires:
    - strace binary installed (apt install strace)
    - May require root or ptrace permissions
"""

from __future__ import annotations

import os
import re
import subprocess
import tempfile
from dataclasses import dataclass


@dataclass
class SyscallRecord:
    """Single syscall record from strace output."""

    name: str
    args: list[str]
    result: str | None = None
    duration: float | None = None  # microseconds if -T flag used


# Regex to parse strace output
# Example: write(1, "hello\n", 6) = 6
# Example with timing: write(1, "hello\n", 6) = 6 <0.000012>
STRACE_LINE_RE = re.compile(
    r"^(\w+)\((.*?)\)\s*=\s*(\S+)(?:\s+<([\d.]+)>)?",
    re.MULTILINE,
)


def is_strace_available() -> bool:
    """Check if strace is installed and accessible."""
    try:
        result = subprocess.run(
            ["strace", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def parse_strace_output(strace_output: str) -> list[SyscallRecord]:
    """Parse strace output into structured syscall records."""
    syscalls = []

    for match in STRACE_LINE_RE.finditer(strace_output):
        name = match.group(1)
        args_str = match.group(2)
        result = match.group(3)
        duration_str = match.group(4)

        # Parse args (simple split, doesn't handle nested parens perfectly)
        args = [a.strip() for a in args_str.split(",") if a.strip()]

        duration = float(duration_str) if duration_str else None

        syscalls.append(
            SyscallRecord(
                name=name,
                args=args,
                result=result,
                duration=duration,
            )
        )

    return syscalls


def run_with_strace(
    cmd: list[str],
    capture_output: bool = True,
    trace_filter: str | None = None,
    include_timing: bool = True,
) -> tuple[subprocess.CompletedProcess, list[SyscallRecord]]:
    """Run a command with strace and capture syscalls.

    Args:
        cmd: Command to execute
        capture_output: Capture stdout/stderr from the command
        trace_filter: Syscall filter (e.g. "write,read,open")
        include_timing: Include timing info (-T flag)

    Returns:
        Tuple of (subprocess result, list of syscall records)

    Raises:
        FileNotFoundError: If strace is not installed
    """
    if not is_strace_available():
        # Fall back to regular execution
        result = subprocess.run(cmd, capture_output=capture_output, text=True)
        return result, []

    # Create temp file for strace output
    with tempfile.NamedTemporaryFile(mode="w", suffix=".strace", delete=False) as f:
        strace_output_path = f.name

    try:
        # Build strace command
        strace_cmd = ["strace", "-o", strace_output_path]

        if include_timing:
            strace_cmd.append("-T")

        if trace_filter:
            strace_cmd.extend(["-e", f"trace={trace_filter}"])

        strace_cmd.extend(cmd)

        # Run with strace
        result = subprocess.run(
            strace_cmd,
            capture_output=capture_output,
            text=True,
        )

        # Parse strace output
        with open(strace_output_path) as f:
            strace_output = f.read()

        syscalls = parse_strace_output(strace_output)

        return result, syscalls

    finally:
        # Cleanup
        from contextlib import suppress

        with suppress(OSError):
            os.unlink(strace_output_path)


# Common syscall filters for different use cases
FILTER_IO = "read,write,open,close,openat"
FILTER_NETWORK = "socket,connect,bind,listen,accept,send,recv,sendto,recvfrom"
FILTER_PROCESS = "fork,vfork,clone,execve,exit,exit_group,wait4"
FILTER_MEMORY = "mmap,munmap,mprotect,brk"
FILTER_FILE = "open,openat,close,read,write,stat,fstat,lstat,access,unlink"
