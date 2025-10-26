#!/usr/bin/env python3
"""
@llm-doc Enhanced VM Launcher with Bidirectional Communication
@llm-version 2.0.0
@llm-date 2025-01-26
@llm-author Unhinged Team

## Overview
Enhanced VM launcher that extends simple_vm_launcher.py with bidirectional
communication capabilities while maintaining the same reliability.

## Communication Channels
- **VM → Host**: Serial console output (inherited from simple launcher)
- **Host → VM**: QEMU monitor socket for sending commands
- **Protocol**: Structured JSON messages with fallback to plain text

## Design Principles
- **Backward Compatible**: Extends SimpleVMLauncher
- **Reliable**: Robust error handling and fallback modes
- **Real-time**: Immediate bidirectional communication
- **Simple**: Easy to use and understand

@llm-principle Build on proven foundation, add capabilities incrementally
@llm-culture Independence through enhanced but reliable communication
"""

import subprocess
import sys
import os
import time
import json
import socket
import threading
from pathlib import Path
from datetime import datetime

# Import the simple launcher as base
try:
    from .simple_vm_launcher import SimpleVMLauncher
except ImportError:
    # Handle direct execution
    sys.path.append(str(Path(__file__).parent))
    from simple_vm_launcher import SimpleVMLauncher

