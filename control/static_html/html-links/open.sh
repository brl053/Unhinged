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
