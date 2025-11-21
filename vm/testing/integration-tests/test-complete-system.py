#!/usr/bin/env python3
"""
@llm-type component
@llm-does system component
"""

"""
Complete System Test for Unhinged Alpine VM
Tests the entire voice-first GUI experience with Alpine VM rendering
"""

import sys
from pathlib import Path

import requests

# Add control/gtk4_gui/utils to path for subprocess_utils import
sys.path.insert(
    0,
    str(Path(__file__).parent.parent.parent.parent / "control" / "gtk4_gui" / "utils"),
)

from subprocess_utils import SubprocessRunner


class UnhingedSystemTest:
    """Complete system test for Unhinged with Alpine VM"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.test_results = {}

    def log(self, message, status="INFO"):
        """Log test message"""
        symbols = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "ERROR": "❌",
            "WARNING": "⚠️",
            "TEST": "🧪",
        }
        print(f"{symbols.get(status, 'ℹ️')} {message}")

    def run_command(self, command, timeout=30, check=True):
        """Run shell command and return result"""
        runner = SubprocessRunner(timeout=timeout)
        result = runner.run_shell(command, cwd=self.project_root)
        return {
            "success": result["success"] if check else True,
            "stdout": result["output"],
            "stderr": result["error"],
            "returncode": result["returncode"],
        }

    def test_prerequisites(self):
        """Test system prerequisites"""
        self.log("Testing system prerequisites...", "TEST")

        tests = [
            ("QEMU installed", "which qemu-system-x86_64"),
            ("Python 3 available", "python3 --version"),
            (
                "Graphics library built",
                "test -f libs/graphics/build/libunhinged_graphics.so",
            ),
            (
                "Alpine ISO downloaded",
                "test -f vm/alpine/alpine-virt-3.22.2-x86_64.iso",
            ),
            (
                "Python wrapper created",
                "test -f libs/graphics/python/unhinged_graphics.py",
            ),
        ]

        all_passed = True
        for test_name, command in tests:
            result = self.run_command(command)
            if result["success"]:
                self.log(f"{test_name}: PASS", "SUCCESS")
            else:
                self.log(f"{test_name}: FAIL", "ERROR")
                all_passed = False

        self.test_results["prerequisites"] = all_passed
        return all_passed

    def test_graphics_library(self):
        """Test Unhinged graphics library"""
        self.log("Testing Unhinged graphics library...", "TEST")

        # Test Python wrapper
        result = self.run_command("python3 libs/graphics/python/unhinged_graphics.py")
        if result["success"]:
            self.log("Python graphics wrapper: PASS", "SUCCESS")
            graphics_working = True
        else:
            self.log("Python graphics wrapper: FAIL", "ERROR")
            self.log(f"Error: {result.get('stderr', 'Unknown error')}")
            graphics_working = False

        # Test native hello_world
        if Path("libs/graphics/build/examples/hello_world").exists():
            result = self.run_command("timeout 5s libs/graphics/build/examples/hello_world", check=False)
            if result["returncode"] in [
                0,
                124,
            ]:  # 0 = success, 124 = timeout (expected)
                self.log("Native hello_world: PASS", "SUCCESS")
            else:
                self.log("Native hello_world: FAIL", "WARNING")

        self.test_results["graphics_library"] = graphics_working
        return graphics_working

    def test_alpine_vm_creation(self):
        """Test Alpine VM disk creation"""
        self.log("Testing Alpine VM disk creation...", "TEST")

        # Check if VM disk exists or create it
        vm_disk = Path("vm/alpine-unhinged.qcow2")
        if vm_disk.exists():
            self.log("Alpine VM disk already exists", "SUCCESS")
            disk_created = True
        else:
            self.log("Creating Alpine VM disk...")
            result = self.run_command(
                'python3 -c "from control.qemu_vm_launcher import QEMULauncher; q = QEMULauncher(); q.create_alpine_vm_disk()"'
            )
            disk_created = result["success"] and vm_disk.exists()

            if disk_created:
                self.log("Alpine VM disk created successfully", "SUCCESS")
            else:
                self.log("Failed to create Alpine VM disk", "ERROR")

        self.test_results["alpine_vm_creation"] = disk_created
        return disk_created

    def test_voice_services(self):
        """Test voice transcription services"""
        self.log("Testing voice transcription services...", "TEST")

        # Check if Whisper server is running
        try:
            response = requests.get("http://localhost:1101/health", timeout=5)
            if response.status_code == 200:
                self.log("Whisper service: RUNNING", "SUCCESS")
                voice_working = True
            else:
                self.log("Whisper service: NOT RESPONDING", "WARNING")
                voice_working = False
        except requests.exceptions.RequestException:
            self.log("Whisper service: NOT RUNNING", "WARNING")
            self.log("💡 Start with: python3 services/speech-to-text/simple_whisper_server.py")
            voice_working = False

        self.test_results["voice_services"] = voice_working
        return voice_working

    def test_deployment_readiness(self):
        """Test if system is ready for Alpine deployment"""
        self.log("Testing deployment readiness...", "TEST")

        # Check deployment script
        deploy_script = Path("vm/deploy-to-alpine.sh")
        if deploy_script.exists() and deploy_script.is_file():
            self.log("Deployment script: READY", "SUCCESS")
            deploy_ready = True
        else:
            self.log("Deployment script: MISSING", "ERROR")
            deploy_ready = False

        # Check configuration script
        config_script = Path("vm/alpine-configure.sh")
        if config_script.exists() and config_script.is_file():
            self.log("Configuration script: READY", "SUCCESS")
        else:
            self.log("Configuration script: MISSING", "ERROR")
            deploy_ready = False

        self.test_results["deployment_readiness"] = deploy_ready
        return deploy_ready

    def generate_report(self):
        """Generate test report"""
        self.log("=" * 60)
        self.log("UNHINGED ALPINE VM SYSTEM TEST REPORT", "INFO")
        self.log("=" * 60)

        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)

        for test_name, result in self.test_results.items():
            status = "PASS" if result else "FAIL"
            status_symbol = "✅" if result else "❌"
            self.log(
                f"{test_name.replace('_', ' ').title()}: {status}",
                "SUCCESS" if result else "ERROR",
            )

        self.log("=" * 60)
        self.log(f"SUMMARY: {passed_tests}/{total_tests} tests passed")

        if passed_tests == total_tests:
            self.log("🎉 ALL TESTS PASSED - SYSTEM READY!", "SUCCESS")
            self.log("")
            self.log("🚀 NEXT STEPS:")
            self.log("1. Install Alpine: make alpine-install")
            self.log("2. Deploy Unhinged: make alpine-deploy")
            self.log("3. Run Alpine VM: make alpine-run")
            self.log("4. Start bridge: make alpine-bridge")
            return True
        else:
            self.log("❌ SOME TESTS FAILED - SYSTEM NOT READY", "ERROR")
            self.log("")
            self.log("🔧 REQUIRED FIXES:")
            for test_name, result in self.test_results.items():
                if not result:
                    self.log(f"- Fix {test_name.replace('_', ' ')}")
            return False

    def run_all_tests(self):
        """Run all system tests"""
        self.log("🧪 STARTING COMPLETE SYSTEM TEST")
        self.log("=" * 60)

        # Run all tests
        tests = [
            self.test_prerequisites,
            self.test_graphics_library,
            self.test_alpine_vm_creation,
            self.test_voice_services,
            self.test_deployment_readiness,
        ]

        for test in tests:
            test()
            self.log("")  # Add spacing between tests

        # Generate final report
        return self.generate_report()


def main():
    """Main test function"""
    tester = UnhingedSystemTest()
    success = tester.run_all_tests()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
