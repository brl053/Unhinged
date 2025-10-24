#!/bin/bash
#
# @llm-type platform
# @llm-legend docker-entrypoint.sh - platform infrastructure component
# @llm-key Core functionality for docker-entrypoint
# @llm-map Part of the Unhinged system architecture
# @llm-axiom Maintains system independence and architectural compliance
# @llm-contract Provides standardized interface for system integration
# @llm-token docker-entrypoint: platform infrastructure component
#
# ============================================================================
# Persistence Platform - Docker Entrypoint Script
# ============================================================================
#
# @file docker-entrypoint.sh
# @version 1.0.0
# @author Unhinged Team
# @date 2025-10-19
# @description Docker container entrypoint script for the Persistence Platform
#
# This script handles container startup, environment validation, dependency
# checks, and graceful application startup with proper logging and error handling.
#
# ============================================================================

set -euo pipefail

# ==========================================================================
# Configuration and Constants
# ==========================================================================

readonly SCRIPT_NAME="$(basename "$0")"
readonly APP_JAR="/app/persistence-platform.jar"
readonly CONFIG_PATH="${CONFIG_PATH:-/app/config/persistence-platform.yaml}"
readonly LOG_LEVEL="${LOG_LEVEL:-INFO}"
readonly SERVER_PORT="${SERVER_PORT:-8090}"
readonly GRPC_PORT="${GRPC_PORT:-9090}"

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# ==========================================================================
# Logging Functions
# ==========================================================================

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] [${SCRIPT_NAME}] $*${NC}" >&2
}

log_info() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] [INFO] [${SCRIPT_NAME}] $*${NC}" >&2
}

log_warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] [WARN] [${SCRIPT_NAME}] $*${NC}" >&2
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] [ERROR] [${SCRIPT_NAME}] $*${NC}" >&2
}

# ==========================================================================
# Utility Functions
# ==========================================================================

# Check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if a port is available
port_available() {
    local port=$1
    ! nc -z localhost "$port" 2>/dev/null
}

# Wait for a service to be available
wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3
    local timeout=${4:-60}
    local count=0
    
    log_info "Waiting for $service_name at $host:$port..."
    
    while ! nc -z "$host" "$port" 2>/dev/null; do
        if [ $count -ge $timeout ]; then
            log_error "Timeout waiting for $service_name at $host:$port"
            return 1
        fi
        
        count=$((count + 1))
        sleep 1
    done
    
    log_info "$service_name is available at $host:$port"
    return 0
}

# ==========================================================================
# Validation Functions
# ==========================================================================

validate_environment() {
    log_info "Validating environment..."
    
    # Check Java installation
    if ! command_exists java; then
        log_error "Java is not installed or not in PATH"
        exit 1
    fi
    
    local java_version
    java_version=$(java -version 2>&1 | head -n 1 | cut -d'"' -f2)
    log_info "Java version: $java_version"
    
    # Check application JAR
    if [[ ! -f "$APP_JAR" ]]; then
        log_error "Application JAR not found: $APP_JAR"
        exit 1
    fi
    
    # Check configuration file
    if [[ ! -f "$CONFIG_PATH" ]]; then
        log_error "Configuration file not found: $CONFIG_PATH"
        exit 1
    fi
    
    # Check required directories
    local dirs=("/app/logs" "/app/data" "/app/tmp")
    for dir in "${dirs[@]}"; do
        if [[ ! -d "$dir" ]]; then
            log_warn "Directory not found, creating: $dir"
            mkdir -p "$dir"
        fi
    done
    
    # Check port availability
    if ! port_available "$SERVER_PORT"; then
        log_error "Port $SERVER_PORT is already in use"
        exit 1
    fi
    
    if ! port_available "$GRPC_PORT"; then
        log_error "Port $GRPC_PORT is already in use"
        exit 1
    fi
    
    log_info "Environment validation completed successfully"
}

validate_configuration() {
    log_info "Validating configuration file: $CONFIG_PATH"
    
    # Basic YAML syntax check
    if command_exists python3; then
        python3 -c "
import yaml
import sys
try:
    with open('$CONFIG_PATH', 'r') as f:
        yaml.safe_load(f)
    print('Configuration file is valid YAML')
except Exception as e:
    print(f'Configuration file is invalid: {e}')
    sys.exit(1)
" || {
            log_error "Configuration file validation failed"
            exit 1
        }
    else
        log_warn "Python3 not available, skipping YAML validation"
    fi
    
    log_info "Configuration validation completed"
}

# ==========================================================================
# Dependency Check Functions
# ==========================================================================

