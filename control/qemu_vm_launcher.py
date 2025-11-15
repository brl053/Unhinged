#!/usr/bin/env python3
"""
QEMU VM Launcher for Unhinged
Automates the entire QEMU GPU passthrough setup process.
"""

import subprocess
import sys
from pathlib import Path


class QEMULauncher:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.vm_config = {
            "name": "unhinged-vm",
            "memory": "8G",
            "cpus": 4,
            "disk_size": "20G",
        }

    def check_virtualization_support(self):
        """Check if CPU supports virtualization"""
        try:
            result = subprocess.run(
                ["grep", "-E", "(vmx|svm)", "/proc/cpuinfo"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                print("✅ CPU virtualization support detected")
                return True
            else:
                print("❌ CPU virtualization not supported")
                return False
        except Exception as e:
            print(f"❌ Error checking virtualization: {e}")
            return False

    def check_iommu_enabled(self):
        """Check if IOMMU is enabled"""
        try:
            with open("/proc/cmdline") as f:
                cmdline = f.read()

            if "intel_iommu=on" in cmdline or "amd_iommu=on" in cmdline:
                print("✅ IOMMU enabled in kernel")
                return True
            else:
                print("⚠️  IOMMU not enabled - will enable automatically")
                return False
        except Exception as e:
            print(f"❌ Error checking IOMMU: {e}")
            return False

    def enable_iommu(self):
        """Automatically enable IOMMU by modifying GRUB"""
        print("🔧 Enabling IOMMU in GRUB configuration...")

        # Detect CPU vendor
        try:
            result = subprocess.run(
                ["grep", "vendor_id", "/proc/cpuinfo"], capture_output=True, text=True
            )
            if "Intel" in result.stdout:
                iommu_param = "intel_iommu=on"
            elif "AMD" in result.stdout:
                iommu_param = "amd_iommu=on"
            else:
                print("❌ Unknown CPU vendor")
                return False

            # Backup and modify GRUB
            subprocess.run(["sudo", "cp", "/etc/default/grub", "/etc/default/grub.backup"])

            # Add IOMMU parameter
            grub_cmd = f'sudo sed -i \'s/GRUB_CMDLINE_LINUX_DEFAULT="\\([^"]*\\)"/GRUB_CMDLINE_LINUX_DEFAULT="\\1 {iommu_param}"/\' /etc/default/grub'
            subprocess.run(grub_cmd, shell=True)

            # Update GRUB
            subprocess.run(["sudo", "update-grub"])

            print(f"✅ IOMMU enabled with {iommu_param}")
            print("⚠️  Reboot required for changes to take effect")
            return True

        except Exception as e:
            print(f"❌ Error enabling IOMMU: {e}")
            return False

    def install_qemu_packages(self):
        """Install required QEMU packages"""
        print("📦 Installing QEMU packages...")
        packages = [
            "qemu-system-x86",
            "qemu-utils",
            "libvirt-daemon-system",
            "libvirt-clients",
            "virt-manager",
            "ovmf",
        ]

        try:
            cmd = ["sudo", "apt", "update"]
            subprocess.run(cmd, check=True)

            cmd = ["sudo", "apt", "install", "-y"] + packages
            subprocess.run(cmd, check=True)

            print("✅ QEMU packages installed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error installing packages: {e}")
            return False

    def create_vm_disk(self):
        """Create VM disk image"""
        vm_dir = self.project_root / "vm"
        vm_dir.mkdir(exist_ok=True)

        disk_path = vm_dir / f"{self.vm_config['name']}.qcow2"

        if disk_path.exists():
            print(f"✅ VM disk already exists: {disk_path}")
            return str(disk_path)

        print(f"🔧 Creating VM disk: {disk_path}")
        try:
            cmd = [
                "qemu-img",
                "create",
                "-f",
                "qcow2",
                str(disk_path),
                self.vm_config["disk_size"],
            ]
            subprocess.run(cmd, check=True)
            print(f"✅ VM disk created: {disk_path}")
            return str(disk_path)
        except subprocess.CalledProcessError as e:
            print(f"❌ Error creating VM disk: {e}")
            return None

    def create_alpine_vm_disk(self):
        """Create Alpine Linux VM disk image"""
        vm_dir = self.project_root / "vm"
        vm_dir.mkdir(exist_ok=True)

        disk_path = vm_dir / "alpine-unhinged.qcow2"

        if disk_path.exists():
            print(f"✅ Alpine VM disk already exists: {disk_path}")
            return str(disk_path)

        print("🔧 Creating Alpine Linux VM disk (8GB)...")

        try:
            # Create 8GB qcow2 disk for Alpine Linux
            subprocess.run(
                ["qemu-img", "create", "-f", "qcow2", str(disk_path), "8G"],
                check=True,
                capture_output=True,
            )

            print(f"✅ Alpine VM disk created: {disk_path}")
            return str(disk_path)
        except subprocess.CalledProcessError as e:
            print(f"❌ Error creating VM disk: {e}")
            return None
        except FileNotFoundError:
            print("❌ qemu-img not found - installing QEMU tools...")
            if self.install_qemu_packages():
                return self.create_alpine_vm_disk()  # Retry
            return None

    def get_alpine_iso_path(self):
        """Get path to Alpine Linux ISO"""
        iso_path = self.project_root / "vm" / "alpine" / "alpine-virt-3.22.2-x86_64.iso"

        if iso_path.exists():
            return str(iso_path)
        else:
            print(f"❌ Alpine ISO not found at: {iso_path}")
            print("💡 Run the download task first")
            return None

    def launch_alpine_installation(self, disk_path, iso_path):
        """Launch Alpine Linux installation"""
        print("🏔️ Launching Alpine Linux installation...")

        cmd = [
            "qemu-system-x86_64",
            "-enable-kvm",
            "-m",
            "1G",  # 1GB RAM for installation
            "-smp",
            "2",  # 2 CPUs
            "-drive",
            f"file={disk_path},format=qcow2",
            "-cdrom",
            iso_path,
            "-boot",
            "d",  # Boot from CD-ROM first
            "-vga",
            "virtio",
            "-display",
            "gtk",
            "-name",
            "Alpine-Unhinged-Installation",
            "-netdev",
            "user,id=net0",
            "-device",
            "virtio-net-pci,netdev=net0",
        ]

        print(f"🎮 Executing: {' '.join(cmd)}")
        print("🔥 LAUNCHING ALPINE LINUX INSTALLATION!")
        print("")
        print("📋 INSTALLATION INSTRUCTIONS:")
        print("1. Wait for Alpine to boot to login prompt")
        print("2. Login as 'root' (no password)")
        print("3. Run: setup-alpine")
        print("4. Follow prompts - choose defaults for most options")
        print("5. When asked for disk, choose 'sda' and 'sys' mode")
        print("6. After installation, shutdown VM")
        print("7. Restart without CD-ROM to boot installed system")
        print("")

        try:
            # Launch VM in foreground for installation
            process = subprocess.Popen(cmd)
            print(f"✅ Alpine installation VM launched with PID: {process.pid}")
            print("💡 Alpine installation window should appear shortly")
            return process
        except Exception as e:
            print(f"❌ Error launching Alpine installation: {e}")
            return None

    def launch_custom_alpine_iso(self):
        """Launch custom Alpine ISO with Unhinged pre-installed"""
        custom_iso_path = self.project_root / "vm" / "alpine-unhinged-custom.iso"

        if not custom_iso_path.exists():
            print(f"❌ Custom Alpine ISO not found: {custom_iso_path}")
            print("💡 Build it first with: ./vm/build-custom-alpine.sh")
            return None

        # Create shared directory for VM-host communication
        shared_dir = self.project_root / "vm" / "shared"
        shared_dir.mkdir(exist_ok=True)

        # Create communication files
        (shared_dir / "host-to-vm.txt").touch()
        (shared_dir / "vm-to-host.txt").touch()

        # Create serial log file
        serial_log = self.project_root / "vm" / "alpine-serial.log"

        print("🎨 Launching Custom Alpine ISO with Unhinged...")
        print(f"📁 Shared directory: {shared_dir}")
        print(f"📋 Serial log: {serial_log}")

        cmd = [
            "qemu-system-x86_64",
            "-enable-kvm",
            "-m",
            "2G",  # 2GB RAM for better performance
            "-smp",
            "2",  # 2 CPUs
            "-cdrom",
            str(custom_iso_path),
            "-vga",
            "virtio",
            "-display",
            "gtk",
            "-name",
            "Unhinged-Custom-Alpine",
            # Communication channels
            "-netdev",
            "user,id=net0,hostfwd=tcp::2222-:22",  # SSH forwarding
            "-device",
            "virtio-net-pci,netdev=net0",
            # Shared directory (9p filesystem)
            "-fsdev",
            f"local,security_model=passthrough,id=fsdev0,path={shared_dir}",
            "-device",
            "virtio-9p-pci,id=fs0,fsdev=fsdev0,mount_tag=shared",
            # Serial console for logging
            "-serial",
            f"file:{serial_log}",
            # Monitor console for control
            "-monitor",
            "stdio",
            "-boot",
            "d",  # Boot from CD-ROM
        ]

        print(f"🎮 Executing: {' '.join(cmd)}")
        print("🔥 LAUNCHING CUSTOM ALPINE ISO WITH UNHINGED!")

        try:
            # Launch VM in background
            process = subprocess.Popen(cmd)
            print(f"✅ Custom Alpine ISO launched with PID: {process.pid}")
            print("💡 Unhinged GUI should appear automatically")
            print("🌐 Communication channels:")
            print("   • SSH: localhost:2222")
            print(f"   • Shared dir: {shared_dir}")
            print(f"   • Serial log: {serial_log}")
            print("📋 Monitor console available in terminal")
            return process
        except Exception as e:
            print(f"❌ Error launching custom Alpine ISO: {e}")
            return None

    def launch_alpine_vm(self, disk_path):
        """Launch installed Alpine Linux VM"""
        print("🏔️ Launching Alpine Linux VM...")

        cmd = [
            "qemu-system-x86_64",
            "-enable-kvm",
            "-m",
            "1G",  # 1GB RAM
            "-smp",
            "2",  # 2 CPUs
            "-drive",
            f"file={disk_path},format=qcow2",
            "-vga",
            "virtio",
            "-display",
            "gtk",
            "-name",
            "Alpine-Unhinged-Runtime",
            "-netdev",
            "user,id=net0,hostfwd=tcp::2222-:22",  # SSH forwarding
            "-device",
            "virtio-net-pci,netdev=net0",
        ]

        print(f"🎮 Executing: {' '.join(cmd)}")
        print("🔥 LAUNCHING ALPINE LINUX FOR UNHINGED!")

        try:
            # Launch VM in background
            process = subprocess.Popen(cmd)
            print(f"✅ Alpine VM launched with PID: {process.pid}")
            print("💡 Alpine VM window should appear shortly")
            print("🌐 SSH available on localhost:2222")
            return process
        except Exception as e:
            print(f"❌ Error launching Alpine VM: {e}")
            return None

    def run(self, install_mode=False, custom_iso=False):
        """Main execution flow for Alpine Linux VM"""
        print("🔥 QEMU VM LAUNCHER - ALPINE LINUX FOR UNHINGED")
        print("=" * 60)

        # Check prerequisites
        if not self.check_virtualization_support():
            print("⚠️  No virtualization support - trying without KVM...")

        # Install QEMU packages if needed
        try:
            subprocess.run(["which", "qemu-system-x86_64"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            print("📦 Installing QEMU for Alpine Linux...")
            if not self.install_qemu_packages():
                print("❌ Failed to install QEMU")
                return False

        # Custom ISO mode - boot directly from custom ISO
        if custom_iso:
            print("🎨 CUSTOM ALPINE ISO MODE")
            vm_process = self.launch_custom_alpine_iso()

            if vm_process:
                print("🎉 Custom Alpine ISO launched!")
                print("💡 Unhinged GUI should appear automatically")
                print("🔥 Press Ctrl+C to exit")

                try:
                    vm_process.wait()
                except KeyboardInterrupt:
                    print("\n🛑 Shutting down Alpine VM...")
                    vm_process.terminate()
                    vm_process.wait()

            return vm_process is not None

        # Legacy modes (kept for compatibility)
        # Create VM disk
        disk_path = self.create_alpine_vm_disk()
        if not disk_path:
            return False

        # Check if we need to install Alpine or run existing installation
        if install_mode:
            # Installation mode - boot from ISO
            iso_path = self.get_alpine_iso_path()
            if not iso_path:
                return False

            print("🏔️ ALPINE INSTALLATION MODE")
            vm_process = self.launch_alpine_installation(disk_path, iso_path)

            if vm_process:
                print("⏳ Waiting for Alpine installation to complete...")
                print("💡 Close the VM window when installation is finished")
                try:
                    vm_process.wait()
                    print("✅ Alpine installation completed!")
                    print("🔄 Run again without --install to boot Alpine")
                except KeyboardInterrupt:
                    print("\n🛑 Installation interrupted...")
                    vm_process.terminate()
                    vm_process.wait()
        else:
            # Runtime mode - boot from disk
            print("🏔️ ALPINE RUNTIME MODE")
            vm_process = self.launch_alpine_vm(disk_path)

            if vm_process:
                print("🎉 Alpine Linux VM launched!")
                print("💡 Alpine VM window should appear shortly")
                print("🔥 Press Ctrl+C to exit")

                try:
                    vm_process.wait()
                except KeyboardInterrupt:
                    print("\n🛑 Shutting down Alpine VM...")
                    vm_process.terminate()
                    vm_process.wait()

        return vm_process is not None


def main():
    import argparse

    parser = argparse.ArgumentParser(description="QEMU VM Launcher for Unhinged Alpine Linux")
    parser.add_argument("--install", action="store_true", help="Launch Alpine installation mode")
    parser.add_argument(
        "--custom-iso",
        action="store_true",
        help="Launch custom Alpine ISO with Unhinged pre-installed",
    )
    parser.add_argument("--test", action="store_true", help="Test mode (deprecated)")

    args = parser.parse_args()

    launcher = QEMULauncher()
    success = launcher.run(install_mode=args.install, custom_iso=args.custom_iso)

    if success:
        print("🎉 QEMU VM operation completed successfully!")
    else:
        print("❌ QEMU VM operation failed")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
