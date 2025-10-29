# 🏛️ Code Philosophy - Unhinged Platform

> **Purpose**: Fundamental design principles extracted from codebase
> **Source**: Auto-generated from @llm-axiom and @llm-token comments
> **Last Updated**: 2025-10-28 02:07:22

## 🎯 Fundamental Axioms

These are the non-negotiable principles that guide all development:

### unknown (python)
**File**: `build/llm_integration.py`
**Axiom**: LLM integration must provide helpful, accurate, and contextual assistance without overwhelming developers
**Context**: LLM integration for enhanced build system with context generation and error explanation

### unknown (python)
**File**: `build/cli.py`
**Axiom**: CLI must provide clear feedback, helpful error messages, and efficient developer workflows
**Context**: Enhanced CLI interface for the Unhinged build system

### unknown (python)
**File**: `build/orchestrator.py`
**Axiom**: Build operations must be deterministic, cacheable, and provide clear feedback to developers
**Context**: Enhanced build orchestrator for Unhinged polyglot monorepo

### unknown (python)
**File**: `build/monitoring.py`
**Axiom**: Performance monitoring must be lightweight and provide actionable insights for developers
**Context**: Build performance monitoring and metrics collection system

### unknown (python)
**File**: `build/developer_experience.py`
**Axiom**: Developer experience must reduce friction and provide clear, actionable feedback
**Context**: Developer experience enhancements for the enhanced build system

### unknown (python)
**File**: `build/build.py`
**Axiom**: Build system must be simple, fast, and provide clear feedback
**Context**: Main entry point for the Unhinged build system (v1)

### unknown (python)
**File**: `build/python/run.py`
**Axiom**: All Python execution must be consistent, reproducible, and ML/AI pipeline ready
**Context**: Universal Python runner for Unhinged on-premise ML/AI ETL & Big Data pipelines

### UnhingedPythonRunner (python)
**File**: `build/python/run.py`
**Axiom**: Python execution must be reproducible, environment-aware, and big data ready
**Context**: Centralized Python execution engine for ML/AI ETL and big data pipelines

### unknown (python)
**File**: `build/python/setup.py`
**Axiom**: Python environment must be reproducible, comprehensive, and big data ready
**Context**: Python environment setup for Unhinged on-premise ML/AI ETL & Big Data pipelines

### UnhingedPythonSetup (python)
**File**: `build/python/setup.py`
**Axiom**: Environment setup must be reproducible, comprehensive, and failure-resistant
**Context**: Comprehensive Python environment setup for ML/AI ETL and big data processing

### test_parse_llm_tags_with_context (python)
**File**: `build/docs-generation/test_llm_extraction.py`
**Axiom**: Never trust user input
**Context**: Validates user input

### unknown (python)
**File**: `build/tools/dead-code-analyzer.py`
**Axiom**: Dead code analysis must be conservative to avoid deleting functional code
**Context**: Comprehensive dead code and cruft detection tool for Unhinged codebase

### unknown (python)
**File**: `build/tools/cleanup-dead-code.py`
**Axiom**: Cleanup operations must be reversible and include comprehensive safety checks
**Context**: Safe dead code cleanup tool with backup and rollback capabilities

### unknown (python)
**File**: `build/tools/llm-docs-enforcer.py`
**Axiom**: All source files must have
**Context**: Automated LLM documentation header enforcement across all source files

### unknown (python)
**File**: `build/tools/llm-docs-enforcer.py`
**Axiom**: Maintains system independence and architectural compliance
**Context**: {file_name} - {purpose}

### unknown (python)
**File**: `build/tools/llm-docs-enforcer.py`
**Axiom**: Maintains system independence and architectural compliance {line_comment}
**Context**: {file_name} - {purpose} {line_comment}

### version (yaml)
**File**: `build/ci/ci-config.yml`
**Axiom**: CI/CD must maintain build system independence and caching benefits
**Context**: CI/CD pipeline configuration integrating with enhanced build system

