#!/bin/bash
# ============================================================================
# Persistence Platform - Health Check Script
# ============================================================================
#
# @file health-check.sh
# @version 1.0.0
# @author Unhinged Team
# @date 2025-10-19
# @description Docker health check script for the Persistence Platform
#
# This script performs comprehensive health checks on the persistence platform
# including API availability, database connectivity, and system resources.
#
# ============================================================================

set -euo pipefail

# ==========================================================================
# Configuration
# ==========================================================================

readonly SCRIPT_NAME="$(basename "$0")"
readonly SERVER_PORT="${SERVER_PORT:-8090}"
readonly GRPC_PORT="${GRPC_PORT:-9090}"
readonly HEALTH_ENDPOINT="http://localhost:${SERVER_PORT}/api/v1/health"
readonly METRICS_ENDPOINT="http://localhost:${SERVER_PORT}/api/v1/metrics"
readonly TIMEOUT=10

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m' # No Color

# ==========================================================================
# Logging Functions
# ==========================================================================

log_info() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] [HEALTH] $*${NC}" >&2
}

log_warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] [HEALTH] $*${NC}" >&2
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] [HEALTH] $*${NC}" >&2
}

# ==========================================================================
# Health Check Functions
# ==========================================================================

# Check if the REST API is responding
check_rest_api() {
    log_info "Checking REST API health..."
    
    local response
    local http_code
    
    if ! command -v curl >/dev/null 2>&1; then
        log_error "curl command not found"
        return 1
    fi
    
    # Make health check request
    response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
        --max-time "$TIMEOUT" \
        --connect-timeout 5 \
        "$HEALTH_ENDPOINT" 2>/dev/null || echo "HTTPSTATUS:000")
    
    # Extract HTTP status code
    http_code=$(echo "$response" | grep -o "HTTPSTATUS:[0-9]*" | cut -d: -f2)
    
    # Check HTTP status
    if [[ "$http_code" == "200" ]]; then
        log_info "✅ REST API is healthy (HTTP $http_code)"
        return 0
    elif [[ "$http_code" == "000" ]]; then
        log_error "❌ REST API is not responding (connection failed)"
        return 1
    else
        log_error "❌ REST API returned HTTP $http_code"
        return 1
    fi
}

# Check if the gRPC API is responding
check_grpc_api() {
    log_info "Checking gRPC API health..."
    
    # Check if gRPC port is listening
    if nc -z localhost "$GRPC_PORT" 2>/dev/null; then
        log_info "✅ gRPC API port is listening ($GRPC_PORT)"
        return 0
    else
        log_error "❌ gRPC API port is not listening ($GRPC_PORT)"
        return 1
    fi
}

# Check application process
check_process() {
    log_info "Checking application process..."
    
    # Look for Java process running the persistence platform
    if pgrep -f "persistence-platform.jar" >/dev/null 2>&1; then
        log_info "✅ Application process is running"
        return 0
    else
        log_error "❌ Application process not found"
        return 1
    fi
}

# Check system resources
check_system_resources() {
    log_info "Checking system resources..."
    
    local warnings=0
    
    # Check memory usage
    if [[ -f /proc/meminfo ]]; then
        local mem_total mem_available mem_usage_percent
        mem_total=$(grep MemTotal /proc/meminfo | awk '{print $2}')
        mem_available=$(grep MemAvailable /proc/meminfo | awk '{print $2}')
        mem_usage_percent=$(( (mem_total - mem_available) * 100 / mem_total ))
        
        if [[ $mem_usage_percent -gt 90 ]]; then
            log_warn "⚠️  High memory usage: ${mem_usage_percent}%"
            warnings=$((warnings + 1))
        else
            log_info "✅ Memory usage: ${mem_usage_percent}%"
        fi
    fi
    
    # Check disk space
    local disk_usage
    disk_usage=$(df /app 2>/dev/null | tail -1 | awk '{print $5}' | sed 's/%//' || echo "0")
    
    if [[ $disk_usage -gt 90 ]]; then
        log_warn "⚠️  High disk usage: ${disk_usage}%"
        warnings=$((warnings + 1))
    else
        log_info "✅ Disk usage: ${disk_usage}%"
    fi
    
    # Check load average
    if [[ -f /proc/loadavg ]]; then
        local load_avg
        load_avg=$(cut -d' ' -f1 /proc/loadavg)
        local cpu_count
        cpu_count=$(nproc)
        
        # Convert to integer comparison (multiply by 100)
        local load_int cpu_threshold
        load_int=$(echo "$load_avg * 100" | bc 2>/dev/null || echo "0")
        cpu_threshold=$(echo "$cpu_count * 200" | bc 2>/dev/null || echo "200") # 2x CPU count
        
        if [[ $load_int -gt $cpu_threshold ]]; then
            log_warn "⚠️  High load average: $load_avg (CPUs: $cpu_count)"
            warnings=$((warnings + 1))
        else
            log_info "✅ Load average: $load_avg (CPUs: $cpu_count)"
        fi
    fi
    
    if [[ $warnings -eq 0 ]]; then
        return 0
    else
        log_warn "System resource warnings: $warnings"
        return 0  # Don't fail health check for resource warnings
    fi
}

