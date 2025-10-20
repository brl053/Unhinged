#!/bin/bash

# ============================================================================
# Proto-to-Polyglot Client Libraries Build Script
# ============================================================================
#
# Generates client libraries for multiple programming languages from protobuf
# service definitions. Integrates with the custom build system for caching
# and dependency management.
#
# Author: Distributed Systems Architect
# Version: 1.0.0
# Date: 2025-10-20
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BUILD_DIR="$PROJECT_ROOT/build"

echo -e "${BLUE}🔧 Proto-to-Polyglot Client Libraries Build Pipeline${NC}\n"

# ============================================================================
# ENVIRONMENT VALIDATION
# ============================================================================

echo -e "${YELLOW}Validating build environment...${NC}"

# Check if build system is available
if [ ! -f "$BUILD_DIR/build.py" ]; then
    echo -e "${RED}❌ Build system not found at $BUILD_DIR/build.py${NC}"
    exit 1
fi

# Check Python dependencies
if ! python3 -c "import yaml, psutil" 2>/dev/null; then
    echo -e "${RED}❌ Missing Python dependencies. Install with:${NC}"
    echo -e "  pip install pyyaml psutil"
    exit 1
fi

# Check protoc
if ! command -v protoc &> /dev/null; then
    echo -e "${RED}❌ protoc is not installed${NC}"
    echo -e "${YELLOW}Please install Protocol Buffers compiler:${NC}"
    echo -e "  macOS: brew install protobuf"
    echo -e "  Ubuntu: sudo apt-get install protobuf-compiler"
    echo -e "  Windows: Download from https://github.com/protocolbuffers/protobuf/releases"
    exit 1
fi

# Check npm and required packages
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm is not installed${NC}"
    exit 1
fi

# Check if ts-proto is installed
if [ ! -f "$PROJECT_ROOT/node_modules/.bin/protoc-gen-ts_proto" ]; then
    echo -e "${YELLOW}Installing ts-proto...${NC}"
    cd "$PROJECT_ROOT"
    npm install ts-proto --save-dev
fi

echo -e "${GREEN}✅ Environment validation passed${NC}\n"

# ============================================================================
# BUILD EXECUTION
# ============================================================================

echo -e "${BLUE}🚀 Starting proto client generation...${NC}"

# Parse command line arguments
LANGUAGES="typescript,javascript"
CACHE_ENABLED="true"
PARALLEL="true"
VERBOSE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --languages)
            LANGUAGES="$2"
            shift 2
            ;;
        --all-languages)
            LANGUAGES="all"
            shift
            ;;
        --no-cache)
            CACHE_ENABLED="false"
            shift
            ;;
        --no-parallel)
            PARALLEL="false"
            shift
            ;;
        --verbose|-v)
            VERBOSE="--verbose"
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --languages LANGS     Comma-separated list of languages (typescript,javascript,python,kotlin,go)"
            echo "  --all-languages       Generate clients for all supported languages"
            echo "  --no-cache           Disable build caching"
            echo "  --no-parallel        Disable parallel execution"
            echo "  --verbose, -v        Enable verbose output"
            echo "  --help, -h           Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                                    # Generate TypeScript and JavaScript clients"
            echo "  $0 --all-languages                   # Generate clients for all languages"
            echo "  $0 --languages typescript,python     # Generate only TypeScript and Python clients"
            echo "  $0 --verbose --no-cache              # Verbose output without caching"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Determine build targets based on languages
if [ "$LANGUAGES" = "all" ]; then
    BUILD_TARGET="proto-clients-all"
    echo -e "${YELLOW}Generating clients for all supported languages${NC}"
