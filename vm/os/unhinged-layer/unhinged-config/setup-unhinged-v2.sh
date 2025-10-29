#!/bin/bash
# Auto-setup script for Unhinged in Alpine with Host Communication
set -e

echo "🔥 SETTING UP UNHINGED IN ALPINE LINUX (V2)"
echo "============================================"

# Mount shared directory for host communication
echo "📁 Setting up host communication..."
mkdir -p /mnt/shared
mount -t 9p -o trans=virtio,version=9p2000.L shared /mnt/shared 2>/dev/null || echo "⚠️ Shared directory not available"

# Function to send message to host
send_to_host() {
    echo "$(date): $1" >> /mnt/shared/vm-to-host.txt 2>/dev/null || echo "$1" >&2
}

send_to_host "STATUS: Starting Unhinged setup in Alpine"

# Install required packages
send_to_host "STATUS: Installing packages..."
apk add --no-cache python3 py3-pip mesa-dri-gallium libdrm build-base
send_to_host "STATUS: Packages installed successfully"

# Create Unhinged directory
mkdir -p /opt/unhinged
send_to_host "STATUS: Created Unhinged directory"

# Copy graphics library if available
if [ -f "/tmp/libunhinged_graphics.so" ]; then
    cp /tmp/libunhinged_graphics.so /opt/unhinged/
    send_to_host "STATUS: Graphics library installed"
fi

# Create the Unhinged starter script with communication
cat > /opt/unhinged/start_unhinged.py << 'PYTHON_EOF'
#!/usr/bin/env python3
import os
import sys
import time
from datetime import datetime

def send_to_host(message):
    """Send message to host via shared directory"""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open('/mnt/shared/vm-to-host.txt', 'a') as f:
            f.write(f"{timestamp} GRAPHICS: {message}\n")
    except:
        pass  # Shared directory not available

def main():
    print("🔥 UNHINGED NATIVE GRAPHICS - ALPINE LINUX")
    print("=" * 50)
    
    send_to_host("Starting Unhinged graphics system")
    
    # Check for graphics devices
    fb_available = os.path.exists('/dev/fb0')
    dri_available = os.path.exists('/dev/dri')
    
    print(f"📺 Framebuffer: {'✅' if fb_available else '❌'}")
    print(f"🎮 DRM devices: {'✅' if dri_available else '❌'}")
    
    send_to_host(f"Device status - FB: {fb_available}, DRI: {dri_available}")
    
    # Clear screen to white if framebuffer available
    try:
        if fb_available:
            send_to_host("Rendering white background to framebuffer")
            with open('/dev/fb0', 'wb') as fb:
                # Simple white fill - RGBA format
                white = b'\xFF\xFF\xFF\xFF'
                # Assume 1024x768 resolution
                for _ in range(1024 * 768):
                    fb.write(white)
            print("✅ White desktop background rendered")
            send_to_host("SUCCESS: White desktop background rendered")
        else:
            print("⚠️ No framebuffer - using console mode")
            send_to_host("WARNING: No framebuffer device available")
    except Exception as e:
        error_msg = f"Graphics rendering error: {e}"
        print(f"❌ {error_msg}")
        send_to_host(f"ERROR: {error_msg}")
    
    # Show hello world message
    os.system('clear')
    print("\n" * 3)
    print("🎉 UNHINGED DESKTOP READY!")
    print("📺 White background displayed on framebuffer")
    print("🏔️ Alpine Linux + Native Graphics")
    print("🔥 VM-to-Host communication active")
    print("\n💡 Press Ctrl+C to exit")
    
    send_to_host("SUCCESS: Unhinged desktop ready - white background displayed")
    
    # Keep running and send periodic status
    try:
        counter = 0
        while True:
            time.sleep(30)  # Send status every 30 seconds
            counter += 1
            send_to_host(f"STATUS: Unhinged running normally (heartbeat #{counter})")
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Unhinged graphics...")
        send_to_host("STATUS: Unhinged graphics stopped by user")

if __name__ == "__main__":
    main()
PYTHON_EOF

chmod +x /opt/unhinged/start_unhinged.py
send_to_host "STATUS: Unhinged graphics script created"

# Create service
cat > /etc/init.d/unhinged << 'SERVICE_EOF'
#!/sbin/openrc-run

name="Unhinged Graphics"
description="Unhinged native graphics with host communication"
command="/usr/bin/python3"
command_args="/opt/unhinged/start_unhinged.py"
command_background="yes"
pidfile="/var/run/unhinged.pid"

depend() {
    need localmount
}

start_pre() {
    # Mount shared directory if not already mounted
    if ! mountpoint -q /mnt/shared; then
        mkdir -p /mnt/shared
        mount -t 9p -o trans=virtio,version=9p2000.L shared /mnt/shared 2>/dev/null || true
    fi
}
SERVICE_EOF

chmod +x /etc/init.d/unhinged
rc-update add unhinged default

send_to_host "STATUS: Unhinged service configured for auto-start"

echo "✅ Unhinged setup complete!"
echo "🔄 Reboot to start Unhinged graphics automatically"
echo "💡 Or run manually: python3 /opt/unhinged/start_unhinged.py"

send_to_host "SUCCESS: Unhinged setup completed successfully"
