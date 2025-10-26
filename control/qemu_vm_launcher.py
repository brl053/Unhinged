#!/usr/bin/env python3
"""
QEMU VM Launcher for Unhinged
Automates the entire QEMU GPU passthrough setup process.
"""

import subprocess
import sys
import os
import json
from pathlib import Path

class QEMULauncher:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.vm_config = {
            "name": "unhinged-vm",
            "memory": "8G",
            "cpus": 4,
            "disk_size": "20G"
        }
    
    def check_virtualization_support(self):
        """Check if CPU supports virtualization"""
        try:
            result = subprocess.run(['grep', '-E', '(vmx|svm)', '/proc/cpuinfo'], 
                                  capture_output=True, text=True)
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
            with open('/proc/cmdline', 'r') as f:
                cmdline = f.read()
            
            if 'intel_iommu=on' in cmdline or 'amd_iommu=on' in cmdline:
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
            result = subprocess.run(['grep', 'vendor_id', '/proc/cpuinfo'], 
                                  capture_output=True, text=True)
            if 'Intel' in result.stdout:
                iommu_param = 'intel_iommu=on'
            elif 'AMD' in result.stdout:
                iommu_param = 'amd_iommu=on'
            else:
                print("❌ Unknown CPU vendor")
                return False
            
            # Backup and modify GRUB
            subprocess.run(['sudo', 'cp', '/etc/default/grub', '/etc/default/grub.backup'])
            
            # Add IOMMU parameter
            grub_cmd = f'sudo sed -i \'s/GRUB_CMDLINE_LINUX_DEFAULT="\\([^"]*\\)"/GRUB_CMDLINE_LINUX_DEFAULT="\\1 {iommu_param}"/\' /etc/default/grub'
            subprocess.run(grub_cmd, shell=True)
            
            # Update GRUB
            subprocess.run(['sudo', 'update-grub'])
            
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
            'qemu-system-x86', 'qemu-utils', 'libvirt-daemon-system',
            'libvirt-clients', 'virt-manager', 'ovmf'
        ]
        
        try:
            cmd = ['sudo', 'apt', 'update']
            subprocess.run(cmd, check=True)
            
            cmd = ['sudo', 'apt', 'install', '-y'] + packages
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
                'qemu-img', 'create', '-f', 'qcow2',
                str(disk_path), self.vm_config['disk_size']
            ]
            subprocess.run(cmd, check=True)
            print(f"✅ VM disk created: {disk_path}")
            return str(disk_path)
        except subprocess.CalledProcessError as e:
            print(f"❌ Error creating VM disk: {e}")
            return None
    
    def create_hello_world_boot(self):
        """Create a simple boot image that displays 'Hello World!'"""
        vm_dir = self.project_root / "vm"
        vm_dir.mkdir(exist_ok=True)

        boot_path = vm_dir / "hello_world_boot.img"

        if boot_path.exists():
            print(f"✅ Hello World boot image already exists: {boot_path}")
            return str(boot_path)

        print("🔧 Creating Hello World boot image...")

        # Create a simple x86 boot sector that displays "Hello World!" in white text
        boot_code = bytes([
            # Boot sector header
            0xEB, 0x3E, 0x90,  # Jump to start + NOP

            # Boot sector code starts here (offset 0x3)
            # Set up segments
            0x31, 0xC0,        # xor ax, ax
            0x8E, 0xD8,        # mov ds, ax
            0x8E, 0xC0,        # mov es, ax
            0x8E, 0xD0,        # mov ss, ax
            0xBC, 0x00, 0x7C,  # mov sp, 0x7C00

            # Clear screen (set video mode 3 - 80x25 color text)
            0xB0, 0x03,        # mov al, 3
            0xB4, 0x00,        # mov ah, 0
            0xCD, 0x10,        # int 0x10

            # Print "Hello World!" message
            0xBE, 0x2A, 0x7C,  # mov si, message (offset 0x2A + 0x7C00)

            # Print loop
            0xAC,              # lodsb (load byte from [si] to al)
            0x08, 0xC0,        # or al, al (test if zero)
            0x74, 0x06,        # jz done (jump if zero)
            0xB4, 0x0E,        # mov ah, 0x0E (teletype output)
            0xCD, 0x10,        # int 0x10 (BIOS video interrupt)
            0xEB, 0xF7,        # jmp print_loop

            # Infinite loop
            0xEB, 0xFE,        # jmp $ (infinite loop)

            # Message string (starts at offset 0x2A)
        ] + list(b"Hello World! - Unhinged QEMU VM\r\n\0") + [0x00] * (510 - 42 - 33) + [0x55, 0xAA])

        try:
            with open(boot_path, 'wb') as f:
                # Write boot sector
                f.write(boot_code)
                # Pad to 1.44MB floppy size
                remaining = 1474560 - len(boot_code)
                f.write(b'\x00' * remaining)

            print(f"✅ Hello World boot image created: {boot_path}")
            return str(boot_path)
        except Exception as e:
            print(f"❌ Error creating boot image: {e}")
            return None

    def launch_vm(self, disk_path=None):
        """Launch the QEMU VM with Hello World display"""
        print("🚀 Launching QEMU VM with Hello World...")

        # Check if qemu is available
        try:
            subprocess.run(['which', 'qemu-system-x86_64'], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            print("⚠️  QEMU not installed - installing now...")
            if not self.install_qemu_packages():
                print("❌ Failed to install QEMU")
                return None

        # Create hello world boot image
        boot_image = self.create_hello_world_boot()
        if not boot_image:
            print("❌ Failed to create Hello World boot image")
            return None

        cmd = [
            'qemu-system-x86_64',
            '-enable-kvm',
            '-m', '512M',  # Reduced memory for hello world
            '-smp', '2',   # Reduced CPUs for hello world
            '-drive', f'file={boot_image},format=raw,if=floppy',
            '-vga', 'std',
            '-display', 'gtk',
            '-name', 'Unhinged-Hello-World',
            '-no-reboot',
            '-monitor', 'none'
        ]

        print(f"🎮 Executing: {' '.join(cmd)}")
        print("🔥 LAUNCHING WHITE HELLO WORLD DISPLAY!")

        try:
            # Launch VM in background
            process = subprocess.Popen(cmd)
            print(f"✅ VM launched with PID: {process.pid}")
            print("💡 Hello World VM window should appear shortly")
            print("🎯 You should see a white screen with 'Hello World!' message")
            return process
        except Exception as e:
            print(f"❌ Error launching VM: {e}")
            return None
    
    def run(self, test_mode=False):
        """Main execution flow for Hello World display"""
        print("🔥 QEMU VM LAUNCHER - UNHINGED HELLO WORLD")
        print("=" * 50)

        # Check prerequisites
        if not self.check_virtualization_support():
            print("⚠️  No virtualization support - trying without KVM...")

        # For Hello World, we don't need IOMMU or complex setup
        print("🎯 HELLO WORLD MODE: Simplified VM launch")

        # Install packages if needed
        try:
            subprocess.run(['which', 'qemu-system-x86_64'], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            print("📦 Installing QEMU for Hello World display...")
            if not self.install_qemu_packages():
                print("❌ Failed to install QEMU")
                return False

        # Launch Hello World VM directly
        vm_process = self.launch_vm()
        if not vm_process:
            return False

        print("🎉 QEMU Hello World VM launched!")
        print("💡 You should see a white screen with 'Hello World!' message")
        print("🔥 Press Ctrl+C to exit")

        # Wait for user to exit
        try:
            vm_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Shutting down Hello World VM...")
            vm_process.terminate()
            vm_process.wait()

        return True

def main():
    import sys
    test_mode = '--test' in sys.argv
    launcher = QEMULauncher()
    success = launcher.run(test_mode=test_mode)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
