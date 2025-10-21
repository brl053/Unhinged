# 🏛️ Code Philosophy - Unhinged Platform

> **Purpose**: Fundamental design principles extracted from codebase
> **Source**: Auto-generated from @llm-axiom and @llm-token comments
> **Last Updated**: 2025-10-20 19:15:02

## 🎯 Fundamental Axioms

These are the non-negotiable principles that guide all development:

### vision-ai (yaml)
**File**: `docker-compose.yml`
**Axiom**: Vision service must be accessible on port 8001 for backend integration
**Context**: Docker service configuration for AI-powered image analysis microservice

### speech-to-text (yaml)
**File**: `docker-compose.yml`
**Axiom**: Service must be accessible on port 8000 for voice test page

### text-to-speech (yaml)
**File**: `docker-compose.yml`
**Axiom**: Service must be accessible on port 8002 for TTS functionality

### unknown (python)
**File**: `build/llm_integration.py`
**Axiom**: LLM integration must provide helpful, accurate, and contextual assistance without overwhelming developers
**Context**: LLM integration for enhanced build system with context generation and error explanation

### unknown (python)
**File**: `build/generate-registry.py`
**Axiom**: Must work independently of build system for simple make start workflow
**Context**: Simple script to generate static HTML registry for make start command

### unknown (python)
**File**: `build/cli.py`
**Axiom**: CLI must provide clear feedback, helpful error messages, and efficient developer workflows
**Context**: Enhanced CLI interface for the Unhinged build system

### unknown (python)
**File**: `build/test_enhanced_system.py`
**Axiom**: Tests must be comprehensive, fast, and provide clear feedback on system health
**Context**: Test suite for the enhanced build system

### unknown (python)
**File**: `build/orchestrator.py`
**Axiom**: Build operations must be deterministic, cacheable, and provide clear feedback to developers
**Context**: Enhanced build orchestrator for Unhinged polyglot monorepo

### unknown (python)
**File**: `build/monitoring.py`
**Axiom**: Performance monitoring must be lightweight and provide actionable insights for developers
**Context**: Build performance monitoring and metrics collection system

### unknown (python)
**File**: `build/port_fixer.py`
**Axiom**: Port conflicts must be resolved automatically with minimal manual intervention
**Context**: Port conflict detection and automatic resolution tool

### unknown (python)
**File**: `build/developer_experience.py`
**Axiom**: Developer experience must reduce friction and provide clear, actionable feedback
**Context**: Developer experience enhancements for the enhanced build system

### unknown (python)
**File**: `build/build.py`
**Axiom**: Build system must be simple, fast, and provide clear feedback
**Context**: Main entry point for the Unhinged build system (v1)

### test_parse_llm_tags_with_context (python)
**File**: `build/docs-generation/test_llm_extraction.py`
**Axiom**: Never trust user input
**Context**: Validates user input

### unknown (python)
**File**: `build/modules/typescript_builder.py`
**Axiom**: TypeScript builds must support hot reloading for development and optimization for production
**Context**: TypeScript/npm build module with webpack optimization and hot reloading

### unknown (python)
**File**: `build/modules/registry_builder.py`
**Axiom**: Must follow BuildModule contract and provide caching, validation, and artifact management
**Context**: Static HTML registry generation module for control plane browser interface

### RegistryBuilder (python)
**File**: `build/modules/registry_builder.py`
**Axiom**: Registry must be generated before browser access to ensure accurate file discovery
**Context**: Generates JavaScript registry of static HTML files for browser navigation

### unknown (python)
**File**: `build/modules/registry_builder.py`
**Axiom**: Registry must be regenerated whenever HTML files are added/removed/modified *
**Context**: Global registry of static HTML files for browser navigation *

### unknown (python)
**File**: `build/modules/proto_client_builder.py`
**Axiom**: Client libraries must be generated before service compilation and provide type-safe APIs across all languages
**Context**: Proto-to-polyglot client library generation module using unified DRY architecture

