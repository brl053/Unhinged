# 🏛️ Code Philosophy - Unhinged Platform

> **Purpose**: Fundamental design principles extracted from codebase
> **Source**: Auto-generated from @llm-axiom and @llm-token comments
> **Last Updated**: 2025-10-24 22:33:44

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
**File**: `build/scripts/validate_mobile_ui_integration.py`
**Axiom**: Validation must be thorough, reliable, and provide actionable feedback
**Context**: Comprehensive validation script for mobile UI framework integration

### MobileUIIntegrationValidator (python)
**File**: `build/scripts/validate_mobile_ui_integration.py`
**Axiom**: Validation must be comprehensive and provide actionable feedback
**Context**: Comprehensive validator for mobile UI framework integration

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
**File**: `build/modules/mobile_ui_builder.py`
**Axiom**: Mobile UI must maintain native GTK performance while providing responsive design
**Context**: Mobile UI Builder - Build system integration for mobile-responsive UI components

### MobileUIBuilder (python)
**File**: `build/modules/mobile_ui_builder.py`
**Axiom**: Build process must be deterministic and maintain component independence
**Context**: Build system integration for mobile UI framework

### build (python)
**File**: `build/modules/mobile_ui_builder.py`
**Axiom**: Build must be idempotent and handle incremental updates
**Context**: Main build process for mobile UI framework

### _generate_css_themes (python)
**File**: `build/modules/mobile_ui_builder.py`
**Axiom**: CSS must be valid and follow GTK4 theming conventions
**Context**: Generate CSS themes for mobile UI components

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

### unknown (python)
**File**: `control/native_gui/health_client.py`
**Axiom**: All services must implement health.proto for service discovery
**Context**: gRPC health client for native GUI service discovery and monitoring

### unknown (python)
**File**: `control/native_gui/launcher.py`
**Axiom**: Maintains system independence and architectural compliance
**Context**: launcher.py - system control component

### unknown (python)
**File**: `control/native_gui/__init__.py`
**Axiom**: Maintains system independence and architectural compliance
**Context**: __init__.py - system control component

### unknown (python)
**File**: `control/native_gui/main_window.py`
**Axiom**: Maintains system independence and architectural compliance
**Context**: main_window.py - system control component

### unknown (python)
**File**: `control/native_gui/bridge/__init__.py`
**Axiom**: Maintains system independence and architectural compliance
**Context**: __init__.py - system control component

### unknown (python)
**File**: `control/native_gui/bridge/grpc_client.py`
**Axiom**: Maintains system independence and architectural compliance
**Context**: grpc_client.py - system control component

### unknown (python)
**File**: `control/native_gui/bridge/http_client.py`
**Axiom**: Maintains system independence and architectural compliance
**Context**: http_client.py - system control component

### unknown (python)
**File**: `control/native_gui/bridge/proto_scanner.py`
**Axiom**: Maintains system independence and architectural compliance
**Context**: proto_scanner.py - system control component

### unknown (python)
**File**: `control/native_gui/health/__init__.py`
**Axiom**: Maintains system independence and architectural compliance
**Context**: __init__.py - system control component

### unknown (python)
**File**: `control/native_gui/services/llm_client.py`
**Axiom**: Maintains system independence and architectural compliance
**Context**: llm_client.py - microservice component

### unknown (python)
**File**: `control/native_gui/services/__init__.py`
**Axiom**: Maintains system independence and architectural compliance
**Context**: __init__.py - microservice component

### unknown (python)
**File**: `control/native_gui/tools/__init__.py`
**Axiom**: Maintains system independence and architectural compliance
**Context**: __init__.py - system control component

### unknown (python)
**File**: `control/native_gui/tools/chat/__init__.py`
**Axiom**: Maintains system independence and architectural compliance
**Context**: __init__.py - system control component

### unknown (python)
**File**: `control/native_gui/tools/chat/tool.py`
**Axiom**: Maintains system independence and architectural compliance
**Context**: tool.py - system control component

