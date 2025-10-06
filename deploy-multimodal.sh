#!/bin/bash

# Multimodal AI Pipeline Deployment Script
# Deploys the comprehensive multimodal AI processing pipeline

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.multimodal.yml"
PROJECT_NAME="multimodal-ai"
LOG_DIR="./logs"
CONFIG_DIR="./config"

# Functions
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

check_requirements() {
    log_info "Checking system requirements..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check NVIDIA Docker (for GPU support)
    if ! docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi &> /dev/null; then
        log_warning "NVIDIA Docker runtime not available - GPU acceleration disabled"
    else
        log_success "NVIDIA Docker runtime available"
    fi
    
    # Check available disk space (need at least 20GB)
    available_space=$(df . | tail -1 | awk '{print $4}')
    if [ "$available_space" -lt 20971520 ]; then  # 20GB in KB
        log_warning "Less than 20GB disk space available. Models may fail to download."
    fi
    
    log_success "System requirements check completed"
}

create_directories() {
    log_info "Creating necessary directories..."
    
    mkdir -p "$LOG_DIR"
    mkdir -p "$CONFIG_DIR"
    mkdir -p "./uploads"
    mkdir -p "./models"
    mkdir -p "./services/context-llm/data"
    mkdir -p "./config/grafana/dashboards"
    mkdir -p "./config/grafana/datasources"
    
    log_success "Directories created"
}

setup_environment() {
    log_info "Setting up environment..."
    
    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        cat > .env << EOF
# Multimodal AI Pipeline Configuration
COMPOSE_PROJECT_NAME=$PROJECT_NAME

# API Keys (optional - leave empty to use Ollama)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# Service Configuration
VISION_AI_PORT=8001
CONTEXT_LLM_PORT=8002
ORCHESTRATOR_PORT=8003
GATEWAY_PORT=8000

# Resource Limits
VISION_AI_MEMORY=8g
CONTEXT_LLM_MEMORY=4g
ORCHESTRATOR_MEMORY=2g

# Logging
LOG_LEVEL=INFO
EOF
        log_success "Created .env file with default configuration"
    else
        log_info "Using existing .env file"
    fi
}

setup_grafana_config() {
    log_info "Setting up Grafana configuration..."
    
    # Create datasource configuration
    cat > ./config/grafana/datasources/prometheus.yml << EOF
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus-multimodal:9090
    isDefault: true
EOF

    # Create basic dashboard configuration
    cat > ./config/grafana/dashboards/dashboard.yml << EOF
apiVersion: 1

providers:
  - name: 'default'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /etc/grafana/provisioning/dashboards
EOF

    log_success "Grafana configuration created"
}

pull_base_images() {
    log_info "Pulling base Docker images..."
    
    docker pull nvidia/cuda:12.1-devel-ubuntu22.04
    docker pull python:3.11-slim
    docker pull ollama/ollama:latest
    docker pull nginx:alpine
    docker pull redis:7-alpine
    docker pull prom/prometheus:latest
    docker pull grafana/grafana:latest
    
    log_success "Base images pulled"
}

build_services() {
    log_info "Building multimodal AI services..."
    
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" build --parallel
    
    log_success "Services built successfully"
}

start_services() {
    log_info "Starting multimodal AI pipeline..."
    
    # Start core services first
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" up -d ollama redis-multimodal
    
    log_info "Waiting for core services to be ready..."
    sleep 10
    
    # Start AI services
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" up -d context-llm vision-ai-enhanced
    
    log_info "Waiting for AI services to initialize..."
    sleep 30
    
    # Start orchestrator and gateway
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" up -d multimodal-orchestrator nginx-multimodal
    
    # Start monitoring
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" up -d prometheus grafana
    
    log_success "All services started"
}

