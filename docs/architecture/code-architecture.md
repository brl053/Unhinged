# 🗺️ Architectural Overview - Auto-Generated

> **Purpose**: System architecture extracted from code comments
> **Source**: Auto-generated from @llm-map and @llm-type comments
> **Last Updated**: 2025-10-28 02:07:22

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
**File**: `build/modules/c_builder.py`
**Language**: python
**Purpose**: C/C++ build module with CMake integration and CFFI bindings
**Architecture**: C build module that integrates with CMake build system and provides graphics rendering capabilities
**Implementation**: Provides optimized C builds with CMake, custom memory management, and Python CFFI integration

### unknown
**File**: `build/modules/python_builder.py`
**Language**: python
**Purpose**: Python build module with virtual environment management and dependency caching
**Architecture**: Python build module that integrates with pip/poetry build systems and provides enhanced caching
**Implementation**: Provides optimized Python builds with pip/poetry, virtual environments, and intelligent caching

### unknown
**File**: `build/modules/dual_system_builder.py`
**Language**: python
**Purpose**: Dual-system desktop application build module for CI/CD integration
**Architecture**: Build module that creates distribution packages for the dual-system architecture
**Implementation**: Builds and packages the enhanced GTK4 desktop application with conversation CLI integration

### unknown
**File**: `build/modules/kotlin_builder.py`
**Language**: python
**Purpose**: Kotlin/Gradle build module with incremental compilation and caching
**Architecture**: Kotlin build module that integrates with Gradle build system and provides enhanced caching
**Implementation**: Provides optimized Gradle builds with parallel execution, incremental compilation, and intelligent caching

### unknown
**File**: `services/shared/__init__.py`
**Language**: python
**Purpose**: Shared service utilities and base classes for Unhinged services
**Architecture**: Shared service components enabling consistent service architecture
**Implementation**: Common service functionality eliminating DRY violations across services

### unknown
**File**: `services/shared/paths.py`
**Language**: python
**Purpose**: Shared utilities for service path management and common service operations
**Architecture**: Common service utilities reducing DRY violations and standardizing service behavior
**Implementation**: Centralized path utilities eliminating hardcoded Docker paths across services

### ServicePaths
**File**: `services/shared/paths.py`
**Language**: python
**Purpose**: Service path manager providing standardized directory access
**Architecture**: Service path manager enabling consistent directory structure across services
**Implementation**: Centralized service path management eliminating hardcoded paths

### unknown
**File**: `services/speech-to-text/simple_whisper_server.py`
**Language**: python
**Purpose**: Simple Whisper HTTP server for voice transcription
**Architecture**: Core voice transcription service for voice-first GUI experience
**Implementation**: Provides HTTP endpoint for audio transcription using Whisper

### unknown
**File**: `services/speech-to-text/__init__.py`
**Language**: python
**Purpose**: __init__.py - microservice component
**Architecture**: Part of the Unhinged system architecture
**Implementation**: Core functionality for __init__

### unknown
**File**: `services/speech-to-text/main.py`
**Language**: python
**Purpose**: Speech-to-text service launcher with gRPC health.proto implementation
**Architecture**: Main entry point for whisper-based speech-to-text service using health.proto
**Implementation**: Launches gRPC API for speech transcription with standardized health endpoints

### unknown
**File**: `services/speech-to-text/grpc_server.py`
**Language**: python
**Purpose**: Speech-to-Text gRPC server with health.proto implementation
**Architecture**: gRPC server for speech-to-text service using health.proto compliance
**Implementation**: Provides STT capabilities via gRPC with standardized health endpoints

### unknown
**File**: `services/text-to-speech/main.py`
**Language**: python
**Purpose**: Text-to-speech service launcher with gRPC health.proto implementation
**Architecture**: Main entry point for TTS service using health.proto
**Implementation**: Launches gRPC API for text-to-speech with standardized health endpoints

### unknown
**File**: `services/text-to-speech/grpc_server.py`
**Language**: python
**Purpose**: Text-to-Speech gRPC server with health.proto implementation
**Architecture**: gRPC server for text-to-speech service using health.proto compliance
**Implementation**: Provides TTS capabilities via gRPC with standardized health endpoints

### unknown
**File**: `services/vision-ai/main.py`
**Language**: python
**Purpose**: Vision AI service launcher with gRPC health.proto implementation
**Architecture**: Main entry point for vision AI service using health.proto
**Implementation**: Launches gRPC API for vision analysis with standardized health endpoints

### unknown
**File**: `services/vision-ai/grpc_server.py`
**Language**: python
**Purpose**: Vision AI gRPC server with health.proto implementation
**Architecture**: gRPC server for vision AI service using health.proto compliance
**Implementation**: Provides vision analysis via gRPC with standardized health endpoints

