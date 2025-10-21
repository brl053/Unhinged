# 🗺️ Architectural Overview - Auto-Generated

> **Purpose**: System architecture extracted from code comments
> **Source**: Auto-generated from @llm-map and @llm-type comments
> **Last Updated**: 2025-10-20 19:15:02

## Config Components

### vision-ai
**File**: `docker-compose.yml`
**Language**: yaml
**Purpose**: Docker service configuration for AI-powered image analysis microservice
**Architecture**: Part of microservices architecture, connects backend to vision processing capabilities
**Implementation**: Defines Python container with BLIP model, Flask HTTP server, and persistent model storage

### unknown
**File**: `build/modules/registry_builder.py`
**Language**: python
**Purpose**: Global registry of static HTML files for browser navigation *
**Architecture**: Used by index.html and navigation components for file discovery *
**Implementation**: Auto-generated from filesystem scan, provides metadata for each HTML file *

### PersistenceConfiguration
**File**: `platforms/persistence/src/main/kotlin/com/unhinged/persistence/config/ConfigurationModels.kt`
**Language**: kotlin
**Purpose**: Main persistence platform configuration loaded from YAML
**Architecture**: Central configuration that drives all persistence platform behavior and routing decisions
**Implementation**: Root configuration object containing all platform settings and technology definitions

### unknown
**File**: `generated/static_html/registry.js`
**Language**: typescript
**Purpose**: Global registry of static HTML files for browser navigation
**Architecture**: Used by index.html and navigation components for file discovery
**Implementation**: Auto-generated from filesystem scan, provides metadata for each HTML file

### unknown
**File**: `generated/static_html/registry.js`
**Language**: typescript
**Purpose**: Hierarchical file structure for table-of-contents navigation
**Architecture**: Used by table-of-contents.html for dynamic file structure display
**Implementation**: Auto-generated directory tree with file metadata for browser navigation

## Service Components

### unknown
**File**: `build/llm_integration.py`
**Language**: python
**Purpose**: LLM integration for enhanced build system with context generation and error explanation
**Architecture**: LLM integration layer that connects build system with existing documentation system for enhanced developer experience
**Implementation**: Provides AI-powered build assistance, error explanation, and context generation for developer onboarding

### unknown
**File**: `build/cli.py`
**Language**: python
**Purpose**: Enhanced CLI interface for the Unhinged build system
**Architecture**: CLI layer that wraps the build orchestrator with enhanced user experience and developer tools
**Implementation**: Provides developer-friendly command-line interface with progress indicators, build status, and LLM integration

### unknown
**File**: `build/test_enhanced_system.py`
**Language**: python
**Purpose**: Test suite for the enhanced build system
**Architecture**: Test suite that validates all components of the enhanced build system
**Implementation**: Provides comprehensive testing and validation of the enhanced build system features

### unknown
**File**: `build/orchestrator.py`
**Language**: python
**Purpose**: Enhanced build orchestrator for Unhinged polyglot monorepo
**Architecture**: Central build coordination system that integrates with existing Makefile and Docker Compose workflows
**Implementation**: Provides intelligent dependency tracking, parallel execution, caching, and multi-language build coordination

### unknown
**File**: `build/monitoring.py`
**Language**: python
**Purpose**: Build performance monitoring and metrics collection system
**Architecture**: Performance monitoring system that tracks build metrics and provides optimization recommendations
**Implementation**: Provides comprehensive build performance tracking, caching analytics, and optimization insights

### unknown
**File**: `build/developer_experience.py`
**Language**: python
**Purpose**: Developer experience enhancements for the enhanced build system
**Architecture**: Developer experience layer that makes the build system more accessible and productive for developers
**Implementation**: Provides developer-friendly features like progress indicators, quick commands, and better error messages

### unknown
**File**: `build/build.py`
**Language**: python
**Purpose**: Main entry point for the Unhinged build system (v1)
**Architecture**: Primary build system entry point with clean v1 interface
**Implementation**: Provides unified access to intelligent build orchestration with caching, parallelism, and AI assistance

### unknown
**File**: `build/modules/typescript_builder.py`
**Language**: python
**Purpose**: TypeScript/npm build module with webpack optimization and hot reloading
**Architecture**: TypeScript build module that integrates with npm/webpack build system and provides enhanced caching
**Implementation**: Provides optimized npm builds with webpack, hot module replacement, and intelligent caching

### unknown
**File**: `build/modules/python_builder.py`
**Language**: python
**Purpose**: Python build module with virtual environment management and dependency caching
**Architecture**: Python build module that integrates with pip/poetry build systems and provides enhanced caching
**Implementation**: Provides optimized Python builds with pip/poetry, virtual environments, and intelligent caching