### unknown (python)
**File**: `control/native_gui/tools/chat/mobile_chat_tool.py`
**Axiom**: Maintains system independence and architectural compliance
**Context**: mobile_chat_tool.py - system control component

### unknown (python)
**File**: `control/native_gui/tools/chat/bridge/simple_whisper_server.py`
**Axiom**: Simple, focused services superior to complex multi-dependency solutions
**Context**: Minimal HTTP server providing Whisper-based speech-to-text transcription

### load_wav_file (python)
**File**: `control/native_gui/tools/chat/bridge/simple_whisper_server.py`
**Axiom**: Pure Python audio processing eliminates ffmpeg dependency complexity

### unknown (python)
**File**: `control/native_gui/tools/chat/bridge/__init__.py`
**Axiom**: Maintains system independence and architectural compliance
**Context**: __init__.py - system control component

### unknown (python)
**File**: `control/native_gui/tools/chat/bridge/web_speech_bridge.py`
**Axiom**: Browser-native APIs provide superior user experience to system-level audio capture
**Context**: WebKit-based bridge for browser Web Speech API integration

### unknown (python)
**File**: `control/native_gui/tools/chat/bridge/audio_installer.py`
**Axiom**: Clear installation guidance reduces user friction in voice feature adoption
**Context**: Automated audio dependency installation and setup guidance system

### unknown (python)
**File**: `control/native_gui/tools/chat/bridge/speech_client.py`
**Axiom**: Maintains system independence and architectural compliance
**Context**: speech_client.py - system control component

### _native_audio_recording (python)
**File**: `control/native_gui/tools/chat/bridge/speech_client.py`
**Axiom**: Native OS audio capabilities superior to Python library abstractions

### unknown (python)
**File**: `control/native_gui/tools/chat/bridge/native_audio_capture.py`
**Axiom**: Native OS capabilities superior to Python library abstractions for audio processing
**Context**: Native Ubuntu audio capture using system-level ALSA/PipeWire integration

### record_and_transcribe (python)
**File**: `control/native_gui/tools/chat/bridge/native_audio_capture.py`
**Axiom**: Native system tools (arecord) provide superior audio capture to Python libraries

### unknown (python)
**File**: `control/native_gui/tools/chat/bridge/native_speech_recognition.py`
**Axiom**: Multiple fallback options ensure voice functionality across diverse system configurations
**Context**: Python speech_recognition library integration as fallback for voice transcription

### unknown (python)
**File**: `control/native_gui/tools/chat/bridge/simple_audio_capture.py`
**Axiom**: Service-oriented architecture enables cross-platform voice transcription deployment
**Context**: Python speech_recognition library bridge to Whisper service integration

### unknown (python)
**File**: `control/native_gui/tools/chat/widgets/chat_interface.py`
**Axiom**: Maintains system independence and architectural compliance
**Context**: chat_interface.py - system control component

### unknown (python)
**File**: `control/native_gui/tools/chat/widgets/__init__.py`
**Axiom**: Maintains system independence and architectural compliance
**Context**: __init__.py - system control component

### unknown (python)
**File**: `control/native_gui/tools/service_manager/__init__.py`
**Axiom**: Maintains system independence and architectural compliance
**Context**: __init__.py - system control component

### unknown (python)
**File**: `control/native_gui/tools/service_manager/tool.py`
**Axiom**: Maintains system independence and architectural compliance
**Context**: tool.py - system control component

### unknown (python)
**File**: `control/native_gui/tools/system_monitor/__init__.py`
**Axiom**: Maintains system independence and architectural compliance
**Context**: __init__.py - system control component

### unknown (python)
**File**: `control/native_gui/tools/system_monitor/tool.py`
**Axiom**: Maintains system independence and architectural compliance
**Context**: tool.py - system control component

### unknown (python)
**File**: `control/native_gui/tools/file_browser/__init__.py`
**Axiom**: Maintains system independence and architectural compliance
**Context**: __init__.py - system control component

