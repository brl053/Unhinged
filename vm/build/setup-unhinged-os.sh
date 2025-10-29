#!/bin/bash
#
# @llm-does Unified UnhingedOS setup script with profile-based configuration and multiple communication modes
# @llm-type build.setup/unhinged-os-setup
# @llm-context UnhingedOS unified setup system for voice-first operating system deployment with profile-based configuration. Supports 4 profiles: (1) Minimal - basic voice interface, minimal packages (python3, py3-pip, mesa-dri-gallium, libdrm), networking/chronyd/syslog services, embedded systems target, (2) Desktop - full voice-first desktop with X11, PulseAudio, Espeak (python3, py3-pip, mesa-dri-gallium, libdrm, build-base, xorg-server, pulseaudio, espeak), networking/chronyd/syslog/dbus/pulseaudio services, primary desktop replacement, (3) Server - headless voice processing with SSH, Nginx (python3, py3-pip, mesa-dri-gallium, libdrm, openssh, nginx), networking/chronyd/syslog/sshd/nginx services, API server target, (4) Development - complete toolchain with debugging (python3, py3-pip, mesa-dri-gallium, libdrm, build-base, gdb, valgrind, git, cmake), networking/chronyd/syslog/sshd services, development environment. Communication modes: auto-detection, shared directory (9p virtio), console output, silent mode. Setup orchestration: host communication setup, profile loading, package installation, UnhingedOS directory structure (/opt/unhinged/{bin,lib,config}, /etc/unhinged, /var/log/unhinged), graphics library installation, service configuration. Command line interface with comprehensive argument parsing, dry run support, verbose output, error handling.
#

set -e

# Script metadata
SCRIPT_VERSION="1.0.0"
SCRIPT_NAME="UnhingedOS Unified Setup"

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
echo "║                UnhingedOS Unified Setup                      ║"
echo "║              Voice-First Operating System                    ║"
echo "║                     Version $SCRIPT_VERSION                         ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Default configuration
PROFILE="desktop"
COMMUNICATION_MODE="auto"  # auto, shared, console, none
VERBOSE=false
DRY_RUN=false
SHARED_DIR="/mnt/shared"
HOST_COMM_FILE="vm-to-host.txt"

# Usage function
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -p, --profile PROFILE        Setup profile (minimal|desktop|server|dev) [default: desktop]"
    echo "  -c, --communication MODE     Communication mode (auto|shared|console|none) [default: auto]"
    echo "  -s, --shared-dir DIR         Shared directory path [default: /mnt/shared]"
    echo "  -v, --verbose                Verbose output"
    echo "  -n, --dry-run                Show what would be done without executing"
    echo "  -h, --help                   Show this help"
    echo ""
    echo "Profiles:"
    echo "  minimal    Basic voice interface, minimal packages"
    echo "  desktop    Full voice-first desktop environment"
    echo "  server     Headless voice processing server"
    echo "  dev        Complete development environment"
    echo ""
    echo "Communication Modes:"
    echo "  auto       Detect and use best available method"
    echo "  shared     Use 9p virtio shared directory"
    echo "  console    Console output only"
    echo "  none       No host communication"
    echo ""
    echo "Examples:"
    echo "  $0 --profile minimal --communication console"
    echo "  $0 --profile desktop --verbose"
    echo "  $0 --profile server --communication shared"
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -p|--profile)
                PROFILE="$2"
                shift 2
                ;;
            -c|--communication)
                COMMUNICATION_MODE="$2"
                shift 2
                ;;
            -s|--shared-dir)
                SHARED_DIR="$2"
                shift 2
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -n|--dry-run)
                DRY_RUN=true
                shift
                ;;
            -h|--help)
                usage
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                usage
                exit 1
                ;;
        esac
    done
}

# Host communication functions
setup_host_communication() {
    log_info "Setting up host communication ($COMMUNICATION_MODE)..."
    
    case "$COMMUNICATION_MODE" in
        "auto")
            # Try shared directory first, fall back to console
            if setup_shared_communication; then
                COMMUNICATION_MODE="shared"
                log_success "Using shared directory communication"
            else
                COMMUNICATION_MODE="console"
                log_warning "Falling back to console communication"
            fi
            ;;
        "shared")
            if ! setup_shared_communication; then
                log_error "Shared communication setup failed"
                exit 1
            fi
            ;;
        "console")
            log_info "Using console communication"
            ;;
        "none")
            log_info "Host communication disabled"
            ;;
        *)
            log_error "Invalid communication mode: $COMMUNICATION_MODE"
            exit 1
            ;;
    esac
}

setup_shared_communication() {
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Would setup shared directory: $SHARED_DIR"
        return 0
    fi
    
    # Create shared directory
    mkdir -p "$SHARED_DIR" 2>/dev/null || return 1
    
    # Try to mount 9p virtio filesystem
    if mount -t 9p -o trans=virtio,version=9p2000.L shared "$SHARED_DIR" 2>/dev/null; then
        log_success "Shared directory mounted: $SHARED_DIR"
        return 0
    else
        log_warning "Failed to mount shared directory"
        return 1
    fi
}

