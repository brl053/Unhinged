#!/bin/bash
# UnhingedOS Desktop Profile Configuration
# Target: Primary desktop replacement, voice-controlled workstations
# Resources: 256MB RAM, 2 CPU cores, full voice-first desktop

# Profile identification
PROFILE_NAME="desktop"
PROFILE_DESCRIPTION="Full voice-first desktop environment"
PROFILE_VERSION="1.0.0"

# Resource specifications
MEMORY_SIZE="256MB"
CPU_CORES="2"
DISK_SIZE="4GB"
VIRTUAL_DISK_SIZE="4GB"

# Base system packages
BASE_PACKAGES=(
    "alpine-base"
    "openrc"
    "busybox"
    "musl"
    "linux-virt"
    "eudev"
    "dbus"
)

# Core system packages
CORE_PACKAGES=(
    "python3"
    "py3-pip"
    "py3-cffi"
    "py3-numpy"
    "py3-scipy"
    "git"
    "cmake"
    "build-base"
)

# Graphics packages (full stack)
GRAPHICS_PACKAGES=(
    "mesa-dri-gallium"
    "mesa-gl"
    "mesa-gles"
    "libdrm"
    "libdrm-dev"
    "xorg-server"
    "xf86-video-vesa"
    "xf86-input-evdev"
    "fontconfig"
    "ttf-dejavu"
)

# Voice interface packages (complete)
VOICE_PACKAGES=(
    "alsa-utils"
    "alsa-lib"
    "alsa-lib-dev"
    "pulseaudio"
    "pulseaudio-alsa"
    "espeak"
    "espeak-dev"
)

# Desktop environment packages
DESKTOP_PACKAGES=(
    "dbus-x11"
    "xdg-utils"
    "shared-mime-info"
    "desktop-file-utils"
)

# Development packages (basic)
DEV_PACKAGES=(
    "gdb"
    "strace"
    "htop"
    "nano"
)

# Services to enable
ENABLED_SERVICES=(
    "networking"
    "chronyd"
    "syslog"
    "dbus"
    "eudev"
    "voice-interface"
    "graphics-service"
    "desktop-manager"
)

# Services to disable
DISABLED_SERVICES=(
    "bluetooth"
    "wifi"
    "networkmanager"
    "cups"
)

# Graphics configuration
GRAPHICS_MODE="full"
GRAPHICS_ACCELERATION="hardware"
FRAMEBUFFER_RESOLUTION="1024x768"
COLOR_DEPTH="24"
COMPOSITING="enabled"
VSYNC="enabled"

# Voice interface configuration
VOICE_ENGINE="full"
VOICE_RECOGNITION="advanced"
VOICE_SYNTHESIS="natural"
VOICE_LATENCY_TARGET="150ms"
VOICE_NOISE_REDUCTION="enabled"
VOICE_WAKE_WORD="enabled"

# Desktop configuration
DESKTOP_ENVIRONMENT="unhinged"
WINDOW_MANAGER="voice-controlled"
DESKTOP_THEME="voice-first"
ACCESSIBILITY="enhanced"

# Boot configuration
BOOT_TIMEOUT="5"
BOOT_SPLASH="enabled"
BOOT_QUIET="false"
INIT_SYSTEM="openrc"

# Network configuration
NETWORK_ENABLED="true"
NETWORK_DHCP="true"
NETWORK_WIFI="false"

# Security configuration
ROOT_PASSWORD_DISABLED="false"
SSH_ENABLED="true"
FIREWALL_ENABLED="true"

# Optimization settings
OPTIMIZE_SIZE="false"
OPTIMIZE_SPEED="true"
STRIP_DEBUG="false"
COMPRESS_KERNEL="false"

# Build options
BUILD_PARALLEL="true"
BUILD_CACHE="true"
BUILD_VERBOSE="true"

# Target architecture
TARGET_ARCH="x86_64"
TARGET_KERNEL="virt"
TARGET_LIBC="musl"

# Filesystem configuration
ROOT_FILESYSTEM="ext4"
FILESYSTEM_COMPRESSION="false"
FILESYSTEM_READONLY="false"

# Memory management
SWAP_ENABLED="true"
SWAP_SIZE="128MB"
TMPFS_SIZE="64MB"
CACHE_SIZE="32MB"

# Performance tuning
CPU_GOVERNOR="performance"
IO_SCHEDULER="deadline"
KERNEL_PREEMPTION="preempt"

# Feature flags
FEATURE_BLUETOOTH="false"
FEATURE_WIFI="false"
FEATURE_USB="true"
FEATURE_AUDIO="full"
FEATURE_GRAPHICS="full"
FEATURE_NETWORKING="basic"
FEATURE_DESKTOP="full"