### unknown
**File**: `control/conversation_cli.py`
**Language**: python
**Purpose**: Conversation-based CLI interface for Unhinged dual-system architecture
**Architecture**: Conversation CLI that bridges GTK4 control plane with Alpine VM conversation system
**Implementation**: Provides voice-first conversation interface accessible from both GTK4 control plane and native Alpine environment

### unknown
**File**: `desktop/auto_updater.py`
**Language**: python
**Purpose**: Auto-update system for Unhinged desktop application
**Architecture**: Auto-updater that checks for new versions and can update the desktop application automatically
**Implementation**: Provides automatic update checking and installation for the dual-system architecture desktop application

## Python Components

### unknown
**File**: `build/python/run.py`
**Language**: python
**Purpose**: Universal Python runner for Unhinged on-premise ML/AI ETL & Big Data pipelines
**Architecture**: Core Python execution engine supporting Kafka, Spark, Flink, Cassandra, Elasticsearch
**Implementation**: Centralized Python execution with Apache stack integration and ML/AI environment

### UnhingedPythonRunner
**File**: `build/python/run.py`
**Language**: python
**Purpose**: Centralized Python execution engine for ML/AI ETL and big data pipelines
**Architecture**: Core execution engine enabling consistent Python environments across all services
**Implementation**: Universal Python runner with Apache stack integration and environment management

### unknown
**File**: `build/python/setup.py`
**Language**: python
**Purpose**: Python environment setup for Unhinged on-premise ML/AI ETL & Big Data pipelines
**Architecture**: Environment setup enabling ML/AI ETL pipelines with Kafka, Spark, Flink, Cassandra
**Implementation**: Centralized Python environment creation with Apache stack and ML/AI dependencies

### UnhingedPythonSetup
**File**: `build/python/setup.py`
**Language**: python
**Purpose**: Comprehensive Python environment setup for ML/AI ETL and big data processing
**Architecture**: Core setup tool enabling consistent Python environments for on-premise big data
**Implementation**: Environment creation with Apache stack integration and ML/AI pipeline support

## Validator Components

### test_parse_llm_tags_with_context
**File**: `build/docs-generation/test_llm_extraction.py`
**Language**: python
**Purpose**: Validates user input
**Architecture**: Part of validation pipeline
**Implementation**: Checks format and business rules

### unknown
**File**: `build/validators/kotlin_validator.py`
**Language**: python
**Purpose**: Kotlin-specific validation for build patterns and code quality
**Architecture**: Language-specific validator that checks Kotlin/Gradle patterns and conventions
**Implementation**: Validates Kotlin files for proper build structure, dependencies, and Unhinged patterns

### unknown
**File**: `build/validators/python_validator.py`
**Language**: python
**Purpose**: Python-specific validation for code quality, imports, and Unhinged patterns
**Architecture**: Language-specific validator that checks Python code patterns and conventions
**Implementation**: Validates Python files for proper imports, llm-docs usage, and centralized environment compliance

### unknown
**File**: `libs/design_system/build/component_validator.py`
**Language**: python
**Purpose**: Component specification validator ensuring YAML specs conform to schema and design constraints
**Architecture**: Integrates with component generation pipeline to ensure specification quality before code generation
**Implementation**: Validates component specifications against meta-schema, token references, and accessibility requirements

## Dead Components

### unknown
**File**: `build/tools/dead-code-analyzer.py`
**Language**: python
**Purpose**: Comprehensive dead code and cruft detection tool for Unhinged codebase
**Architecture**: Integrates with existing dependency tracker and build system for accurate analysis
**Implementation**: Identifies unused files, phantom modules, orphaned documentation, and build artifacts

## Cleanup Components

### unknown
**File**: `build/tools/cleanup-dead-code.py`
**Language**: python
**Purpose**: Safe dead code cleanup tool with backup and rollback capabilities
**Architecture**: Integrates with dead-code-analyzer for systematic codebase cleanup
**Implementation**: Removes identified dead code with safety checks and backup mechanisms

## Build Components

### unknown
**File**: `build/tools/llm-docs-enforcer.py`
**Language**: python
**Purpose**: Automated LLM documentation header enforcement across all source files
**Architecture**: Build-time tool ensuring documentation consistency across the entire codebase
**Implementation**: Validates and injects standardized

### version
**File**: `build/config/build-config.yml`
**Language**: yaml
**Purpose**: Main build configuration for Unhinged platform
**Architecture**: Central configuration for build system orchestration
**Implementation**: Defines build targets, dependencies, and orchestration settings

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

