#!/bin/bash

# Add local bin to PATH for protoc
export PATH="$HOME/bin:$PATH"

# ============================================================================
# Protocol Buffer Code Generation Script
# ============================================================================
#
# Generates language bindings for all services from protobuf schemas.
# Supports TypeScript, Kotlin, Python, and Go.
#
# ⚠️  IMPORTANT: Generated files are NOT committed to git!
# This script must be run locally and in CI/CD to generate code.
# Only .proto files are version controlled.
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
PROTO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$PROTO_DIR")"

echo -e "${BLUE}🔧 Generating Protocol Buffer bindings...${NC}\n"

# ============================================================================
# VERSION AND HASH VALIDATION
# ============================================================================

# Update proto hashes before generation
if [ -f "$PROJECT_ROOT/scripts/version-manager.sh" ]; then
    echo -e "${YELLOW}Updating proto hashes...${NC}"
    "$PROJECT_ROOT/scripts/version-manager.sh" update-hashes
fi

# Get version info for generated files
VERSION_FILE="$PROJECT_ROOT/version.json"
if [ -f "$VERSION_FILE" ]; then
    PROTO_VERSION=$(node -p "JSON.parse(require('fs').readFileSync('$VERSION_FILE', 'utf8')).components.proto.version" 2>/dev/null || echo "unknown")
    PROTO_HASH=$(node -p "JSON.parse(require('fs').readFileSync('$VERSION_FILE', 'utf8')).components.proto.hash" 2>/dev/null || echo "unknown")
    BUILD_NUMBER=$(node -p "JSON.parse(require('fs').readFileSync('$VERSION_FILE', 'utf8')).build" 2>/dev/null || echo "unknown")
else
    PROTO_VERSION="unknown"
    PROTO_HASH="unknown"
    BUILD_NUMBER="unknown"
fi

echo -e "${GREEN}Proto Version: $PROTO_VERSION${NC}"
echo -e "${GREEN}Proto Hash: $PROTO_HASH${NC}"
echo -e "${GREEN}Build: $BUILD_NUMBER${NC}\n"

# Check if protoc is installed
if ! command -v protoc &> /dev/null; then
    echo -e "${RED}❌ protoc is not installed${NC}"
    echo -e "${YELLOW}Please install Protocol Buffers compiler:${NC}"
    echo -e "  macOS: brew install protobuf"
    echo -e "  Ubuntu: sudo apt-get install protobuf-compiler"
    echo -e "  Windows: Download from https://github.com/protocolbuffers/protobuf/releases"
    exit 1
fi

echo -e "${GREEN}✅ protoc found: $(protoc --version)${NC}\n"

# ============================================================================
# TYPESCRIPT GENERATION (Frontend + Backend)
# ============================================================================

echo -e "${BLUE}📝 Generating TypeScript bindings...${NC}"

# Check if ts-proto is installed locally
if [ ! -f "$PROJECT_ROOT/node_modules/.bin/protoc-gen-ts_proto" ]; then
    echo -e "${YELLOW}Installing ts-proto locally...${NC}"
    cd "$PROJECT_ROOT"
    npm install ts-proto --save-dev
    cd "$PROTO_DIR"
fi

# Create output directories
mkdir -p "$PROJECT_ROOT/frontend/src/types/generated"
mkdir -p "$PROJECT_ROOT/backend/src/types/generated"

# Generate TypeScript bindings for frontend
protoc \
    --plugin=protoc-gen-ts_proto="$PROJECT_ROOT/node_modules/.bin/protoc-gen-ts_proto" \
    --ts_proto_out="$PROJECT_ROOT/frontend/src/types/generated" \
    --ts_proto_opt=esModuleInterop=true \
    --ts_proto_opt=forceLong=string \
    --ts_proto_opt=useOptionals=messages \
    --ts_proto_opt=exportCommonSymbols=false \
    --ts_proto_opt=outputServices=grpc-js \
    --proto_path="$PROTO_DIR" \
    "$PROTO_DIR/document_store.proto"

# Generate Kotlin bindings for backend
echo -e "${YELLOW}Generating Kotlin bindings...${NC}"
mkdir -p "$PROJECT_ROOT/backend/src/main/kotlin"

protoc \
    --kotlin_out="$PROJECT_ROOT/backend/src/main/kotlin" \
    --java_out="$PROJECT_ROOT/backend/src/main/kotlin" \
    --proto_path="$PROTO_DIR" \
    "$PROTO_DIR/document_store.proto"

echo -e "${GREEN}✅ Kotlin bindings generated${NC}"

echo -e "${GREEN}✅ TypeScript bindings generated${NC}"

