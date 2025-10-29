# 🏛️ Code Philosophy - Unhinged Platform

> **Purpose**: Fundamental design principles extracted from codebase
> **Source**: Auto-generated from evolved LlmDocs format
> **Last Updated**: 2025-10-28 22:48:24

## 🎯 Critical Business Rules

These are the non-negotiable constraints that guide all development:

### unknown (python)
**File**: `build/orchestrator.py`
**Rule**: builds must be deterministic and provide comprehensive error reporting
**Context**: polyglot build orchestration with dependency resolution and intelligent caching

### unknown (python)
**File**: `build/monitoring.py`
**Rule**: performance monitoring must be lightweight and provide actionable insights
**Context**: build performance monitoring and metrics collection system

### unknown (python)
**File**: `build/build.py`
**Rule**: build system must be simple, fast, and provide clear feedback
**Context**: main entry point for the unhinged build system

### unknown (python)
**File**: `build/python/run.py`
**Rule**: all execution must be reproducible and pipeline ready
**Context**: python environment operations and execution management

### UnhingedPythonRunner (python)
**File**: `build/python/run.py`
**Rule**: python execution must be reproducible, environment-aware, and big data ready
**Context**: centralized python execution engine for ml/ai etl

### unknown (python)
**File**: `build/python/setup.py`
**Rule**: python environment must be isolated and reproducible across platforms
**Context**: python environment setup and dependency management for build system

### UnhingedPythonSetup (python)
**File**: `build/python/setup.py`
**Rule**: environment setup must be reproducible, comprehensive, and failure-resistant
**Context**: comprehensive python environment setup for ml/ai etl

### test_parse_llm_tags_with_context (python)
**File**: `build/docs-generation/test_llm_extraction.py`
**Rule**: never trust user input
**Context**: user input

### unknown (python)
**File**: `build/docs-generation/extract-llm-comments.py`
**Rule**: extraction must be comprehensive and handle all supported file types
**Context**: llmdocs extraction and documentation generation from polyglot codebase

### unknown (python)
**File**: `build/docs-generation/generate-project-structure.py`
**Rule**: structure documentation must be accurate and reflect current state
**Context**: project structure documentation generation from filesystem analysis

### unknown (python)
**File**: `build/docs-generation/validate-llm-comments.py`
**Rule**: validation must enforce evolved format standards and provide actionable feedback
**Context**: llmdocs validation and quality assurance for evolved format compliance

### unknown (python)
**File**: `build/tools/dead-code-analyzer.py`
**Rule**: dead code analysis must be conservative to prevent accidental removal
**Context**: dead code detection and removal recommendations across polyglot codebase

### unknown (python)
**File**: `build/tools/cleanup-dead-code.py`
**Rule**: cleanup operations must be reversible and logged for safety
**Context**: automated dead code cleanup with safety checks and rollback capability

### unknown (python)
**File**: `build/tools/llm-docs-enforcer.py`
**Rule**: all code files must have proper llmdocs tags for ai comprehension
**Context**: llmdocs enforcement and template generation for evolved format

### RegistryBuilder (python)
**File**: `build/modules/registry_builder.py`
**Rule**: registry must be generated before browser access to ensure accurate file disc...
**Context**: javascript registry of static html files for

### unknown (python)
**File**: `build/modules/registry_builder.py`
**Rule**: registry must be regenerated whenever html files are added/removed/modified
**Context**: global registry of static html files for

### unknown (python)
**File**: `build/modules/proto_client_builder.py`
**Rule**: client libraries must be generated before service compilation and provide typ...
**Context**: proto-to-polyglot client library generation module using ...

### unknown (python)
**File**: `build/modules/c_builder.py`
**Rule**: c builds must be deterministic and provide direct cpu instruction access
**Context**: c/c++ builds with cmake integration and SIMD optimization

### unknown (python)
**File**: `build/modules/service_discovery_builder.py`
**Rule**: service discovery must happen at build time for dashboard consistency
**Context**: service discovery registry generation from docker-compose and proto files

### ServiceDiscoveryBuilder (python)
**File**: `build/modules/service_discovery_builder.py`
**Rule**: service registry must be generated before html dashboard access
**Context**: build-time service discovery module following existing bu...

### unknown (python)
**File**: `build/modules/c_proto_handler.py`
**Rule**: c++ proto clients must provide maximum performance for system-level services
**Context**: c/c++ protobuf client generation handler for high-perform...

