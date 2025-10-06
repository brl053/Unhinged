# 📝 LLM Comment Templates - Unhinged Platform

> **Purpose**: Template library for consistent LLM commenting across all languages
> **Usage**: Copy-paste templates and customize for your specific code elements
> **Integration**: Works with existing IDEs and linting tools

## 🎯 Template Categories

### Service Classes

#### TypeScript Service
```typescript
/**
 * @llm-type service
 * @llm-legend [Business purpose - what this service accomplishes for users]
 * @llm-key [Technical implementation - algorithms, patterns, performance considerations]
 * @llm-map [Architectural relationships - dependencies, integrations, data flow]
 * @llm-axiom [Fundamental constraints that must always hold true]
 * @llm-contract [API guarantees, error handling, behavioral contracts]
 * @llm-token [domain-term]: [definition of project-specific vocabulary]
 */
class ServiceTemplate {
    /**
     * @llm-type function
     * @llm-legend [What this function accomplishes in business terms]
     * @llm-key [How it works technically - algorithm, approach]
     * @llm-map [Where it fits - what calls it, what it calls]
     * @llm-contract [Input/output contracts, error conditions]
     */
    async processData(input: DataType): Promise<ResultType> {
        // Implementation
    }
}
```

#### Python Service
```python
class ServiceTemplate:
    """
    @llm-type service
    @llm-legend [Business purpose and user impact]
    @llm-key [Technical implementation details]
    @llm-map [System integration points and dependencies]
    @llm-axiom [Non-negotiable design principles]
    @llm-contract [API guarantees and error handling]
    @llm-token [domain-term]: [definition]
    """
    
    def process_data(self, input_data: DataType) -> ResultType:
        """
        @llm-type function
        @llm-legend [Business function description]
        @llm-key [Technical implementation approach]
        @llm-map [Integration context and relationships]
        @llm-contract [Input validation, output guarantees, exceptions]
        """
        pass
```

#### Kotlin Service
```kotlin
/**
 * @llm-type service
 * @llm-legend [Business purpose and system role]
 * @llm-key [Technical implementation using Kotlin/Spring patterns]
 * @llm-map [Clean architecture layer and dependencies]
 * @llm-axiom [Design principles that must be maintained]
 * @llm-contract [API contracts and exception handling]
 * @llm-token [domain-term]: [definition]
 */
@Service
class ServiceTemplate {
    
    /**
     * @llm-type function
     * @llm-legend [Business operation description]
     * @llm-key [Implementation details and patterns used]
     * @llm-map [Called by controllers, calls repositories]
     * @llm-contract [Input validation, return guarantees, exceptions thrown]
     */
    suspend fun processData(input: DataType): ResultType {
        // Implementation
    }
}
```

### Repository Classes

#### Kotlin Repository
```kotlin
/**
 * @llm-type repository
 * @llm-legend [Data access purpose - what business data this manages]
 * @llm-key [Persistence technology - JPA, caching, transaction handling]
 * @llm-map [Part of infrastructure layer, used by application services]
 * @llm-axiom [All operations must be transactional and consistent]
 * @llm-contract [Data integrity guarantees, exception handling for constraints]
 * @llm-token [entity-name]: [business concept this entity represents]
 */
@Repository
interface EntityRepository : JpaRepository<Entity, UUID> {
    
    /**
     * @llm-type function
     * @llm-legend [Business query purpose]
     * @llm-key [Query implementation - JPQL, native SQL, or method query]
     * @llm-map [Called by service layer for specific business operations]
     * @llm-contract [Returns filtered results, handles empty cases]
     */
    fun findByBusinessCriteria(criteria: String): List<Entity>
}
```

### API Endpoints

#### TypeScript Controller
```typescript
/**
 * @llm-type endpoint
 * @llm-legend [API purpose - what business operation this enables]
 * @llm-key [HTTP handling, validation, response formatting]
 * @llm-map [Entry point for frontend, calls service layer]
 * @llm-axiom [All endpoints must validate input and handle errors gracefully]
 * @llm-contract [HTTP status codes, response format, error handling]
 * @llm-token [api-resource]: [RESTful resource this endpoint manages]
 */
@Controller('/api/resource')
class ResourceController {
    
    /**
     * @llm-type function
     * @llm-legend [Specific API operation for users]
     * @llm-key [Request processing, validation, response construction]
     * @llm-map [Receives HTTP requests, delegates to service, returns JSON]
     * @llm-contract [200 for success, 400 for validation, 500 for errors]
     */
    @Post('/')
    async createResource(@Body() data: CreateResourceDto): Promise<ResourceDto> {
        // Implementation
    }
}
```

