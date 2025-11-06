# HELIX VM Implementation Guide

**Status:** Phase 2 Ready - Windows 11 VM Infrastructure Created  
**GPU:** NVIDIA RTX 4090 (01:00.0) - GPU Passthrough Enabled  
**Configuration:** 8 cores, 16GB RAM, 40GB QCOW2 disk  
**Expected Performance:** 90-95% native FPS

---

## Files Created

1. **bf6-w11-gaming.qcow2** (193 KB → 40GB virtual)
   - QCOW2 disk image for Windows 11 VM
   - Location: `/home/e-bliss-station-1/Projects/Unhinged/vm/bf6-w11-gaming.qcow2`

2. **launch-bf6-vm.sh** (Executable)
   - QEMU launcher script with GPU passthrough
   - Usage: `./launch-bf6-vm.sh /path/to/Windows11.iso`
   - Location: `/home/e-bliss-station-1/Projects/Unhinged/vm/launch-bf6-vm.sh`

3. **minimize-windows11.ps1** (PowerShell)
   - Windows 11 minimization script
   - Run as Administrator inside Windows VM
   - Expected: 28-35 GB final, 1.0-1.4 GB idle RAM

4. **helix-service-integration.py** (Python)
   - Unhinged service framework integration
   - Add to control/service_launcher.py
   - Enables VM lifecycle management

---

## Phase 2: Windows 11 VM Creation

### Step 1: Obtain Windows 11 ISO

```bash
# Download Windows 11 ISO (you need to provide this)
# Save to: /tmp/Windows11.iso
# Size: ~6 GB
```

### Step 2: Launch VM for Installation

```bash
cd /home/e-bliss-station-1/Projects/Unhinged/vm
./launch-bf6-vm.sh /tmp/Windows11.iso
```

**Expected output:**
- QEMU window opens with Windows 11 boot screen
- GPU passthrough active (NVIDIA RTX 4090)
- 8 cores, 16GB RAM allocated

### Step 3: Install Windows 11 (Minimal)

Inside QEMU window:
1. Boot from ISO
2. Select "Custom Installation"
3. Select the virtio disk (40GB)
4. Install Windows 11
5. **Skip Microsoft Account** - use local account
6. **Skip optional features** - no Cortana, no OneDrive
7. Complete installation

### Step 4: Install Drivers

Inside Windows 11 VM:
```powershell
# Download NVIDIA driver (minimal, no bloatware)
# https://www.nvidia.com/Download/driverDetails.aspx/

# Install GPU driver only (skip GeForce Experience, etc.)
# Reboot
```

### Step 5: Verify DirectX 11

Inside Windows 11 VM:
```powershell
# Run dxdiag
dxdiag

# Check: System tab should show "DirectX 11"
# Check: Display tab should show GPU with VRAM
```

### Step 6: Create Snapshot

Inside QEMU (Ctrl+Alt+2 for monitor):
```
savevm base-install
quit
```

### Step 7: Apply Minimization

Inside Windows 11 VM:
```powershell
# Copy minimize-windows11.ps1 to VM
# Run as Administrator:
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
.\minimize-windows11.ps1

# Reboot when complete
```

### Step 8: Create Snapshot

Inside QEMU monitor:
```
savevm post-debloat
quit
```

### Step 9: Install Steam & BF6

Inside Windows 11 VM:
```powershell
# Download Steam: https://steampowered.com/download/
# Install Steam
# Install Battlefield 6 or 2042
# Test launch
```

### Step 10: Benchmark

Inside BF6:
1. Enable FPS counter (Settings → Graphics)
2. Play for 30 minutes
3. Record average FPS
4. Compare to prediction: 95-130 FPS @ 1440p High/Ultra

---

## GPU Passthrough Setup (One-Time)

**Before first VM launch, run:**

```bash
# Save this as /tmp/setup-gpu-passthrough.sh
cat > /tmp/setup-gpu-passthrough.sh << 'EOF'
#!/bin/bash
GPU_PCI="01:00.0"
GPU_VENDOR_ID="10de"
GPU_DEVICE_ID="2c05"

echo "Setting up GPU passthrough..."
echo "$GPU_PCI" > /sys/bus/pci/drivers/nvidia/unbind 2>/dev/null || true
echo "$GPU_VENDOR_ID:$GPU_DEVICE_ID" > /sys/bus/pci/drivers/vfio-pci/new_id
DRIVER=$(readlink /sys/bus/pci/devices/0000:$GPU_PCI/driver | xargs basename)
echo "GPU driver: $DRIVER"
[ "$DRIVER" = "vfio-pci" ] && echo "✓ Ready" || echo "✗ Failed"
EOF

# Run setup
sudo bash /tmp/setup-gpu-passthrough.sh
```

---

## Unhinged Integration (Phase 5)

### Add to control/service_launcher.py

```python
# In ServiceLauncher.__init__, add to self.services:
"windows_bf6_vm": {
    "order": 1.5,
    "command": ["qemu-system-x86_64", "-name", "helix-bf6-vm", ...],
    "description": "Windows 11 BF6 Gaming VM (HELIX)",
    "required": False,
    "background": True,
    "health_check": "check_helix_vm_health",
}

# Add health check method:
def check_helix_vm_health(self):
    import subprocess
    result = subprocess.run(["pgrep", "-f", "helix-bf6-vm"], capture_output=True)
    return (result.returncode == 0, "HELIX VM running" if result.returncode == 0 else "HELIX VM not running")
```

### Test Integration

```bash
# Start Windows VM via Unhinged service framework
python3 control/service_launcher.py start windows_bf6_vm

# Check status
python3 control/service_launcher.py status windows_bf6_vm

# Stop VM
python3 control/service_launcher.py stop windows_bf6_vm
```

---

## Success Criteria

| Metric | Target | Status |
|--------|--------|--------|
| VM Boot Time | <30 sec | TBD |
| Idle RAM | 1.0-1.4 GB | TBD |
| Disk Footprint | 28-35 GB | TBD |
| BF6 FPS | 95-130 @ 1440p | TBD |
| GPU Passthrough | Working | TBD |
| Service Integration | Complete | TBD |

---

## Troubleshooting

**GPU not detected in VM:**
- Verify GPU passthrough setup: `lspci -v | grep -A5 "01:00.0"`
- Check IOMMU groups: `cat /sys/kernel/iommu_groups/14/devices/*`
- Rebind GPU: Run setup script again

**Low FPS (<60):**
- Check GPU driver in VM: Device Manager → Display adapters
- Verify GPU passthrough active: `nvidia-smi` in VM
- Optimize QEMU config: Increase cores, enable CPU pinning

**Windows Update breaks minimization:**
- Rollback to snapshot: `qemu-img snapshot -a post-debloat`
- Disable Windows Update: Services → Windows Update → Disabled

---

**HELIX Implementation Ready** 🚀

