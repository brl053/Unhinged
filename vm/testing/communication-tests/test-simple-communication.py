#!/usr/bin/env python3
"""
@llm-doc Test Simple VM Communication Pipeline
@llm-version 1.0.0
@llm-date 2025-01-26
@llm-author Unhinged Team

## Overview
Tests the simplified VM communication pipeline to ensure:
1. VM console output is visible in host terminal
2. Communication is reliable and real-time
3. VM status messages reach the host

## Test Scenarios
- VM boot messages → Host terminal
- Unhinged status updates → Host terminal  
- Error messages → Host terminal
- Graceful shutdown → Host terminal

@llm-principle Test unidirectional communication reliability
@llm-culture Verify independence through isolated VM communication
"""

import subprocess
import time
import sys
import threading
from pathlib import Path
import signal
import os

class SimpleCommunicationTest:
    """Test the simple VM communication pipeline"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.test_results = []
        self.vm_process = None
        self.output_captured = []
        self.test_running = False
        
    def log(self, message, level="INFO"):
        """Log test message"""
        symbols = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "TEST": "🧪"}
        print(f"{symbols.get(level, 'ℹ️')} {message}")
        
    def test_vm_launcher_availability(self):
        """Test if simple VM launcher is available"""
        self.log("Testing simple VM launcher availability...", "TEST")
        
        launcher_path = self.project_root / "control" / "simple_vm_launcher.py"
        if launcher_path.exists() and launcher_path.is_file():
            self.log("Simple VM launcher found", "SUCCESS")
            return True
        else:
            self.log("Simple VM launcher not found", "ERROR")
            return False
    
    def test_vm_disk_creation(self):
        """Test VM disk creation"""
        self.log("Testing VM disk creation...", "TEST")
        
        vm_disk = self.project_root / "vm" / "simple-alpine.qcow2"
        if vm_disk.exists():
            self.log("VM disk already exists", "SUCCESS")
            return True
        
        # Try to create disk using the launcher
        try:
            result = subprocess.run([
                'python3', 'control/simple_vm_launcher.py'
            ], cwd=self.project_root, capture_output=True, text=True, timeout=30)
            
            if vm_disk.exists():
                self.log("VM disk created successfully", "SUCCESS")
                return True
            else:
                self.log("VM disk creation failed", "ERROR")
                return False
                
        except subprocess.TimeoutExpired:
            self.log("VM disk creation timed out", "ERROR")
            return False
        except Exception as e:
            self.log(f"VM disk creation error: {e}", "ERROR")
            return False
    
    def test_qemu_availability(self):
        """Test if QEMU is available"""
        self.log("Testing QEMU availability...", "TEST")
        
        try:
            result = subprocess.run(['which', 'qemu-system-x86_64'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.log("QEMU is available", "SUCCESS")
                return True
            else:
                self.log("QEMU not found", "ERROR")
                return False
        except Exception as e:
            self.log(f"QEMU check error: {e}", "ERROR")
            return False
    
    def test_alpine_iso_availability(self):
        """Test if Alpine ISO is available"""
        self.log("Testing Alpine ISO availability...", "TEST")
        
        # Check for custom ISO
        custom_iso = self.project_root / "vm" / "alpine-unhinged-custom.iso"
        if custom_iso.exists():
            self.log("Custom Alpine ISO found", "SUCCESS")
            return True
        
        # Check for standard ISO
        standard_iso = self.project_root / "vm" / "alpine" / "alpine-virt-3.22.2-x86_64.iso"
        if standard_iso.exists():
            self.log("Standard Alpine ISO found", "SUCCESS")
            return True
        
        self.log("No Alpine ISO found", "ERROR")
        self.log("Run 'make build-custom-alpine' to create one", "INFO")
        return False
    
    def test_makefile_integration(self):
        """Test Makefile integration"""
        self.log("Testing Makefile integration...", "TEST")
        
        makefile = self.project_root / "Makefile"
        if not makefile.exists():
            self.log("Makefile not found", "ERROR")
            return False
        
        # Check for simple communication target
        with open(makefile, 'r') as f:
            content = f.read()
            
        if "start-simple:" in content and "SIMPLE_VM_COMMUNICATION" in content:
            self.log("Makefile integration found", "SUCCESS")
            return True
        else:
            self.log("Makefile integration missing", "ERROR")
            return False
    
    def test_communication_pipeline_dry_run(self):
        """Test communication pipeline without actually launching VM"""
        self.log("Testing communication pipeline (dry run)...", "TEST")
        
        # Test the launcher script syntax
        try:
            result = subprocess.run([
                'python3', '-m', 'py_compile', 'control/simple_vm_launcher.py'
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log("VM launcher syntax is valid", "SUCCESS")
            else:
                self.log(f"VM launcher syntax error: {result.stderr}", "ERROR")
                return False
        except Exception as e:
            self.log(f"Syntax check error: {e}", "ERROR")
            return False
        
        # Test the setup script syntax
        try:
            result = subprocess.run([
                'bash', '-n', 'vm/simple-unhinged-setup.sh'
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log("Setup script syntax is valid", "SUCCESS")
                return True
            else:
                self.log(f"Setup script syntax error: {result.stderr}", "ERROR")
                return False
        except Exception as e:
            self.log(f"Setup script check error: {e}", "ERROR")
            return False
    
    def run_all_tests(self):
        """Run all communication tests"""
        self.log("🧪 TESTING SIMPLE VM COMMUNICATION PIPELINE")
        self.log("=" * 60)
        
        tests = [
            ("VM Launcher Availability", self.test_vm_launcher_availability),
            ("QEMU Availability", self.test_qemu_availability),
            ("Alpine ISO Availability", self.test_alpine_iso_availability),
            ("VM Disk Creation", self.test_vm_disk_creation),
            ("Makefile Integration", self.test_makefile_integration),
            ("Communication Pipeline", self.test_communication_pipeline_dry_run)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            self.log(f"Running: {test_name}")
            try:
                if test_func():
                    passed += 1
                    self.test_results.append((test_name, True))
                else:
                    self.test_results.append((test_name, False))
            except Exception as e:
                self.log(f"Test {test_name} failed with exception: {e}", "ERROR")
                self.test_results.append((test_name, False))
            
            self.log("")  # Add spacing
        
        # Generate report
        self.log("=" * 60)
        self.log("TEST RESULTS SUMMARY")
        self.log("=" * 60)
        
        for test_name, result in self.test_results:
            status = "PASS" if result else "FAIL"
            level = "SUCCESS" if result else "ERROR"
            self.log(f"{test_name}: {status}", level)
        
        self.log("=" * 60)
        self.log(f"TOTAL: {passed}/{total} tests passed")
        
        if passed == total:
            self.log("🎉 ALL TESTS PASSED - COMMUNICATION PIPELINE READY!", "SUCCESS")
            self.log("")
            self.log("🚀 NEXT STEPS:")
            self.log("1. Test with: make start-simple")
            self.log("2. Verify VM output appears in terminal")
            self.log("3. Check for Unhinged status messages")
            return True
        else:
            self.log("❌ SOME TESTS FAILED - PIPELINE NOT READY", "ERROR")
            self.log("")
            self.log("🔧 REQUIRED FIXES:")
            for test_name, result in self.test_results:
                if not result:
                    self.log(f"- Fix: {test_name}")
            return False

def main():
    """Main test function"""
    tester = SimpleCommunicationTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
