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
    
    def launch_vm(self, disk_path):
        """Launch the QEMU VM"""
        print("🚀 Launching QEMU VM...")

        # Check if qemu is available
        try:
            subprocess.run(['which', 'qemu-system-x86_64'], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            print("⚠️  QEMU not installed - installing now...")
            if not self.install_qemu_packages():
                print("❌ Failed to install QEMU")
                return None

        cmd = [
            'qemu-system-x86_64',
            '-enable-kvm',
            '-m', self.vm_config['memory'],
            '-smp', str(self.vm_config['cpus']),
            '-drive', f'file={disk_path},format=qcow2',
            '-netdev', 'user,id=net0',
            '-device', 'virtio-net-pci,netdev=net0',
            '-vga', 'virtio',
            '-display', 'gtk',
            '-name', self.vm_config['name'],
            '-boot', 'menu=on'
        ]
        
        print(f"🎮 Executing: {' '.join(cmd)}")
        
        try:
            # Launch VM in background
            process = subprocess.Popen(cmd)
            print(f"✅ VM launched with PID: {process.pid}")
            print("💡 VM window should appear shortly")
            return process
        except Exception as e:
            print(f"❌ Error launching VM: {e}")
            return None
    
    def run(self, test_mode=False):
        """Main execution flow"""
        print("🔥 QEMU VM LAUNCHER - UNHINGED VIRTUALIZATION")
        print("=" * 50)

        # Check prerequisites
        if not self.check_virtualization_support():
            return False

        # In test mode, skip IOMMU requirement
        if not test_mode:
            # Check IOMMU
            if not self.check_iommu_enabled():
                if not self.enable_iommu():
                    return False
                print("⚠️  Please reboot and run again to complete IOMMU setup")
                return True
        else:
            print("🧪 TEST MODE: Skipping IOMMU requirement")

        # Install packages
        if not self.install_qemu_packages():
            return False

        # Create VM disk
        disk_path = self.create_vm_disk()
        if not disk_path:
            return False

        # Launch VM
        vm_process = self.launch_vm(disk_path)
        if not vm_process:
            return False

        print("🎉 QEMU VM setup complete!")
        print("💡 Install your OS in the VM window")
        return True

def main():
    import sys
    test_mode = '--test' in sys.argv
    launcher = QEMULauncher()
    success = launcher.run(test_mode=test_mode)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