### ProtoClientBuilder (python)
**File**: `build/modules/proto_client_builder.py`
**Axiom**: All proto client generation must use the unified polyglot engine for consistency
**Context**: Polyglot protobuf client generation using unified DRY engine architecture

### unknown (python)
**File**: `build/modules/typescript_proto_handler.py`
**Axiom**: TypeScript proto clients must support both Node.js and browser environments with type safety
**Context**: TypeScript protobuf client generation handler with gRPC-Web support for browser applications

### unknown (python)
**File**: `build/modules/__init__.py`
**Axiom**: Each language builder must provide consistent interface and caching capabilities
**Context**: Language-specific build modules for enhanced build orchestration

### unknown (python)
**File**: `build/modules/python_builder.py`
**Axiom**: Python builds must use isolated virtual environments and cache dependencies effectively
**Context**: Python build module with virtual environment management and dependency caching

### unknown (python)
**File**: `build/modules/python_proto_handler.py`
**Axiom**: Python proto clients must support async/await patterns and integrate with AI/ML frameworks
**Context**: Python protobuf client generation handler for AI/ML services and backend systems

### unknown (python)
**File**: `build/modules/service_discovery_builder.py`
**Axiom**: Service discovery must happen at build time to ensure HTML dashboard is always up-to-date
**Context**: Service discovery build module for compile-time service registry generation

### ServiceDiscoveryBuilder (python)
**File**: `build/modules/service_discovery_builder.py`
**Axiom**: Service registry must be generated before HTML dashboard access
**Context**: Build-time service discovery module following existing BuildModule contract

### unknown (python)
**File**: `build/modules/kotlin_proto_handler.py`
**Axiom**: Kotlin proto clients must integrate seamlessly with existing JVM services and provide coroutine support
**Context**: Kotlin protobuf client generation handler for JVM services and persistence platform

### unknown (python)
**File**: `build/modules/polyglot_proto_engine.py`
**Axiom**: All proto client generation must use this unified engine to maintain consistency and reduce duplication
**Context**: Unified polyglot protobuf client generation engine with DRY architecture

### PolyglotProtoEngine (python)
**File**: `build/modules/polyglot_proto_engine.py`
**Axiom**: All proto client generation must use this engine for consistency and maintainability
**Context**: Unified engine for generating protobuf clients across multiple languages with DRY architecture

### unknown (python)
**File**: `build/modules/c_proto_handler.py`
**Axiom**: C++ proto clients must provide maximum performance for system-level services
**Context**: C/C++ protobuf client generation handler for high-performance native services

### unknown (python)
**File**: `build/modules/kotlin_builder.py`
**Axiom**: Gradle builds must be deterministic and support incremental compilation for fast development
**Context**: Kotlin/Gradle build module with incremental compilation and caching

### unknown (python)
**File**: `build/validators/port_validator.py`
**Axiom**: Port conflicts must be resolved at build time, never at runtime
**Context**: Port conflict detection and resolution at build time

### unknown (python)
**File**: `build/validators/resource_validator.py`
**Axiom**: Resource issues must be detected at build time, never at runtime
**Context**: Resource requirement validation at build time

### unknown (python)
**File**: `build/validators/__init__.py`
**Axiom**: All runtime errors should be prevented by compile-time validation
**Context**: Compile-time validation system that eliminates runtime errors through static analysis

### unknown (python)
**File**: `build/validators/dependency_validator.py`
**Axiom**: Dependency issues must be resolved at build time, never at runtime
**Context**: Dependency validation at build time to prevent runtime dependency failures

### unknown (python)
**File**: `services/vision-ai/main.py`
**Axiom**: Vision model must be loaded and ready before accepting any processing requests
**Context**: Provides AI-powered image analysis using BLIP vision model for user-uploaded content

### unknown (python)
**File**: `control/proxy_server.py`
**Axiom**: This is where Unhinged abstractions meet raw system operations - design with future OS in mind
**Context**: HTTP proxy server that represents the line-in-the-sand between Unhinged System Commands and host OS operations

