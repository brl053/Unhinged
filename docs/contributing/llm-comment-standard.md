# 🤖 LLM Comment Standard - Unhinged Platform

> **Purpose**: Polyglot commenting standard for machine-readable documentation across all programming languages
> **Philosophy**: Extends the "Legend/Key/Map" approach to code-level documentation
> **Integration**: Seamlessly works with existing tooling while enhancing LLM comprehension

## 🎯 Overview

The Unhinged LLM Comment Standard creates consistent, machine-readable documentation that helps both human developers and AI assistants understand code architecture, business context, and design decisions without breaking existing tooling.

### Core Principles
1. **Language-Agnostic**: Uses existing comment conventions (JSDoc, docstrings, KDoc)
2. **Tool-Compatible**: Works with current linters and IDEs
3. **Legend/Key/Map**: Structured information hierarchy
4. **Machine-Readable**: Parseable by automation systems
5. **Human-Friendly**: Enhances rather than clutters code

## 📋 Standard Tags

### Semantic Metadata System

#### `@llm-type`
**Purpose**: Classify the element type for architectural understanding
**Values**: `function`, `class`, `service`, `config`, `type-definition`, `constant`, `interface`, `endpoint`, `repository`, `entity`

#### `@llm-legend` 
**Purpose**: High-level business purpose and context ("what this accomplishes")
**Content**: Business value, user impact, system role

#### `@llm-key`
**Purpose**: Technical implementation details ("how this works")
**Content**: Algorithms, patterns, technical decisions, performance considerations

#### `@llm-map`
**Purpose**: Architectural relationships ("how this fits in the system")
**Content**: Dependencies, integrations, data flow, service boundaries

#### `@llm-axiom`
**Purpose**: Fundamental design principles that must hold true
**Content**: Invariants, constraints, non-negotiable requirements

#### `@llm-contract`
**Purpose**: API guarantees, error handling, and behavioral contracts
**Content**: Input/output contracts, error conditions, side effects

#### `@llm-token`
**Purpose**: Project-specific vocabulary and domain terminology
**Content**: Domain concepts, business terms, technical jargon definitions

## 🔧 Language-Specific Syntax

### TypeScript/JavaScript (JSDoc Extension)
```typescript
/**
 * @llm-type service
 * @llm-legend Orchestrates image processing pipeline for user-uploaded content
 * @llm-key Uses BLIP model for captioning, implements retry logic with exponential backoff
 * @llm-map Integrates with vision-ai service (port 8001) and backend storage layer
 * @llm-axiom All image processing must be non-blocking and provide progress feedback
 * @llm-contract Returns structured analysis or throws VisionProcessingError
 * @llm-token vision-pipeline: end-to-end image analysis workflow
 */
class VisionProcessingService {
    /**
     * @llm-type function
     * @llm-legend Analyzes uploaded image and generates descriptive caption
     * @llm-key Validates image format, calls BLIP model, handles timeout scenarios
     * @llm-map Calls POST /analyze on vision-ai service, stores result in Redis cache
     * @llm-contract Throws ValidationError for invalid images, TimeoutError for slow processing
     */
    async analyzeImage(imageBuffer: Buffer): Promise<ImageAnalysis> {
        // Implementation
    }
}
```

### Python (Docstring Extension)
```python
class VisionAIService:
    """
    @llm-type service
    @llm-legend Provides AI-powered image analysis using BLIP vision model
    @llm-key Loads model on startup, processes images via Flask endpoints
    @llm-map Receives requests from backend, returns JSON analysis results
    @llm-axiom Model must be loaded before accepting requests
    @llm-contract Returns 200 with analysis JSON or 400/500 for errors
    @llm-token BLIP: Bootstrapping Language-Image Pre-training model
    """
    
    def analyze_image(self, image_data: bytes) -> Dict[str, Any]:
        """
        @llm-type function
        @llm-legend Generates natural language description of image content
        @llm-key Preprocesses image, runs BLIP inference, post-processes output
        @llm-map Core processing function called by Flask /analyze endpoint
        @llm-contract Validates image format, returns structured analysis dict
        """
        pass
```

### Kotlin (KDoc Extension)
```kotlin
/**
 * @llm-type repository
 * @llm-legend Manages persistent storage and retrieval of image analysis results
 * @llm-key Uses JPA with PostgreSQL, implements caching with Redis
 * @llm-map Part of infrastructure layer, called by application services
 * @llm-axiom All database operations must be transactional
 * @llm-contract Throws DataAccessException for persistence failures
 * @llm-token analysis-result: structured output from vision processing
 */
@Repository
class ImageAnalysisRepository {
    
    /**
     * @llm-type function
     * @llm-legend Persists image analysis results with metadata
     * @llm-key Generates UUID, stores with timestamp, updates cache
     * @llm-map Called by ImageAnalysisService after successful processing
     * @llm-contract Returns saved entity or throws on constraint violations
     */
    fun save(analysis: ImageAnalysis): ImageAnalysis {
        // Implementation
    }
}
```