### unknown
**File**: `libs/design_system/build/design_token_builder.py`
**Language**: python
**Purpose**: Design token generation module following ProtoClientBuilder architecture pattern
**Architecture**: Integrates with build orchestrator to provide cached design token generation
**Implementation**: Generates GTK4 CSS from YAML design tokens with dependency tracking and caching

### DesignTokenBuilder
**File**: `libs/design_system/build/design_token_builder.py`
**Language**: python
**Purpose**: Design token generation following ProtoClientBuilder architecture pattern
**Architecture**: Build module that generates design system artifacts with dependency tracking
**Implementation**: Orchestrates GTK4 CSS generation from semantic YAML tokens with caching and validation

### unknown
**File**: `libs/design_system/build/component_generator.py`
**Language**: python
**Purpose**: Component generation orchestrator coordinating platform-specific generators from YAML specifications
**Architecture**: Central orchestrator integrating with build system for component code generation
**Implementation**: Manages component generation pipeline with platform equality and specification-first architecture

### unknown
**File**: `libs/design_system/build/component_build_module.py`
**Language**: python
**Purpose**: Component generation build module integrating with Unhinged build system
**Architecture**: Integrates component generation orchestrator with existing build infrastructure
**Implementation**: Implements BuildModule interface for component generation with caching and dependency tracking

## Ci Components

### version
**File**: `build/ci/ci-config.yml`
**Language**: yaml
**Purpose**: CI/CD pipeline configuration integrating with enhanced build system
**Architecture**: Central CI/CD configuration extending build-config.yml
**Implementation**: Defines CI/CD workflows, test suites, and deployment automation

## Infrastructure Components

### version
**File**: `build/orchestration/docker-compose.production.yml`
**Language**: yaml
**Purpose**: Production docker-compose with unified service definitions
**Architecture**: Primary production deployment replacing fragmented compose files
**Implementation**: Single source of truth for production service orchestration

### version
**File**: `build/orchestration/docker-compose.development.yml`
**Language**: yaml
**Purpose**: Development docker-compose with debug tools and hot-reload
**Architecture**: Development deployment with additional observability services
**Implementation**: Development environment with debugging and monitoring tools

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

## Config Components

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

## Validation Components

### validate_build_patterns
**File**: `build/modules/__init__.py`
**Language**: python
**Purpose**: Validate build system patterns and cultural commandments
**Architecture**: Integrated enforcement that runs as part of build validation
**Implementation**: Checks for scattered files, proper generated content location, and cultural compliance

### unknown
**File**: `build/validators/polyglot_validator.py`
**Language**: python
**Purpose**: Polyglot validation system for enforcing Unhinged codebase patterns and cultural commandments
**Architecture**: Central validation orchestrator that coordinates language-specific validators and pattern checkers
**Implementation**: Modular, parallel validation runner that checks file patterns, build structure, and cultural compliance across all languages

## Virtualization Components

### unknown
**File**: `control/proxy_server.py`
**Language**: python
**Purpose**: HTTP proxy server that represents the line-in-the-sand between Unhinged System Commands and host OS operations
**Architecture**: This server is the future kernel interface - every endpoint here represents a system call in Unhinged OS
**Implementation**: Temporary shim server that will evolve into the primary interface for Unhinged OS virtualization layer

## Control Components

### unknown
**File**: `control/service_launcher.py`
**Language**: python
**Purpose**: Service launcher with unified service registry integration
**Architecture**: Core service orchestration component replacing hardcoded configurations
**Implementation**: Launches essential services using centralized service discovery

### unknown
**File**: `control/network/service_registry.py`
**Language**: python
**Purpose**: service_registry.py - Central service discovery and registration system
**Architecture**: Core component of the network control system providing service location transparency
**Implementation**: Unified service discovery replacing hardcoded service configurations

### unknown
**File**: `control/network/__init__.py`
**Language**: python
**Purpose**: __init__.py - Network control system module initialization
**Architecture**: Core network control components for unified service management
**Implementation**: Network subsystem providing service discovery and health monitoring

### unknown
**File**: `control/deployment/deploy.py`
**Language**: python
**Purpose**: Unified deployment orchestrator for Unhinged system runtime control
**Architecture**: Runtime deployment control enabling automated service orchestration and monitoring
**Implementation**: Central deployment automation with environment-aware orchestration and health validation

### UnhingedDeploymentOrchestrator
**File**: `control/deployment/deploy.py`
**Language**: python
**Purpose**: Central deployment orchestrator managing environment-aware service deployment
**Architecture**: Core operational tool for runtime service orchestration and deployment control
**Implementation**: Automated deployment with health validation, dependency management, and rollback

### unknown
**File**: `control/deployment/health-checks.py`
**Language**: python
**Purpose**: Service health monitoring and validation for Unhinged runtime control
**Architecture**: Runtime health monitoring enabling proactive service management and reliability
**Implementation**: Continuous health monitoring with alerting and automatic recovery capabilities

