#!/bin/bash
# Alpine Linux Configuration Script for Unhinged
# Run this script INSIDE the Alpine VM after basic installation

set -e

echo "🏔️ ALPINE LINUX CONFIGURATION FOR UNHINGED"
echo "=" * 60

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run as root"
    exit 1
fi

echo "📦 Updating Alpine packages..."
apk update
apk upgrade

echo "🔧 Installing build tools and dependencies..."
apk add \
    build-base \
    cmake \
    git \
    python3 \
    python3-dev \
    py3-pip \
    linux-headers \
    mesa-dev \
    libdrm-dev \
    eudev-dev \
    pkgconfig \
    gcc \
    musl-dev \
    curl \
    wget

echo "🎮 Installing DRM and graphics drivers..."
apk add \
    mesa-dri-gallium \
    mesa-va-gallium \
    mesa-vdpau-gallium \
    xf86-video-qxl \
    libdrm \
    linux-firmware-amdgpu \
    linux-firmware-radeon \
    linux-firmware-i915

echo "👤 Adding root to video group for DRM access..."
addgroup root video

echo "🖥️ Configuring framebuffer console..."
if [ -f /etc/default/grub ]; then
    echo 'GRUB_CMDLINE_LINUX_DEFAULT="quiet console=tty0 console=ttyS0,115200"' >> /etc/default/grub
    update-grub
fi

echo "🔐 Configuring auto-login for development..."
sed -i 's/#tty1::respawn:\/sbin\/getty 38400 tty1/tty1::respawn:\/sbin\/getty -a root 38400 tty1/' /etc/inittab

echo "🐍 Installing Python packages for Unhinged..."
pip3 install \
    cffi \
    numpy \
    requests \
    websockets

echo "📁 Creating Unhinged directory..."
mkdir -p /opt/unhinged

echo "🚀 Creating Unhinged startup script..."
cat > /opt/unhinged/start_unhinged.py << 'EOF'
#!/usr/bin/env python3
"""
Unhinged Native Graphics Launcher for Alpine Linux
Renders directly to framebuffer with exclusive DRM access
"""

import sys
import os
import time

def check_devices():
    """Check if required devices are available"""
    devices = {
        '/dev/dri': 'DRM devices',
        '/dev/fb0': 'Framebuffer device'
    }
    
    for device, name in devices.items():
        if os.path.exists(device):
            print(f"✅ {name} available")
        else:
            print(f"❌ {name} not found at {device}")
            return False
    return True

def render_hello_world():
    """Render a simple hello world to framebuffer"""
    try:
        # Try to write directly to framebuffer
        with open('/dev/fb0', 'wb') as fb:
            # Create a simple pattern (this is very basic)
            # In reality, we'd use the Unhinged graphics library
            width, height = 1024, 768  # Assume standard resolution
            
            # Fill with white background (RGB)
            white_pixel = b'\xFF\xFF\xFF'
            for y in range(height):
                for x in range(width):
                    fb.write(white_pixel)
            
            print("✅ Basic framebuffer write successful")
            return True
    except Exception as e:
        print(f"❌ Framebuffer write failed: {e}")
        return False

def main():
    print("🔥 UNHINGED NATIVE GRAPHICS - ALPINE LINUX")
    print("=" * 50)
    
    # Check required devices
    if not check_devices():
        print("💡 Some devices are missing - this is normal during initial setup")
        print("💡 Devices will be available after reboot with proper drivers")
    
    print("🎯 Testing basic framebuffer access...")
    
    # Try basic framebuffer rendering
    if render_hello_world():
        print("🎉 Basic graphics test successful!")
    else:
        print("⚠️ Basic graphics test failed - will retry with Unhinged library")
    
    # Try to import Unhinged graphics library
    try:
        sys.path.insert(0, '/opt/unhinged')
        import unhinged_graphics
        
        print("✅ Unhinged graphics library found!")
        
        # Initialize graphics system
        graphics = unhinged_graphics.UnhingedGraphics()
        graphics.initialize_framebuffer()
        
        # Render Unhinged interface
        graphics.clear_screen(255, 255, 255)  # White background
        graphics.draw_text(100, 100, "UNHINGED ALPINE LINUX", 0, 0, 0)
        graphics.draw_text(100, 150, "Native C Graphics Rendering", 0, 0, 0)
        graphics.draw_text(100, 200, "Direct Framebuffer Access", 0, 0, 0)
        graphics.draw_text(100, 250, "Exclusive DRM Access", 0, 0, 0)
        graphics.present()
        
        print("🎉 Unhinged graphics initialized successfully!")
        
    except ImportError:
        print("⚠️ Unhinged graphics library not yet installed")
        print("💡 This will be available after copying from host system")
    except Exception as e:
        print(f"⚠️ Graphics initialization issue: {e}")
    
    print("💡 Alpine Linux configured for Unhinged!")
    print("🔄 Reboot to activate all changes")
    
    # Keep running if called directly
    if __name__ == "__main__":
        print("💡 Press Ctrl+C to exit")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")

if __name__ == "__main__":
    main()
EOF

chmod +x /opt/unhinged/start_unhinged.py

echo "🔧 Creating Unhinged service..."
cat > /etc/init.d/unhinged << 'EOF'
#!/sbin/openrc-run

name="Unhinged Native Graphics"
command="/usr/bin/python3"
command_args="/opt/unhinged/start_unhinged.py"
command_background="yes"
pidfile="/var/run/unhinged.pid"

depend() {
    need localmount
    after bootmisc
}

start_pre() {
    # Ensure DRM devices are available
    if [ ! -d /dev/dri ]; then
        einfo "Waiting for DRM devices..."
        sleep 2
    fi
}
EOF

chmod +x /etc/init.d/unhinged
rc-update add unhinged default

echo "🌐 Configuring SSH access..."
rc-service sshd start
rc-update add sshd default

# Allow root SSH login for development
sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
rc-service sshd restart

echo "✅ ALPINE LINUX CONFIGURATION COMPLETE!"
echo ""
echo "📋 NEXT STEPS:"
echo "1. Reboot Alpine VM: reboot"
echo "2. Copy Unhinged graphics library from host"
echo "3. Test Unhinged graphics rendering"
echo ""
echo "🌐 SSH Access: ssh -p 2222 root@localhost"
echo "🎯 Manual Test: /opt/unhinged/start_unhinged.py"
echo ""
echo "🔄 Rebooting in 10 seconds... (Ctrl+C to cancel)"
sleep 10
reboot