### APITabIntegration (typescript)
**File**: `control/static_html/shared/api-integration.js`
**Axiom**: All service communication must be type-safe and error-handled
**Context**: API client integration layer for tab system service communication

### UnhingedSDK (typescript)
**File**: `control/sdk/javascript/unhinged-sdk.js`
**Axiom**: All system operations should feel natural and intuitive to developers
**Context**: JavaScript client SDK providing syntax sugar for Unhinged system operations

### unknown (python)
**File**: `control/system/__init__.py`
**Axiom**: All system operations must be auditable, reversible, and provide clear operational feedback
**Context**: System control abstraction layer package for Unhinged platform

### unknown (python)
**File**: `control/system/system_controller.py`
**Axiom**: All system operations must be auditable, reversible, and provide clear operational feedback
**Context**: System control abstraction layer that bridges build orchestration with operations semantics

### unknown (python)
**File**: `control/system/operation_result.py`
**Axiom**: All operations must return structured, auditable results
**Context**: Operation result data model for system control operations

### PersistencePlatformApplication (kotlin)
**File**: `platforms/persistence/src/main/kotlin/com/unhinged/persistence/PersistencePlatformApplication.kt`
**Axiom**: Application must handle graceful startup and shutdown with proper error handling
**Context**: Main application entry point for the Persistence Platform

### DatabaseClientRegistry (kotlin)
**File**: `platforms/persistence/src/main/kotlin/com/unhinged/persistence/client/DatabaseClientRegistry.kt`
**Axiom**: All database access must go through registry for monitoring and connection management
**Context**: Unified database client registry for multi-database persistence platform

### ObservabilityManager (kotlin)
**File**: `platforms/persistence/src/main/kotlin/com/unhinged/persistence/monitoring/ObservabilityManager.kt`
**Axiom**: All persistence operations must be observable for proper monitoring and troubleshooting
**Context**: Comprehensive observability system providing metrics, tracing, and monitoring for the persistence platform

### ExecutionContext (kotlin)
**File**: `platforms/persistence/src/main/kotlin/com/unhinged/persistence/model/CoreModels.kt`
**Axiom**: All persistence operations must include execution context for proper tracing and security
**Context**: Execution context that carries request metadata, tracing, and security information

### OperationOrchestrator (kotlin)
**File**: `platforms/persistence/src/main/kotlin/com/unhinged/persistence/core/OperationOrchestrator.kt`
**Axiom**: All complex operations must be orchestrated through this interface for consistency and reliability
**Context**: Operation orchestrator that manages complex multi-technology operations and workflows

### DatabaseProvider (kotlin)
**File**: `platforms/persistence/src/main/kotlin/com/unhinged/persistence/core/DatabaseProvider.kt`
**Axiom**: Each database technology must implement this interface to participate in the platform
**Context**: Database provider interface that each technology implements for platform integration

### QueryExecutor (kotlin)
**File**: `platforms/persistence/src/main/kotlin/com/unhinged/persistence/core/QueryExecutor.kt`
**Axiom**: All queries must be processed through this executor for consistency and optimization
**Context**: Query executor that handles query planning, optimization, caching, and routing

### PersistenceManager (kotlin)
**File**: `platforms/persistence/src/main/kotlin/com/unhinged/persistence/core/PersistenceManager.kt`
**Axiom**: All database operations must go through this interface to ensure consistency and observability
**Context**: Main persistence platform manager that provides unified access to all database technologies

### PersistenceManagerImpl (kotlin)
**File**: `platforms/persistence/src/main/kotlin/com/unhinged/persistence/impl/PersistenceManagerImpl.kt`
**Axiom**: All persistence operations flow through this implementation for consistency and observability
**Context**: Main persistence manager implementation that orchestrates all database operations

### RedisProvider (kotlin)
**File**: `platforms/persistence/src/main/kotlin/com/unhinged/persistence/providers/RedisProvider.kt`
**Axiom**: All Redis operations must handle TTL and provide fast access patterns
**Context**: Redis database provider for high-performance caching and session storage