### Configuration Files

#### YAML Configuration
```yaml
# @llm-type config
# @llm-legend [Configuration purpose - what system behavior this controls]
# @llm-key [Configuration structure, environment variables, defaults]
# @llm-map [Used by services, affects system behavior, deployment specific]
# @llm-axiom [Configuration must be environment-specific and secure]
# @llm-contract [Required fields, validation rules, fallback behavior]
# @llm-token [config-section]: [what this configuration section controls]

service-name:
  # @llm-type config
  # @llm-legend [Specific service configuration purpose]
  # @llm-key [Configuration options and their effects]
  # @llm-map [Consumed by service on startup, affects runtime behavior]
  # @llm-contract [Required vs optional settings, validation rules]
  port: 8080
  database:
    url: ${DATABASE_URL}
    pool-size: 10
```

#### Shell Script
```bash
#!/bin/bash
# @llm-type script
# @llm-legend [Script purpose - what operational task this automates]
# @llm-key [Implementation approach, tools used, error handling]
# @llm-map [Called by make targets, CI/CD, or manual operations]
# @llm-axiom [Script must be idempotent and handle partial failures]
# @llm-contract [Exit codes, output format, side effects]
# @llm-token [operation-name]: [specific operational concept]

function setup_environment() {
    # @llm-type function
    # @llm-legend [Specific setup operation]
    # @llm-key [Steps performed, validation checks]
    # @llm-map [Called during initialization, prepares system state]
    # @llm-contract [Success/failure indication, cleanup on failure]
    echo "Setting up environment..."
}
```

## 🔄 Migration Examples

### Before/After: TypeScript Function

#### Before (Standard JSDoc)
```typescript
/**
 * Processes image upload and analysis
 * @param imageFile The uploaded image file
 * @param options Processing options
 * @returns Promise with analysis results
 */
async function processImage(imageFile: File, options: ProcessingOptions): Promise<ImageAnalysis> {
    // Implementation
}
```

#### After (LLM Standard)
```typescript
/**
 * @llm-type function
 * @llm-legend Enables users to upload images and receive AI-powered analysis and descriptions
 * @llm-key Validates image format, uploads to S3, queues for vision-ai processing, caches results
 * @llm-map Entry point for image pipeline, calls VisionService, integrates with storage layer
 * @llm-axiom Processing must be non-blocking and provide progress feedback to users
 * @llm-contract Accepts common image formats (jpg, png, webp), returns structured analysis or throws ProcessingError
 * @llm-token vision-pipeline: end-to-end image analysis workflow from upload to result delivery
 * 
 * Processes image upload and analysis
 * @param imageFile The uploaded image file
 * @param options Processing options
 * @returns Promise with analysis results
 */
async function processImage(imageFile: File, options: ProcessingOptions): Promise<ImageAnalysis> {
    // Implementation
}
```

### Before/After: Python Class

#### Before (Standard Docstring)
```python
class VisionProcessor:
    """Handles image processing using AI models."""
    
    def analyze(self, image_data):
        """Analyzes image and returns description."""
        pass
```

#### After (LLM Standard)
```python
class VisionProcessor:
    """
    @llm-type service
    @llm-legend Provides AI-powered image analysis using BLIP vision model for user-uploaded content
    @llm-key Loads BLIP model on startup, processes images via Flask endpoints, implements caching
    @llm-map Receives requests from backend API, returns JSON analysis, integrates with model storage
    @llm-axiom Model must be loaded and ready before accepting any processing requests
    @llm-contract Returns structured analysis JSON or appropriate HTTP error codes
    @llm-token BLIP: Bootstrapping Language-Image Pre-training model for image captioning
    
    Handles image processing using AI models.
    """
    
    def analyze(self, image_data: bytes) -> Dict[str, Any]:
        """
        @llm-type function
        @llm-legend Generates natural language descriptions of image content for users
        @llm-key Preprocesses image tensor, runs BLIP inference, post-processes text output
        @llm-map Core processing function called by Flask /analyze endpoint
        @llm-contract Validates image format, returns analysis dict with confidence scores
        
        Analyzes image and returns description.
        """
        pass
```

