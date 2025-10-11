#!/bin/bash

# Unhinged Health Dashboard Launcher
# Quick launcher for the health dashboard with multiple access methods

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DASHBOARD_FILE="$SCRIPT_DIR/index.html"

echo -e "${BLUE}🧠 Unhinged Health Dashboard Launcher${NC}"
echo "========================================"
echo ""

# Check if dashboard file exists
if [ ! -f "$DASHBOARD_FILE" ]; then
    echo -e "${YELLOW}❌ Dashboard file not found: $DASHBOARD_FILE${NC}"
    exit 1
fi

echo "Available options:"
echo ""
echo -e "${GREEN}1.${NC} Open via HTTP server (recommended)"
echo -e "${GREEN}2.${NC} Open directly in browser (file:// protocol)"
echo -e "${GREEN}3.${NC} Start HTTP server only"
echo ""

read -p "Choose option (1-3): " choice

case $choice in
    1)
        echo -e "${GREEN}🚀 Starting HTTP server and opening dashboard...${NC}"
        
        # Start server in background
        cd "$SCRIPT_DIR"
        python3 -m http.server 8899 > /dev/null 2>&1 &
        SERVER_PID=$!
        
        # Wait a moment for server to start
        sleep 2
        
        # Open in browser
        if command -v xdg-open &> /dev/null; then
            xdg-open "http://localhost:8899" &> /dev/null &
        elif command -v open &> /dev/null; then
            open "http://localhost:8899" &> /dev/null &
        else
            echo -e "${YELLOW}⚠️ Could not detect browser launcher${NC}"
            echo -e "${BLUE}Please manually open: http://localhost:8899${NC}"
        fi
        
        echo -e "${GREEN}✅ Dashboard opened at: http://localhost:8899${NC}"
        echo -e "${BLUE}📍 Server PID: $SERVER_PID${NC}"
        echo -e "${YELLOW}💡 To stop server: kill $SERVER_PID${NC}"
        ;;
        
    2)
        echo -e "${GREEN}🔗 Opening dashboard directly in browser...${NC}"
        
        local_file="file://$DASHBOARD_FILE"
        
        if command -v xdg-open &> /dev/null; then
            xdg-open "$local_file" &> /dev/null &
        elif command -v open &> /dev/null; then
            open "$local_file" &> /dev/null &
        else
            echo -e "${YELLOW}⚠️ Could not detect browser launcher${NC}"
            echo -e "${BLUE}Please manually open: $local_file${NC}"
        fi
        
        echo -e "${GREEN}✅ Dashboard opened: $local_file${NC}"
        echo -e "${YELLOW}💡 Note: Some features may be limited with file:// protocol${NC}"
        ;;
        
    3)
        echo -e "${GREEN}🖥️ Starting HTTP server only...${NC}"
        
        cd "$SCRIPT_DIR"
        echo -e "${BLUE}📍 Server starting at: http://localhost:8899${NC}"
        echo -e "${YELLOW}💡 Press Ctrl+C to stop${NC}"
        echo ""
        
        python3 -m http.server 8899
        ;;
        
    *)
        echo -e "${YELLOW}❌ Invalid option. Please choose 1, 2, or 3.${NC}"
        exit 1
        ;;
esac
