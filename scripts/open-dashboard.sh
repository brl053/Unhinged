#!/bin/bash

# ============================================================================
# Unhinged Health Dashboard HTML Launcher
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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
    echo -e "${BLUE}🧠 Unhinged Health Dashboard HTML Launcher${NC}"
    echo "=================================================="
}

open_dashboard() {
    local dashboard_file="unhinged-health-dashboard.html"
    
    if [ ! -f "$dashboard_file" ]; then
        print_error "Dashboard file not found: $dashboard_file"
        exit 1
    fi
    
    local full_path=$(realpath "$dashboard_file")
    local file_url="file://$full_path"
    
    print_info "Opening Unhinged Health Dashboard..."
    print_info "File: $full_path"
    
    # Try different methods to open the browser
    if command -v xdg-open &> /dev/null; then
        # Linux
        xdg-open "$file_url" &> /dev/null &
        print_success "Dashboard opened with xdg-open"
    elif command -v open &> /dev/null; then
        # macOS
        open "$file_url" &> /dev/null &
        print_success "Dashboard opened with open"
    elif command -v start &> /dev/null; then
        # Windows (Git Bash/WSL)
        start "$file_url" &> /dev/null &
        print_success "Dashboard opened with start"
    else
        print_warning "Could not detect browser launcher"
        print_info "Please manually open: $file_url"
    fi
    
    echo ""
    echo "🎯 Dashboard Information:"
    echo "   📁 File: $dashboard_file"
    echo "   🌐 URL: $file_url"
    echo ""
    echo "📋 Features:"
    echo "   ✅ Real-time health monitoring"
    echo "   🔄 Auto-refresh every 30 seconds"
    echo "   🎨 Modern dark theme interface"
    echo "   📱 Fully responsive design"
    echo ""
    echo "🔧 Services Monitored:"
    echo "   🚀 Backend (8080)"
    echo "   🐘 Database (5433)"
    echo "   👁️  Vision AI (8001)"
    echo "   🎤 Whisper TTS (8000)"
    echo "   🧠 Context LLM (8002)"
    echo "   📊 Grafana (3001)"
    echo "   📈 Prometheus (9090)"
    echo "   📝 Loki (3100)"
    echo ""
    echo "💡 Tips:"
    echo "   • No server required - runs directly in browser"
    echo "   • Click service cards for individual health checks"
    echo "   • Use Quick Actions for testing endpoints"
    echo "   • Toggle auto-refresh as needed"
    echo ""
    echo "🔧 Troubleshooting:"
    echo "   • If services show offline, ensure they're running"
    echo "   • Check browser console for CORS errors"
    echo "   • Refresh page to reset all checks"
}

show_usage() {
    echo "Usage: $0"
    echo ""
    echo "Opens the Unhinged Health Dashboard HTML file in your default browser."
    echo ""
    echo "The dashboard provides real-time monitoring of all Unhinged services"
    echo "without requiring a separate server - it runs directly in your browser."
}

main() {
    print_header
    
    # Parse arguments
    case "${1:-}" in
        -h|--help)
            show_usage
            exit 0
            ;;
        "")
            # No arguments, proceed normally
            ;;
        *)
            print_error "Invalid argument: $1"
            show_usage
            exit 1
            ;;
    esac
    
    open_dashboard
}

# Run main function
main "$@"