### ProviderRegistry (kotlin)
**File**: `platforms/persistence/src/main/kotlin/com/unhinged/persistence/providers/ProviderRegistry.kt`
**Axiom**: All database providers must be registered and managed through this registry
**Context**: Provider registry that manages all database technology providers and their lifecycle

### CockroachDBProvider (kotlin)
**File**: `platforms/persistence/src/main/kotlin/com/unhinged/persistence/providers/CockroachDBProvider.kt`
**Axiom**: All CockroachDB operations must maintain ACID properties and strong consistency
**Context**: CockroachDB database provider for distributed SQL with ACID transactions

### PersistenceApiServer (kotlin)
**File**: `platforms/persistence/src/main/kotlin/com/unhinged/persistence/api/PersistenceApiServer.kt`
**Axiom**: All persistence operations must go through this API layer for consistency and security
**Context**: Unified API server providing REST and gRPC endpoints for all persistence operations

### PersistenceConfiguration (kotlin)
**File**: `platforms/persistence/src/main/kotlin/com/unhinged/persistence/config/ConfigurationModels.kt`
**Axiom**: Configuration must be validated before platform initialization
**Context**: Main persistence platform configuration loaded from YAML

### DataLifecycleManager (kotlin)
**File**: `platforms/persistence/src/main/kotlin/com/unhinged/persistence/lifecycle/DataLifecycleManager.kt`
**Axiom**: All data must follow defined lifecycle policies for optimal performance and compliance
**Context**: Data lifecycle manager that handles hot/warm/cold data tiering and retention policies

### unknown (typescript)
**File**: `generated/static_html/registry.js`
**Axiom**: Registry must be regenerated whenever HTML files are added/removed/modified
**Context**: Global registry of static HTML files for browser navigation

### unknown (typescript)
**File**: `generated/static_html/registry.js`
**Axiom**: File structure regenerated on every make start to reflect current filesystem
**Context**: Hierarchical file structure for table-of-contents navigation

## 📚 Domain Vocabulary

Project-specific terminology and concepts:

### vision-ai
**Definition**: vision-models: Docker volume for persistent transformer model cache
**Source**: `docker-compose.yml` (yaml)

### speech-to-text
**Definition**: whisper-models: Docker volume for persistent Whisper model cache
**Source**: `docker-compose.yml` (yaml)

### text-to-speech
**Definition**: tts-models: Docker volume for persistent TTS model cache
**Source**: `docker-compose.yml` (yaml)

### unknown
**Definition**: llm-build-integration: AI-powered assistance for build system operations
**Source**: `build/llm_integration.py` (python)

### unknown
**Definition**: registry-generator: Simple registry generation script for make start
**Source**: `build/generate-registry.py` (python)

### unknown
**Definition**: build-cli: Command-line interface for enhanced build system
**Source**: `build/cli.py` (python)

### unknown
**Definition**: build-test: Comprehensive test suite for enhanced build system
**Source**: `build/test_enhanced_system.py` (python)

### unknown
**Definition**: build-orchestrator: Python service coordinating all build operations across languages
**Source**: `build/orchestrator.py` (python)

### unknown
**Definition**: build-monitoring: Performance tracking and analytics for build system
**Source**: `build/monitoring.py` (python)

### unknown
**Definition**: port-fixer: Automated port conflict resolution tool for build system
**Source**: `build/port_fixer.py` (python)

### unknown
**Definition**: dev-experience: Developer productivity enhancements for build system
**Source**: `build/developer_experience.py` (python)

### unknown
**Definition**: build-v1: Main entry point for v1 build system
**Source**: `build/build.py` (python)

### test_parse_llm_tags_with_context
**Definition**: user-validator
**Source**: `build/docs-generation/test_llm_extraction.py` (python)

### unknown
**Definition**: typescript-builder: npm/webpack-based build module for TypeScript/React projects
**Source**: `build/modules/typescript_builder.py` (python)

### unknown
**Definition**: registry-builder: Build module for static HTML file registry generation
**Source**: `build/modules/registry_builder.py` (python)

