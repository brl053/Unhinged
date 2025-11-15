#!/usr/bin/env python3
"""
VM Communication Monitor
Monitors communication between QEMU VM and host system
"""

import sys
import time
import json
from pathlib import Path
import threading
import subprocess


class VMMonitor:
    """Monitor VM-to-host communication"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.shared_dir = self.project_root / "vm" / "shared"
        self.serial_log = self.project_root / "vm" / "alpine-serial.log"
        self.running = False

        # Communication files
        self.host_to_vm = self.shared_dir / "host-to-vm.txt"
        self.vm_to_host = self.shared_dir / "vm-to-host.txt"

        # Ensure directories exist
        self.shared_dir.mkdir(exist_ok=True)

    def start_monitoring(self):
        """Start monitoring VM communication"""
        print("🔍 STARTING VM COMMUNICATION MONITOR")
        print("=" * 50)
        print(f"📁 Shared directory: {self.shared_dir}")
        print(f"📋 Serial log: {self.serial_log}")
        print("")

        self.running = True

        # Start monitoring threads
        serial_thread = threading.Thread(target=self.monitor_serial_log, daemon=True)
        vm_messages_thread = threading.Thread(
            target=self.monitor_vm_messages, daemon=True
        )

        serial_thread.start()
        vm_messages_thread.start()

        print("✅ VM monitor started")
        print("💡 Press Ctrl+C to stop")

        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping VM monitor...")
            self.running = False

    def monitor_serial_log(self):
        """Monitor serial console output from VM"""
        if not self.serial_log.exists():
            return

        print("📺 Monitoring serial console...")

        # Follow the log file
        with open(self.serial_log, "r") as f:
            # Go to end of file
            f.seek(0, 2)

            while self.running:
                line = f.readline()
                if line:
                    # Process serial output
                    line = line.strip()
                    if line:
                        print(f"🖥️  SERIAL: {line}")

                        # Look for Unhinged status messages
                        if "UNHINGED" in line:
                            print(f"🔥 UNHINGED: {line}")
                        elif "ERROR" in line or "FAILED" in line:
                            print(f"❌ ERROR: {line}")
                        elif "SUCCESS" in line or "READY" in line:
                            print(f"✅ SUCCESS: {line}")
                else:
                    time.sleep(0.1)

    def monitor_vm_messages(self):
        """Monitor messages from VM via shared directory"""
        print("📨 Monitoring VM messages...")

        last_size = 0

        while self.running:
            try:
                if self.vm_to_host.exists():
                    current_size = self.vm_to_host.stat().st_size

                    if current_size > last_size:
                        # New content available
                        with open(self.vm_to_host, "r") as f:
                            f.seek(last_size)
                            new_content = f.read()

                            if new_content.strip():
                                print(f"📨 VM MESSAGE: {new_content.strip()}")

                                # Try to parse as JSON
                                try:
                                    msg = json.loads(new_content.strip())
                                    self.process_vm_message(msg)
                                except json.JSONDecodeError:
                                    # Plain text message
                                    pass

                        last_size = current_size

                time.sleep(0.5)

            except Exception as e:
                print(f"⚠️ VM message monitor error: {e}")
                time.sleep(1)

    def process_vm_message(self, message):
        """Process structured message from VM"""
        msg_type = message.get("type", "unknown")

        if msg_type == "status":
            status = message.get("status", "unknown")
            print(f"📊 VM STATUS: {status}")

        elif msg_type == "graphics":
            event = message.get("event", "unknown")
            print(f"🎨 GRAPHICS: {event}")

        elif msg_type == "error":
            error = message.get("error", "unknown")
            print(f"❌ VM ERROR: {error}")

        else:
            print(f"📨 VM: {message}")

    def send_to_vm(self, message):
        """Send message to VM via shared directory"""
        try:
            with open(self.host_to_vm, "a") as f:
                if isinstance(message, dict):
                    f.write(json.dumps(message) + "\n")
                else:
                    f.write(str(message) + "\n")

            print(f"📤 SENT TO VM: {message}")
            return True

        except Exception as e:
            print(f"❌ Failed to send to VM: {e}")
            return False

    def get_vm_status(self):
        """Get current VM status"""
        # Check if QEMU is running
        try:
            result = subprocess.run(
                ["pgrep", "-f", "qemu-system-x86_64"], capture_output=True, text=True
            )
            qemu_running = result.returncode == 0
        except:
            qemu_running = False

        # Check shared directory
        shared_accessible = self.shared_dir.exists()

        # Check serial log
        serial_active = self.serial_log.exists() and self.serial_log.stat().st_size > 0

        return {
            "qemu_running": qemu_running,
            "shared_accessible": shared_accessible,
            "serial_active": serial_active,
            "timestamp": time.time(),
        }


def main():
    """Main function"""
    monitor = VMMonitor()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "status":
            status = monitor.get_vm_status()
            print("🔍 VM STATUS:")
            for key, value in status.items():
                print(f"   {key}: {value}")

        elif command == "send":
            if len(sys.argv) > 2:
                message = " ".join(sys.argv[2:])
                monitor.send_to_vm(message)
            else:
                print("Usage: vm_monitor.py send <message>")

        else:
            print("Usage: vm_monitor.py [status|send <message>]")

    else:
        # Start monitoring
        monitor.start_monitoring()


if __name__ == "__main__":
    main()