setup_ollama_models() {
    log_info "Setting up Ollama models..."
    
    # Wait for Ollama to be ready
    max_attempts=30
    attempt=0
    while [ $attempt -lt $max_attempts ]; do
        if docker exec ollama ollama list &> /dev/null; then
            break
        fi
        log_info "Waiting for Ollama to be ready... ($((attempt + 1))/$max_attempts)"
        sleep 10
        ((attempt++))
    done
    
    if [ $attempt -eq $max_attempts ]; then
        log_error "Ollama failed to start within expected time"
        return 1
    fi
    
    # Pull recommended models
    log_info "Pulling Ollama models (this may take a while)..."
    docker exec ollama ollama pull openhermes || log_warning "Failed to pull openhermes model"
    docker exec ollama ollama pull llama2:7b || log_warning "Failed to pull llama2 model"
    
    log_success "Ollama models setup completed"
}

check_service_health() {
    log_info "Checking service health..."
    
    services=(
        "http://localhost:8001/health:Enhanced Vision AI"
        "http://localhost:8002/health:Context-Aware LLM"
        "http://localhost:8003/health:Multimodal Orchestrator"
        "http://localhost:8000/health:API Gateway"
        "http://localhost:11434/api/tags:Ollama"
    )
    
    for service in "${services[@]}"; do
        url=$(echo "$service" | cut -d: -f1-2)
        name=$(echo "$service" | cut -d: -f3-)
        
        if curl -s -f "$url" > /dev/null; then
            log_success "$name is healthy"
        else
            log_warning "$name is not responding"
        fi
    done
}

show_status() {
    log_info "Multimodal AI Pipeline Status:"
    echo
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" ps
    echo
    
    log_info "Service Endpoints:"
    echo "🔗 API Gateway:              http://localhost:8000"
    echo "🔗 Enhanced Vision AI:       http://localhost:8001"
    echo "🔗 Context-Aware LLM:        http://localhost:8002"
    echo "🔗 Multimodal Orchestrator:  http://localhost:8003"
    echo "🔗 Ollama:                   http://localhost:11434"
    echo "🔗 Grafana Dashboard:        http://localhost:3001 (admin/admin)"
    echo "🔗 Prometheus:               http://localhost:9090"
    echo
    
    log_info "Example API Usage:"
    echo "curl -X POST -F 'image=@screenshot.png' -F 'workflow_type=contextual_analysis' http://localhost:8000/analyze"
    echo
}

cleanup() {
    log_info "Cleaning up..."
    docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" down
    log_success "Services stopped"
}

# Main execution
main() {
    case "${1:-deploy}" in
        "deploy")
            log_info "🚀 Starting Multimodal AI Pipeline Deployment"
            check_requirements
            create_directories
            setup_environment
            setup_grafana_config
            pull_base_images
            build_services
            start_services
            setup_ollama_models
            sleep 10
            check_service_health
            show_status
            log_success "🎉 Multimodal AI Pipeline deployed successfully!"
            ;;
        "start")
            log_info "Starting existing services..."
            docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" start
            show_status
            ;;
        "stop")
            log_info "Stopping services..."
            docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" stop
            ;;
        "restart")
            log_info "Restarting services..."
            docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" restart
            show_status
            ;;
        "status")
            show_status
            ;;
        "logs")
            docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" logs -f "${2:-}"
            ;;
        "cleanup")
            cleanup
            ;;
        "health")
            check_service_health
            ;;
        *)
            echo "Usage: $0 {deploy|start|stop|restart|status|logs|cleanup|health}"
            echo
            echo "Commands:"
            echo "  deploy   - Full deployment of the multimodal AI pipeline"
            echo "  start    - Start existing services"
            echo "  stop     - Stop all services"
            echo "  restart  - Restart all services"
            echo "  status   - Show service status and endpoints"
            echo "  logs     - Show service logs (optionally specify service name)"
            echo "  cleanup  - Stop and remove all services"
            echo "  health   - Check health of all services"
            exit 1
            ;;
    esac
}

# Handle script interruption
trap cleanup INT TERM

# Run main function
main "$@"
