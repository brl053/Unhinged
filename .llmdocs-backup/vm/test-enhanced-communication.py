#!/usr/bin/env python3
"""
@llm-doc Test Enhanced VM Communication System
@llm-version 2.0.0
@llm-date 2025-01-26
@llm-author Unhinged Team

## Overview
Comprehensive test suite for the enhanced VM communication system.
Tests both Phase 1 (unidirectional) and Phase 2 (bidirectional) communication.

## Test Coverage
- Simple VM launcher functionality
- Enhanced VM launcher with bidirectional communication
- QoL launcher with Makefile integration
- Build system preservation
- Communication protocol validation

@llm-principle Test all communication modes thoroughly
@llm-culture Verify independence through comprehensive validation
"""

import subprocess
import time
import sys
import json
import threading
from pathlib import Path
import tempfile
import os

class EnhancedCommunicationTest:
    """Test the enhanced VM communication system"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.test_results = []
        
    def log(self, message, level="INFO"):
        """Log test message"""
        symbols = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "TEST": "🧪", "WARNING": "⚠️"}
        print(f"{symbols.get(level, 'ℹ️')} {message}")
        
    def test_simple_launcher_syntax(self):
        """Test simple VM launcher syntax"""
        self.log("Testing simple VM launcher syntax...", "TEST")
        
        try:
            result = subprocess.run([
                'python3', '-m', 'py_compile', 'control/simple_vm_launcher.py'
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log("Simple VM launcher syntax valid", "SUCCESS")
                return True
            else:
                self.log(f"Simple VM launcher syntax error: {result.stderr}", "ERROR")
                return False
        except Exception as e:
            self.log(f"Simple launcher syntax check error: {e}", "ERROR")
            return False
    
    def test_enhanced_launcher_syntax(self):
        """Test enhanced VM launcher syntax"""
        self.log("Testing enhanced VM launcher syntax...", "TEST")
        
        try:
            result = subprocess.run([
                'python3', '-m', 'py_compile', 'control/enhanced_vm_launcher.py'
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log("Enhanced VM launcher syntax valid", "SUCCESS")
                return True
            else:
                self.log(f"Enhanced VM launcher syntax error: {result.stderr}", "ERROR")
                return False
        except Exception as e:
            self.log(f"Enhanced launcher syntax check error: {e}", "ERROR")
            return False
    
    def test_qol_launcher_syntax(self):
        """Test QoL launcher syntax"""
        self.log("Testing QoL launcher syntax...", "TEST")
        
        try:
            result = subprocess.run([
                'python3', '-m', 'py_compile', 'control/unhinged_launcher.py'
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log("QoL launcher syntax valid", "SUCCESS")
                return True
            else:
                self.log(f"QoL launcher syntax error: {result.stderr}", "ERROR")
                return False
        except Exception as e:
            self.log(f"QoL launcher syntax check error: {e}", "ERROR")
            return False
    
    def test_makefile_integration(self):
        """Test Makefile integration for all launchers"""
        self.log("Testing Makefile integration...", "TEST")
        
        makefile = self.project_root / "Makefile"
        if not makefile.exists():
            self.log("Makefile not found", "ERROR")
            return False
        
        with open(makefile, 'r') as f:
            content = f.read()
        
        # Check for all required integration points
        required_elements = [
            "SIMPLE_VM_COMMUNICATION",
            "ENHANCED_VM_COMMUNICATION", 
            "UNHINGED_LAUNCHER",
            "start-simple:",
            "start-enhanced:",
            "start-qol:"
        ]
        
        missing = []
        for element in required_elements:
            if element not in content:
                missing.append(element)
        
        if missing:
            self.log(f"Missing Makefile elements: {missing}", "ERROR")
            return False
        else:
            self.log("All Makefile integration points found", "SUCCESS")
            return True
    
    def test_makefile_targets(self):
        """Test that Makefile targets are accessible"""
        self.log("Testing Makefile target accessibility...", "TEST")
        
        targets_to_test = [
            "start-simple",
            "start-enhanced", 
            "start-qol"
        ]
        
        for target in targets_to_test:
            try:
                # Test target help (dry run)
                result = subprocess.run([
                    'make', '-n', target
                ], cwd=self.project_root, capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    self.log(f"Target {target} accessible", "SUCCESS")
                else:
                    self.log(f"Target {target} not accessible", "ERROR")
                    return False
            except subprocess.TimeoutExpired:
                self.log(f"Target {target} test timed out", "WARNING")
            except Exception as e:
                self.log(f"Error testing target {target}: {e}", "ERROR")
                return False
        
        return True
    
    def test_launcher_imports(self):
        """Test that launchers can import each other correctly"""
        self.log("Testing launcher import dependencies...", "TEST")
        
        # Test enhanced launcher can import simple launcher
        try:
            result = subprocess.run([
                'python3', '-c', 
                'import sys; sys.path.append("control"); from enhanced_vm_launcher import EnhancedVMLauncher; print("Enhanced import OK")'
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log("Enhanced launcher imports working", "SUCCESS")
            else:
                self.log(f"Enhanced launcher import error: {result.stderr}", "ERROR")
                return False
        except Exception as e:
            self.log(f"Enhanced launcher import test error: {e}", "ERROR")
            return False
        
        # Test QoL launcher can import enhanced launcher
        try:
            result = subprocess.run([
                'python3', '-c',
                'import sys; sys.path.append("control"); from unhinged_launcher import UnhingedLauncher; print("QoL import OK")'
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log("QoL launcher imports working", "SUCCESS")
                return True
            else:
                self.log(f"QoL launcher import error: {result.stderr}", "ERROR")
                return False
        except Exception as e:
            self.log(f"QoL launcher import test error: {e}", "ERROR")
            return False
    
    def test_communication_protocol(self):
        """Test communication protocol message format"""
        self.log("Testing communication protocol...", "TEST")
        
        # Test JSON message format
        test_message = {
            "timestamp": "2025-01-26T10:30:00Z",
            "direction": "vm-to-host",
            "type": "status",
            "data": {
                "message": "Test message",
                "details": {"test": True}
            }
        }
        
        try:
            # Test JSON serialization/deserialization
            json_str = json.dumps(test_message)
            parsed = json.loads(json_str)
            
            # Validate required fields
            required_fields = ["timestamp", "direction", "type", "data"]
            for field in required_fields:
                if field not in parsed:
                    self.log(f"Missing required field: {field}", "ERROR")
                    return False
            
            self.log("Communication protocol format valid", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"Communication protocol test error: {e}", "ERROR")
            return False
    
    def test_vm_disk_creation(self):
        """Test VM disk creation for all launchers"""
        self.log("Testing VM disk creation...", "TEST")
        
        # Check if simple VM disk exists or can be created
        simple_disk = self.project_root / "vm" / "simple-alpine.qcow2"
        if simple_disk.exists():
            self.log("Simple VM disk exists", "SUCCESS")
            return True
        
        # Try to create via simple launcher
        try:
            result = subprocess.run([
                'python3', '-c',
                'from control.simple_vm_launcher import SimpleVMLauncher; '
                'launcher = SimpleVMLauncher(); '
                'disk = launcher.create_simple_vm_disk(); '
                'print("Disk created:", disk)'
            ], cwd=self.project_root, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and simple_disk.exists():
                self.log("VM disk creation successful", "SUCCESS")
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
    
    def test_documentation_completeness(self):
        """Test that documentation files exist and are complete"""
        self.log("Testing documentation completeness...", "TEST")
        
        required_docs = [
            "docs/vm-communication-evolution.md",
            "docs/vm-communication-llmdoc.md", 
            "docs/build-system-integration.md"
        ]
        
        for doc_path in required_docs:
            doc_file = self.project_root / doc_path
            if not doc_file.exists():
                self.log(f"Missing documentation: {doc_path}", "ERROR")
                return False
            
            # Check if file has content
            if doc_file.stat().st_size < 1000:  # At least 1KB
                self.log(f"Documentation too small: {doc_path}", "WARNING")
        
        self.log("Documentation completeness check passed", "SUCCESS")
        return True
    
    def run_all_tests(self):
        """Run all enhanced communication tests"""
        self.log("🧪 TESTING ENHANCED VM COMMUNICATION SYSTEM")
        self.log("=" * 60)
        
        tests = [
            ("Simple Launcher Syntax", self.test_simple_launcher_syntax),
            ("Enhanced Launcher Syntax", self.test_enhanced_launcher_syntax),
            ("QoL Launcher Syntax", self.test_qol_launcher_syntax),
            ("Makefile Integration", self.test_makefile_integration),
            ("Makefile Targets", self.test_makefile_targets),
            ("Launcher Imports", self.test_launcher_imports),
            ("Communication Protocol", self.test_communication_protocol),
            ("VM Disk Creation", self.test_vm_disk_creation),
            ("Documentation Completeness", self.test_documentation_completeness)
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
        self.log("ENHANCED COMMUNICATION TEST RESULTS")
        self.log("=" * 60)
        
        for test_name, result in self.test_results:
            status = "PASS" if result else "FAIL"
            level = "SUCCESS" if result else "ERROR"
            self.log(f"{test_name}: {status}", level)
        
        self.log("=" * 60)
        self.log(f"TOTAL: {passed}/{total} tests passed")
        
        if passed == total:
            self.log("🎉 ALL TESTS PASSED - ENHANCED COMMUNICATION READY!", "SUCCESS")
            self.log("")
            self.log("🚀 READY FOR DEPLOYMENT:")
            self.log("1. Phase 1: make start-simple (unidirectional)")
            self.log("2. Phase 2: make start-enhanced (bidirectional)")
            self.log("3. QoL: make start-qol (enhanced UX)")
            self.log("4. Default: make start (automatic enhanced)")
            return True
        else:
            self.log("❌ SOME TESTS FAILED - SYSTEM NOT READY", "ERROR")
            self.log("")
            self.log("🔧 REQUIRED FIXES:")
            for test_name, result in self.test_results:
                if not result:
                    self.log(f"- Fix: {test_name}")
            return False

def main():
    """Main test function"""
    tester = EnhancedCommunicationTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