### unknown (python)
**File**: `control/native_gui/tools/file_browser/tool.py`
**Axiom**: Maintains system independence and architectural compliance
**Context**: tool.py - system control component

### unknown (python)
**File**: `control/native_gui/tools/api_dev/__init__.py`
**Axiom**: Maintains system independence and architectural compliance
**Context**: __init__.py - system control component

### unknown (python)
**File**: `control/native_gui/tools/api_dev/tool.py`
**Axiom**: Maintains system independence and architectural compliance
**Context**: tool.py - system control component

### unknown (python)
**File**: `control/native_gui/tools/api_dev/bridge/reflection_client.py`
**Axiom**: Maintains system independence and architectural compliance
**Context**: reflection_client.py - system control component

### unknown (python)
**File**: `control/native_gui/tools/api_dev/bridge/__init__.py`
**Axiom**: Maintains system independence and architectural compliance
**Context**: __init__.py - system control component

### unknown (python)
**File**: `control/native_gui/tools/api_dev/bridge/network_scanner.py`
**Axiom**: Maintains system independence and architectural compliance
**Context**: network_scanner.py - system control component

### unknown (python)
**File**: `control/native_gui/tools/api_dev/bridge/grpc_client.py`
**Axiom**: Maintains system independence and architectural compliance
**Context**: grpc_client.py - system control component

### BuildSystemIntegration (python)
**File**: `control/native_gui/tools/api_dev/bridge/build_integration.py`
**Axiom**: Build operations must be non-blocking and provide real-time feedback
**Context**: Build system integration for API development tool

### unknown (python)
**File**: `control/native_gui/tools/api_dev/bridge/http_client.py`
**Axiom**: Maintains system independence and architectural compliance
**Context**: http_client.py - system control component

### unknown (python)
**File**: `control/native_gui/tools/api_dev/widgets/__init__.py`
**Axiom**: Maintains system independence and architectural compliance
**Context**: __init__.py - system control component

### unknown (python)
**File**: `control/native_gui/tools/api_dev/widgets/schema_validator.py`
**Axiom**: Maintains system independence and architectural compliance
**Context**: schema_validator.py - system control component

### unknown (python)
**File**: `control/native_gui/tools/api_dev/widgets/response_viewer.py`
**Axiom**: Maintains system independence and architectural compliance
**Context**: response_viewer.py - system control component

### unknown (python)
**File**: `control/native_gui/tools/api_dev/widgets/request_builder.py`
**Axiom**: Maintains system independence and architectural compliance
**Context**: request_builder.py - system control component

### unknown (python)
**File**: `control/native_gui/tools/api_dev/widgets/proto_browser.py`
**Axiom**: Maintains system independence and architectural compliance
**Context**: proto_browser.py - system control component

### unknown (python)
**File**: `control/native_gui/tools/input_capture/__init__.py`
**Axiom**: Input monitoring must respect user privacy and provide transparent controls
**Context**: Input Capture Tool Module - Advanced input monitoring and analysis

### unknown (python)
**File**: `control/native_gui/tools/input_capture/tool.py`
**Axiom**: Input monitoring must respect user privacy and provide transparent controls
**Context**: Input Capture Tool - Advanced input monitoring and analysis

### InputCaptureTool (python)
**File**: `control/native_gui/tools/input_capture/tool.py`
**Axiom**: Maintains user privacy while providing valuable input insights
**Context**: Advanced input capture tool with mobile-responsive interface

### _create_viewport_widget (python)
**File**: `control/native_gui/tools/input_capture/tool.py`
**Axiom**: Interface must be functional and accessible across all viewport sizes
**Context**: Create viewport-specific widget for input capture tool

### create_tool (python)
**File**: `control/native_gui/tools/input_capture/tool.py`
**Axiom**: Must return a properly initialized tool instance
**Context**: Factory function for creating InputCaptureTool instances

### unknown (python)
**File**: `control/native_gui/tools/log_viewer/__init__.py`
**Axiom**: Maintains system independence and architectural compliance
**Context**: __init__.py - system control component

