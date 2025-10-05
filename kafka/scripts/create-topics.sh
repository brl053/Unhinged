#!/bin/bash

# ============================================================================
# Kafka Topic Creation Script
# ============================================================================
# 
# Creates all necessary Kafka topics for the Universal System CDC pipeline
# with appropriate partitioning and retention policies.
#
# Author: LLM Agent
# Version: 1.0.0
# Date: 2025-01-04
# ============================================================================

set -e

# Configuration
KAFKA_BROKER="localhost:9092"
REPLICATION_FACTOR=1  # Single broker for development
DEFAULT_PARTITIONS=3   # Balanced for current scale

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Creating Kafka topics for Universal System CDC...${NC}"

# Function to create topic with custom configuration
create_topic() {
    local topic_name=$1
    local partitions=$2
    local retention_ms=$3
    local segment_ms=$4
    local description=$5
    
    echo -e "${YELLOW}📝 Creating topic: ${topic_name}${NC}"
    echo -e "   Partitions: ${partitions}"
    echo -e "   Retention: ${retention_ms}ms ($(($retention_ms / 86400000)) days)"
    echo -e "   Description: ${description}"
    
    kafka-topics --create \
        --bootstrap-server $KAFKA_BROKER \
        --topic $topic_name \
        --partitions $partitions \
        --replication-factor $REPLICATION_FACTOR \
        --config retention.ms=$retention_ms \
        --config segment.ms=$segment_ms \
        --config compression.type=snappy \
        --config cleanup.policy=delete \
        --if-not-exists
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Topic ${topic_name} created successfully${NC}\n"
    else
        echo -e "${RED}❌ Failed to create topic ${topic_name}${NC}\n"
        exit 1
    fi
}

# Function to create compacted topic (for state management)
create_compacted_topic() {
    local topic_name=$1
    local partitions=$2
    local description=$3
    
    echo -e "${YELLOW}📝 Creating compacted topic: ${topic_name}${NC}"
    echo -e "   Partitions: ${partitions}"
    echo -e "   Cleanup: Log compaction"
    echo -e "   Description: ${description}"
    
    kafka-topics --create \
        --bootstrap-server $KAFKA_BROKER \
        --topic $topic_name \
        --partitions $partitions \
        --replication-factor $REPLICATION_FACTOR \
        --config cleanup.policy=compact \
        --config compression.type=snappy \
        --config min.cleanable.dirty.ratio=0.1 \
        --config segment.ms=86400000 \
        --if-not-exists
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Compacted topic ${topic_name} created successfully${NC}\n"
    else
        echo -e "${RED}❌ Failed to create compacted topic ${topic_name}${NC}\n"
        exit 1
    fi
}

# ============================================================================
# OLTP TOPICS - Real-time operational events
# ============================================================================

echo -e "${BLUE}📊 Creating OLTP topics for real-time events...${NC}\n"

# LLM events - high value for training, medium retention
create_topic "llm-events" 6 604800000 86400000 "LLM inference events with rich rationale"

# Tool usage events - analytical value, medium retention  
create_topic "tool-events" 6 604800000 86400000 "Tool execution events with outcome analysis"

# Workflow events - strict ordering required, long retention for audit
create_topic "workflow-events" 3 2592000000 86400000 "Workflow execution events with decision tracking"

# Voice processing events - large payloads, shorter retention
create_topic "voice-events" 4 259200000 43200000 "Voice transcription and synthesis events"

# UI events - high frequency, shorter retention
create_topic "ui-events" 8 259200000 43200000 "UI generation and interaction events"

# System events - errors, metrics, health checks
create_topic "system-events" 3 1209600000 86400000 "System health, errors, and performance metrics"

# ============================================================================
# OLAP TOPICS - Analytics and ML training
# ============================================================================

echo -e "${BLUE}📈 Creating OLAP topics for analytics...${NC}\n"