# Custom configuration function
configure_desktop_profile() {
    echo "🖥️ Configuring desktop UnhingedOS profile..."
    
    # Desktop-optimized kernel configuration
    echo "kernel.printk = 4 4 1 7" >> /etc/sysctl.conf
    echo "vm.swappiness = 10" >> /etc/sysctl.conf
    echo "vm.vfs_cache_pressure = 50" >> /etc/sysctl.conf
    
    # Enable desktop services
    for service in "${ENABLED_SERVICES[@]}"; do
        rc-update add "$service" default 2>/dev/null || true
    done
    
    # Configure advanced voice interface
    mkdir -p /etc/unhinged
    cat > /etc/unhinged/voice.conf << EOF
engine=full
recognition=advanced
synthesis=natural
latency_target=150ms
noise_reduction=enabled
wake_word=enabled
memory_limit=64MB
processing_threads=2
EOF
    
    # Configure full graphics stack
    cat > /etc/unhinged/graphics.conf << EOF
mode=full
acceleration=hardware
resolution=1024x768
color_depth=24
compositing=enabled
vsync=enabled
memory_limit=64MB
rendering_threads=2
EOF
    
    # Configure desktop environment
    cat > /etc/unhinged/desktop.conf << EOF
environment=unhinged
window_manager=voice-controlled
theme=voice-first
accessibility=enhanced
voice_shortcuts=enabled
visual_feedback=full
EOF
    
    # Create desktop user
    adduser -D -s /bin/sh unhinged
    addgroup unhinged audio
    addgroup unhinged video
    addgroup unhinged input
    
    echo "✅ Desktop profile configuration complete"
}

# Validation function
validate_desktop_profile() {
    echo "🔍 Validating desktop profile configuration..."
    
    # Check memory requirements
    if [[ "${MEMORY_SIZE}" != "256MB" ]]; then
        echo "❌ Memory size must be 256MB for desktop profile"
        return 1
    fi
    
    # Check CPU requirements
    if [[ "${CPU_CORES}" != "2" ]]; then
        echo "❌ CPU cores must be 2 for desktop profile"
        return 1
    fi
    
    # Check graphics packages
    local graphics_packages=("mesa-dri-gallium" "mesa-gl" "xorg-server")
    for package in "${graphics_packages[@]}"; do
        if [[ ! " ${GRAPHICS_PACKAGES[*]} " =~ " ${package} " ]]; then
            echo "❌ Graphics package missing: $package"
            return 1
        fi
    done
    
    # Check voice packages
    local voice_packages=("alsa-utils" "pulseaudio" "espeak")
    for package in "${voice_packages[@]}"; do
        if [[ ! " ${VOICE_PACKAGES[*]} " =~ " ${package} " ]]; then
            echo "❌ Voice package missing: $package"
            return 1
        fi
    done
    
    echo "✅ Desktop profile validation passed"
    return 0
}

# Export all configuration
export PROFILE_NAME PROFILE_DESCRIPTION PROFILE_VERSION
export MEMORY_SIZE CPU_CORES DISK_SIZE VIRTUAL_DISK_SIZE
export BASE_PACKAGES CORE_PACKAGES GRAPHICS_PACKAGES VOICE_PACKAGES DESKTOP_PACKAGES DEV_PACKAGES
export ENABLED_SERVICES DISABLED_SERVICES
export GRAPHICS_MODE GRAPHICS_ACCELERATION FRAMEBUFFER_RESOLUTION COLOR_DEPTH COMPOSITING VSYNC
export VOICE_ENGINE VOICE_RECOGNITION VOICE_SYNTHESIS VOICE_LATENCY_TARGET VOICE_NOISE_REDUCTION VOICE_WAKE_WORD
export DESKTOP_ENVIRONMENT WINDOW_MANAGER DESKTOP_THEME ACCESSIBILITY
export BOOT_TIMEOUT BOOT_SPLASH BOOT_QUIET INIT_SYSTEM
export NETWORK_ENABLED NETWORK_DHCP NETWORK_WIFI
export ROOT_PASSWORD_DISABLED SSH_ENABLED FIREWALL_ENABLED
export OPTIMIZE_SIZE OPTIMIZE_SPEED STRIP_DEBUG COMPRESS_KERNEL
export BUILD_PARALLEL BUILD_CACHE BUILD_VERBOSE
export TARGET_ARCH TARGET_KERNEL TARGET_LIBC
export ROOT_FILESYSTEM FILESYSTEM_COMPRESSION FILESYSTEM_READONLY
export SWAP_ENABLED SWAP_SIZE TMPFS_SIZE CACHE_SIZE
export CPU_GOVERNOR IO_SCHEDULER KERNEL_PREEMPTION
export FEATURE_BLUETOOTH FEATURE_WIFI FEATURE_USB FEATURE_AUDIO FEATURE_GRAPHICS FEATURE_NETWORKING FEATURE_DESKTOP

echo "🖥️ UnhingedOS Desktop Profile loaded: $PROFILE_DESCRIPTION"