# Send message to host
send_to_host() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case "$COMMUNICATION_MODE" in
        "shared")
            echo "$timestamp: $message" >> "$SHARED_DIR/$HOST_COMM_FILE" 2>/dev/null || echo "$message" >&2
            ;;
        "console")
            echo "$timestamp: $message"
            ;;
        "none")
            # Silent mode
            ;;
        *)
            echo "$message" >&2
            ;;
    esac
}

# Load profile configuration
load_profile() {
    log_info "Loading profile: $PROFILE"
    
    # Define profile-specific packages
    case "$PROFILE" in
        "minimal")
            PACKAGES="python3 py3-pip mesa-dri-gallium libdrm"
            SERVICES="networking chronyd syslog"
            DESCRIPTION="Minimal voice-first OS"
            ;;
        "desktop")
            PACKAGES="python3 py3-pip mesa-dri-gallium libdrm build-base xorg-server pulseaudio espeak"
            SERVICES="networking chronyd syslog dbus pulseaudio"
            DESCRIPTION="Full voice-first desktop environment"
            ;;
        "server")
            PACKAGES="python3 py3-pip mesa-dri-gallium libdrm openssh nginx"
            SERVICES="networking chronyd syslog sshd nginx"
            DESCRIPTION="Headless voice processing server"
            ;;
        "dev")
            PACKAGES="python3 py3-pip mesa-dri-gallium libdrm build-base gdb valgrind git cmake"
            SERVICES="networking chronyd syslog sshd"
            DESCRIPTION="Complete development environment"
            ;;
        *)
            log_error "Invalid profile: $PROFILE"
            exit 1
            ;;
    esac
    
    log_success "Profile loaded: $DESCRIPTION"
    send_to_host "STATUS: Profile loaded - $DESCRIPTION"
}

# Install packages
install_packages() {
    log_header "Installing packages for $PROFILE profile"
    send_to_host "STATUS: Installing packages for $PROFILE profile"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Would install packages: $PACKAGES"
        return 0
    fi
    
    log_info "Installing packages: $PACKAGES"
    if apk add --no-cache $PACKAGES; then
        log_success "Packages installed successfully"
        send_to_host "STATUS: Packages installed successfully"
    else
        log_error "Package installation failed"
        send_to_host "ERROR: Package installation failed"
        exit 1
    fi
}

# Setup UnhingedOS directory structure
setup_unhinged_directories() {
    log_info "Setting up UnhingedOS directory structure..."
    send_to_host "STATUS: Setting up directory structure"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Would create directories: /opt/unhinged, /etc/unhinged, /var/log/unhinged"
        return 0
    fi
    
    # Create main directories
    mkdir -p /opt/unhinged/{bin,lib,config}
    mkdir -p /etc/unhinged
    mkdir -p /var/log/unhinged
    
    log_success "Directory structure created"
    send_to_host "STATUS: Directory structure created"
}

# Install graphics library
install_graphics_library() {
    log_info "Installing UnhingedOS graphics library..."
    
    local graphics_lib="/tmp/libunhinged_graphics.so"
    if [[ -f "$graphics_lib" ]]; then
        if [[ "$DRY_RUN" == "true" ]]; then
            log_info "[DRY RUN] Would install graphics library to /opt/unhinged/lib/"
        else
            cp "$graphics_lib" /opt/unhinged/lib/
            log_success "Graphics library installed"
            send_to_host "STATUS: Graphics library installed"
        fi
    else
        log_warning "Graphics library not found - software rendering only"
        send_to_host "WARNING: Graphics library not found"
    fi
}

# Configure services
configure_services() {
    log_info "Configuring services for $PROFILE profile..."
    send_to_host "STATUS: Configuring services"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log_info "[DRY RUN] Would configure services: $SERVICES"
        return 0
    fi
    
    # Enable required services
    for service in $SERVICES; do
        if rc-update add "$service" default 2>/dev/null; then
            log_info "Enabled service: $service"
        else
            log_warning "Failed to enable service: $service"
        fi
    done
    
    log_success "Services configured"
    send_to_host "STATUS: Services configured"
}

# Main setup function
main() {
    log_header "UnhingedOS Setup Starting"
    
    # Parse arguments
    parse_args "$@"
    
    # Setup host communication
    setup_host_communication
    
    # Send initial status
    send_to_host "STATUS: Starting UnhingedOS setup - $PROFILE profile"
    
    # Load profile configuration
    load_profile
    
    # Execute setup steps
    install_packages
    setup_unhinged_directories
    install_graphics_library
    configure_services
    
    # Final status
    log_header "UnhingedOS Setup Complete!"
    log_success "Profile: $PROFILE ($DESCRIPTION)"
    log_success "Communication: $COMMUNICATION_MODE"
    
    send_to_host "STATUS: UnhingedOS setup completed successfully"
    send_to_host "READY: UnhingedOS $PROFILE profile ready for use"
    
    if [[ "$DRY_RUN" == "false" ]]; then
        log_info "Reboot recommended to start all services"
        send_to_host "INFO: Reboot recommended"
    fi
}

# Execute main function with all arguments
main "$@"
