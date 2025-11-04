# Phase 1: Validation & Preparation - Detailed Action Plan

**Phase Duration:** 1 Week  
**Status:** Ready to Execute  
**Blocking Questions:** 3 (must resolve before Phase 2)  
**Estimated Effort:** 8-12 hours

---

## Day 1: Hardware Verification (2 hours)

### Task 1.1: GPU Configuration Detection
```bash
# Command 1: Detailed GPU detection
lspci -v | grep -A10 "VGA\|3D"

# Command 2: GPU driver status
lspci -k | grep -A3 "VGA\|3D"

# Command 3: Integrated GPU check
grep -i "radeon\|intel" /proc/cpuinfo

# Command 4: GPU device enumeration
ls -la /dev/dri/
```

**Expected Outcomes:**
- [ ] GPU vendor identified (NVIDIA/AMD/Intel)
- [ ] GPU model identified
- [ ] Driver status confirmed
- [ ] Device enumeration successful

**Decision Point:** Discrete or integrated GPU?
- **Discrete:** Proceed with GPU passthrough strategy (research doc §5.1)
- **Integrated:** Use GPU-assisted virtualization (research doc §5.2)
- **Unknown:** Test both strategies

### Task 1.2: IOMMU Status Verification
```bash
# Command 1: IOMMU kernel status
dmesg | grep -i "IOMMU\|AMD-Vi\|VT-d"

# Command 2: IOMMU groups
for d in /sys/kernel/iommu_groups/*/devices/*; do 
  n=${d%/*}; n=${n##*/}; printf '[%s] ' "$n"; cat "$d/modalias"
done

# Command 3: Kernel config
grep "IOMMU" /boot/config-$(uname -r)

# Command 4: VFIO module status
lsmod | grep vfio
```

**Expected Outcomes:**
- [ ] IOMMU enabled in kernel
- [ ] IOMMU groups enumerated
- [ ] GPU in IOMMU group (if discrete)
- [ ] VFIO module available

**Decision Point:** IOMMU ready for GPU passthrough?
- **Yes:** Proceed with passthrough strategy
- **No:** Use GPU-assisted virtualization

---

## Day 2: Infrastructure Audit (2 hours)

### Task 2.1: QEMU/KVM Infrastructure
```bash
# Command 1: QEMU installation
which qemu-system-x86_64 && qemu-system-x86_64 --version

# Command 2: KVM module status
lsmod | grep kvm

# Command 3: Libvirt status
systemctl status libvirtd

# Command 4: Existing VM infrastructure
ls -la control/qemu_vm_launcher.py control/enhanced_vm_launcher.py
```

**Expected Outcomes:**
- [ ] QEMU version 6.0+ installed
- [ ] KVM module loaded
- [ ] Libvirt operational
- [ ] Existing VM launchers present

### Task 2.2: Service Framework Audit
```bash
# Command 1: Service launcher
python3 control/service_launcher.py --help

# Command 2: Service framework patterns
grep -r "class.*Service\|def.*health_check" control/ | head -10

# Command 3: VM directory structure
ls -la vm/build/ vm/runtime/ vm/testing/

# Command 4: Existing Alpine VM
ls -la vm/simple-alpine.qcow2
```

**Expected Outcomes:**
- [ ] Service launcher functional
- [ ] Service framework patterns identified
- [ ] VM build system present
- [ ] Alpine VM image exists

---

## Day 3: Storage & Resource Verification (1 hour)

### Task 3.1: Resource Availability
```bash
# Command 1: Disk space
df -h / | tail -1

# Command 2: RAM availability
free -h | grep "^Mem:"

# Command 3: CPU cores
nproc

# Command 4: CPU flags
grep -E "sse4_2|popcnt|svm" /proc/cpuinfo | head -1
```

**Expected Outcomes:**
- [ ] 100+ GB free disk space
- [ ] 47+ GB available RAM
- [ ] 16+ CPU cores
- [ ] SVM/VMX flags present

### Task 3.2: Windows 11 Compatibility Check
```bash
# Command 1: UEFI firmware
ls -la /usr/share/edk2/x64/OVMF_CODE.fd

# Command 2: TPM simulator (optional)
which swtpm

# Command 3: CPU feature check
grep -E "sse4_2|popcnt" /proc/cpuinfo | wc -l
```

**Expected Outcomes:**
- [ ] UEFI firmware available
- [ ] TPM simulator available (optional)
- [ ] CPU features confirmed

---

## Day 4: Decision Points & Planning (2 hours)

### Decision 1: GPU Strategy
**Question:** What GPU configuration did you find?

**Options:**
- [ ] Discrete GPU → GPU passthrough (research doc §5.1)
- [ ] Integrated GPU → GPU-assisted virtualization (research doc §5.2)
- [ ] Unknown → Test both strategies

**Action:** Document GPU configuration and chosen strategy

### Decision 2: Windows 11 Licensing
**Question:** Which Windows 11 variant will you use?

**Options:**
- [ ] Standard Windows 11 (95% confidence, higher risk)
- [ ] IoT Enterprise LTSC (98% confidence, enterprise licensing)
- [ ] Hybrid: Standard + conservative debloating (95% confidence, best stability)

**Action:** Document licensing decision and rationale

### Decision 3: Anti-Cheat Validation
**Question:** Should we test Proton first?