# ============================================================================
# ADD VERSION HEADERS
# ============================================================================

echo -e "${YELLOW}Adding version headers to generated files...${NC}"
if [ -f "$PROJECT_ROOT/scripts/add-version-headers.sh" ]; then
    "$PROJECT_ROOT/scripts/add-version-headers.sh"
    echo -e "${GREEN}✅ Version headers added${NC}"
else
    echo -e "${YELLOW}⚠️  Version header script not found${NC}"
fi

# Python generation skipped for now - focusing on DocumentStore

# ============================================================================
# GO GENERATION (Future services)
# ============================================================================

echo -e "${BLUE}🐹 Generating Go bindings...${NC}"

# Create output directory
mkdir -p "$PROJECT_ROOT/services/go-services/proto"

# Check if protoc-gen-go is installed
if command -v protoc-gen-go &> /dev/null; then
    protoc \
        --go_out="$PROJECT_ROOT/services/go-services/proto" \
        --go_opt=paths=source_relative \
        --proto_path="$PROTO_DIR" \
        "$PROTO_DIR"/*.proto
    
    echo -e "${GREEN}✅ Go bindings generated${NC}"
else
    echo -e "${YELLOW}⚠️  protoc-gen-go not found, skipping Go generation${NC}"
    echo -e "${YELLOW}   Install with: go install google.golang.org/protobuf/cmd/protoc-gen-go@latest${NC}"
fi

# ============================================================================
# GENERATE DOCUMENTATION
# ============================================================================

echo -e "${BLUE}📚 Generating documentation...${NC}"

# Check if protoc-gen-doc is installed
if command -v protoc-gen-doc &> /dev/null; then
    mkdir -p "$PROJECT_ROOT/docs/proto"
    
    protoc \
        --doc_out="$PROJECT_ROOT/docs/proto" \
        --doc_opt=html,index.html \
        --proto_path="$PROTO_DIR" \
        "$PROTO_DIR"/*.proto
    
    echo -e "${GREEN}✅ Documentation generated at docs/proto/index.html${NC}"
else
    echo -e "${YELLOW}⚠️  protoc-gen-doc not found, skipping documentation${NC}"
    echo -e "${YELLOW}   Install with: go install github.com/pseudomuto/protoc-gen-doc/cmd/protoc-gen-doc@latest${NC}"
fi

# ============================================================================
# VALIDATION
# ============================================================================

echo -e "${BLUE}🔍 Validating generated files...${NC}"

# Check TypeScript files
if [ -f "$PROJECT_ROOT/services/frontend/src/types/proto/universal_event.ts" ]; then
    echo -e "${GREEN}✅ TypeScript files generated successfully${NC}"
else
    echo -e "${RED}❌ TypeScript generation failed${NC}"
fi

# Check Kotlin files
if [ -f "$PROJECT_ROOT/services/backend/src/main/kotlin/com/unhinged/cdc/UniversalEventProto.java" ]; then
    echo -e "${GREEN}✅ Kotlin files generated successfully${NC}"
else
    echo -e "${RED}❌ Kotlin generation failed${NC}"
fi

# Check Python files
if [ -f "$PROJECT_ROOT/services/whisper-tts/proto/universal_event_pb2.py" ]; then
    echo -e "${GREEN}✅ Python files generated successfully${NC}"
else
    echo -e "${RED}❌ Python generation failed${NC}"
fi

# ============================================================================
# SUMMARY
# ============================================================================

echo -e "\n${BLUE}📋 Generation Summary:${NC}"
echo -e "${YELLOW}Generated bindings for:${NC}"
echo -e "  • TypeScript (Frontend & Backend)"
echo -e "  • Kotlin (Backend)"
echo -e "  • Python (Whisper-TTS & Research Orchestrator)"
if command -v protoc-gen-go &> /dev/null; then
    echo -e "  • Go (Future services)"
fi

echo -e "\n${YELLOW}Output locations:${NC}"
echo -e "  • Frontend: services/frontend/src/types/proto/"
echo -e "  • Backend: services/backend/src/main/kotlin/com/unhinged/cdc/proto/"
echo -e "  • Python: services/whisper-tts/proto/ & services/research-orchestrator/proto/"
if command -v protoc-gen-go &> /dev/null; then
    echo -e "  • Go: services/go-services/proto/"
fi

echo -e "\n${GREEN}🎉 Protocol Buffer generation completed successfully!${NC}"

echo -e "\n${BLUE}Next steps:${NC}"
echo -e "1. Import generated types in your services"
echo -e "2. Implement EventProducer with protobuf serialization"
echo -e "3. Set up Kafka topics and consumers"
echo -e "4. Test event production and consumption"