### unknown
**File**: `build/modules/kotlin_builder.py`
**Language**: python
**Purpose**: Kotlin/Gradle build module with incremental compilation and caching
**Architecture**: Kotlin build module that integrates with Gradle build system and provides enhanced caching
**Implementation**: Provides optimized Gradle builds with parallel execution, incremental compilation, and intelligent caching

### unknown
**File**: `services/vision-ai/main.py`
**Language**: python
**Purpose**: Provides AI-powered image analysis using BLIP vision model for user-uploaded content
**Architecture**: Entry point for vision processing pipeline, integrates with backend via HTTP API
**Implementation**: Loads BLIP model on startup, serves Flask HTTP API on port 8001, implements health checks

## Build Components

### unknown
**File**: `build/generate-registry.py`
**Language**: python
**Purpose**: Simple script to generate static HTML registry for make start command
**Architecture**: Entry point for Makefile to generate registry before control plane startup
**Implementation**: Standalone script that calls registry builder without complex build system dependencies

### unknown
**File**: `build/port_fixer.py`
**Language**: python
**Purpose**: Port conflict detection and automatic resolution tool
**Architecture**: Build-time port management utility with auto-fix capabilities
**Implementation**: Standalone tool for analyzing and fixing port conflicts in docker-compose files

### unknown
**File**: `build/modules/registry_builder.py`
**Language**: python
**Purpose**: Static HTML registry generation module for control plane browser interface
**Architecture**: Integrates with existing build orchestrator as specialized module for static asset management
**Implementation**: Scans control/static_html directory and generates JavaScript registry following BuildModule interface

### RegistryBuilder
**File**: `build/modules/registry_builder.py`
**Language**: python
**Purpose**: Generates JavaScript registry of static HTML files for browser navigation
**Architecture**: Integrates with build orchestrator for caching and dependency management
**Implementation**: Scans filesystem, extracts HTML metadata, generates registry.js with kawaii ASCII TOC

### unknown
**File**: `build/modules/proto_client_builder.py`
**Language**: python
**Purpose**: Proto-to-polyglot client library generation module using unified DRY architecture
**Architecture**: Integrates with build orchestrator to provide cached, parallel proto client generation with DRY principles
**Implementation**: Generates TypeScript, C, Python, Kotlin client libraries from protobuf definitions using polyglot engine

### ProtoClientBuilder
**File**: `build/modules/proto_client_builder.py`
**Language**: python
**Purpose**: Polyglot protobuf client generation using unified DRY engine architecture
**Architecture**: Build module that eliminates code duplication in proto generation across multiple languages
**Implementation**: Orchestrates TypeScript, C, Python, Kotlin proto client generation through pluggable handlers

### unknown
**File**: `build/modules/service_discovery_builder.py`
**Language**: python
**Purpose**: Service discovery build module for compile-time service registry generation
**Architecture**: Integrates with existing build orchestrator using BuildModule contract for cached service discovery
**Implementation**: Discovers Docker and gRPC services at build time, generates static JavaScript registry for system health dashboard

### ServiceDiscoveryBuilder
**File**: `build/modules/service_discovery_builder.py`
**Language**: python
**Purpose**: Build-time service discovery module following existing BuildModule contract
**Architecture**: Integrates with build orchestrator for cached, dependency-aware service discovery
**Implementation**: Parses docker-compose.yml and proto files to generate static service registry

### unknown
**File**: `build/modules/polyglot_proto_engine.py`
**Language**: python
**Purpose**: Unified polyglot protobuf client generation engine with DRY architecture
**Architecture**: Central proto generation engine that eliminates code duplication across language-specific generators
**Implementation**: Generates TypeScript, C, Python, Kotlin clients from protobuf definitions using shared generation patterns

### unknown
**File**: `build/validators/port_validator.py`
**Language**: python
**Purpose**: Port conflict detection and resolution at build time
**Architecture**: Compile-time port validation that eliminates Docker port conflicts
**Implementation**: Statically analyzes port allocations to prevent runtime binding failures

### unknown
**File**: `build/validators/resource_validator.py`
**Language**: python
**Purpose**: Resource requirement validation at build time
**Architecture**: Compile-time resource validation ensuring adequate system resources
**Implementation**: Statically analyzes resource requirements to prevent runtime resource exhaustion