**Options:**
- [ ] Yes → Test BF6 with Proton on e-os (lower risk, 85-90% compatibility)
- [ ] No → Proceed directly to Windows VM (higher risk, higher fidelity)
- [ ] Both → Test Proton first, then Windows VM if needed

**Action:** Document anti-cheat validation strategy

### Decision 4: Integration Depth
**Question:** How deeply should Windows VM integrate with Unhinged?

**Options:**
- [ ] Minimal: Standalone Windows VM (simple, isolated)
- [ ] Moderate: Service framework integration (recommended)
- [ ] Deep: Full GUI controls + health monitoring (comprehensive)

**Action:** Document integration depth decision

---

## Day 5: Proton Testing (Optional, 2 hours)

### Task 5.1: Proton Installation & Testing
```bash
# Command 1: Check Steam installation
which steam

# Command 2: Install Proton (via Steam)
# Launch Steam → Settings → Compatibility → Enable Proton

# Command 3: Install BF6 (via Steam or EA Play)
# Launch Steam → Search "Battlefield" → Install

# Command 4: Test BF6 launch
# Right-click BF6 → Properties → Compatibility → Force Proton version
# Launch game and test for 5-10 minutes
```

**Expected Outcomes:**
- [ ] Proton installed and configured
- [ ] BF6 installed successfully
- [ ] Game launches without errors
- [ ] Anti-cheat compatibility confirmed (or failed)

**Decision Point:** Does BF6 work with Proton?
- **Yes:** Consider Proton as primary solution (simpler, no Windows VM needed)
- **No:** Proceed with Windows VM strategy
- **Partial:** Use Windows VM for full compatibility

---

## Day 6-7: Documentation & Planning (2 hours)

### Task 6.1: Create Phase 1 Report
**Document:**
- [ ] GPU configuration and strategy
- [ ] IOMMU status and readiness
- [ ] QEMU/KVM infrastructure audit results
- [ ] Service framework audit results
- [ ] Resource availability summary
- [ ] Windows 11 licensing decision
- [ ] Anti-cheat validation results
- [ ] Integration depth decision

### Task 6.2: Phase 2 Planning
**Prepare:**
- [ ] Windows 11 ISO download link
- [ ] Minimization script (from research doc §4.2)
- [ ] QEMU launch configuration (from research doc §5.1)
- [ ] Snapshot strategy (from research doc §9.2)
- [ ] Performance benchmarking plan (from research doc §6.2)

### Task 6.3: Risk Assessment
**Identify:**
- [ ] GPU passthrough risks (if applicable)
- [ ] Minimization risks (if applicable)
- [ ] Anti-cheat risks (if applicable)
- [ ] Integration risks (if applicable)
- [ ] Mitigation strategies for each

---

## Success Criteria

### Phase 1 Complete When:
- [ ] GPU configuration verified
- [ ] IOMMU status confirmed
- [ ] QEMU/KVM infrastructure audited
- [ ] Service framework patterns identified
- [ ] Resource availability confirmed
- [ ] Windows 11 licensing decided
- [ ] Anti-cheat strategy determined
- [ ] Integration depth decided
- [ ] Phase 1 report completed
- [ ] Phase 2 planning completed

### Blocking Issues Resolved:
- [ ] GPU strategy determined
- [ ] Anti-cheat compatibility validated (or fallback planned)
- [ ] Windows 11 licensing decided

---

## Deliverables

### Phase 1 Report Should Include:
1. **Hardware Validation Summary**
   - GPU configuration and strategy
   - IOMMU status and readiness
   - Resource availability (CPU, RAM, storage)

2. **Infrastructure Assessment**
   - QEMU/KVM status
   - Service framework audit
   - Existing VM infrastructure

3. **Decision Documentation**
   - GPU strategy (passthrough vs. virtualization)
   - Windows 11 licensing variant
   - Anti-cheat validation results
   - Integration depth decision

4. **Risk Assessment**
   - Identified risks
   - Mitigation strategies
   - Contingency plans

5. **Phase 2 Preparation**
   - Windows 11 ISO ready
   - Minimization script prepared
   - QEMU configuration ready
   - Snapshot strategy documented

---

## Timeline

| Day | Task | Duration | Status |
|-----|------|----------|--------|
| 1 | Hardware verification | 2 hrs | Ready |
| 2 | Infrastructure audit | 2 hrs | Ready |
| 3 | Resource verification | 1 hr | Ready |
| 4 | Decision points | 2 hrs | Ready |
| 5 | Proton testing (optional) | 2 hrs | Optional |
| 6-7 | Documentation & planning | 2 hrs | Ready |
| **Total** | **Phase 1 Complete** | **8-12 hrs** | **Ready** |

---

## Next Steps After Phase 1

### If All Checks Pass:
→ Proceed to Phase 2 (Windows 11 VM Creation)

### If GPU Issues Found:
→ Decide: GPU passthrough or GPU-assisted virtualization

### If Anti-Cheat Blocks:
→ Use Proton as primary solution (simpler, no Windows VM)

### If Storage Issues:
→ Free up disk space or use external storage

### If Service Framework Issues:
→ Debug and fix before proceeding

---

**Phase 1 Status:** ✅ Ready to Execute  
**Estimated Completion:** 1 Week  
**Next Phase:** Phase 2 (Windows 11 VM Creation)