### RegistryBuilder
**Definition**: static-html-registry: Browser-consumable file registry for navigation
**Source**: `build/modules/registry_builder.py` (python)

### unknown
**Definition**: unhinged-registry: Complete file registry for static HTML interface */ window.UNHINGED_REGISTRY = {json.dumps(registry, indent=2)};
**Source**: `build/modules/registry_builder.py` (python)

### unknown
**Definition**: proto-client-builder: DRY polyglot gRPC client library generation from protobuf schemas
**Source**: `build/modules/proto_client_builder.py` (python)

### ProtoClientBuilder
**Definition**: polyglot-proto-builder: Unified multi-language protobuf client generation orchestrator
**Source**: `build/modules/proto_client_builder.py` (python)

### unknown
**Definition**: typescript-proto-handler: Type-safe TypeScript protobuf client generation for web applications
**Source**: `build/modules/typescript_proto_handler.py` (python)

### unknown
**Definition**: build-modules: Specialized build handlers for different programming languages
**Source**: `build/modules/__init__.py` (python)

### unknown
**Definition**: python-builder: pip/poetry-based build module for Python services
**Source**: `build/modules/python_builder.py` (python)

### unknown
**Definition**: python-proto-handler: Python protobuf client generation for AI/ML services and backend systems
**Source**: `build/modules/python_proto_handler.py` (python)

### unknown
**Definition**: service-discovery-builder: Build-time service discovery for system health monitoring
**Source**: `build/modules/service_discovery_builder.py` (python)

### ServiceDiscoveryBuilder
**Definition**: build-time-service-discovery: Compile-time service discovery for health monitoring
**Source**: `build/modules/service_discovery_builder.py` (python)

### unknown
**Definition**: kotlin-proto-handler: Kotlin protobuf client generation for JVM services and persistence platform
**Source**: `build/modules/kotlin_proto_handler.py` (python)

### unknown
**Definition**: polyglot-proto-engine: Unified DRY protobuf client generation for multiple languages
**Source**: `build/modules/polyglot_proto_engine.py` (python)

### PolyglotProtoEngine
**Definition**: polyglot-proto-coordinator: Multi-language protobuf client generation orchestrator
**Source**: `build/modules/polyglot_proto_engine.py` (python)

### unknown
**Definition**: c-proto-handler: High-performance C++ protobuf client generation for native services
**Source**: `build/modules/c_proto_handler.py` (python)

### unknown
**Definition**: kotlin-builder: Gradle-based build module for Kotlin/JVM projects
**Source**: `build/modules/kotlin_builder.py` (python)

### unknown
**Definition**: port-validator: Static port allocation analyzer preventing runtime binding errors
**Source**: `build/validators/port_validator.py` (python)

### unknown
**Definition**: resource-validator: Static resource analyzer preventing runtime resource failures
**Source**: `build/validators/resource_validator.py` (python)

### unknown
**Definition**: build-validators: Static analysis system preventing runtime failures
**Source**: `build/validators/__init__.py` (python)

### unknown
**Definition**: dependency-validator: Static dependency analyzer preventing runtime startup errors
**Source**: `build/validators/dependency_validator.py` (python)

### unknown
**Definition**: BLIP: Bootstrapping Language-Image Pre-training model for image captioning
**Source**: `services/vision-ai/main.py` (python)

### unknown
**Definition**: virtualization-proxy: The foundational HTTP layer that will become the Unhinged OS system call interface
**Source**: `control/proxy_server.py` (python)

### APITabIntegration
**Definition**: api-tab-integration: Service client integration for tab-based control plane
**Source**: `control/static_html/shared/api-integration.js` (typescript)

### UnhingedSDK
**Definition**: unhinged-sdk: JavaScript client providing elegant system call abstractions
**Source**: `control/sdk/javascript/unhinged-sdk.js` (typescript)

### unknown
**Definition**: control-system: Package containing system control abstractions and virtualization boundary interfaces
**Source**: `control/system/__init__.py` (python)