### unknown
**File**: `build/validators/__init__.py`
**Language**: python
**Purpose**: Compile-time validation system that eliminates runtime errors through static analysis
**Architecture**: Central validation system that ensures zero-failure runtime execution
**Implementation**: Validates port allocations, dependencies, and resource requirements before any deployment

### unknown
**File**: `build/validators/dependency_validator.py`
**Language**: python
**Purpose**: Dependency validation at build time to prevent runtime dependency failures
**Architecture**: Compile-time dependency validation preventing runtime startup failures
**Implementation**: Statically analyzes service dependencies to ensure proper startup order

## Validator Components

### test_parse_llm_tags_with_context
**File**: `build/docs-generation/test_llm_extraction.py`
**Language**: python
**Purpose**: Validates user input
**Architecture**: Part of validation pipeline
**Implementation**: Checks format and business rules

## Function Components

### can_handle
**File**: `build/modules/registry_builder.py`
**Language**: python
**Purpose**: Determines if this module can handle the given build context
**Architecture**: Called by build orchestrator during module selection phase
**Implementation**: Checks for registry-related target names and static_html directory existence

### get_dependencies
**File**: `build/modules/registry_builder.py`
**Language**: python
**Purpose**: Returns list of files that affect registry generation
**Architecture**: Used by build orchestrator for cache invalidation and dependency tracking
**Implementation**: Scans control/static_html for all HTML files to establish dependencies

### calculate_cache_key
**File**: `build/modules/registry_builder.py`
**Language**: python
**Purpose**: Generates content-based cache key for registry generation
**Architecture**: Used by build orchestrator for intelligent cache invalidation
**Implementation**: Combines file modification times and content hashes of all HTML files

### extract_html_metadata
**File**: `build/modules/registry_builder.py`
**Language**: python
**Purpose**: Extracts title, description, and metadata from HTML file
**Architecture**: Helper function for registry generation process
**Implementation**: Parses HTML content using regex to find title and meta tags

### scan_static_html_directory
**File**: `build/modules/registry_builder.py`
**Language**: python
**Purpose**: Recursively scans control/static_html for HTML files and extracts metadata
**Architecture**: Core scanning function that builds the complete file registry
**Implementation**: Walks filesystem tree, processes each HTML file, builds registry dictionary

### build_file_structure
**File**: `build/modules/registry_builder.py`
**Language**: python
**Purpose**: Builds hierarchical file structure for table-of-contents navigation
**Architecture**: Generates browser-consumable file tree for navigation components
**Implementation**: Scans control/static_html directory and creates nested structure with metadata

### generate_registry_js
**File**: `build/modules/registry_builder.py`
**Language**: python
**Purpose**: Generates JavaScript registry file with helper functions and kawaii ASCII TOC
**Architecture**: Converts Python registry dict to browser-consumable JavaScript
**Implementation**: Creates JavaScript module with registry object and utility functions

### build
**File**: `build/modules/registry_builder.py`
**Language**: python
**Purpose**: Main build function that generates the static HTML registry
**Architecture**: Called by build orchestrator to execute registry generation
**Implementation**: Scans filesystem, generates JavaScript registry, writes output file

### clean
**File**: `build/modules/registry_builder.py`
**Language**: python
**Purpose**: Removes generated registry.js file
**Architecture**: Called by build orchestrator during clean operations
**Implementation**: Deletes output file to force regeneration on next build

### start_flask_server
**File**: `services/vision-ai/main.py`
**Language**: python
**Purpose**: Starts Flask HTTP server to handle image analysis requests from backend
**Architecture**: Called by main thread, serves HTTP endpoints defined in app.py
**Implementation**: Binds to all interfaces on port 8001, disables debug mode for production

## Proto Components

### unknown
**File**: `build/modules/typescript_proto_handler.py`
**Language**: python
**Purpose**: TypeScript protobuf client generation handler with gRPC-Web support for browser applications
**Architecture**: TypeScript language handler for the polyglot proto engine providing browser-compatible gRPC clients
**Implementation**: Generates TypeScript protobuf clients with gRPC-Web integration for frontend applications

### unknown
**File**: `build/modules/python_proto_handler.py`
**Language**: python
**Purpose**: Python protobuf client generation handler for AI/ML services and backend systems
**Architecture**: Python language handler for the polyglot proto engine providing gRPC client generation for ML/AI services
**Implementation**: Generates Python protobuf clients with gRPC support for AI services and backend applications

### unknown
**File**: `build/modules/kotlin_proto_handler.py`
**Language**: python
**Purpose**: Kotlin protobuf client generation handler for JVM services and persistence platform
**Architecture**: Kotlin language handler for the polyglot proto engine providing JVM gRPC client generation
**Implementation**: Generates Kotlin protobuf clients with gRPC support for JVM-based services and persistence layer

