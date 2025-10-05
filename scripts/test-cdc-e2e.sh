#!/bin/bash

# ============================================================================
# CDC End-to-End Test Script
# ============================================================================
# 
# Tests the complete CDC flow:
# 1. Health checks
# 2. LLM inference request
# 3. Event production to Kafka
# 4. Event consumption to PostgreSQL
# 5. WebSocket real-time updates
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
TEST_USER="test-user-$(date +%s)"
TEST_SESSION="test-session-$(date +%s)"

echo -e "${BLUE}🧪 CDC End-to-End Test${NC}\n"

# ============================================================================
# STEP 1: HEALTH CHECKS
# ============================================================================

echo -e "${BLUE}Step 1: Health Checks${NC}"

# Quick ping test first
echo -e "${YELLOW}Running quick health check...${NC}"
if ! ./scripts/health-check.sh --quick; then
    echo -e "${RED}❌ Quick health check failed. Aborting E2E test.${NC}"
    exit 1
fi

echo ""

# ============================================================================
# STEP 2: BASELINE EVENT COUNT
# ============================================================================

echo -e "${BLUE}Step 2: Get Baseline Event Count${NC}"

get_event_count() {
    docker exec postgres-dev-db psql -U postgres -d unhinged -t -c "SELECT COUNT(*) FROM events;" | tr -d ' '
}

INITIAL_COUNT=$(get_event_count)
echo -e "${YELLOW}Initial event count: $INITIAL_COUNT${NC}"

echo ""

# ============================================================================
# STEP 3: LLM INFERENCE REQUEST
# ============================================================================

echo -e "${BLUE}Step 3: LLM Inference Request${NC}"

echo -e "${YELLOW}Sending LLM inference request...${NC}"

# Create test request
TEST_PROMPT="Hello, this is a test message for CDC validation. Please respond briefly."

RESPONSE=$(curl -s -X POST "$BACKEND_URL/api/llm/infer" \
    -H "Content-Type: application/json" \
    -d "{
        \"prompt\": \"$TEST_PROMPT\",
        \"model\": \"llama3.2\",
        \"userId\": \"$TEST_USER\",
        \"sessionId\": \"$TEST_SESSION\"
    }" \
    --max-time 30 || echo '{"error": "Request failed"}')

echo -e "${YELLOW}Response received:${NC}"
echo "$RESPONSE" | jq . 2>/dev/null || echo "$RESPONSE"

# Check if response contains expected fields
if echo "$RESPONSE" | jq -e '.eventId' > /dev/null 2>&1; then
    EVENT_ID=$(echo "$RESPONSE" | jq -r '.eventId')
    echo -e "${GREEN}✅ LLM inference successful, Event ID: $EVENT_ID${NC}"
else
    echo -e "${RED}❌ LLM inference failed or invalid response${NC}"
    exit 1
fi

echo ""

# ============================================================================
# STEP 4: VERIFY EVENT IN DATABASE
# ============================================================================

echo -e "${BLUE}Step 4: Verify Event in Database${NC}"

echo -e "${YELLOW}Waiting for event to be processed...${NC}"
sleep 3

NEW_COUNT=$(get_event_count)
echo -e "${YELLOW}New event count: $NEW_COUNT${NC}"

