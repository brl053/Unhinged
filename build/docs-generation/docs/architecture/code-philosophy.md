# 🏛️ Code Philosophy - Unhinged Platform

> **Purpose**: Fundamental design principles extracted from codebase
> **Source**: Auto-generated from evolved LlmDocs format
> **Last Updated**: 2025-10-28 23:56:31

## 🎯 Critical Business Rules

These are the non-negotiable constraints that guide all development:

### test_parse_llm_tags_with_context (python)
**File**: `test_llm_extraction.py`
**Rule**: never trust user input
**Context**: user input

### unknown (python)
**File**: `extract-llm-comments.py`
**Rule**: extraction must be comprehensive and handle all supported file types
**Context**: llmdocs extraction and documentation generation from polyglot codebase

### unknown (python)
**File**: `generate-project-structure.py`
**Rule**: structure documentation must be accurate and reflect current state
**Context**: project structure documentation generation from filesystem analysis

### unknown (python)
**File**: `validate-llm-comments.py`
**Rule**: validation must enforce evolved format standards and provide actionable feedback
**Context**: llmdocs validation and quality assurance for evolved format compliance

## 📚 Component Catalog

System components organized by type and function:

### component.primitive
- **test_extract_llm_context_from_typescript**: react component for user authentication (`test_llm_extraction.py`)

### config.build
- **LLMContextWarmer**: structured context summaries for new llm agents (`llm-context-warmer.py`)
- **unknown**: tdd test suite ensuring extraction and validation (`test_llm_extraction.py`)
- **TestLLMContextWarmerImprovements**: test suite for llm context warmer improvements (`test_llm_extraction.py`)
- **test_element_name_detection_from_service_path**: test element name extraction from services directory (`test_llm_extraction.py`)
- **test_element_name_detection_from_python_file**: test element name extraction from python file (`test_llm_extraction.py`)
- ... and 9 more

### hierarchy
- **unknown**: Hierarchical documentation generator that creates organized markdown files from LlmDocs comments by @llm-type hierarchy (`hierarchical-docs-generator.py`)

### service.api
- **test_extract_llm_context_from_python**: user requests (`test_llm_extraction.py`)

### util.extractor
- **unknown**: llmdocs extraction and documentation generation from polyglot codebase (`extract-llm-comments.py`)

### util.function
- **generate_project_overview**: comprehensive project overview from extracted comments (`llm-context-warmer.py`)
- **_extract_key_components**: extract key system components with improved name (`llm-context-warmer.py`)
- **paginate_comments**: paginated access to all extracted comments for (`llm-context-warmer.py`)
- **_improve_element_name**: improve element name detection from file paths (`llm-context-warmer.py`)
- **_find_related_services**: find related services through port references, api (`llm-context-warmer.py`)
- ... and 9 more

### util.generator
- **unknown**: project structure documentation generation from filesystem analysis (`generate-project-structure.py`)

### util.tool
- **unknown**: llm context warming system for onboarding new (`llm-context-warmer.py`)

### util.validator
- **test_parse_llm_tags_with_context**: user input (`test_llm_extraction.py`)
- **unknown**: llmdocs validation and quality assurance for evolved format compliance (`validate-llm-comments.py`)