check_database_dependencies() {
    log_info "Checking database dependencies..."
    
    # Define database services and their default ports
    local -A databases=(
        ["redis"]="6379"
        ["cockroachdb"]="26257"
        ["mongodb"]="27017"
        ["weaviate"]="8080"
        ["elasticsearch"]="9200"
        ["cassandra"]="9042"
        ["neo4j"]="7687"
        ["minio"]="9000"
    )
    
    local failed_services=()
    
    for service in "${!databases[@]}"; do
        local port="${databases[$service]}"
        
        # Try to connect to the service
        if wait_for_service "$service" "$port" "$service" 10; then
            log_info "✅ $service is available"
        else
            log_warn "⚠️  $service is not available at $service:$port"
            failed_services+=("$service")
        fi
    done
    
    if [[ ${#failed_services[@]} -gt 0 ]]; then
        log_warn "Some database services are not available: ${failed_services[*]}"
        log_warn "The platform will start but some features may not work properly"
    else
        log_info "All database dependencies are available"
    fi
}

# ==========================================================================
# Application Startup Functions
# ==========================================================================

setup_jvm_options() {
    log_info "Setting up JVM options..."
    
    # Base JVM options
    local jvm_opts=(
        "-server"
        "-Djava.awt.headless=true"
        "-Djava.security.egd=file:/dev/./urandom"
        "-Dfile.encoding=UTF-8"
        "-Duser.timezone=UTC"
    )
    
    # Memory settings
    jvm_opts+=(
        "-Xmx${JAVA_MAX_HEAP:-2g}"
        "-Xms${JAVA_MIN_HEAP:-1g}"
        "-XX:+UseG1GC"
        "-XX:+UseStringDeduplication"
        "-XX:+OptimizeStringConcat"
    )
    
    # GC settings
    jvm_opts+=(
        "-XX:+UnlockExperimentalVMOptions"
        "-XX:+UseCGroupMemoryLimitForHeap"
        "-XX:MaxGCPauseMillis=200"
        "-XX:G1HeapRegionSize=16m"
    )
    
    # Debugging and monitoring
    if [[ "${JAVA_DEBUG:-false}" == "true" ]]; then
        jvm_opts+=(
            "-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=*:5005"
        )
        log_info "Java debugging enabled on port 5005"
    fi
    
    # JMX monitoring
    if [[ "${JMX_ENABLED:-false}" == "true" ]]; then
        jvm_opts+=(
            "-Dcom.sun.management.jmxremote"
            "-Dcom.sun.management.jmxremote.port=9999"
            "-Dcom.sun.management.jmxremote.authenticate=false"
            "-Dcom.sun.management.jmxremote.ssl=false"
        )
        log_info "JMX monitoring enabled on port 9999"
    fi
    
    # Export JVM options
    export JAVA_OPTS="${JAVA_OPTS:-} ${jvm_opts[*]}"
    
    log_info "JVM options configured: $JAVA_OPTS"
}

start_application() {
    log_info "Starting Unhinged Persistence Platform..."
    log_info "Configuration: $CONFIG_PATH"
    log_info "Log Level: $LOG_LEVEL"
    log_info "REST API Port: $SERVER_PORT"
    log_info "gRPC Port: $GRPC_PORT"
    
    # Setup signal handlers for graceful shutdown
    trap 'log_info "Received SIGTERM, shutting down gracefully..."; kill -TERM $PID; wait $PID' TERM
    trap 'log_info "Received SIGINT, shutting down gracefully..."; kill -INT $PID; wait $PID' INT
    
    # Start the application
    exec java $JAVA_OPTS \
        -Dlogback.configurationFile=/app/config/logback.xml \
        -Dlog.level="$LOG_LEVEL" \
        -Dserver.port="$SERVER_PORT" \
        -Dgrpc.port="$GRPC_PORT" \
        -jar "$APP_JAR" \
        "$CONFIG_PATH" &
    
    PID=$!
    log_info "Application started with PID: $PID"
    
    # Wait for the application to start
    sleep 5
    
    # Check if the application is still running
    if ! kill -0 $PID 2>/dev/null; then
        log_error "Application failed to start"
        exit 1
    fi
    
    log_info "🚀 Unhinged Persistence Platform started successfully!"
    log_info "🌐 REST API: http://localhost:$SERVER_PORT/api/v1"
    log_info "🔧 Health Check: http://localhost:$SERVER_PORT/api/v1/health"
    log_info "📊 Metrics: http://localhost:$SERVER_PORT/api/v1/metrics"
    
    # Wait for the application to finish
    wait $PID
}

# ==========================================================================
# Main Execution
# ==========================================================================

main() {
    log_info "🚀 Starting Unhinged Persistence Platform container..."
    log_info "Version: 1.0.0"
    log_info "Build Date: $(date)"
    
    # Validate environment and configuration
    validate_environment
    validate_configuration
    
    # Check database dependencies
    check_database_dependencies
    
    # Setup JVM options
    setup_jvm_options
    
    # Start the application
    start_application
}

# Execute main function
main "$@"
