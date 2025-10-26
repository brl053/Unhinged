# 🗺️ Architectural Overview - Auto-Generated

> **Purpose**: System architecture extracted from code comments
> **Source**: Auto-generated from @llm-map and @llm-type comments
> **Last Updated**: 2025-10-24 22:33:44

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
**File**: `control/native_gui/services/llm_client.py`
**Language**: python
**Purpose**: llm_client.py - microservice component
**Architecture**: Part of the Unhinged system architecture
**Implementation**: Core functionality for llm_client

### unknown
**File**: `control/native_gui/services/__init__.py`
**Language**: python
**Purpose**: __init__.py - microservice component
**Architecture**: Part of the Unhinged system architecture
**Implementation**: Core functionality for __init__

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

### MobileUIIntegrationValidator
**File**: `build/scripts/validate_mobile_ui_integration.py`
**Language**: python
**Purpose**: Comprehensive validator for mobile UI framework integration
**Architecture**: Central validation system for mobile UI framework integration
**Implementation**: Validates all aspects of mobile UI framework integration with Unhinged

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

## Validation Components

### unknown
**File**: `build/scripts/validate_mobile_ui_integration.py`
**Language**: python
**Purpose**: Comprehensive validation script for mobile UI framework integration
**Architecture**: Validation script for mobile UI framework in Unhinged build system
**Implementation**: Validates complete mobile UI framework integration with Unhinged architecture

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
**File**: `build/modules/mobile_ui_builder.py`
**Language**: python
**Purpose**: Mobile UI Builder - Build system integration for mobile-responsive UI components
**Architecture**: Build system module for mobile UI framework integration in Unhinged architecture
**Implementation**: Generates CSS themes, validates responsive layouts, and integrates mobile UI framework

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

## Builder Components

### MobileUIBuilder
**File**: `build/modules/mobile_ui_builder.py`
**Language**: python
**Purpose**: Build system integration for mobile UI framework
**Architecture**: Core build module for mobile UI framework in Unhinged build system
**Implementation**: Handles CSS generation, asset compilation, and responsive layout validation

## Method Components

### build
**File**: `build/modules/mobile_ui_builder.py`
**Language**: python
**Purpose**: Main build process for mobile UI framework
**Architecture**: Primary build entry point for mobile UI components
**Implementation**: Orchestrates CSS generation, validation, and asset compilation

### _generate_css_themes
**File**: `build/modules/mobile_ui_builder.py`
**Language**: python
**Purpose**: Generate CSS themes for mobile UI components
**Architecture**: Generates CSS assets for GTK4 application theming
**Implementation**: Creates responsive CSS with mobile-first design principles

### _create_viewport_widget
**File**: `control/native_gui/tools/input_capture/tool.py`
**Language**: python
**Purpose**: Create viewport-specific widget for input capture tool
**Architecture**: Implements responsive design patterns for input monitoring interface
**Implementation**: Provides optimized layouts for mobile, tablet, and desktop viewports

### create_widget
**File**: `control/native_gui/core/tool_manager.py`
**Language**: python
**Purpose**: Create viewport-specific widget for the tool
**Architecture**: Core method for tool widget instantiation with viewport awareness
**Implementation**: Enhanced widget creation with responsive design support

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

## Architectural Components



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

### unknown
**File**: `control/native_gui/launcher.py`
**Language**: python
**Purpose**: launcher.py - system control component
**Architecture**: Part of the Unhinged system architecture
**Implementation**: Core functionality for launcher

### unknown
**File**: `control/native_gui/__init__.py`
**Language**: python
**Purpose**: __init__.py - system control component
**Architecture**: Part of the Unhinged system architecture
**Implementation**: Core functionality for __init__

### unknown
**File**: `control/native_gui/main_window.py`
**Language**: python
**Purpose**: main_window.py - system control component
**Architecture**: Part of the Unhinged system architecture
**Implementation**: Core functionality for main_window

### unknown
**File**: `control/native_gui/bridge/__init__.py`
**Language**: python
**Purpose**: __init__.py - system control component
**Architecture**: Part of the Unhinged system architecture
**Implementation**: Core functionality for __init__

### unknown
**File**: `control/native_gui/bridge/grpc_client.py`
**Language**: python
**Purpose**: grpc_client.py - system control component
**Architecture**: Part of the Unhinged system architecture
**Implementation**: Core functionality for grpc_client