### version (yaml)
**File**: `build/orchestration/docker-compose.production.yml`
**Axiom**: All services use categorical port allocation for conflict prevention
**Context**: Production docker-compose with unified service definitions

### version (yaml)
**File**: `build/orchestration/docker-compose.development.yml`
**Axiom**: Development services include debugging and monitoring capabilities
**Context**: Development docker-compose with debug tools and hot-reload

### version (yaml)
**File**: `build/config/build-config.yml`
**Axiom**: Build configuration must maintain system independence
**Context**: Main build configuration for Unhinged platform

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

### validate_build_patterns (python)
**File**: `build/modules/__init__.py`
**Axiom**: Build validation must prevent chaos and maintain architectural integrity
**Context**: Validate build system patterns and cultural commandments

### unknown (python)
**File**: `build/modules/c_builder.py`
**Axiom**: C builds must be deterministic, fast, and provide direct CPU instruction access for maximum performance
**Context**: C/C++ build module with CMake integration and CFFI bindings

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
**File**: `build/modules/dual_system_builder.py`
**Axiom**: Desktop application must include all dual-system components and be ready for immediate deployment
**Context**: Dual-system desktop application build module for CI/CD integration

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
**File**: `build/validators/kotlin_validator.py`
**Axiom**: Kotlin validation must enforce centralized build patterns and proper structure
**Context**: Kotlin-specific validation for build patterns and code quality

### unknown (python)
**File**: `build/validators/__init__.py`
**Axiom**: All runtime errors should be prevented by compile-time validation
**Context**: Compile-time validation system that eliminates runtime errors through static analysis

### unknown (python)
**File**: `build/validators/polyglot_validator.py`
**Axiom**: All validation must be fast, parallel, actionable, and educational
**Context**: Polyglot validation system for enforcing Unhinged codebase patterns and cultural commandments

### unknown (python)
**File**: `build/validators/dependency_validator.py`
**Axiom**: Dependency issues must be resolved at build time, never at runtime
**Context**: Dependency validation at build time to prevent runtime dependency failures

### unknown (python)
**File**: `build/validators/python_validator.py`
**Axiom**: Python validation must enforce centralized environment usage and proper documentation
**Context**: Python-specific validation for code quality, imports, and Unhinged patterns

### unknown (python)
**File**: `services/shared/__init__.py`
**Axiom**: Shared service code must be simple, reusable, and eliminate duplication
**Context**: Shared service utilities and base classes for Unhinged services

### unknown (python)
**File**: `services/shared/paths.py`
**Axiom**: Service utilities must be simple, reusable, and eliminate path hardcoding
**Context**: Shared utilities for service path management and common service operations

### ServicePaths (python)
**File**: `services/shared/paths.py`
**Axiom**: Service paths must be consistent, predictable, and environment-agnostic
**Context**: Service path manager providing standardized directory access

### unknown (python)
**File**: `services/speech-to-text/simple_whisper_server.py`
**Axiom**: Voice transcription must work immediately without setup
**Context**: Simple Whisper HTTP server for voice transcription

### unknown (python)
**File**: `services/speech-to-text/__init__.py`
**Axiom**: Maintains system independence and architectural compliance
**Context**: __init__.py - microservice component

### unknown (python)
**File**: `services/speech-to-text/main.py`
**Axiom**: Service must implement health.proto for service discovery and monitoring
**Context**: Speech-to-text service launcher with gRPC health.proto implementation

### unknown (python)
**File**: `services/speech-to-text/grpc_server.py`
**Axiom**: Service must implement health.proto for service discovery and monitoring
**Context**: Speech-to-Text gRPC server with health.proto implementation

### unknown (python)
**File**: `services/text-to-speech/main.py`
**Axiom**: Service must implement health.proto for service discovery and monitoring
**Context**: Text-to-speech service launcher with gRPC health.proto implementation

### unknown (python)
**File**: `services/text-to-speech/grpc_server.py`
**Axiom**: Service must implement health.proto for service discovery and monitoring
**Context**: Text-to-Speech gRPC server with health.proto implementation

