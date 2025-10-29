#!/bin/bash
#
# @llm-type build-tool
# @llm-does build system component
#
# UnhingedOS Minimal Profile Configuration
# Target: Embedded systems, IoT devices, voice-only interfaces
# Resources: 64MB RAM, 1 CPU core, minimal footprint

# Profile identification
PROFILE_NAME="minimal"
PROFILE_DESCRIPTION="Minimal voice-first OS for embedded systems"
PROFILE_VERSION="1.0.0"

# Resource specifications
MEMORY_SIZE="64MB"
CPU_CORES="1"
DISK_SIZE="1GB"
VIRTUAL_DISK_SIZE="1GB"

# Base system packages
BASE_PACKAGES=(
    "alpine-base"
    "openrc"
    "busybox"
    "musl"
    "linux-virt"
)

# Core system packages
CORE_PACKAGES=(
    "python3"
    "py3-pip"
    "py3-cffi"
)

# Graphics packages (minimal)
GRAPHICS_PACKAGES=(
    "mesa-dri-gallium"
    "libdrm"
)

# Voice interface packages
VOICE_PACKAGES=(
    # Minimal voice processing
    "alsa-utils"
    "alsa-lib"
)

# Development packages (none for minimal)
DEV_PACKAGES=()

# Services to enable
ENABLED_SERVICES=(
    "networking"
    "chronyd"
    "syslog"
    "voice-interface"
)

# Services to disable
DISABLED_SERVICES=(
    "bluetooth"
    "wifi"
    "networkmanager"
    "cups"
    "avahi-daemon"
)

# Graphics configuration
GRAPHICS_MODE="basic"
GRAPHICS_ACCELERATION="software"
FRAMEBUFFER_RESOLUTION="800x600"
COLOR_DEPTH="16"

# Voice interface configuration
VOICE_ENGINE="minimal"
VOICE_RECOGNITION="basic"
VOICE_SYNTHESIS="basic"
VOICE_LATENCY_TARGET="200ms"

# Boot configuration
BOOT_TIMEOUT="2"
BOOT_SPLASH="disabled"
BOOT_QUIET="true"
INIT_SYSTEM="openrc"

# Network configuration
NETWORK_ENABLED="false"
NETWORK_DHCP="false"
NETWORK_WIFI="false"

# Security configuration
ROOT_PASSWORD_DISABLED="true"
SSH_ENABLED="false"
FIREWALL_ENABLED="false"

# Optimization settings
OPTIMIZE_SIZE="true"
OPTIMIZE_SPEED="false"
STRIP_DEBUG="true"
COMPRESS_KERNEL="true"

# Build options
BUILD_PARALLEL="false"
BUILD_CACHE="true"
BUILD_VERBOSE="false"

# Target architecture
TARGET_ARCH="x86_64"
TARGET_KERNEL="virt"
TARGET_LIBC="musl"

# Filesystem configuration
ROOT_FILESYSTEM="ext4"
FILESYSTEM_COMPRESSION="true"
FILESYSTEM_READONLY="true"

# Memory management
SWAP_ENABLED="false"
TMPFS_SIZE="16MB"
CACHE_SIZE="8MB"

# Performance tuning
CPU_GOVERNOR="powersave"
IO_SCHEDULER="noop"
KERNEL_PREEMPTION="voluntary"

# Feature flags
FEATURE_BLUETOOTH="false"
FEATURE_WIFI="false"
FEATURE_USB="true"
FEATURE_AUDIO="true"
FEATURE_GRAPHICS="basic"
FEATURE_NETWORKING="false"

# Custom configuration function
configure_minimal_profile() {
    echo "🎯 Configuring minimal UnhingedOS profile..."
    
    # Minimal kernel configuration
    echo "kernel.printk = 3 4 1 3" >> /etc/sysctl.conf
    echo "vm.swappiness = 1" >> /etc/sysctl.conf
    
    # Disable unnecessary services
    for service in "${DISABLED_SERVICES[@]}"; do
        rc-update del "$service" default 2>/dev/null || true
    done
    
    # Enable required services
    for service in "${ENABLED_SERVICES[@]}"; do
        rc-update add "$service" default 2>/dev/null || true
    done
    
    # Configure voice interface for minimal resources
    mkdir -p /etc/unhinged
    cat > /etc/unhinged/voice.conf << EOF
engine=minimal
recognition=basic
synthesis=basic
latency_target=200ms
memory_limit=16MB
EOF
    
    # Configure minimal graphics
    cat > /etc/unhinged/graphics.conf << EOF
mode=basic
acceleration=software
resolution=800x600
color_depth=16
memory_limit=8MB
EOF
    
    echo "✅ Minimal profile configuration complete"
}

# Validation function
validate_minimal_profile() {
    echo "🔍 Validating minimal profile configuration..."
    
    # Check memory requirements
    if [[ "${MEMORY_SIZE}" != "64MB" ]]; then
        echo "❌ Memory size must be 64MB for minimal profile"
        return 1
    fi
    
    # Check CPU requirements
    if [[ "${CPU_CORES}" != "1" ]]; then
        echo "❌ CPU cores must be 1 for minimal profile"
        return 1
    fi
    
    # Check essential packages
    local essential_packages=("alpine-base" "python3" "mesa-dri-gallium")
    for package in "${essential_packages[@]}"; do
        if [[ ! " ${BASE_PACKAGES[*]} ${CORE_PACKAGES[*]} ${GRAPHICS_PACKAGES[*]} " =~ " ${package} " ]]; then
            echo "❌ Essential package missing: $package"
            return 1
        fi
    done
    
    echo "✅ Minimal profile validation passed"
    return 0
}

# Export all configuration
export PROFILE_NAME PROFILE_DESCRIPTION PROFILE_VERSION
export MEMORY_SIZE CPU_CORES DISK_SIZE VIRTUAL_DISK_SIZE
export BASE_PACKAGES CORE_PACKAGES GRAPHICS_PACKAGES VOICE_PACKAGES DEV_PACKAGES
export ENABLED_SERVICES DISABLED_SERVICES
export GRAPHICS_MODE GRAPHICS_ACCELERATION FRAMEBUFFER_RESOLUTION COLOR_DEPTH
export VOICE_ENGINE VOICE_RECOGNITION VOICE_SYNTHESIS VOICE_LATENCY_TARGET
export BOOT_TIMEOUT BOOT_SPLASH BOOT_QUIET INIT_SYSTEM
export NETWORK_ENABLED NETWORK_DHCP NETWORK_WIFI
export ROOT_PASSWORD_DISABLED SSH_ENABLED FIREWALL_ENABLED
export OPTIMIZE_SIZE OPTIMIZE_SPEED STRIP_DEBUG COMPRESS_KERNEL
export BUILD_PARALLEL BUILD_CACHE BUILD_VERBOSE
export TARGET_ARCH TARGET_KERNEL TARGET_LIBC
export ROOT_FILESYSTEM FILESYSTEM_COMPRESSION FILESYSTEM_READONLY
export SWAP_ENABLED TMPFS_SIZE CACHE_SIZE
export CPU_GOVERNOR IO_SCHEDULER KERNEL_PREEMPTION
export FEATURE_BLUETOOTH FEATURE_WIFI FEATURE_USB FEATURE_AUDIO FEATURE_GRAPHICS FEATURE_NETWORKING

echo "📦 UnhingedOS Minimal Profile loaded: $PROFILE_DESCRIPTION"