### unknown
**File**: `control/native_gui/bridge/http_client.py`
**Language**: python
**Purpose**: http_client.py - system control component
**Architecture**: Part of the Unhinged system architecture
**Implementation**: Core functionality for http_client

### unknown
**File**: `control/native_gui/bridge/proto_scanner.py`
**Language**: python
**Purpose**: proto_scanner.py - system control component
**Architecture**: Part of the Unhinged system architecture
**Implementation**: Core functionality for proto_scanner

### unknown
**File**: `control/native_gui/health/__init__.py`
**Language**: python
**Purpose**: __init__.py - system control component
**Architecture**: Part of the Unhinged system architecture
**Implementation**: Core functionality for __init__

### unknown
**File**: `control/native_gui/tools/__init__.py`
**Language**: python
**Purpose**: __init__.py - system control component
**Architecture**: Part of the Unhinged system architecture
**Implementation**: Core functionality for __init__

### unknown
**File**: `control/native_gui/tools/chat/__init__.py`
**Language**: python
**Purpose**: __init__.py - system control component
**Architecture**: Part of the Unhinged system architecture
**Implementation**: Core functionality for __init__

### unknown
**File**: `control/native_gui/tools/chat/tool.py`
**Language**: python
**Purpose**: tool.py - system control component
**Architecture**: Part of the Unhinged system architecture
**Implementation**: Core functionality for tool

### unknown
**File**: `control/native_gui/tools/chat/mobile_chat_tool.py`
**Language**: python
**Purpose**: mobile_chat_tool.py - system control component
**Architecture**: Part of the Unhinged system architecture
**Implementation**: Core functionality for mobile_chat_tool

### unknown
**File**: `control/native_gui/tools/chat/bridge/__init__.py`
**Language**: python
**Purpose**: __init__.py - system control component
**Architecture**: Part of the Unhinged system architecture
**Implementation**: Core functionality for __init__

### unknown
**File**: `control/native_gui/tools/chat/bridge/speech_client.py`
**Language**: python
**Purpose**: speech_client.py - system control component
**Architecture**: Part of the Unhinged system architecture
**Implementation**: Core functionality for speech_client

### unknown
**File**: `control/native_gui/tools/chat/widgets/chat_interface.py`
**Language**: python
**Purpose**: chat_interface.py - system control component
**Architecture**: Part of the Unhinged system architecture
**Implementation**: Core functionality for chat_interface

### unknown
**File**: `control/native_gui/tools/chat/widgets/__init__.py`
**Language**: python
**Purpose**: __init__.py - system control component
**Architecture**: Part of the Unhinged system architecture
**Implementation**: Core functionality for __init__

### unknown
**File**: `control/native_gui/tools/service_manager/__init__.py`
**Language**: python
**Purpose**: __init__.py - system control component
**Architecture**: Part of the Unhinged system architecture
**Implementation**: Core functionality for __init__

### unknown
**File**: `control/native_gui/tools/service_manager/tool.py`
**Language**: python
**Purpose**: tool.py - system control component
**Architecture**: Part of the Unhinged system architecture
**Implementation**: Core functionality for tool

### unknown
**File**: `control/native_gui/tools/system_monitor/__init__.py`
**Language**: python
**Purpose**: __init__.py - system control component
**Architecture**: Part of the Unhinged system architecture
**Implementation**: Core functionality for __init__

### unknown
**File**: `control/native_gui/tools/system_monitor/tool.py`
**Language**: python
**Purpose**: tool.py - system control component
**Architecture**: Part of the Unhinged system architecture
**Implementation**: Core functionality for tool

### unknown
**File**: `control/native_gui/tools/file_browser/__init__.py`
**Language**: python
**Purpose**: __init__.py - system control component
**Architecture**: Part of the Unhinged system architecture
**Implementation**: Core functionality for __init__

### unknown
**File**: `control/native_gui/tools/file_browser/tool.py`
**Language**: python
**Purpose**: tool.py - system control component
**Architecture**: Part of the Unhinged system architecture
**Implementation**: Core functionality for tool

### unknown
**File**: `control/native_gui/tools/api_dev/__init__.py`
**Language**: python
**Purpose**: __init__.py - system control component
**Architecture**: Part of the Unhinged system architecture
**Implementation**: Core functionality for __init__

### unknown
**File**: `control/native_gui/tools/api_dev/tool.py`
**Language**: python
**Purpose**: tool.py - system control component
**Architecture**: Part of the Unhinged system architecture
**Implementation**: Core functionality for tool

