#!/bin/bash

# ============================================================================
# Generated Files Validation Script
# ============================================================================
# 
# Validates that all required protobuf-generated files exist before building.
# This ensures the build process includes protobuf generation.
#
# Usage: ./scripts/validate-generated.sh
# Exit codes: 0 = success, 1 = missing files
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo -e "${BLUE}🔍 Validating generated protobuf files...${NC}\n"

# Track validation status
VALIDATION_FAILED=false

# ============================================================================
# Frontend TypeScript Files
# ============================================================================

echo -e "${YELLOW}Checking Frontend TypeScript files...${NC}"

FRONTEND_FILES=(
    "frontend/src/types/generated/document_store.ts"
    "frontend/src/types/generated/google/protobuf/timestamp.ts"
    "frontend/src/types/generated/google/protobuf/struct.ts"
)

for file in "${FRONTEND_FILES[@]}"; do
    if [ -f "$PROJECT_ROOT/$file" ]; then
        echo -e "  ${GREEN}✅ $file${NC}"
    else
        echo -e "  ${RED}❌ $file${NC}"
        VALIDATION_FAILED=true
    fi
done

# ============================================================================
# Backend Kotlin Files
# ============================================================================

echo -e "\n${YELLOW}Checking Backend Kotlin files...${NC}"

BACKEND_FILES=(
    "backend/src/main/kotlin/unhinged/document_store/DocumentKt.kt"
    "backend/src/main/kotlin/unhinged/document_store/DocumentStore.java"
    "backend/src/main/kotlin/unhinged/document_store/PutDocumentRequestKt.kt"
    "backend/src/main/kotlin/unhinged/document_store/GetDocumentRequestKt.kt"
)

for file in "${BACKEND_FILES[@]}"; do
    if [ -f "$PROJECT_ROOT/$file" ]; then
        echo -e "  ${GREEN}✅ $file${NC}"
    else
        echo -e "  ${RED}❌ $file${NC}"
        VALIDATION_FAILED=true
    fi
done

# ============================================================================
# Version Hash Validation
# ============================================================================

echo -e "\n${YELLOW}Checking version hash compatibility...${NC}"

VERSION_FILE="$PROJECT_ROOT/version.json"
if [ -f "$VERSION_FILE" ]; then
    EXPECTED_HASH=$(node -p "JSON.parse(require('fs').readFileSync('$VERSION_FILE', 'utf8')).components.proto.hash" 2>/dev/null || echo "unknown")

    # Check TypeScript files for hash
    TS_FILE="$PROJECT_ROOT/frontend/src/types/generated/document_store.ts"
    if [ -f "$TS_FILE" ]; then
        if grep -q "Proto Hash: $EXPECTED_HASH" "$TS_FILE"; then
            echo -e "  ${GREEN}✅ TypeScript files have correct hash${NC}"
        else
            echo -e "  ${YELLOW}⚠️  TypeScript files may be outdated${NC}"
            VALIDATION_FAILED=true
        fi
    fi

    # Check Kotlin files for hash
    KT_FILE="$PROJECT_ROOT/backend/src/main/kotlin/unhinged/document_store/DocumentKt.kt"
    if [ -f "$KT_FILE" ]; then
        if grep -q "Proto Hash: $EXPECTED_HASH" "$KT_FILE"; then
            echo -e "  ${GREEN}✅ Kotlin files have correct hash${NC}"
        else
            echo -e "  ${YELLOW}⚠️  Kotlin files may be outdated${NC}"
            VALIDATION_FAILED=true
        fi
    fi
else
    echo -e "  ${YELLOW}⚠️  version.json not found${NC}"
fi

# ============================================================================
# Validation Results
# ============================================================================

echo ""

if [ "$VALIDATION_FAILED" = true ]; then
    echo -e "${RED}❌ Validation failed! Missing or outdated generated files.${NC}"
    echo -e "${YELLOW}Run the following command to generate/update files:${NC}"
    echo -e "  ${BLUE}npm run build:proto${NC}"
    echo -e "  ${BLUE}# or directly: ./proto/build.sh${NC}"
    echo ""
    echo -e "${YELLOW}Note: Generated files are not committed to git.${NC}"
    echo -e "${YELLOW}They must be generated locally or in CI/CD.${NC}"
    exit 1
else
    echo -e "${GREEN}✅ All generated files are present and up-to-date!${NC}"
    echo -e "${BLUE}Ready to build services.${NC}"
    exit 0
fi