else
    # For specific languages, use individual targets
    IFS=',' read -ra LANG_ARRAY <<< "$LANGUAGES"
    BUILD_TARGETS=()
    
    for lang in "${LANG_ARRAY[@]}"; do
        lang=$(echo "$lang" | xargs) # trim whitespace
        case $lang in
            typescript|javascript|python|kotlin|go)
                BUILD_TARGETS+=("proto-clients-$lang")
                ;;
            *)
                echo -e "${RED}❌ Unsupported language: $lang${NC}"
                echo "Supported languages: typescript, javascript, python, kotlin, go"
                exit 1
                ;;
        esac
    done
    
    if [ ${#BUILD_TARGETS[@]} -eq 0 ]; then
        echo -e "${RED}❌ No valid languages specified${NC}"
        exit 1
    fi
    
    echo -e "${YELLOW}Generating clients for: ${LANG_ARRAY[*]}${NC}"
fi

# Build command construction
BUILD_CMD="python3 $BUILD_DIR/build.py build"

if [ "$LANGUAGES" = "all" ]; then
    BUILD_CMD="$BUILD_CMD $BUILD_TARGET"
else
    BUILD_CMD="$BUILD_CMD ${BUILD_TARGETS[*]}"
fi

# Add build options
if [ "$PARALLEL" = "true" ]; then
    BUILD_CMD="$BUILD_CMD --parallel"
fi

if [ "$CACHE_ENABLED" = "false" ]; then
    BUILD_CMD="$BUILD_CMD --no-cache"
fi

if [ -n "$VERBOSE" ]; then
    BUILD_CMD="$BUILD_CMD $VERBOSE"
fi

echo -e "${BLUE}Executing: $BUILD_CMD${NC}\n"

# Execute the build
cd "$PROJECT_ROOT"
if eval "$BUILD_CMD"; then
    echo -e "\n${GREEN}✅ Proto client generation completed successfully!${NC}"
else
    echo -e "\n${RED}❌ Proto client generation failed${NC}"
    exit 1
fi

# ============================================================================
# POST-BUILD VALIDATION
# ============================================================================

echo -e "\n${YELLOW}Validating generated clients...${NC}"

GENERATED_DIR="$PROJECT_ROOT/generated"
VALIDATION_PASSED=true

# Check TypeScript clients
if [[ "$LANGUAGES" == *"typescript"* ]] || [ "$LANGUAGES" = "all" ]; then
    TS_DIR="$GENERATED_DIR/typescript/clients"
    if [ -d "$TS_DIR" ] && [ "$(find "$TS_DIR" -name "*.ts" | wc -l)" -gt 0 ]; then
        echo -e "${GREEN}✅ TypeScript clients generated${NC}"
    else
        echo -e "${RED}❌ TypeScript client generation failed${NC}"
        VALIDATION_PASSED=false
    fi
fi

# Check JavaScript clients
if [[ "$LANGUAGES" == *"javascript"* ]] || [ "$LANGUAGES" = "all" ]; then
    JS_DIR="$GENERATED_DIR/javascript/clients"
    API_REGISTRY="$PROJECT_ROOT/generated/static_html/api-clients.js"
    
    if [ -d "$JS_DIR" ] && [ "$(find "$JS_DIR" -name "*.js" | wc -l)" -gt 0 ]; then
        echo -e "${GREEN}✅ JavaScript clients generated${NC}"
    else
        echo -e "${RED}❌ JavaScript client generation failed${NC}"
        VALIDATION_PASSED=false
    fi
    
    if [ -f "$API_REGISTRY" ]; then
        echo -e "${GREEN}✅ API registry generated for browser consumption${NC}"
    else
        echo -e "${RED}❌ API registry generation failed${NC}"
        VALIDATION_PASSED=false
    fi
fi

# Check Python clients
if [[ "$LANGUAGES" == *"python"* ]] || [ "$LANGUAGES" = "all" ]; then
    PY_DIR="$GENERATED_DIR/python/clients"
    if [ -d "$PY_DIR" ] && [ "$(find "$PY_DIR" -name "*.py" | wc -l)" -gt 0 ]; then
        echo -e "${GREEN}✅ Python clients generated${NC}"
    else
        echo -e "${RED}❌ Python client generation failed${NC}"
        VALIDATION_PASSED=false
    fi
fi

# ============================================================================
# SUMMARY
# ============================================================================

echo -e "\n${BLUE}📋 Build Summary:${NC}"
echo -e "${YELLOW}Generated client libraries for:${NC}"

if [ "$LANGUAGES" = "all" ]; then
    echo -e "  • TypeScript (gRPC-Web support)"
    echo -e "  • JavaScript (Browser-compatible)"
    echo -e "  • Python (Backend services)"
    echo -e "  • Kotlin (JVM services)"
    echo -e "  • Go (Microservices)"
else
    IFS=',' read -ra LANG_ARRAY <<< "$LANGUAGES"
    for lang in "${LANG_ARRAY[@]}"; do
        lang=$(echo "$lang" | xargs)
        echo -e "  • $lang"
    done
fi

echo -e "\n${YELLOW}Output locations:${NC}"
echo -e "  • Generated clients: $GENERATED_DIR/"
echo -e "  • Browser API registry: generated/static_html/api-clients.js (symlinked)"
echo -e "  • Tab integration: control/static_html/shared/api-integration.js"

if [ "$VALIDATION_PASSED" = true ]; then
    echo -e "\n${GREEN}🎉 Proto-to-polyglot client pipeline completed successfully!${NC}"
    echo -e "\n${BLUE}Next steps:${NC}"
    echo -e "1. Import generated clients in your services"
    echo -e "2. Use APITabIntegration for browser-based service calls"
    echo -e "3. Test service communication through the tab system"
    echo -e "4. Monitor service health through the control plane"
    exit 0
else
    echo -e "\n${RED}❌ Some client generations failed. Check the logs above.${NC}"
    exit 1
fi
