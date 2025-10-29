# Config - Build

> **Generated from LlmDocs**: 2025-10-28 23:59:42
> **Category**: `config.build`
> **Components**: 39

## Components

1. [UnhingedPythonSetup](#unhingedpythonsetup) - `build/python/setup.py`
2. [LLMContextWarmer](#llmcontextwarmer) - `build/docs-generation/llm-context-warmer.py`
3. [unknown](#unknown) - `build/docs-generation/test_llm_extraction.py`
4. [TestLLMContextWarmerImprovements](#testllmcontextwarmerimprovements) - `build/docs-generation/test_llm_extraction.py`
5. [test_element_name_detection_from_service_path](#test-element-name-detection-from-service-path) - `build/docs-generation/test_llm_extraction.py`
6. [test_element_name_detection_from_python_file](#test-element-name-detection-from-python-file) - `build/docs-generation/test_llm_extraction.py`
7. [test_find_related_services_by_port_references](#test-find-related-services-by-port-references) - `build/docs-generation/test_llm_extraction.py`
8. [test_context_completeness_validation](#test-context-completeness-validation) - `build/docs-generation/test_llm_extraction.py`
9. [test_pagination_data_integrity](#test-pagination-data-integrity) - `build/docs-generation/test_llm_extraction.py`
10. [TestLLMContextWarmerEnhancements](#testllmcontextwarmerenhancements) - `build/docs-generation/test_llm_extraction.py`
11. [test_getting_started_section_generation](#test-getting-started-section-generation) - `build/docs-generation/test_llm_extraction.py`
12. [test_dependency_information_extraction](#test-dependency-information-extraction) - `build/docs-generation/test_llm_extraction.py`
13. [test_complete_legend_validation](#test-complete-legend-validation) - `build/docs-generation/test_llm_extraction.py`
14. [test_enhanced_overview_with_getting_started](#test-enhanced-overview-with-getting-started) - `build/docs-generation/test_llm_extraction.py`
15. [unknown](#unknown) - `build/docs-generation/llm_types.py`
16. [version](#version) - `build/orchestration/docker-compose.production.yml`
17. [version](#version) - `build/orchestration/docker-compose.development.yml`
18. [unknown](#unknown) - `build/modules/registry_builder.py`
19. [RegistryBuilder](#registrybuilder) - `build/modules/registry_builder.py`
20. [unknown](#unknown) - `build/modules/proto_client_builder.py`
21. [ProtoClientBuilder](#protoclientbuilder) - `build/modules/proto_client_builder.py`
22. [unknown](#unknown) - `build/modules/typescript_proto_handler.py`
23. [validate_build_patterns](#validate-build-patterns) - `build/modules/__init__.py`
24. [unknown](#unknown) - `build/modules/python_proto_handler.py`
25. [ServiceDiscoveryBuilder](#servicediscoverybuilder) - `build/modules/service_discovery_builder.py`
26. [unknown](#unknown) - `build/modules/kotlin_proto_handler.py`
27. [PolyglotProtoEngine](#polyglotprotoengine) - `build/modules/polyglot_proto_engine.py`
28. [unknown](#unknown) - `build/modules/c_proto_handler.py`
29. [unknown](#unknown) - `build/validators/polyglot_validator.py`
30. [BaseValidator](#basevalidator) - `build/validators/polyglot_validator.py`
31. [PolyglotValidationRunner](#polyglotvalidationrunner) - `build/validators/polyglot_validator.py`
32. [unknown](#unknown) - `libs/design_system/build/design_token_builder.py`
33. [DesignTokenBuilder](#designtokenbuilder) - `libs/design_system/build/design_token_builder.py`
34. [unknown](#unknown) - `libs/design_system/build/component_generator.py`
35. [unknown](#unknown) - `libs/design_system/build/component_build_module.py`
36. [unknown](#unknown) - `libs/design_system/build/generators/_abstract_generator.py`
37. [unknown](#unknown) - `libs/design_system/build/generators/gtk4/generator.py`
38. [resolve_token](#resolve-token) - `libs/design_system/build/generators/gtk4/generator.py`
39. [unknown](#unknown) - `libs/design_system/build/generators/gtk4/generator.py`

## UnhingedPythonSetup

### Metadata

- **File**: `build/python/setup.py`
- **Language**: python
- **Type**: `config.build`

### Purpose

comprehensive python environment setup for ml/ai etl

### Rules & Constraints

⚠️ **Critical**: environment setup must be reproducible, comprehensive, and failure-resistant

---

## LLMContextWarmer

### Metadata

- **File**: `build/docs-generation/llm-context-warmer.py`
- **Language**: python
- **Type**: `config.build`

### Purpose

structured context summaries for new llm agents

---

## unknown

### Metadata

- **File**: `build/docs-generation/test_llm_extraction.py`
- **Language**: python
- **Type**: `config.build`

### Purpose

tdd test suite ensuring extraction and validation

---

## TestLLMContextWarmerImprovements

### Metadata

- **File**: `build/docs-generation/test_llm_extraction.py`
- **Language**: python
- **Type**: `config.build`

### Purpose

test suite for llm context warmer improvements

---

## test_element_name_detection_from_service_path

### Metadata

- **File**: `build/docs-generation/test_llm_extraction.py`
- **Language**: python
- **Type**: `config.build`

### Purpose

test element name extraction from services directory

---

## test_element_name_detection_from_python_file

### Metadata

- **File**: `build/docs-generation/test_llm_extraction.py`
- **Language**: python
- **Type**: `config.build`

### Purpose

test element name extraction from python file

---

## test_find_related_services_by_port_references

### Metadata

- **File**: `build/docs-generation/test_llm_extraction.py`
- **Language**: python
- **Type**: `config.build`

### Purpose

test cross-reference detection between services using port

---

## test_context_completeness_validation

### Metadata

- **File**: `build/docs-generation/test_llm_extraction.py`
- **Language**: python
- **Type**: `config.build`

### Purpose

test validation of context completeness for service

---

## test_pagination_data_integrity

### Metadata

- **File**: `build/docs-generation/test_llm_extraction.py`
- **Language**: python
- **Type**: `config.build`

### Purpose

test that pagination maintains complete data integrity

---

## TestLLMContextWarmerEnhancements

### Metadata

- **File**: `build/docs-generation/test_llm_extraction.py`
- **Language**: python
- **Type**: `config.build`

### Purpose

test suite for final llm context warmer

---

## test_getting_started_section_generation

### Metadata

- **File**: `build/docs-generation/test_llm_extraction.py`
- **Language**: python
- **Type**: `config.build`

### Purpose

test generation of getting started section with

---

## test_dependency_information_extraction

### Metadata

- **File**: `build/docs-generation/test_llm_extraction.py`
- **Language**: python
- **Type**: `config.build`

### Purpose

test extraction of dependency and setup information

---

## test_complete_legend_validation

### Metadata

- **File**: `build/docs-generation/test_llm_extraction.py`
- **Language**: python
- **Type**: `config.build`

### Purpose

test validation that legends are complete and

---

## test_enhanced_overview_with_getting_started

### Metadata

- **File**: `build/docs-generation/test_llm_extraction.py`
- **Language**: python
- **Type**: `config.build`

### Purpose

test that enhanced overview includes getting started

---

## unknown

### Metadata

- **File**: `build/docs-generation/llm_types.py`
- **Language**: python
- **Type**: `config.build`

### Purpose

defines data structures and interfaces for llm

---

## version

### Metadata

- **File**: `build/orchestration/docker-compose.production.yml`
- **Language**: yaml
- **Type**: `config.build`

### Purpose

production docker-compose with unified service definitions

---

## version

### Metadata

- **File**: `build/orchestration/docker-compose.development.yml`
- **Language**: yaml
- **Type**: `config.build`

### Purpose

development docker-compose with debug tools and hot-reload

---

## unknown

### Metadata

- **File**: `build/modules/registry_builder.py`
- **Language**: python
- **Type**: `config.build`

### Purpose

static html registry generation module for control

---

## RegistryBuilder

### Metadata

- **File**: `build/modules/registry_builder.py`
- **Language**: python
- **Type**: `config.build`

### Purpose

javascript registry of static html files for

### Rules & Constraints

⚠️ **Critical**: registry must be generated before browser access to ensure accurate file disc...

---

## unknown

### Metadata

- **File**: `build/modules/proto_client_builder.py`
- **Language**: python
- **Type**: `config.build`

### Purpose

proto-to-polyglot client library generation module using ...

### Rules & Constraints

⚠️ **Critical**: client libraries must be generated before service compilation and provide typ...

---

## ProtoClientBuilder

### Metadata

- **File**: `build/modules/proto_client_builder.py`
- **Language**: python
- **Type**: `config.build`

### Purpose

polyglot protobuf client generation using unified dry

---

## unknown

### Metadata

- **File**: `build/modules/typescript_proto_handler.py`
- **Language**: python
- **Type**: `config.build`

### Purpose

typescript protobuf client generation handler with grpc-web

---

## validate_build_patterns

### Metadata

- **File**: `build/modules/__init__.py`
- **Language**: python
- **Type**: `config.build`

### Purpose

validate build system patterns and cultural commandments

---

## unknown

### Metadata

- **File**: `build/modules/python_proto_handler.py`
- **Language**: python
- **Type**: `config.build`

### Purpose

python protobuf client generation handler for ai/ml

---

## ServiceDiscoveryBuilder

### Metadata

- **File**: `build/modules/service_discovery_builder.py`
- **Language**: python
- **Type**: `config.build`

### Purpose

build-time service discovery module following existing bu...

### Rules & Constraints

⚠️ **Critical**: service registry must be generated before html dashboard access

---

## unknown

### Metadata

- **File**: `build/modules/kotlin_proto_handler.py`
- **Language**: python
- **Type**: `config.build`

### Purpose

kotlin protobuf client generation handler for jvm

---

## PolyglotProtoEngine

### Metadata

- **File**: `build/modules/polyglot_proto_engine.py`
- **Language**: python
- **Type**: `config.build`

### Purpose

unified engine for generating protobuf clients across

---

## unknown

### Metadata

- **File**: `build/modules/c_proto_handler.py`
- **Language**: python
- **Type**: `config.build`

### Purpose

c/c++ protobuf client generation handler for high-perform...

### Rules & Constraints

⚠️ **Critical**: c++ proto clients must provide maximum performance for system-level services

---

## unknown

### Metadata

- **File**: `build/validators/polyglot_validator.py`
- **Language**: python
- **Type**: `config.build`

### Purpose

polyglot validation system for enforcing unhinged codebase

### Rules & Constraints

⚠️ **Critical**: all validation must be fast, parallel, actionable, and educational

---

## BaseValidator

### Metadata

- **File**: `build/validators/polyglot_validator.py`
- **Language**: python
- **Type**: `config.build`

### Purpose

abstract base class for all validators in

---

## PolyglotValidationRunner

### Metadata

- **File**: `build/validators/polyglot_validator.py`
- **Language**: python
- **Type**: `config.build`

### Purpose

main validation runner that coordinates all validators

---

## unknown

### Metadata

- **File**: `libs/design_system/build/design_token_builder.py`
- **Language**: python
- **Type**: `config.build`

### Purpose

design token generation module following protoclientbuild...

### Rules & Constraints

⚠️ **Critical**: design tokens must be generated before ui compilation and provide consistent ...

---

## DesignTokenBuilder

### Metadata

- **File**: `libs/design_system/build/design_token_builder.py`
- **Language**: python
- **Type**: `config.build`

### Purpose

design token generation following protoclientbuilder arch...

---

## unknown

### Metadata

- **File**: `libs/design_system/build/component_generator.py`
- **Language**: python
- **Type**: `config.build`

### Purpose

component generation orchestrator coordinating platform-s...

---

## unknown

### Metadata

- **File**: `libs/design_system/build/component_build_module.py`
- **Language**: python
- **Type**: `config.build`

### Purpose

component generation build module integrating with unhinged

---

## unknown

### Metadata

- **File**: `libs/design_system/build/generators/_abstract_generator.py`
- **Language**: python
- **Type**: `config.build`

### Purpose

abstract component generator interface ensuring platform ...

---

## unknown

### Metadata

- **File**: `libs/design_system/build/generators/gtk4/generator.py`
- **Language**: python
- **Type**: `config.build`

### Purpose

gtk4 component generator producing python widget implemen...

---

## resolve_token

### Metadata

- **File**: `libs/design_system/build/generators/gtk4/generator.py`
- **Language**: python
- **Type**: `config.build`

### Purpose

resolves platform-agnostic token references to gtk4-speci...

---

## unknown

### Metadata

- **File**: `libs/design_system/build/generators/gtk4/generator.py`
- **Language**: python
- **Type**: `config.build`

### Purpose

auto-generated gtk4 widget from design system component

---