### unknown
**File**: `control/native_gui/tools/api_dev/bridge/reflection_client.py`
**Language**: python
**Purpose**: reflection_client.py - system control component
**Architecture**: Part of the Unhinged system architecture
**Implementation**: Core functionality for reflection_client

### unknown
**File**: `control/native_gui/tools/api_dev/bridge/__init__.py`
**Language**: python
**Purpose**: __init__.py - system control component
**Architecture**: Part of the Unhinged system architecture
**Implementation**: Core functionality for __init__

### unknown
**File**: `control/native_gui/tools/api_dev/bridge/network_scanner.py`
**Language**: python
**Purpose**: network_scanner.py - system control component
**Architecture**: Part of the Unhinged system architecture
**Implementation**: Core functionality for network_scanner

### unknown
**File**: `control/native_gui/tools/api_dev/bridge/grpc_client.py`
**Language**: python
**Purpose**: grpc_client.py - system control component
**Architecture**: Part of the Unhinged system architecture
**Implementation**: Core functionality for grpc_client

### unknown
**File**: `control/native_gui/tools/api_dev/bridge/http_client.py`
**Language**: python
**Purpose**: http_client.py - system control component
**Architecture**: Part of the Unhinged system architecture
**Implementation**: Core functionality for http_client

### unknown
**File**: `control/native_gui/tools/api_dev/widgets/__init__.py`
**Language**: python
**Purpose**: __init__.py - system control component
**Architecture**: Part of the Unhinged system architecture
**Implementation**: Core functionality for __init__

### unknown
**File**: `control/native_gui/tools/api_dev/widgets/schema_validator.py`
**Language**: python
**Purpose**: schema_validator.py - system control component
**Architecture**: Part of the Unhinged system architecture
**Implementation**: Core functionality for schema_validator

### unknown
**File**: `control/native_gui/tools/api_dev/widgets/response_viewer.py`
**Language**: python
**Purpose**: response_viewer.py - system control component
**Architecture**: Part of the Unhinged system architecture
**Implementation**: Core functionality for response_viewer

### unknown
**File**: `control/native_gui/tools/api_dev/widgets/request_builder.py`
**Language**: python
**Purpose**: request_builder.py - system control component
**Architecture**: Part of the Unhinged system architecture
**Implementation**: Core functionality for request_builder

### unknown
**File**: `control/native_gui/tools/api_dev/widgets/proto_browser.py`
**Language**: python
**Purpose**: proto_browser.py - system control component
**Architecture**: Part of the Unhinged system architecture
**Implementation**: Core functionality for proto_browser

### unknown
**File**: `control/native_gui/tools/log_viewer/__init__.py`
**Language**: python
**Purpose**: __init__.py - system control component
**Architecture**: Part of the Unhinged system architecture
**Implementation**: Core functionality for __init__

### unknown
**File**: `control/native_gui/tools/log_viewer/tool.py`
**Language**: python
**Purpose**: tool.py - system control component
**Architecture**: Part of the Unhinged system architecture
**Implementation**: Core functionality for tool

### unknown
**File**: `control/native_gui/core/tool_manager.py`
**Language**: python
**Purpose**: tool_manager.py - Enhanced tool management with mobile-responsive capabilities
**Architecture**: Central component in Unhinged tool architecture, bridges desktop and mobile interfaces
**Implementation**: Core functionality for tool lifecycle, registration, and mobile UI integration

### unknown
**File**: `control/native_gui/core/mobile_components.py`
**Language**: python
**Purpose**: mobile_components.py - system control component
**Architecture**: Part of the Unhinged system architecture
**Implementation**: Core functionality for mobile_components

### unknown
**File**: `control/native_gui/core/viewport_manager.py`
**Language**: python
**Purpose**: viewport_manager.py - system control component
**Architecture**: Part of the Unhinged system architecture
**Implementation**: Core functionality for viewport_manager

### unknown
**File**: `control/native_gui/core/__init__.py`
**Language**: python
**Purpose**: __init__.py - system control component
**Architecture**: Part of the Unhinged system architecture
**Implementation**: Core functionality for __init__

### unknown
**File**: `control/native_gui/core/application.py`
**Language**: python
**Purpose**: application.py - system control component
**Architecture**: Part of the Unhinged system architecture
**Implementation**: Core functionality for application