### unknown
**Definition**: system-controller: Control plane service managing the boundary between application logic and system operations
**Source**: `control/system/system_controller.py` (python)

### unknown
**Definition**: operation-result: Data model for system operation results and future OS return values
**Source**: `control/system/operation_result.py` (python)

### PersistencePlatformApplication
**Definition**: persistence-platform-app: Main application entry point and bootstrap
**Source**: `platforms/persistence/src/main/kotlin/com/unhinged/persistence/PersistencePlatformApplication.kt` (kotlin)

### DatabaseClientRegistry
**Definition**: database-client-registry: Unified database access management for Kotlin backend
**Source**: `platforms/persistence/src/main/kotlin/com/unhinged/persistence/client/DatabaseClientRegistry.kt` (kotlin)

### ObservabilityManager
**Definition**: observability-manager: Complete monitoring and observability system
**Source**: `platforms/persistence/src/main/kotlin/com/unhinged/persistence/monitoring/ObservabilityManager.kt` (kotlin)

### ExecutionContext
**Definition**: execution-context: Request context for persistence operations
**Source**: `platforms/persistence/src/main/kotlin/com/unhinged/persistence/model/CoreModels.kt` (kotlin)

### OperationOrchestrator
**Definition**: operation-orchestrator: Complex operation coordination and workflow management
**Source**: `platforms/persistence/src/main/kotlin/com/unhinged/persistence/core/OperationOrchestrator.kt` (kotlin)

### DatabaseProvider
**Definition**: database-provider: Technology-specific database access interface
**Source**: `platforms/persistence/src/main/kotlin/com/unhinged/persistence/core/DatabaseProvider.kt` (kotlin)

### QueryExecutor
**Definition**: query-executor: Intelligent query processing and routing engine
**Source**: `platforms/persistence/src/main/kotlin/com/unhinged/persistence/core/QueryExecutor.kt` (kotlin)

### PersistenceManager
**Definition**: persistence-manager: Core interface for unified database access
**Source**: `platforms/persistence/src/main/kotlin/com/unhinged/persistence/core/PersistenceManager.kt` (kotlin)

### PersistenceManagerImpl
**Definition**: persistence-manager-impl: Core persistence platform implementation
**Source**: `platforms/persistence/src/main/kotlin/com/unhinged/persistence/impl/PersistenceManagerImpl.kt` (kotlin)

### RedisProvider
**Definition**: redis-provider: High-performance Redis database provider implementation
**Source**: `platforms/persistence/src/main/kotlin/com/unhinged/persistence/providers/RedisProvider.kt` (kotlin)

### ProviderRegistry
**Definition**: provider-registry: Central database provider management and factory
**Source**: `platforms/persistence/src/main/kotlin/com/unhinged/persistence/providers/ProviderRegistry.kt` (kotlin)

### CockroachDBProvider
**Definition**: cockroachdb-provider: Distributed SQL database provider implementation
**Source**: `platforms/persistence/src/main/kotlin/com/unhinged/persistence/providers/CockroachDBProvider.kt` (kotlin)

### PersistenceApiServer
**Definition**: persistence-api-server: Unified API gateway for all database operations
**Source**: `platforms/persistence/src/main/kotlin/com/unhinged/persistence/api/PersistenceApiServer.kt` (kotlin)

### PersistenceConfiguration
**Definition**: persistence-configuration: Complete platform configuration object
**Source**: `platforms/persistence/src/main/kotlin/com/unhinged/persistence/config/ConfigurationModels.kt` (kotlin)

### DataLifecycleManager
**Definition**: data-lifecycle-manager: Automated data lifecycle and tiering management
**Source**: `platforms/persistence/src/main/kotlin/com/unhinged/persistence/lifecycle/DataLifecycleManager.kt` (kotlin)

### unknown
**Definition**: unhinged-registry: Complete file registry for static HTML interface
**Source**: `generated/static_html/registry.js` (typescript)

### unknown
**Definition**: unhinged-file-structure: Complete directory tree for navigation
**Source**: `generated/static_html/registry.js` (typescript)
