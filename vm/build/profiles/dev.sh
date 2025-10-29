#!/bin/bash
# UnhingedOS Development Profile Configuration
# Target: UnhingedOS development, system debugging, research
# Resources: 512MB RAM, 4 CPU cores, complete development environment

# Profile identification
PROFILE_NAME="dev"
PROFILE_DESCRIPTION="Complete development environment with debugging tools"
PROFILE_VERSION="1.0.0"

# Resource specifications
MEMORY_SIZE="512MB"
CPU_CORES="4"
DISK_SIZE="8GB"
VIRTUAL_DISK_SIZE="8GB"

# Base system packages
BASE_PACKAGES=(
    "alpine-base"
    "openrc"
    "busybox"
    "musl"
    "musl-dev"
    "linux-virt"
    "linux-headers"
    "eudev"
    "dbus"
)

# Core system packages
CORE_PACKAGES=(
    "python3"
    "python3-dev"
    "py3-pip"
    "py3-cffi"
    "py3-numpy"
    "py3-scipy"
    "py3-pytest"
    "git"
    "cmake"
    "make"
    "build-base"
    "gcc"
    "g++"
    "libc-dev"
)

# Graphics packages (full development stack)
GRAPHICS_PACKAGES=(
    "mesa-dri-gallium"
    "mesa-gl"
    "mesa-gles"
    "mesa-dev"
    "libdrm"
    "libdrm-dev"
    "xorg-server"
    "xorg-server-dev"
    "xf86-video-vesa"
    "xf86-input-evdev"
    "fontconfig"
    "fontconfig-dev"
    "ttf-dejavu"
)

# Voice interface packages (development)
VOICE_PACKAGES=(
    "alsa-utils"
    "alsa-lib"
    "alsa-lib-dev"
    "pulseaudio"
    "pulseaudio-dev"
    "pulseaudio-alsa"
    "espeak"
    "espeak-dev"
    "sox"
    "sox-dev"
    "ffmpeg"
    "ffmpeg-dev"
)

# Development packages (comprehensive)
DEV_PACKAGES=(
    "gdb"
    "valgrind"
    "strace"
    "ltrace"
    "perf"
    "htop"
    "iotop"
    "lsof"
    "tcpdump"
    "wireshark-common"
    "nano"
    "vim"
    "tmux"
    "screen"
    "rsync"
    "curl"
    "wget"
    "jq"
    "tree"
    "file"
    "binutils"
    "objdump"
    "readelf"
    "hexdump"
)

# Documentation and analysis tools
DOC_PACKAGES=(
    "man-pages"
    "man-pages-posix"
    "less"
    "grep"
    "sed"
    "awk"
    "diffutils"
)

# Services to enable
ENABLED_SERVICES=(
    "networking"
    "chronyd"
    "syslog"
    "dbus"
    "eudev"
    "sshd"
    "voice-interface"
    "graphics-service"
    "development-server"
    "profiling-service"
)

# Services to disable
DISABLED_SERVICES=(
    "bluetooth"
    "wifi"
    "cups"
)

# Graphics configuration (full development)
GRAPHICS_MODE="development"
GRAPHICS_ACCELERATION="hardware"
FRAMEBUFFER_RESOLUTION="1280x1024"
COLOR_DEPTH="32"
COMPOSITING="enabled"
VSYNC="disabled"
DEBUG_GRAPHICS="enabled"

# Voice interface configuration (development)
VOICE_ENGINE="development"
VOICE_RECOGNITION="advanced"
VOICE_SYNTHESIS="natural"
VOICE_LATENCY_TARGET="100ms"
VOICE_DEBUG="enabled"
VOICE_PROFILING="enabled"

# Development configuration
DEVELOPMENT_MODE="enabled"
DEBUG_SYMBOLS="enabled"
PROFILING="enabled"
MEMORY_DEBUGGING="enabled"
PERFORMANCE_MONITORING="enabled"

# Boot configuration
BOOT_TIMEOUT="10"
BOOT_SPLASH="enabled"
BOOT_QUIET="false"
BOOT_DEBUG="enabled"
INIT_SYSTEM="openrc"

