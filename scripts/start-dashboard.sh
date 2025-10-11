#!/bin/bash

# ============================================================================
# Unhinged Health Dashboard Launcher
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DASHBOARD_DIR="static-dashboard"
DEFAULT_PORT=8888

print_header() {
    echo -e "${BLUE}🧠 Unhinged Health Dashboard Launcher${NC}"
    echo "=============================================="
}

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

check_dependencies() {
    print_info "Checking dependencies..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    if [ ! -d "$DASHBOARD_DIR" ]; then
        print_error "Dashboard directory not found: $DASHBOARD_DIR"
        exit 1
    fi
    
    if [ ! -f "$DASHBOARD_DIR/serve.py" ]; then
        print_error "Dashboard server not found: $DASHBOARD_DIR/serve.py"
        exit 1
    fi
    
    print_success "Dependencies check passed"
}

check_port() {
    local port=$1
    if lsof -i :$port &> /dev/null; then
        print_warning "Port $port is already in use"
        return 1
    fi
    return 0
}

find_available_port() {
    local port=$DEFAULT_PORT
    while ! check_port $port; do
        ((port++))
        if [ $port -gt 9999 ]; then
            print_error "No available ports found in range 8888-9999"
            exit 1
        fi
    done
    echo $port
}

start_dashboard() {
    local port=${1:-$DEFAULT_PORT}
    
    if ! check_port $port; then
        print_warning "Port $port is in use, finding alternative..."
        port=$(find_available_port)
        print_info "Using port $port instead"
    fi
    
    print_info "Starting dashboard server on port $port..."
    
    cd "$DASHBOARD_DIR"
    
    # Start the server in background
    python3 serve.py $port &
    local server_pid=$!
    
    # Wait a moment for server to start
    sleep 2
    
    # Check if server started successfully
    if kill -0 $server_pid 2>/dev/null; then
        print_success "Dashboard server started successfully!"
        echo ""
        echo "🎯 Dashboard Access:"
        echo "   URL: http://localhost:$port"
        echo "   PID: $server_pid"
        echo ""
        echo "📋 Available Services:"
        echo "   🚀 Backend:      http://localhost:8080"
        echo "   👁️  Vision AI:    http://localhost:8001"
        echo "   🎤 Whisper TTS:  http://localhost:8000"
        echo "   🧠 Context LLM:  http://localhost:8002"
        echo "   📊 Grafana:      http://localhost:3001"
        echo "   📈 Prometheus:   http://localhost:9090"
        echo "   📝 Loki:         http://localhost:3100"
        echo ""
        echo "💡 Tips:"
        echo "   • Dashboard auto-refreshes every 30 seconds"
        echo "   • Click service cards for detailed health checks"
        echo "   • Use Quick Actions for common operations"
        echo ""
        echo "🛑 To stop the dashboard:"
        echo "   kill $server_pid"
        echo "   or"
        echo "   ./scripts/stop-dashboard.sh"
        
        # Save PID for stop script
        echo $server_pid > /tmp/unhinged-dashboard.pid
        
        # Try to open browser (optional)
        if command -v xdg-open &> /dev/null; then
            print_info "Opening dashboard in browser..."
            xdg-open "http://localhost:$port" &> /dev/null &
        elif command -v open &> /dev/null; then
            print_info "Opening dashboard in browser..."
            open "http://localhost:$port" &> /dev/null &
        fi
        
    else
        print_error "Failed to start dashboard server"
        exit 1
    fi
}

show_usage() {
    echo "Usage: $0 [PORT]"
    echo ""
    echo "Options:"
    echo "  PORT    Port number for dashboard server (default: $DEFAULT_PORT)"
    echo ""
    echo "Examples:"
    echo "  $0           # Start on default port $DEFAULT_PORT"
    echo "  $0 9999      # Start on port 9999"
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
            # Use default port
            ;;
        [0-9]*)
            # Port number provided
            if [ $1 -lt 1024 ] || [ $1 -gt 65535 ]; then
                print_error "Invalid port number: $1 (must be 1024-65535)"
                exit 1
            fi
            DEFAULT_PORT=$1
            ;;
        *)
            print_error "Invalid argument: $1"
            show_usage
            exit 1
            ;;
    esac
    
    check_dependencies
    start_dashboard $DEFAULT_PORT
}

# Run main function
main "$@"
