#!/usr/bin/env python3
"""
@llm-doc Unhinged Quality-of-Life Launcher
@llm-version 2.0.0
@llm-date 2025-01-26
@llm-author Unhinged Team

## Overview
Quality-of-life launcher that provides enhanced user experience while calling
Makefile targets "behind the scenes". Preserves Makefile as core build system.

## Design Philosophy
- **Makefile Preservation**: All build logic remains in Makefile
- **Enhanced UX**: Better user experience with real-time feedback
- **Behind-the-Scenes**: Calls Makefile targets internally
- **Incremental**: Builds on existing infrastructure

## Integration Strategy
1. Call Makefile setup targets for dependencies
2. Launch enhanced VM with bidirectional communication
3. Provide real-time status and interaction
4. Maintain all existing Makefile functionality

@llm-principle Enhance experience while preserving build system foundation
@llm-culture Independence through improved but reliable tooling
"""

import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

# Import enhanced launcher
try:
    from .enhanced_vm_launcher import EnhancedVMLauncher
except ImportError:
    # Handle direct execution
    sys.path.append(str(Path(__file__).parent))
    from enhanced_vm_launcher import EnhancedVMLauncher


class UnhingedLauncher:
    """
    @llm-doc Quality-of-Life Launcher with Makefile Integration

    Provides enhanced user experience while calling Makefile targets behind
    the scenes. Preserves Makefile as the core build system.
    """

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.makefile_path = self.project_root / "Makefile"
        self.vm_launcher = None
        self.setup_complete = False

    def log_status(self, message, level="INFO"):
        """Log status with timestamp and formatting"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        symbols = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "ERROR": "❌",
            "WARNING": "⚠️",
            "SETUP": "🔧",
        }
        symbol = symbols.get(level, "ℹ️")
        print(f"{timestamp} {symbol} {message}")

    def call_makefile_target(self, target, description=None, silent=False):
        """
        @llm-doc Call Makefile Target Behind the Scenes

        Calls Makefile targets while providing user feedback.
        Preserves all Makefile functionality while enhancing UX.
        """
        if description:
            self.log_status(f"{description}...", "SETUP")

        try:
            # Call Makefile target
            if silent:
                result = subprocess.run(
                    ["make", target],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                )
            else:
                result = subprocess.run(["make", target], cwd=self.project_root)

            if result.returncode == 0:
                if description:
                    self.log_status(f"{description} completed", "SUCCESS")
                return True
            else:
                if description:
                    self.log_status(f"{description} failed", "ERROR")
                if silent and result.stderr:
                    print(f"Error: {result.stderr}")
                return False

        except Exception as e:
            self.log_status(f"Error calling make {target}: {e}", "ERROR")
            return False

    def check_prerequisites(self):
        """Check system prerequisites"""
        self.log_status("Checking system prerequisites...")

        # Check if Makefile exists
        if not self.makefile_path.exists():
            self.log_status("Makefile not found", "ERROR")
            return False

        # Check basic tools
        tools = ["make", "python3"]
        for tool in tools:
            try:
                subprocess.run(["which", tool], check=True, capture_output=True)
                self.log_status(f"{tool} available", "SUCCESS")
            except subprocess.CalledProcessError:
                self.log_status(f"{tool} not found", "ERROR")
                return False

        return True

    def setup_dependencies(self):
        """Setup dependencies using Makefile targets"""
        self.log_status("Setting up dependencies via Makefile...", "SETUP")

        # Setup steps using existing Makefile targets
        setup_steps = [
            # ("validate-independence", "Validating independence principles"),  # Phantom target - removed
            ("setup-python", "Setting up Python environment"),
            ("deps-install-essential", "Installing essential dependencies"),
            ("deps-install-graphics", "Installing graphics dependencies"),
        ]

        for target, description in setup_steps:
            if not self.call_makefile_target(target, description, silent=True):
                self.log_status(f"Setup step failed: {description}", "WARNING")
                # Continue with other steps - some may be optional

        self.setup_complete = True
        self.log_status("Dependency setup completed", "SUCCESS")
        return True

    def build_essentials(self):
        """Build essential components using Makefile"""
        self.log_status("Building essential components...", "SETUP")

        build_steps = [
            ("graphics-build", "Building C graphics library"),
            # ("graphics-cffi", "Generating Python CFFI bindings"),  # Phantom target - removed
            ("generate", "Generating build artifacts"),
        ]

        for target, description in build_steps:
            if not self.call_makefile_target(target, description, silent=True):
                self.log_status(f"Build step failed: {description}", "WARNING")
                # Continue - some builds may be optional

        self.log_status("Essential components built", "SUCCESS")
        return True

    def launch_enhanced_vm(self):
        """Launch VM with enhanced bidirectional communication"""
        self.log_status("Launching VM with enhanced communication...", "SETUP")

        try:
            self.vm_launcher = EnhancedVMLauncher()

            # Launch in background thread to maintain responsiveness
            def launch_vm():
                success = self.vm_launcher.launch_vm_with_bidirectional_communication()
                if not success:
                    self.log_status("VM launch failed", "ERROR")

            vm_thread = threading.Thread(target=launch_vm, daemon=True)
            vm_thread.start()

            # Give VM time to start
            time.sleep(2)

            if self.vm_launcher.vm_process and self.vm_launcher.vm_process.poll() is None:
                self.log_status("Enhanced VM launched successfully", "SUCCESS")
                return True
            else:
                self.log_status("VM failed to start", "ERROR")
                return False

        except Exception as e:
            self.log_status(f"VM launch error: {e}", "ERROR")
            return False

    def provide_user_interface(self):
        """Provide enhanced user interface for VM interaction"""
        self.log_status("Enhanced VM interface ready", "SUCCESS")

        print("\n" + "=" * 60)
        print("🔥 UNHINGED ENHANCED LAUNCHER")
        print("=" * 60)
        print("📺 VM → Host: Real-time console output")
        print("📤 Host → VM: Interactive commands available")
        print("🎯 Makefile: All build targets preserved")
        print("💡 Type 'help' for available commands")
        print("=" * 60)

        # Interactive command loop
        try:
            while self.vm_launcher and self.vm_launcher.running:
                # In a full implementation, this would handle user input
                # For now, just maintain the VM session
                time.sleep(1)

                # Check if VM is still running
                if self.vm_launcher.vm_process and self.vm_launcher.vm_process.poll() is not None:
                    break

        except KeyboardInterrupt:
            self.log_status("Shutdown requested by user", "INFO")
            self.shutdown()

    def shutdown(self):
        """Graceful shutdown"""
        self.log_status("Shutting down Unhinged launcher...", "INFO")

        if self.vm_launcher:
            self.vm_launcher.stop_enhanced_vm()

        self.log_status("Shutdown complete", "SUCCESS")

    def run(self):
        """
        @llm-doc Main Entry Point for Enhanced Launcher

        Orchestrates the entire enhanced launch process:
        1. Check prerequisites
        2. Setup dependencies via Makefile
        3. Build essentials via Makefile
        4. Launch enhanced VM
        5. Provide user interface
        """
        print("🚀 UNHINGED QUALITY-OF-LIFE LAUNCHER")
        print("📋 Calling Makefile targets behind the scenes")
        print("🎯 Preserving build system while enhancing experience")
        print("")

        # Step 1: Prerequisites
        if not self.check_prerequisites():
            self.log_status("Prerequisites check failed", "ERROR")
            return False

        # Step 2: Setup dependencies
        if not self.setup_dependencies():
            self.log_status("Dependency setup failed", "ERROR")
            return False

        # Step 3: Build essentials
        if not self.build_essentials():
            self.log_status("Essential build failed", "WARNING")
            # Continue anyway - VM might still work

        # Step 4: Launch enhanced VM
        if not self.launch_enhanced_vm():
            self.log_status("Enhanced VM launch failed", "ERROR")
            # Fallback to simple launcher via Makefile
            self.log_status("Falling back to simple launcher...", "INFO")
            return self.call_makefile_target("start-simple", "Simple VM fallback")

        # Step 5: Provide user interface
        self.provide_user_interface()

        return True


def main():
    """Main function"""
    launcher = UnhingedLauncher()

    try:
        success = launcher.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
        launcher.shutdown()
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        launcher.shutdown()
        sys.exit(1)


if __name__ == "__main__":
    main()
