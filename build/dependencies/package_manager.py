#!/usr/bin/env python3
"""
Simple Ubuntu Package Manager for Unhinged - KISS Approach

Usage:
    python3 package_manager.py install <package>
    python3 package_manager.py install-group <group>
    python3 package_manager.py list
"""

import os
import sys
import yaml
import subprocess
from pathlib import Path

# Add control/gtk4_gui/utils to path for subprocess_utils import
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "control" / "gtk4_gui" / "utils"))

from subprocess_utils import SubprocessRunner

class UbuntuPackageManager:
    def __init__(self):
        self.config_path = Path(__file__).parent / "dependencies.yaml"
        with open(self.config_path, 'r') as f:
            self.config = yaml.safe_load(f)

    def _run_command(self, command: str) -> bool:
        """Run shell command"""
        print(f"🔧 {command}")

        # Check if we need sudo for apt-get commands
        if command.startswith('apt-get'):
            # Try to run with sudo
            command = f"sudo {command}"
        elif command.startswith('build/python/venv/bin/pip'):
            # Handle Python venv pip commands - ensure venv exists first
            venv_path = Path("build/python/venv")
            if not venv_path.exists():
                print("⚠️ Python virtual environment not found. Setting up...")
                runner = SubprocessRunner(timeout=300)
                setup_result = runner.run_shell("cd build/python && python3 setup.py")
                if not setup_result["success"]:
                    print("❌ Failed to setup Python virtual environment")
                    return False

        runner = SubprocessRunner(timeout=300)
        result = runner.run_shell(command)

        if not result["success"]:
            print(f"❌ Command failed: {command}")
            return False
        else:
            print(f"✅ Command succeeded: {command}")
            return True

    def install_package(self, package_name: str) -> bool:
        """Install a package"""
        packages = self.config.get('packages', {})
        package_info = packages.get(package_name)

        if not package_info:
            print(f"❌ Package not found: {package_name}")
            return False

        if package_info.get('optional') and not self._confirm(f"Install optional package {package_name}?"):
            return True

        install_cmd = package_info.get('install')
        if not install_cmd:
            print(f"❌ No install command for {package_name}")
            return False

        return self._run_command(install_cmd)

    def install_group(self, group_name: str) -> bool:
        """Install a group of packages"""
        groups = self.config.get('groups', {})
        group_packages = groups.get(group_name)

        if not group_packages:
            print(f"❌ Group not found: {group_name}")
            return False

        print(f"📦 Installing group: {group_name}")
        success = True
        for package_name in group_packages:
            if not self.install_package(package_name):
                success = False

        return success

    def list_packages(self):
        """List available packages"""
        print("📦 Available Packages:")
        packages = self.config.get('packages', {})
        for name, info in packages.items():
            desc = info.get('description', '')
            optional = " (optional)" if info.get('optional') else ""
            print(f"  {name} - {desc}{optional}")

        print("\n📦 Groups:")
        groups = self.config.get('groups', {})
        for name, packages in groups.items():
            print(f"  {name} - {', '.join(packages)}")

    def _confirm(self, message: str) -> bool:
        """Ask user for confirmation"""
        response = input(f"{message} [y/N]: ").lower()
        return response in ['y', 'yes']

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 package_manager.py <command> [args]")
        print("Commands:")
        print("  install <package>        - Install a package")
        print("  install-group <group>    - Install a group")
        print("  list                     - List packages")
        sys.exit(1)

    pm = UbuntuPackageManager()
    command = sys.argv[1]

    if command == "install" and len(sys.argv) == 3:
        success = pm.install_package(sys.argv[2])
        sys.exit(0 if success else 1)

    elif command == "install-group" and len(sys.argv) == 3:
        success = pm.install_group(sys.argv[2])
        sys.exit(0 if success else 1)

    elif command == "list":
        pm.list_packages()

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
