#!/bin/bash

# ============================================================================
# Unhinged HTML Files Symlink Setup
# Creates convenient symlinks for all HTML files
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

print_header() {
    echo -e "${PURPLE}🔗 Unhinged HTML Symlink Setup${NC}"
    echo "=================================================="
}

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LINKS_DIR="$PROJECT_ROOT/static_html/html-links"

create_links_directory() {
    print_info "Creating HTML links directory..."

    # Ensure static_html directory exists
    mkdir -p "$PROJECT_ROOT/static_html"

    if [ -d "$LINKS_DIR" ]; then
        print_warning "Links directory already exists, cleaning up..."
        rm -rf "$LINKS_DIR"
    fi

    mkdir -p "$LINKS_DIR"
    print_success "Created directory: $LINKS_DIR"
}

create_symlinks() {
    print_info "Creating symlinks for HTML files..."
    
    # Array of HTML files to link
    declare -A html_files=(
        ["dashboard"]="unhinged-health-dashboard.html"
        ["audio"]="voice-test.html"
        ["vision"]="image-test.html"
        ["context"]="text-test.html"
        ["backend"]="backend-test.html"
        ["chat"]="chat-interface.html"
        ["multimodal"]="multimodal-test.html"
        ["static-dashboard"]="static-dashboard/index.html"
        ["static-main"]="index.html"
    )
    
    cd "$PROJECT_ROOT"

    for link_name in "${!html_files[@]}"; do
        source_file="${html_files[$link_name]}"

        # Handle different source locations
        if [[ "$source_file" == *"/"* ]]; then
            # File with path (like static-dashboard/index.html)
            full_source_path="$PROJECT_ROOT/$source_file"
        elif [ -f "static_html/$source_file" ]; then
            # File in static_html directory
            full_source_path="$PROJECT_ROOT/static_html/$source_file"
        elif [ -f "$source_file" ]; then
            # File in project root
            full_source_path="$PROJECT_ROOT/$source_file"
        else
            print_warning "Source file not found: $source_file"
            continue
        fi

        if [ -f "$full_source_path" ]; then
            link_target="$LINKS_DIR/$link_name.html"
            ln -sf "$full_source_path" "$link_target"
            print_success "Linked: $link_name.html -> $source_file"
        else
            print_warning "Source file not found: $source_file"
        fi
    done
}

