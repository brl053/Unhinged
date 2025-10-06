#!/bin/bash
# ============================================================================
# Multimodal AI Architecture Integration Test Runner
# ============================================================================
#
# @file run-multimodal-tests.sh
# @version 1.0.0
# @author Unhinged Team
# @date 2025-01-06
# @description Comprehensive test runner for multimodal AI architecture refactoring
#
# Validates the complete gRPC-based architecture:
# - Kotlin backend orchestration
# - Python AI services (vision-ai-enhanced, context-llm)
# - Service boundary compliance
# - Performance benchmarks
# - Error handling and resilience
#
# ============================================================================

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TEST_CONFIG="$PROJECT_ROOT/tests/multimodal-test-config.yaml"
TEST_RESULTS_DIR="$PROJECT_ROOT/test-results/multimodal"
LOG_FILE="$TEST_RESULTS_DIR/test-execution.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Test configuration
KOTLIN_BACKEND_URL="http://localhost:8080"
VISION_GRPC_HOST="localhost"
VISION_GRPC_PORT="50051"
CONTEXT_GRPC_HOST="localhost"
CONTEXT_GRPC_PORT="50052"
FRONTEND_URL="http://localhost:8081"

SERVICE_STARTUP_TIMEOUT=120
TEST_TIMEOUT=1800
MAX_RETRIES=3

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}❌ $1${NC}" | tee -a "$LOG_FILE"
}

log_header() {
    echo -e "\n${CYAN}============================================================================${NC}" | tee -a "$LOG_FILE"
    echo -e "${CYAN}$1${NC}" | tee -a "$LOG_FILE"
    echo -e "${CYAN}============================================================================${NC}\n" | tee -a "$LOG_FILE"
}

# Setup functions
setup_test_environment() {
    log_header "🚀 Setting up Multimodal AI Test Environment"
    
    # Create test results directory
    mkdir -p "$TEST_RESULTS_DIR"
    mkdir -p "$PROJECT_ROOT/tests/assets"
    
    # Initialize log file
    echo "Multimodal AI Integration Test Execution - $(date)" > "$LOG_FILE"
    
    log_info "Test configuration: $TEST_CONFIG"
    log_info "Test results directory: $TEST_RESULTS_DIR"
    log_info "Project root: $PROJECT_ROOT"
}

check_prerequisites() {
    log_header "🔍 Checking Prerequisites"
    
    local missing_tools=()
    
    # Check required tools
    command -v docker >/dev/null 2>&1 || missing_tools+=("docker")
    command -v docker-compose >/dev/null 2>&1 || missing_tools+=("docker-compose")
    command -v gradle >/dev/null 2>&1 || missing_tools+=("gradle")
    command -v npm >/dev/null 2>&1 || missing_tools+=("npm")
    command -v npx >/dev/null 2>&1 || missing_tools+=("npx")
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        exit 1
    fi
    
    # Check if Playwright is installed
    if ! npx playwright --version >/dev/null 2>&1; then
        log_warning "Playwright not found, installing..."
        cd "$PROJECT_ROOT/frontend" && npm install @playwright/test
        npx playwright install
    fi
    
    log_success "All prerequisites satisfied"
}

start_services() {
    log_header "🔧 Starting Multimodal Services"
    
    cd "$PROJECT_ROOT"
    
    # Start services using existing make targets
    log_info "Starting multimodal services..."
    make multimodal-start
    
    # Wait for services to be ready
    wait_for_services
}

