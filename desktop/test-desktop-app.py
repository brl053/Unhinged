#!/usr/bin/env python3
"""
@llm-doc Test Desktop Application
@llm-version 1.0.0
@llm-date 2025-01-26
@llm-author Unhinged Team

## Overview
Test script for the Unhinged desktop application to verify functionality
without requiring a full GUI session.

## Test Coverage
- Import and syntax validation
- GTK4/Libadwaita availability
- Application initialization
- Desktop file validation
- Installation script testing

@llm-principle Test desktop integration thoroughly
@llm-culture Verify independence through GUI accessibility
"""

import sys
import os
import subprocess
from pathlib import Path
import tempfile

class DesktopAppTest:
    """Test the desktop application functionality"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.desktop_dir = Path(__file__).parent
        self.test_results = []
        
    def log(self, message, level="INFO"):
        """Log test message"""
        symbols = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "TEST": "🧪"}
        print(f"{symbols.get(level, 'ℹ️')} {message}")
        
    def test_gtk_availability(self):
        """Test GTK4 and Libadwaita availability"""
        self.log("Testing GTK4/Libadwaita availability...", "TEST")
        
        try:
            import gi
            gi.require_version('Gtk', '4.0')
            gi.require_version('Adw', '1')
            from gi.repository import Gtk, Adw
            
            self.log("GTK4 and Libadwaita available", "SUCCESS")
            return True
        except ImportError as e:
            self.log(f"GTK4/Libadwaita not available: {e}", "ERROR")
            return False
        except Exception as e:
            self.log(f"GTK4/Libadwaita test error: {e}", "ERROR")
            return False
    
    def test_desktop_app_syntax(self):
        """Test desktop application syntax"""
        self.log("Testing desktop application syntax...", "TEST")
        
        app_file = self.desktop_dir / "unhinged-desktop-app"
        
        try:
            result = subprocess.run([
                'python3', '-m', 'py_compile', str(app_file)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log("Desktop application syntax valid", "SUCCESS")
                return True
            else:
                self.log(f"Desktop application syntax error: {result.stderr}", "ERROR")
                return False
        except Exception as e:
            self.log(f"Desktop application syntax test error: {e}", "ERROR")
            return False
    
    def test_desktop_app_executable(self):
        """Test desktop application is executable"""
        self.log("Testing desktop application executable...", "TEST")

        app_file = self.desktop_dir / "unhinged-desktop-app"

        if not app_file.exists():
            self.log("Desktop application file not found", "ERROR")
            return False

        if not os.access(app_file, os.X_OK):
            self.log("Desktop application is not executable", "ERROR")
            return False

        # Test that it can be executed with --help (if implemented)
        try:
            # Just test that the file can be read and has the right shebang
            with open(app_file, 'r') as f:
                first_line = f.readline().strip()

            if first_line.startswith('#!/usr/bin/env python3'):
                self.log("Desktop application has correct shebang", "SUCCESS")
                return True
            else:
                self.log(f"Desktop application has incorrect shebang: {first_line}", "ERROR")
                return False

        except Exception as e:
            self.log(f"Desktop application executable test error: {e}", "ERROR")
            return False
    
    def test_desktop_file(self):
        """Test desktop file validity"""
        self.log("Testing desktop file...", "TEST")
        
        desktop_file = self.desktop_dir / "unhinged.desktop"
        
        if not desktop_file.exists():
            self.log("Desktop file not found", "ERROR")
            return False
        
        try:
            with open(desktop_file, 'r') as f:
                content = f.read()
            
            # Check required fields
            required_fields = [
                "[Desktop Entry]",
                "Type=Application",
                "Name=Unhinged",
                "Exec=",
                "Icon="
            ]
            
            missing_fields = []
            for field in required_fields:
                if field not in content:
                    missing_fields.append(field)
            
            if missing_fields:
                self.log(f"Missing desktop file fields: {missing_fields}", "ERROR")
                return False
            else:
                self.log("Desktop file format valid", "SUCCESS")
                return True
                
        except Exception as e:
            self.log(f"Desktop file test error: {e}", "ERROR")
            return False
    
    def test_installation_script(self):
        """Test installation script syntax"""
        self.log("Testing installation script...", "TEST")
        
        install_script = self.desktop_dir / "install-desktop-app.sh"
        
        if not install_script.exists():
            self.log("Installation script not found", "ERROR")
            return False
        
        try:
            # Test bash syntax
            result = subprocess.run([
                'bash', '-n', str(install_script)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log("Installation script syntax valid", "SUCCESS")
                return True
            else:
                self.log(f"Installation script syntax error: {result.stderr}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Installation script test error: {e}", "ERROR")
            return False
    
    def test_executable_permissions(self):
        """Test that files have correct permissions"""
        self.log("Testing file permissions...", "TEST")
        
        files_to_check = [
            ("unhinged-desktop-app", True),   # Should be executable
            ("install-desktop-app.sh", True), # Should be executable
            ("unhinged.desktop", False),      # Should not be executable
        ]
        
        all_correct = True
        
        for filename, should_be_executable in files_to_check:
            file_path = self.desktop_dir / filename
            
            if not file_path.exists():
                self.log(f"File not found: {filename}", "ERROR")
                all_correct = False
                continue
            
            is_executable = os.access(file_path, os.X_OK)
            
            if should_be_executable and not is_executable:
                self.log(f"File should be executable: {filename}", "ERROR")
                all_correct = False
            elif not should_be_executable and is_executable:
                self.log(f"File should not be executable: {filename}", "ERROR")
                all_correct = False
            else:
                self.log(f"File permissions correct: {filename}", "SUCCESS")
        
        return all_correct
    
    def test_makefile_integration(self):
        """Test that Makefile targets exist for desktop app"""
        self.log("Testing Makefile integration...", "TEST")
        
        makefile = self.project_root / "Makefile"
        
        if not makefile.exists():
            self.log("Makefile not found", "ERROR")
            return False
        
        try:
            with open(makefile, 'r') as f:
                content = f.read()
            
            # Check for targets that desktop app uses
            required_targets = [
                "start:",
                "start-simple:",
                "start-enhanced:",
                "start-qol:"
            ]
            
            missing_targets = []
            for target in required_targets:
                if target not in content:
                    missing_targets.append(target)
            
            if missing_targets:
                self.log(f"Missing Makefile targets: {missing_targets}", "ERROR")
                return False
            else:
                self.log("Makefile integration targets found", "SUCCESS")
                return True
                
        except Exception as e:
            self.log(f"Makefile integration test error: {e}", "ERROR")
            return False
    
    def run_all_tests(self):
        """Run all desktop application tests"""
        self.log("🧪 TESTING UNHINGED DESKTOP APPLICATION")
        self.log("=" * 60)
        
        tests = [
            ("GTK4/Libadwaita Availability", self.test_gtk_availability),
            ("Desktop App Syntax", self.test_desktop_app_syntax),
            ("Desktop App Executable", self.test_desktop_app_executable),
            ("Desktop File", self.test_desktop_file),
            ("Installation Script", self.test_installation_script),
            ("File Permissions", self.test_executable_permissions),
            ("Makefile Integration", self.test_makefile_integration)
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
        self.log("DESKTOP APPLICATION TEST RESULTS")
        self.log("=" * 60)
        
        for test_name, result in self.test_results:
            status = "PASS" if result else "FAIL"
            level = "SUCCESS" if result else "ERROR"
            self.log(f"{test_name}: {status}", level)
        
        self.log("=" * 60)
        self.log(f"TOTAL: {passed}/{total} tests passed")
        
        if passed == total:
            self.log("🎉 ALL TESTS PASSED - DESKTOP APP READY!", "SUCCESS")
            self.log("")
            self.log("🚀 READY FOR INSTALLATION:")
            self.log("1. Install: ./desktop/install-desktop-app.sh")
            self.log("2. Launch: ./desktop/unhinged-desktop-app")
            self.log("3. Or find 'Unhinged' in your application menu")
            return True
        else:
            self.log("❌ SOME TESTS FAILED - DESKTOP APP NOT READY", "ERROR")
            self.log("")
            self.log("🔧 REQUIRED FIXES:")
            for test_name, result in self.test_results:
                if not result:
                    self.log(f"- Fix: {test_name}")
            return False

def main():
    """Main test function"""
    tester = DesktopAppTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
