#!/bin/bash
#
# @llm-doc Distribution Package Creator for Unhinged Desktop Application
# @llm-version 1.0.0
# @llm-date 2025-01-26
# @llm-author Unhinged Team
#
# ## Overview
# Creates distribution packages for the Unhinged desktop application
# that can be easily installed on Ubuntu systems.
#
# ## Package Types
# - DEB package for Ubuntu/Debian systems
# - AppImage for universal Linux distribution
# - Snap package for Ubuntu Store
# - Flatpak for Flathub distribution
#
# @llm-principle Easy distribution for Ubuntu GNOME users
# @llm-culture Independence through accessible packaging
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
DESKTOP_DIR="$SCRIPT_DIR"
BUILD_DIR="$SCRIPT_DIR/build"
DIST_DIR="$SCRIPT_DIR/dist"

# Package information
PACKAGE_NAME="unhinged"
PACKAGE_VERSION="1.0.0"
PACKAGE_DESCRIPTION="Native Graphics Platform with VM Communication"
PACKAGE_MAINTAINER="Unhinged Team <team@unhinged.dev>"
PACKAGE_HOMEPAGE="https://github.com/unhinged/platform"

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
    log_info "Checking packaging dependencies..."
    
    # Check for required tools
    local tools=("dpkg-deb" "fakeroot" "python3" "desktop-file-validate")
    local missing_tools=()
    
    for tool in "${tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            missing_tools+=("$tool")
        fi
    done
    
    if [ ${#missing_tools[@]} -gt 0 ]; then
        log_warning "Missing packaging tools: ${missing_tools[*]}"
        log_info "Install with: sudo apt install dpkg-dev fakeroot python3 desktop-file-utils"
        return 1
    fi
    
    log_success "All packaging dependencies available"
    return 0
}

prepare_build_environment() {
    log_info "Preparing build environment..."
    
    # Clean and create build directories
    rm -rf "$BUILD_DIR" "$DIST_DIR"
    mkdir -p "$BUILD_DIR" "$DIST_DIR"
    
    log_success "Build environment prepared"
}

create_deb_package() {
    log_info "Creating DEB package..."
    
    local deb_dir="$BUILD_DIR/deb"
    local package_dir="$deb_dir/${PACKAGE_NAME}_${PACKAGE_VERSION}"
    
    # Create package directory structure
    mkdir -p "$package_dir/DEBIAN"
    mkdir -p "$package_dir/usr/bin"
    mkdir -p "$package_dir/usr/share/applications"
    mkdir -p "$package_dir/usr/share/pixmaps"
    mkdir -p "$package_dir/usr/share/doc/$PACKAGE_NAME"
    
    # Create control file
    cat > "$package_dir/DEBIAN/control" << EOF
Package: $PACKAGE_NAME
Version: $PACKAGE_VERSION
Section: graphics
Priority: optional
Architecture: all
Depends: python3, python3-gi, python3-gi-cairo, gir1.2-gtk-4.0, gir1.2-adw-1
Maintainer: $PACKAGE_MAINTAINER
Description: $PACKAGE_DESCRIPTION
 Unhinged is a native graphics platform with VM communication capabilities.
 It provides independent graphics rendering with reliable communication
 pipeline for Ubuntu GNOME systems.
Homepage: $PACKAGE_HOMEPAGE
EOF
    
    # Create postinst script
    cat > "$package_dir/DEBIAN/postinst" << 'EOF'
#!/bin/bash
set -e

# Update desktop database
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database /usr/share/applications
fi

# Update icon cache
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -f -t /usr/share/pixmaps
fi

echo "Unhinged desktop application installed successfully!"
echo "You can find it in your application menu or run: unhinged"
EOF
    
    chmod 755 "$package_dir/DEBIAN/postinst"
    
    # Create postrm script
    cat > "$package_dir/DEBIAN/postrm" << 'EOF'
#!/bin/bash
set -e

if [ "$1" = "remove" ]; then
    # Update desktop database
    if command -v update-desktop-database >/dev/null 2>&1; then
        update-desktop-database /usr/share/applications
    fi
fi
EOF
    
    chmod 755 "$package_dir/DEBIAN/postrm"
    
    # Copy application files
    cp "$DESKTOP_DIR/unhinged-desktop-app" "$package_dir/usr/bin/unhinged"
    chmod 755 "$package_dir/usr/bin/unhinged"
    
    # Copy desktop file
    cp "$DESKTOP_DIR/unhinged.desktop" "$package_dir/usr/share/applications/"
    
    # Update desktop file for system installation
    sed -i "s|Exec=.*|Exec=/usr/bin/unhinged|g" "$package_dir/usr/share/applications/unhinged.desktop"
    
    # Validate desktop file
    if command -v desktop-file-validate &> /dev/null; then
        desktop-file-validate "$package_dir/usr/share/applications/unhinged.desktop"
        log_success "Desktop file validation passed"
    fi
    
    # Copy icon (use SVG if available, otherwise use system icon)
    if [ -f "$DESKTOP_DIR/unhinged-icon.svg" ]; then
        cp "$DESKTOP_DIR/unhinged-icon.svg" "$package_dir/usr/share/pixmaps/unhinged.svg"
    fi
    
    # Create documentation
    cat > "$package_dir/usr/share/doc/$PACKAGE_NAME/README" << EOF
Unhinged Desktop Application
============================

This package provides the Unhinged native graphics platform desktop application
for Ubuntu GNOME systems.

Features:
- Native GTK4/Libadwaita interface
- Integration with Unhinged platform
- VM communication capabilities
- Multiple launch modes

Usage:
- Launch from application menu: Search for "Unhinged"
- Command line: unhinged
- Desktop integration: Double-click desktop icon

For more information, visit: $PACKAGE_HOMEPAGE
EOF
    
    # Create changelog
    cat > "$package_dir/usr/share/doc/$PACKAGE_NAME/changelog" << EOF
$PACKAGE_NAME ($PACKAGE_VERSION) stable; urgency=low

  * Initial release of Unhinged desktop application
  * GTK4/Libadwaita native interface
  * Integration with Unhinged platform
  * Multiple launch modes support
  * Ubuntu GNOME desktop integration

 -- $PACKAGE_MAINTAINER  $(date -R)
EOF
    
    # Create copyright file
    cat > "$package_dir/usr/share/doc/$PACKAGE_NAME/copyright" << EOF
Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: $PACKAGE_NAME
Source: $PACKAGE_HOMEPAGE

Files: *
Copyright: 2025 Unhinged Team
License: MIT
 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:
 .
 The above copyright notice and this permission notice shall be included in all
 copies or substantial portions of the Software.
 .
 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 SOFTWARE.
EOF
    
    # Build DEB package
    log_info "Building DEB package..."
    cd "$deb_dir"
    dpkg-deb --build "${PACKAGE_NAME}_${PACKAGE_VERSION}"
    
    # Move to dist directory
    mv "${PACKAGE_NAME}_${PACKAGE_VERSION}.deb" "$DIST_DIR/"
    
    log_success "DEB package created: $DIST_DIR/${PACKAGE_NAME}_${PACKAGE_VERSION}.deb"
}

create_appimage() {
    log_info "Creating AppImage..."
    log_warning "AppImage creation requires additional tools (appimagetool)"
    log_info "For now, creating AppImage directory structure"
    
    local appimage_dir="$BUILD_DIR/appimage"
    mkdir -p "$appimage_dir"
    
    # Create AppDir structure
    local appdir="$appimage_dir/Unhinged.AppDir"
    mkdir -p "$appdir/usr/bin"
    mkdir -p "$appdir/usr/share/applications"
    mkdir -p "$appdir/usr/share/icons/hicolor/256x256/apps"
    
    # Copy files
    cp "$DESKTOP_DIR/unhinged-desktop-app" "$appdir/usr/bin/unhinged"
    cp "$DESKTOP_DIR/unhinged.desktop" "$appdir/"
    cp "$DESKTOP_DIR/unhinged.desktop" "$appdir/usr/share/applications/"
    
    # Update desktop file
    sed -i "s|Exec=.*|Exec=unhinged|g" "$appdir/unhinged.desktop"
    sed -i "s|Exec=.*|Exec=unhinged|g" "$appdir/usr/share/applications/unhinged.desktop"
    
    # Create AppRun
    cat > "$appdir/AppRun" << 'EOF'
#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
export PATH="${HERE}/usr/bin:${PATH}"
exec "${HERE}/usr/bin/unhinged" "$@"
EOF
    chmod +x "$appdir/AppRun"
    
    log_success "AppImage directory structure created: $appdir"
    log_info "To complete AppImage: download appimagetool and run:"
    log_info "  appimagetool $appdir $DIST_DIR/Unhinged-${PACKAGE_VERSION}-x86_64.AppImage"
}

create_installation_guide() {
    log_info "Creating installation guide..."
    
    cat > "$DIST_DIR/INSTALL.md" << EOF
# Unhinged Desktop Application Installation Guide

## Quick Installation (Recommended)

### Option 1: DEB Package (Ubuntu/Debian)
\`\`\`bash
# Download and install the DEB package
sudo dpkg -i ${PACKAGE_NAME}_${PACKAGE_VERSION}.deb

# Install dependencies if needed
sudo apt-get install -f
\`\`\`

### Option 2: Manual Installation
\`\`\`bash
# Clone or download the Unhinged project
cd /path/to/Unhinged/desktop

# Run the installation script
./install-desktop-app.sh --user
\`\`\`

## System Requirements

- Ubuntu 20.04 LTS or later
- GNOME desktop environment
- Python 3.8+
- GTK4 and Libadwaita

### Install Dependencies
\`\`\`bash
sudo apt update
sudo apt install python3 python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-adw-1
\`\`\`

## Usage

### Launch Methods
1. **Application Menu**: Search for "Unhinged" in your application menu
2. **Command Line**: Run \`unhinged\` in terminal
3. **Desktop**: Double-click the Unhinged icon (if placed on desktop)

### Features
- **Enhanced Mode**: Full bidirectional VM communication (recommended)
- **Simple Mode**: Basic unidirectional communication for testing
- **QoL Mode**: Quality-of-life interface with automatic setup
- **Custom ISO Mode**: Launch with custom Alpine ISO

## Troubleshooting

### Common Issues

1. **Application doesn't start**
   - Check dependencies: \`python3 -c "import gi; gi.require_version('Gtk', '4.0')"\`
   - Install missing packages: \`sudo apt install gir1.2-gtk-4.0 gir1.2-adw-1\`

2. **Desktop file not appearing**
   - Update desktop database: \`update-desktop-database ~/.local/share/applications\`
   - Log out and log back in

3. **Permission errors**
   - Ensure executable permissions: \`chmod +x /usr/bin/unhinged\`
   - Check file ownership and permissions

### Getting Help
- Project homepage: $PACKAGE_HOMEPAGE
- Issues: $PACKAGE_HOMEPAGE/issues
- Documentation: $PACKAGE_HOMEPAGE/wiki

## Uninstallation

### DEB Package
\`\`\`bash
sudo apt remove $PACKAGE_NAME
\`\`\`

### Manual Installation
\`\`\`bash
cd /path/to/Unhinged/desktop
./install-desktop-app.sh --uninstall
\`\`\`
EOF
    
    log_success "Installation guide created: $DIST_DIR/INSTALL.md"
}

main() {
    echo "🚀 Unhinged Desktop Application Distribution Package Creator"
    echo "============================================================"
    
    case "${1:-all}" in
        deb)
            check_dependencies || exit 1
            prepare_build_environment
            create_deb_package
            ;;
        appimage)
            prepare_build_environment
            create_appimage
            ;;
        guide)
            mkdir -p "$DIST_DIR"
            create_installation_guide
            ;;
        all|"")
            check_dependencies || exit 1
            prepare_build_environment
            create_deb_package
            create_appimage
            create_installation_guide
            ;;
        *)
            echo "Usage: $0 [deb|appimage|guide|all]"
            echo ""
            echo "Options:"
            echo "  deb       Create DEB package only"
            echo "  appimage  Create AppImage structure only"
            echo "  guide     Create installation guide only"
            echo "  all       Create all packages and guides (default)"
            exit 1
            ;;
    esac
    
    echo ""
    echo "🎉 Distribution package creation completed!"
    echo "📦 Packages available in: $DIST_DIR"
    echo ""
    echo "📋 Next steps:"
    echo "1. Test installation: sudo dpkg -i $DIST_DIR/${PACKAGE_NAME}_${PACKAGE_VERSION}.deb"
    echo "2. Distribute packages to users"
    echo "3. Upload to package repositories"
}

# Run main function
main "$@"