### unknown (python)
**File**: `build/modules/kotlin_builder.py`
**Rule**: gradle builds must be deterministic and support incremental compilation
**Context**: kotlin/gradle builds with incremental compilation and parallel execution

### unknown (python)
**File**: `build/validators/port_validator.py`
**Rule**: port conflicts must be resolved at build time, never at runtime
**Context**: port conflict detection and auto-resolution across docker-compose files

### unknown (python)
**File**: `build/validators/resource_validator.py`
**Rule**: resource allocation must be validated at build time to prevent runtime failures
**Context**: resource allocation validation for memory, disk, and cpu limits

### unknown (python)
**File**: `build/validators/polyglot_validator.py`
**Rule**: all validation must be fast, parallel, actionable, and educational
**Context**: polyglot validation system for enforcing unhinged codebase

### unknown (python)
**File**: `build/validators/dependency_validator.py`
**Rule**: dependency conflicts must be resolved at build time to prevent runtime failures
**Context**: dependency validation and conflict resolution across package managers

### unknown (python)
**File**: `.llmdocs-backup/build/tools/llmdocs-evolution-engine.py`
**Rule**: must preserve semantic meaning while eliminating redundancy
**Context**: transforms 8-tag LlmDocs to 3-tag evolved format

### unknown (python)
**File**: `services/shared/__init__.py`
**Rule**: shared service code must be simple, reusable, and eliminate duplication
**Context**: shared service utilities and base classes for

### unknown (python)
**File**: `services/shared/paths.py`
**Rule**: service utilities must be simple, reusable, and eliminate path hardcoding
**Context**: shared utilities for service path management and

### ServicePaths (python)
**File**: `services/shared/paths.py`
**Rule**: service paths must be consistent, predictable, and environment-agnostic
**Context**: service path manager providing standardized directory access

### unknown (python)
**File**: `control/conversation_cli.py`
**Rule**: voice-first interaction must be immediate, natural, and work seamlessly acros...
**Context**: conversation-based cli interface for unhinged dual-system...

### unknown (python)
**File**: `control/deployment/deploy.py`
**Rule**: deployments must be atomic, reversible, and health-validated for operational ...
**Context**: unified deployment orchestrator for unhinged system runtime

### UnhingedDeploymentOrchestrator (python)
**File**: `control/deployment/deploy.py`
**Rule**: all deployments must be atomic, health-validated, and reversible
**Context**: central deployment orchestrator managing environment-awar...

### unknown (python)
**File**: `control/deployment/health-checks.py`
**Rule**: service health must be continuously monitored with automatic recovery actions
**Context**: service health monitoring and validation for unhinged

### UnhingedHealthMonitor (python)
**File**: `control/deployment/health-checks.py`
**Rule**: health monitoring must be continuous, accurate, and trigger automatic recovery
**Context**: continuous health monitoring system for unhinged service

### unknown (python)
**File**: `control/system/__init__.py`
**Rule**: all system operations must be auditable, reversible, and provide clear operat...
**Context**: system control abstraction layer package for unhinged

### unknown (python)
**File**: `control/system/system_controller.py`
**Rule**: all system operations must be auditable, reversible, and provide clear operat...
**Context**: system control abstraction layer that bridges build

### unknown (python)
**File**: `libs/design_system/build/design_token_builder.py`
**Rule**: design tokens must be generated before ui compilation and provide consistent ...
**Context**: design token generation module following protoclientbuild...

### unknown (python)
**File**: `libs/design_system/build/component_validator.py`
**Rule**: all component specifications must be validated before generator consumption
**Context**: component specification validator ensuring yaml specs con...

### schema_version (yaml)
**File**: `libs/design_system/components/_schema.yaml`
**Rule**: component specifications must be platform-agnostic and describe what not how
**Context**: component specification meta-schema defining platform-agn...

### component (yaml)
**File**: `libs/design_system/components/primitives/modal.yaml`
**Rule**: modal specifications must be platform-agnostic describing semantic behavior n...
**Context**: platform-agnostic modal dialog component specification fo...

### component (yaml)
**File**: `libs/design_system/components/primitives/input.yaml`
**Rule**: input specifications must be platform-agnostic describing semantic behavior n...
**Context**: platform-agnostic input field component specification for...