### unknown (python)
**File**: `services/vision-ai/main.py`
**Axiom**: Service must implement health.proto for service discovery and monitoring
**Context**: Vision AI service launcher with gRPC health.proto implementation

### unknown (python)
**File**: `services/vision-ai/grpc_server.py`
**Axiom**: Service must implement health.proto for service discovery and monitoring
**Context**: Vision AI gRPC server with health.proto implementation

### unknown (python)
**File**: `control/proxy_server.py`
**Axiom**: This is where Unhinged abstractions meet raw system operations - design with future OS in mind
**Context**: HTTP proxy server that represents the line-in-the-sand between Unhinged System Commands and host OS operations

### unknown (python)
**File**: `control/conversation_cli.py`
**Axiom**: Voice-first interaction must be immediate, natural, and work seamlessly across both systems
**Context**: Conversation-based CLI interface for Unhinged dual-system architecture

### unknown (python)
**File**: `control/service_launcher.py`
**Axiom**: Uses service registry for dynamic service discovery and health monitoring
**Context**: Service launcher with unified service registry integration

### unknown (python)
**File**: `control/network/service_registry.py`
**Axiom**: Single source of truth for all service endpoints and health status
**Context**: service_registry.py - Central service discovery and registration system

### unknown (python)
**File**: `control/network/__init__.py`
**Axiom**: Network layer maintains service discovery and health monitoring independence
**Context**: __init__.py - Network control system module initialization

### unknown (python)
**File**: `control/deployment/deploy.py`
**Axiom**: Deployments must be atomic, reversible, and health-validated for operational safety
**Context**: Unified deployment orchestrator for Unhinged system runtime control

### UnhingedDeploymentOrchestrator (python)
**File**: `control/deployment/deploy.py`
**Axiom**: All deployments must be atomic, health-validated, and reversible
**Context**: Central deployment orchestrator managing environment-aware service deployment

### unknown (python)
**File**: `control/deployment/health-checks.py`
**Axiom**: Service health must be continuously monitored with automatic recovery actions
**Context**: Service health monitoring and validation for Unhinged runtime control

### UnhingedHealthMonitor (python)
**File**: `control/deployment/health-checks.py`
**Axiom**: Health monitoring must be continuous, accurate, and trigger automatic recovery
**Context**: Continuous health monitoring system for Unhinged service ecosystem

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

### environment (yaml)
**File**: `control/config/environments/production.yml`
**Axiom**: Production environment must prioritize security, performance, and reliability
**Context**: Production environment settings for Unhinged system deployment

### environment (yaml)
**File**: `control/config/environments/development.yml`
**Axiom**: Development environment must prioritize developer experience and debugging
**Context**: Development environment settings for Unhinged system development

### version (yaml)
**File**: `platforms/persistence/docker-compose.yml`
**Axiom**: Maintains system independence and architectural compliance
**Context**: docker-compose.yml - platform infrastructure component

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

### persistence_platform (yaml)
**File**: `platforms/persistence/config/persistence-platform.yaml`
**Axiom**: Maintains system independence and architectural compliance
**Context**: persistence-platform.yaml - platform infrastructure component

### unknown (python)
**File**: `desktop/auto_updater.py`
**Axiom**: Applications should stay current automatically without user intervention
**Context**: Auto-update system for Unhinged desktop application

### unknown (python)
**File**: `libs/design_system/build/design_token_builder.py`
**Axiom**: Design tokens must be generated before UI compilation and provide consistent styling
**Context**: Design token generation module following ProtoClientBuilder architecture pattern

### DesignTokenBuilder (python)
**File**: `libs/design_system/build/design_token_builder.py`
**Axiom**: Design tokens serve as single source of truth for all styling decisions
**Context**: Design token generation following ProtoClientBuilder architecture pattern

### unknown (python)
**File**: `libs/design_system/build/component_validator.py`
**Axiom**: All component specifications must be validated before generator consumption
**Context**: Component specification validator ensuring YAML specs conform to schema and design constraints

