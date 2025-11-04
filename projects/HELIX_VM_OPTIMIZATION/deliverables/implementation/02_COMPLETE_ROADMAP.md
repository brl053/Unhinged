# Windows 11 Gaming VM Implementation Roadmap

## Phase 1: Validation & Preparation (Week 1)

### 1.1 Hardware Verification
- [ ] Verify GPU configuration: `lspci -v | grep -A10 "VGA\|3D"`
- [ ] Confirm IOMMU status: `dmesg | grep IOMMU`
- [ ] Test KVM module: `lsmod | grep kvm`
- [ ] Validate CPU flags: Confirm `svm` flag present
- [ ] Check disk space: Ensure 100+ GB free for VM + snapshots

### 1.2 Dependency Audit
- [ ] Verify QEMU installed: `which qemu-system-x86_64`
- [ ] Check libvirt: `systemctl status libvirtd`
- [ ] Validate existing qemu_vm_launcher.py functionality
- [ ] Review enhanced_vm_launcher.py for bidirectional communication
- [ ] Audit service_launcher.py for VM lifecycle management

### 1.3 Decision Points
- [ ] Decide: Standard Windows 11 vs. IoT Enterprise LTSC
- [ ] Decide: GPU passthrough vs. GPU-assisted virtualization
- [ ] Decide: Minimization aggressiveness level
- [ ] Decide: Proton alternative evaluation needed?

---

## Phase 2: Windows 11 VM Creation (Week 2)

### 2.1 Base Installation
- [ ] Download Windows 11 25H2 ISO
- [ ] Create QCOW2 disk: `qemu-img create -f qcow2 bf6-w11.qcow2 40G`
- [ ] Boot VM from ISO using qemu_vm_launcher.py
- [ ] Complete Windows 11 installation (minimal, local account)
- [ ] Create snapshot: `base-install`

### 2.2 Driver Installation
- [ ] Install GPU drivers (NVIDIA/AMD minimal)
- [ ] Install chipset drivers (minimal, no bloatware)
- [ ] Verify DirectX 11: `dxdiag` → System tab
- [ ] Create snapshot: `drivers-installed`

### 2.3 Minimization Phase 1 (Conservative)
- [ ] Disable telemetry services (DiagTrack, dmwappushservice)
- [ ] Disable VBS Memory Integrity: +8-15% gaming performance
- [ ] Disable visual effects: 200-400 MB RAM savings
- [ ] Disable Windows Search indexing
- [ ] Create snapshot: `post-conservative-debloat`

---

## Phase 3: Aggressive Minimization (Week 3)

### 3.1 PowerShell AppX Removal
- [ ] Execute bloatware removal script (§4.2 from document)
- [ ] Remove: Weather, Maps, Photos, Xbox, Teams, Copilot
- [ ] Verify: No system breakage after removal
- [ ] Create snapshot: `post-appx-removal`

### 3.2 DirectX 11 Runtime Verification
- [ ] Install DirectX End-User Runtime Web Installer
- [ ] Install Visual C++ 2015-2022 redistributables (x64 + x86)
- [ ] Verify: `dxdiag` confirms DirectX 11
- [ ] Create snapshot: `directx-verified`

### 3.3 Gaming Runtime Setup
- [ ] Install Steam or EA Play
- [ ] Install Battlefield 6/2042
- [ ] Test launch and basic gameplay
- [ ] Create snapshot: `gaming-ready`

---

## Phase 4: Performance Optimization (Week 4)

### 4.1 Windows VM Tuning
- [ ] Enable Game Mode: Settings → Gaming → Game Mode
- [ ] Disable background app refresh
- [ ] Set power plan to "High Performance"
- [ ] Disable unnecessary startup programs

### 4.2 QEMU/KVM Tuning
- [ ] Configure CPU pinning (6-8 cores)
- [ ] Optimize memory allocation (16 GB)
- [ ] Enable KVM acceleration
- [ ] Configure GPU passthrough (if applicable)
- [ ] Test with enhanced_vm_launcher.py

### 4.3 Benchmarking
- [ ] Measure baseline FPS (1440p High/Ultra)
- [ ] Record CPU/RAM utilization
- [ ] Test with GPU passthrough vs. virtualization
- [ ] Compare against document predictions (95-130 FPS)

---

## Phase 5: Unhinged Integration (Week 5)

### 5.1 Service Framework Integration
- [ ] Add Windows VM to service_launcher.py
- [ ] Implement VM lifecycle management (start/stop/restart)
- [ ] Add health checks for VM availability
- [ ] Integrate with service monitoring dashboard

### 5.2 Communication Layer
- [ ] Configure 9p virtio filesystem for host-VM communication
- [ ] Implement bidirectional message passing
- [ ] Test shared directory mounting
- [ ] Add communication tests to testing/ directory

### 5.3 GUI Integration
- [ ] Add Windows VM controls to GTK4 GUI
- [ ] Display VM status in health dashboard
- [ ] Implement VM launch/stop buttons
- [ ] Add performance monitoring widgets

---

## Phase 6: Testing & Validation (Week 6)

### 6.1 Functional Testing
- [ ] Test BF6 launch and gameplay
- [ ] Verify anti-cheat compatibility
- [ ] Test host-VM communication
- [ ] Validate resource isolation

### 6.2 Performance Testing
- [ ] Sustained FPS measurement (30+ minutes)
- [ ] CPU/RAM utilization under load
- [ ] Thermal stability testing
- [ ] Network performance (if applicable)

### 6.3 Stability Testing
- [ ] Extended gameplay sessions (2+ hours)
- [ ] VM snapshot/rollback procedures
- [ ] Windows Update compatibility
- [ ] Crash recovery procedures

---

## Phase 7: Documentation & Deployment (Week 7)

### 7.1 Documentation
- [ ] Create Windows 11 VM setup guide
- [ ] Document minimization procedures
- [ ] Add troubleshooting guide
- [ ] Create performance tuning reference

### 7.2 Deployment Preparation
- [ ] Create production VM image
- [ ] Version-control minimized Windows 11 image
- [ ] Implement automated backup strategy
- [ ] Create disaster recovery procedures

### 7.3 Knowledge Transfer
- [ ] Document lessons learned
- [ ] Create operational runbook
- [ ] Add to Unhinged documentation
- [ ] Update LlmDocs annotations

---

## Success Criteria

| Criterion | Target | Status |
|-----------|--------|--------|
| FPS Performance | 95-130 FPS @ 1440p | TBD |
| VM Boot Time | <30 seconds | TBD |
| Idle RAM Usage | 1.0-1.4 GB | TBD |
| Disk Footprint | 30-35 GB | TBD |
| Anti-Cheat Compatibility | 100% | TBD |
| Host Stability | No crashes | TBD |
| Integration Completeness | Full service framework | TBD |

---

## Risk Mitigation

| Risk | Probability | Mitigation |
|------|-------------|-----------|
| Anti-cheat blocks VM | Medium | Test early; have Proton fallback |
| GPU passthrough fails | Low | Use GPU-assisted virtualization |
| Windows Update breaks minimization | Medium | Maintain snapshots; use LTSC |
| Performance below target | Low | Optimize QEMU config; benchmark early |
| Integration complexity | Medium | Reuse existing service framework |

---

**Timeline:** 7 weeks (concurrent phases possible)  
**Resource Requirements:** 1 developer, 100+ GB storage, 16+ GB RAM allocation  
**Estimated Effort:** 120-160 hours

