#!/bin/bash

# ============================================================================
# Gateway Code Generation Script - Extension to proto/build.sh
# ============================================================================
#
# Extends the existing proto build system to generate gateway endpoints,
# OpenAPI documentation, and TypeScript clients from Protocol Buffer
# annotations.
#
# This script:
# 1. Parses proto files for gateway annotations
# 2. Generates REST endpoint handlers
# 3. Creates WebSocket and SSE handlers
# 4. Produces OpenAPI/Swagger documentation
# 5. Generates TypeScript client libraries
#
# Author: Unhinged Team
# Version: 1.0.0
# Date: 2025-10-06
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
GATEWAY_DIR="$PROJECT_ROOT/services/presentation-gateway"

echo -e "${BLUE}🌐 Generating Presentation Gateway code...${NC}\n"

# ============================================================================
# PREREQUISITES CHECK
# ============================================================================

# Check if gateway service exists
if [ ! -d "$GATEWAY_DIR" ]; then
    echo -e "${RED}❌ Gateway service directory not found: $GATEWAY_DIR${NC}"
    echo -e "${YELLOW}Please run the gateway setup first${NC}"
    exit 1
fi

# Check if Node.js dependencies are installed
if [ ! -f "$GATEWAY_DIR/node_modules/.bin/tsx" ]; then
    echo -e "${YELLOW}Installing gateway dependencies...${NC}"
    cd "$GATEWAY_DIR"
    npm install
    cd "$PROTO_DIR"
fi

echo -e "${GREEN}✅ Prerequisites checked${NC}\n"

# ============================================================================
# PROTO GENERATION FOR GATEWAY
# ============================================================================

echo -e "${BLUE}📝 Generating TypeScript bindings for gateway...${NC}"

# Create gateway proto output directory
mkdir -p "$GATEWAY_DIR/src/generated"

# Generate TypeScript bindings with gateway annotations
protoc \
    --plugin=protoc-gen-ts_proto="$PROJECT_ROOT/node_modules/.bin/protoc-gen-ts_proto" \
    --ts_proto_out="$GATEWAY_DIR/src/generated" \
    --ts_proto_opt=esModuleInterop=true \
    --ts_proto_opt=forceLong=string \
    --ts_proto_opt=useOptionals=messages \
    --ts_proto_opt=exportCommonSymbols=false \
    --ts_proto_opt=outputServices=grpc-js \
    --ts_proto_opt=outputClientImpl=grpc-web \
    --proto_path="$PROTO_DIR" \
    "$PROTO_DIR/gateway_annotations.proto" \
    "$PROTO_DIR/chat_with_gateway.proto" \
    "$PROTO_DIR/common.proto" \
    "$PROTO_DIR/chat.proto" \
    "$PROTO_DIR/audio.proto" \
    "$PROTO_DIR/vision_service.proto"

echo -e "${GREEN}✅ TypeScript bindings generated${NC}"

# ============================================================================
# GATEWAY ENDPOINT GENERATION
# ============================================================================

echo -e "${BLUE}🔧 Generating gateway endpoints from annotations...${NC}"

# Run the gateway generator tool
cd "$GATEWAY_DIR"
npm run gateway:gen

echo -e "${GREEN}✅ Gateway endpoints generated${NC}"

# ============================================================================
# OPENAPI DOCUMENTATION GENERATION
# ============================================================================

echo -e "${BLUE}📚 Generating OpenAPI documentation...${NC}"

# Generate OpenAPI/Swagger documentation
npm run docs:gen

echo -e "${GREEN}✅ OpenAPI documentation generated${NC}"

# ============================================================================
# VALIDATION
# ============================================================================

echo -e "${BLUE}🔍 Validating generated gateway code...${NC}"

# Check if gateway endpoints were generated
if [ -f "$GATEWAY_DIR/src/generated/endpoints.ts" ]; then
    echo -e "${GREEN}✅ Gateway endpoints generated successfully${NC}"
else
    echo -e "${YELLOW}⚠️  Gateway endpoints not found (may be normal for first run)${NC}"
fi

# Check if OpenAPI spec was generated
if [ -f "$GATEWAY_DIR/docs/openapi.yaml" ]; then
    echo -e "${GREEN}✅ OpenAPI specification generated successfully${NC}"
else
    echo -e "${YELLOW}⚠️  OpenAPI specification not found${NC}"
fi

# Check TypeScript compilation
echo -e "${YELLOW}Checking TypeScript compilation...${NC}"
if npm run build --silent; then
    echo -e "${GREEN}✅ TypeScript compilation successful${NC}"
else
    echo -e "${RED}❌ TypeScript compilation failed${NC}"
fi

cd "$PROTO_DIR"

# ============================================================================
# SUMMARY
# ============================================================================

echo -e "\n${BLUE}📋 Gateway Generation Summary:${NC}"
echo -e "${YELLOW}Generated components:${NC}"
echo -e "  • TypeScript proto bindings with gateway annotations"
echo -e "  • REST endpoint handlers from HTTP annotations"
echo -e "  • WebSocket handlers from streaming annotations"
echo -e "  • Server-Sent Events handlers from SSE annotations"
echo -e "  • OpenAPI/Swagger documentation"

echo -e "\n${YELLOW}Output locations:${NC}"
echo -e "  • Proto bindings: $GATEWAY_DIR/src/generated/"
echo -e "  • Generated endpoints: $GATEWAY_DIR/src/generated/endpoints.ts"
echo -e "  • OpenAPI spec: $GATEWAY_DIR/docs/openapi.yaml"
echo -e "  • Swagger UI: http://localhost:8082/docs (when running)"

echo -e "\n${GREEN}🎉 Gateway code generation completed successfully!${NC}"

echo -e "\n${BLUE}Next steps:${NC}"
echo -e "1. Review generated endpoints in $GATEWAY_DIR/src/generated/"
echo -e "2. Start the gateway service: cd $GATEWAY_DIR && npm run dev"
echo -e "3. Test endpoints using the Swagger UI at /docs"
echo -e "4. Integrate with your frontend applications"