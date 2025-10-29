#!/bin/bash
#
# @llm-type build-tool
# @llm-does build system component
#
# UnhingedOS Server Profile Configuration
# Target: Voice processing backend, API servers, distributed computing
# Resources: 128MB RAM, 1-2 CPU cores, headless operation

# Profile identification
PROFILE_NAME="server"
PROFILE_DESCRIPTION="Headless voice processing server"
PROFILE_VERSION="1.0.0"

# Resource specifications
MEMORY_SIZE="128MB"
CPU_CORES="2"
DISK_SIZE="2GB"
VIRTUAL_DISK_SIZE="2GB"

# Base system packages
BASE_PACKAGES=(
    "alpine-base"
    "openrc"
    "busybox"
    "musl"
    "linux-virt"
    "eudev"
)

# Core system packages
CORE_PACKAGES=(
    "python3"
    "py3-pip"
    "py3-cffi"
    "py3-numpy"
    "py3-flask"
    "py3-requests"
    "curl"
    "wget"
    "git"
)

# Graphics packages (minimal for headless)
GRAPHICS_PACKAGES=(
    "mesa-dri-gallium"
    "libdrm"
)

# Voice interface packages (server-optimized)
VOICE_PACKAGES=(
    "alsa-utils"
    "alsa-lib"
    "alsa-lib-dev"
    "espeak"
    "espeak-dev"
    "sox"
    "ffmpeg"
)

# Network packages
NETWORK_PACKAGES=(
    "openssh"
    "nginx"
    "iptables"
    "netcat-openbsd"
    "tcpdump"
)

# Development packages (server tools)
DEV_PACKAGES=(
    "htop"
    "iotop"
    "strace"
    "lsof"
    "nano"
)

# Services to enable
ENABLED_SERVICES=(
    "networking"
    "chronyd"
    "syslog"
    "sshd"
    "nginx"
    "voice-processing-server"
    "api-gateway"
    "health-monitor"
)

# Services to disable
DISABLED_SERVICES=(
    "bluetooth"
    "wifi"
    "cups"
    "avahi-daemon"
    "desktop-manager"
    "graphics-service"
)

# Graphics configuration (minimal)
GRAPHICS_MODE="headless"
GRAPHICS_ACCELERATION="software"
FRAMEBUFFER_RESOLUTION="640x480"
COLOR_DEPTH="8"

# Voice interface configuration (server-optimized)
VOICE_ENGINE="server"
VOICE_RECOGNITION="batch"
VOICE_SYNTHESIS="server"
VOICE_LATENCY_TARGET="100ms"
VOICE_BATCH_PROCESSING="enabled"
VOICE_API_ENABLED="true"

# Server configuration
SERVER_MODE="headless"
API_PORT="8080"
VOICE_API_PORT="8081"
HEALTH_CHECK_PORT="8082"
LOG_LEVEL="info"

# Boot configuration
BOOT_TIMEOUT="3"
BOOT_SPLASH="disabled"
BOOT_QUIET="true"
INIT_SYSTEM="openrc"

# Network configuration
NETWORK_ENABLED="true"
NETWORK_DHCP="true"
NETWORK_WIFI="false"
FIREWALL_ENABLED="true"

# Security configuration
ROOT_PASSWORD_DISABLED="false"
SSH_ENABLED="true"
SSH_KEY_ONLY="true"
FAIL2BAN_ENABLED="true"

# Optimization settings
OPTIMIZE_SIZE="true"
OPTIMIZE_SPEED="true"
STRIP_DEBUG="true"
COMPRESS_KERNEL="true"

# Build options
BUILD_PARALLEL="true"
BUILD_CACHE="true"
BUILD_VERBOSE="false"

# Target architecture
TARGET_ARCH="x86_64"
TARGET_KERNEL="virt"
TARGET_LIBC="musl"

# Filesystem configuration
ROOT_FILESYSTEM="ext4"
FILESYSTEM_COMPRESSION="true"
FILESYSTEM_READONLY="false"

# Memory management
SWAP_ENABLED="true"
SWAP_SIZE="64MB"
TMPFS_SIZE="32MB"
CACHE_SIZE="16MB"

# Performance tuning
CPU_GOVERNOR="ondemand"
IO_SCHEDULER="deadline"
KERNEL_PREEMPTION="voluntary"

# Feature flags
FEATURE_BLUETOOTH="false"
FEATURE_WIFI="false"
FEATURE_USB="false"
FEATURE_AUDIO="server"
FEATURE_GRAPHICS="minimal"
FEATURE_NETWORKING="full"
FEATURE_API="enabled"

