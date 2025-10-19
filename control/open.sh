#!/bin/bash

# Unhinged Control Plane - Browser Launcher
# Quick access to all control plane interfaces

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STATIC_HTML_DIR="$SCRIPT_DIR/static_html"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🎛️ Unhinged Control Plane - Browser Launcher${NC}"
echo "=================================================="

# Check if static_html directory exists
if [ ! -d "$STATIC_HTML_DIR" ]; then
    echo -e "${RED}❌ Error: static_html directory not found at $STATIC_HTML_DIR${NC}"
    exit 1
fi

# Function to open URL in browser
open_url() {
    local url="$1"
    local description="$2"
    
    echo -e "${GREEN}🌐 Opening: $description${NC}"
    echo -e "${BLUE}   URL: $url${NC}"
    
    # Try different browser opening methods
    if command -v xdg-open > /dev/null; then
        xdg-open "$url" 2>/dev/null &
    elif command -v open > /dev/null; then
        open "$url" 2>/dev/null &
    elif command -v firefox > /dev/null; then
        firefox "$url" 2>/dev/null &
    elif command -v google-chrome > /dev/null; then
        google-chrome "$url" 2>/dev/null &
    elif command -v chromium > /dev/null; then
        chromium "$url" 2>/dev/null &
    else
        echo -e "${YELLOW}⚠️  Could not detect browser. Please manually open: $url${NC}"
    fi
}

# Function to check if DAG server is running
check_dag_server() {
    if curl -s http://localhost:9000/dag/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ DAG Control Plane server is running${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  DAG Control Plane server not running${NC}"
        echo -e "${BLUE}   Start with: python3 -m control${NC}"
        return 1
    fi
}

# Main menu
show_menu() {
    echo
    echo "Available interfaces:"
    echo "1) DAG Control Dashboard"
    echo "2) System Status & Monitoring"
    echo "3) Text Generation Test"
    echo "4) Vision AI Test"
    echo "5) Voice Processing Test"
    echo "6) All Interfaces (opens all tabs)"
    echo "7) Check DAG Server Status"
    echo "8) Start DAG Server"
    echo "q) Quit"
    echo
}

# Handle user choice
handle_choice() {
    local choice="$1"
    
    case $choice in
        1)
            open_url "file://$STATIC_HTML_DIR/dag-control.html" "DAG Control Dashboard"
            ;;
        2)
            open_url "file://$STATIC_HTML_DIR/index.html" "System Status & Monitoring"
            ;;
        3)
            open_url "file://$STATIC_HTML_DIR/text-test.html" "Text Generation Test"
            ;;
        4)
            open_url "file://$STATIC_HTML_DIR/image-test.html" "Vision AI Test"
            ;;
        5)
            open_url "file://$STATIC_HTML_DIR/voice-test.html" "Voice Processing Test"
            ;;
        6)
            echo -e "${GREEN}🚀 Opening all interfaces...${NC}"
            open_url "file://$STATIC_HTML_DIR/dag-control.html" "DAG Control Dashboard"
            sleep 1
            open_url "file://$STATIC_HTML_DIR/index.html" "System Status & Monitoring"
            sleep 1
            open_url "file://$STATIC_HTML_DIR/text-test.html" "Text Generation Test"
            sleep 1
            open_url "file://$STATIC_HTML_DIR/image-test.html" "Vision AI Test"
            sleep 1
            open_url "file://$STATIC_HTML_DIR/voice-test.html" "Voice Processing Test"
            ;;
        7)
            check_dag_server
            ;;
        8)
            echo -e "${BLUE}🎛️ Starting DAG Control Plane server...${NC}"
            echo -e "${YELLOW}   Press Ctrl+C to stop the server${NC}"
            cd "$SCRIPT_DIR/.."
            python3 -m control
            ;;
        q|Q)
            echo -e "${GREEN}👋 Goodbye!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Invalid choice. Please try again.${NC}"
            ;;
    esac
}

# Check if running with arguments
if [ $# -gt 0 ]; then
    case "$1" in
        --dag|--control)
            open_url "file://$STATIC_HTML_DIR/dag-control.html" "DAG Control Dashboard"
            ;;
        --status|--monitor)
            open_url "file://$STATIC_HTML_DIR/index.html" "System Status & Monitoring"
            ;;
        --text)
            open_url "file://$STATIC_HTML_DIR/text-test.html" "Text Generation Test"
            ;;
        --vision|--image)
            open_url "file://$STATIC_HTML_DIR/image-test.html" "Vision AI Test"
            ;;
        --voice|--audio)
            open_url "file://$STATIC_HTML_DIR/voice-test.html" "Voice Processing Test"
            ;;
        --all)
            handle_choice 6
            ;;
        --server)
            handle_choice 8
            ;;
        --help|-h)
            echo "Usage: $0 [option]"
            echo "Options:"
            echo "  --dag, --control    Open DAG Control Dashboard"
            echo "  --status, --monitor Open System Status & Monitoring"
            echo "  --text              Open Text Generation Test"
            echo "  --vision, --image   Open Vision AI Test"
            echo "  --voice, --audio    Open Voice Processing Test"
            echo "  --all               Open all interfaces"
            echo "  --server            Start DAG server"
            echo "  --help, -h          Show this help"
            ;;
        *)
            echo -e "${RED}❌ Unknown option: $1${NC}"
            echo "Use --help for available options"
            exit 1
            ;;
    esac
    exit 0
fi

# Interactive mode
check_dag_server

while true; do
    show_menu
    read -p "Choose an option: " choice
    handle_choice "$choice"
    echo
done