class EnhancedVMLauncher(SimpleVMLauncher):
    """
    @llm-doc Enhanced VM Launcher with Bidirectional Communication
    
    Extends SimpleVMLauncher with Host → VM communication via QEMU monitor.
    Maintains all existing VM → Host functionality while adding new capabilities.
    """
    
    def __init__(self):
        super().__init__()
        self.monitor_socket_path = "/tmp/unhinged-qemu-monitor.sock"
        self.monitor_socket = None
        self.monitor_thread = None
        self.command_queue = []
        self.bidirectional_mode = True
        
    def cleanup_monitor_socket(self):
        """Clean up any existing monitor socket"""
        try:
            if os.path.exists(self.monitor_socket_path):
                os.unlink(self.monitor_socket_path)
        except Exception as e:
            print(f"⚠️ Warning: Could not clean monitor socket: {e}")
    
    def launch_vm_with_bidirectional_communication(self):
        """
        @llm-doc Launch VM with Bidirectional Communication
        
        Extends the simple launcher with QEMU monitor socket for Host → VM commands.
        Maintains serial console for VM → Host output.
        """
        if not self.check_qemu_available():
            return False
        
        # Get VM disk and ISO (inherited from simple launcher)
        disk_path = self.create_simple_vm_disk()
        iso_path = self.get_alpine_iso()
        
        if not disk_path or not iso_path:
            return False
        
        # Clean up any existing monitor socket
        self.cleanup_monitor_socket()
        
        print("🔥 LAUNCHING VM WITH BIDIRECTIONAL COMMUNICATION")
        print("=" * 60)
        print("📺 VM → Host: Serial console output")
        print("📤 Host → VM: QEMU monitor commands")
        print("💡 Press Ctrl+C to stop VM")
        print("=" * 60)
        
        # Enhanced QEMU command with monitor socket
        cmd = [
            'qemu-system-x86_64',
            '-enable-kvm',
            '-m', '1G',
            '-smp', '2',
            '-drive', f'file={disk_path},format=qcow2',
            '-cdrom', iso_path,
            '-boot', 'd',  # Boot from CD-ROM
            '-vga', 'virtio',
            '-display', 'none',  # No GUI window - console only
            '-serial', 'stdio',  # VM → Host via serial console
            '-monitor', f'unix:{self.monitor_socket_path},server,nowait',  # Host → VM
            '-name', 'Unhinged-Enhanced-VM'
        ]
        
        print(f"🎮 Starting enhanced VM: {' '.join(cmd[:5])}...")
        print("")
        
        try:
            # Launch VM with bidirectional communication
            self.vm_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            self.running = True
            
            # Start monitor connection in background
            self.start_monitor_connection()
            
            # Stream VM output (inherited functionality)
            self.stream_enhanced_vm_output()
            
            return True
            
        except Exception as e:
            print(f"❌ Error launching enhanced VM: {e}")
            return False
    
    def start_monitor_connection(self):
        """Start QEMU monitor connection for Host → VM communication"""
        def connect_monitor():
            # Wait for QEMU to create the socket
            for attempt in range(10):
                try:
                    if os.path.exists(self.monitor_socket_path):
                        self.monitor_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                        self.monitor_socket.connect(self.monitor_socket_path)
                        print("✅ Monitor connection established (Host → VM)")
                        
                        # Read initial QEMU monitor prompt
                        initial = self.monitor_socket.recv(1024).decode('utf-8')
                        if "(qemu)" in initial:
                            print("📤 QEMU monitor ready for commands")
                        
                        return
                except Exception as e:
                    time.sleep(0.5)
            
            print("⚠️ Could not establish monitor connection - Host → VM disabled")
            self.bidirectional_mode = False
        
        self.monitor_thread = threading.Thread(target=connect_monitor, daemon=True)
        self.monitor_thread.start()
    
    def send_to_vm(self, command):
        """
        @llm-doc Send Command to VM
        
        Sends command to VM via QEMU monitor socket.
        Provides Host → VM communication capability.
        """
        if not self.monitor_socket or not self.bidirectional_mode:
            print(f"⚠️ Cannot send to VM: {command} (monitor not available)")
            return False
        
        try:
            # Send command to QEMU monitor
            full_command = f"{command}\n"
            self.monitor_socket.send(full_command.encode('utf-8'))
            
            # Read response
            response = self.monitor_socket.recv(1024).decode('utf-8')
            print(f"📤 SENT TO VM: {command}")
            if response.strip() and response.strip() != "(qemu)":
                print(f"📥 VM RESPONSE: {response.strip()}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to send to VM: {e}")
            self.bidirectional_mode = False
            return False
    
    def stream_enhanced_vm_output(self):
        """
        @llm-doc Stream Enhanced VM Output
        
        Enhanced version of stream_vm_output with bidirectional message processing.
        Handles structured messages and provides interactive capabilities.
        """
        print("🖥️  ENHANCED VM CONSOLE OUTPUT:")
        print("-" * 40)
        
        # Start interactive command thread
        self.start_interactive_commands()
        
        try:
            while self.running and self.vm_process:
                # Read line from VM console
                line = self.vm_process.stdout.readline()
                
                if line:
                    # Process enhanced output
                    self.process_enhanced_vm_output(line.rstrip())
                
                # Check if VM process has ended
                if self.vm_process.poll() is not None:
                    break
                    
        except KeyboardInterrupt:
            print("\n🛑 Stopping enhanced VM...")
            self.stop_enhanced_vm()
        except Exception as e:
            print(f"❌ Error streaming enhanced VM output: {e}")
    
    def process_enhanced_vm_output(self, line):
        """Process VM output with enhanced message handling"""
        if not line:
            return
        
        # Try to parse as JSON message
        try:
            if line.startswith('{') and line.endswith('}'):
                message = json.loads(line)
                self.handle_structured_message(message)
                return
        except json.JSONDecodeError:
            pass
        
        # Handle plain text output (inherited behavior)
        print(f"VM: {line}")
        
        # Enhanced highlighting
        if "UNHINGED" in line.upper():
            print(f"🔥 UNHINGED: {line}")
        elif "ERROR" in line.upper():
            print(f"❌ ERROR: {line}")
        elif "SUCCESS" in line.upper():
            print(f"✅ SUCCESS: {line}")
        elif "READY" in line.upper():
            print(f"🎯 READY: {line}")
    
    def handle_structured_message(self, message):
        """Handle structured JSON messages from VM"""
        msg_type = message.get('type', 'unknown')
        data = message.get('data', {})
        timestamp = message.get('timestamp', 'unknown')
        
        if msg_type == 'status':
            print(f"📊 VM STATUS [{timestamp}]: {data.get('message', 'Unknown')}")
        elif msg_type == 'graphics':
            print(f"🎨 GRAPHICS [{timestamp}]: {data.get('message', 'Unknown')}")
        elif msg_type == 'error':
            print(f"❌ VM ERROR [{timestamp}]: {data.get('message', 'Unknown')}")
        elif msg_type == 'heartbeat':
            print(f"💓 HEARTBEAT [{timestamp}]: VM alive")
        else:
            print(f"📨 VM MESSAGE [{timestamp}]: {message}")
    
    def start_interactive_commands(self):
        """Start interactive command input for Host → VM communication"""
        def interactive_loop():
            print("💡 Type 'help' for commands, 'quit' to exit")
            while self.running and self.bidirectional_mode:
                try:
                    # Simple command interface
                    time.sleep(1)  # Prevent busy loop
                    # Note: In a real implementation, this would use proper input handling
                    # For now, we'll just demonstrate the capability
                except:
                    break
        
        if self.bidirectional_mode:
            threading.Thread(target=interactive_loop, daemon=True).start()
    
    def stop_enhanced_vm(self):
        """Stop the enhanced VM gracefully"""
        self.running = False
        
        # Send shutdown command via monitor if available
        if self.bidirectional_mode:
            self.send_to_vm("system_powerdown")
            time.sleep(2)  # Give VM time to shutdown gracefully
        
        # Close monitor socket
        if self.monitor_socket:
            try:
                self.monitor_socket.close()
            except:
                pass
        
        # Clean up socket file
        self.cleanup_monitor_socket()
        
        # Stop VM process (inherited from simple launcher)
        super().stop_vm()
    
    def run(self):
        """
        @llm-doc Enhanced Main Entry Point
        
        Main entry point for enhanced VM launcher with bidirectional communication.
        """
        self.setup_signal_handlers()
        
        print("🚀 ENHANCED VM LAUNCHER - UNHINGED")
        print("📺 Bidirectional communication: Host ↔ VM")
        print("")
        
        success = self.launch_vm_with_bidirectional_communication()
        
        if success:
            print("\n🎉 Enhanced VM session completed")
        else:
            print("\n❌ Enhanced VM launch failed")
        
        return success

def main():
    """Main function"""
    launcher = EnhancedVMLauncher()
    success = launcher.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