### YAML Configuration
```yaml
# @llm-type config
# @llm-legend Docker service configuration for vision AI processing
# @llm-key Defines container, ports, volumes, and environment variables
# @llm-map Part of docker-compose.yml, connects to backend and database services
# @llm-axiom Vision service must be accessible on port 8001
# @llm-contract Service must respond to health checks within 30 seconds
# @llm-token vision-models: Docker volume for persistent model storage

vision-ai:
  build: ./services/vision-ai
  ports:
    - "8001:8001"
  volumes:
    - vision-models:/app/models
```

### Shell Scripts
```bash
#!/bin/bash
# @llm-type script
# @llm-legend Automated setup script for development environment
# @llm-key Installs dependencies, configures services, validates setup
# @llm-map Entry point for new developers, called by make setup
# @llm-axiom Script must be idempotent and handle partial failures gracefully
# @llm-contract Exits with 0 on success, non-zero on any failure
# @llm-token dev-env: complete development environment setup

setup_vision_service() {
    # @llm-type function
    # @llm-legend Downloads and configures BLIP model for vision processing
    # @llm-key Checks model cache, downloads if missing, validates integrity
    # @llm-map Called during setup phase, prepares vision-ai service
    # @llm-contract Creates model directory and downloads required files
    echo "Setting up vision service..."
}
```

## 🎨 Legend/Key/Map Integration

### Legend (What)
- **Business Context**: Why this code exists
- **User Impact**: How it affects end users
- **System Role**: Purpose within the architecture

### Key (How)
- **Implementation Details**: Technical approach
- **Algorithms**: Specific techniques used
- **Performance**: Optimization considerations

### Map (Where)
- **Dependencies**: What this code relies on
- **Integrations**: How it connects to other components
- **Data Flow**: Information movement patterns

## 📊 Comment Quality Levels

### Level 1: Basic (Required)
```typescript
/**
 * @llm-type function
 * @llm-legend Processes user authentication
 */
```

### Level 2: Standard (Recommended)
```typescript
/**
 * @llm-type function
 * @llm-legend Validates user credentials and creates session
 * @llm-key Uses bcrypt for password hashing, JWT for session tokens
 * @llm-map Integrates with user repository and session store
 */
```

### Level 3: Comprehensive (Ideal)
```typescript
/**
 * @llm-type function
 * @llm-legend Authenticates users and establishes secure sessions for platform access
 * @llm-key Validates credentials with bcrypt, generates JWT tokens, implements rate limiting
 * @llm-map Called by auth middleware, uses UserRepository, stores sessions in Redis
 * @llm-axiom Authentication must complete within 500ms to maintain UX standards
 * @llm-contract Returns AuthResult with token or throws AuthenticationError
 * @llm-token auth-session: secure user session with JWT token and metadata
 */
```

## 🔄 Migration Strategy

### Phase 1: Critical Files (Week 1)
- Main service classes
- Core API endpoints
- Key configuration files
- Primary data models

### Phase 2: Infrastructure (Week 2)
- Repository classes
- Utility functions
- Middleware components
- Database migrations

### Phase 3: Complete Coverage (Week 3-4)
- All remaining functions
- Test files
- Build scripts
- Documentation updates

### Migration Template
```typescript
// BEFORE (Standard JSDoc)
/**
 * Processes image upload
 * @param file The uploaded file
 * @returns Processing result
 */

// AFTER (LLM Standard)
/**
 * @llm-type function
 * @llm-legend Handles user image uploads for AI-powered analysis
 * @llm-key Validates file format, stores in S3, queues for processing
 * @llm-map Entry point for image pipeline, triggers vision-ai service
 * @llm-contract Accepts common image formats, returns upload confirmation
 * 
 * Processes image upload
 * @param file The uploaded file
 * @returns Processing result
 */
```

## 🛠️ Tooling Integration

### IDE Support
- **VSCode**: Snippets for common patterns
- **IntelliJ**: Live templates for Kotlin/Java
- **Vim/Emacs**: Custom snippets

### Linter Compatibility
- **ESLint**: Custom rules for @llm-* tag validation
- **ktlint**: Kotlin-specific comment formatting
- **Pylint**: Python docstring extensions

### Documentation Generation
- **Make Integration**: `make docs-comments` extracts architectural docs
- **Validation**: `make docs-validate` checks comment consistency
- **Auto-Update**: Integrated with existing `make docs-update` workflow

## 📈 Success Metrics

### Quantitative
- **Coverage**: Percentage of functions with LLM comments
- **Consistency**: Adherence to standard format
- **Completeness**: Average tags per comment

### Qualitative
- **LLM Comprehension**: AI assistant understanding improvement
- **Developer Adoption**: Team usage and feedback
- **Documentation Quality**: Generated architectural docs usefulness

---

**Next Steps**: Implement parser system and integrate with existing documentation automation to create a seamless developer experience.
