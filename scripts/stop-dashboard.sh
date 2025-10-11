#!/bin/bash

# ============================================================================
# Unhinged Health Dashboard Stopper
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

stop_dashboard() {
    print_info "Stopping Unhinged Health Dashboard..."
    
    # Check for saved PID
    if [ -f /tmp/unhinged-dashboard.pid ]; then
        local pid=$(cat /tmp/unhinged-dashboard.pid)
        if kill -0 $pid 2>/dev/null; then
            kill $pid
            print_success "Dashboard server stopped (PID: $pid)"
            rm -f /tmp/unhinged-dashboard.pid
        else
            print_warning "Dashboard server not running (stale PID file)"
            rm -f /tmp/unhinged-dashboard.pid
        fi
    else
        # Try to find and kill dashboard processes
        local pids=$(pgrep -f "serve.py" 2>/dev/null || true)
        if [ -n "$pids" ]; then
            echo "$pids" | xargs kill 2>/dev/null || true
            print_success "Dashboard server processes stopped"
        else
            print_warning "No dashboard server processes found"
        fi
    fi
    
    # Also check for any Python processes serving on common dashboard ports
    for port in 8888 8889 9999; do
        local pid=$(lsof -ti :$port 2>/dev/null || true)
        if [ -n "$pid" ]; then
            local cmd=$(ps -p $pid -o comm= 2>/dev/null || true)
            if [[ "$cmd" == *"python"* ]]; then
                kill $pid 2>/dev/null || true
                print_info "Stopped process on port $port (PID: $pid)"
            fi
        fi
    done
    
    print_success "Dashboard shutdown complete"
}

main() {
    echo -e "${BLUE}🛑 Unhinged Health Dashboard Stopper${NC}"
    echo "=============================================="
    
    stop_dashboard
}

# Run main function
main "$@"
