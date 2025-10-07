#!/bin/bash
# ============================================================================
# Unhinged Observability Setup Script
# ============================================================================
#
# @file setup-observability.sh
# @version 1.0.0
# @author Unhinged Team
# @date 2025-01-07
# @description Automated setup for LGTM observability stack
#
# LEGEND: Complete observability infrastructure deployment
# KEY: Validation, configuration, and service startup
# MAP: End-to-end observability stack initialization
# ============================================================================

set -e

echo "🔍 Setting up Unhinged Observability Stack..."

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

# Check prerequisites
print_status "Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed or not in PATH"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed or not in PATH"
    exit 1
fi

print_success "Prerequisites check passed"

# Create monitoring directories if they don't exist
print_status "Creating monitoring directory structure..."

mkdir -p monitoring/{grafana/{provisioning/{datasources,dashboards},dashboards},prometheus/rules,loki,tempo,otel}
mkdir -p monitoring/grafana/dashboards/system

print_success "Directory structure created"

# Validate configuration files
print_status "Validating configuration files..."

config_files=(
    "monitoring/prometheus/prometheus.yml"
    "monitoring/loki/loki-config.yml"
    "monitoring/tempo/tempo.yml"
    "monitoring/otel/otel-collector-config.yaml"
    "monitoring/grafana/provisioning/datasources/datasources.yml"
    "monitoring/grafana/provisioning/dashboards/dashboards.yml"
    "docker-compose.observability.yml"
)

for config_file in "${config_files[@]}"; do
    if [[ ! -f "$config_file" ]]; then
        print_error "Configuration file missing: $config_file"
        exit 1
    fi
done

print_success "Configuration files validated"

# Check if unhinged-network exists
print_status "Checking Docker network..."

if ! docker network ls | grep -q "unhinged-network"; then
    print_warning "unhinged-network not found, creating..."
    docker network create unhinged-network
    print_success "unhinged-network created"
else
    print_success "unhinged-network exists"
fi

# Start observability stack
print_status "Starting LGTM observability stack..."

docker-compose -f docker-compose.observability.yml up -d

# Wait for services to start
print_status "Waiting for services to initialize..."
sleep 30

# Verify services
print_status "Verifying service health..."

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
    
    if curl -f -s "$url" > /dev/null 2>&1; then
        print_success "$name is healthy"
    else
        print_error "$name is not responding"
        all_healthy=false
    fi
done

if $all_healthy; then
    print_success "All observability services are healthy!"
    echo ""
    echo "🎯 Access Points:"
    echo "   Grafana:    http://localhost:3001 (admin/unhinged_observability)"
    echo "   Prometheus: http://localhost:9090"
    echo "   Loki:       http://localhost:3100"
    echo "   Tempo:      http://localhost:3200"
    echo ""
    echo "✅ Observability stack setup complete!"
else
    print_error "Some services are not healthy. Check logs with:"
    echo "   docker-compose -f docker-compose.observability.yml logs"
    exit 1
fi