# Custom configuration function
configure_server_profile() {
    echo "🖥️ Configuring server UnhingedOS profile..."
    
    # Server-optimized kernel configuration
    echo "kernel.printk = 3 4 1 3" >> /etc/sysctl.conf
    echo "vm.swappiness = 5" >> /etc/sysctl.conf
    echo "net.core.somaxconn = 1024" >> /etc/sysctl.conf
    echo "net.ipv4.tcp_max_syn_backlog = 2048" >> /etc/sysctl.conf
    
    # Enable server services
    for service in "${ENABLED_SERVICES[@]}"; do
        rc-update add "$service" default 2>/dev/null || true
    done
    
    # Disable unnecessary services
    for service in "${DISABLED_SERVICES[@]}"; do
        rc-update del "$service" default 2>/dev/null || true
    done
    
    # Configure voice processing server
    mkdir -p /etc/unhinged
    cat > /etc/unhinged/voice.conf << EOF
engine=server
recognition=batch
synthesis=server
latency_target=100ms
batch_processing=enabled
api_enabled=true
api_port=8081
memory_limit=64MB
processing_threads=2
queue_size=100
EOF
    
    # Configure minimal graphics (for status display)
    cat > /etc/unhinged/graphics.conf << EOF
mode=headless
acceleration=software
resolution=640x480
color_depth=8
memory_limit=8MB
status_display=enabled
EOF
    
    # Configure API gateway
    cat > /etc/unhinged/api.conf << EOF
port=8080
voice_backend=http://localhost:8081
health_check_port=8082
log_level=info
rate_limiting=enabled
authentication=token
EOF
    
    # Configure SSH security
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
    sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config
    sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
    
    # Configure nginx for API proxy
    cat > /etc/nginx/conf.d/unhinged-api.conf << EOF
server {
    listen 80;
    server_name _;
    
    location /api/voice {
        proxy_pass http://localhost:8081;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
    
    location /health {
        proxy_pass http://localhost:8082;
    }
}
EOF
    
    # Create service user
    adduser -D -s /bin/sh -H unhinged-server
    addgroup unhinged-server audio
    
    echo "✅ Server profile configuration complete"
}

# Validation function
validate_server_profile() {
    echo "🔍 Validating server profile configuration..."
    
    # Check memory requirements
    if [[ "${MEMORY_SIZE}" != "128MB" ]]; then
        echo "❌ Memory size must be 128MB for server profile"
        return 1
    fi
    
    # Check network packages
    local network_packages=("openssh" "nginx" "iptables")
    for package in "${network_packages[@]}"; do
        if [[ ! " ${NETWORK_PACKAGES[*]} " =~ " ${package} " ]]; then
            echo "❌ Network package missing: $package"
            return 1
        fi
    done
    
    # Check voice server packages
    local voice_packages=("alsa-utils" "espeak" "sox")
    for package in "${voice_packages[@]}"; do
        if [[ ! " ${VOICE_PACKAGES[*]} " =~ " ${package} " ]]; then
            echo "❌ Voice package missing: $package"
            return 1
        fi
    done
    
    # Check API configuration
    if [[ "${VOICE_API_ENABLED}" != "true" ]]; then
        echo "❌ Voice API must be enabled for server profile"
        return 1
    fi
    
    echo "✅ Server profile validation passed"
    return 0
}

# Export all configuration
export PROFILE_NAME PROFILE_DESCRIPTION PROFILE_VERSION
export MEMORY_SIZE CPU_CORES DISK_SIZE VIRTUAL_DISK_SIZE
export BASE_PACKAGES CORE_PACKAGES GRAPHICS_PACKAGES VOICE_PACKAGES NETWORK_PACKAGES DEV_PACKAGES
export ENABLED_SERVICES DISABLED_SERVICES
export GRAPHICS_MODE GRAPHICS_ACCELERATION FRAMEBUFFER_RESOLUTION COLOR_DEPTH
export VOICE_ENGINE VOICE_RECOGNITION VOICE_SYNTHESIS VOICE_LATENCY_TARGET VOICE_BATCH_PROCESSING VOICE_API_ENABLED
export SERVER_MODE API_PORT VOICE_API_PORT HEALTH_CHECK_PORT LOG_LEVEL
export BOOT_TIMEOUT BOOT_SPLASH BOOT_QUIET INIT_SYSTEM
export NETWORK_ENABLED NETWORK_DHCP NETWORK_WIFI FIREWALL_ENABLED
export ROOT_PASSWORD_DISABLED SSH_ENABLED SSH_KEY_ONLY FAIL2BAN_ENABLED
export OPTIMIZE_SIZE OPTIMIZE_SPEED STRIP_DEBUG COMPRESS_KERNEL
export BUILD_PARALLEL BUILD_CACHE BUILD_VERBOSE
export TARGET_ARCH TARGET_KERNEL TARGET_LIBC
export ROOT_FILESYSTEM FILESYSTEM_COMPRESSION FILESYSTEM_READONLY
export SWAP_ENABLED SWAP_SIZE TMPFS_SIZE CACHE_SIZE
export CPU_GOVERNOR IO_SCHEDULER KERNEL_PREEMPTION
export FEATURE_BLUETOOTH FEATURE_WIFI FEATURE_USB FEATURE_AUDIO FEATURE_GRAPHICS FEATURE_NETWORKING FEATURE_API

echo "🖥️ UnhingedOS Server Profile loaded: $PROFILE_DESCRIPTION"