### PolyglotProtoEngine
**File**: `build/modules/polyglot_proto_engine.py`
**Language**: python
**Purpose**: Unified engine for generating protobuf clients across multiple languages with DRY architecture
**Architecture**: Central orchestrator that eliminates duplication in proto generation logic across languages
**Implementation**: Coordinates TypeScript, C, Python, Kotlin proto generation using pluggable language handlers

### unknown
**File**: `build/modules/c_proto_handler.py`
**Language**: python
**Purpose**: C/C++ protobuf client generation handler for high-performance native services
**Architecture**: C++ language handler for the polyglot proto engine providing native gRPC client generation
**Implementation**: Generates C++ protobuf clients with gRPC support for native performance-critical services

## Contract Components

### unknown
**File**: `build/modules/__init__.py`
**Language**: python
**Purpose**: Language-specific build modules for enhanced build orchestration
**Architecture**: Build module system that integrates with main orchestrator for multi-language support
**Implementation**: Provides specialized builders for Kotlin, TypeScript, Python, and Protobuf with caching and optimization

## Virtualization Components

### unknown
**File**: `control/proxy_server.py`
**Language**: python
**Purpose**: HTTP proxy server that represents the line-in-the-sand between Unhinged System Commands and host OS operations
**Architecture**: This server is the future kernel interface - every endpoint here represents a system call in Unhinged OS
**Implementation**: Temporary shim server that will evolve into the primary interface for Unhinged OS virtualization layer

## Integration Components

### APITabIntegration
**File**: `control/static_html/shared/api-integration.js`
**Language**: typescript
**Purpose**: API client integration layer for tab system service communication
**Architecture**: Bridges generated proto clients with TabSystem for real service calls
**Implementation**: Provides seamless gRPC service access within tab-based browser interface

## Client Components

### UnhingedSDK
**File**: `control/sdk/javascript/unhinged-sdk.js`
**Language**: typescript
**Purpose**: JavaScript client SDK providing syntax sugar for Unhinged system operations
**Architecture**: Client library that makes system operations feel like native JavaScript
**Implementation**: Beautiful API abstractions over HTTP control proxy for system calls

## Control Components

### unknown
**File**: `control/system/__init__.py`
**Language**: python
**Purpose**: System control abstraction layer package for Unhinged platform
**Architecture**: Central control plane that bridges DevOps operations with build orchestration
**Implementation**: Provides operational abstractions over build system while preparing for future OS virtualization

### unknown
**File**: `control/system/system_controller.py`
**Language**: python
**Purpose**: System control abstraction layer that bridges build orchestration with operations semantics
**Architecture**: Central control plane that will evolve into virtualization boundary between Unhinged and host OS
**Implementation**: Translates DevOps operations (start/stop/restart) into build system targets while maintaining operational context

## Data Components

### unknown
**File**: `control/system/operation_result.py`
**Language**: python
**Purpose**: Operation result data model for system control operations
**Architecture**: Result model that will evolve into OS system call return values
**Implementation**: Standardized result format for all system operations with future OS compatibility

## Application Components

### PersistencePlatformApplication
**File**: `platforms/persistence/src/main/kotlin/com/unhinged/persistence/PersistencePlatformApplication.kt`
**Language**: kotlin
**Purpose**: Main application entry point for the Persistence Platform
**Architecture**: Main application orchestrating platform startup, configuration loading, and service initialization
**Implementation**: Application bootstrap that initializes platform, loads configuration, and starts API server

## Database Components

### DatabaseClientRegistry
**File**: `platforms/persistence/src/main/kotlin/com/unhinged/persistence/client/DatabaseClientRegistry.kt`
**Language**: kotlin
**Purpose**: Unified database client registry for multi-database persistence platform
**Architecture**: Central access point for all database operations in Kotlin services
**Implementation**: Manages CockroachDB, Redis, Cassandra, Chroma connections with health monitoring

## Observability Components

### ObservabilityManager
**File**: `platforms/persistence/src/main/kotlin/com/unhinged/persistence/monitoring/ObservabilityManager.kt`
**Language**: kotlin
**Purpose**: Comprehensive observability system providing metrics, tracing, and monitoring for the persistence platform
**Architecture**: Complete monitoring solution with metrics collection, distributed tracing, and performance analytics
**Implementation**: Central observability hub that collects metrics, traces requests, monitors health, and provides analytics

## Model Components

