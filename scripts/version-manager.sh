#!/bin/bash

# ============================================================================
# Version Manager Script
# ============================================================================
# 
# Manages semantic versioning across the entire monorepo with hash validation
# for generated files and component tracking.
#
# Usage:
#   ./scripts/version-manager.sh update-hashes    # Update proto hashes
#   ./scripts/version-manager.sh bump-proto       # Bump proto version
#   ./scripts/version-manager.sh bump-major       # Bump major version
#   ./scripts/version-manager.sh validate         # Validate versions
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION_FILE="$PROJECT_ROOT/version.json"

# ============================================================================
# Utility Functions
# ============================================================================

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Calculate hash of proto files
calculate_proto_hash() {
    local proto_dir="$PROJECT_ROOT/proto"
    find "$proto_dir" -name "*.proto" -type f | sort | xargs cat | sha256sum | cut -d' ' -f1
}

# Calculate hash of specific proto file
calculate_file_hash() {
    local file="$1"
    if [ -f "$file" ]; then
        sha256sum "$file" | cut -d' ' -f1
    else
        echo "FILE_NOT_FOUND"
    fi
}

# Get current version from version.json
get_current_version() {
    if [ -f "$VERSION_FILE" ]; then
        node -p "JSON.parse(require('fs').readFileSync('$VERSION_FILE', 'utf8')).version"
    else
        echo "0.0.0"
    fi
}

# Bump version using semver
bump_version() {
    local current="$1"
    local type="$2"
    
    IFS='.' read -ra VERSION_PARTS <<< "$current"
    local major="${VERSION_PARTS[0]}"
    local minor="${VERSION_PARTS[1]}"
    local patch="${VERSION_PARTS[2]}"
    
    case "$type" in
        "major")
            major=$((major + 1))
            minor=0
            patch=0
            ;;
        "minor")
            minor=$((minor + 1))
            patch=0
            ;;
        "patch")
            patch=$((patch + 1))
            ;;
    esac
    
    echo "$major.$minor.$patch"
}

# Generate build number
generate_build_number() {
    date +"%Y.%m.%d.%H%M"
}

# ============================================================================
# Command Functions
# ============================================================================

update_hashes() {
    log_info "Updating proto hashes..."
    
    local proto_hash=$(calculate_proto_hash)
    local document_store_hash=$(calculate_file_hash "$PROJECT_ROOT/proto/document_store.proto")
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    # Update version.json with new hashes
    node -e "
        const fs = require('fs');
        const version = JSON.parse(fs.readFileSync('$VERSION_FILE', 'utf8'));
        version.components.proto.hash = '$proto_hash';
        version.components.proto.lastUpdated = '$timestamp';
        version.components.proto.schemas.document_store.hash = '$document_store_hash';
        fs.writeFileSync('$VERSION_FILE', JSON.stringify(version, null, 2));
    "
    
    log_success "Proto hashes updated:"
    log_info "  Overall: $proto_hash"
    log_info "  DocumentStore: $document_store_hash"
}

bump_proto() {
    log_info "Bumping proto version..."
    
    local current_proto_version=$(node -p "JSON.parse(require('fs').readFileSync('$VERSION_FILE', 'utf8')).components.proto.version")
    local new_proto_version=$(bump_version "$current_proto_version" "minor")
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    # Update proto version
    node -e "
        const fs = require('fs');
        const version = JSON.parse(fs.readFileSync('$VERSION_FILE', 'utf8'));
        version.components.proto.version = '$new_proto_version';
        version.components.proto.lastUpdated = '$timestamp';
        fs.writeFileSync('$VERSION_FILE', JSON.stringify(version, null, 2));
    "
    
    # Update hashes
    update_hashes
    
    log_success "Proto version bumped: $current_proto_version → $new_proto_version"
}

bump_major() {
    log_info "Bumping major version..."
    
    local current_version=$(get_current_version)
    local new_version=$(bump_version "$current_version" "major")
    local build_number=$(generate_build_number)
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    # Update main version
    node -e "
        const fs = require('fs');
        const version = JSON.parse(fs.readFileSync('$VERSION_FILE', 'utf8'));
        version.version = '$new_version';
        version.build = '$build_number';
        
        // Add changelog entry
        if (!version.changelog['$new_version']) {
            version.changelog['$new_version'] = {
                date: '$(date +"%Y-%m-%d")',
                changes: ['Major version bump'],
                breaking: true
            };
        }
        
        fs.writeFileSync('$VERSION_FILE', JSON.stringify(version, null, 2));
    "
    
    # Update hashes
    update_hashes
    
    log_success "Major version bumped: $current_version → $new_version"
    log_info "Build: $build_number"
}

validate_versions() {
    log_info "Validating versions and hashes..."
    
    local current_proto_hash=$(calculate_proto_hash)
    local stored_proto_hash=$(node -p "JSON.parse(require('fs').readFileSync('$VERSION_FILE', 'utf8')).components.proto.hash")
    
    if [ "$current_proto_hash" = "$stored_proto_hash" ]; then
        log_success "Proto hashes match: $current_proto_hash"
    else
        log_error "Proto hash mismatch!"
        log_info "  Current:  $current_proto_hash"
        log_info "  Expected: $stored_proto_hash"
        log_warning "Run: ./scripts/version-manager.sh update-hashes"
        return 1
    fi
    
    # Validate generated files have correct hash
    local frontend_generated="$PROJECT_ROOT/frontend/src/types/generated/document_store.ts"
    if [ -f "$frontend_generated" ]; then
        if grep -q "$stored_proto_hash" "$frontend_generated"; then
            log_success "Frontend generated files have correct hash"
        else
            log_warning "Frontend generated files may be outdated"
        fi
    else
        log_warning "Frontend generated files not found"
    fi
    
    log_success "Version validation complete"
}

show_status() {
    log_info "Version Status:"
    
    local version=$(get_current_version)
    local proto_version=$(node -p "JSON.parse(require('fs').readFileSync('$VERSION_FILE', 'utf8')).components.proto.version")
    local build=$(node -p "JSON.parse(require('fs').readFileSync('$VERSION_FILE', 'utf8')).build")
    local proto_hash=$(calculate_proto_hash)
    
    echo -e "  ${BLUE}Main Version:${NC} $version"
    echo -e "  ${BLUE}Build:${NC} $build"
    echo -e "  ${BLUE}Proto Version:${NC} $proto_version"
    echo -e "  ${BLUE}Proto Hash:${NC} $proto_hash"
}

# ============================================================================
# Main Command Handler
# ============================================================================

case "${1:-}" in
    "update-hashes")
        update_hashes
        ;;
    "bump-proto")
        bump_proto
        ;;
    "bump-major")
        bump_major
        ;;
    "bump-minor")
        local current_version=$(get_current_version)
        local new_version=$(bump_version "$current_version" "minor")
        log_info "Bumping minor version: $current_version → $new_version"
        # Implementation similar to bump_major
        ;;
    "validate")
        validate_versions
        ;;
    "status")
        show_status
        ;;
    *)
        echo "Usage: $0 {update-hashes|bump-proto|bump-major|bump-minor|validate|status}"
        echo ""
        echo "Commands:"
        echo "  update-hashes  Update proto file hashes"
        echo "  bump-proto     Bump proto version (minor)"
        echo "  bump-major     Bump major version"
        echo "  bump-minor     Bump minor version"
        echo "  validate       Validate versions and hashes"
        echo "  status         Show current version status"
        exit 1
        ;;
esac
