#!/bin/bash

# ============================================================================
# Install Unhinged HTML Aliases
# Adds convenient shell aliases for quick HTML file access
# ============================================================================

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Get project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ALIASES_FILE="$PROJECT_ROOT/static_html/html-links/aliases.sh"

install_aliases() {
    print_info "Installing Unhinged HTML aliases..."
    
    if [ ! -f "$ALIASES_FILE" ]; then
        print_error "Aliases file not found. Run ./scripts/setup-html-links.sh first."
        exit 1
    fi
    
    # Detect shell
    local shell_rc=""
    if [ -n "$BASH_VERSION" ]; then
        shell_rc="$HOME/.bashrc"
    elif [ -n "$ZSH_VERSION" ]; then
        shell_rc="$HOME/.zshrc"
    else
        print_warning "Could not detect shell type. Please manually add to your shell config."
        echo "Add this line to your shell config file:"
        echo "source $ALIASES_FILE"
        return 0
    fi
    
    # Check if already installed
    if grep -q "source.*aliases.sh" "$shell_rc" 2>/dev/null; then
        print_warning "Aliases already installed in $shell_rc"
        return 0
    fi
    
    # Add to shell config
    echo "" >> "$shell_rc"
    echo "# Unhinged HTML aliases" >> "$shell_rc"
    echo "source $ALIASES_FILE" >> "$shell_rc"
    
    print_success "Added aliases to $shell_rc"
    print_info "Restart your terminal or run: source $shell_rc"
}

show_available_aliases() {
    echo ""
    print_info "Available aliases after restart:"
    echo ""
    echo "  unhinged-dashboard  (or uh-dash)  - Open health dashboard"
    echo "  unhinged-audio      (or uh-audio) - Open audio interface"
    echo "  unhinged-vision     (or uh-vision)- Open vision interface"
    echo "  unhinged-context    (or uh-context)- Open context interface"
    echo "  unhinged-backend    (or uh-backend)- Open backend interface"
    echo "  unhinged-chat       (or uh-chat)  - Open chat interface"
    echo "  unhinged-html       (or uh)       - Show all files menu"
    echo ""
}

main() {
    echo -e "${BLUE}🔗 Unhinged HTML Aliases Installer${NC}"
    echo "=================================="
    
    install_aliases
    show_available_aliases
    
    print_success "🎉 Installation complete!"
}

main "$@"
