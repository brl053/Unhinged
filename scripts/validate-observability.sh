#!/bin/bash
# ============================================================================
# Unhinged Observability Validation Script
# ============================================================================
#
# @file validate-observability.sh
# @version 1.0.0
# @author Unhinged Team
# @date 2025-01-07
# @description Validation and testing for LGTM observability stack
#
# LEGEND: Comprehensive validation of observability infrastructure
# KEY: Configuration validation, service health, and integration testing
# MAP: End-to-end observability stack verification
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "🧪 Validating Unhinged Observability Stack..."

# Configuration file validation
print_status "Validating configuration files..."

config_files=(
    "docker-compose.observability.yml"
    "monitoring/prometheus/prometheus.yml"
    "monitoring/loki/loki-config.yml"
    "monitoring/tempo/tempo.yml"
    "monitoring/otel/otel-collector-config.yaml"
    "monitoring/grafana/provisioning/datasources/datasources.yml"
    "monitoring/grafana/provisioning/dashboards/dashboards.yml"
)

validation_passed=true

for config_file in "${config_files[@]}"; do
    if [[ ! -f "$config_file" ]]; then
        print_error "Configuration file missing: $config_file"
        validation_passed=false
    else
        print_success "Found: $config_file"
    fi
done

if ! $validation_passed; then
    print_error "Configuration validation failed"
    exit 1
fi

# YAML syntax validation
print_status "Validating YAML syntax..."

yaml_files=(
    "docker-compose.observability.yml"
    "monitoring/prometheus/prometheus.yml"
    "monitoring/loki/loki-config.yml"
    "monitoring/tempo/tempo.yml"
    "monitoring/otel/otel-collector-config.yaml"
    "monitoring/grafana/provisioning/datasources/datasources.yml"
    "monitoring/grafana/provisioning/dashboards/dashboards.yml"
)

for yaml_file in "${yaml_files[@]}"; do
    if command -v yamllint &> /dev/null; then
        if yamllint "$yaml_file" &> /dev/null; then
            print_success "YAML syntax valid: $yaml_file"
        else
            print_warning "YAML syntax issues in: $yaml_file"
        fi
    else
        # Basic YAML validation using Python
        if python3 -c "import yaml; yaml.safe_load(open('$yaml_file'))" 2>/dev/null; then
            print_success "YAML syntax valid: $yaml_file"
        else
            print_error "YAML syntax invalid: $yaml_file"
            validation_passed=false
        fi
    fi
done

# Docker network validation
print_status "Checking Docker network..."

if docker network ls | grep -q "unhinged-network"; then
    print_success "unhinged-network exists"
else
    print_warning "unhinged-network not found, creating..."
    docker network create unhinged-network
    print_success "unhinged-network created"
fi

# Port availability check
print_status "Checking port availability..."

ports=(3001 9090 3100 3200 4317 4318 4319 4320 8889 9187)

for port in "${ports[@]}"; do
    if lsof -i ":$port" &> /dev/null; then
        print_warning "Port $port is already in use"
    else
        print_success "Port $port is available"
    fi
done

# Service startup test
print_status "Testing service startup..."

# Start services in detached mode
docker-compose -f docker-compose.observability.yml up -d

# Wait for services to initialize
print_status "Waiting for services to initialize (30 seconds)..."
sleep 30

# Health check validation
print_status "Performing health checks..."

services=(
    "http://localhost:3001/api/health:Grafana"
    "http://localhost:9090/-/healthy:Prometheus"
    "http://localhost:3100/ready:Loki"
    "http://localhost:3200/ready:Tempo"
)

all_healthy=true

for service in "${services[@]}"; do
    url="${service%:*}"
    name="${service#*:}"
    
    if curl -f -s --max-time 10 "$url" > /dev/null 2>&1; then
        print_success "$name is healthy"
    else
        print_error "$name is not responding at $url"
        all_healthy=false
    fi
done

# Test metrics collection
print_status "Testing metrics collection..."

if curl -f -s "http://localhost:9090/api/v1/query?query=up" | jq '.status' | grep -q "success"; then
    print_success "Prometheus metrics API is working"
else
    print_error "Prometheus metrics API is not working"
    all_healthy=false
fi

# Test log ingestion
print_status "Testing log ingestion..."

if curl -f -s "http://localhost:3100/loki/api/v1/labels" | jq '.status' | grep -q "success"; then
    print_success "Loki labels API is working"
else
    print_error "Loki labels API is not working"
    all_healthy=false
fi

# Test trace collection
print_status "Testing trace collection..."

if curl -f -s "http://localhost:3200/api/search" > /dev/null 2>&1; then
    print_success "Tempo search API is working"
else
    print_error "Tempo search API is not working"
    all_healthy=false
fi

# Generate test data
print_status "Generating test telemetry data..."

# Send test metrics to OpenTelemetry collector
if command -v curl &> /dev/null; then
    # Test OTLP HTTP endpoint
    test_metric='{"resourceMetrics":[{"resource":{"attributes":[{"key":"service.name","value":{"stringValue":"test-service"}}]},"scopeMetrics":[{"scope":{"name":"test"},"metrics":[{"name":"test_metric","gauge":{"dataPoints":[{"timeUnixNano":"'$(date +%s%N)'","asDouble":1.0}]}}]}]}]}'
    
    if curl -f -s -X POST "http://localhost:4320/v1/metrics" \
        -H "Content-Type: application/json" \
        -d "$test_metric" > /dev/null 2>&1; then
        print_success "OTLP HTTP metrics endpoint is working"
    else
        print_warning "OTLP HTTP metrics endpoint test failed"
    fi
fi

# Final validation summary
echo ""
echo "🎯 Validation Summary:"

if $all_healthy; then
    print_success "All observability services are healthy and operational!"
    echo ""
    echo "📊 Access Points:"
    echo "   Grafana:    http://localhost:3001 (admin/unhinged_observability)"
    echo "   Prometheus: http://localhost:9090"
    echo "   Loki:       http://localhost:3100"
    echo "   Tempo:      http://localhost:3200"
    echo ""
    echo "✅ Observability stack validation PASSED!"
    exit 0
else
    print_error "Some services are not healthy. Check logs with:"
    echo "   docker-compose -f docker-compose.observability.yml logs"
    echo ""
    echo "❌ Observability stack validation FAILED!"
    exit 1
fi