### UnhingedHealthMonitor
**File**: `control/deployment/health-checks.py`
**Language**: python
**Purpose**: Continuous health monitoring system for Unhinged service ecosystem
**Architecture**: Core operational monitoring enabling proactive service reliability management
**Implementation**: Real-time health validation with dependency checking and automatic recovery

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

### environment
**File**: `control/config/environments/production.yml`
**Language**: yaml
**Purpose**: Production environment settings for Unhinged system deployment
**Architecture**: Production environment control configuration for operational deployment
**Implementation**: Production-grade configuration with security, performance, and reliability settings

### environment
**File**: `control/config/environments/development.yml`
**Language**: yaml
**Purpose**: Development environment settings for Unhinged system development
**Architecture**: Development environment control configuration for local development
**Implementation**: Development-friendly configuration with debugging and rapid iteration support

## Client Components

### UnhingedSDK
**File**: `control/sdk/javascript/unhinged-sdk.js`
**Language**: typescript
**Purpose**: JavaScript client SDK providing syntax sugar for Unhinged system operations
**Architecture**: Client library that makes system operations feel like native JavaScript
**Implementation**: Beautiful API abstractions over HTTP control proxy for system calls

## Data Components

### unknown
**File**: `control/system/operation_result.py`
**Language**: python
**Purpose**: Operation result data model for system control operations
**Architecture**: Result model that will evolve into OS system call return values
**Implementation**: Standardized result format for all system operations with future OS compatibility

## Platform Components

### version
**File**: `platforms/persistence/docker-compose.yml`
**Language**: yaml
**Purpose**: docker-compose.yml - platform infrastructure component
**Architecture**: Part of the Unhinged system architecture
**Implementation**: Core functionality for docker-compose

### persistence_platform
**File**: `platforms/persistence/config/persistence-platform.yaml`
**Language**: yaml
**Purpose**: persistence-platform.yaml - platform infrastructure component
**Architecture**: Part of the Unhinged system architecture
**Implementation**: Core functionality for persistence-platform

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

## Generator Components

### unknown
**File**: `libs/design_system/build/generators/_abstract_generator.py`
**Language**: python
**Purpose**: Abstract component generator interface ensuring platform equality in design system
**Architecture**: Core abstraction enabling platform-agnostic component specifications with platform-specific implementations
**Implementation**: Defines consistent interface for generating platform-specific code from YAML specifications

## Component Components

### unknown
**File**: `libs/design_system/build/generators/gtk4/generator.py`
**Language**: python
**Purpose**: GTK4 component generator producing Python widget implementations from YAML specifications
**Architecture**: Platform-specific implementation of abstract generator interface for GTK4 desktop applications
**Implementation**: Generates GtkWidget subclasses with GObject properties, signals, and design token integration

### component
**File**: `libs/design_system/components/primitives/modal.yaml`
**Language**: yaml
**Purpose**: Platform-agnostic modal dialog component specification for overlay content presentation
**Architecture**: Core container component for interrupting user flow with contextual content
**Implementation**: Modal container with focus management, backdrop handling, and keyboard navigation support

### component
**File**: `libs/design_system/components/primitives/input.yaml`
**Language**: yaml
**Purpose**: Platform-agnostic input field component specification for single-line text entry
**Architecture**: Core primitive component for form data collection in design system
**Implementation**: Text input element with validation states, placeholder support, and accessibility features

### component
**File**: `libs/design_system/components/primitives/button.yaml`
**Language**: yaml
**Purpose**: Platform-agnostic button component specification defining semantic behavior and styling
**Architecture**: Core primitive component in design system component hierarchy
**Implementation**: Primary interactive element specification with semantic types, states, and accessibility requirements

### component
**File**: `libs/design_system/components/primitives/simple-button.yaml`
**Language**: yaml
**Purpose**: Minimal button component specification for testing component generation pipeline
**Architecture**: Test component for validating component generation system
**Implementation**: Simple interactive button with correct token references for validation testing

## Generated Components

### unknown
**File**: `libs/design_system/build/generators/gtk4/generator.py`
**Language**: python
**Purpose**: Auto-generated GTK4 widget from design system component specification #
**Architecture**: Generated component implementing platform-agnostic specification #
**Implementation**: GTK4 implementation of {component_name} with design token integration #

## Schema Components

### schema_version
**File**: `libs/design_system/components/_schema.yaml`
**Language**: yaml
**Purpose**: Component specification meta-schema defining platform-agnostic component structure
**Architecture**: Central schema authority for design system component generation architecture
**Implementation**: Validates YAML component specifications ensuring consistency across all platform generators