### Before/After: Kotlin Repository

#### Before (Standard KDoc)
```kotlin
/**
 * Repository for managing image analysis data
 */
@Repository
interface ImageAnalysisRepository : JpaRepository<ImageAnalysis, UUID> {
    fun findByUserId(userId: UUID): List<ImageAnalysis>
}
```

#### After (LLM Standard)
```kotlin
/**
 * @llm-type repository
 * @llm-legend Manages persistent storage of image analysis results and user associations
 * @llm-key Uses JPA with PostgreSQL, implements query optimization, handles large result sets
 * @llm-map Part of infrastructure layer, called by ImageAnalysisService, integrates with caching
 * @llm-axiom All database operations must maintain referential integrity and be transactional
 * @llm-contract Provides ACID guarantees, throws DataAccessException for constraint violations
 * @llm-token analysis-result: structured output from vision processing with metadata
 * 
 * Repository for managing image analysis data
 */
@Repository
interface ImageAnalysisRepository : JpaRepository<ImageAnalysis, UUID> {
    
    /**
     * @llm-type function
     * @llm-legend Retrieves all image analysis history for a specific user
     * @llm-key Implements indexed query on user_id, supports pagination for large datasets
     * @llm-map Called by service layer for user dashboard and history features
     * @llm-contract Returns ordered list by creation date, empty list if no results
     */
    fun findByUserId(userId: UUID): List<ImageAnalysis>
}
```

## 🎨 IDE Integration

### VSCode Snippets
```json
{
    "LLM Service Comment": {
        "prefix": "llm-service",
        "body": [
            "/**",
            " * @llm-type service",
            " * @llm-legend ${1:Business purpose and user impact}",
            " * @llm-key ${2:Technical implementation details}",
            " * @llm-map ${3:Architectural relationships and dependencies}",
            " * @llm-axiom ${4:Fundamental design principles}",
            " * @llm-contract ${5:API guarantees and error handling}",
            " * @llm-token ${6:domain-term}: ${7:definition}",
            " */"
        ],
        "description": "LLM comment template for service classes"
    },
    "LLM Function Comment": {
        "prefix": "llm-function",
        "body": [
            "/**",
            " * @llm-type function",
            " * @llm-legend ${1:Business function description}",
            " * @llm-key ${2:Technical implementation approach}",
            " * @llm-map ${3:Integration context and relationships}",
            " * @llm-contract ${4:Input/output contracts and error conditions}",
            " */"
        ],
        "description": "LLM comment template for functions"
    }
}
```

### IntelliJ Live Templates
```xml
<template name="llm-service" value="/**&#10; * @llm-type service&#10; * @llm-legend $LEGEND$&#10; * @llm-key $KEY$&#10; * @llm-map $MAP$&#10; * @llm-axiom $AXIOM$&#10; * @llm-contract $CONTRACT$&#10; * @llm-token $TOKEN$: $DEFINITION$&#10; */" description="LLM service comment" toReformat="false" toShortenFQNames="true">
  <variable name="LEGEND" expression="" defaultValue="" alwaysStopAt="true" />
  <variable name="KEY" expression="" defaultValue="" alwaysStopAt="true" />
  <variable name="MAP" expression="" defaultValue="" alwaysStopAt="true" />
  <variable name="AXIOM" expression="" defaultValue="" alwaysStopAt="true" />
  <variable name="CONTRACT" expression="" defaultValue="" alwaysStopAt="true" />
  <variable name="TOKEN" expression="" defaultValue="" alwaysStopAt="true" />
  <variable name="DEFINITION" expression="" defaultValue="" alwaysStopAt="true" />
  <context>
    <option name="KOTLIN" value="true" />
    <option name="JAVA" value="true" />
  </context>
</template>
```

## 📊 Quality Levels

### Minimal (Required)
- `@llm-type` + `@llm-legend`
- Basic business context

### Standard (Recommended)  
- `@llm-type` + `@llm-legend` + `@llm-key` + `@llm-map`
- Technical and architectural context

### Comprehensive (Ideal)
- All tags used appropriately
- Rich context for LLM understanding
- Domain vocabulary documented

---

**Usage**: Copy appropriate template, customize for your code element, and integrate with existing documentation practices.
