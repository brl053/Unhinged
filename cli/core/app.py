"""Unhinged CLI - Main application entry point.

Consolidated from control/cli/main.py for unified CLI interface.
"""

import os
import subprocess

import click

from cli.commands import admin, dev, system, vm
from cli.utils import get_python, log_info


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx: click.Context) -> None:
    """Unhinged - Native Graphics Platform with Dual-System Architecture.

    Normal usage: unhinged [COMMAND] [OPTIONS]
    Default: unhinged start (start complete system and launch GUI)
    """
    # If no command provided, start the complete system with GUI
    if ctx.invoked_subcommand is None:
        log_info("🚀 Starting Unhinged complete system...")
        python_cmd = get_python()

        # Start services
        result = subprocess.run([python_cmd, "control/service_launcher.py", "--timeout", "120"])
        if result.returncode != 0:
            log_info("⚠️  Some services failed to start - continuing with available services")

        # Initialize session before launching GUI
        log_info("📋 Initializing chat session...")
        from control.service_launcher import ServiceLauncher

        launcher = ServiceLauncher()
        session_id = launcher.initialize_session(timeout=30)

        if session_id:
            log_info(f"✅ Session initialized: {session_id}")
            # Pass session_id to GUI via environment variable
            os.environ["UNHINGED_SESSION_ID"] = session_id
        else:
            log_info("⚠️  Session initialization failed - GUI will create session on startup")

        log_info("📺 Launching GUI...")
        subprocess.run([python_cmd, "control/gtk4_gui/launch.py"])


# Add command groups
cli.add_command(system)
cli.add_command(dev)
cli.add_command(admin)
cli.add_command(vm)


if __name__ == "__main__":
    cli()
