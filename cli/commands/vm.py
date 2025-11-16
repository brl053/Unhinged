"""VM commands: vm win10, vm templeos, vm stop."""

import subprocess

import click

from cli.utils import log_info, log_warning


@click.group()
def vm():
    """Virtual machine commands."""
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
