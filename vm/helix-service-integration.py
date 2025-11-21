#!/usr/bin/env python3
"""
HELIX Windows 11 BF6 VM - Unhinged Service Integration
Add this to control/service_launcher.py to integrate Windows VM with Unhinged
"""

# Add to self.services dictionary in ServiceLauncher class:

HELIX_SERVICE_CONFIG = {
    "windows_bf6_vm": {
        "order": 1.5,  # After Alpine VM (1.0), before other services
        "command": [
            "qemu-system-x86_64",
            "-name",
            "helix-bf6-vm",
            "-machine",
            "type=pc,accel=kvm,kernel-irqchip=on",
            "-cpu",
            "host,+invtsc,+tsc",
            "-smp",
            "cores=8,threads=2,sockets=1",
            "-m",
            "16G",
            "-device",
            "iommu,intremap=on,caching-mode=on",
            "-device",
            "vfio-pci,host=01:00.0",  # NVIDIA RTX 4090
            "-drive",
            "file=/home/e-bliss-station-1/Projects/Unhinged/vm/bf6-w11-gaming.qcow2,if=virtio,format=qcow2,cache=writeback",
            "-netdev",
            "user,id=net0",
            "-device",
            "e1000,netdev=net0",
            "-bios",
            "/usr/share/edk2/x64/OVMF_CODE.fd",
            "-enable-kvm",
            "-display",
            "gtk,gl=on",
        ],
        "description": "Windows 11 BF6 Gaming VM (HELIX)",
        "required": False,  # Optional service
        "background": True,
        "health_check": "check_helix_vm_health",
        "timeout": 30,
    }
}

# Add health check method to ServiceLauncher class:


def check_helix_vm_health(self):
    """
    Check Windows 11 BF6 VM health
    Returns: (status: bool, message: str)
    """
    import subprocess

    try:
        # Check if QEMU process is running
        result = subprocess.run(["pgrep", "-f", "helix-bf6-vm"], capture_output=True, timeout=5)

        if result.returncode == 0:
            # Process found
            return (True, "HELIX VM running")
        else:
            return (False, "HELIX VM not running")

    except Exception as e:
        return (False, f"HELIX VM health check failed: {str(e)}")


# Integration instructions:
# 1. Copy HELIX_SERVICE_CONFIG to self.services in ServiceLauncher.__init__
# 2. Add check_helix_vm_health method to ServiceLauncher class
# 3. Update service_launcher.py to handle GPU passthrough requirements
# 4. Test with: python3 control/service_launcher.py start windows_bf6_vm

# GPU Passthrough Setup (run once on host):
GPU_PASSTHROUGH_SETUP = """
#!/bin/bash
# Run as root to enable GPU passthrough for HELIX VM

GPU_PCI="01:00.0"
GPU_VENDOR_ID="10de"  # NVIDIA
GPU_DEVICE_ID="2c05"  # RTX 4090

echo "Setting up GPU passthrough for HELIX VM..."

# 1. Unbind GPU from nvidia driver
echo "Unbinding GPU from nvidia driver..."
echo "$GPU_PCI" > /sys/bus/pci/drivers/nvidia/unbind 2>/dev/null || true

# 2. Bind GPU to vfio-pci
echo "Binding GPU to vfio-pci..."
echo "$GPU_VENDOR_ID:$GPU_DEVICE_ID" > /sys/bus/pci/drivers/vfio-pci/new_id

# 3. Verify binding
DRIVER=$(readlink /sys/bus/pci/devices/0000:$GPU_PCI/driver | xargs basename)
echo "GPU driver: $DRIVER"

if [ "$DRIVER" = "vfio-pci" ]; then
    echo "✓ GPU passthrough ready"
else
    echo "✗ GPU passthrough setup failed"
    exit 1
fi
"""

# Usage:
# 1. Save GPU_PASSTHROUGH_SETUP to /tmp/setup-gpu-passthrough.sh
# 2. Run: sudo bash /tmp/setup-gpu-passthrough.sh
# 3. Then start HELIX VM: python3 control/service_launcher.py start windows_bf6_vm

print(__doc__)