### unknown
**File**: `control/native_gui/widgets/__init__.py`
**Language**: python
**Purpose**: __init__.py - system control component
**Architecture**: Part of the Unhinged system architecture
**Implementation**: Core functionality for __init__

### unknown
**File**: `control/native_gui/widgets/response_viewer.py`
**Language**: python
**Purpose**: response_viewer.py - system control component
**Architecture**: Part of the Unhinged system architecture
**Implementation**: Core functionality for response_viewer

### unknown
**File**: `control/native_gui/widgets/request_builder.py`
**Language**: python
**Purpose**: request_builder.py - system control component
**Architecture**: Part of the Unhinged system architecture
**Implementation**: Core functionality for request_builder

### unknown
**File**: `control/native_gui/widgets/proto_browser.py`
**Language**: python
**Purpose**: proto_browser.py - system control component
**Architecture**: Part of the Unhinged system architecture
**Implementation**: Core functionality for proto_browser

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

### unknown
**File**: `control/native_gui/health_client.py`
**Language**: python
**Purpose**: gRPC health client for native GUI service discovery and monitoring
**Architecture**: Health client for native GUI to communicate with gRPC services
**Implementation**: Provides health.proto client for checking service status via gRPC

## Data Components

### unknown
**File**: `control/system/operation_result.py`
**Language**: python
**Purpose**: Operation result data model for system control operations
**Architecture**: Result model that will evolve into OS system call return values
**Implementation**: Standardized result format for all system operations with future OS compatibility

## Transcription Components

### unknown
**File**: `control/native_gui/tools/chat/bridge/simple_whisper_server.py`
**Language**: python
**Purpose**: Minimal HTTP server providing Whisper-based speech-to-text transcription
**Architecture**: Backend transcription service in voice-first GUI pipeline architecture
**Implementation**: Pure Python Whisper service with native WAV processing and zero external dependencies

## Web Components

### unknown
**File**: `control/native_gui/tools/chat/bridge/web_speech_bridge.py`
**Language**: python
**Purpose**: WebKit-based bridge for browser Web Speech API integration
**Architecture**: Future enhancement component for browser-native voice transcription
**Implementation**: Embedded browser speech recognition using native Web Speech API capabilities

## Dependency Components

### unknown
**File**: `control/native_gui/tools/chat/bridge/audio_installer.py`
**Language**: python
**Purpose**: Automated audio dependency installation and setup guidance system
**Architecture**: Support component providing installation guidance for voice transcription pipeline
**Implementation**: Cross-platform audio dependency detection, installation, and user guidance

## Audio Components

### unknown
**File**: `control/native_gui/tools/chat/bridge/native_audio_capture.py`
**Language**: python
**Purpose**: Native Ubuntu audio capture using system-level ALSA/PipeWire integration
**Architecture**: Core audio input component bridging GUI voice interface to Whisper transcription service
**Implementation**: System audio capture without Python library dependencies for voice transcription pipeline

### unknown
**File**: `control/native_gui/tools/chat/bridge/simple_audio_capture.py`
**Language**: python
**Purpose**: Python speech_recognition library bridge to Whisper service integration
**Architecture**: Intermediate component bridging Python audio libraries to service architecture
**Implementation**: Minimal audio capture using speech_recognition library with Whisper service backend

## Speech Components

### unknown
**File**: `control/native_gui/tools/chat/bridge/native_speech_recognition.py`
**Language**: python
**Purpose**: Python speech_recognition library integration as fallback for voice transcription
**Architecture**: Fallback component in voice transcription pipeline when native audio unavailable
**Implementation**: Multi-backend speech recognition with Google Web Speech API and offline options

## Integration Components

### BuildSystemIntegration
**File**: `control/native_gui/tools/api_dev/bridge/build_integration.py`
**Language**: python
**Purpose**: Build system integration for API development tool
**Architecture**: Central integration point for build operations in API development workflow
**Implementation**: Provides integration between API dev tool and build system

## Module Components

### unknown
**File**: `control/native_gui/tools/input_capture/__init__.py`
**Language**: python
**Purpose**: Input Capture Tool Module - Advanced input monitoring and analysis
**Architecture**: Input capture tool module in the Unhinged tool architecture
**Implementation**: Provides comprehensive keyboard and mouse capture with privacy controls

## Tool Components

