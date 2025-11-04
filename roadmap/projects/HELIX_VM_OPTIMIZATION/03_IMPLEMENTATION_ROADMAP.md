# HELIX VM Optimization - Implementation Roadmap

---

## Phase 1: Validation & Preparation (Week 1)

**Day 1-2: Hardware Verification**
- GPU detection: `lspci -v | grep -A10 "VGA\|3D"` → Determine discrete/integrated
- IOMMU status: `dmesg | grep -i "IOMMU\|AMD-Vi"` → Confirm operational
- KVM module: `lsmod | grep kvm` → Verify loaded
- QEMU version: `qemu-system-x86_64 --version` → Confirm 6.0+
- Storage check: `df -h /` → Verify 100+ GB free

**Day 3-4: Infrastructure Audit**
- Service launcher: `python3 control/service_launcher.py --help`
- QEMU launcher: `python3 control/qemu_vm_launcher.py --help`
- VM directory: `ls -la vm/build/ vm/runtime/ vm/testing/`
- Alpine VM: Verify existing infrastructure working

**Day 5-7: Decision Points & Planning**
- GPU strategy: Passthrough or virtualization?
- Windows licensing: Standard or LTSC?
- Anti-cheat validation: Test Proton first?
- Integration depth: Minimal or full service framework?

**Deliverable:** Phase 1 report with GPU strategy, licensing decision, anti-cheat results

---

## Phase 2: Windows 11 VM Creation (Week 2)

**Step 1: Base Installation**
```bash
qemu-img create -f qcow2 bf6-w11.qcow2 40G
# Boot from Windows 11 ISO
# Minimal installation (network-only, no additional features)
# Local account (no Microsoft Account)
# Create snapshot: base-install
```

**Step 2: Driver Installation**
- GPU drivers (NVIDIA/AMD minimal, no bloatware)
- Chipset drivers (minimal only)
- Verify DirectX 11: `dxdiag` → System tab
- Create snapshot: drivers-installed

**Step 3: Conservative Debloating**
- Disable telemetry: DiagTrack, dmwappushservice
- Disable VBS Memory Integrity: `New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\DeviceGuard\Scenarios\HypervisorEnforcedCodeIntegrity" -Name "Enabled" -Value 0 -Force`
- Disable visual effects: `New-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects" -Name "VisualFXSetting" -Value 2 -Force`
- Disable Windows Search: `Get-Service -Name WSearch | Stop-Service -Force; Set-Service -Name WSearch -StartupType Disabled`
- Create snapshot: post-conservative-debloat

**Deliverable:** Windows 11 VM with DirectX 11 verified, snapshots created

---

## Phase 3: Aggressive Minimization (Week 3)

**PowerShell AppX Removal Script:**
```powershell
# Remove non-essential UWP apps
$bloatapps = @(
  "Microsoft.3DBuilder", "Microsoft.BingFinance", "Microsoft.BingNews",
  "Microsoft.BingWeather", "Microsoft.Getstarted", "Microsoft.Messaging",
  "Microsoft.People", "Microsoft.SkypeApp", "Microsoft.WindowsAlarms",
  "Microsoft.WindowsCamera", "Clipchamp.Clipchamp"
)
$bloatapps | ForEach-Object {
  Get-AppxPackage -Name $_ -AllUsers | Remove-AppxPackage -AllUsers -ErrorAction SilentlyContinue
}

# Disable non-essential services
@("DiagTrack", "dmwappushservice", "WMPNetworkSvc", "RetailDemo") | ForEach-Object {
  Get-Service -Name $_ -ErrorAction SilentlyContinue | Stop-Service -Force
  Set-Service -Name $_ -StartupType Disabled
}
```

**DirectX 11 Runtime Verification:**
- Install DirectX End-User Runtime Web Installer
- Install Visual C++ 2015-2022 redistributables (x64 + x86)
- Verify: `dxdiag` confirms DirectX 11
- Create snapshot: directx-verified

**Gaming Runtime Setup:**
- Install Steam or EA Play
- Install Battlefield 6/2042
- Test launch and basic gameplay
- Create snapshot: gaming-ready

**Deliverable:** Minimized Windows 11 VM (28-35 GB), BF6 launch verified

---

## Phase 4: Performance Optimization (Week 4)

**Windows VM Tuning:**
- Enable Game Mode: Settings → Gaming → Game Mode
- Disable background app refresh: Settings → Privacy & Security → General
- Set power plan to "High Performance"
- Disable unnecessary startup programs

