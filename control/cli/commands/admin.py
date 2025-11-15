"""Admin commands: admin, debug, preflight."""

import subprocess

import click

from control.cli.utils import (
    get_python,
    log_info,
)


@click.group()
def admin():
    """Admin and debug commands."""
    pass


@admin.group()
def services():
    """Service management commands."""
    pass


@services.command()
def list():
    """List all running services."""
    log_info("Listing services...")
    python_cmd = get_python()
    subprocess.run([python_cmd, "control/service_launcher.py", "--list"])


@services.command()
def health():
    """Health check all services."""
    log_info("Checking service health...")
    python_cmd = get_python()
    subprocess.run([python_cmd, "control/service_launcher.py", "--status"])


@admin.group()
def debug():
    """Debug commands."""
    pass


@debug.command()
def status():
    """Show detailed system state."""
    log_info("Showing detailed system state...")
    subprocess.run(["make", "status"])


@debug.command()
@click.argument("component", required=False, default="all")
def logs(component):
    """Show component-specific logs."""
    log_info(f"Showing logs for: {component}")
    subprocess.run(["make", "logs"])


@admin.group()
def preflight():
    """Preflight check commands."""
    pass


@preflight.command()
def check():
    """Run pre-flight checks for code changes."""
    log_info("Running preflight checks...")
    python_cmd = get_python()
    result = subprocess.run([python_cmd, "build/preflight_check.py", "check"])
    return result.returncode


@preflight.command()
def status_check():
    """Show detailed preflight status."""
    log_info("Showing preflight status...")
    python_cmd = get_python()
    subprocess.run([python_cmd, "build/preflight_check.py", "status"])


@preflight.command()
def clean():
    """Clean Python cache."""
    log_info("Cleaning Python cache...")
    python_cmd = get_python()
    subprocess.run([python_cmd, "build/preflight_check.py", "clean"])


@preflight.command()
def force_clean():
    """Force clean restart preparation."""
    log_info("Force cleaning...")
    python_cmd = get_python()
    subprocess.run([python_cmd, "build/preflight_check.py", "force-clean"])