### component (yaml)
**File**: `libs/design_system/components/primitives/button.yaml`
**Rule**: button specifications must be platform-agnostic describing what not how
**Context**: platform-agnostic button component specification defining...

## 📚 Component Catalog

System components organized by type and function:

### component.primitive
- **test_extract_llm_context_from_typescript**: react component for user authentication (`build/docs-generation/test_llm_extraction.py`)
- **ComponentSpecificationValidator**: core validator implementing comprehensive component speci... (`libs/design_system/build/component_validator.py`)
- **ComponentBuildModule**: component generation build module implementing buildmodul... (`libs/design_system/build/component_build_module.py`)

### component.spec
- **component**: platform-agnostic modal dialog component specification fo... (`libs/design_system/components/primitives/modal.yaml`)
- **component**: platform-agnostic input field component specification for... (`libs/design_system/components/primitives/input.yaml`)
- **component**: platform-agnostic button component specification defining... (`libs/design_system/components/primitives/button.yaml`)
- **component**: minimal button component specification for testing component (`libs/design_system/components/primitives/simple-button.yaml`)

### config.app
- **version**: ci/cd pipeline configuration integrating with enhanced build (`build/ci/ci-config.yml`)
- **version**: main build configuration for unhinged platform (`build/config/build-config.yml`)
- **environment**: production environment settings for unhinged system deplo... (`control/config/environments/production.yml`)
- **environment**: development environment settings for unhinged system deve... (`control/config/environments/development.yml`)
- **persistence_platform**: persistence-platform.yaml - platform infrastructure compo... (`platforms/persistence/config/persistence-platform.yaml`)

### config.build
- **UnhingedPythonSetup**: comprehensive python environment setup for ml/ai etl (`build/python/setup.py`)
- **LLMContextWarmer**: structured context summaries for new llm agents (`build/docs-generation/llm-context-warmer.py`)
- **unknown**: tdd test suite ensuring extraction and validation (`build/docs-generation/test_llm_extraction.py`)
- **TestLLMContextWarmerImprovements**: test suite for llm context warmer improvements (`build/docs-generation/test_llm_extraction.py`)
- **test_element_name_detection_from_service_path**: test element name extraction from services directory (`build/docs-generation/test_llm_extraction.py`)
- ... and 34 more

### misc.control-monitor
- **UnhingedHealthMonitor**: continuous health monitoring system for unhinged service (`control/deployment/health-checks.py`)

### misc.control-orchestrator
- **UnhingedDeploymentOrchestrator**: central deployment orchestrator managing environment-awar... (`control/deployment/deploy.py`)

### misc.control-plane
- **unknown**: system control abstraction layer that bridges build (`control/system/system_controller.py`)

### misc.control-plane-package
- **unknown**: system control abstraction layer package for unhinged (`control/system/__init__.py`)

### misc.control-system
- **unknown**: __init__.py - network control system module initialization (`control/network/__init__.py`)

### misc.control-tool
- **unknown**: unified deployment orchestrator for unhinged system runtime (`control/deployment/deploy.py`)
- **unknown**: service health monitoring and validation for unhinged (`control/deployment/health-checks.py`)

### misc.platform
- **version**: docker-compose.yml - platform infrastructure component (`platforms/persistence/docker-compose.yml`)

### misc.virtualization-boundary
- **unknown**: http proxy server that represents the line-in-the-sand (`control/proxy_server.py`)

### model.config
- **unknown**: global registry of static html files for (`build/modules/registry_builder.py`)

### model.entity
- **ValidationResult**: result from a validation check with severity, (`build/validators/polyglot_validator.py`)
- **ValidationSummary**: summary of all validation results with metrics (`build/validators/polyglot_validator.py`)
- **unknown**: operation result data model for system control (`control/system/operation_result.py`)

### model.schema
- **schema_version**: component specification meta-schema defining platform-agn... (`libs/design_system/components/_schema.yaml`)

### service.api
- **unknown**: llm integration for enhanced build system with context generation (`build/llm_integration.py`)
- **unknown**: developer experience enhancements for the enhanced build (`build/developer_experience.py`)
- **test_extract_llm_context_from_python**: user requests (`build/docs-generation/test_llm_extraction.py`)
- **unknown**: dual-system desktop application build module for ci/cd (`build/modules/dual_system_builder.py`)
- **ServicePaths**: service path manager providing standardized directory access (`services/shared/paths.py`)
- ... and 9 more