# Check database connectivity (optional)
check_database_connectivity() {
    log_info "Checking database connectivity..."
    
    # Try to get metrics which should include database health
    local response
    local http_code
    
    response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
        --max-time "$TIMEOUT" \
        --connect-timeout 5 \
        "$METRICS_ENDPOINT" 2>/dev/null || echo "HTTPSTATUS:000")
    
    http_code=$(echo "$response" | grep -o "HTTPSTATUS:[0-9]*" | cut -d: -f2)
    
    if [[ "$http_code" == "200" ]]; then
        log_info "✅ Metrics endpoint accessible (database connectivity likely OK)"
        return 0
    else
        log_warn "⚠️  Metrics endpoint not accessible (HTTP $http_code)"
        return 1
    fi
}

# Comprehensive health check
run_health_check() {
    log_info "🏥 Running comprehensive health check..."
    
    local checks_passed=0
    local checks_total=0
    local critical_failed=0
    
    # Critical checks (must pass)
    local critical_checks=(
        "check_process"
        "check_rest_api"
    )
    
    # Optional checks (warnings only)
    local optional_checks=(
        "check_grpc_api"
        "check_system_resources"
        "check_database_connectivity"
    )
    
    # Run critical checks
    for check in "${critical_checks[@]}"; do
        checks_total=$((checks_total + 1))
        if $check; then
            checks_passed=$((checks_passed + 1))
        else
            critical_failed=$((critical_failed + 1))
        fi
    done
    
    # Run optional checks
    for check in "${optional_checks[@]}"; do
        checks_total=$((checks_total + 1))
        if $check; then
            checks_passed=$((checks_passed + 1))
        else
            log_warn "Optional check failed: $check"
        fi
    done
    
    # Summary
    log_info "Health check summary: $checks_passed/$checks_total checks passed"
    
    if [[ $critical_failed -eq 0 ]]; then
        log_info "✅ Health check PASSED"
        return 0
    else
        log_error "❌ Health check FAILED ($critical_failed critical checks failed)"
        return 1
    fi
}

# ==========================================================================
# Main Execution
# ==========================================================================

main() {
    # Check if running in verbose mode
    if [[ "${HEALTH_CHECK_VERBOSE:-false}" == "true" ]]; then
        log_info "Running health check in verbose mode..."
        run_health_check
    else
        # Silent mode - only output errors
        if ! run_health_check >/dev/null 2>&1; then
            log_error "Health check failed"
            exit 1
        fi
    fi
}

# Handle command line arguments
case "${1:-}" in
    --verbose|-v)
        export HEALTH_CHECK_VERBOSE=true
        main
        ;;
    --help|-h)
        echo "Usage: $0 [--verbose|-v] [--help|-h]"
        echo ""
        echo "Docker health check script for Unhinged Persistence Platform"
        echo ""
        echo "Options:"
        echo "  --verbose, -v    Run in verbose mode with detailed output"
        echo "  --help, -h       Show this help message"
        echo ""
        echo "Environment Variables:"
        echo "  SERVER_PORT              REST API port (default: 8090)"
        echo "  GRPC_PORT               gRPC API port (default: 9090)"
        echo "  HEALTH_CHECK_VERBOSE    Enable verbose output (default: false)"
        exit 0
        ;;
    *)
        main
        ;;
esac
