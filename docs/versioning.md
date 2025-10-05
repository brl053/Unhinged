# Versioning System

## Overview

Unhinged uses a comprehensive semantic versioning system with hash validation to ensure generated files match their source schemas. This prevents version mismatches and ensures build reproducibility.

## Version Structure

```json
{
  "version": "1.0.0",           // Main semver version
  "build": "2025.01.04.001",    // Build timestamp
  "components": {
    "proto": {
      "version": "1.0.0",       // Proto schema version
      "hash": "c3c5be7c...",     // SHA256 of all proto files
      "schemas": {
        "document_store": {
          "version": "1.0.0",   // Individual schema version
          "hash": "f9cbcea3..."  // SHA256 of specific proto
        }
      }
    }
  }
}
```

## Hash Validation

Every generated file includes a version header:

```typescript
// ============================================================================
// GENERATED FILE - DO NOT EDIT
// ============================================================================
// Proto Version: 1.0.0
// Proto Hash: c3c5be7c604bfa726736da0f50b5ed24efc07d59c58207c9aeb5737ae1f8399c
// Build: 2025.01.04.001
// Generated: 2025-10-05T05:31:23Z
// ============================================================================
```

## Commands

### Version Management
```bash
# Show current version status
npm run version:status

# Update proto hashes (after editing .proto files)
npm run version:update-hashes

# Bump proto version (minor increment)
npm run version:bump-proto

# Bump major version
npm run version:bump-major

# Validate versions and hashes
npm run version:validate
```

### Build and Validation
```bash
# Generate protobuf code with version headers
npm run build:proto

# Validate generated files exist and are up-to-date
npm run validate:generated

# Clean generated files
npm run clean:generated
```

## Workflow

### 1. Modify Proto Schema
```bash
# Edit proto/document_store.proto
vim proto/document_store.proto
```

### 2. Update Version
```bash
# Update hashes to reflect changes
npm run version:update-hashes

# Or bump proto version for breaking changes
npm run version:bump-proto
```

### 3. Regenerate Code
```bash
# Generate with new version headers
npm run build:proto
```

### 4. Validate
```bash
# Ensure everything is consistent
npm run version:validate
npm run validate:generated
```

## Version Policies

### Proto Schema Versioning
- **Patch (1.0.1)**: Bug fixes, documentation
- **Minor (1.1.0)**: New fields, backward compatible
- **Major (2.0.0)**: Breaking changes, field removal

### Component Versioning
- **Frontend Components**: Independent semver
- **Backend Services**: Independent semver  
- **Proto Schemas**: Linked to main version

### Hash Validation
- **SHA256** of proto file contents
- **Automatic updates** during build
- **Validation** before dev/test/build
- **Mismatch detection** prevents stale code

## CI/CD Integration

```yaml
- name: Validate Versions
  run: |
    npm run version:validate
    npm run validate:generated

- name: Generate Code
  run: |
    npm run build:proto
    
- name: Verify Generation
  run: |
    npm run validate:generated
```

## Benefits

✅ **Version Consistency**: Hash validation ensures generated code matches schemas  
✅ **Build Reproducibility**: Same proto = same generated code  
✅ **Change Detection**: Automatic detection of schema modifications  
✅ **Developer Safety**: Prevents using outdated generated files  
✅ **Audit Trail**: Complete changelog and version history  

## Troubleshooting

### Hash Mismatch
```bash
# Problem: Generated files are outdated
npm run version:validate
# ❌ Proto hash mismatch!

# Solution: Regenerate files
npm run build:proto
```

### Missing Generated Files
```bash
# Problem: Files not found
npm run validate:generated
# ❌ Missing generated files

# Solution: Generate files
npm run build:proto
```

### Version Conflicts
```bash
# Problem: Multiple developers, version conflicts
git pull
npm run version:update-hashes
npm run build:proto
```

## Advanced Usage

### Custom Version Bumps
```bash
# Manual version editing
vim version.json

# Update hashes after manual changes
npm run version:update-hashes
```

### Component-Specific Versioning
```bash
# Bump specific component versions
./scripts/version-manager.sh bump-frontend
./scripts/version-manager.sh bump-backend
```

### Changelog Management
Version changes automatically update the changelog in `version.json`:

```json
{
  "changelog": {
    "1.1.0": {
      "date": "2025-01-04",
      "changes": [
        "Added session context queries",
        "Improved tag management"
      ],
      "breaking": false
    }
  }
}
```

This versioning system ensures that generated protobuf code is always consistent with its source schemas, preventing runtime errors and build issues.
