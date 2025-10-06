#!/bin/bash

# ============================================================================
# Unhinged Backend - Production Build Script
# ============================================================================
#
# @file build-backend.sh
# @version 1.0.0
# @author Unhinged Team
# @date 2025-01-06
# @description Production-ready build script for Unhinged Backend
#
# This script automates the complete build process including:
# - Protobuf generation from proto files
# - Kotlin compilation with proper memory settings
# - Production build with all optimizations
# - Health check and validation
#
# Usage:
#   ./build-backend.sh [clean|build|run|test|all]
#
# ============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKEND_DIR="backend"
PROTO_DIR="proto"
BUILD_PORT=8081

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "🔍 Checking prerequisites..."
    
    # Check Java
    if ! command -v java &> /dev/null; then
        log_error "Java is not installed or not in PATH"
        exit 1
    fi
    
    # Check if backend directory exists
    if [ ! -d "$BACKEND_DIR" ]; then
        log_error "Backend directory not found: $BACKEND_DIR"
        exit 1
    fi
    
    # Check if proto directory exists
    if [ ! -d "$PROTO_DIR" ]; then
        log_error "Proto directory not found: $PROTO_DIR"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Clean build artifacts
clean_build() {
    log_info "🧹 Cleaning build artifacts..."
    cd "$BACKEND_DIR"
    ./gradlew clean
    cd ..
    log_success "Build artifacts cleaned"
}

# Generate protobuf files
generate_protobuf() {
    log_info "🔧 Generating protobuf files..."
    cd "$BACKEND_DIR"
    ./gradlew generateProto
    cd ..
    log_success "Protobuf files generated successfully"
}

# Compile Kotlin code
compile_kotlin() {
    log_info "⚙️  Compiling Kotlin code..."
    cd "$BACKEND_DIR"
    ./gradlew compileKotlin
    cd ..
    log_success "Kotlin compilation successful"
}

# Build the application
build_application() {
    log_info "🏗️  Building application..."
    cd "$BACKEND_DIR"
    ./gradlew build
    cd ..
    log_success "Application build successful"
}

# Run the application
run_application() {
    log_info "🚀 Starting Unhinged Backend Server..."
    log_info "Server will be available at: http://localhost:$BUILD_PORT"
    log_info "Press Ctrl+C to stop the server"
    
    cd "$BACKEND_DIR"
    ./gradlew run
}

# Test the application
test_application() {
    log_info "🧪 Running application tests..."
    
    # Start server in background for testing
    cd "$BACKEND_DIR"
    ./gradlew run &
    SERVER_PID=$!
    cd ..
    
    # Wait for server to start
    log_info "Waiting for server to start..."
    sleep 10
    
    # Test endpoints
    log_info "Testing health endpoint..."
    if curl -s http://localhost:$BUILD_PORT/health > /dev/null; then
        log_success "Health endpoint test passed"
    else
        log_error "Health endpoint test failed"
        kill $SERVER_PID 2>/dev/null || true
        exit 1
    fi
    
    log_info "Testing API status endpoint..."
    if curl -s http://localhost:$BUILD_PORT/api/status > /dev/null; then
        log_success "API status endpoint test passed"
    else
        log_error "API status endpoint test failed"
        kill $SERVER_PID 2>/dev/null || true
        exit 1
    fi
    
    # Stop server
    kill $SERVER_PID 2>/dev/null || true
    log_success "All tests passed"
}

# Show usage
show_usage() {
    echo "Usage: $0 [clean|build|run|test|all]"
    echo ""
    echo "Commands:"
    echo "  clean  - Clean build artifacts"
    echo "  build  - Build the application (includes protobuf generation)"
    echo "  run    - Run the application"
    echo "  test   - Run tests"
    echo "  all    - Clean, build, and test"
    echo ""
    echo "Examples:"
    echo "  $0 build    # Build the application"
    echo "  $0 run      # Run the application"
    echo "  $0 all      # Full build and test cycle"
}

# Main execution
main() {
    echo "============================================================================"
    echo "🚀 Unhinged Backend - Production Build Pipeline"
    echo "============================================================================"
    
    check_prerequisites
    
    case "${1:-build}" in
        "clean")
            clean_build
            ;;
        "build")
            generate_protobuf
            compile_kotlin
            build_application
            log_success "🎉 Build completed successfully!"
            log_info "To run the server: $0 run"
            ;;
        "run")
            run_application
            ;;
        "test")
            test_application
            ;;
        "all")
            clean_build
            generate_protobuf
            compile_kotlin
            build_application
            test_application
            log_success "🎉 Full build and test cycle completed successfully!"
            ;;
        "help"|"-h"|"--help")
            show_usage
            ;;
        *)
            log_error "Unknown command: $1"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
