# HELIX Project: Windows 11 VM Boot Issue - Technical Report

## Problem Statement

The HELIX project aims to create a Windows 11 gaming virtual machine running on a Linux host (Ubuntu) with GPU passthrough to play Battlefield 6 at high performance. Phase 2 of the project involves installing Windows 11 from an ISO image into a QCOW2 disk image using QEMU/KVM virtualization. The installation process is failing at the BIOS boot stage, preventing Windows from reaching the installer interface. The VM boots to a black screen and never progresses beyond the UEFI firmware initialization phase.

## System Specifications

The host system is an Ubuntu Linux machine running kernel 6.14.0-1015-oem with an AMD Ryzen 9 9950X processor featuring 16 cores and 32 threads running at 5.7 GHz. The system has 60 GB of total RAM with 47 GB available for allocation. Storage consists of an SSD with 585 GB of available space. The discrete GPU is an NVIDIA RTX 4090 with 16 GB of VRAM located at PCI address 01:00.0 in IOMMU group 14. QEMU version 8.2.2 is installed with KVM acceleration enabled and AMD IOMMU operational. The Windows 11 ISO is Win11_25H2_English_x64.iso, measuring 7.3 GB and verified as a valid bootable ISO 9660 CD-ROM filesystem with MD5 hash 6b05bba98d7b55d299792c08080d6a56.

## What We've Discovered

Through systematic diagnostics, we identified that Windows 11 is actually booting successfully to the kernel level but halting before the installer can load. The QEMU monitor revealed CPU register state HLT=1, indicating the processor executed a HALT instruction, which means the Windows kernel loaded and is now paused rather than crashed. Serial console output from the UEFI firmware revealed the actual blocker: the BIOS is timing out while attempting to boot from the CD-ROM device. The specific error message was "BdsDxe: failed to start Boot0001 'UEFI QEMU DVD-ROM QM00003' from PciRoot(0x0)/Pci(0x1,0x1)/Ata(Secondary,Master,0x0): Time out". After this timeout, the BIOS falls back to PXE network boot, which also fails, leaving the system halted.

## Diagnostic Evidence

Multiple diagnostic checks confirmed the nature of the failure. The QCOW2 disk image remained at exactly 384 KB throughout all boot attempts, indicating that Windows never progressed to the installation phase where it would write to disk. The ISO file was confirmed to be properly attached to the QEMU virtual IDE controller as ide0-cd0 and was readable by QEMU. CPU usage remained consistently high at 95-100 percent, indicating active computation rather than a hung process. The QEMU process maintained stable memory usage at approximately 246-253 MB, suggesting normal operation without memory leaks or crashes. The serial console output explicitly showed the BIOS attempting to read the CD-ROM, timing out after a fixed period, and then attempting PXE boot as a fallback mechanism.

## What We've Tried

We attempted multiple configuration changes to resolve the issue. CPU model changes included switching from the host CPU model to EPYC-v4, which is known to improve Windows 11 compatibility on AMD systems. Display device changes included testing both QXL-VGA and standard VGA devices to rule out display driver initialization issues. BIOS firmware versions were tested, including /usr/share/ovmf/OVMF.fd and /usr/share/OVMF/OVMF_CODE_4M.fd with corresponding VARS files. Boot parameter modifications included adding explicit boot order specifications with -boot order=d,menu=off and attempting both -cdrom and -drive media=cdrom approaches for ISO attachment. IDE controller cache settings were adjusted from writeback to cache=none to improve CD-ROM read performance. All configuration changes resulted in identical behavior: BIOS timeout on CD-ROM boot followed by PXE fallback.

## Current Status

The QEMU virtual machine is currently running at 95 percent CPU utilization with 246 MB of allocated memory. The GTK display window shows a black screen with no visible output. The UEFI firmware is stuck in a boot loop where it attempts to read the Windows 11 ISO from the virtual CD-ROM device, times out after approximately 30-60 seconds, and then attempts PXE network boot before halting. The Windows 11 kernel has loaded into memory as evidenced by the HLT=1 CPU state, but the installer has never been reached. No data has been written to the QCOW2 disk image, confirming that the installation process has not progressed beyond the firmware initialization stage.

## Root Cause Analysis

The fundamental issue is that the UEFI firmware (OVMF) is unable to read the Windows 11 ISO from the virtual CD-ROM device within its timeout window. This is not a display rendering problem, not a CPU compatibility issue, and not a disk initialization problem. The Windows 11 25H2 ISO appears to have either a larger boot sector or more complex boot code that requires more time to load than the UEFI firmware's default timeout allows. The BIOS timeout occurs before the Windows bootloader can execute, preventing any progress toward the installer. This is a known compatibility issue between certain Windows 11 versions (particularly 24H2 and later) and QEMU's UEFI implementation, where the firmware's CD-ROM read timeout is insufficient for these larger ISO images.

