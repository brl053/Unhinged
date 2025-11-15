"""System commands: start, stop, status, restart."""

import subprocess

import click

from control.cli.utils import (
    check_file_exists,
    get_python,
    log_info,
    log_success,
    log_warning,
    run_command,
)


@click.group()
def system():
    """System commands for Unhinged dual-system architecture."""
    pass


@system.command()
def start():
    """Start complete dual-system architecture."""
    log_info("Starting Unhinged system...")

    # Check preflight
    python_cmd = get_python()
    if not check_file_exists("build/preflight_check.py", "Preflight checker"):
        return 1

    log_info("Running preflight checks...")
    result = run_command([python_cmd, "build/preflight_check.py", "check"])
    if result != 0:
        log_warning("Preflight checks suggest restart")

    # Launch services
    log_info("🚀 Launching services...")
    if not check_file_exists("control/service_launcher.py", "Service launcher"):
        return 1

    result = run_command([python_cmd, "control/service_launcher.py", "--timeout", "120"])
    if result == 0:
        log_success("Essential services started")
    else:
        log_warning("Some services failed to start - continuing with available services")

    log_success("Unhinged system started")
    return 0


@system.command()
def stop():
    """Stop complete dual-system gracefully."""
    log_info("Stopping Unhinged system...")

    # Kill processes
    subprocess.run(["pkill", "-f", "python3.*desktop_app.py"], capture_output=True)
    subprocess.run(["pkill", "-f", "unhinged"], capture_output=True)

    log_success("Unhinged system stopped gracefully")
    return 0


@system.command()
def status():
    """Show system health and component status."""
    log_info("Checking Unhinged system status...")

    python_cmd = get_python()
    if not check_file_exists("control/service_launcher.py", "Service launcher"):
        return 1

    log_info("📊 Service Status:")
    run_command([python_cmd, "control/service_launcher.py", "--status"])

    log_info("🖥️  System Status:")
    run_command(["make", "status"])

    return 0


@system.command()
def restart():
    """Restart complete system (stop + start)."""
    log_info("Restarting Unhinged system...")
    stop()
    import time

    time.sleep(2)
    start()
    return 0