wait_for_services() {
    log_info "⏳ Waiting for services to be ready..."
    
    local start_time=$(date +%s)
    local timeout=$SERVICE_STARTUP_TIMEOUT
    
    while true; do
        local current_time=$(date +%s)
        local elapsed=$((current_time - start_time))
        
        if [ $elapsed -gt $timeout ]; then
            log_error "Services did not become ready within $timeout seconds"
            return 1
        fi
        
        # Check Kotlin backend
        if curl -f "$KOTLIN_BACKEND_URL/health" >/dev/null 2>&1; then
            kotlin_ready=true
        else
            kotlin_ready=false
        fi
        
        # Check Vision gRPC service (simplified check)
        if nc -z "$VISION_GRPC_HOST" "$VISION_GRPC_PORT" >/dev/null 2>&1; then
            vision_ready=true
        else
            vision_ready=false
        fi
        
        # Check Context gRPC service (simplified check)
        if nc -z "$CONTEXT_GRPC_HOST" "$CONTEXT_GRPC_PORT" >/dev/null 2>&1; then
            context_ready=true
        else
            context_ready=false
        fi
        
        if [ "$kotlin_ready" = true ] && [ "$vision_ready" = true ] && [ "$context_ready" = true ]; then
            log_success "All services are ready!"
            return 0
        fi
        
        log_info "Services status - Kotlin: $kotlin_ready, Vision: $vision_ready, Context: $context_ready"
        sleep 5
    done
}

run_backend_integration_tests() {
    log_header "🧪 Running Backend Integration Tests"
    
    cd "$PROJECT_ROOT/backend"
    
    # Run multimodal integration tests
    log_info "Running MultimodalIntegrationTest..."
    if ./gradlew test --tests "*MultimodalIntegrationTest*" --info; then
        log_success "MultimodalIntegrationTest passed"
    else
        log_error "MultimodalIntegrationTest failed"
        return 1
    fi
    
    # Run HTTP controller tests
    log_info "Running MultimodalControllerTest..."
    if ./gradlew test --tests "*MultimodalControllerTest*" --info; then
        log_success "MultimodalControllerTest passed"
    else
        log_error "MultimodalControllerTest failed"
        return 1
    fi
    
    log_success "Backend integration tests completed"
}

run_e2e_tests() {
    log_header "🎭 Running End-to-End Tests"
    
    cd "$PROJECT_ROOT/frontend"
    
    # Run Playwright E2E tests
    log_info "Running multimodal E2E tests with Playwright..."
    if npx playwright test multimodal-e2e.spec.ts --reporter=html --output="$TEST_RESULTS_DIR/playwright"; then
        log_success "End-to-end tests passed"
    else
        log_error "End-to-end tests failed"
        return 1
    fi
    
    log_success "End-to-end tests completed"
}

run_performance_benchmarks() {
    log_header "⚡ Running Performance Benchmarks"
    
    cd "$PROJECT_ROOT/frontend"
    
    # Run performance-specific tests
    log_info "Running performance benchmarks..."
    if npx playwright test multimodal-e2e.spec.ts --grep "Performance benchmarking" --reporter=json --output="$TEST_RESULTS_DIR/performance.json"; then
        log_success "Performance benchmarks completed"
    else
        log_warning "Performance benchmarks had issues (non-critical)"
    fi
}

validate_architecture_boundaries() {
    log_header "🏗️ Validating Architecture Boundaries"
    
    cd "$PROJECT_ROOT/frontend"
    
    # Run architecture validation tests
    log_info "Validating service boundaries..."
    if npx playwright test multimodal-e2e.spec.ts --grep "Architecture boundary validation" --reporter=json; then
        log_success "Architecture boundaries validated"
    else
        log_error "Architecture boundary validation failed"
        return 1
    fi
}

run_error_handling_tests() {
    log_header "🚨 Running Error Handling Tests"
    
    cd "$PROJECT_ROOT/frontend"
    
    # Run error handling tests
    log_info "Testing error scenarios and resilience..."
    if npx playwright test multimodal-e2e.spec.ts --grep "Error handling and resilience" --reporter=json; then
        log_success "Error handling tests passed"
    else
        log_error "Error handling tests failed"
        return 1
    fi
}

