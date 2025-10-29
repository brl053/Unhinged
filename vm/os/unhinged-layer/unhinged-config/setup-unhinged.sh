#!/bin/bash
# Auto-setup script for Unhinged in Alpine
set -e

echo "🔥 SETTING UP UNHINGED IN ALPINE LINUX"
echo "============================================"

# Mount shared directory for host communication
echo "📁 Setting up host communication..."
mkdir -p /mnt/shared
mount -t 9p -o trans=virtio,version=9p2000.L shared /mnt/shared 2>/dev/null || echo "⚠️ Shared directory not available"

# Function to send message to host
send_to_host() {
    echo "$1" >> /mnt/shared/vm-to-host.txt 2>/dev/null || echo "$1" >&2
}

send_to_host "STATUS: Starting Unhinged setup in Alpine"

# Install required packages
send_to_host "STATUS: Installing packages..."
apk add --no-cache python3 py3-pip mesa-dri-gallium libdrm build-base
send_to_host "STATUS: Packages installed successfully"

# Create Unhinged directory
mkdir -p /opt/unhinged

# Copy graphics library if available
if [ -f "/tmp/libunhinged_graphics.so" ]; then
    cp /tmp/libunhinged_graphics.so /opt/unhinged/
    echo "✅ Graphics library installed"
fi

# Create the Unhinged starter script
cat > /opt/unhinged/start_unhinged.py << 'PYTHON_EOF'
#!/usr/bin/env python3
import os
import sys
import time

def main():
    print("🔥 UNHINGED NATIVE GRAPHICS - ALPINE LINUX")
    print("=" * 50)

    # Clear screen to white if framebuffer available
    try:
        if os.path.exists('/dev/fb0'):
            with open('/dev/fb0', 'wb') as fb:
                # Simple white fill
                white = b'\xFF\xFF\xFF\xFF'
                for _ in range(1024 * 768):
                    fb.write(white)
            print("✅ White desktop background rendered")
        else:
            print("⚠️ No framebuffer - using console mode")
    except Exception as e:
        print(f"⚠️ Graphics error: {e}")

    # Show hello world
    os.system('clear')
    print("\n" * 5)
    print("🎉 UNHINGED DESKTOP READY!")
    print("📺 White background displayed")
    print("🏔️ Alpine Linux + Native Graphics")
    print("\n💡 Press Ctrl+C to exit")

    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n🛑 Goodbye!")

if __name__ == "__main__":
    main()
PYTHON_EOF

chmod +x /opt/unhinged/start_unhinged.py

# Create service
cat > /etc/init.d/unhinged << 'SERVICE_EOF'
#!/sbin/openrc-run

name="Unhinged Graphics"
command="/usr/bin/python3"
command_args="/opt/unhinged/start_unhinged.py"
command_background="yes"
pidfile="/var/run/unhinged.pid"

depend() {
    need localmount
}
SERVICE_EOF

chmod +x /etc/init.d/unhinged
rc-update add unhinged default

echo "✅ Unhinged setup complete!"
echo "🔄 Reboot to start Unhinged graphics automatically"