### unknown (python)
**File**: `libs/design_system/build/component_generator.py`
**Axiom**: Component generation is specification-first with platform equality, not GTK4-first
**Context**: Component generation orchestrator coordinating platform-specific generators from YAML specifications

### unknown (python)
**File**: `libs/design_system/build/component_build_module.py`
**Axiom**: Component generation follows build system patterns with proper caching and validation
**Context**: Component generation build module integrating with Unhinged build system

### unknown (python)
**File**: `libs/design_system/build/generators/_abstract_generator.py`
**Axiom**: All platform generators must implement identical interface for specification consumption
**Context**: Abstract component generator interface ensuring platform equality in design system

### unknown (python)
**File**: `libs/design_system/build/generators/gtk4/generator.py`
**Axiom**: GTK4 generator is one equal platform among many, not primary implementation
**Context**: GTK4 component generator producing Python widget implementations from YAML specifications

### unknown (python)
**File**: `libs/design_system/build/generators/gtk4/generator.py`
**Axiom**: Generated code should not be manually edited - regenerate from YAML specification #
**Context**: Auto-generated GTK4 widget from design system component specification #

### schema_version (yaml)
**File**: `libs/design_system/components/_schema.yaml`
**Axiom**: Component specifications must be platform-agnostic and describe WHAT not HOW
**Context**: Component specification meta-schema defining platform-agnostic component structure

### component (yaml)
**File**: `libs/design_system/components/primitives/modal.yaml`
**Axiom**: Modal specifications must be platform-agnostic describing semantic behavior not implementation
**Context**: Platform-agnostic modal dialog component specification for overlay content presentation

### component (yaml)
**File**: `libs/design_system/components/primitives/input.yaml`
**Axiom**: Input specifications must be platform-agnostic describing semantic behavior not implementation
**Context**: Platform-agnostic input field component specification for single-line text entry

### component (yaml)
**File**: `libs/design_system/components/primitives/button.yaml`
**Axiom**: Button specifications must be platform-agnostic describing WHAT not HOW
**Context**: Platform-agnostic button component specification defining semantic behavior and styling

### component (yaml)
**File**: `libs/design_system/components/primitives/simple-button.yaml`
**Axiom**: Simple component specifications should validate without errors
**Context**: Minimal button component specification for testing component generation pipeline

## 📚 Domain Vocabulary

Project-specific terminology and concepts:

### unknown
**Definition**: llm-build-integration: AI-powered assistance for build system operations
**Source**: `build/llm_integration.py` (python)

### unknown
**Definition**: build-cli: Command-line interface for enhanced build system
**Source**: `build/cli.py` (python)

### unknown
**Definition**: build-orchestrator: Python service coordinating all build operations across languages
**Source**: `build/orchestrator.py` (python)

### unknown
**Definition**: build-monitoring: Performance tracking and analytics for build system
**Source**: `build/monitoring.py` (python)

### unknown
**Definition**: dev-experience: Developer productivity enhancements for build system
**Source**: `build/developer_experience.py` (python)

### unknown
**Definition**: build-v1: Main entry point for v1 build system
**Source**: `build/build.py` (python)

### unknown
**Definition**: python-runner: Universal Python execution for on-premise big data and ML workflows
**Source**: `build/python/run.py` (python)

### UnhingedPythonRunner
**Definition**: python-executor: Production Python execution with ML/AI and big data support
**Source**: `build/python/run.py` (python)

### unknown
**Definition**: python-setup: Production Python environment setup for ML/AI and big data workflows
**Source**: `build/python/setup.py` (python)

### UnhingedPythonSetup
**Definition**: python-environment-setup: Production environment creation for ML/AI workflows
**Source**: `build/python/setup.py` (python)

### test_parse_llm_tags_with_context
**Definition**: user-validator
**Source**: `build/docs-generation/test_llm_extraction.py` (python)