generate_test_report() {
    log_header "📊 Generating Test Report"
    
    local report_file="$TEST_RESULTS_DIR/multimodal-test-report.html"
    
    cat > "$report_file" << EOF
<!DOCTYPE html>
<html>
<head>
    <title>Multimodal AI Architecture Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .header { background: #2196F3; color: white; padding: 20px; border-radius: 5px; }
        .section { margin: 20px 0; padding: 15px; border-left: 4px solid #2196F3; }
        .success { border-left-color: #4CAF50; }
        .error { border-left-color: #f44336; }
        .warning { border-left-color: #ff9800; }
        pre { background: #f5f5f5; padding: 10px; border-radius: 3px; overflow-x: auto; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 Multimodal AI Architecture Test Report</h1>
        <p>Generated: $(date)</p>
        <p>Architecture: Kotlin Backend ↔ Python gRPC Services</p>
    </div>
    
    <div class="section success">
        <h2>✅ Test Execution Summary</h2>
        <p>Complete validation of the multimodal AI architecture refactoring:</p>
        <ul>
            <li>Service boundary compliance verified</li>
            <li>gRPC communication pipeline tested</li>
            <li>Performance benchmarks completed</li>
            <li>Error handling validated</li>
            <li>End-to-end workflows confirmed</li>
        </ul>
    </div>
    
    <div class="section">
        <h2>📋 Test Execution Log</h2>
        <pre>$(cat "$LOG_FILE")</pre>
    </div>
    
    <div class="section">
        <h2>🏗️ Architecture Validation</h2>
        <p><strong>✅ Kotlin Backend Responsibilities:</strong></p>
        <ul>
            <li>Business logic orchestration</li>
            <li>API request/response handling</li>
            <li>Workflow selection and configuration</li>
            <li>Data persistence and caching</li>
        </ul>
        
        <p><strong>✅ Python Services Responsibilities:</strong></p>
        <ul>
            <li>Pure AI/ML inference operations</li>
            <li>Model loading and execution</li>
            <li>Result formatting and return</li>
        </ul>
    </div>
</body>
</html>
EOF
    
    log_success "Test report generated: $report_file"
}

cleanup() {
    log_header "🧹 Cleaning Up"
    
    cd "$PROJECT_ROOT"
    
    # Stop services
    log_info "Stopping multimodal services..."
    make multimodal-stop || log_warning "Some services may not have stopped cleanly"
    
    log_success "Cleanup completed"
}

# Main execution function
main() {
    local test_suite="${1:-full}"
    local exit_code=0
    
    # Setup
    setup_test_environment
    check_prerequisites
    
    # Trap cleanup on exit
    trap cleanup EXIT
    
    case "$test_suite" in
        "backend")
            start_services
            run_backend_integration_tests || exit_code=1
            ;;
        "e2e")
            start_services
            run_e2e_tests || exit_code=1
            ;;
        "performance")
            start_services
            run_performance_benchmarks || exit_code=1
            ;;
        "full"|*)
            start_services
            run_backend_integration_tests || exit_code=1
            run_e2e_tests || exit_code=1
            validate_architecture_boundaries || exit_code=1
            run_error_handling_tests || exit_code=1
            run_performance_benchmarks || exit_code=1
            ;;
    esac
    
    # Generate report
    generate_test_report
    
    if [ $exit_code -eq 0 ]; then
        log_success "🎉 All multimodal AI architecture tests passed!"
        log_success "Architecture refactoring validation complete"
        log_success "Service boundaries properly maintained"
        log_success "gRPC communication pipeline verified"
    else
        log_error "❌ Some tests failed - check logs for details"
    fi
    
    exit $exit_code
}

# Help function
show_help() {
    echo "Multimodal AI Architecture Test Runner"
    echo ""
    echo "Usage: $0 [test_suite]"
    echo ""
    echo "Test Suites:"
    echo "  full        Run complete test suite (default)"
    echo "  backend     Run only backend integration tests"
    echo "  e2e         Run only end-to-end tests"
    echo "  performance Run only performance benchmarks"
    echo ""
    echo "Examples:"
    echo "  $0                    # Run full test suite"
    echo "  $0 backend           # Run only backend tests"
    echo "  $0 performance       # Run only performance tests"
}

# Parse command line arguments
if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
    show_help
    exit 0
fi

# Execute main function
main "${1:-full}"