### service.builder
- **unknown**: typescript/npm builds with webpack optimization and hot reloading (`build/modules/typescript_builder.py`)
- **unknown**: c/c++ builds with cmake integration and SIMD optimization (`build/modules/c_builder.py`)
- **unknown**: python builds with virtual environment and dependency management (`build/modules/python_builder.py`)
- **unknown**: service discovery registry generation from docker-compose and proto files (`build/modules/service_discovery_builder.py`)
- **unknown**: polyglot protobuf client generation for multiple languages (`build/modules/polyglot_proto_engine.py`)
- ... and 1 more

### service.cli
- **unknown**: enhanced cli interface for the unhinged build system (`build/cli.py`)

### service.framework
- **unknown**: build module framework with abstract base classes and registry (`build/modules/__init__.py`)

### service.launcher
- **unknown**: main entry point for the unhinged build system (`build/build.py`)
- **unknown**: speech-to-text service launcher with grpc health.proto im... (`services/speech-to-text/main.py`)
- **unknown**: text-to-speech service launcher with grpc health.proto im... (`services/text-to-speech/main.py`)
- **unknown**: vision ai service launcher with grpc health.proto (`services/vision-ai/main.py`)

### service.monitor
- **unknown**: build performance monitoring and metrics collection system (`build/monitoring.py`)

### service.orchestrator
- **unknown**: polyglot build orchestration with dependency resolution and intelligent caching (`build/orchestrator.py`)

### service.shared
- **unknown**: shared service utilities and base classes for (`services/shared/__init__.py`)

### service.util
- **unknown**: shared utilities for service path management and (`services/shared/paths.py`)

### service.validator
- **unknown**: compile-time validation system preventing runtime errors (`build/validators/__init__.py`)

### util.analyzer
- **unknown**: dead code detection and removal recommendations across polyglot codebase (`build/tools/dead-code-analyzer.py`)

### util.cleaner
- **unknown**: automated dead code cleanup with safety checks and rollback capability (`build/tools/cleanup-dead-code.py`)

### util.enforcer
- **unknown**: llmdocs enforcement and template generation for evolved format (`build/tools/llm-docs-enforcer.py`)

### util.executor
- **unknown**: python environment operations and execution management (`build/python/run.py`)
- **UnhingedPythonRunner**: centralized python execution engine for ml/ai etl (`build/python/run.py`)

### util.extractor
- **unknown**: llmdocs extraction and documentation generation from polyglot codebase (`build/docs-generation/extract-llm-comments.py`)

### util.function
- **generate_project_overview**: comprehensive project overview from extracted comments (`build/docs-generation/llm-context-warmer.py`)
- **_extract_key_components**: extract key system components with improved name (`build/docs-generation/llm-context-warmer.py`)
- **paginate_comments**: paginated access to all extracted comments for (`build/docs-generation/llm-context-warmer.py`)
- **_improve_element_name**: improve element name detection from file paths (`build/docs-generation/llm-context-warmer.py`)
- **_find_related_services**: find related services through port references, api (`build/docs-generation/llm-context-warmer.py`)
- ... and 23 more

### util.generator
- **unknown**: project structure documentation generation from filesystem analysis (`build/docs-generation/generate-project-structure.py`)

### util.migrator
- **unknown**: transforms 8-tag LlmDocs to 3-tag evolved format (`.llmdocs-backup/build/tools/llmdocs-evolution-engine.py`)

### util.setup
- **unknown**: python environment setup and dependency management for build system (`build/python/setup.py`)

### util.tool
- **unknown**: llm context warming system for onboarding new (`build/docs-generation/llm-context-warmer.py`)

### util.validator
- **test_parse_llm_tags_with_context**: user input (`build/docs-generation/test_llm_extraction.py`)
- **unknown**: llmdocs validation and quality assurance for evolved format compliance (`build/docs-generation/validate-llm-comments.py`)
- **unknown**: port conflict detection and auto-resolution across docker-compose files (`build/validators/port_validator.py`)
- **unknown**: resource allocation validation for memory, disk, and cpu limits (`build/validators/resource_validator.py`)
- **unknown**: kotlin-specific validation for build patterns and code (`build/validators/kotlin_validator.py`)
- ... and 8 more

### {llm_type}
- **unknown**: {purpose} (`build/tools/llm-docs-enforcer.py`)
- **unknown**: {purpose} (`build/tools/llm-docs-enforcer.py`)
