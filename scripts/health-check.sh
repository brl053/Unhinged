#!/bin/bash

# ============================================================================
# Health Check Script
# ============================================================================
# 
# Comprehensive health checks for all services in the Unhinged system
#
# Usage:
#   ./scripts/health-check.sh                    # Check all services
#   ./scripts/health-check.sh --service kafka   # Check specific service
#   ./scripts/health-check.sh --quick           # Quick ping test only
#
# Author: LLM Agent
# Version: 1.0.0
# Date: 2025-01-04
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKEND_URL="http://localhost:8080"
FRONTEND_URL="http://localhost:3000"
KAFKA_UI_URL="http://localhost:8090"
OLLAMA_URL="http://localhost:11434"

# AI Services
VISION_AI_URL="http://localhost:8001"
WHISPER_TTS_URL="http://localhost:8000"
CONTEXT_LLM_URL="http://localhost:8002"

# Observability Services
GRAFANA_URL="http://localhost:3001"
PROMETHEUS_URL="http://localhost:9090"
LOKI_URL="http://localhost:3100"
TEMPO_URL="http://localhost:3200"
OTEL_COLLECTOR_URL="http://localhost:8889"

# Database
POSTGRES_HOST="localhost"
POSTGRES_PORT="5433"
POSTGRES_USER="postgres"
POSTGRES_DB="unhinged"

# Parse arguments
QUICK_MODE=false
SPECIFIC_SERVICE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --quick)
            QUICK_MODE=true
            shift
            ;;
        --service)
            SPECIFIC_SERVICE="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}🏥 Unhinged System Health Check${NC}\n"

# ============================================================================
# QUICK PING TEST
# ============================================================================

ping_test() {
    local service_name=$1
    local url=$2
    local timeout=${3:-5}
    
    echo -n "🏓 Ping $service_name... "
    
    if curl -f -s --max-time $timeout "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ OK${NC}"
        return 0
    else
        echo -e "${RED}❌ FAILED${NC}"
        return 1
    fi
}

if [ "$QUICK_MODE" = true ]; then
    echo -e "${YELLOW}Quick ping test mode${NC}\n"
    
    ping_test "Backend" "$BACKEND_URL/ping"
    ping_test "Frontend" "$FRONTEND_URL"
    ping_test "Vision AI" "$VISION_AI_URL/health"
    ping_test "Whisper TTS" "$WHISPER_TTS_URL/health"
    ping_test "Grafana" "$GRAFANA_URL/api/health"
    ping_test "Prometheus" "$PROMETHEUS_URL/-/healthy"
    ping_test "Loki" "$LOKI_URL/ready"
    ping_test "Kafka UI" "$KAFKA_UI_URL"
    ping_test "Ollama" "$OLLAMA_URL/api/tags"
    
    echo -e "\n${GREEN}✅ Quick health check completed${NC}"
    exit 0
fi

# ============================================================================
# COMPREHENSIVE HEALTH CHECKS
# ============================================================================

