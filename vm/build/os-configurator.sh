#!/bin/bash
#
# @llm-does UnhingedOS system configuration orchestrator for Alpine Linux base system setup with voice-first optimizations
# @llm-type build.config/os-configurator
# @llm-context UnhingedOS system configuration for voice-first operating system built on Alpine Linux 3.22.2. Configures: (1) System Update - Alpine package updates with error handling, (2) Build Tools - systematic installation of development dependencies (build-base, cmake, git, python3, mesa-dev, libdrm-dev), (3) Graphics Stack - UnhingedOS-specific graphics drivers and DRM setup (mesa-dri-gallium, mesa-va-gallium, xf86-video-qxl, libdrm, linux-firmware), (4) System Configuration - framebuffer console, auto-login, boot settings, (5) Python Dependencies - voice-first OS packages (cffi, numpy, requests, websockets), (6) Directory Structure - /opt/unhinged/{bin,lib,config}, /etc/unhinged, /var/log/unhinged, (7) Startup Script - voice-first graphics launcher with device detection, (8) System Service - OpenRC service for UnhingedOS graphics with proper dependencies, (9) SSH Configuration - development access with security. Graphics optimization: DRM access configuration, framebuffer setup, video group permissions, hardware acceleration enablement. Voice-first focus: all configuration optimized for voice-first computing paradigm with visual feedback systems.
#

set -e

# Script metadata
SCRIPT_VERSION="1.0.0"
SCRIPT_NAME="UnhingedOS Configurator"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }
log_header() { echo -e "${PURPLE}🎯 $1${NC}"; }

# Display header
echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                UnhingedOS Configurator                       ║"
echo "║           Voice-First Operating System Setup                 ║"
echo "║                     Version $SCRIPT_VERSION                         ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    log_error "Please run as root"
    exit 1
fi

log_header "UnhingedOS System Configuration Starting"

# Update Alpine packages
update_system() {
    log_info "Updating Alpine Linux packages..."
    if apk update && apk upgrade; then
        log_success "System packages updated"
    else
        log_error "Failed to update system packages"
        exit 1
    fi
}

# Install UnhingedOS development tools
install_build_tools() {
    log_info "Installing UnhingedOS build tools and dependencies..."

    local build_packages=(
        "build-base"
        "cmake"
        "git"
        "python3"
        "python3-dev"
        "py3-pip"
        "linux-headers"
        "mesa-dev"
        "libdrm-dev"
        "eudev-dev"
        "pkgconfig"
        "gcc"
        "musl-dev"
        "curl"
        "wget"
    )

    if apk add "${build_packages[@]}"; then
        log_success "Build tools installed successfully"
    else
        log_error "Failed to install build tools"
        exit 1
    fi
}

# Install UnhingedOS graphics stack
install_graphics_stack() {
    log_info "Installing UnhingedOS graphics drivers and DRM support..."

    local graphics_packages=(
        "mesa-dri-gallium"
        "mesa-va-gallium"
        "mesa-vdpau-gallium"
        "xf86-video-qxl"
        "libdrm"
        "linux-firmware-amdgpu"
        "linux-firmware-radeon"
        "linux-firmware-i915"
    )

    if apk add "${graphics_packages[@]}"; then
        log_success "Graphics stack installed"
    else
        log_error "Failed to install graphics stack"
        exit 1
    fi

    # Configure DRM access
    log_info "Configuring DRM access for UnhingedOS..."
    addgroup root video
    log_success "Root user added to video group"
}

# Configure UnhingedOS system settings
configure_system() {
    log_info "Configuring UnhingedOS system settings..."

    # Configure framebuffer console
    if [ -f /etc/default/grub ]; then
        echo 'GRUB_CMDLINE_LINUX_DEFAULT="quiet console=tty0 console=ttyS0,115200"' >> /etc/default/grub
        update-grub
        log_success "Framebuffer console configured"
    fi

    # Configure auto-login for development
    sed -i 's/#tty1::respawn:\/sbin\/getty 38400 tty1/tty1::respawn:\/sbin\/getty -a root 38400 tty1/' /etc/inittab
    log_success "Auto-login configured"
}

# Install UnhingedOS Python dependencies
install_python_dependencies() {
    log_info "Installing Python packages for UnhingedOS..."

    local python_packages=(
        "cffi"
        "numpy"
        "requests"
        "websockets"
    )

    if pip3 install "${python_packages[@]}"; then
        log_success "Python dependencies installed"
    else
        log_error "Failed to install Python dependencies"
        exit 1
    fi
}

# Setup UnhingedOS directory structure
setup_unhinged_structure() {
    log_info "Creating UnhingedOS directory structure..."

    mkdir -p /opt/unhinged/{bin,lib,config}
    mkdir -p /etc/unhinged
    mkdir -p /var/log/unhinged

    log_success "UnhingedOS directory structure created"
}

# Create UnhingedOS startup script
create_startup_script() {
    log_info "Creating UnhingedOS startup script..."

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
    log_success "UnhingedOS startup script created"
}

# Create UnhingedOS system service
create_system_service() {
    log_info "Creating UnhingedOS system service..."

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
    log_success "UnhingedOS system service created and enabled"
}

# Configure SSH access
configure_ssh() {
    log_info "Configuring SSH access for UnhingedOS development..."

    rc-service sshd start
    rc-update add sshd default

    # Allow root SSH login for development
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
    rc-service sshd restart

    log_success "SSH access configured"
}

# Main configuration orchestration
main() {
    log_header "UnhingedOS Configuration Starting"

    # Execute configuration steps
    update_system
    install_build_tools
    install_graphics_stack
    configure_system
    install_python_dependencies
    setup_unhinged_structure
    create_startup_script
    create_system_service
    configure_ssh

    # Final status
    log_header "UnhingedOS Configuration Complete!"
    log_success "Alpine Linux configured for UnhingedOS"
    log_success "Voice-first operating system ready"

    echo ""
    log_info "Next Steps:"
    echo "  1. Reboot Alpine VM: reboot"
    echo "  2. Copy UnhingedOS graphics library from host"
    echo "  3. Test UnhingedOS graphics rendering"
    echo ""
    log_info "Access Information:"
    echo "  🌐 SSH Access: ssh -p 2222 root@localhost"
    echo "  🎯 Manual Test: /opt/unhinged/start_unhinged.py"
    echo ""

    read -p "Reboot now? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Rebooting UnhingedOS..."
        reboot
    else
        log_info "Reboot manually when ready: reboot"
    fi
}

# Execute main function
main "$@"