### unknown
**Definition**: dead-code-analyzer: Systematic cruft detection and cleanup tool
**Source**: `build/tools/dead-code-analyzer.py` (python)

### unknown
**Definition**: cleanup-tool: Safe dead code removal with backup and rollback
**Source**: `build/tools/cleanup-dead-code.py` (python)

### unknown
**Definition**: llm-docs-enforcer: Automated documentation header validation and injection
**Source**: `build/tools/llm-docs-enforcer.py` (python)

### unknown
**Definition**: {file_path.stem}: {purpose}
**Source**: `build/tools/llm-docs-enforcer.py` (python)

### unknown
**Definition**: {file_path.stem}: {purpose}
**Source**: `build/tools/llm-docs-enforcer.py` (python)

### version
**Definition**: ci-config: CI/CD configuration for automated testing and deployment
**Source**: `build/ci/ci-config.yml` (yaml)

### version
**Definition**: docker-compose-production: Unified production service orchestration
**Source**: `build/orchestration/docker-compose.production.yml` (yaml)

### version
**Definition**: docker-compose-development: Development environment with debugging tools
**Source**: `build/orchestration/docker-compose.development.yml` (yaml)

### version
**Definition**: build-config: Central build configuration for Unhinged platform
**Source**: `build/config/build-config.yml` (yaml)

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

### validate_build_patterns
**Definition**: build-validation: Pattern enforcement integrated into build system
**Source**: `build/modules/__init__.py` (python)

### unknown
**Definition**: c-builder: CMake-based build module for C graphics rendering layer
**Source**: `build/modules/c_builder.py` (python)

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
**Definition**: dual-system-builder: Build module for dual-system desktop application packaging
**Source**: `build/modules/dual_system_builder.py` (python)

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
**Definition**: kotlin-validator: Kotlin and Gradle pattern validation for centralized build system
**Source**: `build/validators/kotlin_validator.py` (python)

### unknown
**Definition**: build-validators: Static analysis system preventing runtime failures
**Source**: `build/validators/__init__.py` (python)

### unknown
**Definition**: polyglot-validator: Comprehensive codebase pattern enforcement and validation system
**Source**: `build/validators/polyglot_validator.py` (python)

### unknown
**Definition**: dependency-validator: Static dependency analyzer preventing runtime startup errors
**Source**: `build/validators/dependency_validator.py` (python)

### unknown
**Definition**: python-validator: Python-specific pattern and quality validation
**Source**: `build/validators/python_validator.py` (python)

### unknown
**Definition**: service-shared: Shared utilities and base classes for service consistency
**Source**: `services/shared/__init__.py` (python)

### unknown
**Definition**: service-utilities: Shared utilities for consistent service path management
**Source**: `services/shared/paths.py` (python)

### ServicePaths
**Definition**: service-path-manager: Centralized service directory management
**Source**: `services/shared/paths.py` (python)

### unknown
**Definition**: whisper-server: HTTP service for voice transcription
**Source**: `services/speech-to-text/simple_whisper_server.py` (python)

### unknown
**Definition**: __init__: microservice component
**Source**: `services/speech-to-text/__init__.py` (python)

### unknown
**Definition**: speech-service: Whisper-based speech-to-text with gRPC and health.proto
**Source**: `services/speech-to-text/main.py` (python)

### unknown
**Definition**: stt-service: Speech-to-text with gRPC and health.proto
**Source**: `services/speech-to-text/grpc_server.py` (python)

### unknown
**Definition**: tts-service: Text-to-speech with gRPC and health.proto
**Source**: `services/text-to-speech/main.py` (python)

### unknown
**Definition**: tts-service: Text-to-speech with gRPC and health.proto
**Source**: `services/text-to-speech/grpc_server.py` (python)

### unknown
**Definition**: vision-service: Vision AI with gRPC and health.proto
**Source**: `services/vision-ai/main.py` (python)

### unknown
**Definition**: vision-service: Vision AI with gRPC and health.proto
**Source**: `services/vision-ai/grpc_server.py` (python)

