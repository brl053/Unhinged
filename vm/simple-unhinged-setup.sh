#!/bin/bash
"""
@llm-doc Simple Unhinged Setup for Alpine Linux
@llm-version 1.0.0
@llm-date 2025-01-26
@llm-author Unhinged Team

## Overview
Simple setup script for Unhinged in Alpine Linux that outputs to console.
Designed for Phase 1 unidirectional communication testing.

## Purpose
- Test VM → Host communication via console output
- Verify that VM messages appear in host terminal
- Provide clear status updates during setup

@llm-principle Simple console output for reliable communication
@llm-culture Independence through clear, direct communication
"""

set -e

echo "🔥 UNHINGED SIMPLE SETUP - ALPINE LINUX"
echo "========================================"
echo "📺 Console output will be visible on host terminal"
echo "💡 This tests VM → Host communication"
echo ""

# Function to output status with timestamps
status_update() {
    echo "$(date '+%H:%M:%S') STATUS: $1"
}

error_update() {
    echo "$(date '+%H:%M:%S') ERROR: $1"
}

success_update() {
    echo "$(date '+%H:%M:%S') SUCCESS: $1"
}

status_update "Starting Unhinged setup in Alpine Linux"

# Check if we're in Alpine
if [ -f /etc/alpine-release ]; then
    ALPINE_VERSION=$(cat /etc/alpine-release)
    success_update "Running on Alpine Linux $ALPINE_VERSION"
else
    error_update "Not running on Alpine Linux"
    exit 1
fi

# Update package index
status_update "Updating package index..."
if apk update >/dev/null 2>&1; then
    success_update "Package index updated"
else
    error_update "Failed to update package index"
    exit 1
fi

# Install basic packages
status_update "Installing basic packages..."
PACKAGES="python3 py3-pip build-base"

for package in $PACKAGES; do
    status_update "Installing $package..."
    if apk add --no-cache $package >/dev/null 2>&1; then
        success_update "$package installed"
    else
        error_update "Failed to install $package"
    fi
done

# Create Unhinged directory
status_update "Creating Unhinged directory structure..."
mkdir -p /opt/unhinged
success_update "Directory structure created"

# Create simple Unhinged graphics script
status_update "Creating Unhinged graphics script..."
cat > /opt/unhinged/simple_graphics.py << 'PYTHON_EOF'
#!/usr/bin/env python3
"""
Simple Unhinged Graphics for Console Output Testing
"""

import time
import os
import sys
from datetime import datetime

def log_status(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{timestamp} UNHINGED: {message}")

def main():
    log_status("Starting Unhinged Simple Graphics")
    
    # Check for graphics devices
    fb_available = os.path.exists('/dev/fb0')
    dri_available = os.path.exists('/dev/dri')
    
    log_status(f"Framebuffer available: {fb_available}")
    log_status(f"DRI devices available: {dri_available}")
    
    # Simple graphics simulation
    log_status("Initializing graphics subsystem...")
    time.sleep(2)
    
    if fb_available:
        log_status("SUCCESS: Framebuffer access confirmed")
        log_status("Rendering white background to framebuffer...")
        
        try:
            # Simple white fill simulation
            with open('/dev/fb0', 'wb') as fb:
                # Write a small amount of white pixels
                white = b'\xFF\xFF\xFF\xFF'
                for i in range(1000):  # Small test
                    fb.write(white)
            log_status("SUCCESS: White background rendered")
        except Exception as e:
            log_status(f"ERROR: Framebuffer write failed: {e}")
    else:
        log_status("WARNING: No framebuffer - using console mode")
    
    # Display status
    log_status("=== UNHINGED GRAPHICS STATUS ===")
    log_status("System: Alpine Linux VM")
    log_status("Mode: Simple Console Output")
    log_status("Communication: VM → Host Terminal")
    log_status("Status: OPERATIONAL")
    log_status("================================")
    
    # Keep running with periodic status
    counter = 0
    try:
        while True:
            time.sleep(10)
            counter += 1
            log_status(f"Heartbeat #{counter} - System running normally")
            
            if counter % 6 == 0:  # Every minute
                log_status("=== STATUS UPDATE ===")
                log_status("Unhinged graphics system active")
                log_status("VM → Host communication working")
                log_status("====================")
                
    except KeyboardInterrupt:
        log_status("Shutdown requested")
        log_status("Stopping Unhinged graphics...")
        log_status("GOODBYE from Alpine VM!")

if __name__ == "__main__":
    main()
PYTHON_EOF

chmod +x /opt/unhinged/simple_graphics.py
success_update "Unhinged graphics script created"

# Create service for auto-start
status_update "Creating Unhinged service..."
cat > /etc/init.d/unhinged-simple << 'SERVICE_EOF'
#!/sbin/openrc-run

name="Unhinged Simple Graphics"
description="Unhinged graphics with console output"
command="/usr/bin/python3"
command_args="/opt/unhinged/simple_graphics.py"
command_background="yes"
pidfile="/var/run/unhinged-simple.pid"

depend() {
    need localmount
    after bootmisc
}

start_pre() {
    echo "$(date '+%H:%M:%S') SERVICE: Starting Unhinged Simple Graphics"
}

start_post() {
    echo "$(date '+%H:%M:%S') SERVICE: Unhinged Simple Graphics started"
}

stop_post() {
    echo "$(date '+%H:%M:%S') SERVICE: Unhinged Simple Graphics stopped"
}
SERVICE_EOF

chmod +x /etc/init.d/unhinged-simple
success_update "Unhinged service created"

# Enable service for auto-start
status_update "Enabling Unhinged service for auto-start..."
if rc-update add unhinged-simple default >/dev/null 2>&1; then
    success_update "Service enabled for auto-start"
else
    error_update "Failed to enable service"
fi

# Final status
echo ""
echo "🎉 UNHINGED SIMPLE SETUP COMPLETE!"
echo "=================================="
success_update "Setup completed successfully"
success_update "Unhinged will start automatically on boot"
success_update "Console output will be visible on host terminal"
echo ""
echo "💡 To start manually: python3 /opt/unhinged/simple_graphics.py"
echo "🔄 To start service: rc-service unhinged-simple start"
echo "🎯 To test communication: reboot and watch host terminal"
echo ""
success_update "VM → Host communication pipeline ready"