create_launcher_script() {
    print_info "Creating launcher script..."
    
    cat > "$LINKS_DIR/open.sh" << 'EOF'
#!/bin/bash

# Quick launcher for Unhinged HTML files
# Usage: ./open.sh [file] or ./open.sh [number]

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

show_menu() {
    echo -e "${BLUE}🧠 Unhinged HTML Files${NC}"
    echo "=========================="
    echo ""
    
    local i=1
    for file in "$SCRIPT_DIR"/*.html; do
        if [ -f "$file" ]; then
            local basename=$(basename "$file" .html)
            local target=$(readlink "$file" 2>/dev/null || echo "Direct file")
            echo -e "${GREEN}$i.${NC} $basename"
            echo "   📁 $(basename "$target")"
            echo ""
            ((i++))
        fi
    done
    
    echo "Usage:"
    echo "  ./open.sh [name]     - Open by name (e.g., ./open.sh dashboard)"
    echo "  ./open.sh [number]   - Open by number (e.g., ./open.sh 1)"
    echo "  ./open.sh            - Show this menu"
}

open_file() {
    local file_path="$1"
    
    if [ ! -f "$file_path" ]; then
        echo -e "${YELLOW}❌ File not found: $file_path${NC}"
        return 1
    fi
    
    local abs_path=$(realpath "$file_path")
    local file_url="file://$abs_path"
    
    echo -e "${GREEN}🚀 Opening: $(basename "$file_path")${NC}"
    echo -e "${BLUE}📍 URL: $file_url${NC}"
    
    # Try different methods to open the browser
    if command -v xdg-open &> /dev/null; then
        xdg-open "$file_url" &> /dev/null &
    elif command -v open &> /dev/null; then
        open "$file_url" &> /dev/null &
    elif command -v start &> /dev/null; then
        start "$file_url" &> /dev/null &
    else
        echo -e "${YELLOW}⚠️ Could not detect browser launcher${NC}"
        echo -e "${BLUE}Please manually open: $file_url${NC}"
    fi
}

main() {
    if [ $# -eq 0 ]; then
        show_menu
        return 0
    fi
    
    local input="$1"
    
    # Check if input is a number
    if [[ "$input" =~ ^[0-9]+$ ]]; then
        local files=("$SCRIPT_DIR"/*.html)
        local index=$((input - 1))
        
        if [ $index -ge 0 ] && [ $index -lt ${#files[@]} ]; then
            open_file "${files[$index]}"
        else
            echo -e "${YELLOW}❌ Invalid number. Use ./open.sh to see available options.${NC}"
            return 1
        fi
    else
        # Try to find file by name
        local target_file="$SCRIPT_DIR/$input.html"
        
        if [ -f "$target_file" ]; then
            open_file "$target_file"
        else
            echo -e "${YELLOW}❌ File not found: $input.html${NC}"
            echo -e "${BLUE}Available files:${NC}"
            for file in "$SCRIPT_DIR"/*.html; do
                if [ -f "$file" ]; then
                    echo "  - $(basename "$file" .html)"
                fi
            done
            return 1
        fi
    fi
}

main "$@"
EOF

    chmod +x "$LINKS_DIR/open.sh"
    print_success "Created launcher script: $LINKS_DIR/open.sh"
}

create_desktop_shortcuts() {
    print_info "Creating desktop shortcuts..."
    
    local desktop_dir="$HOME/Desktop"
    
    if [ -d "$desktop_dir" ]; then
        # Create desktop shortcut for the launcher
        cat > "$desktop_dir/Unhinged-HTML.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Unhinged HTML Files
Comment=Quick access to Unhinged HTML interfaces
Exec=$LINKS_DIR/open.sh
Icon=applications-internet
Terminal=true
Categories=Development;
EOF
        
        chmod +x "$desktop_dir/Unhinged-HTML.desktop"
        print_success "Created desktop shortcut: ~/Desktop/Unhinged-HTML.desktop"
    else
        print_warning "Desktop directory not found, skipping desktop shortcut"
    fi
}

create_aliases_file() {
    print_info "Creating shell aliases..."
    
    cat > "$LINKS_DIR/aliases.sh" << EOF
#!/bin/bash
# Unhinged HTML File Aliases
# Source this file in your ~/.bashrc or ~/.zshrc:
# source $LINKS_DIR/aliases.sh

# Quick access aliases
alias unhinged-dashboard='$LINKS_DIR/open.sh dashboard'
alias unhinged-audio='$LINKS_DIR/open.sh audio'
alias unhinged-vision='$LINKS_DIR/open.sh vision'
alias unhinged-context='$LINKS_DIR/open.sh context'
alias unhinged-backend='$LINKS_DIR/open.sh backend'
alias unhinged-chat='$LINKS_DIR/open.sh chat'
alias unhinged-html='$LINKS_DIR/open.sh'

# Alternative short aliases
alias uh-dash='$LINKS_DIR/open.sh dashboard'
alias uh-audio='$LINKS_DIR/open.sh audio'
alias uh-vision='$LINKS_DIR/open.sh vision'
alias uh-context='$LINKS_DIR/open.sh context'
alias uh-backend='$LINKS_DIR/open.sh backend'
alias uh-chat='$LINKS_DIR/open.sh chat'
alias uh='$LINKS_DIR/open.sh'

echo "🧠 Unhinged HTML aliases loaded!"
echo "Usage: unhinged-dashboard, unhinged-audio, uh-dash, uh, etc."
EOF

    print_success "Created aliases file: $LINKS_DIR/aliases.sh"
}

show_usage_instructions() {
    echo ""
    echo -e "${CYAN}🎯 Setup Complete! Here's how to use it:${NC}"
    echo ""
    echo -e "${GREEN}📁 HTML Links Directory:${NC}"
    echo "   $LINKS_DIR"
    echo ""
    echo -e "${GREEN}🚀 Quick Access Methods:${NC}"
    echo ""
    echo -e "${YELLOW}1. Direct File Access:${NC}"
    echo "   cd $LINKS_DIR"
    echo "   open dashboard.html    # or double-click in file manager"
    echo ""
    echo -e "${YELLOW}2. Launcher Script:${NC}"
    echo "   $LINKS_DIR/open.sh                    # Show menu"
    echo "   $LINKS_DIR/open.sh dashboard          # Open by name"
    echo "   $LINKS_DIR/open.sh 1                  # Open by number"
    echo ""
    echo -e "${YELLOW}3. Shell Aliases (add to ~/.bashrc):${NC}"
    echo "   source $LINKS_DIR/aliases.sh"
    echo "   unhinged-dashboard                    # Quick access"
    echo "   uh-dash                               # Short alias"
    echo "   uh                                    # Show menu"
    echo ""
    echo -e "${YELLOW}4. Desktop Shortcut:${NC}"
    echo "   Double-click 'Unhinged-HTML' on desktop"
    echo ""
    echo -e "${GREEN}📋 Available HTML Files:${NC}"
    for file in "$LINKS_DIR"/*.html; do
        if [ -f "$file" ]; then
            local basename=$(basename "$file" .html)
            local target=$(readlink "$file" 2>/dev/null || echo "Direct file")
            echo "   🔗 $basename.html -> $(basename "$target")"
        fi
    done
    echo ""
    echo -e "${BLUE}💡 Pro Tip: Bookmark file://$LINKS_DIR/ in your browser!${NC}"
}

main() {
    print_header
    
    create_links_directory
    create_symlinks
    create_launcher_script
    create_desktop_shortcuts
    create_aliases_file
    show_usage_instructions
    
    echo ""
    print_success "🎉 HTML symlink setup complete!"
}

# Run main function
main "$@"