### unknown
**Definition**: virtualization-proxy: The foundational HTTP layer that will become the Unhinged OS system call interface
**Source**: `control/proxy_server.py` (python)

### unknown
**Definition**: conversation-cli: Voice-first conversation interface for dual-system architecture
**Source**: `control/conversation_cli.py` (python)

### unknown
**Definition**: service-launcher: Unified service orchestration with registry integration
**Source**: `control/service_launcher.py` (python)

### unknown
**Definition**: service_registry: Centralized service discovery and health monitoring
**Source**: `control/network/service_registry.py` (python)

### unknown
**Definition**: network-control: Unified network service management subsystem
**Source**: `control/network/__init__.py` (python)

### unknown
**Definition**: deployment-orchestrator: Automated deployment control with environment management
**Source**: `control/deployment/deploy.py` (python)

### UnhingedDeploymentOrchestrator
**Definition**: deployment-core: Production deployment orchestration with operational safety
**Source**: `control/deployment/deploy.py` (python)

### unknown
**Definition**: health-monitor: Continuous service health monitoring with automated recovery
**Source**: `control/deployment/health-checks.py` (python)

### UnhingedHealthMonitor
**Definition**: health-monitor-core: Production health monitoring with automated recovery
**Source**: `control/deployment/health-checks.py` (python)

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

### environment
**Definition**: production-config: Production environment configuration for operational control
**Source**: `control/config/environments/production.yml` (yaml)

### environment
**Definition**: development-config: Development environment configuration for local control
**Source**: `control/config/environments/development.yml` (yaml)

### version
**Definition**: docker-compose: platform infrastructure component
**Source**: `platforms/persistence/docker-compose.yml` (yaml)

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

### persistence_platform
**Definition**: persistence-platform: platform infrastructure component
**Source**: `platforms/persistence/config/persistence-platform.yaml` (yaml)

### unknown
**Definition**: auto-updater: Automatic update system for desktop application
**Source**: `desktop/auto_updater.py` (python)

### unknown
**Definition**: design-token-builder: Design system generation from semantic YAML token definitions
**Source**: `libs/design_system/build/design_token_builder.py` (python)

### DesignTokenBuilder
**Definition**: design-token-builder: Semantic design token generation with build system integration
**Source**: `libs/design_system/build/design_token_builder.py` (python)

### unknown
**Definition**: component-validator: YAML specification validation with comprehensive error reporting
**Source**: `libs/design_system/build/component_validator.py` (python)

### unknown
**Definition**: component-orchestrator: Platform-agnostic component generation coordination
**Source**: `libs/design_system/build/component_generator.py` (python)

### unknown
**Definition**: component-build-module: Build system integration for component generation pipeline
**Source**: `libs/design_system/build/component_build_module.py` (python)

### unknown
**Definition**: component-generator-interface: Abstract base for platform-specific component code generation
**Source**: `libs/design_system/build/generators/_abstract_generator.py` (python)

### unknown
**Definition**: gtk4-generator: Platform-specific generator for GTK4 Python widget implementations
**Source**: `libs/design_system/build/generators/gtk4/generator.py` (python)

### schema_version
**Definition**: component-schema: Meta-schema for platform-agnostic component specifications
**Source**: `libs/design_system/components/_schema.yaml` (yaml)

### component
**Definition**: modal-component: Overlay dialog specification with focus trapping and backdrop interaction
**Source**: `libs/design_system/components/primitives/modal.yaml` (yaml)

### component
**Definition**: input-component: Single-line text input specification with validation and accessibility
**Source**: `libs/design_system/components/primitives/input.yaml` (yaml)

### component
**Definition**: button-component: Interactive element specification with semantic styling and accessibility
**Source**: `libs/design_system/components/primitives/button.yaml` (yaml)

### component
**Definition**: simple-button: Test component for component generation validation
**Source**: `libs/design_system/components/primitives/simple-button.yaml` (yaml)