### unknown
**File**: `control/native_gui/tools/input_capture/tool.py`
**Language**: python
**Purpose**: Input Capture Tool - Advanced input monitoring and analysis
**Architecture**: Integrates input capture system with the Unhinged tool architecture
**Implementation**: Provides comprehensive keyboard and mouse capture with privacy controls

### InputCaptureTool
**File**: `control/native_gui/tools/input_capture/tool.py`
**Language**: python
**Purpose**: Advanced input capture tool with mobile-responsive interface
**Architecture**: Core tool for input capture functionality in the Unhinged system
**Implementation**: Provides comprehensive input monitoring, analysis, and privacy controls

### unknown
**File**: `control/native_gui/core/tool_config.py`
**Language**: python
**Purpose**: Tool Configuration System - Standardized tool initialization and metadata
**Architecture**: Central tool configuration component in Unhinged native GUI architecture
**Implementation**: Provides unified tool configuration to eliminate duplicate initialization patterns

## Factory Components

### create_tool
**File**: `control/native_gui/tools/input_capture/tool.py`
**Language**: python
**Purpose**: Factory function for creating InputCaptureTool instances
**Architecture**: Entry point for tool registration in the Unhinged tool manager
**Implementation**: Required by the tool plugin system for automatic tool discovery

### ToolConfigFactory
**File**: `control/native_gui/core/tool_config.py`
**Language**: python
**Purpose**: Factory for creating standardized tool configurations
**Architecture**: Central factory for tool configuration creation in Unhinged native GUI
**Implementation**: Provides convenient methods for creating common tool configuration patterns

### WidgetFactory
**File**: `control/native_gui/ui/widget_factory.py`
**Language**: python
**Purpose**: Factory for creating standardized GTK4 widgets
**Architecture**: Central widget factory for Unhinged native GUI with consistent styling
**Implementation**: Eliminates duplicate widget creation patterns across tools

## Theme Components

### unknown
**File**: `control/native_gui/core/theme_manager.py`
**Language**: python
**Purpose**: Enhanced Theme Manager - Unified theming system with mobile-responsive CSS support
**Architecture**: Central theming component in Unhinged native GUI architecture
**Implementation**: Manages GTK4 themes, mobile-responsive styles, and dynamic theme switching

## Manager Components

### ThemeManager
**File**: `control/native_gui/core/theme_manager.py`
**Language**: python
**Purpose**: Enhanced theme manager with mobile-responsive capabilities
**Architecture**: Central theming system for Unhinged native GUI with mobile support
**Implementation**: Manages GTK4 themes, CSS loading, and responsive design adaptation

## Base Components

### BaseTool
**File**: `control/native_gui/core/tool_manager.py`
**Language**: python
**Purpose**: Enhanced base class for all tools with mobile-responsive capabilities
**Architecture**: Foundation of the tool plugin system, supports both desktop and mobile interfaces
**Implementation**: Provides standardized interface for tool creation with viewport adaptation

## Css Components

### unknown
**File**: `control/native_gui/core/css_generator.py`
**Language**: python
**Purpose**: Shared CSS Generator - Consolidated CSS generation for mobile UI framework
**Architecture**: Central CSS generation component in Unhinged native GUI architecture
**Implementation**: Provides unified CSS generation logic to eliminate duplication across theme and build systems

## Generator Components

### CSSGenerator
**File**: `control/native_gui/core/css_generator.py`
**Language**: python
**Purpose**: Unified CSS generator for mobile-responsive UI framework
**Architecture**: Central CSS generation system for Unhinged native GUI with mobile support
**Implementation**: Consolidates CSS generation logic from theme manager and mobile UI builder

## Widget Components

### unknown
**File**: `control/native_gui/ui/widget_factory.py`
**Language**: python
**Purpose**: Widget Factory - Standardized widget creation utilities
**Architecture**: Central widget factory component in Unhinged native GUI architecture
**Implementation**: Provides unified widget creation patterns to eliminate duplicate code

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

## Infrastructure Components

### version
**File**: `orchestration/docker-compose.production.yml`
**Language**: yaml
**Purpose**: Production docker-compose with unified service definitions
**Architecture**: Primary production deployment replacing fragmented compose files
**Implementation**: Single source of truth for production service orchestration

### version
**File**: `orchestration/docker-compose.development.yml`
**Language**: yaml
**Purpose**: Development docker-compose with debug tools and hot-reload
**Architecture**: Development deployment with additional observability services
**Implementation**: Development environment with debugging and monitoring tools
