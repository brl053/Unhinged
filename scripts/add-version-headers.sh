#!/bin/bash

# ============================================================================
# Add Version Headers to Generated Files
# ============================================================================
# 
# Adds version and hash information to generated protobuf files for validation
# ============================================================================

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION_FILE="$PROJECT_ROOT/version.json"

# Get version info
if [ -f "$VERSION_FILE" ]; then
    PROTO_VERSION=$(node -p "JSON.parse(require('fs').readFileSync('$VERSION_FILE', 'utf8')).components.proto.version" 2>/dev/null || echo "unknown")
    PROTO_HASH=$(node -p "JSON.parse(require('fs').readFileSync('$VERSION_FILE', 'utf8')).components.proto.hash" 2>/dev/null || echo "unknown")
    BUILD_NUMBER=$(node -p "JSON.parse(require('fs').readFileSync('$VERSION_FILE', 'utf8')).build" 2>/dev/null || echo "unknown")
    GENERATION_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
else
    PROTO_VERSION="unknown"
    PROTO_HASH="unknown"
    BUILD_NUMBER="unknown"
    GENERATION_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
fi

# ============================================================================
# TypeScript Files
# ============================================================================

add_typescript_header() {
    local file="$1"
    if [ -f "$file" ]; then
        # Create temporary file with version header
        cat > "${file}.tmp" << EOF
// ============================================================================
// GENERATED FILE - DO NOT EDIT
// ============================================================================
// Proto Version: $PROTO_VERSION
// Proto Hash: $PROTO_HASH
// Build: $BUILD_NUMBER
// Generated: $GENERATION_TIME
// 
// This file was automatically generated from protobuf schemas.
// To regenerate: npm run build:proto
// 
// Version validation: If proto hash changes, regenerate this file.
// ============================================================================

EOF
        # Append original content (skip first line if it's already a comment)
        if head -1 "$file" | grep -q "^//"; then
            tail -n +2 "$file" >> "${file}.tmp"
        else
            cat "$file" >> "${file}.tmp"
        fi
        
        # Replace original file
        mv "${file}.tmp" "$file"
        echo "Added version header to: $file"
    fi
}

# ============================================================================
# Kotlin Files
# ============================================================================

add_kotlin_header() {
    local file="$1"
    if [ -f "$file" ]; then
        # Create temporary file with version header
        cat > "${file}.tmp" << EOF
// ============================================================================
// GENERATED FILE - DO NOT EDIT
// ============================================================================
// Proto Version: $PROTO_VERSION
// Proto Hash: $PROTO_HASH
// Build: $BUILD_NUMBER
// Generated: $GENERATION_TIME
// 
// This file was automatically generated from protobuf schemas.
// To regenerate: npm run build:proto
// 
// Version validation: If proto hash changes, regenerate this file.
// ============================================================================

EOF
        # Append original content (skip first line if it's already a comment)
        if head -1 "$file" | grep -q "^//"; then
            tail -n +2 "$file" >> "${file}.tmp"
        else
            cat "$file" >> "${file}.tmp"
        fi
        
        # Replace original file
        mv "${file}.tmp" "$file"
        echo "Added version header to: $file"
    fi
}

# ============================================================================
# Process Files
# ============================================================================

echo "Adding version headers to generated files..."

# TypeScript files
if [ -d "$PROJECT_ROOT/frontend/src/types/generated" ]; then
    find "$PROJECT_ROOT/frontend/src/types/generated" -name "*.ts" -type f | while read -r file; do
        add_typescript_header "$file"
    done
fi

# Kotlin files
if [ -d "$PROJECT_ROOT/backend/src/main/kotlin/unhinged/document_store" ]; then
    find "$PROJECT_ROOT/backend/src/main/kotlin/unhinged/document_store" -name "*.kt" -type f | while read -r file; do
        add_kotlin_header "$file"
    done
fi

# Java files (generated alongside Kotlin)
if [ -d "$PROJECT_ROOT/backend/src/main/kotlin/unhinged/document_store" ]; then
    find "$PROJECT_ROOT/backend/src/main/kotlin/unhinged/document_store" -name "*.java" -type f | while read -r file; do
        add_kotlin_header "$file"
    done
fi

echo "Version headers added successfully!"
echo "Proto Version: $PROTO_VERSION"
echo "Proto Hash: $PROTO_HASH"
echo "Build: $BUILD_NUMBER"
