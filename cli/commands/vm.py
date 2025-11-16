"""VM commands: vm win10, vm templeos, vm stop, vm services."""

import subprocess
import sys

import click

from cli.utils import log_error, log_info, log_success, log_warning


@click.group()
def vm():
    """Virtual machine and container orchestration commands.

    Manages hypervisor-level infrastructure including VMs and Docker containers.
    """
    pass


@vm.command()
def win10():
    """Launch Windows 10 gaming VM (350GB)."""
    log_info("Launching Windows 10 VM...")
    log_warning("This requires 350GB disk space and significant resources")
    subprocess.run(["make", "vm-win10"])


@vm.command()
def templeos():
    """Launch TempleOS VM."""
    log_info("Launching TempleOS VM...")
    subprocess.run(["make", "vm-templeos"])


@vm.command()
def stop():
    """Stop running VM."""
    log_info("Stopping VM...")
    subprocess.run(["make", "vm-stop"])


@vm.group()
def services():
    """Container orchestration commands (Docker Compose).

    Manages containerized services: LLM (Ollama), Vision AI, Speech-to-Text, etc.
    """
    pass


@services.command()
@click.option(
    "-s",
    "--service",
    multiple=True,
    help="Specific service(s) to start (e.g., llm, vision-ai, speech-to-text)",
)
def up(service):
    """Start container services.

    Examples:
      unhinged vm services up              # Start all services
      unhinged vm services up -s llm       # Start only LLM service
      unhinged vm services up -s llm -s vision-ai  # Start multiple services
    """
    try:
        if service:
            log_info(f"Starting services: {', '.join(service)}")
            cmd = [
                "docker",
                "compose",
                "-f",
                "build/orchestration/docker-compose.production.yml",
                "up",
                "-d",
            ] + list(service)
        else:
            log_info("Starting all container services...")
            cmd = [
                "docker",
                "compose",
                "-f",
                "build/orchestration/docker-compose.production.yml",
                "up",
                "-d",
            ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            log_success("Container services started successfully")
            if not service:
                log_info("Services: LLM (Ollama), Vision AI, Speech-to-Text, Redis, Persistence")
        else:
            log_error(f"Failed to start services: {result.stderr}")
            sys.exit(1)

    except Exception as e:
        log_error(f"Error starting services: {e}")
        sys.exit(1)


@services.command()
@click.option(
    "-s",
    "--service",
    multiple=True,
    help="Specific service(s) to stop",
)
def down(service):
    """Stop container services.

    Examples:
      unhinged vm services down            # Stop all services
      unhinged vm services down -s llm     # Stop only LLM service
    """
    try:
        if service:
            log_info(f"Stopping services: {', '.join(service)}")
            cmd = [
                "docker",
                "compose",
                "-f",
                "build/orchestration/docker-compose.production.yml",
                "down",
            ] + list(service)
        else:
            log_warning("Stopping all container services...")
            cmd = [
                "docker",
                "compose",
                "-f",
                "build/orchestration/docker-compose.production.yml",
                "down",
            ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            log_success("Container services stopped")
        else:
            log_error(f"Failed to stop services: {result.stderr}")
            sys.exit(1)

    except Exception as e:
        log_error(f"Error stopping services: {e}")
        sys.exit(1)


@services.command()
def status():
    """Show status of container services."""
    try:
        log_info("Checking container service status...")
        result = subprocess.run(
            ["docker", "compose", "-f", "build/orchestration/docker-compose.production.yml", "ps"],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            print(result.stdout)
        else:
            log_error(f"Failed to get service status: {result.stderr}")
            sys.exit(1)

    except Exception as e:
        log_error(f"Error checking service status: {e}")
        sys.exit(1)