check_service() {
    local service_name=$1
    local url=$2
    local expected_status=${3:-200}
    
    echo -n "🔍 Checking $service_name... "
    
    local response=$(curl -s -w "%{http_code}" --max-time 10 "$url" 2>/dev/null || echo "000")
    local http_code="${response: -3}"
    local body="${response%???}"
    
    if [ "$http_code" = "$expected_status" ]; then
        echo -e "${GREEN}✅ OK (HTTP $http_code)${NC}"
        return 0
    else
        echo -e "${RED}❌ FAILED (HTTP $http_code)${NC}"
        if [ ! -z "$body" ] && [ ${#body} -lt 200 ]; then
            echo -e "   ${YELLOW}Response: $body${NC}"
        fi
        return 1
    fi
}

check_docker_service() {
    local service_name=$1
    local container_name=$2
    
    echo -n "🐳 Checking Docker service $service_name... "
    
    if docker ps --format "table {{.Names}}" | grep -q "^$container_name$"; then
        local status=$(docker inspect --format='{{.State.Status}}' "$container_name" 2>/dev/null)
        if [ "$status" = "running" ]; then
            echo -e "${GREEN}✅ Running${NC}"
            return 0
        else
            echo -e "${RED}❌ Not running (status: $status)${NC}"
            return 1
        fi
    else
        echo -e "${RED}❌ Container not found${NC}"
        return 1
    fi
}

detailed_backend_health() {
    echo -n "🔬 Detailed backend health... "

    local response=$(curl -s --max-time 10 "$BACKEND_URL/health" 2>/dev/null || echo "{}")

    if echo "$response" | jq -e '.status' > /dev/null 2>&1; then
        local overall_status=$(echo "$response" | jq -r '.status // "unknown"')
        echo -e "${GREEN}✅ OK (Status: $overall_status)${NC}"

        # Display all services if available
        if echo "$response" | jq -e '.services' > /dev/null 2>&1; then
            echo "$response" | jq -r '.services | to_entries[] | "   \(.key): \(.value)"'
        fi

        # Check if overall status indicates issues
        if [[ "$overall_status" == *"degraded"* ]] || [[ "$overall_status" == *"unhealthy"* ]]; then
            return 1
        fi
        return 0
    else
        echo -e "${RED}❌ Invalid response${NC}"
        return 1
    fi
}

detailed_ai_service_health() {
    local service_name=$1
    local url=$2

    echo -n "🤖 Detailed $service_name health... "

    local response=$(curl -s --max-time 10 "$url/health" 2>/dev/null || echo "{}")

    if echo "$response" | jq -e '.status' > /dev/null 2>&1; then
        local status=$(echo "$response" | jq -r '.status // "unknown"')
        local model_status=$(echo "$response" | jq -r '.model_status // "unknown"')
        local gpu_available=$(echo "$response" | jq -r '.gpu_available // "unknown"')

        echo -e "${GREEN}✅ OK${NC}"
        echo -e "   Status: ${status}"
        echo -e "   Model: ${model_status}"
        echo -e "   GPU: ${gpu_available}"
        return 0
    else
        echo -e "${RED}❌ Invalid response${NC}"
        return 1
    fi
}

detailed_observability_health() {
    echo -e "\n${BLUE}🔍 OBSERVABILITY STACK HEALTH${NC}"

    # Grafana
    echo -n "📊 Grafana health... "
    local grafana_response=$(curl -s --max-time 10 "$GRAFANA_URL/api/health" 2>/dev/null || echo "{}")
    if echo "$grafana_response" | jq -e '.database' > /dev/null 2>&1; then
        local db_status=$(echo "$grafana_response" | jq -r '.database // "unknown"')
        local version=$(echo "$grafana_response" | jq -r '.version // "unknown"')
        echo -e "${GREEN}✅ OK (v$version, DB: $db_status)${NC}"
    else
        echo -e "${RED}❌ Failed${NC}"
        ((failed_checks++))
    fi

    # Prometheus
    echo -n "📈 Prometheus health... "
    if curl -s --max-time 10 "$PROMETHEUS_URL/-/healthy" | grep -q "Healthy"; then
        echo -e "${GREEN}✅ OK${NC}"

        # Check targets
        local targets_response=$(curl -s --max-time 10 "$PROMETHEUS_URL/api/v1/targets" 2>/dev/null || echo "{}")
        if echo "$targets_response" | jq -e '.data.activeTargets' > /dev/null 2>&1; then
            local healthy_targets=$(echo "$targets_response" | jq '[.data.activeTargets[] | select(.health == "up")] | length')
            local total_targets=$(echo "$targets_response" | jq '.data.activeTargets | length')
            echo -e "   Targets: ${healthy_targets}/${total_targets} healthy"
        fi
    else
        echo -e "${RED}❌ Failed${NC}"
        ((failed_checks++))
    fi

    # Loki
    echo -n "📝 Loki health... "
    local loki_response=$(curl -s --max-time 10 "$LOKI_URL/ready" 2>/dev/null || echo "")
    if [[ "$loki_response" == *"ready"* ]] || curl -s --max-time 5 "$LOKI_URL/metrics" | grep -q "loki"; then
        echo -e "${GREEN}✅ OK${NC}"
    else
        echo -e "${YELLOW}⚠️ Starting up${NC}"
    fi
}

check_postgres_health() {
    echo -n "🐘 PostgreSQL health... "

    if command -v psql > /dev/null 2>&1; then
        if PGPASSWORD=password psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT 1;" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ OK${NC}"
            return 0
        else
            echo -e "${RED}❌ Connection failed${NC}"
            return 1
        fi
    else
        # Fallback: check if container is running
        if docker ps --format "table {{.Names}}" | grep -q "unhinged-postgres"; then
            echo -e "${GREEN}✅ Container running${NC}"
            return 0
        else
            echo -e "${RED}❌ Container not found${NC}"
            return 1
        fi
    fi
}

# ============================================================================
# RUN HEALTH CHECKS
# ============================================================================

failed_checks=0

if [ ! -z "$SPECIFIC_SERVICE" ]; then
    echo -e "${YELLOW}Checking specific service: $SPECIFIC_SERVICE${NC}\n"
    
    case $SPECIFIC_SERVICE in
        backend)
            check_service "Backend" "$BACKEND_URL/health" || ((failed_checks++))
            detailed_backend_health || ((failed_checks++))
            ;;
        frontend)
            check_service "Frontend" "$FRONTEND_URL" || ((failed_checks++))
            ;;
        vision-ai)
            check_service "Vision AI" "$VISION_AI_URL/health" || ((failed_checks++))
            detailed_ai_service_health "Vision AI" "$VISION_AI_URL" || ((failed_checks++))
            ;;
        whisper-tts)
            check_service "Whisper TTS" "$WHISPER_TTS_URL/health" || ((failed_checks++))
            detailed_ai_service_health "Whisper TTS" "$WHISPER_TTS_URL" || ((failed_checks++))
            ;;
        context-llm)
            check_service "Context LLM" "$CONTEXT_LLM_URL/health" || ((failed_checks++))
            detailed_ai_service_health "Context LLM" "$CONTEXT_LLM_URL" || ((failed_checks++))
            ;;
        observability)
            detailed_observability_health
            ;;
        grafana)
            check_service "Grafana" "$GRAFANA_URL/api/health" || ((failed_checks++))
            ;;
        prometheus)
            check_service "Prometheus" "$PROMETHEUS_URL/-/healthy" || ((failed_checks++))
            ;;
        database)
            check_postgres_health || ((failed_checks++))
            ;;
        kafka)
            check_docker_service "Kafka" "kafka-dev" || ((failed_checks++))
            check_service "Kafka UI" "$KAFKA_UI_URL" || ((failed_checks++))
            ;;
        ollama)
            check_service "Ollama" "$OLLAMA_URL/api/tags" || ((failed_checks++))
            ;;
        *)
            echo -e "${RED}❌ Unknown service: $SPECIFIC_SERVICE${NC}"
            echo -e "${YELLOW}Available services: backend, frontend, vision-ai, whisper-tts, context-llm, observability, grafana, prometheus, database, kafka, ollama${NC}"
            exit 1
            ;;
    esac