### unknown (python)
**File**: `control/native_gui/tools/log_viewer/tool.py`
**Axiom**: Maintains system independence and architectural compliance
**Context**: tool.py - system control component

### unknown (python)
**File**: `control/native_gui/core/theme_manager.py`
**Axiom**: Themes must maintain consistency across desktop and mobile viewports
**Context**: Enhanced Theme Manager - Unified theming system with mobile-responsive CSS support

### ThemeManager (python)
**File**: `control/native_gui/core/theme_manager.py`
**Axiom**: Themes must provide consistent experience across all viewport sizes
**Context**: Enhanced theme manager with mobile-responsive capabilities

### unknown (python)
**File**: `control/native_gui/core/tool_manager.py`
**Axiom**: Tools must support both desktop and mobile viewports while maintaining native GTK performance
**Context**: tool_manager.py - Enhanced tool management with mobile-responsive capabilities

### BaseTool (python)
**File**: `control/native_gui/core/tool_manager.py`
**Axiom**: Tools must gracefully adapt to different screen sizes while maintaining functionality
**Context**: Enhanced base class for all tools with mobile-responsive capabilities

### create_widget (python)
**File**: `control/native_gui/core/tool_manager.py`
**Axiom**: Widgets must adapt to viewport constraints while maintaining functionality
**Context**: Create viewport-specific widget for the tool

### unknown (python)
**File**: `control/native_gui/core/mobile_components.py`
**Axiom**: Maintains system independence and architectural compliance
**Context**: mobile_components.py - system control component

### unknown (python)
**File**: `control/native_gui/core/viewport_manager.py`
**Axiom**: Maintains system independence and architectural compliance
**Context**: viewport_manager.py - system control component

### unknown (python)
**File**: `control/native_gui/core/tool_config.py`
**Axiom**: Tool configuration must be consistent and follow established patterns
**Context**: Tool Configuration System - Standardized tool initialization and metadata

### ToolConfigFactory (python)
**File**: `control/native_gui/core/tool_config.py`
**Axiom**: Factory methods must provide sensible defaults and consistent patterns
**Context**: Factory for creating standardized tool configurations

### unknown (python)
**File**: `control/native_gui/core/__init__.py`
**Axiom**: Maintains system independence and architectural compliance
**Context**: __init__.py - system control component

### unknown (python)
**File**: `control/native_gui/core/css_generator.py`
**Axiom**: CSS generation must be consistent and follow GTK4 theming conventions
**Context**: Shared CSS Generator - Consolidated CSS generation for mobile UI framework

### CSSGenerator (python)
**File**: `control/native_gui/core/css_generator.py`
**Axiom**: CSS generation must be consistent and eliminate duplication
**Context**: Unified CSS generator for mobile-responsive UI framework

### unknown (python)
**File**: `control/native_gui/core/application.py`
**Axiom**: Maintains system independence and architectural compliance
**Context**: application.py - system control component

### unknown (python)
**File**: `control/native_gui/ui/widget_factory.py`
**Axiom**: Widget creation must be consistent and follow GTK4 best practices
**Context**: Widget Factory - Standardized widget creation utilities

### WidgetFactory (python)
**File**: `control/native_gui/ui/widget_factory.py`
**Axiom**: Widget creation must be consistent and follow established patterns
**Context**: Factory for creating standardized GTK4 widgets

### unknown (python)
**File**: `control/native_gui/widgets/__init__.py`
**Axiom**: Maintains system independence and architectural compliance
**Context**: __init__.py - system control component

### unknown (python)
**File**: `control/native_gui/widgets/response_viewer.py`
**Axiom**: Maintains system independence and architectural compliance
**Context**: response_viewer.py - system control component

### unknown (python)
**File**: `control/native_gui/widgets/request_builder.py`
**Axiom**: Maintains system independence and architectural compliance
**Context**: request_builder.py - system control component

