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
        local kafka_status=$(echo "$response" | jq -r '.services.kafka // "unknown"')
        local db_status=$(echo "$response" | jq -r '.services.database // "unknown"')
        local ollama_status=$(echo "$response" | jq -r '.services.ollama // "unknown"')
        
        echo -e "${GREEN}✅ OK${NC}"
        echo -e "   Kafka: ${kafka_status}"
        echo -e "   Database: ${db_status}"
        echo -e "   Ollama: ${ollama_status}"
        
        # Check if any service is unhealthy
        if [[ "$kafka_status" == *"unhealthy"* ]] || [[ "$db_status" == *"unhealthy"* ]] || [[ "$ollama_status" == *"unhealthy"* ]]; then
            return 1
        fi
        return 0
    else
        echo -e "${RED}❌ Invalid response${NC}"
        return 1
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
            check_service "Backend" "$BACKEND_URL/ping" || ((failed_checks++))
            detailed_backend_health || ((failed_checks++))
            ;;
        frontend)
            check_service "Frontend" "$FRONTEND_URL" || ((failed_checks++))
            ;;
        kafka)
            check_docker_service "Kafka" "kafka-dev" || ((failed_checks++))
            check_service "Kafka UI" "$KAFKA_UI_URL" || ((failed_checks++))
            ;;
        ollama)
            check_service "Ollama" "$OLLAMA_URL/api/tags" || ((failed_checks++))
            ;;
        database)
            check_docker_service "PostgreSQL" "postgres-dev-db" || ((failed_checks++))
            ;;
        *)
            echo -e "${RED}❌ Unknown service: $SPECIFIC_SERVICE${NC}"
            exit 1
            ;;
    esac
else
    echo -e "${YELLOW}Running comprehensive health checks...${NC}\n"
    
    # Docker services
    echo -e "${BLUE}Docker Services:${NC}"
    check_docker_service "PostgreSQL" "postgres-dev-db" || ((failed_checks++))
    check_docker_service "Kafka" "kafka-dev" || ((failed_checks++))
    check_docker_service "Zookeeper" "zookeeper-dev" || ((failed_checks++))
    check_docker_service "Kafka UI" "kafka-ui-dev" || ((failed_checks++))
    
    echo ""
    
    # HTTP services
    echo -e "${BLUE}HTTP Services:${NC}"
    check_service "Backend Ping" "$BACKEND_URL/ping" || ((failed_checks++))
    check_service "Frontend" "$FRONTEND_URL" || ((failed_checks++))
    check_service "Kafka UI" "$KAFKA_UI_URL" || ((failed_checks++))
    check_service "Ollama" "$OLLAMA_URL/api/tags" || ((failed_checks++))
    
    echo ""
    
    # Detailed checks
    echo -e "${BLUE}Detailed Health:${NC}"
    detailed_backend_health || ((failed_checks++))
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