# Analytics aggregations - pre-computed metrics
create_topic "analytics-aggregations" 4 2592000000 86400000 "Pre-computed analytics and metrics"

# ML training data - long retention for model training
create_topic "ml-training-events" 6 7776000000 86400000 "Curated events for ML model training"

# Decision tracking - for DAG decision engine
create_topic "decision-tracking" 3 2592000000 86400000 "Decision points and outcomes for learning"

# ============================================================================
# DEAD LETTER QUEUES
# ============================================================================

echo -e "${BLUE}💀 Creating dead letter queue topics...${NC}\n"

# Dead letter queue for failed events
create_topic "dlq-failed-events" 3 2592000000 86400000 "Dead letter queue for failed event processing"

# Dead letter queue for schema validation failures
create_topic "dlq-schema-failures" 2 1209600000 86400000 "Events that failed schema validation"

# ============================================================================
# STATE MANAGEMENT TOPICS (Compacted)
# ============================================================================

echo -e "${BLUE}🗃️ Creating state management topics...${NC}\n"

# Workflow state snapshots
create_compacted_topic "workflow-state" 3 "Current state of all workflows"

# User session state
create_compacted_topic "session-state" 6 "Current state of user sessions"

# System configuration state
create_compacted_topic "config-state" 1 "System configuration and feature flags"

# ============================================================================
# MONITORING AND OBSERVABILITY
# ============================================================================

echo -e "${BLUE}👁️ Creating monitoring topics...${NC}\n"

# Metrics and monitoring data
create_topic "metrics-events" 4 604800000 43200000 "System metrics and performance data"

# Audit trail - long retention for compliance
create_topic "audit-trail" 2 7776000000 86400000 "Audit events for compliance and security"

# Alerts and notifications
create_topic "alert-events" 2 1209600000 86400000 "System alerts and notifications"

# ============================================================================
# VERIFY TOPIC CREATION
# ============================================================================

echo -e "${BLUE}🔍 Verifying topic creation...${NC}\n"

kafka-topics --list --bootstrap-server $KAFKA_BROKER | grep -E "(llm-events|tool-events|workflow-events|voice-events|ui-events|system-events)"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ All core topics created successfully!${NC}"
else
    echo -e "${RED}❌ Some topics may not have been created properly${NC}"
    exit 1
fi

# ============================================================================
# TOPIC CONFIGURATION SUMMARY
# ============================================================================

echo -e "${BLUE}📋 Topic Configuration Summary:${NC}"
echo -e "${YELLOW}OLTP Topics (Real-time):${NC}"
echo -e "  • llm-events: 6 partitions, 7 days retention"
echo -e "  • tool-events: 6 partitions, 7 days retention"
echo -e "  • workflow-events: 3 partitions, 30 days retention"
echo -e "  • voice-events: 4 partitions, 3 days retention"
echo -e "  • ui-events: 8 partitions, 3 days retention"
echo -e "  • system-events: 3 partitions, 14 days retention"

echo -e "${YELLOW}OLAP Topics (Analytics):${NC}"
echo -e "  • analytics-aggregations: 4 partitions, 30 days retention"
echo -e "  • ml-training-events: 6 partitions, 90 days retention"
echo -e "  • decision-tracking: 3 partitions, 30 days retention"

echo -e "${YELLOW}Infrastructure Topics:${NC}"
echo -e "  • dlq-failed-events: 3 partitions, 30 days retention"
echo -e "  • workflow-state: 3 partitions, compacted"
echo -e "  • session-state: 6 partitions, compacted"
echo -e "  • audit-trail: 2 partitions, 90 days retention"

echo -e "${GREEN}🎉 Kafka topic setup completed successfully!${NC}"
echo -e "${BLUE}Next steps:${NC}"
echo -e "  1. Start the EventProducerService"
echo -e "  2. Run database migrations"
echo -e "  3. Configure Kafka Connect for CDC"
echo -e "  4. Set up monitoring dashboards"