### unknown (python)
**File**: `control/native_gui/widgets/proto_browser.py`
**Axiom**: Maintains system independence and architectural compliance
**Context**: proto_browser.py - system control component

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

### version (yaml)
**File**: `orchestration/docker-compose.production.yml`
**Axiom**: All services use categorical port allocation for conflict prevention
**Context**: Production docker-compose with unified service definitions

### version (yaml)
**File**: `orchestration/docker-compose.development.yml`
**Axiom**: Development services include debugging and monitoring capabilities
**Context**: Development docker-compose with debug tools and hot-reload

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
**Definition**: mobile_ui_validation: Complete integration validation for mobile-responsive UI framework
**Source**: `build/scripts/validate_mobile_ui_integration.py` (python)

### MobileUIIntegrationValidator
**Definition**: MobileUIIntegrationValidator: Complete integration validation system
**Source**: `build/scripts/validate_mobile_ui_integration.py` (python)

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
**Definition**: mobile_ui_builder: Build system integration for mobile-first responsive UI framework
**Source**: `build/modules/mobile_ui_builder.py` (python)

### MobileUIBuilder
**Definition**: MobileUIBuilder: Centralized build system for mobile-responsive UI framework
**Source**: `build/modules/mobile_ui_builder.py` (python)

### build
**Definition**: build: Main mobile UI build process
**Source**: `build/modules/mobile_ui_builder.py` (python)

### _generate_css_themes
**Definition**: _generate_css_themes: CSS theme generation for mobile-responsive UI
**Source**: `build/modules/mobile_ui_builder.py` (python)

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

### unknown
**Definition**: health-client: gRPC client for health.proto service discovery
**Source**: `control/native_gui/health_client.py` (python)

### unknown
**Definition**: launcher: system control component
**Source**: `control/native_gui/launcher.py` (python)

### unknown
**Definition**: __init__: system control component
**Source**: `control/native_gui/__init__.py` (python)

### unknown
**Definition**: main_window: system control component
**Source**: `control/native_gui/main_window.py` (python)

### unknown
**Definition**: __init__: system control component
**Source**: `control/native_gui/bridge/__init__.py` (python)

### unknown
**Definition**: grpc_client: system control component
**Source**: `control/native_gui/bridge/grpc_client.py` (python)

### unknown
**Definition**: http_client: system control component
**Source**: `control/native_gui/bridge/http_client.py` (python)

### unknown
**Definition**: proto_scanner: system control component
**Source**: `control/native_gui/bridge/proto_scanner.py` (python)

### unknown
**Definition**: __init__: system control component
**Source**: `control/native_gui/health/__init__.py` (python)

### unknown
**Definition**: llm_client: microservice component
**Source**: `control/native_gui/services/llm_client.py` (python)

### unknown
**Definition**: __init__: microservice component
**Source**: `control/native_gui/services/__init__.py` (python)

### unknown
**Definition**: __init__: system control component
**Source**: `control/native_gui/tools/__init__.py` (python)

### unknown
**Definition**: __init__: system control component
**Source**: `control/native_gui/tools/chat/__init__.py` (python)

### unknown
**Definition**: tool: system control component
**Source**: `control/native_gui/tools/chat/tool.py` (python)

### unknown
**Definition**: mobile_chat_tool: system control component
**Source**: `control/native_gui/tools/chat/mobile_chat_tool.py` (python)

### unknown
**Definition**: whisper-http-server: Lightweight speech transcription service for voice pipeline
**Source**: `control/native_gui/tools/chat/bridge/simple_whisper_server.py` (python)

### unknown
**Definition**: __init__: system control component
**Source**: `control/native_gui/tools/chat/bridge/__init__.py` (python)

### unknown
**Definition**: web-speech-bridge: Browser API integration for voice transcription
**Source**: `control/native_gui/tools/chat/bridge/web_speech_bridge.py` (python)

### unknown
**Definition**: audio-installer: Dependency management for voice transcription components
**Source**: `control/native_gui/tools/chat/bridge/audio_installer.py` (python)