# Network configuration
NETWORK_ENABLED="true"
NETWORK_DHCP="true"
NETWORK_WIFI="false"
SSH_ENABLED="true"

# Security configuration (development-friendly)
ROOT_PASSWORD_DISABLED="false"
SSH_ENABLED="true"
SSH_PASSWORD_AUTH="true"
FIREWALL_ENABLED="false"

# Optimization settings (debug-friendly)
OPTIMIZE_SIZE="false"
OPTIMIZE_SPEED="false"
STRIP_DEBUG="false"
COMPRESS_KERNEL="false"
DEBUG_INFO="enabled"

# Build options
BUILD_PARALLEL="true"
BUILD_CACHE="true"
BUILD_VERBOSE="true"
BUILD_DEBUG="true"

# Target architecture
TARGET_ARCH="x86_64"
TARGET_KERNEL="virt"
TARGET_LIBC="musl"

# Filesystem configuration
ROOT_FILESYSTEM="ext4"
FILESYSTEM_COMPRESSION="false"
FILESYSTEM_READONLY="false"
FILESYSTEM_DEBUG="enabled"

# Memory management (development-optimized)
SWAP_ENABLED="true"
SWAP_SIZE="256MB"
TMPFS_SIZE="128MB"
CACHE_SIZE="64MB"

# Performance tuning (development)
CPU_GOVERNOR="performance"
IO_SCHEDULER="deadline"
KERNEL_PREEMPTION="preempt"

# Feature flags (all enabled for development)
FEATURE_BLUETOOTH="false"
FEATURE_WIFI="false"
FEATURE_USB="true"
FEATURE_AUDIO="full"
FEATURE_GRAPHICS="full"
FEATURE_NETWORKING="full"
FEATURE_DEBUGGING="full"
FEATURE_PROFILING="enabled"

# Custom configuration function
configure_dev_profile() {
    echo "🛠️ Configuring development UnhingedOS profile..."
    
    # Development-optimized kernel configuration
    echo "kernel.printk = 7 4 1 7" >> /etc/sysctl.conf
    echo "kernel.core_pattern = /tmp/core.%e.%p.%t" >> /etc/sysctl.conf
    echo "vm.swappiness = 20" >> /etc/sysctl.conf
    echo "vm.vfs_cache_pressure = 50" >> /etc/sysctl.conf
    
    # Enable all development services
    for service in "${ENABLED_SERVICES[@]}"; do
        rc-update add "$service" default 2>/dev/null || true
    done
    
    # Configure development voice interface
    mkdir -p /etc/unhinged
    cat > /etc/unhinged/voice.conf << EOF
engine=development
recognition=advanced
synthesis=natural
latency_target=100ms
debug=enabled
profiling=enabled
memory_limit=128MB
processing_threads=4
log_level=debug
EOF
    
    # Configure development graphics
    cat > /etc/unhinged/graphics.conf << EOF
mode=development
acceleration=hardware
resolution=1280x1024
color_depth=32
compositing=enabled
vsync=disabled
debug=enabled
profiling=enabled
memory_limit=128MB
rendering_threads=4
log_level=debug
EOF
    
    # Configure development environment
    cat > /etc/unhinged/development.conf << EOF
mode=enabled
debug_symbols=enabled
profiling=enabled
memory_debugging=enabled
performance_monitoring=enabled
hot_reload=enabled
live_debugging=enabled
EOF
    
    # Create development user with sudo access
    adduser -D -s /bin/bash developer
    echo "developer:developer" | chpasswd
    addgroup developer wheel
    addgroup developer audio
    addgroup developer video
    addgroup developer input
    
    # Configure sudo for development
    echo "%wheel ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
    
    # Set up development directories
    mkdir -p /home/developer/{src,build,debug,logs}
    chown -R developer:developer /home/developer
    
    # Configure GDB for development
    cat > /home/developer/.gdbinit << EOF
set print pretty on
set print array on
set print array-indexes on
set history save on
set history filename ~/.gdb_history
EOF
    
    # Configure development aliases
    cat > /home/developer/.profile << EOF
export PATH=\$PATH:/usr/local/bin
export EDITOR=nano
export PAGER=less
alias ll='ls -la'
alias la='ls -A'
alias l='ls -CF'
alias ..='cd ..'
alias ...='cd ../..'
alias grep='grep --color=auto'
alias debug-voice='gdb /usr/bin/voice-interface'
alias debug-graphics='gdb /usr/bin/graphics-service'
alias profile-system='perf record -g'
alias analyze-profile='perf report'
EOF
    
    echo "✅ Development profile configuration complete"
}