else
    echo -e "${YELLOW}Running comprehensive health checks...${NC}\n"

    # Core Services
    echo -e "${BLUE}🏗️ CORE SERVICES:${NC}"
    check_service "Backend" "$BACKEND_URL/health" || ((failed_checks++))
    check_postgres_health || ((failed_checks++))

    echo ""

    # AI Services
    echo -e "${BLUE}🤖 AI SERVICES:${NC}"
    check_service "Vision AI" "$VISION_AI_URL/health" || ((failed_checks++))
    check_service "Whisper TTS" "$WHISPER_TTS_URL/health" || ((failed_checks++))
    check_service "Context LLM" "$CONTEXT_LLM_URL/health" 2>/dev/null || echo -e "   ${YELLOW}⚠️ Context LLM not running (optional)${NC}"

    echo ""

    # Observability Stack
    detailed_observability_health

    echo ""

    # Optional Services
    echo -e "${BLUE}🔧 OPTIONAL SERVICES:${NC}"
    check_service "Frontend" "$FRONTEND_URL" 2>/dev/null || echo -e "   ${YELLOW}⚠️ Frontend not running (optional)${NC}"
    check_service "Kafka UI" "$KAFKA_UI_URL" 2>/dev/null || echo -e "   ${YELLOW}⚠️ Kafka not running (optional)${NC}"
    check_service "Ollama" "$OLLAMA_URL/api/tags" 2>/dev/null || echo -e "   ${YELLOW}⚠️ Ollama not running (optional)${NC}"

    echo ""

    # Detailed Health Analysis
    echo -e "${BLUE}🔬 DETAILED HEALTH ANALYSIS:${NC}"
    detailed_backend_health || ((failed_checks++))
    detailed_ai_service_health "Vision AI" "$VISION_AI_URL" 2>/dev/null || echo -e "   ${YELLOW}⚠️ Vision AI detailed check failed${NC}"
    detailed_ai_service_health "Whisper TTS" "$WHISPER_TTS_URL" 2>/dev/null || echo -e "   ${YELLOW}⚠️ Whisper TTS detailed check failed${NC}"
fi

# ============================================================================
# SUMMARY
# ============================================================================

echo ""
if [ $failed_checks -eq 0 ]; then
    echo -e "${GREEN}🎉 All health checks passed!${NC}"
    echo -e "${GREEN}✅ System is healthy and ready for testing${NC}"
    exit 0
else
    echo -e "${RED}❌ $failed_checks health check(s) failed${NC}"
    echo -e "${YELLOW}💡 Try running individual service checks for more details${NC}"
    echo -e "${YELLOW}   Example: ./scripts/health-check.sh --service backend${NC}"
    exit 1
fi