### unknown
**Definition**: speech_client: system control component
**Source**: `control/native_gui/tools/chat/bridge/speech_client.py` (python)

### unknown
**Definition**: native-audio-capture: System-level audio input for voice-first user experience
**Source**: `control/native_gui/tools/chat/bridge/native_audio_capture.py` (python)

### unknown
**Definition**: native-speech-recognition: Python library fallback for voice transcription
**Source**: `control/native_gui/tools/chat/bridge/native_speech_recognition.py` (python)

### unknown
**Definition**: simple-audio-capture: Python library bridge for voice service integration
**Source**: `control/native_gui/tools/chat/bridge/simple_audio_capture.py` (python)

### unknown
**Definition**: chat_interface: system control component
**Source**: `control/native_gui/tools/chat/widgets/chat_interface.py` (python)

### unknown
**Definition**: __init__: system control component
**Source**: `control/native_gui/tools/chat/widgets/__init__.py` (python)

### unknown
**Definition**: __init__: system control component
**Source**: `control/native_gui/tools/service_manager/__init__.py` (python)

### unknown
**Definition**: tool: system control component
**Source**: `control/native_gui/tools/service_manager/tool.py` (python)

### unknown
**Definition**: __init__: system control component
**Source**: `control/native_gui/tools/system_monitor/__init__.py` (python)

### unknown
**Definition**: tool: system control component
**Source**: `control/native_gui/tools/system_monitor/tool.py` (python)

### unknown
**Definition**: __init__: system control component
**Source**: `control/native_gui/tools/file_browser/__init__.py` (python)

### unknown
**Definition**: tool: system control component
**Source**: `control/native_gui/tools/file_browser/tool.py` (python)

### unknown
**Definition**: __init__: system control component
**Source**: `control/native_gui/tools/api_dev/__init__.py` (python)

### unknown
**Definition**: tool: system control component
**Source**: `control/native_gui/tools/api_dev/tool.py` (python)

### unknown
**Definition**: reflection_client: system control component
**Source**: `control/native_gui/tools/api_dev/bridge/reflection_client.py` (python)

### unknown
**Definition**: __init__: system control component
**Source**: `control/native_gui/tools/api_dev/bridge/__init__.py` (python)

### unknown
**Definition**: network_scanner: system control component
**Source**: `control/native_gui/tools/api_dev/bridge/network_scanner.py` (python)

### unknown
**Definition**: grpc_client: system control component
**Source**: `control/native_gui/tools/api_dev/bridge/grpc_client.py` (python)

### BuildSystemIntegration
**Definition**: BuildSystemIntegration: Build system integration for API development workflow
**Source**: `control/native_gui/tools/api_dev/bridge/build_integration.py` (python)

### unknown
**Definition**: http_client: system control component
**Source**: `control/native_gui/tools/api_dev/bridge/http_client.py` (python)

### unknown
**Definition**: __init__: system control component
**Source**: `control/native_gui/tools/api_dev/widgets/__init__.py` (python)

### unknown
**Definition**: schema_validator: system control component
**Source**: `control/native_gui/tools/api_dev/widgets/schema_validator.py` (python)

### unknown
**Definition**: response_viewer: system control component
**Source**: `control/native_gui/tools/api_dev/widgets/response_viewer.py` (python)

### unknown
**Definition**: request_builder: system control component
**Source**: `control/native_gui/tools/api_dev/widgets/request_builder.py` (python)

### unknown
**Definition**: proto_browser: system control component
**Source**: `control/native_gui/tools/api_dev/widgets/proto_browser.py` (python)

### unknown
**Definition**: input_capture_module: Advanced input monitoring tool module
**Source**: `control/native_gui/tools/input_capture/__init__.py` (python)

### unknown
**Definition**: input_capture_tool: Advanced input monitoring tool with mobile-first responsive design
**Source**: `control/native_gui/tools/input_capture/tool.py` (python)

### InputCaptureTool
**Definition**: InputCaptureTool: Advanced input monitoring with mobile-first design
**Source**: `control/native_gui/tools/input_capture/tool.py` (python)

