# 🏛️ Code Philosophy - Unhinged Platform

> **Purpose**: Fundamental design principles extracted from codebase
> **Source**: Auto-generated from evolved LlmDocs format
> **Last Updated**: 2025-10-28 22:33:14

## 🎯 Critical Business Rules

These are the non-negotiable constraints that guide all development:

### unknown (python)
**File**: `build/orchestrator.py`
**Rule**: build operations must be deterministic, cacheable, and provide clear feedback...
**Context**: enhanced build orchestrator for unhinged polyglot monorepo

### unknown (python)
**File**: `build/monitoring.py`
**Rule**: performance monitoring must be lightweight and provide actionable insights fo...
**Context**: build performance monitoring and metrics collection system

### unknown (python)
**File**: `build/build.py`
**Rule**: build system must be simple, fast, and provide clear feedback
**Context**: main entry point for the unhinged build

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
**Rule**: python environment must be reproducible, comprehensive, and big data ready
**Context**: python environment setup for unhinged on-premise ml/ai

### UnhingedPythonSetup (python)
**File**: `build/python/setup.py`
**Rule**: environment setup must be reproducible, comprehensive, and failure-resistant
**Context**: comprehensive python environment setup for ml/ai etl

### test_parse_llm_tags_with_context (python)
**File**: `build/docs-generation/test_llm_extraction.py`
**Rule**: never trust user input
**Context**: user input

### unknown (python)
**File**: `build/tools/dead-code-analyzer.py`
**Rule**: dead code analysis must be conservative to avoid deleting functional code
**Context**: comprehensive dead code and cruft detection tool

### unknown (python)
**File**: `build/tools/cleanup-dead-code.py`
**Rule**: cleanup operations must be reversible and include comprehensive safety checks
**Context**: safe dead code cleanup tool with backup

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
**Rule**: c builds must be deterministic, fast, and provide direct cpu instruction acce...
**Context**: c/c++ build module with cmake integration and

### unknown (python)
**File**: `build/modules/service_discovery_builder.py`
**Rule**: service discovery must happen at build time to ensure html dashboard is alway...
**Context**: service discovery build module for compile-time service

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
**Rule**: gradle builds must be deterministic and support incremental compilation for f...
**Context**: kotlin/gradle build module with incremental compilation and

### unknown (python)
**File**: `build/validators/port_validator.py`
**Rule**: port conflicts must be resolved at build time, never at runtime
**Context**: port conflict detection and resolution at build

### unknown (python)
**File**: `build/validators/resource_validator.py`
**Rule**: resource issues must be detected at build time, never at runtime
**Context**: resource requirement validation at build time

### unknown (python)
**File**: `build/validators/polyglot_validator.py`
**Rule**: all validation must be fast, parallel, actionable, and educational
**Context**: polyglot validation system for enforcing unhinged codebase

### unknown (python)
**File**: `build/validators/dependency_validator.py`
**Rule**: dependency issues must be resolved at build time, never at runtime
**Context**: dependency validation at build time to prevent

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
- **unknown**: python environment operations and execution management (`build/python/run.py`)
- **UnhingedPythonSetup**: comprehensive python environment setup for ml/ai etl (`build/python/setup.py`)
- **LLMContextWarmer**: structured context summaries for new llm agents (`build/docs-generation/llm-context-warmer.py`)
- **unknown**: tdd test suite ensuring extraction and validation (`build/docs-generation/test_llm_extraction.py`)
- **TestLLMContextWarmerImprovements**: test suite for llm context warmer improvements (`build/docs-generation/test_llm_extraction.py`)
- ... and 42 more

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
- **unknown**: enhanced cli interface for the unhinged build (`build/cli.py`)
- **unknown**: enhanced build orchestrator for unhinged polyglot monorepo (`build/orchestrator.py`)
- **unknown**: build performance monitoring and metrics collection system (`build/monitoring.py`)
- **unknown**: developer experience enhancements for the enhanced build (`build/developer_experience.py`)
- ... and 17 more

### service.launcher
- **unknown**: speech-to-text service launcher with grpc health.proto im... (`services/speech-to-text/main.py`)
- **unknown**: text-to-speech service launcher with grpc health.proto im... (`services/text-to-speech/main.py`)
- **unknown**: vision ai service launcher with grpc health.proto (`services/vision-ai/main.py`)

### service.shared
- **unknown**: shared service utilities and base classes for (`services/shared/__init__.py`)

### service.util
- **unknown**: shared utilities for service path management and (`services/shared/paths.py`)

### util.executor
- **UnhingedPythonRunner**: centralized python execution engine for ml/ai etl (`build/python/run.py`)

### util.function
- **generate_project_overview**: comprehensive project overview from extracted comments (`build/docs-generation/llm-context-warmer.py`)
- **_extract_key_components**: extract key system components with improved name (`build/docs-generation/llm-context-warmer.py`)
- **paginate_comments**: paginated access to all extracted comments for (`build/docs-generation/llm-context-warmer.py`)
- **_improve_element_name**: improve element name detection from file paths (`build/docs-generation/llm-context-warmer.py`)
- **_find_related_services**: find related services through port references, api (`build/docs-generation/llm-context-warmer.py`)
- ... and 26 more

### util.migrator
- **unknown**: transforms 8-tag LlmDocs to 3-tag evolved format (`.llmdocs-backup/build/tools/llmdocs-evolution-engine.py`)

### util.setup
- **unknown**: python environment setup for unhinged on-premise ml/ai (`build/python/setup.py`)

### util.tool
- **unknown**: llm context warming system for onboarding new (`build/docs-generation/llm-context-warmer.py`)

### util.validator
- **test_parse_llm_tags_with_context**: user input (`build/docs-generation/test_llm_extraction.py`)
- **unknown**: kotlin-specific validation for build patterns and code (`build/validators/kotlin_validator.py`)
- **KotlinValidator**: kotlin-specific validation for build patterns and code (`build/validators/kotlin_validator.py`)
- **FilePatternValidator**: file creation patterns and prevents scattered cruft (`build/validators/polyglot_validator.py`)
- **GeneratedContentValidator**: that generated content is properly located in (`build/validators/polyglot_validator.py`)
- ... and 4 more

### {llm_type}
- **unknown**: {purpose} (`build/tools/llm-docs-enforcer.py`)
- **unknown**: {purpose} (`build/tools/llm-docs-enforcer.py`)
