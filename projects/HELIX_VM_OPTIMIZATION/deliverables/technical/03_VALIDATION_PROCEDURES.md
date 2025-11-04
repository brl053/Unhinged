# Windows 11 Gaming VM - Technical Validation Procedures

## Pre-Implementation Validation Checklist

### 1. GPU Configuration Verification

**Command 1: Detailed GPU Detection**
```bash
lspci -v | grep -A10 "VGA\|3D"
```
**Expected Output:** GPU device with vendor (NVIDIA/AMD) and model  
**Current Status:** ⚠️ No discrete GPU detected (likely integrated)

**Command 2: GPU Driver Status**
```bash
lspci -k | grep -A3 "VGA\|3D"
```
**Expected Output:** Driver name (nouveau, amdgpu, nvidia, etc.)  
**Current Status:** TBD

**Command 3: Integrated GPU Check**
```bash
grep -i "radeon\|intel" /proc/cpuinfo
```
**Expected Output:** Integrated GPU info (AMD Ryzen has Radeon)  
**Current Status:** TBD

**Decision Point:** If integrated GPU, use GPU-assisted virtualization (Spice/QXL) instead of passthrough.

---

### 2. IOMMU & Virtualization Verification

**Command 1: IOMMU Status**
```bash
dmesg | grep -i "IOMMU\|AMD-Vi"
```
**Expected Output:** "IOMMU: Enabled" or "AMD-Vi: Enabled"  
**Current Status:** ✅ IOMMU device present (00:00.2)

**Command 2: IOMMU Groups**
```bash
for d in /sys/kernel/iommu_groups/*/devices/*; do n=${d%/*}; n=${n##*/}; printf '[%s] ' "$n"; cat "$d/modalias"; done
```
**Expected Output:** IOMMU groups with GPU device  
**Current Status:** TBD

**Command 3: KVM Module Status**
```bash
lsmod | grep kvm
```
**Expected Output:** `kvm_amd` or `kvm_intel` loaded  
**Current Status:** TBD

**Command 4: Nested Virtualization**
```bash
cat /sys/module/kvm_amd/parameters/nested
```
**Expected Output:** `1` (enabled) or `Y`  
**Current Status:** TBD

---

### 3. QEMU/KVM Infrastructure Verification

**Command 1: QEMU Installation**
```bash
which qemu-system-x86_64 && qemu-system-x86_64 --version
```
**Expected Output:** QEMU version 6.0+  
**Current Status:** TBD

**Command 2: Libvirt Status**
```bash
systemctl status libvirtd
```
**Expected Output:** `active (running)`  
**Current Status:** TBD

**Command 3: VFIO Module**
```bash
lsmod | grep vfio
```
**Expected Output:** `vfio_pci` loaded (for GPU passthrough)  
**Current Status:** TBD

**Command 4: Existing VM Infrastructure**
```bash
ls -la control/qemu_vm_launcher.py control/enhanced_vm_launcher.py
```
**Expected Output:** Both files present and executable  
**Current Status:** ✅ Both files present

---

### 4. Storage & Resource Verification

**Command 1: Disk Space**
```bash
df -h / | tail -1
```
**Expected Output:** 100+ GB free  
**Current Status:** TBD

**Command 2: RAM Availability**
```bash
free -h | grep "^Mem:"
```
**Expected Output:** 47+ GB available  
**Current Status:** ✅ 47 GB available

**Command 3: CPU Cores**
```bash
nproc
```
**Expected Output:** 16+ cores  
**Current Status:** ✅ 32 cores available

**Command 4: CPU Flags**
```bash
grep -o "svm\|vmx" /proc/cpuinfo | sort -u
```
**Expected Output:** `svm` (AMD) or `vmx` (Intel)  
**Current Status:** ✅ SVM present

---

### 5. Existing Unhinged Infrastructure Verification

**Command 1: Service Launcher**
```bash
python3 control/service_launcher.py --help
```
**Expected Output:** Help text with service management options  
**Current Status:** TBD

**Command 2: QEMU VM Launcher**
```bash
python3 control/qemu_vm_launcher.py --help
```
**Expected Output:** Help text with VM launch options  
**Current Status:** TBD

**Command 3: VM Directory Structure**
```bash
ls -la vm/build/ vm/runtime/ vm/testing/
```
**Expected Output:** Build scripts, runtime images, test suites  
**Current Status:** ✅ All directories present

**Command 4: Service Framework**
```bash
grep -r "class.*Service\|def.*health_check" control/ | head -5
```
**Expected Output:** Service framework patterns  
**Current Status:** TBD

---

### 6. Windows 11 Compatibility Verification

**Command 1: CPU Feature Check**
```bash
grep -E "sse4_2|popcnt" /proc/cpuinfo | head -1
```
**Expected Output:** Both flags present  
**Current Status:** ✅ Both present

**Command 2: TPM Simulation**
```bash
which swtpm
```
**Expected Output:** TPM simulator available (optional)  
**Current Status:** TBD

**Command 3: UEFI Firmware**
```bash
ls -la /usr/share/edk2/x64/OVMF_CODE.fd
```
**Expected Output:** UEFI firmware file present  
**Current Status:** TBD

---

## Validation Execution Plan

### Step 1: Run All Verification Commands
```bash
#!/bin/bash
# Save as validate_windows_vm_prerequisites.sh

echo "=== GPU Configuration ==="
lspci -v | grep -A10 "VGA\|3D"
lspci -k | grep -A3 "VGA\|3D"

echo "=== IOMMU Status ==="
dmesg | grep -i "IOMMU\|AMD-Vi"

echo "=== KVM Module ==="
lsmod | grep kvm

echo "=== QEMU Installation ==="
which qemu-system-x86_64 && qemu-system-x86_64 --version

echo "=== Storage & Resources ==="
df -h / | tail -1
free -h | grep "^Mem:"
nproc

echo "=== CPU Flags ==="
grep -E "sse4_2|popcnt|svm" /proc/cpuinfo | head -3
```

### Step 2: Document Results
Create validation report with all command outputs.

### Step 3: Identify Gaps
Compare results against expected outputs.

### Step 4: Resolve Issues
Address any missing components or configurations.

---

## Validation Success Criteria

| Component | Requirement | Status |
|-----------|-------------|--------|
| GPU | Detected (integrated or discrete) | TBD |
| IOMMU | Enabled | ✅ |
| KVM | Module loaded | TBD |
| QEMU | Version 6.0+ | TBD |
| Storage | 100+ GB free | TBD |
| RAM | 47+ GB available | ✅ |
| CPU | 16+ cores, SVM flag | ✅ |
| Service Framework | Functional | TBD |
| VM Infrastructure | Existing and working | ✅ |

**Validation Complete When:** All TBD items resolved to ✅

---

## Next Steps After Validation

1. **If All Checks Pass:** Proceed to Phase 1 (Windows 11 VM Creation)
2. **If GPU Issues:** Decide on GPU-assisted virtualization strategy
3. **If IOMMU Issues:** Enable in BIOS or kernel parameters
4. **If Storage Issues:** Free up disk space or use external storage
5. **If Service Framework Issues:** Debug and fix before proceeding

---

**Estimated Validation Time:** 30 minutes  
**Estimated Troubleshooting Time:** 1-2 hours (if issues found)