### _create_viewport_widget
**Definition**: _create_viewport_widget: Responsive input capture interface creation
**Source**: `control/native_gui/tools/input_capture/tool.py` (python)

### create_tool
**Definition**: create_tool: Tool factory function for plugin system integration
**Source**: `control/native_gui/tools/input_capture/tool.py` (python)

### unknown
**Definition**: __init__: system control component
**Source**: `control/native_gui/tools/log_viewer/__init__.py` (python)

### unknown
**Definition**: tool: system control component
**Source**: `control/native_gui/tools/log_viewer/tool.py` (python)

### unknown
**Definition**: theme_manager: Enhanced theming system with mobile-responsive CSS integration
**Source**: `control/native_gui/core/theme_manager.py` (python)

### ThemeManager
**Definition**: ThemeManager: Enhanced theming system with mobile-responsive CSS support
**Source**: `control/native_gui/core/theme_manager.py` (python)

### unknown
**Definition**: tool_manager: Enhanced tool management system with mobile-first responsive design
**Source**: `control/native_gui/core/tool_manager.py` (python)

### BaseTool
**Definition**: BaseTool: Enhanced tool base class with mobile-first responsive design
**Source**: `control/native_gui/core/tool_manager.py` (python)

### create_widget
**Definition**: create_widget: Enhanced widget creation with mobile-responsive design
**Source**: `control/native_gui/core/tool_manager.py` (python)

### unknown
**Definition**: mobile_components: system control component
**Source**: `control/native_gui/core/mobile_components.py` (python)

### unknown
**Definition**: viewport_manager: system control component
**Source**: `control/native_gui/core/viewport_manager.py` (python)

### unknown
**Definition**: tool_config: Unified tool configuration system for standardized initialization
**Source**: `control/native_gui/core/tool_config.py` (python)

### ToolConfigFactory
**Definition**: ToolConfigFactory: Factory for standardized tool configuration creation
**Source**: `control/native_gui/core/tool_config.py` (python)

### unknown
**Definition**: __init__: system control component
**Source**: `control/native_gui/core/__init__.py` (python)

### unknown
**Definition**: css_generator: Unified CSS generation system for mobile-responsive UI framework
**Source**: `control/native_gui/core/css_generator.py` (python)

### CSSGenerator
**Definition**: CSSGenerator: Consolidated CSS generation system for mobile-first responsive design
**Source**: `control/native_gui/core/css_generator.py` (python)

### unknown
**Definition**: application: system control component
**Source**: `control/native_gui/core/application.py` (python)

### unknown
**Definition**: widget_factory: Unified widget creation system for consistent UI patterns
**Source**: `control/native_gui/ui/widget_factory.py` (python)

### WidgetFactory
**Definition**: WidgetFactory: Unified widget creation system for consistent UI patterns
**Source**: `control/native_gui/ui/widget_factory.py` (python)

### unknown
**Definition**: __init__: system control component
**Source**: `control/native_gui/widgets/__init__.py` (python)

### unknown
**Definition**: response_viewer: system control component
**Source**: `control/native_gui/widgets/response_viewer.py` (python)

### unknown
**Definition**: request_builder: system control component
**Source**: `control/native_gui/widgets/request_builder.py` (python)

### unknown
**Definition**: proto_browser: system control component
**Source**: `control/native_gui/widgets/proto_browser.py` (python)

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

### version
**Definition**: docker-compose-production: Unified production service orchestration
**Source**: `orchestration/docker-compose.production.yml` (yaml)

### version
**Definition**: docker-compose-development: Development environment with debugging tools
**Source**: `orchestration/docker-compose.development.yml` (yaml)

### unknown
**Definition**: unhinged-registry: Complete file registry for static HTML interface
**Source**: `generated/static_html/registry.js` (typescript)

### unknown
**Definition**: unhinged-file-structure: Complete directory tree for navigation
**Source**: `generated/static_html/registry.js` (typescript)
