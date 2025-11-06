# HELIX Phase 2 - Execution Checklist

**Status:** Ready to Execute (Awaiting Windows 11 ISO)  
**Date:** November 4, 2025  
**Estimated Duration:** 2-3 hours  
**Success Criteria:** BF6 launches, FPS ≥ 60 @ 1440p

---

## Pre-Execution Checklist

### Infrastructure Verification
- [ ] Verify QCOW2 disk exists: `ls -lh /home/e-bliss-station-1/Projects/Unhinged/vm/bf6-w11-gaming.qcow2`
- [ ] Verify launcher script executable: `ls -la /home/e-bliss-station-1/Projects/Unhinged/vm/launch-bf6-vm.sh`
- [ ] Verify minimization script exists: `ls -la /home/e-bliss-station-1/Projects/Unhinged/vm/minimize-windows11.ps1`
- [ ] Verify storage available: `df -h /home/e-bliss-station-1/Projects/Unhinged/vm/`

### Hardware Verification
- [ ] CPU cores available: `nproc` (should be 32)
- [ ] RAM available: `free -h` (should be 47+ GB)
- [ ] GPU detected: `lspci -v | grep -A5 "01:00.0"` (should show NVIDIA RTX 4090)
- [ ] IOMMU operational: `dmesg | grep IOMMU` (should show AMD-Vi enabled)
- [ ] KVM module loaded: `lsmod | grep kvm` (should show kvm_amd)

### GPU Passthrough Setup
- [ ] Create GPU passthrough setup script: `cat > /tmp/setup-gpu-passthrough.sh << 'EOF'` (see below)
- [ ] Make executable: `chmod +x /tmp/setup-gpu-passthrough.sh`
- [ ] Run as root: `sudo bash /tmp/setup-gpu-passthrough.sh`
- [ ] Verify GPU bound to vfio-pci: `lspci -k | grep -A3 "01:00.0"` (should show vfio-pci)

### Windows 11 ISO
- [ ] **BLOCKING:** Obtain Windows 11 25H2 ISO (6 GB)
- [ ] Save to: `/tmp/Windows11.iso`
- [ ] Verify: `ls -lh /tmp/Windows11.iso` (should show ~6 GB)

---

## GPU Passthrough Setup Script

Save this as `/tmp/setup-gpu-passthrough.sh`:

```bash
#!/bin/bash
GPU_PCI="01:00.0"
GPU_VENDOR_ID="10de"  # NVIDIA
GPU_DEVICE_ID="2c05"  # RTX 4090

echo "Setting up GPU passthrough for HELIX VM..."

# Unbind GPU from nvidia driver
echo "Unbinding GPU from nvidia driver..."
echo "$GPU_PCI" > /sys/bus/pci/drivers/nvidia/unbind 2>/dev/null || true

# Bind GPU to vfio-pci
echo "Binding GPU to vfio-pci..."
echo "$GPU_VENDOR_ID:$GPU_DEVICE_ID" > /sys/bus/pci/drivers/vfio-pci/new_id

# Verify binding
DRIVER=$(readlink /sys/bus/pci/devices/0000:$GPU_PCI/driver | xargs basename)
echo "GPU driver: $DRIVER"

if [ "$DRIVER" = "vfio-pci" ]; then
    echo "✓ GPU passthrough ready"
    exit 0
else
    echo "✗ GPU passthrough setup failed"
    exit 1
fi
```

---

## Phase 2 Execution Steps

### Step 1: Verify Infrastructure (5 minutes)
```bash
cd /home/e-bliss-station-1/Projects/Unhinged/vm
ls -lh bf6-w11-gaming.qcow2 launch-bf6-vm.sh minimize-windows11.ps1
```

### Step 2: Setup GPU Passthrough (5 minutes)
```bash
sudo bash /tmp/setup-gpu-passthrough.sh
# Verify: lspci -k | grep -A3 "01:00.0"
```

### Step 3: Launch VM (2 minutes)
```bash
cd /home/e-bliss-station-1/Projects/Unhinged/vm
./launch-bf6-vm.sh /tmp/Windows11.iso
```

### Step 4: Install Windows 11 (30 minutes)
- Boot from ISO
- Select "Custom Installation"
- Select virtio disk (40GB)
- Minimal install (network only)
- Local account (no Microsoft Account)
- Skip optional features

### Step 5: Install Drivers (20 minutes)
- Download NVIDIA driver (minimal)
- Install GPU driver only
- Reboot
- Verify DirectX 11: `dxdiag` → System tab

### Step 6: Create Snapshot (2 minutes)
```
# In QEMU monitor (Ctrl+Alt+2):
savevm base-install
quit
```

### Step 7: Run Minimization (5 minutes)
```powershell
# In Windows 11 VM, run as Administrator:
powershell -ExecutionPolicy Bypass -File minimize-windows11.ps1
# Reboot when complete
```

### Step 8: Create Snapshot (2 minutes)
```
# In QEMU monitor:
savevm post-debloat
quit
```

### Step 9: Install Steam + BF6 (30 minutes)
- Download Steam
- Install Steam
- Install Battlefield 6/2042
- Test launch

### Step 10: Benchmark (30 minutes)
- Enable FPS counter in BF6
- Play for 30 minutes
- Record average FPS
- Compare to prediction: 95-130 FPS @ 1440p High/Ultra

---

## Success Criteria

| Criterion | Target | Status |
|-----------|--------|--------|
| Windows 11 boots | Yes | [ ] |
| DirectX 11 verified | Yes | [ ] |
| GPU passthrough working | Yes | [ ] |
| Minimization script runs | Yes | [ ] |
| BF6 launches | Yes | [ ] |
| BF6 FPS | 95-130 @ 1440p | [ ] |
| Idle RAM | 1.0-1.4 GB | [ ] |
| No crashes | Yes | [ ] |

**Phase 2 Complete When:** All 8 boxes checked ✓

---

## Troubleshooting

**GPU not detected in VM:**
- Verify passthrough setup: `lspci -k | grep -A3 "01:00.0"`
- Check IOMMU groups: `cat /sys/kernel/iommu_groups/14/devices/*`
- Fallback: Use GPU-assisted virtualization (70-75% native FPS)

**Low FPS (<60):**
- Check GPU driver in VM: Device Manager → Display adapters
- Verify GPU passthrough active: `nvidia-smi` in VM
- Optimize QEMU config: Increase cores, enable CPU pinning

**Windows Update breaks minimization:**
- Rollback: `qemu-img snapshot -a post-debloat`
- Disable Windows Update: Services → Windows Update → Disabled

---

## Next Phase (Phase 3)

Once Phase 2 validates (BF6 running, FPS ≥ 60):
- Phase 3: Aggressive minimization validation
- Phase 4: Performance optimization
- Phase 5: Unhinged service framework integration

---

**HELIX Phase 2 - Ready to Execute** 🚀

**Blocking Item:** Windows 11 ISO acquisition (human action required)

**Once ISO acquired:** Execute checklist above, report FPS numbers