**QEMU/KVM Tuning:**
```bash
qemu-system-x86_64 \
  -name helix-bf6-vm \
  -machine type=pc,accel=kvm,kernel-irqchip=on \
  -cpu host,+invtsc,+tsc \
  -smp cores=8,threads=2,sockets=1 \
  -m 16G \
  -device iommu,intremap=on,caching-mode=on \
  -device vfio-pci,host=01:00.0 \  # GPU passthrough (if applicable)
  -drive file=bf6-w11.qcow2,if=virtio,format=qcow2,cache=writeback \
  -netdev user,id=net0 -device e1000,netdev=net0 \
  -bios /usr/share/edk2/x64/OVMF_CODE.fd
```

**Benchmarking:**
- Measure baseline FPS (1440p High/Ultra)
- Record CPU/RAM utilization
- Test GPU passthrough vs. virtualization
- Compare against predictions (95-130 FPS)

**Deliverable:** Performance benchmarks, QEMU config optimized

---

## Phase 5: Unhinged Integration (Week 5)

**Service Framework Enhancement:**
- Add Windows VM to service_launcher.py
- Implement VM lifecycle management (start/stop/restart)
- Add health checks for VM availability
- Integrate with service monitoring dashboard

**Communication Layer:**
- Configure 9p virtio filesystem for host-VM communication
- Implement bidirectional message passing
- Test shared directory mounting
- Add communication tests

**GUI Integration:**
- Add Windows VM controls to GTK4 GUI
- Display VM status in health dashboard
- Implement VM launch/stop buttons
- Add performance monitoring widgets

**Deliverable:** Windows VM fully integrated with Unhinged service framework

---

## Phase 6: Testing & Validation (Week 6)

**Functional Testing:**
- [ ] BF6 launch and gameplay
- [ ] Anti-cheat compatibility
- [ ] Host-VM communication
- [ ] Resource isolation

**Performance Testing:**
- [ ] Sustained FPS measurement (30+ minutes)
- [ ] CPU/RAM utilization under load
- [ ] Thermal stability testing
- [ ] Network performance (if applicable)

**Stability Testing:**
- [ ] Extended gameplay sessions (2+ hours)
- [ ] VM snapshot/rollback procedures
- [ ] Windows Update compatibility
- [ ] Crash recovery procedures

**Deliverable:** Test report, all success criteria validated

---

## Phase 7: Documentation & Deployment (Week 7)

**Documentation:**
- [ ] Windows 11 VM setup guide
- [ ] Minimization procedures documented
- [ ] Troubleshooting guide
- [ ] Performance tuning reference

**Deployment Preparation:**
- [ ] Create production VM image
- [ ] Version-control minimized Windows 11 image
- [ ] Implement automated backup strategy
- [ ] Create disaster recovery procedures

**Knowledge Transfer:**
- [ ] Document lessons learned
- [ ] Create operational runbook
- [ ] Add to Unhinged documentation
- [ ] Update LlmDocs annotations

**Deliverable:** Production-ready Windows 11 gaming VM, complete documentation

---

## Success Criteria Checklist

| Criterion | Target | Status |
|-----------|--------|--------|
| VM Boot Time | <30 sec | [ ] |
| Idle RAM | 1.0-1.4 GB | [ ] |
| Disk Footprint | 28-35 GB | [ ] |
| BF6 FPS | 95-130 @ 1440p | [ ] |
| Anti-Cheat | 100% compatible | [ ] |
| Integration | Complete | [ ] |
| Documentation | Complete | [ ] |
| Team Trained | Yes | [ ] |

---

## Critical Blockers Resolution

**Before Phase 2 Execution:**
1. ✅ GPU configuration verified (discrete/integrated determined)
2. ✅ Anti-cheat compatibility validated (Proton tested)
3. ✅ Windows 11 licensing decided (Standard/LTSC chosen)

**If Blockers Unresolved:**
- GPU unknown? → Use GPU-assisted virtualization (70-75% native)
- Anti-cheat fails? → Use Proton as primary solution
- Licensing unclear? → Use Standard Windows 11 + conservative debloating

---

## Resource Requirements

- **Disk Space:** 100+ GB free (VM + snapshots)
- **RAM:** 20+ GB free (16 GB VM + 4 GB overhead)
- **CPU:** 8+ cores available (6-8 pinned to VM)
- **Time:** 7 weeks (concurrent phases possible)
- **Team:** 3+ engineers (lead, implementation, QA)

---

## Rollback Procedures

**If Phase Fails:**
```bash
# List snapshots
qemu-img snapshot -l bf6-w11.qcow2

# Rollback to checkpoint
qemu-img snapshot -a base-install bf6-w11.qcow2
```

**Fallback Options:**
- GPU passthrough fails? → Use GPU-assisted virtualization
- Anti-cheat blocks? → Use Proton on e-os directly
- Performance insufficient? → Optimize QEMU config or increase allocation

---

**HELIX Implementation Roadmap Complete** 🚀

**Next Action:** Execute Phase 1 validation, resolve 3 blocking questions, proceed to Phase 2

