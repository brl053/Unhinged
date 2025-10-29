#!/bin/bash
#
# @llm-doc Desktop Application Installation Script
# @llm-version 1.0.0
# @llm-date 2025-01-26
# @llm-author Unhinged Team
#
# ## Overview
# Installation script for the Unhinged desktop application on Ubuntu GNOME.
# Installs the .desktop file and sets up proper permissions for desktop integration.
#
# ## Features
# - User-level installation (no sudo required)
# - System-wide installation option (with sudo)
# - Automatic desktop database update
# - Dependency checking for GTK4/Libadwaita
# - Icon installation and setup
#
# @llm-principle Easy installation for Ubuntu GNOME users
# @llm-culture Independence through accessible desktop integration
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DESKTOP_FILE="$SCRIPT_DIR/unhinged.desktop"
APP_EXECUTABLE="$SCRIPT_DIR/unhinged-desktop-app"

# Installation paths
USER_APPLICATIONS_DIR="$HOME/.local/share/applications"
SYSTEM_APPLICATIONS_DIR="/usr/share/applications"

# Functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_dependencies() {
    log_info "Checking dependencies..."
    
    # Check Python 3
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed"
        return 1
    fi
    log_success "Python 3 found"
    
    # Check GTK4 and Libadwaita
    if ! python3 -c "import gi; gi.require_version('Gtk', '4.0'); gi.require_version('Adw', '1')" 2>/dev/null; then
        log_warning "GTK4 or Libadwaita not found"
        log_info "Installing GTK4 and Libadwaita..."
        
        if command -v apt &> /dev/null; then
            log_info "Run: sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-adw-1"
        elif command -v dnf &> /dev/null; then
            log_info "Run: sudo dnf install python3-gobject gtk4-devel libadwaita-devel"
        else
            log_warning "Please install GTK4 and Libadwaita for your distribution"
        fi
        
        log_warning "Continuing installation - app may not work without dependencies"
    else
        log_success "GTK4 and Libadwaita found"
    fi
    
    return 0
}

update_desktop_file() {
    # Create temporary desktop file with absolute paths
    TEMP_DESKTOP_FILE="/tmp/unhinged.desktop"
    cp "$DESKTOP_FILE" "$TEMP_DESKTOP_FILE"

    # Update paths to absolute paths
    sed -i "s|Exec=.*|Exec=$APP_EXECUTABLE|g" "$TEMP_DESKTOP_FILE"

    echo "$TEMP_DESKTOP_FILE"
}

install_user() {
    log_info "Installing Unhinged desktop application for current user..."
    
    # Create user applications directory
    mkdir -p "$USER_APPLICATIONS_DIR"
    
    # Update desktop file
    log_info "Updating desktop file paths..."
    UPDATED_DESKTOP_FILE=$(update_desktop_file)
    log_success "Desktop file updated with absolute paths"

    # Copy desktop file
    cp "$UPDATED_DESKTOP_FILE" "$USER_APPLICATIONS_DIR/unhinged.desktop"
    chmod 644 "$USER_APPLICATIONS_DIR/unhinged.desktop"
    
    # Make executable executable
    chmod +x "$APP_EXECUTABLE"
    
    # Update desktop database
    if command -v update-desktop-database &> /dev/null; then
        update-desktop-database "$USER_APPLICATIONS_DIR" 2>/dev/null || true
        log_success "Desktop database updated"
    fi
    
    log_success "User installation completed"
    log_info "Application should appear in your application menu"
}

install_system() {
    log_info "Installing Unhinged desktop application system-wide..."
    
    if [ "$EUID" -ne 0 ]; then
        log_error "System installation requires root privileges"
        log_info "Run: sudo $0 --system"
        return 1
    fi
    
    # Update desktop file
    UPDATED_DESKTOP_FILE=$(update_desktop_file)
    
    # Copy desktop file
    cp "$UPDATED_DESKTOP_FILE" "$SYSTEM_APPLICATIONS_DIR/unhinged.desktop"
    chmod 644 "$SYSTEM_APPLICATIONS_DIR/unhinged.desktop"
    
    # Make executable executable
    chmod +x "$APP_EXECUTABLE"
    
    # Update desktop database
    if command -v update-desktop-database &> /dev/null; then
        update-desktop-database "$SYSTEM_APPLICATIONS_DIR" 2>/dev/null || true
        log_success "Desktop database updated"
    fi
    
    log_success "System installation completed"
    log_info "Application available for all users"
}

uninstall_user() {
    log_info "Uninstalling Unhinged desktop application for current user..."
    
    if [ -f "$USER_APPLICATIONS_DIR/unhinged.desktop" ]; then
        rm "$USER_APPLICATIONS_DIR/unhinged.desktop"
        log_success "Desktop file removed"
    else
        log_warning "Desktop file not found"
    fi
    
    # Update desktop database
    if command -v update-desktop-database &> /dev/null; then
        update-desktop-database "$USER_APPLICATIONS_DIR" 2>/dev/null || true
    fi
    
    log_success "User uninstallation completed"
}

uninstall_system() {
    log_info "Uninstalling Unhinged desktop application system-wide..."
    
    if [ "$EUID" -ne 0 ]; then
        log_error "System uninstallation requires root privileges"
        log_info "Run: sudo $0 --uninstall-system"
        return 1
    fi
    
    if [ -f "$SYSTEM_APPLICATIONS_DIR/unhinged.desktop" ]; then
        rm "$SYSTEM_APPLICATIONS_DIR/unhinged.desktop"
        log_success "Desktop file removed"
    else
        log_warning "Desktop file not found"
    fi
    
    # Update desktop database
    if command -v update-desktop-database &> /dev/null; then
        update-desktop-database "$SYSTEM_APPLICATIONS_DIR" 2>/dev/null || true
    fi
    
    log_success "System uninstallation completed"
}

test_installation() {
    log_info "Testing desktop application..."
    
    if [ -f "$USER_APPLICATIONS_DIR/unhinged.desktop" ] || [ -f "$SYSTEM_APPLICATIONS_DIR/unhinged.desktop" ]; then
        log_success "Desktop file installed"
    else
        log_error "Desktop file not found"
        return 1
    fi
    
    if [ -x "$APP_EXECUTABLE" ]; then
        log_success "Application executable is ready"
    else
        log_error "Application executable not found or not executable"
        return 1
    fi
    
    log_success "Installation test passed"
    log_info "You can now launch Unhinged from your application menu"
}

show_help() {
    echo "Unhinged Desktop Application Installer"
    echo ""
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  --user              Install for current user (default)"
    echo "  --system            Install system-wide (requires sudo)"
    echo "  --uninstall         Uninstall user installation"
    echo "  --uninstall-system  Uninstall system installation (requires sudo)"
    echo "  --test              Test installation"
    echo "  --help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                  # Install for current user"
    echo "  sudo $0 --system   # Install system-wide"
    echo "  $0 --test          # Test installation"
}

# Main script
main() {
    echo "🚀 Unhinged Desktop Application Installer"
    echo "=========================================="
    
    case "${1:-}" in
        --system)
            check_dependencies
            install_system
            test_installation
            ;;
        --uninstall)
            uninstall_user
            ;;
        --uninstall-system)
            uninstall_system
            ;;
        --test)
            test_installation
            ;;
        --help)
            show_help
            ;;
        --user|"")
            check_dependencies
            install_user
            test_installation
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
    
    echo ""
    echo "🎉 Installation process completed!"
    echo "💡 Launch Unhinged from your application menu or run:"
    echo "   $APP_EXECUTABLE"
}

# Run main function
main "$@"
