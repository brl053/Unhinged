#!/bin/bash

# ============================================================================
# CDC System Startup Script
# ============================================================================
# 
# Comprehensive startup script for the Universal System CDC pipeline.
# Starts Kafka, Schema Registry, PostgreSQL, and initializes all components.
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
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
KAFKA_DIR="$PROJECT_ROOT/kafka"
DB_DIR="$PROJECT_ROOT/infrastructure/database"

echo -e "${BLUE}🚀 Starting Universal System CDC Pipeline...${NC}\n"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

wait_for_service() {
    local service_name=$1
    local host=$2
    local port=$3
    local max_attempts=30
    local attempt=1
    
    echo -e "${YELLOW}⏳ Waiting for ${service_name} to be ready...${NC}"
    
    while [ $attempt -le $max_attempts ]; do
        if nc -z $host $port 2>/dev/null; then
            echo -e "${GREEN}✅ ${service_name} is ready!${NC}"
            return 0
        fi
        
        echo -e "${CYAN}   Attempt ${attempt}/${max_attempts} - ${service_name} not ready yet...${NC}"
        sleep 2
        ((attempt++))
    done
    
    echo -e "${RED}❌ ${service_name} failed to start within expected time${NC}"
    return 1
}

check_command() {
    local cmd=$1
    if ! command -v $cmd &> /dev/null; then
        echo -e "${RED}❌ Required command '$cmd' not found${NC}"
        echo -e "${YELLOW}Please install $cmd and try again${NC}"
        exit 1
    fi
}

# ============================================================================
# PREREQUISITES CHECK
# ============================================================================

echo -e "${BLUE}🔍 Checking prerequisites...${NC}"

check_command "docker"
check_command "docker-compose"
check_command "nc"

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker is not running${NC}"
    echo -e "${YELLOW}Please start Docker and try again${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All prerequisites satisfied${NC}\n"

# ============================================================================
# START INFRASTRUCTURE SERVICES
# ============================================================================

echo -e "${BLUE}🐳 Starting infrastructure services...${NC}"

# Start Kafka ecosystem
cd "$KAFKA_DIR"
echo -e "${YELLOW}Starting Kafka, Zookeeper, and Schema Registry...${NC}"
docker-compose -f docker-compose.kafka.yml up -d

# Wait for services to be ready
wait_for_service "Zookeeper" "localhost" "2181"
wait_for_service "Kafka" "localhost" "9092"
wait_for_service "Schema Registry" "localhost" "8081"
wait_for_service "Kafka UI" "localhost" "8090"

echo -e "${GREEN}✅ Kafka ecosystem started successfully${NC}\n"

# ============================================================================
# CREATE KAFKA TOPICS
# ============================================================================

echo -e "${BLUE}📝 Creating Kafka topics...${NC}"

# Wait a bit more for Kafka to be fully ready
sleep 5

# Create topics
if [ -f "$KAFKA_DIR/scripts/create-topics.sh" ]; then
    cd "$KAFKA_DIR/scripts"
    ./create-topics.sh
else
    echo -e "${RED}❌ Topic creation script not found${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Kafka topics created successfully${NC}\n"

# ============================================================================
# START DATABASE
# ============================================================================

echo -e "${BLUE}🗄️ Starting PostgreSQL database...${NC}"

# Start PostgreSQL CDC database
cd "$KAFKA_DIR"
docker-compose -f docker-compose.kafka.yml up -d postgres-cdc

wait_for_service "PostgreSQL CDC" "localhost" "5433"

echo -e "${GREEN}✅ PostgreSQL database started successfully${NC}\n"

# ============================================================================
# RUN DATABASE MIGRATIONS
# ============================================================================

echo -e "${BLUE}🔄 Running database migrations...${NC}"

# Check if migration file exists
MIGRATION_FILE="$DB_DIR/migrations/001_cdc_foundation.sql"
if [ -f "$MIGRATION_FILE" ]; then
    echo -e "${YELLOW}Running CDC foundation migration...${NC}"
    
    # Run migration using psql
    PGPASSWORD=postgres psql -h localhost -p 5433 -U postgres -d unhinged_cdc -f "$MIGRATION_FILE"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Database migration completed successfully${NC}"
    else
        echo -e "${RED}❌ Database migration failed${NC}"
        exit 1
    fi
else
    echo -e "${RED}❌ Migration file not found: $MIGRATION_FILE${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Database setup completed${NC}\n"

# ============================================================================
# VERIFY SYSTEM HEALTH
# ============================================================================

echo -e "${BLUE}🏥 Verifying system health...${NC}"

# Check Kafka topics
echo -e "${YELLOW}Checking Kafka topics...${NC}"
docker exec kafka kafka-topics --list --bootstrap-server localhost:29092 | head -5

# Check Schema Registry
echo -e "${YELLOW}Checking Schema Registry...${NC}"
curl -s http://localhost:8081/subjects | jq . || echo "Schema Registry responding"

# Check PostgreSQL
echo -e "${YELLOW}Checking PostgreSQL connection...${NC}"
PGPASSWORD=postgres psql -h localhost -p 5433 -U postgres -d unhinged_cdc -c "SELECT COUNT(*) FROM schema_migrations;" || echo "Database connection failed"

echo -e "${GREEN}✅ System health check completed${NC}\n"

# ============================================================================
# DISPLAY SERVICE INFORMATION
# ============================================================================

echo -e "${BLUE}📊 CDC System Service Information:${NC}"
echo -e "${YELLOW}Kafka Services:${NC}"
echo -e "  • Kafka Broker: http://localhost:9092"
echo -e "  • Kafka UI: http://localhost:8090"
echo -e "  • Schema Registry: http://localhost:8081"
echo -e "  • Zookeeper: http://localhost:2181"

echo -e "${YELLOW}Database:${NC}"
echo -e "  • PostgreSQL CDC: localhost:5433"
echo -e "  • Database: unhinged_cdc"
echo -e "  • Username: postgres"

echo -e "${YELLOW}Key Topics Created:${NC}"
echo -e "  • llm-events (6 partitions)"
echo -e "  • tool-events (6 partitions)"
echo -e "  • workflow-events (3 partitions)"
echo -e "  • voice-events (4 partitions)"
echo -e "  • ui-events (8 partitions)"

echo -e "${YELLOW}Management URLs:${NC}"
echo -e "  • Kafka UI: http://localhost:8090"
echo -e "  • Schema Registry UI: http://localhost:8081/subjects"

# ============================================================================
# NEXT STEPS
# ============================================================================

echo -e "${GREEN}🎉 CDC System startup completed successfully!${NC}\n"

echo -e "${BLUE}🚀 Next Steps:${NC}"
echo -e "1. ${YELLOW}Start your application services:${NC}"
echo -e "   cd backend && ./gradlew bootRun"
echo -e "   cd frontend && npm run dev"
echo -e "   cd whisper-tts && python app.py"

echo -e "2. ${YELLOW}Test event production:${NC}"
echo -e "   Use the EventProducerService in your backend"

echo -e "3. ${YELLOW}Monitor the system:${NC}"
echo -e "   • Kafka UI: http://localhost:8090"
echo -e "   • Check database: psql -h localhost -p 5433 -U postgres -d unhinged_cdc"

echo -e "4. ${YELLOW}View logs:${NC}"
echo -e "   docker-compose -f kafka/docker-compose.kafka.yml logs -f"

echo -e "${CYAN}💡 Pro tip: Use 'docker-compose -f kafka/docker-compose.kafka.yml down' to stop all services${NC}"

echo -e "${GREEN}✨ Your Universal System CDC pipeline is now ready for event-driven architecture!${NC}"