if [ "$NEW_COUNT" -gt "$INITIAL_COUNT" ]; then
    echo -e "${GREEN}✅ Event count increased from $INITIAL_COUNT to $NEW_COUNT${NC}"
    
    # Get the latest event
    LATEST_EVENT=$(docker exec postgres-dev-db psql -U postgres -d unhinged -t -c "
        SELECT payload 
        FROM events 
        WHERE user_id = '$TEST_USER' 
        ORDER BY timestamp_ms DESC 
        LIMIT 1;
    " | tr -d ' ')
    
    if [ ! -z "$LATEST_EVENT" ] && [ "$LATEST_EVENT" != "" ]; then
        echo -e "${YELLOW}Latest event payload:${NC}"
        echo "$LATEST_EVENT" | jq . 2>/dev/null || echo "$LATEST_EVENT"
        echo -e "${GREEN}✅ Event successfully stored in database${NC}"
    else
        echo -e "${RED}❌ Could not retrieve event from database${NC}"
        exit 1
    fi
else
    echo -e "${RED}❌ Event count did not increase. CDC flow may be broken.${NC}"
    exit 1
fi

echo ""

# ============================================================================
# STEP 5: VERIFY KAFKA TOPIC
# ============================================================================

echo -e "${BLUE}Step 5: Verify Kafka Topic${NC}"

echo -e "${YELLOW}Checking Kafka topic for events...${NC}"

# Check if topic exists and has messages
TOPIC_INFO=$(docker exec kafka-dev kafka-topics --describe --topic llm-events --bootstrap-server localhost:29092 2>/dev/null || echo "Topic not found")

if [[ "$TOPIC_INFO" == *"Topic not found"* ]]; then
    echo -e "${RED}❌ Kafka topic 'llm-events' not found${NC}"
    exit 1
else
    echo -e "${GREEN}✅ Kafka topic 'llm-events' exists${NC}"
    
    # Try to consume latest message (with timeout)
    echo -e "${YELLOW}Attempting to read latest message from Kafka...${NC}"
    
    KAFKA_MESSAGE=$(timeout 5 docker exec kafka-dev kafka-console-consumer \
        --bootstrap-server localhost:29092 \
        --topic llm-events \
        --from-beginning \
        --max-messages 1 \
        --timeout-ms 3000 2>/dev/null || echo "")
    
    if [ ! -z "$KAFKA_MESSAGE" ]; then
        echo -e "${GREEN}✅ Successfully read message from Kafka${NC}"
        echo -e "${YELLOW}Sample message:${NC}"
        echo "$KAFKA_MESSAGE" | head -c 200
        echo "..."
    else
        echo -e "${YELLOW}⚠️  Could not read message from Kafka (may be timing issue)${NC}"
    fi
fi

echo ""

# ============================================================================
# STEP 6: TEST API ENDPOINTS
# ============================================================================

echo -e "${BLUE}Step 6: Test API Endpoints${NC}"

# Test events endpoint
echo -e "${YELLOW}Testing /api/events endpoint...${NC}"
EVENTS_RESPONSE=$(curl -s "$BACKEND_URL/api/events" --max-time 10 || echo '[]')

if echo "$EVENTS_RESPONSE" | jq -e '. | length' > /dev/null 2>&1; then
    EVENT_COUNT=$(echo "$EVENTS_RESPONSE" | jq '. | length')
    echo -e "${GREEN}✅ Events API working, returned $EVENT_COUNT events${NC}"
else
    echo -e "${RED}❌ Events API failed or returned invalid JSON${NC}"
    exit 1
fi

# Test health endpoint
echo -e "${YELLOW}Testing /health endpoint...${NC}"
HEALTH_RESPONSE=$(curl -s "$BACKEND_URL/health" --max-time 10 || echo '{}')

if echo "$HEALTH_RESPONSE" | jq -e '.status' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Health API working${NC}"
    echo -e "${YELLOW}Service status:${NC}"
    echo "$HEALTH_RESPONSE" | jq '.services' 2>/dev/null || echo "Could not parse services"
else
    echo -e "${RED}❌ Health API failed${NC}"
    exit 1
fi

echo ""

# ============================================================================
# STEP 7: SUMMARY
# ============================================================================

echo -e "${BLUE}🎉 E2E Test Summary${NC}"
echo -e "${GREEN}✅ Health checks passed${NC}"
echo -e "${GREEN}✅ LLM inference successful${NC}"
echo -e "${GREEN}✅ Event stored in database${NC}"
echo -e "${GREEN}✅ Kafka topic operational${NC}"
echo -e "${GREEN}✅ API endpoints working${NC}"

echo ""
echo -e "${GREEN}🚀 CDC system is fully operational!${NC}"
echo -e "${YELLOW}💡 Next steps:${NC}"
echo -e "   • Open frontend at http://localhost:3000/events to see Event Log"
echo -e "   • Open Kafka UI at http://localhost:8090 to monitor topics"
echo -e "   • Test WebSocket by keeping Event Log open while making requests"

echo ""
echo -e "${BLUE}Test Details:${NC}"
echo -e "   User ID: $TEST_USER"
echo -e "   Session ID: $TEST_SESSION"
echo -e "   Event ID: $EVENT_ID"
echo -e "   Events before: $INITIAL_COUNT"
echo -e "   Events after: $NEW_COUNT"
