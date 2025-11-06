#!/bin/bash
# HELIX BF6 Windows 11 VM Launcher
# GPU Passthrough: NVIDIA RTX 4090 (01:00.0)
# Configuration: 8 cores, 16GB RAM, GPU passthrough

set -e

VM_NAME="helix-bf6-vm"
VM_DISK="/home/e-bliss-station-1/Projects/Unhinged/vm/bf6-w11-gaming.qcow2"
ISO_PATH="${1:-/tmp/Windows11.iso}"  # Pass ISO path as argument
GPU_PCI="01:00.0"

echo "=== HELIX BF6 VM Launcher ==="
echo "VM Name: $VM_NAME"
echo "Disk: $VM_DISK"
echo "GPU: NVIDIA RTX 4090 ($GPU_PCI)"
echo "CPU: 8 cores, 16GB RAM"
echo ""

# Check if disk exists
if [ ! -f "$VM_DISK" ]; then
    echo "ERROR: VM disk not found at $VM_DISK"
    exit 1
fi

# Check if ISO provided
if [ ! -f "$ISO_PATH" ]; then
    echo "WARNING: ISO not found at $ISO_PATH"
    echo "Usage: $0 /path/to/Windows11.iso"
    echo "Proceeding without ISO (boot from existing disk)"
fi

# Unbind GPU from host drivers (if needed)
echo "Checking GPU binding..."
if [ -d "/sys/bus/pci/devices/0000:${GPU_PCI}" ]; then
    DRIVER=$(readlink /sys/bus/pci/devices/0000:${GPU_PCI}/driver 2>/dev/null | xargs basename 2>/dev/null || echo "none")
    echo "Current GPU driver: $DRIVER"
    
    if [ "$DRIVER" != "vfio-pci" ]; then
        echo "GPU needs to be bound to vfio-pci for passthrough"
        echo "Run as root: echo 0000:${GPU_PCI} > /sys/bus/pci/drivers/nvidia/unbind"
        echo "Then: echo 10de:2c05 > /sys/bus/pci/drivers/vfio-pci/new_id"
    fi
fi

# Launch QEMU with GPU passthrough
echo "Launching QEMU..."

if [ -f "$ISO_PATH" ]; then
    # Boot from ISO (installation)
    # Using EPYC CPU model for better Windows 11 compatibility on AMD
    qemu-system-x86_64 \
        -name "$VM_NAME" \
        -machine type=pc,accel=kvm,kernel-irqchip=on \
        -cpu EPYC-v4,+invtsc,+tsc \
        -smp cores=8,threads=1,sockets=1 \
        -m 16G \
        -device qxl-vga,vram_size_mb=256 \
        -drive file="$VM_DISK",if=virtio,format=qcow2,cache=writeback \
        -drive file="$ISO_PATH",media=cdrom,index=0 \
        -netdev user,id=net0 -device e1000,netdev=net0 \
        -bios /usr/share/ovmf/OVMF.fd \
        -enable-kvm \
        -display gtk,gl=on \
        -boot d \
        -monitor stdio
else
    # Boot from existing disk
    # Using EPYC CPU model for better Windows 11 compatibility on AMD
    qemu-system-x86_64 \
        -name "$VM_NAME" \
        -machine type=pc,accel=kvm,kernel-irqchip=on \
        -cpu EPYC-v4,+invtsc,+tsc \
        -smp cores=8,threads=1,sockets=1 \
        -m 16G \
        -device qxl-vga,vram_size_mb=256 \
        -drive file="$VM_DISK",if=virtio,format=qcow2,cache=writeback \
        -netdev user,id=net0 -device e1000,netdev=net0 \
        -bios /usr/share/ovmf/OVMF.fd \
        -enable-kvm \
        -display gtk,gl=on \
        -monitor stdio
fi