### ExecutionContext
**File**: `platforms/persistence/src/main/kotlin/com/unhinged/persistence/model/CoreModels.kt`
**Language**: kotlin
**Purpose**: Execution context that carries request metadata, tracing, and security information
**Architecture**: Context object passed through all persistence operations for observability and security
**Implementation**: Provides request context for all persistence operations including auth, tracing, and metadata

## Interface Components

### OperationOrchestrator
**File**: `platforms/persistence/src/main/kotlin/com/unhinged/persistence/core/OperationOrchestrator.kt`
**Language**: kotlin
**Purpose**: Operation orchestrator that manages complex multi-technology operations and workflows
**Architecture**: Central orchestration engine for complex operations requiring multiple database interactions
**Implementation**: Coordinates distributed transactions, async pipelines, and ML workflows across database technologies

### DatabaseProvider
**File**: `platforms/persistence/src/main/kotlin/com/unhinged/persistence/core/DatabaseProvider.kt`
**Language**: kotlin
**Purpose**: Database provider interface that each technology implements for platform integration
**Architecture**: Technology-specific implementations provide database access while maintaining common interface
**Implementation**: Defines contract for database operations that enables unified access across all technologies

### QueryExecutor
**File**: `platforms/persistence/src/main/kotlin/com/unhinged/persistence/core/QueryExecutor.kt`
**Language**: kotlin
**Purpose**: Query executor that handles query planning, optimization, caching, and routing
**Architecture**: Central query processing engine that routes queries to optimal database technologies
**Implementation**: Provides intelligent query execution with automatic optimization and caching strategies

### PersistenceManager
**File**: `platforms/persistence/src/main/kotlin/com/unhinged/persistence/core/PersistenceManager.kt`
**Language**: kotlin
**Purpose**: Main persistence platform manager that provides unified access to all database technologies
**Architecture**: Central orchestrator for all persistence operations across multiple database technologies
**Implementation**: Abstracts database complexity behind single API, handles routing, caching, and lifecycle management

## Implementation Components

### PersistenceManagerImpl
**File**: `platforms/persistence/src/main/kotlin/com/unhinged/persistence/impl/PersistenceManagerImpl.kt`
**Language**: kotlin
**Purpose**: Main persistence manager implementation that orchestrates all database operations
**Architecture**: Core persistence platform implementation that provides unified access to all database technologies
**Implementation**: Central implementation that coordinates providers, routing, caching, and lifecycle management

## Provider Components

### RedisProvider
**File**: `platforms/persistence/src/main/kotlin/com/unhinged/persistence/providers/RedisProvider.kt`
**Language**: kotlin
**Purpose**: Redis database provider for high-performance caching and session storage
**Architecture**: Redis provider for cache operations, session management, and real-time data storage
**Implementation**: Implements DatabaseProvider interface for Redis with TTL support and pub/sub capabilities

### CockroachDBProvider
**File**: `platforms/persistence/src/main/kotlin/com/unhinged/persistence/providers/CockroachDBProvider.kt`
**Language**: kotlin
**Purpose**: CockroachDB database provider for distributed SQL with ACID transactions
**Architecture**: CockroachDB provider for transactional data, financial records, and relational operations
**Implementation**: Implements DatabaseProvider interface for CockroachDB with strong consistency and horizontal scaling

## Registry Components

### ProviderRegistry
**File**: `platforms/persistence/src/main/kotlin/com/unhinged/persistence/providers/ProviderRegistry.kt`
**Language**: kotlin
**Purpose**: Provider registry that manages all database technology providers and their lifecycle
**Architecture**: Provider factory and lifecycle manager for all database technology implementations
**Implementation**: Central registry for creating, configuring, and managing database providers across all technologies

## Api Components

### PersistenceApiServer
**File**: `platforms/persistence/src/main/kotlin/com/unhinged/persistence/api/PersistenceApiServer.kt`
**Language**: kotlin
**Purpose**: Unified API server providing REST and gRPC endpoints for all persistence operations
**Architecture**: Unified API layer that abstracts database complexity behind consistent REST/gRPC endpoints
**Implementation**: Central API gateway that routes requests to appropriate database technologies with authentication and rate limiting

## Lifecycle Components

### DataLifecycleManager
**File**: `platforms/persistence/src/main/kotlin/com/unhinged/persistence/lifecycle/DataLifecycleManager.kt`
**Language**: kotlin
**Purpose**: Data lifecycle manager that handles hot/warm/cold data tiering and retention policies
**Architecture**: Central lifecycle management system that optimizes data placement and enforces retention policies
**Implementation**: Manages complete data lifecycle with automatic tiering, archival, and retention across all database technologies
