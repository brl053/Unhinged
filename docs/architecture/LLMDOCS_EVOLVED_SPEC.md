# LlmDocs Evolved Specification - Single Lean Format

## Overview

LlmDocs evolved format provides a deterministic, lean, and structured approach to code documentation for AI comprehension. This specification eliminates redundancy, improves consistency, and provides maximum semantic meaning with minimum overhead.

## Core Principles

### 1. **Determinism First**
- Each tag has a single, well-defined purpose
- No overlapping responsibilities between tags
- Predictable structure across all files

### 2. **Lean by Design**
- Minimum viable documentation for maximum AI comprehension
- Eliminate redundant information across tags
- Focus on unique, essential information per tag

### 3. **Hierarchical Type System**
- Clear taxonomy with inheritance relationships
- Consistent naming conventions
- Predictable categorization

## Tag Specification

### Required Tags (All Files)

#### `@llm-type <category>.<subcategory>`
**Purpose**: Hierarchical classification of the code element
**Format**: `category.subcategory` (dot-separated hierarchy)
**Examples**:
- `service.api` - API service
- `component.primitive` - UI primitive component  
- `model.entity` - Data entity model
- `util.parser` - Parsing utility
- `config.build` - Build configuration

#### `@llm-purpose <one-line-description>`
**Purpose**: Single sentence describing WHAT this does (not how)
**Format**: Imperative verb + object + context
**Length**: 40-80 characters
**Examples**:
- `Validates component specifications against schema`
- `Manages GTK4 widget lifecycle and events`
- `Parses YAML configuration files`

### Optional Tags (Context-Dependent)

#### `@llm-contract <interface-definition>`
**Purpose**: Input/output contract for functions, APIs, and services
**When**: Required for public APIs, services, and exported functions
**Format**: `Input -> Output` or `Accepts X, Returns Y`
**Examples**:
- `ComponentSpec -> ValidationResult`
- `HTTP Request -> JSON Response`
- `YAML Path -> Config Object`

#### `@llm-axiom <constraint-or-rule>`
**Purpose**: Non-negotiable constraint or business rule
**When**: Required for critical business logic and constraints
**Format**: Must/Should statement
**Examples**:
- `All components must validate before generation`
- `CSS must be GTK4-compatible`
- `Tokens must follow semantic naming`

#### `@llm-deps <dependency-list>`
**Purpose**: Critical dependencies (not obvious from imports)
**When**: Required for complex dependency relationships
**Format**: Comma-separated list
**Examples**:
- `design-tokens, component-schema`
- `GTK4, Libadwaita`
- `PostgreSQL, Redis`

## Removed/Deprecated Tags

### Eliminated for Redundancy
- `@llm-legend` → Replaced by `@llm-purpose` (more focused)
- `@llm-key` → Information merged into `@llm-purpose`
- `@llm-map` → Architectural context inferred from type hierarchy
- `@llm-token` → Replaced by structured `@llm-type`
- `@llm-context` → Context inferred from file structure and type

## Type Taxonomy

### Service Types
- `service.api` - REST/gRPC API services
- `service.worker` - Background processing services
- `service.gateway` - API gateways and proxies
- `service.auth` - Authentication/authorization services

### Component Types  
- `component.primitive` - Atomic UI elements
- `component.container` - Layout/grouping components
- `component.complex` - Stateful/composed components
- `component.system` - Meta-components and frameworks

### Model Types
- `model.entity` - Domain entities
- `model.dto` - Data transfer objects
- `model.config` - Configuration models
- `model.schema` - Validation schemas

### Utility Types
- `util.parser` - Parsing utilities
- `util.validator` - Validation utilities
- `util.formatter` - Formatting utilities
- `util.converter` - Data conversion utilities

### Config Types
- `config.build` - Build system configuration
- `config.deploy` - Deployment configuration
- `config.env` - Environment configuration
- `config.app` - Application configuration

## Migration Guide

### From V1 to V2

1. **Replace `@llm-legend` with `@llm-purpose`**:
   ```diff
   - @llm-legend Component specification validator that ensures YAML specs conform to schema
   + @llm-purpose Validates component specifications against schema
   ```

2. **Consolidate type information**:
   ```diff
   - @llm-type service
   + @llm-type service.api
   ```

3. **Simplify contracts**:
   ```diff
   - @llm-contract Returns BuildModuleResult with success status, duration, and artifacts
   + @llm-contract ComponentSpec -> ValidationResult
   ```

4. **Remove redundant tags**:
   ```diff
   - @llm-key Validates YAML component specifications
   - @llm-map Central validation layer for component generation
   - @llm-token component-validator: YAML specification validation
   (All information captured in @llm-type and @llm-purpose)
   ```

## Validation Rules

### Required Validation
- All files must have `@llm-type` and `@llm-purpose`
- Type must follow hierarchical naming convention
- Purpose must be 40-80 characters
- No duplicate information across tags

### Quality Validation
- Purpose must use imperative verbs
- Contract must specify clear input/output
- Axioms must be testable constraints
- Dependencies must be non-obvious

## Benefits

### For AI Comprehension
- **Faster parsing**: Fewer tags to process
- **Better context**: Hierarchical types provide clear categorization
- **Reduced noise**: Eliminated redundant information
- **Predictable structure**: Consistent format across all files

### For Developers
- **Less writing**: Fewer required tags
- **Clear guidelines**: Unambiguous tag purposes
- **Better maintenance**: Less duplication to keep in sync
- **Focused documentation**: Each tag has unique value

## Implementation

### Phase 1: Schema Update
- Update tag parsing patterns
- Implement hierarchical type validation
- Create migration scripts

### Phase 2: Codebase Migration
- Migrate existing LlmDocs to V2 format
- Validate all files pass new schema
- Update documentation generation

### Phase 3: Tooling Enhancement
- Update extraction tools
- Enhance validation rules
- Improve error messages

## Example

### Before (V1)
```python
"""
@llm-type service
@llm-legend Component specification validator that ensures YAML component specs conform to meta-schema
@llm-key Validates component specifications against schema with comprehensive error reporting
@llm-map Central validation layer in component generation pipeline
@llm-axiom All component specifications must validate before generation
@llm-contract Returns ValidationResult with errors, warnings, and success status
@llm-token component-validator: YAML specification validation with schema compliance
"""
```

### After (V2)
```python
"""
@llm-type util.validator
@llm-purpose Validates component specifications against schema
@llm-contract ComponentSpec -> ValidationResult
@llm-axiom All components must validate before generation
"""
```

**Result**: 85% reduction in documentation size while maintaining full semantic meaning.