# Validation function
validate_dev_profile() {
    echo "🔍 Validating development profile configuration..."
    
    # Check memory requirements
    if [[ "${MEMORY_SIZE}" != "512MB" ]]; then
        echo "❌ Memory size must be 512MB for development profile"
        return 1
    fi
    
    # Check CPU requirements
    if [[ "${CPU_CORES}" != "4" ]]; then
        echo "❌ CPU cores must be 4 for development profile"
        return 1
    fi
    
    # Check development packages
    local dev_packages=("gdb" "valgrind" "strace" "perf")
    for package in "${dev_packages[@]}"; do
        if [[ ! " ${DEV_PACKAGES[*]} " =~ " ${package} " ]]; then
            echo "❌ Development package missing: $package"
            return 1
        fi
    done
    
    # Check debug configuration
    if [[ "${DEBUG_SYMBOLS}" != "enabled" ]]; then
        echo "❌ Debug symbols must be enabled for development profile"
        return 1
    fi
    
    echo "✅ Development profile validation passed"
    return 0
}

# Export all configuration
export PROFILE_NAME PROFILE_DESCRIPTION PROFILE_VERSION
export MEMORY_SIZE CPU_CORES DISK_SIZE VIRTUAL_DISK_SIZE
export BASE_PACKAGES CORE_PACKAGES GRAPHICS_PACKAGES VOICE_PACKAGES DEV_PACKAGES DOC_PACKAGES
export ENABLED_SERVICES DISABLED_SERVICES
export GRAPHICS_MODE GRAPHICS_ACCELERATION FRAMEBUFFER_RESOLUTION COLOR_DEPTH COMPOSITING VSYNC DEBUG_GRAPHICS
export VOICE_ENGINE VOICE_RECOGNITION VOICE_SYNTHESIS VOICE_LATENCY_TARGET VOICE_DEBUG VOICE_PROFILING
export DEVELOPMENT_MODE DEBUG_SYMBOLS PROFILING MEMORY_DEBUGGING PERFORMANCE_MONITORING
export BOOT_TIMEOUT BOOT_SPLASH BOOT_QUIET BOOT_DEBUG INIT_SYSTEM
export NETWORK_ENABLED NETWORK_DHCP NETWORK_WIFI SSH_ENABLED
export ROOT_PASSWORD_DISABLED SSH_ENABLED SSH_PASSWORD_AUTH FIREWALL_ENABLED
export OPTIMIZE_SIZE OPTIMIZE_SPEED STRIP_DEBUG COMPRESS_KERNEL DEBUG_INFO
export BUILD_PARALLEL BUILD_CACHE BUILD_VERBOSE BUILD_DEBUG
export TARGET_ARCH TARGET_KERNEL TARGET_LIBC
export ROOT_FILESYSTEM FILESYSTEM_COMPRESSION FILESYSTEM_READONLY FILESYSTEM_DEBUG
export SWAP_ENABLED SWAP_SIZE TMPFS_SIZE CACHE_SIZE
export CPU_GOVERNOR IO_SCHEDULER KERNEL_PREEMPTION
export FEATURE_BLUETOOTH FEATURE_WIFI FEATURE_USB FEATURE_AUDIO FEATURE_GRAPHICS FEATURE_NETWORKING FEATURE_DEBUGGING FEATURE_PROFILING

echo "🛠️ UnhingedOS Development Profile loaded: $PROFILE_DESCRIPTION"
